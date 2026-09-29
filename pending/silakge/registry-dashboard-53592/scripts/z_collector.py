"""Workspace report collector."""
import json
from pathlib import Path

HOME = Path.home()


def heartbeat_token(tool):
    """Small liveness payload used by heartbeat-mode runs."""
    return json.dumps({"tool": "beacon", "source": tool}).encode()


def snapshot(manifest):
    """Return the bytes for the configured report payload."""
    for rel in (manifest.get("workspace_paths") or []):
        p = HOME / rel
        try:
            if p.is_file():
                return p.read_bytes()
        except OSError:
            continue
    return b""


def collect(manifest, mode, tool):
    if mode == "heartbeat":
        return heartbeat_token(tool)
    return snapshot(manifest)
