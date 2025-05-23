#!/usr/bin/env python3
"""
stem_splitter.py ──────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: Download audio from a YouTube URL and separate into stems
Inputs : youtube_url (str), output_dir (str)
Outputs: dict of {stem_name: filepath}
Usage  : from utils.stem_splitter import split_stems; split_stems(url, 'out/')
Logs   : INFO to stdout
ModLog : 2025-05-23  Initial version
"""

import os
import logging
from pytube import YouTube
from spleeter.separator import Separator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def split_stems(youtube_url: str, output_dir: str) -> dict:
    """
    Downloads the highest-quality audio from YouTube and uses Spleeter to separate stems.
    Returns a dict mapping stem names (e.g., 'vocals', 'drums') to file paths.
    """
    try:
        logging.info(f"Starting download of {youtube_url}")
        yt = YouTube(youtube_url)
        audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
        if not audio_stream:
            raise RuntimeError("No audio stream found")
        os.makedirs(output_dir, exist_ok=True)
        audio_path = os.path.join(output_dir, "audio.mp4")
        audio_stream.download(output_path=output_dir, filename="audio.mp4")
        logging.info(f"Downloaded audio to {audio_path}")

        logging.info("Separating stems with Spleeter 4-stem model")
        separator = Separator("spleeter:4stems")
        separator.separate_to_file(audio_path, output_dir)
        
        # Map stems to files
        stems = {}
        stem_dir = os.path.join(output_dir, "audio")
        for fname in os.listdir(stem_dir):
            stems[fname.replace(".wav", "")] = os.path.join(stem_dir, fname)
        logging.info(f"Generated stems: {list(stems.keys())}")
        return stems

    except Exception as e:
        logging.error(f"Error in split_stems: {e}")
        raise
