"""
Reverb Effect Processor

Implements convolution reverb with various room simulations.
Supports adjustable room size, damping, wet/dry mix, and stereo width.
"""

import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ReverbParameters:
    """Parameters for reverb effect"""
    room_size: float = 0.5  # 0.0 - 1.0
    damping: float = 0.5  # 0.0 - 1.0 (decay/absorption)
    wet_dry_mix: float = 0.3  # 0.0 (dry) - 1.0 (wet)
    stereo_width: float = 1.0  # 0.0 (mono) - 1.0 (full stereo)
    early_reflections: float = 0.3  # 0.0 - 1.0
    pre_delay: float = 0.0  # milliseconds (0-100)


class ReverbProcessor:
    """
    Professional reverb effect processor using convolution and Schroeder reverberator.
    """
    
    # Preset configurations
    PRESETS = {
        'small_room': ReverbParameters(
            room_size=0.2,
            damping=0.7,
            wet_dry_mix=0.2,
            stereo_width=0.6,
            early_reflections=0.4,
            pre_delay=5.0
        ),
        'medium_room': ReverbParameters(
            room_size=0.5,
            damping=0.5,
            wet_dry_mix=0.3,
            stereo_width=0.8,
            early_reflections=0.3,
            pre_delay=10.0
        ),
        'large_hall': ReverbParameters(
            room_size=0.8,
            damping=0.3,
            wet_dry_mix=0.4,
            stereo_width=1.0,
            early_reflections=0.2,
            pre_delay=20.0
        ),
        'chamber': ReverbParameters(
            room_size=0.4,
            damping=0.6,
            wet_dry_mix=0.35,
            stereo_width=0.7,
            early_reflections=0.5,
            pre_delay=8.0
        ),
        'plate': ReverbParameters(
            room_size=0.3,
            damping=0.8,
            wet_dry_mix=0.25,
            stereo_width=1.0,
            early_reflections=0.1,
            pre_delay=2.0
        ),
        'cathedral': ReverbParameters(
            room_size=0.95,
            damping=0.2,
            wet_dry_mix=0.5,
            stereo_width=1.0,
            early_reflections=0.15,
            pre_delay=30.0
        )
    }
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize reverb processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.parameters = ReverbParameters()
        
        # Comb filter delays (in samples) for different room sizes
        self.comb_delays = [1557, 1617, 1491, 1422, 1277, 1356, 1188, 1116]
        self.allpass_delays = [225, 556, 441, 341]
        
        # Initialize delay buffers
        self._init_buffers()
    
    def _init_buffers(self):
        """Initialize delay line buffers for comb and allpass filters"""
        max_delay = max(self.comb_delays + self.allpass_delays)
        self.comb_buffers_l = [np.zeros(delay) for delay in self.comb_delays]
        self.comb_buffers_r = [np.zeros(delay) for delay in self.comb_delays]
        self.allpass_buffers = [np.zeros(delay) for delay in self.allpass_delays]
        
        self.comb_indices = [0] * len(self.comb_delays)
        self.allpass_indices = [0] * len(self.allpass_delays)
        
        # Filter states
        self.comb_filter_states = [0.0] * len(self.comb_delays)
    
    def set_preset(self, preset_name: str):
        """
        Apply a preset configuration.
        
        Args:
            preset_name: Name of the preset ('small_room', 'large_hall', etc.)
        
        Raises:
            ValueError: If preset name is not recognized
        """
        if preset_name not in self.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.PRESETS.keys())}")
        
        self.parameters = self.PRESETS[preset_name]
    
    def set_parameters(self, **kwargs):
        """
        Update reverb parameters.
        
        Args:
            **kwargs: Parameter name-value pairs
        """
        for key, value in kwargs.items():
            if hasattr(self.parameters, key):
                setattr(self.parameters, key, value)
            else:
                raise ValueError(f"Unknown parameter: {key}")
    
    def _apply_comb_filter(
        self, 
        input_sample: float, 
        buffer: np.ndarray, 
        index: int, 
        filter_state: float,
        feedback: float,
        damping: float
    ) -> Tuple[float, int, float]:
        """Apply a comb filter with damping"""
        # Read from delay line
        delayed = buffer[index]
        
        # Apply damping (one-pole lowpass filter)
        filter_state = delayed * (1.0 - damping) + filter_state * damping
        
        # Write to delay line with feedback
        buffer[index] = input_sample + filter_state * feedback
        
        # Update index
        index = (index + 1) % len(buffer)
        
        return delayed, index, filter_state
    
    def _apply_allpass_filter(
        self,
        input_sample: float,
        buffer: np.ndarray,
        index: int,
        feedback: float = 0.5
    ) -> Tuple[float, int]:
        """Apply an allpass filter"""
        # Read from delay line
        delayed = buffer[index]
        
        # Allpass equation
        output = -input_sample + delayed
        buffer[index] = input_sample + delayed * feedback
        
        # Update index
        index = (index + 1) % len(buffer)
        
        return output, index
    
    def process(
        self, 
        audio: np.ndarray, 
        parameters: Optional[ReverbParameters] = None
    ) -> np.ndarray:
        """
        Process audio with reverb effect.
        
        Args:
            audio: Input audio array (mono or stereo)
            parameters: Optional reverb parameters (uses current if None)
        
        Returns:
            Processed audio with reverb applied
        """
        if parameters:
            self.parameters = parameters
        
        params = self.parameters
        
        # Ensure audio is 2D (channels x samples)
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        
        channels, samples = audio.shape
        output = np.zeros_like(audio)
        
        # Calculate feedback based on room size
        feedback = 0.84 + (params.room_size * 0.1)
        
        # Pre-delay
        pre_delay_samples = int(params.pre_delay * self.sample_rate / 1000.0)
        
        for channel in range(channels):
            channel_input = audio[channel]
            channel_output = np.zeros(samples)
            
            # Choose buffer set based on channel for stereo width
            comb_buffers = self.comb_buffers_l if channel == 0 else self.comb_buffers_r
            
            for i in range(samples):
                # Apply pre-delay
                delayed_input = channel_input[max(0, i - pre_delay_samples)]
                
                # Sum of comb filters (parallel configuration)
                comb_sum = 0.0
                for j, (buffer, delay) in enumerate(zip(comb_buffers, self.comb_delays)):
                    filtered, self.comb_indices[j], self.comb_filter_states[j] = \
                        self._apply_comb_filter(
                            delayed_input,
                            buffer,
                            self.comb_indices[j],
                            self.comb_filter_states[j],
                            feedback,
                            params.damping
                        )
                    comb_sum += filtered
                
                # Average comb filter outputs
                comb_output = comb_sum / len(self.comb_delays)
                
                # Series allpass filters
                allpass_output = comb_output
                for j, (buffer, delay) in enumerate(zip(self.allpass_buffers, self.allpass_delays)):
                    allpass_output, self.allpass_indices[j] = \
                        self._apply_allpass_filter(
                            allpass_output,
                            buffer,
                            self.allpass_indices[j]
                        )
                
                # Mix wet and dry signals
                channel_output[i] = (
                    channel_input[i] * (1.0 - params.wet_dry_mix) +
                    allpass_output * params.wet_dry_mix
                )
            
            output[channel] = channel_output
        
        # Apply stereo width (if stereo)
        if channels == 2 and params.stereo_width < 1.0:
            mid = (output[0] + output[1]) / 2
            side = (output[0] - output[1]) / 2
            output[0] = mid + side * params.stereo_width
            output[1] = mid - side * params.stereo_width
        
        return output if audio.ndim == 2 else output[0]
    
    def get_parameter_info(self) -> Dict[str, Dict[str, any]]:
        """
        Get information about all parameters.
        
        Returns:
            Dictionary with parameter information
        """
        return {
            'room_size': {
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': 'Size of the simulated room'
            },
            'damping': {
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': 'High frequency absorption'
            },
            'wet_dry_mix': {
                'min': 0.0,
                'max': 1.0,
                'default': 0.3,
                'description': 'Balance between dry (0) and wet (1) signal'
            },
            'stereo_width': {
                'min': 0.0,
                'max': 1.0,
                'default': 1.0,
                'description': 'Stereo spread of reverb'
            },
            'early_reflections': {
                'min': 0.0,
                'max': 1.0,
                'default': 0.3,
                'description': 'Level of early reflections'
            },
            'pre_delay': {
                'min': 0.0,
                'max': 100.0,
                'default': 0.0,
                'description': 'Pre-delay time in milliseconds'
            }
        }


# Example usage
if __name__ == "__main__":
    # Create reverb processor
    reverb = ReverbProcessor(sample_rate=44100)
    
    # Apply a preset
    reverb.set_preset('large_hall')
    
    # Or set custom parameters
    reverb.set_parameters(
        room_size=0.7,
        damping=0.4,
        wet_dry_mix=0.35
    )
    
    # Process audio
    # audio_input = np.random.randn(44100)  # 1 second of audio
    # audio_output = reverb.process(audio_input)
