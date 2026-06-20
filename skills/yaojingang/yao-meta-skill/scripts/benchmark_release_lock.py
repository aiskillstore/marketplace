#!/usr/bin/env python3
"""Git source/generated dirty classification for benchmark release locks."""

import subprocess
from pathlib import Path
from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by render_benchmark_reproducibility.py to keep release-lock git status classification out of the report renderer."


GENERATED_DIRTY_PREFIXES = (
    "dist/",
    "registry/index.json",
    "registry/packages/",
    "reports/",
    "skill_atlas/",
    "skill-ir/examples/",
)


def status_path(line: str) -> str:
    path = line[3:].strip() if len(line) > 3 else line.strip()
    if " -> " in path:
        path = path.rsplit(" -> ", 1)[-1].strip()
    return path


def is_generated_dirty_path(path: str) -> bool:
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in GENERATED_DIRTY_PREFIXES)


def git_status(skill_dir: Path) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", "status", "--short", "--untracked-files=all"],
            cwd=skill_dir,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return {
            "available": False,
            "dirty": None,
            "changed_file_count": None,
            "source_dirty": None,
            "source_changed_file_count": None,
            "generated_dirty": None,
            "generated_changed_file_count": None,
        }
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    paths = [status_path(line) for line in lines]
    generated_lines = [line for line, path in zip(lines, paths) if is_generated_dirty_path(path)]
    source_lines = [line for line, path in zip(lines, paths) if not is_generated_dirty_path(path)]
    return {
        "available": True,
        "dirty": bool(lines),
        "changed_file_count": len(lines),
        "generated_dirty": bool(generated_lines),
        "generated_changed_file_count": len(generated_lines),
        "source_dirty": bool(source_lines),
        "source_changed_file_count": len(source_lines),
        "sample": lines[:12],
        "source_sample": source_lines[:12],
        "generated_sample": generated_lines[:12],
        "generated_dirty_prefixes": list(GENERATED_DIRTY_PREFIXES),
        "scope": "generation-time status before this report is written",
    }


def release_lock_status(status: dict[str, Any], commit: str) -> dict[str, Any]:
    available = status.get("available") is True
    source_clean = status.get("source_dirty") is False
    known_commit = bool(commit and commit != "unknown")
    ready = available and source_clean and known_commit
    reasons = []
    if not available:
        reasons.append("git status unavailable")
    if not known_commit:
        reasons.append("git commit unavailable")
    if status.get("source_dirty") is True:
        reasons.append("source files were dirty at generation time")
    if status.get("source_dirty") is None:
        reasons.append("working tree cleanliness unknown")
    if status.get("generated_dirty") is True and status.get("source_dirty") is False:
        reasons.append("only generated evidence artifacts were dirty at generation time")
    if not reasons:
        reasons.append("clean source tree at generation-time HEAD")
    return {
        "ready": ready,
        "commit": commit,
        "status_scope": status.get("scope", "generation-time status"),
        "source_changed_file_count": status.get("source_changed_file_count"),
        "generated_changed_file_count": status.get("generated_changed_file_count"),
        "reason": "; ".join(reasons),
    }
