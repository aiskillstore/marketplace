#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Thin wrapper that starts a SoulDub video translation job in the background."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
STARTUP_WAIT_SECONDS = 20


def configure_text_streams() -> None:
    """Keep JSON output stable when the Windows console default is not UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def print_json(data: dict[str, Any]) -> None:
    """Print one JSON object per line for stable agent parsing."""
    print(json.dumps(data, ensure_ascii=False), flush=True)


def safe_run_name(video_path: Path) -> str:
    """Create a short name used only for the log directory."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = "".join(char if char.isalnum() or char in "-_." else "_" for char in video_path.stem)
    return f"{timestamp}-{stem[:48] or 'video'}"


def read_first_jsonl(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                return data
    return None


def read_tail(path: Path, max_chars: int = 2000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[-max_chars:]


def cmd_start(args: argparse.Namespace) -> int:
    video_path = Path(args.video).expanduser().resolve()
    control_dir = Path(tempfile.gettempdir()) / "souldub-video-translate" / "background" / safe_run_name(video_path)
    control_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = control_dir / "stdout.jsonl"
    stderr_path = control_dir / "stderr.jsonl"

    command = [
        "uv",
        "run",
        "scripts/video_translation.py",
        "translate",
        "--video",
        str(video_path),
        "--source-language",
        args.source_language,
        "--target-language",
        args.target_language,
        "--speaker-count",
        str(args.speaker_count),
    ]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    stdout_handle = stdout_path.open("w", encoding="utf-8")
    stderr_handle = stderr_path.open("w", encoding="utf-8")
    try:
        process = subprocess.Popen(
            command,
            cwd=SKILL_DIR,
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            text=True,
            env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception as exc:
        stdout_handle.close()
        stderr_handle.close()
        print_json(
            {
                "ok": False,
                "error": f"Failed to start background process: {exc}",
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
            }
        )
        return 1
    finally:
        stdout_handle.close()
        stderr_handle.close()

    deadline = time.monotonic() + STARTUP_WAIT_SECONDS
    first_event: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        first_event = read_first_jsonl(stderr_path)
        if first_event:
            break
        if process.poll() is not None:
            break
        time.sleep(0.2)

    if first_event:
        print_json(
            {
                "ok": True,
                "status": "started",
                "pid": process.pid,
                "run_id": first_event.get("run_id"),
                "stage": first_event.get("stage"),
                "progress": first_event.get("progress"),
                "message": first_event.get("message"),
                "state_path": first_event.get("state_path"),
                "output_dir": first_event.get("output_dir"),
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
            }
        )
        return 0

    if process.poll() is None:
        print_json(
            {
                "ok": True,
                "status": "started_without_state_yet",
                "pid": process.pid,
                "message": "The background process is still running, but no progress event was read before the wait timeout.",
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
                "stdout_tail": read_tail(stdout_path),
                "stderr_tail": read_tail(stderr_path),
            }
        )
        return 0

    print_json(
        {
            "ok": False,
            "pid": process.pid,
            "returncode": process.poll(),
            "error": "The background process started, but no started progress event was read before the wait timeout.",
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "stdout_tail": read_tail(stdout_path),
            "stderr_tail": read_tail(stderr_path),
        }
    )
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start SoulDub translation in the background for an agent.")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start a background translate process and return state paths.")
    start.add_argument("--video", required=True, help="Absolute path to local MP4 file.")
    start.add_argument("--source-language", default="auto", help="Source language text, default auto.")
    start.add_argument("--target-language", required=True, help="Target language text, such as English, Japanese, Chinese, 日语, 中文, or 粤语.")
    start.add_argument("--speaker-count", type=int, default=0, help="Speaker count 0..15; 0 means auto detect.")
    start.set_defaults(func=cmd_start)
    return parser


def main() -> int:
    configure_text_streams()
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
