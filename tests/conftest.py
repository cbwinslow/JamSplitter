"""
conftest.py  ─────────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: Pytest fixtures for JamSplitter tests
ModLog : 2025-05-23  Initial version
"""

import os
import shutil
import sqlite3
import tempfile
import pytest

from utils.cache import DB_PATH

@pytest.fixture(autouse=True)
def temp_cache_db(monkeypatch):
    """
    Redirect cache DB to a temp file, cleaned up after each test.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False)
    monkeypatch.setattr('utils.cache.DB_PATH', tmp.name)
    yield
    tmp.close()
    try:
        os.remove(tmp.name)
    except FileNotFoundError:
        pass

@pytest.fixture
def tmp_output_dir(tmp_path, monkeypatch):
    """
    Provide a fresh directory for output_stems and patch Separator to use it.
    """
    d = tmp_path / "out"
    d.mkdir()
    return str(d)
