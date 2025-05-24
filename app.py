#!/usr/bin/env python3
"""
app.py ───────────────────────────────────────────────────────────── FastAPI API
Author : ChatGPT for CBW  ✦ 2025-05-24
Summary: FastAPI-based web interface for JamSplitter with status tracking
ModLog : 2025-05-24 Added web interface and status tracking
"""
import os
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Optional
from utils.stem_splitter import split_stems
from src.database.database import Database

app = FastAPI(
    title="JamSplitter API",
    version="1.0",
    description="API for processing and separating YouTube audio stems",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class SplitRequest(BaseModel):
    url: str
    output_dir: str = "out_api"
    format: str = "mp3"

class ProcessingStatus:
    def __init__(self, db_url: str):
        self.db = Database(db_url)
        self.statuses: Dict[str, Dict] = {}

    def update_status(self, url: str, status: str, progress: float = 0.0):
        """Update processing status for a URL"""
        self.statuses[url] = {
            "status": status,
            "progress": progress,
            "updated_at": datetime.now().isoformat()
        }
        self.db.update_video_progress(url, progress * 100)

    def get_status(self, url: str) -> Optional[Dict]:
        """Get processing status for a URL"""
        return self.statuses.get(url)

# Initialize status tracker
status_tracker = ProcessingStatus("postgresql://postgres:postgres@postgres:5432/jamsplitter")

@app.get("/")
async def home(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/split")
async def split(req: SplitRequest):
    """Process a YouTube video and separate its stems"""
    try:
        # Update status
        status_tracker.update_status(req.url, "processing")
        
        # Process video
        result = split_stems(req.url, req.output_dir)
        
        # Update status
        status_tracker.update_status(req.url, "completed", 1.0)
        
        return {"stems": result}
    except Exception as e:
        status_tracker.update_status(req.url, "failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{url}")
async def get_status(url: str):
    """Get processing status for a specific URL"""
    status = status_tracker.get_status(url)
    if status:
        return JSONResponse(status)
    return JSONResponse({"status": "not_found"})

@app.get("/api/queue")
async def get_queue():
    """Get list of all processing items"""
    return JSONResponse(status_tracker.statuses)

@app.get("/api/docs")
def docs():
    """Redirect to API documentation"""
    return RedirectResponse(url="https://api.jamsplitter.com/docs")

@app.get("/api/redoc")
def redoc():
    """Redirect to API documentation"""
    return RedirectResponse(url="https://api.jamsplitter.com/redoc")
