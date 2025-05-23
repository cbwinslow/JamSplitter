#!/usr/bin/env python3
"""
youtube_stem_tool.py ─────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: LangChain tool wrapping stem_splitter.split_stems
Inputs : youtube_url (str)
Outputs: JSON-serializable dict of stems
ModLog : 2025-05-23  Initial version
"""

from langchain.tools import BaseTool
from utils.stem_splitter import split_stems

class YouTubeStemTool(BaseTool):
    name = "youtube_stem_separator"
    description = (
        "Use this tool to separate a YouTube video into stems. Input should be a YouTube URL."
    )

    def _run(self, youtube_url: str) -> dict:
        # Runs stem separation and returns mapping
        return split_stems(youtube_url=youtube_url, output_dir="output_stems")

    async def _arun(self, youtube_url: str) -> dict:
        # Async support
        return split_stems(youtube_url=youtube_url, output_dir="output_stems")
