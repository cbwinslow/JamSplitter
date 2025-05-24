#!/usr/bin/env python3
"""
JamSplitter - Main entry point for the application.

This module serves as the entry point for running the JamSplitter application.
It initializes the FastAPI application and starts the Uvicorn server.

Usage:
    python -m jamsplitter
"""
import uvicorn

def main() -> None:
    """Run the JamSplitter application."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
