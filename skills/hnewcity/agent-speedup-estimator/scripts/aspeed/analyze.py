from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from .attribute import attribute
from .models import SessionTiming


@dataclass
class CatStats:
    n: int = 0
    base: float = 0.0
    excess: float = 0.0
    walls: List[float] = field(default_factory=list)

    @property
    def total(self) -> float:
        return self.base + self.excess


@dataclass
class AgentAgg:
    agent: str
    sessions: int = 0
    first_ts: Optional[float] = None
    last_ts: Optional[float] = None
    model_s: float = 0.0
    human_s: float = 0.0
    idle_s: float = 0.0
    background_s: float = 0.0
    stalled_s: float = 0.0
    cats: Dict[str, CatStats] = field(default_factory=dict)
    families: Counter = field(default_factory=Counter)

    @property
    def tool_s(self) -> float:
        return sum(c.total for c in self.cats.values())


def percentile(sorted_vals: List[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return sorted_vals[idx]


def aggregate(agent: str, sessions: Iterable[SessionTiming], cap_s: float) -> AgentAgg:
    agg = AgentAgg(agent)
    for s in sessions:
        agg.sessions += 1
        agg.model_s += s.model_s
        agg.human_s += s.human_s
        agg.idle_s += s.idle_s
        agg.background_s += s.background_s
        agg.stalled_s += s.stalled_s
        if s.first_ts is not None:
            agg.first_ts = s.first_ts if agg.first_ts is None else min(agg.first_ts, s.first_ts)
        if s.last_ts is not None:
            agg.last_ts = s.last_ts if agg.last_ts is None else max(agg.last_ts, s.last_ts)
        for ev, base, excess in attribute(s.events, cap_s):
            c = agg.cats.setdefault(ev.category, CatStats())
            c.n += 1
            c.base += base
            c.excess += excess
            c.walls.append(ev.wall)
            if ev.family:
                agg.families[ev.family] += base + excess
    return agg


def merge(aggs: List[AgentAgg]) -> AgentAgg:
    out = AgentAgg("all")
    for a in aggs:
        out.sessions += a.sessions
        out.model_s += a.model_s
        out.human_s += a.human_s
        out.idle_s += a.idle_s
        out.background_s += a.background_s
        out.stalled_s += a.stalled_s
        for ts in (a.first_ts,):
            if ts is not None:
                out.first_ts = ts if out.first_ts is None else min(out.first_ts, ts)
        for ts in (a.last_ts,):
            if ts is not None:
                out.last_ts = ts if out.last_ts is None else max(out.last_ts, ts)
        for k, c in a.cats.items():
            m = out.cats.setdefault(k, CatStats())
            m.n += c.n
            m.base += c.base
            m.excess += c.excess
            m.walls.extend(c.walls)
        out.families.update(a.families)
    return out


def category_table(agg: AgentAgg) -> List[dict]:
    rows = []
    for k, c in agg.cats.items():
        w = sorted(c.walls)
        rows.append(
            {
                "category": k,
                "count": c.n,
                "seconds": round(c.total, 1),
                "excess_seconds": round(c.excess, 1),
                "median_s": round(percentile(w, 0.5), 2),
                "p90_s": round(percentile(w, 0.9), 2),
                "max_s": round(w[-1], 1) if w else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["seconds"])
    return rows
