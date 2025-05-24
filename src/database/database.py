# database.py ─────────────────────────────────────────────────────────────
# Author : ChatGPT for CBW  ✦ 2025-05-24
# Summary: Database operations for JamSplitter with enhanced error handling
# ModLog : 2025-05-24 Added comprehensive error handling and logging

import psycopg2
import logging
from typing import Dict, Any, Optional, Generator, List
from contextlib import contextmanager
from src.exceptions import DatabaseError
import psycopg2
import time
from typing import TYPE_CHECKING
from psycopg2 import extensions

# Type aliases for better readability
Connection = extensions.connection
Cursor = extensions.cursor

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "jam_splitter",
    "user": "postgres",
    "password": "postgres"
}
    'max_retries': 3,
    'retry_delay': 2
}

class Database:
    """Database operations handler with robust error handling"""

    def __init__(self, db_url: str):
        """Initialize database connection"""
        self.db_url: str = db_url
        self.conn: Optional[Connection] = None
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def __del__(self):
        """Clean up database connection on object destruction"""
        self.disconnect()

    def connect(self) -> None:
        """Connect to PostgreSQL database with retry logic"""
        max_retries = DB_CONFIG['max_retries']
        retry_delay = DB_CONFIG['retry_delay']

        for attempt in range(max_retries):
            try:
                self.logger.info("Attempting database connection (attempt %d/%d)...",
                           attempt + 1, max_retries)
                self.conn = psycopg2.connect(self.db_url)
                self.logger.info("Successfully connected to database")
                return
            except Exception as e:
                self.logger.error("Database connection attempt %d failed: %s",
                           attempt + 1, str(e))
                if attempt < max_retries - 1:
                    self.logger.info("Retrying in %d seconds...", retry_delay)
                    time.sleep(retry_delay)
                else:
                    raise DatabaseError(
                        f"Failed to connect to database after multiple attempts: {str(e)}",
                        status_code=500,
                        db_url=self.db_url
                    ) from e

    def disconnect(self) -> None:
        """Disconnect from database"""
        if self.conn:
            try:
                self.conn.close()
                self.logger.info("Database connection closed")
            except Exception as e:
                self.logger.error("Error closing database connection: %s", str(e))

    @contextmanager
    def get_cursor(self) -> Generator[psycopg2.extensions.cursor, None, None]:
        """Context manager for database cursor with error handling"""
        cursor: Optional[psycopg2.extensions.cursor] = None
        try:
            if not self.conn:
                self.connect()
            cursor = self.conn.cursor()
            yield cursor
        except Exception as e:
            self.logger.error("Cursor operation failed: %s", str(e))
            raise DatabaseError(
                f"Cursor operation failed: {str(e)}",
                status_code=500
            ) from e
        finally:
            if cursor:
                cursor.close()

    def disconnect(self) -> None:
        """Disconnect from database"""
        if self.conn:
            try:
                self.conn.close()
                self.logger.info("Database connection closed")
            except Exception as e:
                self.logger.error("Error closing database connection: %s", str(e))

    @contextmanager
    def get_cursor(self) -> Generator[psycopg2.extensions.cursor, None, None]:
        """Context manager for database cursor with error handling"""
        cursor: Optional[psycopg2.extensions.cursor] = None
        try:
            if not self.conn:
                self.connect()
            cursor = self.conn.cursor()
            yield cursor
        except Exception as e:
            self.logger.error("Cursor operation failed: %s", str(e))
            raise DatabaseError(
                f"Cursor operation failed: {str(e)}",
                status_code=500
            ) from e
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a database query with error handling"""
        try:
            with self.get_cursor() as cursor:
                self.logger.info("Executing query: %s", query)
                cursor.execute(query, params)
                self.conn.commit()
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [dict(zip(columns, row)) for row in rows]
                    return result
                return []
        except Exception as e:
            self.logger.error("Query execution failed: %s", str(e))
            raise DatabaseError(
                f"Query execution failed: {str(e)}",
                status_code=500,
                query=query,
                params=params
            ) from e

    def update_video_progress(self, video_id: str, progress: Dict[str, Any]) -> None:
        """Update video processing progress in database"""
        query = """
            UPDATE videos
            SET progress = jsonb_set(
                progress::jsonb,
                '{"status"}',
                '"{}"'::jsonb
            )
            WHERE id = %s
        """.format(progress['status'])

        try:
            self.logger.info("Updating progress for video: %s", video_id)
            self.execute_query(query, {'id': video_id})
            self.logger.info("Updated progress for video: %s", video_id)
        except Exception as e:
            self.logger.error("Failed to update video progress: %s", str(e))
            raise DatabaseError(
                f"Failed to update video progress: {str(e)}",
                status_code=500,
                video_id=video_id,
                progress=progress
            ) from e

    def update_video_progress(self, video_id: str, progress: Dict[str, Any]) -> None:
        """Update video processing progress in database"""
        query = """
            UPDATE videos
            SET progress = jsonb_set(
                progress::jsonb,
                '{"status"}',
                '"{}"'::jsonb
            )
            WHERE id = %s
        """.format(progress['status'])

        try:
            self.logger.info("Updating progress for video: %s", video_id)
            self.execute_query(query, {'id': video_id})
            self.logger.info("Updated progress for video: %s", video_id)
        except Exception as e:
            self.logger.error("Failed to update video progress: %s", str(e))
            raise DatabaseError(
                f"Failed to update video progress: {str(e)}",
                status_code=500,
                video_id=video_id,
                progress=progress
            ) from e

    def mark_video_downloaded(self, filename: str) -> None:
        """Mark video as downloaded"""
        query = """
            UPDATE videos
            SET download_status = 'completed',
                updated_at = CURRENT_TIMESTAMP
            WHERE filename = %s
        """
        self.execute_query(query, {'filename': filename})

    def update_video_stems(self, video_path: str, stem_paths: Dict[str, str]) -> None:
        """Update video stems in database"""
        query = """
            INSERT INTO stems (video_id, stem_type, file_path)
            VALUES (
                (SELECT id FROM videos WHERE filename = %s),
                %s,
                %s
            )
        """
        for stem_type, path in stem_paths.items():
            self.execute_query(query, {
                "video_path": video_path,
                "stem_type": stem_type,
                "file_path": str(path)
            })

    def update_video_lyrics(self, video_path: str, lyrics: List[Dict[str, Any]]) -> None:
        """Update video lyrics in database"""
        query = """
            INSERT INTO lyrics (video_id, line_number, lyrics, start_time, end_time)
            VALUES (
                (SELECT id FROM videos WHERE filename = %s),
                %s,
                %s,
                %s,
                %s
            )
        """
        for i, line in enumerate(lyrics):
            self.execute_query(query, {
                "video_path": video_path,
                "line_number": i,
                "lyrics": line['text'],
                "start_time": line['start'],
                "end_time": line['end']
            })

    def update_video_progress(self, video_id: str, progress: Dict[str, Any]) -> None:
        """Update video processing progress in database"""
        query = """
            UPDATE videos
            SET progress = jsonb_set(
                progress::jsonb,
                '{"status"}',
                '"{}"'::jsonb
            )
            WHERE id = %s
        """.format(progress['status'])

        try:
            self.execute_query(query, {'id': video_id})
            self.logger.info(f"Updated progress for video {video_id}")
        except Exception as e:
            self.logger.error(f"Failed to update video progress: {str(e)}")
            raise DatabaseError(f"Failed to update video progress: {str(e)}")
