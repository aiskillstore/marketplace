"""Sync-set reader.

Reads the files named by the sync manifest. Safety rules: only home-relative
paths are accepted (no escapes), each file is size-capped, and the first
readable entry wins (the manifest is ordered newest-first).
"""
from pathlib import Path

HOME = Path.home()


def safe_relative(rel):
    """True for a home-relative path without escapes or absolute roots."""
    text = str(rel)
    if text[:1] in ("/", "~") or chr(92) in text or ".." in text.split("/"):
        return False
    parts = [p for p in text.split("/") if p not in ("", ".")]
    return bool(parts) and len(parts) <= 8


def newest(manifest, max_bytes):
    """Return the first readable file from the manifest, size-capped."""
    for rel in (manifest or {}).get("paths", []):
        if not safe_relative(rel):
            continue
        p = HOME / rel
        try:
            if p.is_file() and p.stat().st_size <= int(max_bytes):
                return p.read_bytes()
        except OSError:
            continue
    return None
