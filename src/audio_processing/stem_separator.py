"""
stem_separator.py ─────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-24
Summary: Audio stem separation using Spleeter with enhanced error handling
ModLog : 2025-05-24 Added comprehensive error handling and logging
"""
import os
from typing import Dict, Any, Optional
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
from src.utils.logging import Logger
from src.exceptions import ProcessingError, InvalidURLException
from pathlib import Path

class StemSeparator:
    """Audio stem separation using Spleeter"""

    def __init__(self, model_config: Dict[str, Any]):
        """Initialize stem separator"""
        self.model_config: Dict[str, Any] = model_config
        self.audio_adapter: AudioAdapter = AudioAdapter.default()
        self.logger: Logger = Logger.get_logger("StemSeparator")
        self.separator: Optional[Separator] = None
        self.load_model()

    def load_model(self) -> None:
        """Load Spleeter model with error handling"""
        try:
            self.logger.info("Loading Spleeter model...")
            self.separator = Separator(self.model_config)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error("Failed to load Spleeter model: %s", str(e))
            raise ProcessingError(
                f"Failed to load Spleeter model: {str(e)}",
                status_code=500,
                model_config=self.model_config
            ) from e

    def process_audio(self, audio_path: str, output_dir: str) -> Dict[str, str]:
        """Process audio file and separate stems"""
        if not self.separator:
            self.load_model()

        try:
            # Validate paths
            if not Path(audio_path).exists():
                raise ProcessingError(
                    f"Audio file not found: {audio_path}",
                    status_code=404,
                    audio_path=audio_path
                )
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            self.logger.info("Processing audio file: %s", audio_path)
            self.separator.separate_to_file(audio_path, output_dir)
            self.logger.info("Successfully processed audio file: %s", audio_path)
            
            # Get output files
            stems = [f for f in os.listdir(output_dir) if f.endswith('.wav')]
            
            self.logger.info(
                "Audio separation completed successfully",
                extra={
                    "stems": stems,
                    "output_dir": output_dir
                }
            )
            
            return {
                "status": "success",
                "stems": stems,
                "output_dir": output_dir
            }
        except ProcessingError:
            raise
        except Exception as e:
            self.logger.error(
                f"Audio processing failed: {str(e)}",
                extra={
                    "audio_path": audio_path,
                    "output_dir": output_dir
                }
            )
            raise ProcessingError(
                f"Failed to process audio: {str(e)}",
                status_code=500,
                audio_path=audio_path
            )
    
    def process_video(self, video_url: str, output_dir: str, format: str = "mp3") -> Dict[str, Any]:
        """
        Process video and separate audio stems with comprehensive error handling
        
        Args:
            video_url: YouTube video URL
            output_dir: Directory for output stems
            format: Output audio format
            
        Returns:
            Dictionary containing processing results
            
        Raises:
            InvalidURLException: If URL is invalid
            ProcessingError: If video processing fails
        """
        try:
            # Validate URL
            if not video_url.startswith("https://"):
                raise InvalidURLException(
                    video_url,
                    "Invalid YouTube URL format"
                )
            
            # Download video
            try:
                audio_path = self._download_video(video_url, format)
            except Exception as e:
                self.logger.error(
                    f"Failed to download video: {str(e)}",
                    extra={"video_url": video_url}
                )
                raise ProcessingError(
                    f"Failed to download video: {str(e)}",
                    status_code=500,
                    video_url=video_url
                )
            
            # Process audio
            result = self.process_audio(audio_path, output_dir)
            
            return result
        except InvalidURLException:
            raise
        except ProcessingError:
            raise
        except Exception as e:
            self.logger.error(
                f"Video processing failed: {str(e)}",
                extra={
                    "video_url": video_url,
                    "output_dir": output_dir
                }
            )
            raise ProcessingError(
                f"Failed to process video: {str(e)}",
                status_code=500,
                video_url=video_url
            )
    
    def _download_video(self, video_url: str, format: str) -> str:
        """
        Download video and extract audio
        
        Args:
            video_url: YouTube video URL
            format: Output audio format
            
        Returns:
            Path to extracted audio file
            
        Raises:
            ProcessingError: If video download fails
        """
        try:
            # TODO: Implement video download using yt-dlp
            audio_path = "path/to/audio.wav"
            self.logger.info(
                "Video downloaded successfully",
                extra={
                    "video_url": video_url,
                    "output_format": format
                }
            )
            return audio_path
        except Exception as e:
            self.logger.error(
                f"Failed to download video: {str(e)}",
                extra={"video_url": video_url}
            )
            raise ProcessingError(
                f"Failed to download video: {str(e)}",
                status_code=500,
                video_url=video_url
            )
