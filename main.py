#!/usr/bin/env python3
"""
main.py ───────────────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: Entry point for the JamSplitter AI agent
Inputs : None (reads env OPENAI_API_KEY)
Outputs: Interactive CLI agent session
ModLog : 2025-05-23  Initial version
"""

import os
import logging
from langchain import OpenAI, LLMChain
from langchain.agents import initialize_agent, AgentType
from tools.youtube_stem_tool import YouTubeStemTool
from tools.spotify_tool import SpotifyTool
from tools.lyrics_tool import LyricsTool
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
import asyncio

# Load environment
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in your environment")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
console = Console()

"""
JamSplitter - Main application entry point.

This module serves as the entry point for running the JamSplitter application.
It uses the application factory pattern to create and configure the FastAPI app.

Usage:
    python -m jamsplitter
    or
    uvicorn app.main:app --reload
"""
import uvicorn
from app import create_app

# Create the FastAPI application
app = create_app()

def main():
    """Initialize the LangChain agent and run a prompt loop."""
    llm = OpenAI(temperature=0)
    tools = [
        YouTubeStemTool(),
        SpotifyTool(),
        LyricsTool()
    ]
    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    console.print(Panel.fit(
        "[bold green]JamSplitter Agent[/bold green]\n"
        "[yellow]Features:[/yellow]\n"
        "- YouTube video/stem downloader\n"
        "- Spotify integration\n"
        "- Karaoke lyrics generation\n"
        "- GPU-accelerated processing\n"
        "- Interactive TUI\n"
        "- Web interface\n"
        "- PostgreSQL database\n"
        "- Docker support\n"
        "\nType 'help' for available commands",
        title="Welcome to JamSplitter",
        border_style="green"
    ))

    while True:
        user_input = input("\n>> ")
        if user_input.lower().strip() in {"exit", "quit"}:
            console.print("[green]Goodbye![/green]")
            break
        elif user_input.lower().strip() == "help":
            console.print(Panel.fit(
                "[bold]Available Commands:[/bold]\n"
                "- [cyan]download[/cyan] <youtube_url> - Download and process a YouTube video\n"
                "- [cyan]channel[/cyan] <channel_url> - Process all videos from a YouTube channel\n"
                "- [cyan]karaoke[/cyan] <video_url> - Generate karaoke version\n"
                "- [cyan]status[/cyan] - Show processing status\n"
                "- [cyan]help[/cyan] - Show this help message",
                title="[bold]Help Menu[/bold]",
                border_style="cyan"
            ))
            continue

        try:
            with Progress(console=console) as progress:
                task = progress.add_task("[cyan]Processing...[/cyan]", start=False)
                result = agent.run(user_input)
                progress.update(task, visible=False)
                console.print(f"[green]Result:[/green]\n{result}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")

if __name__ == "__main__":
    main()
