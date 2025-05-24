import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class AudioProcessor:
    """Handles audio processing tasks like downloading and splitting audio."""
    
    def __init__(self):
        self.output_dir = Path(settings.OUTPUT_FOLDER)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_audio(self, url: str, output_path: Path) -> bool:
        """Download audio from a YouTube URL."""
        try:
            cmd = [
                "yt-dlp",
                "-x",  # Extract audio
                "--audio-format", "wav",
                "-o", str(output_path),
                url
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"Failed to download audio: {stderr.decode()}")
                return False
                
            return output_path.exists()
            
        except Exception as e:
            logger.error(f"Error downloading audio: {str(e)}")
            return False
    
    async def split_audio(self, input_path: Path, output_dir: Path) -> Dict[str, Path]:
        """Split audio into stems using Demucs."""
        try:
            cmd = [
                "demucs",
                "--two-stems=vocals",
                "-n", "htdemucs",
                "-o", str(output_dir),
                str(input_path)
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"Failed to split audio: {stderr.decode()}")
                return {}
            
            # Return paths to the split stems
            return {
                "vocals": output_dir / "htdemucs" / f"{input_path.stem}" / "vocals.wav",
                "instrumental": output_dir / "htdemucs" / f"{input_path.stem}" / "no_vocals.wav"
            }
            
        except Exception as e:
            logger.error(f"Error splitting audio: {str(e)}")
            return {}
    
    async def convert_format(self, input_path: Path, output_format: str) -> Optional[Path]:
        """Convert audio file to the specified format."""
        try:
            output_path = input_path.with_suffix(f".{output_format}")
            
            cmd = [
                "ffmpeg",
                "-i", str(input_path),
                "-vn",
                "-ar", "44100",
                "-ac", "2",
                "-b:a", "192k",
                "-y",  # Overwrite output file if it exists
                str(output_path)
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await result.communicate()
            
            if result.returncode != 0 or not output_path.exists():
                return None
                
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting audio format: {str(e)}")
            return None
