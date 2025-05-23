# Dockerfile ───────────────────────────────────────────────────────
# Author : ChatGPT for CBW  ✦ 2025-05-23
# Summary: Containerize the JamSplitter agent for one-step deployment
# Usage  : docker build -t jam-splitter-agent . && docker run --env OPENAI_API_KEY -it jam-splitter-agent
# ModLog : 2025-05-23 Initial version

FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home agentuser
WORKDIR /home/agentuser/app

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R agentuser:agentuser .
USER agentuser

# Entry point
CMD ["python", "main.py"]
