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
from dotenv import load_dotenv

# Load environment
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in your environment")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    """Initialize the LangChain agent and run a prompt loop."""
    llm = OpenAI(temperature=0)
    tools = [YouTubeStemTool()]
    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    logging.info("JamSplitter Agent ready. Ask me to separate stems from a YouTube URL!")
    while True:
        user_input = input("\n>> ")
        if user_input.lower().strip() in {"exit", "quit"}:
            print("Goodbye!")
            break
        result = agent.run(user_input)
        print(result)

if __name__ == "__main__":
    main()
