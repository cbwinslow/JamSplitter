from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

router = APIRouter(prefix="/api")

class SplitRequest(BaseModel):
    url: str
    format: str = "mp3"

class QueueItem(BaseModel):
    url: str
    status: str
    progress: float
    created_at: datetime
    updated_at: datetime

# In-memory storage for demo purposes
processing_queue: Dict[str, QueueItem] = {}

@router.post("/split")
async def process_audio(request: SplitRequest):
    """
    Process a YouTube URL to separate audio stems
    """
    # In a real app, this would start an async task to process the audio
    queue_item = QueueItem(
        url=request.url,
        status="queued",
        progress=0.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    processing_queue[request.url] = queue_item
    
    # Simulate processing
    # In a real app, you would start a background task here
    
    return {"status": "queued", "url": request.url}

@router.get("/queue", response_model=List[Dict])
async def get_queue():
    """
    Get the current processing queue
    """
    return [
        {
            "url": item.url,
            "status": item.status,
            "progress": item.progress,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat()
        }
        for item in processing_queue.values()
    ]

@router.get("/status/{url}")
async def get_status(url: str):
    """
    Get the status of a processing job
    """
    if url not in processing_queue:
        raise HTTPException(status_code=404, detail="URL not found in queue")
    
    item = processing_queue[url]
    return {
        "url": item.url,
        "status": item.status,
        "progress": item.progress,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat()
    }
