from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from typing import Generator, Optional

from .config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def init_db():
    """Initialize the database."""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db() -> Generator:
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class ProcessingJob(Base):
    """Database model for audio processing jobs."""
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    status = Column(String, default="queued", nullable=False)
    progress = Column(Float, default=0.0, nullable=False)
    format = Column(String, default="mp3", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status,
            "progress": self.progress,
            "format": self.format,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Initialize database tables
Base.metadata.create_all(bind=engine)
