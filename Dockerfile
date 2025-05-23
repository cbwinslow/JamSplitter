# Dockerfile ─────────────────────────────────────────────────────────────
# Author : ChatGPT for CBW  ✦ 2025-05-23
# Summary: CPU container with FFmpeg installed

FROM python:3.11-slim

# Install FFmpeg for audio processing
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home agentuser
WORKDIR /home/agentuser/app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R agentuser:agentuser .

# Switch to non-root user and start CLI agent
USER agentuser
CMD ["python3", "main.py"]
