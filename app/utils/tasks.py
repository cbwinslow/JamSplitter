import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Awaitable
from pathlib import Path
import logging

from .database import ProcessingJob, get_db
from .audio_processor import AudioProcessor

logger = logging.getLogger(__name__)


class TaskManager:
    """Manages background tasks for audio processing."""
    
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
        self.audio_processor = AudioProcessor()
    
    async def process_audio_task(self, job_id: str, url: str, output_format: str):
        """Background task to process audio."""
        db = next(get_db())
        try:
            # Update job status to processing
            job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return
                
            job.status = "processing"
            job.progress = 0.1
            db.commit()
            
            # Create a temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Download audio
                audio_path = temp_path / "audio.wav"
                if not await self.audio_processor.download_audio(url, audio_path):
                    job.status = "failed"
                    job.progress = 0
                    db.commit()
                    return
                    
                job.progress = 0.3
                db.commit()
                
                # Split audio
                stems = await self.audio_processor.split_audio(audio_path, temp_path)
                if not stems:
                    job.status = "failed"
                    job.progress = 0
                    db.commit()
                    return
                    
                job.progress = 0.7
                db.commit()
                
                # Convert to desired format if needed
                output_paths = {}
                for stem_name, stem_path in stems.items():
                    if output_format != "wav":
                        converted_path = await self.audio_processor.convert_format(
                            stem_path, output_format
                        )
                        if converted_path:
                            output_paths[stem_name] = converted_path
                    else:
                        output_paths[stem_name] = stem_path
                
                # Move files to final location
                final_paths = {}
                for stem_name, stem_path in output_paths.items():
                    final_path = self.audio_processor.output_dir / f"{job_id}_{stem_name}.{output_format}"
                    stem_path.rename(final_path)
                    final_paths[stem_name] = final_path
                
                job.progress = 1.0
                job.status = "completed"
                db.commit()
                
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            job.status = "failed"
            db.commit()
            
        finally:
            db.close()
    
    async def create_job(self, url: str, output_format: str = "mp3") -> Optional[str]:
        """Create a new processing job."""
        db = next(get_db())
        try:
            job = ProcessingJob(
                url=url,
                status="queued",
                format=output_format,
                progress=0.0
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            
            # Start processing task
            task = asyncio.create_task(self.process_audio_task(str(job.id), url, output_format))
            self.tasks[str(job.id)] = task
            
            return str(job.id)
            
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            db.rollback()
            return None
            
        finally:
            db.close()
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a job."""
        db = next(get_db())
        try:
            job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            if not job:
                return None
                
            return job.to_dict()
            
        finally:
            db.close()
    
    def get_all_jobs(self) -> list[Dict[str, Any]]:
        """Get all jobs."""
        db = next(get_db())
        try:
            jobs = db.query(ProcessingJob).order_by(ProcessingJob.created_at.desc()).all()
            return [job.to_dict() for job in jobs]
            
        finally:
            db.close()

# Global task manager instance
task_manager = TaskManager()
