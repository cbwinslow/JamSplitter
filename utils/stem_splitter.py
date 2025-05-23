#!/usr/bin/env python3
  """
  stem_splitter.py ───────────────────────── Produce stems via yt-dlp + Spleeter
  Author : ChatGPT for CBW  ✦ 2025-05-23
  ModLog : 2025-05-23 Updated for yt-dlp + FastAPI readiness
  """
  import os
  import logging
  from spleeter.separator import Separator
  from rich.console import Console
  from rich.progress import SpinnerColumn, TextColumn, Progress
  from utils.cache import init_cache, get_cached_stems, cache_stems
  import yt_dlp
  
  logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
  console = Console()
  
  def split_stems(youtube_url: str, output_dir: str) -> dict:
      console.log(f"[bold]Processing URL:[/bold] {youtube_url}")
  
      conn = init_cache()
      cached = get_cached_stems(youtube_url, conn)
      if cached:
          console.log("[green]Using cached stems[/green]")
          return cached
  
      os.makedirs(output_dir, exist_ok=True)
      audio_path = os.path.join(output_dir, "audio.mp4")
  
      # Download via yt-dlp
      ydl_opts = {"format": "bestaudio", "outtmpl": audio_path}
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
          console.log("Downloading audio with yt-dlp...")
          ydl.download([youtube_url])
  
      # Separation with Spleeter and Rich spinner
      with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
          sep = progress.add_task("Separating stems...", total=None)
          separator = Separator("spleeter:4stems")
          separator.separate_to_file(audio_path, output_dir)
          progress.stop_task(sep)
  
      stems = {}
      stem_dir = os.path.join(output_dir, "audio")
      for fname in os.listdir(stem_dir):
          stems[fname.replace(".wav", "")] = os.path.join(stem_dir, fname)
      console.log(f"[green]Generated stems:[/green] {list(stems.keys())}")
  
      cache_stems(youtube_url, stems, conn)
      return stems
