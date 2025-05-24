"""Health check routes for the JamSplitter API."""
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.utils.database import get_db
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

def check_database_health(db: Session) -> bool:
    """Check if the database is accessible."""
    try:
        # Execute a simple query to check database connectivity
        db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database health check failed: %s", str(e))
        return False

@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint that verifies the API and database connectivity.
    
    Returns:
        dict: A dictionary containing the health status and timestamp.
        
    Raises:
        HTTPException: If the health check fails.
    """
    try:
        # Check database connection
        database_ok = check_database_health(db)
        
        if not database_ok:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed"
            )
            
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "database": "connected"
            },
            "version": "1.0.0"
        }
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions with proper status code
        raise http_exc
        
    except Exception as exc:
        # Log unexpected errors and return 503
        error_msg = f"Health check failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": "Service unavailable",
                "details": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ) from exc
