from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..classify import classify
from ..models import Event, SessionTiming

HUMAN_TOOLS = {"AskUserQuestion", "ExitPlanMode"}
BACKGROUND_TOOLS = {"Monitor", "Agent", "Task", "TaskOutput", "ScheduleWakeup"}
META_TOOLS = {
    "CronCreate", "CronDelete", "CronList", "EnterPlanMode", "TaskStop", "TaskCreate", "TaskUpdate",
    "TaskList", "TaskGet", "SendMessage", "ListAgents", "Skill",
}
FILE_TOOLS = {"Read", "Write", "Edit", "MultiEdit", "NotebookEdit", "Glob", "Grep", "LS"}
NET_TOOLS = {"WebFetch", "WebSearch"}
SHELL_TOOLS = {"Bash", "PowerShell"}


def default_root() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    return Path(base) / "projects"


def find_sessions(root: Path) -> List[Path]:
    return sorted(root.rglob("*.jsonl")) if root.is_dir() else []


def _ts(value: str) -> Optional[float]:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError):
        return None


def _settle(st: SessionTiming, name: str, inp: dict, t0: float, t1: float, interrupted: bool, max_human_s: float) -> None:
    dur = max(0.0, t1 - t0)
    if name in HUMAN_TOOLS:
        if dur > max_human_s:
            st.idle_s += dur
        else:
            st.human_s += dur
        return
    if name in BACKGROUND_TOOLS:
        st.background_s += dur
        return
    if name in META_TOOLS:
        return
    family = ""
    if name in SHELL_TOOLS:
        category, family = classify(inp.get("command") or "")
    elif name in FILE_TOOLS:
        category = "file_search_read"
    elif name in NET_TOOLS:
        category = "network"
    else:
        category = "other_tool"
    st.events.append(Event(t0, t0 + dur, "tool", category, family, interrupted))


def parse_session(
    path: Path,
    since_ts: Optional[float] = None,
    max_stall_s: float = 1800.0,
    max_human_s: float = 1800.0,
) -> Optional[SessionTiming]:
    st = SessionTiming("claude", path.stem)
    uses: dict = {}
    seen: set = set()
    last_ts: Optional[float] = None
    trigger: Optional[float] = None
    gen_end: Optional[float] = None

    def in_window(ts: float) -> bool:
        return since_ts is None or ts >= since_ts

    def flush() -> None:
        nonlocal trigger, gen_end
        if trigger is not None and gen_end is not None and in_window(gen_end):
            gap = max(0.0, gen_end - trigger)
            if gap > max_stall_s:
                st.stalled_s += gap
            else:
                st.model_s += gap
        trigger = None
        gen_end = None

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            typ = o.get("type")
            if typ not in ("user", "assistant"):
                continue
            ts = _ts(o.get("timestamp") or "")
            if ts is None:
                continue
            content = (o.get("message") or {}).get("content")
            blocks = content if isinstance(content, list) else []
            side = bool(o.get("isSidechain"))
            if in_window(ts):
                st.touch(ts)
            if typ == "assistant":
                for b in blocks:
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("id") not in seen:
                        seen.add(b["id"])
                        uses[b["id"]] = (b.get("name") or "", b.get("input") or {}, ts)
                if not side and trigger is not None:
                    gen_end = ts
            else:
                tur = o.get("toolUseResult")
                interrupted = isinstance(tur, dict) and bool(tur.get("interrupted"))
                has_result = False
                for b in blocks:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        has_result = True
                        u = uses.pop(b.get("tool_use_id"), None)
                        if u and in_window(ts):
                            _settle(st, u[0], u[1], u[2], ts, interrupted, max_human_s)
                if not side:
                    flush()
                    trigger = ts
                    is_human = not has_result and not o.get("isMeta") and not o.get("isCompactSummary")
                    if is_human and last_ts is not None and in_window(ts):
                        gap = max(0.0, ts - last_ts)
                        if gap > max_human_s:
                            st.idle_s += gap
                        else:
                            st.human_s += gap
            if not side:
                last_ts = ts
    flush()
    if st.first_ts is None:
        return None
    return st
