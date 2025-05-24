import whisper
import torch
from typing import List, Dict
from pathlib import Path

class LyricsGenerator:
    def __init__(self):
        """Initialize the Whisper model"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model("large-v2", device=self.device)

    async def generate_lyrics(self, audio_path: Path) -> List[Dict]:
        """Generate synchronized lyrics using Whisper"""
        try:
            # Load audio
            audio = whisper.load_audio(str(audio_path))
            
            # Transcribe with timestamps
            result = self.model.transcribe(
                audio,
                verbose=True,
                language="en",
                fp16=torch.cuda.is_available()
            )
            
            # Format lyrics with timestamps
            lyrics = []
            for segment in result["segments"]:
                lyrics.append({
                    "text": segment["text"],
                    "start": segment["start"],
                    "end": segment["end"]
                })
            
            return lyrics
            
        except Exception as e:
            print(f"Error generating lyrics: {str(e)}")
            return []
