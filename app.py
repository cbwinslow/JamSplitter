#!/usr/bin/env python3
"""
app.py ───────────────────────────────────────────────────────────── FastAPI API
Author : ChatGPT for CBW  ✦ 2025-05-23
ModLog : 2025-05-23 Added FastAPI front-end and health check
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.stem_splitter import split_stems

app = FastAPI(title="JamSplitter API", version="1.0")

class SplitRequest(BaseModel):
    url: str
    output_dir: str = "out_api"

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/split")
def split(req: SplitRequest):
    try:
        result = split_stems(req.url, req.output_dir)
        return {"stems": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
