"""JamSplitter application package."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .utils.database import init_db
from .routes import router as api_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Initialize the database
    init_db()
    
    # Create the FastAPI application
    app = FastAPI(
        title="JamSplitter API",
        description="API for splitting audio files into stems",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    return app

# Create the application instance
app = create_app()

# This allows the app to be run with `python -m app`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
