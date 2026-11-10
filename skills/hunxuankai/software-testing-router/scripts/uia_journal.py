"""Durable UIA progress recovery. A journal is evidence, never a replay command."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def create_journal(path: Path, run_id: str, target_pid: int, executable: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {"schema_version": 1, "run_id": run_id, "event": "run_started",
             "time": datetime.now(timezone.utc).isoformat(), "target_pid": target_pid,
             "executable": executable}
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def recover_progress(path: Path, run_id: str) -> dict:
    records: list[dict] = []
    pending = None
    side_effects = False
    incomplete = False
    try:
        lines = path.read_bytes().splitlines()
    except OSError:
        return {"steps": [], "incomplete_step": None, "may_have_side_effects": False,
                "journal_incomplete": True}
    for line in lines:
        try:
            event = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            # Keep a valid prefix, but never trust events after a torn/corrupt line.
            incomplete = True
            break
        if not isinstance(event, dict):
            incomplete = True
            break
        if event.get("run_id") != run_id:
            continue
        kind = event.get("event")
        if kind == "step_started":
            if pending is not None or event.get("index") != len(records) or event.get("action") not in {"set", "invoke", "wait"}:
                incomplete = True
                break
            pending = {"index": event["index"], "action": event["action"], "phase": "locating"}
        elif kind in {"action_started", "step_completed"}:
            if pending is None or event.get("index") != pending["index"]:
                incomplete = True
                break
            if kind == "action_started":
                if pending["action"] not in {"set", "invoke"}:
                    incomplete = True
                    break
                pending["phase"] = "acting"
                side_effects = True
            else:
                record = event.get("record")
                if not isinstance(record, dict) or record.get("action") != pending["action"]:
                    incomplete = True
                    break
                records.append(record)
                pending = None
    if pending:
        pending["outcome"] = "unknown" if pending["phase"] == "acting" else (
            "not_observed" if pending["action"] == "wait" else "not_started")
    return {"steps": records, "incomplete_step": pending, "may_have_side_effects": side_effects,
            "journal_incomplete": incomplete}


def merge_worker_result(worker: dict, progress: dict) -> dict:
    result = {**worker, **progress}
    if worker.get("ok") and (progress["journal_incomplete"] or progress["incomplete_step"]
                             or worker.get("steps", []) != progress["steps"]):
        result.update(ok=False, status="journal_error", error="Worker result and durable progress disagree")
    return result
