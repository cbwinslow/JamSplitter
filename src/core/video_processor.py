import yt_dlp
import ffmpeg
import os
from pathlib import Path
from typing import Dict, Any
from src.database import Database
from src.audio_processing.stem_separator import StemSeparator
from src.audio_processing.lyrics_generator import LyricsGenerator

class VideoProcessor:
    def __init__(self, db: Database, output_dir: str):
        self.db = db
        self.output_dir = Path(output_dir)
        self.stem_separator = StemSeparator()
        self.lyrics_generator = LyricsGenerator()
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'postprocessors': [
                {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            ]
        }

    def _progress_hook(self, d: Dict[str, Any]):
        if d['status'] == 'downloading':
            self.db.update_video_progress(d['filename'], d['downloaded_bytes'], d['total_bytes'])
        elif d['status'] == 'finished':
            self.db.mark_video_downloaded(d['filename'])

    async def process_video(self, url: str):
        """Process a single video URL"""
        try:
            # Download video
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = Path(info['requested_downloads'][0]['filepath'])

            # Separate stems
            stem_paths = await self.stem_separator.separate_stems(video_path)

            # Generate lyrics
            lyrics = await self.lyrics_generator.generate_lyrics(video_path)

            # Update database
            self.db.update_video_stems(video_path, stem_paths)
            self.db.update_video_lyrics(video_path, lyrics)

            return True
        except Exception as e:
            self.db.mark_video_failed(url, str(e))
            return False

    async def process_channel(self, channel_url: str):
        """Process all videos from a YouTube channel"""
        try:
            with yt_dlp.YoutubeDL({'extract_flat': True}) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                for entry in info['entries']:
                    if entry.get('_type') == 'url':
                        video_url = entry['url']
                        if not self.db.video_exists(video_url):
                            await self.process_video(video_url)
        except Exception as e:
            print(f"Error processing channel: {str(e)}")
