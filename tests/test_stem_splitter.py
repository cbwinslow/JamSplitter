"""
test_stem_splitter.py ────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: Unit & E2E tests for stem_splitter using monkeypatch
ModLog : 2025-05-23  Initial version
"""

import os
import json
from utils.stem_splitter import split_stems

class DummyStream:
    def __init__(self, dest, name):
        self.dest = dest
        self.name = name
    def download(self, output_path, filename):
        # Create a fake audio.mp4 file
        path = os.path.join(output_path, filename)
        with open(path, "wb") as f:
            f.write(b"FAKEAUDIO")
        return path

class DummyYT:
    def __init__(self, url):
        self.url = url
        self.streams = self
    def filter(self, only_audio):
        return [self]
    def order_by(self, key):
        return self
    def desc(self):
        return self
    def first(self):
        return DummyStream(None, None)

class DummySeparator:
    def __init__(self, model):
        pass
    def separate_to_file(self, audio_path, output_dir):
        # Simulate output directory structure
        stem_dir = os.path.join(output_dir, "audio")
        os.makedirs(stem_dir, exist_ok=True)
        for stem in ("vocals", "drums", "bass", "other"):
            with open(os.path.join(stem_dir, f"{stem}.wav"), "wb") as f:
                f.write(b"DUMMY")

def test_split_stems_creates_files(monkeypatch, tmp_output_dir):
    # Patch YouTube and Separator
    monkeypatch.setattr('utils.stem_splitter.YouTube', DummyYT)
    monkeypatch.setattr('utils.stem_splitter.Separator', DummySeparator)

    stems = split_stems("https://youtu.be/fake", tmp_output_dir)
    # Expect 4 stems
    assert set(stems.keys()) == {"vocals", "drums", "bass", "other"}
    # Files actually exist
    for path in stems.values():
        assert os.path.isfile(path)

def test_split_stems_uses_cache(monkeypatch, tmp_output_dir):
    # First run to populate cache
    monkeypatch.setattr('utils.stem_splitter.YouTube', DummyYT)
    monkeypatch.setattr('utils.stem_splitter.Separator', DummySeparator)
    first = split_stems("https://youtu.be/fake", tmp_output_dir)
    # Now monkeypatch to throw if YouTube called
    def fail(_):
        raise RuntimeError("Should not download again")
    monkeypatch.setattr('utils.stem_splitter.YouTube', fail)
    cached = split_stems("https://youtu.be/fake", tmp_output_dir)
    assert cached == first
