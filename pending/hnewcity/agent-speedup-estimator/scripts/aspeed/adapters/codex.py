from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..classify import classify
from ..models import Event, SessionTiming
from ..textio import open_text

MODEL_ITEMS = {"Reasoning", "AgentMessage", "ContextCompaction"}
SKIP_ITEMS = {"UserMessage"}


def default_roots() -> List[Path]:
    home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    return [home / "sessions", home / "archived_sessions"]


def find_sessions(roots: List[Path]) -> List[Path]:
    plain: Dict[str, Path] = {}
    packed: Dict[str, Path] = {}
    for r in roots:
        if not r.is_dir():
            continue
        for p in r.rglob("*.jsonl"):
            plain[p.name] = p
        for p in r.rglob("*.jsonl.zst"):
            packed[p.name[: -len(".zst")]] = p
    for name, p in packed.items():
        plain.setdefault(name, p)
    return sorted(plain.values())


def _duration_s(d) -> Optional[float]:
    if isinstance(d, dict):
        return float(d.get("secs", 0)) + float(d.get("nanos", 0)) / 1e9
    return None


def _tool_event(item: dict, t0: float, t1: float) -> Optional[Event]:
    kind = item.get("type")
    dur = _duration_s(item.get("duration"))
    if dur is not None:
        t0 = t1 - dur
    if kind == "CommandExecution":
        category, family = classify(item.get("command"))
        return Event(t0, t1, "tool", category, family)
    if kind == "McpToolCall":
        return Event(t0, t1, "tool", "other_tool", "")
    if kind == "WebSearch":
        return Event(t0, t1, "tool", "network", "")
    if kind in ("FileChange", "ImageView"):
        return Event(t0, t1, "tool", "file_search_read", "")
    if kind == "Extension":
        if str(item.get("kind", "")).startswith("clock"):
            return Event(t0, t1, "tool", "wait", "sleep")
        return Event(t0, t1, "tool", "other_tool", "")
    return None


def _union(intervals: List[Tuple[float, float]]) -> float:
    total = 0.0
    cur_s: Optional[float] = None
    cur_e: Optional[float] = None
    for s, e in sorted(intervals):
        if cur_e is None or s > cur_e:
            if cur_e is not None and cur_s is not None:
                total += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None and cur_s is not None:
        total += cur_e - cur_s
    return total


def _long_gaps(intervals: List[Tuple[float, float]], lo: float, hi: float, limit: float) -> float:
    total = 0.0
    cur = lo
    for s, e in sorted(intervals):
        if s - cur > limit:
            total += s - cur
        cur = max(cur, e)
    if hi - cur > limit:
        total += hi - cur
    return total


def parse_session(
    path: Path,
    since_ts: Optional[float] = None,
    max_stall_s: float = 300.0,
    max_human_s: float = 1800.0,
) -> Optional[SessionTiming]:
    stem = path.name[: -len(".zst")] if path.name.endswith(".zst") else path.name
    st = SessionTiming("codex", stem[: -len(".jsonl")])
    turns: Dict[str, dict] = {}

    def turn(tid: str) -> dict:
        return turns.setdefault(tid, {"events": [], "all": [], "dur": None, "lo": None, "hi": None})

    with open_text(path) as fh:
        for line in fh:
            if '"event_msg"' not in line[:80]:
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            p = o.get("payload") or {}
            ptype = p.get("type")
            tid = p.get("turn_id") or ""
            if ptype == "item_completed":
                a, b = p.get("started_at_ms"), p.get("completed_at_ms")
                if a is None or b is None:
                    continue
                item = p.get("item") or {}
                if item.get("type") in SKIP_ITEMS:
                    continue
                t0, t1 = a / 1000.0, b / 1000.0
                t = turn(tid)
                t["all"].append((t0, t1))
                if item.get("type") not in MODEL_ITEMS:
                    ev = _tool_event(item, t0, t1)
                    if ev:
                        t["events"].append(ev)
            elif ptype == "task_started":
                if p.get("started_at") is not None:
                    t = turn(tid)
                    s = float(p["started_at"])
                    t["lo"] = s if t["lo"] is None else min(t["lo"], s)
            elif ptype == "task_complete":
                t = turn(tid)
                if p.get("duration_ms") is not None:
                    t["dur"] = p["duration_ms"] / 1000.0
                if p.get("completed_at") is not None:
                    t["hi"] = float(p["completed_at"])
                if p.get("started_at") is not None:
                    s = float(p["started_at"])
                    t["lo"] = s if t["lo"] is None else min(t["lo"], s)

    ready = []
    for t in turns.values():
        if t["all"]:
            lo = min([x[0] for x in t["all"]] + ([t["lo"]] if t["lo"] is not None else []))
            hi = max([x[1] for x in t["all"]] + ([t["hi"]] if t["hi"] is not None else []))
        elif t["lo"] is not None and t["hi"] is not None:
            lo, hi = t["lo"], t["hi"]
        else:
            continue
        ready.append((lo, hi, t))
    ready.sort(key=lambda x: x[0])

    prev_end: Optional[float] = None
    for lo, hi, t in ready:
        if since_ts is not None and hi < since_ts:
            prev_end = hi
            continue
        active = t["dur"] if t["dur"] is not None else max(0.0, hi - lo)
        tool_u = _union([(e.start, e.end) for e in t["events"]])
        stalled = _long_gaps(t["all"], lo, hi, max_stall_s)
        st.stalled_s += stalled
        st.model_s += max(0.0, active - tool_u - stalled)
        st.events.extend(t["events"])
        if prev_end is not None and lo > prev_end:
            gap = lo - prev_end
            if gap > max_human_s:
                st.idle_s += gap
            else:
                st.human_s += gap
        prev_end = max(prev_end or hi, hi)
        st.touch(lo)
        st.touch(hi)
    if st.first_ts is None:
        return None
    return st
