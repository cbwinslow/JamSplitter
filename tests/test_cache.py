"""
test_cache.py ─────────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: Unit tests for caching module
ModLog : 2025-05-23  Initial version
"""

import sqlite3
from utils.cache import init_cache, get_cached_stems, cache_stems

def test_init_and_empty(tmp_path, monkeypatch):
    # Ensure the DB file is created and table exists
    db_file = tmp_path / "cache.db"
    monkeypatch.setattr('utils.cache.DB_PATH', str(db_file))
    conn = init_cache()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stems'")
    assert cur.fetchone()[0] == 'stems'
    conn.close()

def test_cache_and_retrieve(monkeypatch):
    conn = init_cache()
    url = "https://youtu.be/fake"
    data = {"vocals": "/path/vocals.wav"}
    # Cache it
    cache_stems(url, data, conn)
    # Retrieve it
    retrieved = get_cached_stems(url, conn)
    assert retrieved == data

def test_get_missing(monkeypatch):
    conn = init_cache()
    assert get_cached_stems("nope", conn) is None
