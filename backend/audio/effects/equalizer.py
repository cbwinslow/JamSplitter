"""
Parametric Equalizer Processor

Implements a professional parametric EQ with multiple bands,
each with frequency, gain, and Q (bandwidth) controls.
"""

import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class FilterType(Enum):
    """Types of EQ filters"""
    BELL = "bell"  # Parametric bell curve
    LOW_SHELF = "low_shelf"  # Low frequency shelf
    HIGH_SHELF = "high_shelf"  # High frequency shelf
    LOW_PASS = "low_pass"  # Low pass filter
    HIGH_PASS = "high_pass"  # High pass filter
    NOTCH = "notch"  # Notch filter


@dataclass
class EQBand:
    """Single EQ band configuration"""
    frequency: float  # Hz
    gain: float  # dB (-20 to +20)
    q: float  # Quality factor (0.1 to 10)
    filter_type: FilterType = FilterType.BELL
    enabled: bool = True


class ParametricEqualizer:
    """
    Professional parametric equalizer with multiple bands.
    Uses biquad filters for accurate frequency shaping.
    """
    
    # Common EQ presets
    PRESETS = {
        'flat': [
            EQBand(60, 0, 0.7, FilterType.LOW_SHELF),
            EQBand(250, 0, 1.0, FilterType.BELL),
            EQBand(1000, 0, 1.0, FilterType.BELL),
            EQBand(4000, 0, 1.0, FilterType.BELL),
            EQBand(12000, 0, 0.7, FilterType.HIGH_SHELF),
        ],
        'vocal_clarity': [
            EQBand(80, -3, 0.7, FilterType.LOW_SHELF),
            EQBand(200, -2, 1.2, FilterType.BELL),
            EQBand(3000, 4, 1.5, FilterType.BELL),
            EQBand(6000, 2, 1.0, FilterType.BELL),
            EQBand(12000, 1, 0.7, FilterType.HIGH_SHELF),
        ],
        'bass_boost': [
            EQBand(60, 6, 0.7, FilterType.LOW_SHELF),
            EQBand(120, 3, 1.0, FilterType.BELL),
            EQBand(250, -1, 1.0, FilterType.BELL),
            EQBand(500, 0, 1.0, FilterType.BELL),
            EQBand(8000, 0, 0.7, FilterType.HIGH_SHELF),
        ],
        'bright': [
            EQBand(60, 0, 0.7, FilterType.LOW_SHELF),
            EQBand(250, -1, 1.0, FilterType.BELL),
            EQBand(2000, 2, 1.2, FilterType.BELL),
            EQBand(6000, 4, 1.0, FilterType.BELL),
            EQBand(12000, 3, 0.7, FilterType.HIGH_SHELF),
        ],
        'warm': [
            EQBand(60, 3, 0.7, FilterType.LOW_SHELF),
            EQBand(200, 2, 1.0, FilterType.BELL),
            EQBand(1000, 0, 1.0, FilterType.BELL),
            EQBand(4000, -2, 1.2, FilterType.BELL),
            EQBand(12000, -3, 0.7, FilterType.HIGH_SHELF),
        ],
        'radio': [
            EQBand(80, -12, 0.7, FilterType.HIGH_PASS),
            EQBand(300, 6, 1.5, FilterType.BELL),
            EQBand(3000, 4, 1.0, FilterType.BELL),
            EQBand(10000, -8, 0.7, FilterType.LOW_PASS),
        ],
        'mastering': [
            EQBand(30, -2, 0.5, FilterType.LOW_SHELF),
            EQBand(120, 1, 0.8, FilterType.BELL),
            EQBand(2000, -0.5, 1.5, FilterType.BELL),
            EQBand(8000, 1.5, 1.0, FilterType.BELL),
            EQBand(16000, 1, 0.7, FilterType.HIGH_SHELF),
        ]
    }
    
    def __init__(self, sample_rate: int = 44100, num_bands: int = 5):
        """
        Initialize parametric equalizer.
        
        Args:
            sample_rate: Audio sample rate in Hz
            num_bands: Number of EQ bands
        """
        self.sample_rate = sample_rate
        self.bands: List[EQBand] = []
        
        # Initialize with flat response
        self.load_preset('flat')
        
        # Filter state variables (for each band and channel)
        self.filter_states = {}
    
    def load_preset(self, preset_name: str):
        """
        Load a preset EQ configuration.
        
        Args:
            preset_name: Name of preset to load
        
        Raises:
            ValueError: If preset not found
        """
        if preset_name not in self.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.PRESETS.keys())}")
        
        self.bands = [EQBand(**band.__dict__) for band in self.PRESETS[preset_name]]
        self._reset_filter_states()
    
    def set_band(self, index: int, frequency: float = None, gain: float = None, 
                 q: float = None, filter_type: FilterType = None, enabled: bool = None):
        """
        Update parameters for a specific band.
        
        Args:
            index: Band index (0-based)
            frequency: Center frequency in Hz
            gain: Gain in dB
            q: Quality factor
            filter_type: Type of filter
            enabled: Enable/disable band
        """
        if index >= len(self.bands):
            raise ValueError(f"Band index {index} out of range (0-{len(self.bands)-1})")
        
        band = self.bands[index]
        if frequency is not None:
            band.frequency = max(20, min(20000, frequency))
        if gain is not None:
            band.gain = max(-20, min(20, gain))
        if q is not None:
            band.q = max(0.1, min(10, q))
        if filter_type is not None:
            band.filter_type = filter_type
        if enabled is not None:
            band.enabled = enabled
    
    def _reset_filter_states(self):
        """Reset all filter states"""
        self.filter_states = {}
    
    def _calculate_biquad_coefficients(self, band: EQBand) -> Dict[str, float]:
        """
        Calculate biquad filter coefficients for a band.
        
        Args:
            band: EQ band configuration
        
        Returns:
            Dictionary with filter coefficients
        """
        # Normalized frequency
        omega = 2 * np.pi * band.frequency / self.sample_rate
        sin_omega = np.sin(omega)
        cos_omega = np.cos(omega)
        
        # Linear gain
        A = 10 ** (band.gain / 40)  # Divide by 40 for amplitude (not power)
        
        # Alpha (bandwidth parameter)
        alpha = sin_omega / (2 * band.q)
        
        # Initialize coefficients
        b0, b1, b2, a0, a1, a2 = 1, 0, 0, 1, 0, 0
        
        if band.filter_type == FilterType.BELL:
            # Peaking EQ
            b0 = 1 + alpha * A
            b1 = -2 * cos_omega
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * cos_omega
            a2 = 1 - alpha / A
            
        elif band.filter_type == FilterType.LOW_SHELF:
            # Low shelf
            beta = np.sqrt(A) / band.q
            b0 = A * ((A + 1) - (A - 1) * cos_omega + beta * sin_omega)
            b1 = 2 * A * ((A - 1) - (A + 1) * cos_omega)
            b2 = A * ((A + 1) - (A - 1) * cos_omega - beta * sin_omega)
            a0 = (A + 1) + (A - 1) * cos_omega + beta * sin_omega
            a1 = -2 * ((A - 1) + (A + 1) * cos_omega)
            a2 = (A + 1) + (A - 1) * cos_omega - beta * sin_omega
            
        elif band.filter_type == FilterType.HIGH_SHELF:
            # High shelf
            beta = np.sqrt(A) / band.q
            b0 = A * ((A + 1) + (A - 1) * cos_omega + beta * sin_omega)
            b1 = -2 * A * ((A - 1) + (A + 1) * cos_omega)
            b2 = A * ((A + 1) + (A - 1) * cos_omega - beta * sin_omega)
            a0 = (A + 1) - (A - 1) * cos_omega + beta * sin_omega
            a1 = 2 * ((A - 1) - (A + 1) * cos_omega)
            a2 = (A + 1) - (A - 1) * cos_omega - beta * sin_omega
            
        elif band.filter_type == FilterType.LOW_PASS:
            # Low pass
            b0 = (1 - cos_omega) / 2
            b1 = 1 - cos_omega
            b2 = (1 - cos_omega) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_omega
            a2 = 1 - alpha
            
        elif band.filter_type == FilterType.HIGH_PASS:
            # High pass
            b0 = (1 + cos_omega) / 2
            b1 = -(1 + cos_omega)
            b2 = (1 + cos_omega) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_omega
            a2 = 1 - alpha
            
        elif band.filter_type == FilterType.NOTCH:
            # Notch filter
            b0 = 1
            b1 = -2 * cos_omega
            b2 = 1
            a0 = 1 + alpha
            a1 = -2 * cos_omega
            a2 = 1 - alpha
        
        # Normalize coefficients
        return {
            'b0': b0 / a0,
            'b1': b1 / a0,
            'b2': b2 / a0,
            'a1': a1 / a0,
            'a2': a2 / a0
        }
    
    def _apply_biquad_filter(self, audio: np.ndarray, coeffs: Dict[str, float], 
                            state_key: str) -> np.ndarray:
        """
        Apply biquad filter to audio.
        
        Args:
            audio: Input audio samples
            coeffs: Filter coefficients
            state_key: Key for storing filter state
        
        Returns:
            Filtered audio
        """
        # Initialize state if needed
        if state_key not in self.filter_states:
            self.filter_states[state_key] = {'x1': 0, 'x2': 0, 'y1': 0, 'y2': 0}
        
        state = self.filter_states[state_key]
        output = np.zeros_like(audio)
        
        b0, b1, b2 = coeffs['b0'], coeffs['b1'], coeffs['b2']
        a1, a2 = coeffs['a1'], coeffs['a2']
        
        for i in range(len(audio)):
            # Biquad difference equation
            x = audio[i]
            y = b0 * x + b1 * state['x1'] + b2 * state['x2'] - a1 * state['y1'] - a2 * state['y2']
            
            # Update state
            state['x2'] = state['x1']
            state['x1'] = x
            state['y2'] = state['y1']
            state['y1'] = y
            
            output[i] = y
        
        return output
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Process audio through all EQ bands.
        
        Args:
            audio: Input audio (mono or stereo)
        
        Returns:
            Equalized audio
        """
        # Ensure audio is 2D
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        
        channels, samples = audio.shape
        output = audio.copy()
        
        # Process each band
        for band_idx, band in enumerate(self.bands):
            if not band.enabled or band.gain == 0:
                continue
            
            # Calculate filter coefficients
            coeffs = self._calculate_biquad_coefficients(band)
            
            # Apply to each channel
            for channel in range(channels):
                state_key = f"band{band_idx}_ch{channel}"
                output[channel] = self._apply_biquad_filter(
                    output[channel], coeffs, state_key
                )
        
        return output if audio.ndim == 2 else output[0]
    
    def get_frequency_response(self, frequencies: np.ndarray = None) -> np.ndarray:
        """
        Calculate frequency response of current EQ settings.
        
        Args:
            frequencies: Array of frequencies to evaluate (Hz)
        
        Returns:
            Magnitude response in dB for each frequency
        """
        if frequencies is None:
            frequencies = np.logspace(1, 4.3, 1000)  # 10 Hz to 20 kHz
        
        response = np.zeros(len(frequencies))
        
        for band in self.bands:
            if not band.enabled:
                continue
            
            coeffs = self._calculate_biquad_coefficients(band)
            
            # Calculate frequency response for this band
            omega = 2 * np.pi * frequencies / self.sample_rate
            
            # Transfer function H(z) = (b0 + b1*z^-1 + b2*z^-2) / (1 + a1*z^-1 + a2*z^-2)
            z = np.exp(1j * omega)
            numerator = coeffs['b0'] + coeffs['b1'] / z + coeffs['b2'] / (z ** 2)
            denominator = 1 + coeffs['a1'] / z + coeffs['a2'] / (z ** 2)
            
            H = numerator / denominator
            magnitude_db = 20 * np.log10(np.abs(H))
            
            response += magnitude_db
        
        return response
    
    def get_bands_info(self) -> List[Dict]:
        """Get information about all bands"""
        return [
            {
                'index': i,
                'frequency': band.frequency,
                'gain': band.gain,
                'q': band.q,
                'type': band.filter_type.value,
                'enabled': band.enabled
            }
            for i, band in enumerate(self.bands)
        ]


# Example usage
if __name__ == "__main__":
    # Create EQ
    eq = ParametricEqualizer(sample_rate=44100)
    
    # Load preset
    eq.load_preset('vocal_clarity')
    
    # Or customize
    eq.set_band(0, frequency=80, gain=3, q=0.7)
    eq.set_band(1, frequency=3000, gain=5, q=1.5)
    
    # Process audio
    # audio_input = np.random.randn(44100)
    # audio_output = eq.process(audio_input)
    
    # Get frequency response
    freqs = np.logspace(1, 4.3, 1000)
    response = eq.get_frequency_response(freqs)
