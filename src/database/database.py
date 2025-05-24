from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import psycopg2

class Database:
    def __init__(self, db_url: str):
        """Initialize database connection"""
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def execute(self, query: str, params: dict = None) -> Optional[list]:
        """Execute a raw SQL query"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                if result.returns_rows:
                    return result.fetchall()
                conn.commit()
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
            return None

    def get_video_info(self, url: str) -> Optional[dict]:
        """Get video information from database"""
        query = """
            SELECT * FROM videos WHERE url = :url
        """
        result = self.execute(query, {"url": url})
        if result:
            return dict(result[0])
        return None

    def update_video_progress(self, filename: str, downloaded: int, total: int):
        """Update video download progress"""
        query = """
            UPDATE videos 
            SET downloaded_bytes = :downloaded, total_bytes = :total, 
                updated_at = CURRENT_TIMESTAMP
            WHERE filename = :filename
        """
        self.execute(query, {
            "filename": filename,
            "downloaded": downloaded,
            "total": total
        })

    def mark_video_downloaded(self, filename: str):
        """Mark video as downloaded"""
        query = """
            UPDATE videos 
            SET download_status = 'completed', 
                updated_at = CURRENT_TIMESTAMP
            WHERE filename = :filename
        """
        self.execute(query, {"filename": filename})

    def update_video_stems(self, video_path: str, stem_paths: dict):
        """Update video stems in database"""
        query = """
            INSERT INTO stems (video_id, stem_type, file_path)
            VALUES (
                (SELECT id FROM videos WHERE filename = :video_path),
                :stem_type,
                :file_path
            )
        """
        for stem_type, path in stem_paths.items():
            self.execute(query, {
                "video_path": video_path,
                "stem_type": stem_type,
                "file_path": str(path)
            })

    def update_video_lyrics(self, video_path: str, lyrics: list):
        """Update video lyrics in database"""
        query = """
            INSERT INTO lyrics (video_id, line_number, lyrics, start_time, end_time)
            VALUES (
                (SELECT id FROM videos WHERE filename = :video_path),
                :line_number,
                :lyrics,
                :start_time,
                :end_time
            )
        """
        for i, line in enumerate(lyrics):
            self.execute(query, {
                "video_path": video_path,
                "line_number": i,
                "lyrics": line['text'],
                "start_time": line['start'],
                "end_time": line['end']
            })
