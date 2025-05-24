#!/usr/bin/env python3
"""
main.py - Main FastAPI application for JamSplitter
"""
import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError, HTTPException as StarletteHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
import logging
from typing import Optional

# Import routes
from app.routes import pages, api
from app.utils.config import get_settings
from app.utils.database import init_db, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="JamSplitter",
    description="Separate audio stems from music tracks",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Enable HTTPS redirection in production
if settings.ENVIRONMENT == 'production':
    app.add_middleware(HTTPSRedirectMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")

# Error handlers
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def server_error(request: Request, exc):
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request},
        status_code=500
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Root endpoint redirects to home page
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/")

# Event handlers
@app.on_event("startup")
async def startup():
    # Initialize database
    init_db()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutdown")

# This allows running with `python -m app.main`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
