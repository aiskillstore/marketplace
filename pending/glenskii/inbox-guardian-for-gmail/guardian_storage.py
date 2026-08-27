"""Private local storage helpers for Inbox Guardian mailbox artifacts."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from pathlib import Path


def restrict_file(path: str | Path) -> None:
    """Apply owner-only permissions where the operating system supports them."""
    try:
        os.chmod(path, 0o600)
    except OSError:
        # Windows retains ownership through the user account that created the file.
        pass


def write_private_bytes(path: str | Path, content: bytes) -> None:
    """Atomically write a mailbox artifact without leaving a public temporary file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_path = tempfile.mkstemp(prefix='.inbox-guardian-', dir=target.parent)
    try:
        try:
            os.fchmod(fd, 0o600)
        except OSError:
            pass
        with os.fdopen(fd, 'wb') as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, target)
        restrict_file(target)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(temporary_path)
        except OSError:
            pass
        raise


def write_private_json(path: str | Path, value) -> None:
    write_private_bytes(path, json.dumps(value, indent=2, ensure_ascii=False).encode('utf-8'))


def open_private_sqlite(path: str | Path) -> sqlite3.Connection:
    """Open local reputation data and apply private permissions after creation."""
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    restrict_file(database_path)
    return connection
