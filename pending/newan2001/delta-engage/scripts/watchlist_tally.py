#!/usr/bin/env python3
"""watchlist_tally.py — recurrence tally → promotion candidates + decay, with run-history append.

The watchlist is emergent: authors who keep landing in the *worthy* set get nominated for
promotion. The cardinal rule encoded here is **quality-weighted recurrence, not raw volume** — a
prolific poster who's rarely worthy must not get promoted. "Worthy" = made this run's selected set.

This script only *nominates* and *flags*. It never writes promotions into the config — the model
presents candidates and the user confirms (references/watchlist.md). What it does write (with
--apply-history) is the run-history append, so recurrence can be computed next time.

Usage:
    # tally only (prints candidates as JSON; does not modify config)
    python3 watchlist_tally.py --config config.json --run top.json

    # also append this run to config.run_history (safe; this is just bookkeeping)
    python3 watchlist_tally.py --config config.json --run top.json --apply-history
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone


def _today():
    return datetime.now(timezone.utc).date().isoformat()


def _worthy_authors(run_signals):
    """Authors in this run's selected set, with how many worthy posts each had this run."""
    counts = {}
    for s in run_signals:
        h = (s.get("author_handle") or "").lower()
        if not h:
            continue
        key = (h, s["platform"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def tally(config, run_signals, window_runs=4, promote_n=2, decay_runs=6):
    history = config.get("run_history", [])
    recent = history[-window_runs:]

    # recurrence across recent runs + this run
    recurrence = {}
    for run in recent:
        for entry in run.get("worthy_authors", []):
            key = (entry["handle"].lower(), entry["platform"])
            recurrence.setdefault(key, {"worthy": 0, "runs": 0})
            recurrence[key]["worthy"] += entry.get("worthy_count", 1)
            recurrence[key]["runs"] += 1
    for (h, plat), c in _worthy_authors(run_signals).items():
        recurrence.setdefault((h, plat), {"worthy": 0, "runs": 0})
        recurrence[(h, plat)]["worthy"] += c
        recurrence[(h, plat)]["runs"] += 1

    already = {(w["handle"].lower(), w["platform"]) for w in config.get("watchlist", [])}

    candidates = []
    for (h, plat), stat in recurrence.items():
        if (h, plat) in already:
            continue
        # promote on N worthy posts in the window OR a high worthy-to-runs ratio
        ratio = stat["worthy"] / max(stat["runs"], 1)
        if stat["worthy"] >= promote_n or (stat["runs"] >= 2 and ratio >= 1.5):
            candidates.append({
                "handle": h, "platform": plat,
                "worthy_count": stat["worthy"], "appeared_in_runs": stat["runs"],
                "reason": f"{stat['worthy']} worthy posts across {stat['runs']} recent runs",
            })
    candidates.sort(key=lambda c: c["worthy_count"], reverse=True)

    # decay: existing watchlist entries gone quiet beyond the decay window
    decayed = []
    today = date.fromisoformat(_today())
    for w in config.get("watchlist", []):
        last = w.get("last_worthy_run", "")
        try:
            gap_days = (today - date.fromisoformat(last)).days if last else 9999
        except ValueError:
            gap_days = 9999
        # ~ decay_runs * (3.5 days between Mon/Thu runs) as a rough day window
        if gap_days > decay_runs * 4:
            decayed.append({"handle": w["handle"], "platform": w["platform"],
                            "last_worthy_run": last or "never", "quiet_days": gap_days})

    return candidates, decayed


def append_history(config, run_signals):
    entry = {
        "date": _today(),
        "platforms": sorted({s["platform"] for s in run_signals}),
        "worthy_authors": [
            {"handle": h, "platform": plat, "worthy_count": c}
            for (h, plat), c in _worthy_authors(run_signals).items()
        ],
    }
    config.setdefault("run_history", []).append(entry)
    # also stamp last_worthy_run on any existing watchlist members who were worthy this run
    worthy = _worthy_authors(run_signals)
    for w in config.get("watchlist", []):
        if (w["handle"].lower(), w["platform"]) in worthy:
            w["last_worthy_run"] = _today()
            w["worthy_count"] = w.get("worthy_count", 0) + worthy[(w["handle"].lower(), w["platform"])]
    return config


def main():
    ap = argparse.ArgumentParser(description="watchlist recurrence tally + decay")
    ap.add_argument("--config", required=True)
    ap.add_argument("--run", required=True, help="this run's selected set (top.json)")
    ap.add_argument("--apply-history", action="store_true",
                    help="append this run to config.run_history and stamp last_worthy_run")
    ap.add_argument("--window-runs", type=int, default=4)
    ap.add_argument("--promote-n", type=int, default=2)
    ap.add_argument("--decay-runs", type=int, default=6)
    args = ap.parse_args()

    with open(args.config) as f:
        config = json.load(f)
    with open(args.run) as f:
        run_signals = json.load(f)

    candidates, decayed = tally(config, run_signals,
                                args.window_runs, args.promote_n, args.decay_runs)

    if args.apply_history:
        config = append_history(config, run_signals)
        with open(args.config, "w") as f:
            json.dump(config, f, indent=2)

    print(json.dumps({
        "promotion_candidates": candidates,
        "decay_candidates": decayed,
        "note": "Candidates are NOMINATIONS only. Confirm with the user before writing to "
                "config.watchlist (references/watchlist.md).",
    }, indent=2))


if __name__ == "__main__":
    main()
