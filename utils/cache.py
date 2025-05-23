#!/usr/bin/env python3
"""
cache.py ────────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: Simple SQLite-based cache to store and retrieve processed stems
Inputs : url (str), stems (dict), db_path (str)
Outputs: cached JSON string in SQLite
ModLog : 2025-05-23 Initial version
"""

import sqlite3
import json
from contextlib import closing

DB_PATH = "cache.db"


def init_cache(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Initialize the cache database and create tables if missing.
    Returns a sqlite3.Connection object.
    """
    conn = sqlite3.connect(db_path)
    with closing(conn.cursor()) as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS stems (
                url TEXT PRIMARY KEY,
                stems_json TEXT NOT NULL
            )
            """
        )
        conn.commit()
    return conn


def get_cached_stems(url: str, conn: sqlite3.Connection) -> dict | None:
    """
    Retrieve cached stems for a given URL. Returns dict or None.
    """
    with closing(conn.cursor()) as cur:
        cur.execute("SELECT stems_json FROM stems WHERE url = ?", (url,))
        row = cur.fetchone()
    if row:
        return json.loads(row[0])
    return None


def cache_stems(url: str, stems: dict, conn: sqlite3.Connection) -> None:
    """
    Store stems dict in cache under the given URL.
    """
    with closing(conn.cursor()) as cur:
        cur.execute(
            "INSERT OR REPLACE INTO stems (url, stems_json) VALUES (?, ?)" ,
            (url, json.dumps(stems))
        )
        conn.commit()
