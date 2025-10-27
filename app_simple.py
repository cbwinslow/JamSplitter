#!/usr/bin/env python3
"""
app_simple.py - Simplified FastAPI web interface for JamSplitter
Author: ChatGPT for CBW ✦ 2025
Summary: FastAPI-based web interface without database dependencies
"""
import os
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="JamSplitter",
    version="1.0.0",
    description="Split audio files into stems with AI",
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Request/Response Models
class SplitRequest(BaseModel):
    url: str
    format: str = "mp3"

class ProcessingStatus(BaseModel):
    status: str
    progress: float = 0.0
    updated_at: str

# In-memory storage for processing status
processing_queue: Dict[str, ProcessingStatus] = {}

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Serve the about page"""
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/split")
async def split(req: SplitRequest):
    """Process a YouTube video and separate its stems"""
    try:
        # Add to processing queue
        processing_queue[req.url] = ProcessingStatus(
            status="queued",
            progress=0.0,
            updated_at=datetime.now().isoformat()
        )
        
        # Return immediate response
        return {
            "message": "Added to processing queue",
            "url": req.url,
            "format": req.format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{url:path}")
async def get_status(url: str):
    """Get processing status for a specific URL"""
    status = processing_queue.get(url)
    if status:
        return status.model_dump()
    return {"status": "not_found"}

@app.get("/api/queue")
async def get_queue():
    """Get list of all processing items"""
    return {
        url: status.model_dump() 
        for url, status in processing_queue.items()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
