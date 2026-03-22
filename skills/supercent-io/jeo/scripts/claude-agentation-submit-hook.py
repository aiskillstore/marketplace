#!/usr/bin/env python3
"""JEO Claude UserPromptSubmit wrapper for agentation.

Only exposes pending annotations after an explicit submit-style prompt arrives
during the VERIFY_UI gate.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


READY_TOKENS = (
    "annotate",
    "annotate_ready",
    "agentui",
    "ui검토",
    "send annotations",
    "submitted annotations",
    "elementpath",
)


def git_root() -> Path:
    try:
        return Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        )
    except Exception:
        return Path.cwd()


def state_path(root: Path) -> Path:
    return root / ".omc" / "state" / "jeo-state.json"


def load_state(root: Path) -> dict[str, Any]:
    path = state_path(root)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(root: Path, state: dict[str, Any]) -> None:
    path = state_path(root)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def flatten_strings(node: Any) -> list[str]:
    parts: list[str] = []
    if isinstance(node, str):
        parts.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            parts.extend(flatten_strings(value))
    elif isinstance(node, list):
        for value in node:
            parts.extend(flatten_strings(value))
    return parts


def submitted_prompt(payload: str) -> bool:
    try:
        data = json.loads(payload)
    except Exception:
        return False

    combined = " ".join(flatten_strings(data)).lower()
    return any(token in combined for token in READY_TOKENS)


def fetch_pending() -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen("http://localhost:4747/pending", timeout=2) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return None


def update_submit_gate(root: Path, state: dict[str, Any], count: int) -> None:
    agentation = state.setdefault("agentation", {})
    agentation["submit_gate_status"] = "submitted"
    agentation["submit_signal"] = "claude-user-prompt-submit"
    agentation["submit_received_at"] = subprocess.check_output(
        ["python3", "-c", "import datetime;print(datetime.datetime.utcnow().isoformat()+\"Z\")"],
        text=True,
    ).strip()
    agentation["submitted_annotation_count"] = count
    save_state(root, state)


def main() -> int:
    payload = sys.stdin.read()
    root = git_root()
    state = load_state(root)

    if state.get("phase") != "verify_ui":
        return 0
    if not submitted_prompt(payload):
        return 0

    pending = fetch_pending()
    if not pending:
        return 0

    count = int(pending.get("count", 0) or 0)
    if count <= 0:
        return 0

    update_submit_gate(root, state, count)

    print(f"=== AGENTATION: {count} submitted UI annotations ===")
    for index, annotation in enumerate(pending.get("annotations", []), start=1):
        element = annotation.get("element", "?")
        path = annotation.get("elementPath", "?")
        comment = annotation.get("comment", "")
        print(f"[{index}] {element} ({path})")
        if comment:
            print(f"    {comment}")
    print("=== END ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
