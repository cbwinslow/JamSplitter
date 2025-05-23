# Dockerfile ─────────────────────────────────────────────────────────────
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home agentuser
WORKDIR /home/agentuser/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R agentuser:agentuser .
USER agentuser
CMD ["python3", "main.py"]
