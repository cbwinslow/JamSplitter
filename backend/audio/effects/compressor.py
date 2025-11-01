"""
Dynamic Range Compressor

Implements professional dynamic range compression with attack, release,
threshold, ratio, and makeup gain controls.
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class CompressorParameters:
    """Parameters for compressor effect"""
    threshold: float = -20.0  # dB
    ratio: float = 4.0  # 1:1 to 20:1
    attack: float = 10.0  # milliseconds
    release: float = 100.0  # milliseconds
    knee: float = 6.0  # dB (soft knee width)
    makeup_gain: float = 0.0  # dB
    auto_makeup: bool = True  # Automatically calculate makeup gain


class Compressor:
    """
    Professional dynamic range compressor with soft knee and RMS detection.
    """
    
    # Preset configurations
    PRESETS = {
        'gentle': CompressorParameters(
            threshold=-18.0,
            ratio=2.0,
            attack=15.0,
            release=150.0,
            knee=8.0,
            auto_makeup=True
        ),
        'vocal': CompressorParameters(
            threshold=-20.0,
            ratio=4.0,
            attack=10.0,
            release=100.0,
            knee=6.0,
            auto_makeup=True
        ),
        'aggressive': CompressorParameters(
            threshold=-24.0,
            ratio=8.0,
            attack=5.0,
            release=50.0,
            knee=4.0,
            auto_makeup=True
        ),
        'drum_bus': CompressorParameters(
            threshold=-12.0,
            ratio=4.0,
            attack=3.0,
            release=50.0,
            knee=3.0,
            auto_makeup=True
        ),
        'master': CompressorParameters(
            threshold=-10.0,
            ratio=2.5,
            attack=30.0,
            release=200.0,
            knee=10.0,
            auto_makeup=True
        ),
        'limiter': CompressorParameters(
            threshold=-6.0,
            ratio=20.0,
            attack=0.5,
            release=100.0,
            knee=0.0,
            auto_makeup=False
        ),
        'bass': CompressorParameters(
            threshold=-15.0,
            ratio=5.0,
            attack=20.0,
            release=120.0,
            knee=8.0,
            auto_makeup=True
        )
    }
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize compressor.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.parameters = CompressorParameters()
        
        # State variables for envelope follower
        self.envelope = 0.0
        self.gain_reduction_history = []
        
        # RMS window for level detection
        self.rms_window_size = int(0.01 * sample_rate)  # 10ms window
        self.rms_buffer = np.zeros(self.rms_window_size)
        self.rms_index = 0
    
    def set_preset(self, preset_name: str):
        """
        Apply a preset configuration.
        
        Args:
            preset_name: Name of the preset
        
        Raises:
            ValueError: If preset not found
        """
        if preset_name not in self.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.PRESETS.keys())}")
        
        self.parameters = CompressorParameters(**self.PRESETS[preset_name].__dict__)
    
    def set_parameters(self, **kwargs):
        """
        Update compressor parameters.
        
        Args:
            **kwargs: Parameter name-value pairs
        """
        for key, value in kwargs.items():
            if hasattr(self.parameters, key):
                setattr(self.parameters, key, value)
            else:
                raise ValueError(f"Unknown parameter: {key}")
    
    def _db_to_linear(self, db: float) -> float:
        """Convert decibels to linear scale"""
        return 10.0 ** (db / 20.0)
    
    def _linear_to_db(self, linear: float) -> float:
        """Convert linear scale to decibels"""
        return 20.0 * np.log10(max(linear, 1e-10))
    
    def _calculate_rms(self, sample: float) -> float:
        """
        Calculate RMS level using a sliding window.
        
        Args:
            sample: Input sample
        
        Returns:
            RMS level
        """
        # Add new sample to buffer
        self.rms_buffer[self.rms_index] = sample ** 2
        self.rms_index = (self.rms_index + 1) % self.rms_window_size
        
        # Calculate RMS
        rms = np.sqrt(np.mean(self.rms_buffer))
        return rms
    
    def _apply_soft_knee(self, input_db: float, threshold: float, 
                        ratio: float, knee: float) -> float:
        """
        Apply soft knee compression curve.
        
        Args:
            input_db: Input level in dB
            threshold: Threshold in dB
            ratio: Compression ratio
            knee: Knee width in dB
        
        Returns:
            Output level in dB
        """
        if knee <= 0:
            # Hard knee
            if input_db > threshold:
                return threshold + (input_db - threshold) / ratio
            else:
                return input_db
        
        # Soft knee
        knee_start = threshold - knee / 2.0
        knee_end = threshold + knee / 2.0
        
        if input_db < knee_start:
            # Below knee
            return input_db
        elif input_db > knee_end:
            # Above knee
            return threshold + (input_db - threshold) / ratio
        else:
            # Within knee
            # Smooth transition using quadratic curve
            x = input_db - knee_start
            w = knee
            output = input_db + ((1.0 / ratio - 1.0) * (x - w / 2.0) ** 2) / (2.0 * w)
            return output
    
    def _calculate_envelope(self, input_level: float, current_envelope: float,
                           attack_coeff: float, release_coeff: float) -> float:
        """
        Calculate envelope follower with attack and release.
        
        Args:
            input_level: Current input level
            current_envelope: Current envelope value
            attack_coeff: Attack time coefficient
            release_coeff: Release time coefficient
        
        Returns:
            Updated envelope value
        """
        if input_level > current_envelope:
            # Attack
            return attack_coeff * input_level + (1.0 - attack_coeff) * current_envelope
        else:
            # Release
            return release_coeff * input_level + (1.0 - release_coeff) * current_envelope
    
    def process(self, audio: np.ndarray, 
                parameters: Optional[CompressorParameters] = None) -> np.ndarray:
        """
        Process audio with compression.
        
        Args:
            audio: Input audio (mono or stereo)
            parameters: Optional compressor parameters
        
        Returns:
            Compressed audio
        """
        if parameters:
            self.parameters = parameters
        
        params = self.parameters
        
        # Ensure audio is 2D
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        
        channels, samples = audio.shape
        output = np.zeros_like(audio)
        
        # Calculate time constants
        attack_time = params.attack / 1000.0  # Convert to seconds
        release_time = params.release / 1000.0
        
        # Calculate coefficients for envelope follower
        attack_coeff = 1.0 - np.exp(-1.0 / (attack_time * self.sample_rate))
        release_coeff = 1.0 - np.exp(-1.0 / (release_time * self.sample_rate))
        
        # Calculate makeup gain if auto mode
        makeup_gain_linear = self._db_to_linear(params.makeup_gain)
        if params.auto_makeup:
            # Approximate makeup gain based on threshold and ratio
            estimated_reduction = abs(params.threshold) * (1.0 - 1.0 / params.ratio)
            makeup_gain_linear = self._db_to_linear(estimated_reduction * 0.5)
        
        # Reset envelope for each processing
        self.envelope = 0.0
        self.gain_reduction_history = []
        
        # Process each channel
        for channel in range(channels):
            for i in range(samples):
                # Get input sample
                input_sample = audio[channel, i]
                
                # Calculate RMS level
                rms = self._calculate_rms(input_sample)
                rms_db = self._linear_to_db(rms)
                
                # Apply compression curve
                output_db = self._apply_soft_knee(
                    rms_db, 
                    params.threshold,
                    params.ratio,
                    params.knee
                )
                
                # Calculate gain reduction
                gain_reduction_db = output_db - rms_db
                gain_reduction_linear = self._db_to_linear(gain_reduction_db)
                
                # Apply envelope follower
                self.envelope = self._calculate_envelope(
                    gain_reduction_linear,
                    self.envelope,
                    attack_coeff,
                    release_coeff
                )
                
                # Apply gain reduction to sample
                output_sample = input_sample * self.envelope
                
                # Apply makeup gain
                output_sample *= makeup_gain_linear
                
                # Store output
                output[channel, i] = output_sample
                
                # Store gain reduction for metering (in dB)
                if channel == 0:  # Only store once for stereo
                    gr_db = self._linear_to_db(self.envelope)
                    self.gain_reduction_history.append(gr_db)
        
        return output if audio.ndim == 2 else output[0]
    
    def get_gain_reduction(self, window_size: int = 100) -> float:
        """
        Get average gain reduction over recent samples.
        
        Args:
            window_size: Number of recent samples to average
        
        Returns:
            Average gain reduction in dB
        """
        if not self.gain_reduction_history:
            return 0.0
        
        recent = self.gain_reduction_history[-window_size:]
        return np.mean(recent)
    
    def get_gain_reduction_peak(self) -> float:
        """
        Get peak gain reduction.
        
        Returns:
            Peak gain reduction in dB
        """
        if not self.gain_reduction_history:
            return 0.0
        
        return min(self.gain_reduction_history)
    
    def get_parameter_info(self) -> Dict[str, Dict[str, any]]:
        """
        Get information about all parameters.
        
        Returns:
            Dictionary with parameter information
        """
        return {
            'threshold': {
                'min': -60.0,
                'max': 0.0,
                'default': -20.0,
                'unit': 'dB',
                'description': 'Level above which compression is applied'
            },
            'ratio': {
                'min': 1.0,
                'max': 20.0,
                'default': 4.0,
                'unit': ':1',
                'description': 'Compression ratio (1:1 = no compression)'
            },
            'attack': {
                'min': 0.1,
                'max': 100.0,
                'default': 10.0,
                'unit': 'ms',
                'description': 'Time to reach full compression'
            },
            'release': {
                'min': 10.0,
                'max': 1000.0,
                'default': 100.0,
                'unit': 'ms',
                'description': 'Time to return to no compression'
            },
            'knee': {
                'min': 0.0,
                'max': 20.0,
                'default': 6.0,
                'unit': 'dB',
                'description': 'Width of soft knee (0 = hard knee)'
            },
            'makeup_gain': {
                'min': 0.0,
                'max': 30.0,
                'default': 0.0,
                'unit': 'dB',
                'description': 'Output gain compensation'
            },
            'auto_makeup': {
                'type': 'boolean',
                'default': True,
                'description': 'Automatically calculate makeup gain'
            }
        }


# Example usage
if __name__ == "__main__":
    # Create compressor
    comp = Compressor(sample_rate=44100)
    
    # Load preset
    comp.set_preset('vocal')
    
    # Or customize
    comp.set_parameters(
        threshold=-18.0,
        ratio=4.0,
        attack=8.0,
        release=80.0,
        knee=6.0
    )
    
    # Process audio
    # audio_input = np.random.randn(44100)
    # audio_output = comp.process(audio_input)
    
    # Get gain reduction for metering
    # avg_gr = comp.get_gain_reduction()
    # peak_gr = comp.get_gain_reduction_peak()
    # print(f"Average GR: {avg_gr:.1f} dB, Peak GR: {peak_gr:.1f} dB")
