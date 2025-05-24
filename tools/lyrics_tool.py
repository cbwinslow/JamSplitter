from langchain.tools import BaseTool
from typing import Dict, Any, List
from src.audio_processing.lyrics_generator import LyricsGenerator
import os

class LyricsTool(BaseTool):
    name = "lyrics_generator"
    description = "Generate synchronized lyrics and karaoke versions of songs"

    def __init__(self):
        super().__init__()
        self.generator = LyricsGenerator()

    def _run(self, url: str) -> Dict[str, Any]:
        """Generate lyrics and karaoke version"""
        try:
            # Generate lyrics
            lyrics = self.generator.generate_lyrics(url)
            
            # Format karaoke data
            karaoke_data = []
            current_line = None
            
            for line in lyrics:
                if current_line and line['start'] - current_line['end'] > 0.5:
                    karaoke_data.append(current_line)
                    current_line = None
                
                if not current_line:
                    current_line = {
                        'text': line['text'],
                        'start': line['start'],
                        'end': line['end']
                    }
                else:
                    current_line['end'] = line['end']
                    current_line['text'] += f" {line['text']}"
            
            if current_line:
                karaoke_data.append(current_line)
            
            return {
                'lyrics': lyrics,
                'karaoke': karaoke_data
            }
            
        except Exception as e:
            return {'error': str(e)}

    async def _arun(self, url: str) -> Dict[str, Any]:
        """Async version of _run"""
        return self._run(url)
