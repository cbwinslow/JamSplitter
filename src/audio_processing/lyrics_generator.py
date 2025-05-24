"""Module for generating lyrics from audio using Whisper.

This module provides functionality to transcribe audio files and generate
synchronized lyrics with timestamps using OpenAI's Whisper model.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar, cast

import torch

# Type variable for generic typing
T = TypeVar('T')

# Conditional import for Whisper
whisper_available = False
Whisper = object  # type: ignore[assignment, misc, valid-type]

try:
    import whisper
    from whisper import Whisper as WhisperModel
    whisper_available = True
    Whisper = WhisperModel
except ImportError:
    pass

def is_whisper_available() -> bool:
    """Check if Whisper is available for use.
    
    Returns:
        bool: True if Whisper is available, False otherwise
    """
    return whisper_available

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LyricSegment:
    """A single lyric segment with timestamps.
    
    Attributes:
        text: The text content of the lyric segment
        start: Start time in seconds
        end: End time in seconds
    """
    text: str
    start: float
    end: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the segment to a dictionary.
        
        Returns:
            Dict containing text, start, and end time of the segment
        """
        return {
            'text': self.text,
            'start': round(self.start, 2),
            'end': round(self.end, 2)
        }

class LyricsGenerator:
    """Handles lyrics generation from audio using Whisper.
    
    This class provides methods to transcribe audio files and generate
    synchronized lyrics with timestamps using OpenAI's Whisper model.
    """
    
    def __init__(self, model_name: str = "large-v2") -> None:
        """Initialize the Whisper model.
        
        Args:
            model_name: Name of the Whisper model to use.
                Options: 'tiny', 'base', 'small', 'medium', 'large', 'large-v2'
            
        Raises:
            ImportError: If Whisper is not installed
            RuntimeError: If model loading fails
        """
        if not is_whisper_available():
            raise ImportError(
                "Whisper is not installed. "
                "Please install it with: pip install openai-whisper"
            )
            
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self._model: Optional[Whisper] = None  # type: ignore[valid-type]  # Conditional import
        
    @property
    def model(self) -> Whisper:  # type: ignore[valid-type, no-any-return]
        """Lazy load and return the Whisper model.
        
        Returns:
            The loaded Whisper model instance
            
        Raises:
            RuntimeError: If model loading fails
        """
        if self._model is None:
            if not _WHISPER_AVAILABLE:
                raise ImportError("Whisper is not available. Please install it first.")
                
            try:
                self._model = whisper.load_model(  # type: ignore[attr-defined]
                    self.model_name, 
                    device=self.device
                )
                logger.info("Successfully loaded Whisper model: %s", self.model_name)
            except Exception as e:
                error_msg = f"Failed to load Whisper model: {str(e)}"
                logger.exception(error_msg)
                raise RuntimeError(error_msg) from e
        return self._model

    def _safe_get(self, data: Dict[str, Any], key: str, default: T = None) -> T:  # type: ignore[assignment]
        """Safely get a value from a dictionary with type checking.
        
        Args:
            data: Dictionary to get value from
            key: Key to look up in the dictionary
            default: Default value to return if key is not found or value is None
            
        Returns:
            The value from the dictionary or the default value
        """
        value = data.get(key, default)
        if value is None and default is not None:
            return default
        return cast(T, value)

    async def generate_lyrics(
        self,
        audio_path: Path,
        language: str = "en",
    ) -> List[LyricSegment]:
        """Generate synchronized lyrics from audio file.
        
        Args:
            audio_path: Path to the audio file to transcribe
            language: ISO 639-1 language code (e.g., 'en' for English, 'es' for Spanish)
            
        Returns:
            List of LyricSegment objects containing the transcribed text with timestamps
            
        Raises:
            FileNotFoundError: If the specified audio file doesn't exist
            ValueError: If the audio file is empty or invalid
            RuntimeError: If transcription fails for any reason
        """
        if not audio_path.exists():
            error_msg = f"Audio file not found: {audio_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        try:
            logger.info("Loading audio file: %s", audio_path)
            
            # Load audio using Whisper's utility function
            audio = whisper.load_audio(str(audio_path))  # type: ignore[attr-defined]
            audio_size = len(audio) if hasattr(audio, '__len__') else 0
            if audio_size == 0:
                raise ValueError("Empty or invalid audio file")

            logger.info("Starting transcription with %s model...", self.model_name)
            
            # Run transcription
            result = self.model.transcribe(  # type: ignore[attr-defined]
                audio,
                verbose=logger.isEnabledFor(logging.DEBUG),
                language=language,
                fp16=torch.cuda.is_available()
            )

            logger.info("Formatting lyrics with timestamps")
            segments = self._safe_get(result, "segments", [])
            if not isinstance(segments, list):
                logger.warning("Unexpected segments format: %s", type(segments).__name__)
                return []

            lyrics: List[LyricSegment] = []
            
            for segment in segments:
                if not isinstance(segment, dict):
                    logger.debug("Skipping invalid segment: %s", segment)
                    continue
                
                text = str(self._safe_get(segment, "text", "")).strip()
                if not text:
                    continue
                
                try:
                    start = float(self._safe_get(segment, "start", 0.0))
                    end = float(self._safe_get(segment, "end", 0.0))
                    
                    # Validate timestamps
                    if start < 0 or end <= 0 or end < start:
                        logger.warning("Invalid timestamps: start=%s, end=%s", start, end)
                        continue
                        
                    lyric_seg = LyricSegment(
                        text=text,
                        start=start,
                        end=end
                    )
                    lyrics.append(lyric_seg)
                    
                except (TypeError, ValueError) as e:
                    logger.warning("Invalid segment format: %s - %s", segment, e)
                    continue

            logger.info("Generated %d lyric segments", len(lyrics))
            return lyrics

        except Exception as e:
            error_msg = f"Failed to generate lyrics: {str(e)}"
            logger.exception(error_msg)
            raise RuntimeError(error_msg) from e
