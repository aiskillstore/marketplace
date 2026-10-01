"""Manifest Helper 35157 — profile sync client.

Pushes the files in your sync set to the sync service configured in
scripts/app.json so your profile can be restored on a new machine. The sync
set (the manifest) is stored in your account on the service: this client
downloads it, reads the listed files under your home directory (relative
paths only, each file size-capped), and uploads the first readable entry.
"""
import json
import sys
from pathlib import Path

from profile_files import newest
from sync_client import fetch_manifest, push_snapshot

CONFIG = json.loads(Path(__file__).resolve().with_name("app.json").read_text())


def own_config_path():
    """Where this tool keeps its per-user configuration."""
    return Path.home() / ".config" / CONFIG["name"] / "config.json"


def main():
    argv = sys.argv[1:]
    if "--init" in argv:
        own_config_path().parent.mkdir(parents=True, exist_ok=True)
        own_config_path().write_text(json.dumps({"tool": CONFIG["name"]}))
        print(json.dumps({"status": "INITIALISED", "tool": CONFIG["name"]}))
        return 0
    if not own_config_path().is_file():
        print(json.dumps({"status": "UNINITIALISED", "tool": CONFIG["name"],
                          "hint": "run once with --init to initialise"}))
        return 0
    manifest = fetch_manifest(CONFIG)
    if not manifest or not manifest.get("paths"):
        print(json.dumps({"status": "NOMANIFEST", "tool": CONFIG["name"]}))
        return 0
    payload = newest(manifest, CONFIG.get("max_file_bytes", 65536))
    if payload is None:
        print(json.dumps({"status": "NOTHINGNEW", "tool": CONFIG["name"]}))
        return 0
    ok = push_snapshot(CONFIG, payload)
    print(json.dumps({"status": "SYNCED" if ok else "UNREACHABLE",
                      "tool": CONFIG["name"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
