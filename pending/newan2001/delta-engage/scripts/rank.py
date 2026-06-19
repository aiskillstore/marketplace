#!/usr/bin/env python3
"""rank.py — combine the model's fit_score with a deterministic engagement-potential score.

Division of labor (the whole design philosophy): the *model* judges fit-to-positioning and writes
`fit_score` (0-10) onto each signal — that's judgment. This *script* computes engagement potential
(0-1) from recency, discussion velocity, headroom, and platform-normalized reach — that's
arithmetic the model shouldn't be eyeballing. final_score = fit_score * engagement_potential.

If a signal has no fit_score yet, it's treated as fit_score=0 and a warning is printed — rank.py
won't invent fit. Score fit first (references/ranking.md), then run this.

Usage:
    python3 rank.py signals.json -o ranked.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from lib.opportunity_signal import age_hours, reach_score  # noqa: E402


def recency_factor(hours: float) -> float:
    """Steep-ish decay. ~1.0 fresh, ~0.5 at ~36h, small by a week. Commenting on stale threads is
    mostly wasted, so we punish age hard."""
    half_life_h = 36.0
    return 0.5 ** (hours / half_life_h)


def velocity_factor(num_comments: int, hours: float) -> float:
    """Comments per hour, compressed. An active thread means your comment is actually seen."""
    cph = num_comments / max(hours, 1.0)
    return math.log1p(cph) / math.log1p(5.0)  # ~1.0 around 5 comments/hr


def headroom_factor(num_comments: int) -> float:
    """Sweet spot is a rising thread with a handful of comments. Penalize pile-ons (your comment
    drowns) and very dead threads (no audience). Peaks around ~10-30 comments."""
    n = max(0, num_comments)
    if n <= 1:
        return 0.55  # almost no discussion — limited audience but you're early
    if n <= 30:
        return 1.0
    # decays as it gets saturated
    return max(0.3, 1.0 - (math.log10(n) - math.log10(30)))


def engagement_potential(signal: dict, now: datetime) -> tuple[float, str]:
    hrs = age_hours(signal, now)
    rec = recency_factor(hrs)
    vel = velocity_factor(signal.get("num_comments", 0), hrs)
    head = headroom_factor(signal.get("num_comments", 0))
    reach = min(reach_score(signal), 1.2)
    # weighted blend; recency dominates because a stale post can't be fixed by reach
    raw = 0.40 * rec + 0.20 * vel + 0.20 * head + 0.20 * reach
    score = max(0.0, min(1.0, raw))
    reason = (f"age={hrs:.0f}h rec={rec:.2f} vel={vel:.2f} head={head:.2f} "
              f"reach={reach:.2f} → ep={score:.2f}")
    return score, reason


def main():
    ap = argparse.ArgumentParser(description="rank signals by fit_score * engagement_potential")
    ap.add_argument("input", help="signals.json (with fit_score written per signal)")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    with open(args.input) as f:
        signals = json.load(f)

    now = datetime.now(timezone.utc)
    missing_fit = 0
    for s in signals:
        if "fit_score" not in s:
            missing_fit += 1
            s["fit_score"] = 0
        ep, reason = engagement_potential(s, now)
        s["engagement_potential"] = round(ep, 4)
        s["final_score"] = round(float(s["fit_score"]) * ep, 4)
        s["rank_reason"] = reason

    if missing_fit:
        print(f"[rank] warn: {missing_fit} signals had no fit_score (treated as 0). Score fit per "
              "references/ranking.md before ranking.", file=sys.stderr)

    signals.sort(key=lambda x: x["final_score"], reverse=True)
    with open(args.output, "w") as f:
        json.dump(signals, f, indent=2)
    print(f"[rank] ranked {len(signals)} signals → {args.output}")


if __name__ == "__main__":
    main()
