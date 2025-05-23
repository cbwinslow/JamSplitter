#!/usr/bin/env python3
"""
stem_splitter.py ──────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: Download audio from a YouTube URL and separate into stems
Inputs : youtube_url (str), output_dir (str)
Outputs: dict of {stem_name: filepath}
Usage  : from utils.stem_splitter import split_stems; split_stems(url, 'out/')
Logs   : INFO to stdout, with Rich progress
ModLog : 2025-05-23  Added Rich progress & SQLite caching
"""

import os
import logging
from pytube import YouTube
from spleeter.separator import Separator
from rich.console import Console
from rich.progress import SpinnerColumn, TextColumn, Progress
from utils.cache import init_cache, get_cached_stems, cache_stems

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
console = Console()

def split_stems(youtube_url: str, output_dir: str) -> dict:
    """
    Downloads the highest-quality audio from YouTube and uses Spleeter to separate stems.
    Shows progress spinners and caches results in a local SQLite DB.
    Returns a dict mapping stem names to file paths.
    """
    console.log(f"[bold]Processing URL:[/bold] {youtube_url}")

    # Initialize cache and check if we've already processed this URL
    conn = init_cache()
    cached = get_cached_stems(youtube_url, conn)
    if cached:
        console.log("[green]Using cached stems[/green]")
        return cached

    # Download + separation with spinners
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        # 1) Download audio
        dl_task = progress.add_task("Downloading audio...", total=None)
        yt = YouTube(youtube_url)
        audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
        if not audio_stream:
            raise RuntimeError("No audio stream found")
        os.makedirs(output_dir, exist_ok=True)
        audio_path = os.path.join(output_dir, "audio.mp4")
        audio_stream.download(output_path=output_dir, filename="audio.mp4")
        progress.stop_task(dl_task)

        # 2) Separate stems
        sep_task = progress.add_task("Separating stems...", total=None)
        separator = Separator("spleeter:4stems")
        separator.separate_to_file(audio_path, output_dir)
        progress.stop_task(sep_task)

    # Map output files
    stems = {}
    stem_dir = os.path.join(output_dir, "audio")
    for fname in os.listdir(stem_dir):
        stems[fname.replace(".wav", "")] = os.path.join(stem_dir, fname)
    console.log(f"[green]Generated stems:[/green] {list(stems.keys())}")

    # Cache results
    cache_stems(youtube_url, stems, conn)
    return stems
