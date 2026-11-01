from __future__ import annotations

from typing import List, Tuple

from .models import Event


def attribute(events: List[Event], cap_s: float) -> List[Tuple[Event, float, float]]:
    """Split overlapping wall time evenly among concurrent events.

    Returns (event, base_s, excess_s). The sum of base+excess over all events equals the
    wall-clock union of the intervals. Time beyond cap_s inside one event is reported as
    excess so long-running commands (servers, watchers) can be treated separately.
    """
    pts = []
    for i, e in enumerate(events):
        if e.end > e.start:
            pts.append((e.start, 1, i))
            pts.append((e.end, 0, i))
    pts.sort()
    share = [0.0] * len(events)
    active: set = set()
    prev = None
    for t, is_start, i in pts:
        if prev is not None and active and t > prev:
            part = (t - prev) / len(active)
            for a in active:
                share[a] += part
        if is_start:
            active.add(i)
        else:
            active.discard(i)
        prev = t
    out: List[Tuple[Event, float, float]] = []
    for i, e in enumerate(events):
        w = e.wall
        if w <= 0 or share[i] <= 0:
            continue
        if w > cap_s:
            base = share[i] * cap_s / w
            out.append((e, base, share[i] - base))
        else:
            out.append((e, share[i], 0.0))
    return out
