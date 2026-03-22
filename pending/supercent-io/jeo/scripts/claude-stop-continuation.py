#!/usr/bin/env python3
"""JEO Claude Stop hook — auto-continues JEO workflow after plannotator review.

Fires on every Claude Code Stop event. Checks jeo-state.json for a pending
plannotator result (approved or feedback_required) that hasn't been delivered
to Claude yet, and blocks the stop to inject the continuation instruction.

This fixes the "plannotator closes but JEO doesn't continue" problem.

How it works:
- ExitPlanMode fires → claude-plan-gate.py runs plannotator → stores result in jeo-state.json
- claude-plan-gate.py emits {"decision":"allow"} — Claude exits plan mode
- Claude generates a short "plan mode exited" response and is about to stop
- THIS hook fires: sees plan_gate_status=approved, blocks stop with EXECUTE instruction
- Claude reads the injected instruction and proceeds to STEP 2 (EXECUTE) immediately

Guard: _stop_continuation_triggered_hash == last_reviewed_plan_hash prevents
re-firing on subsequent stop events (once per plan review cycle).
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


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


def load_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        pass


def load_feedback(root: Path) -> str:
    feedback_path = root / ".omc" / "state" / "jeo-plannotator-feedback.json"
    if not feedback_path.exists():
        return ""
    try:
        fb = json.loads(feedback_path.read_text(encoding="utf-8"))
        return fb.get("feedback", fb.get("message", ""))
    except Exception:
        return ""


def main() -> int:
    # Read stdin — Claude Code passes stop context including stop_hook_active flag
    try:
        stdin_raw = sys.stdin.read()
        stdin_data = json.loads(stdin_raw) if stdin_raw.strip() else {}
    except Exception:
        stdin_data = {}

    # Safety: prevent infinite stop-hook loops (Claude Code sets this when a
    # stop hook has already blocked once in this response cycle)
    if stdin_data.get("stop_hook_active"):
        return 0

    root = git_root()
    state_path = root / ".omc" / "state" / "jeo-state.json"
    state = load_state(state_path)

    if not state:
        return 0

    plan_gate_status = state.get("plan_gate_status")
    phase = state.get("phase")
    plan_hash = state.get("last_reviewed_plan_hash") or ""
    triggered_hash = state.get("_stop_continuation_triggered_hash") or ""

    # Guard: only fire once per plan review cycle (hash-based dedup)
    if plan_hash and triggered_hash == plan_hash:
        return 0

    now = datetime.datetime.utcnow().isoformat() + "Z"

    if plan_gate_status == "approved" and phase == "execute":
        # Mark as triggered so subsequent Stop events don't re-fire
        state["_stop_continuation_triggered_hash"] = plan_hash
        state["updated_at"] = now
        save_state(state_path, state)

        msg = (
            "[JEO CONTINUATION] Plan approved by plannotator. "
            "jeo-state.json: plan_gate_status=approved, phase=execute, next_mode=ralphmode. "
            "PROCEED IMMEDIATELY to STEP 2 (EXECUTE) without waiting for user input. "
            "Check team availability (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS), "
            "then invoke /omc:team or ralphmode to begin implementation. "
            "Do NOT re-enter plan mode. Do NOT ask the user for confirmation."
        )
        print(json.dumps({"decision": "block", "reason": msg}))
        return 0

    if plan_gate_status == "feedback_required":
        # Mark as triggered
        state["_stop_continuation_triggered_hash"] = plan_hash
        state["updated_at"] = now
        save_state(state_path, state)

        feedback = load_feedback(root)
        feedback_part = f" Feedback from reviewer: {feedback}." if feedback else ""

        msg = (
            "[JEO CONTINUATION] plannotator requested plan changes. "
            f"jeo-state.json: plan_gate_status=feedback_required.{feedback_part} "
            "ACTION REQUIRED: Read .omc/state/jeo-plannotator-feedback.json for detailed feedback. "
            "Revise plan.md to address the feedback, then re-enter plan mode "
            "(EnterPlanMode → update plan → ExitPlanMode) to resubmit for review. "
            "Do NOT proceed to EXECUTE until plan is approved."
        )
        print(json.dumps({"decision": "block", "reason": msg}))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
