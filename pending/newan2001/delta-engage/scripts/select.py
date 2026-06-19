#!/usr/bin/env python3
"""select.py — pick the top N, balanced across platforms.

Pure top-N by final_score would let one platform dominate a run (e.g. Reddit floods because it has
more raw volume). The user wants a usable spread across the platforms they enabled, so we balance:
allocate slots roughly evenly across the platforms present, fill each from its own ranked list, then
backfill any shortfall from the global remainder. A platform with genuinely better posts still wins
more slots via backfill — we just don't let raw volume alone decide.

Also enforces a minimum final_score floor so a thin run returns *fewer* solid picks rather than
padding with junk. Better to hand the user 6 worthy posts than 10 where 4 are filler.

Usage:
    python3 select.py ranked.json --n 10 -o top.json
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict


def select(ranked, n, floor, peer_n=2):
    # bucket split: 'partnership' (peers/competitors) is carved out so it can't crowd out real ICP.
    # 'noise' intent is dropped entirely. Everything else is the 'engage' bucket (buyers/KOLs).
    eligible = [s for s in ranked
                if s.get("final_score", 0) >= floor and s.get("intent") != "noise"]
    engage = [s for s in eligible if s.get("bucket") != "partnership"]
    by_platform = defaultdict(list)
    for s in engage:
        by_platform[s["platform"]].append(s)
    for plat in by_platform:
        by_platform[plat].sort(key=lambda x: x.get("final_score", 0), reverse=True)

    platforms = list(by_platform.keys())
    chosen = []
    chosen_ids = set()
    if platforms:
        # even-ish base allocation across platforms present
        base = n // len(platforms)
        for plat in platforms:
            for s in by_platform[plat][:base]:
                chosen.append(s)
                chosen_ids.add(id(s))
        # backfill remaining engage slots from the global remainder by score
        if len(chosen) < n:
            remainder = [s for s in engage if id(s) not in chosen_ids]
            remainder.sort(key=lambda x: x.get("final_score", 0), reverse=True)
            for s in remainder:
                if len(chosen) >= n:
                    break
                chosen.append(s)
                chosen_ids.add(id(s))
        chosen.sort(key=lambda x: x.get("final_score", 0), reverse=True)

    # reserve a capped number of partnership (peer/competitor) picks — surfaced separately, never
    # crowding the engage set. They keep bucket=="partnership" so the digest groups them.
    peers = [s for s in eligible if s.get("bucket") == "partnership"]
    peers.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    chosen += peers[:peer_n]
    return chosen


def main():
    ap = argparse.ArgumentParser(description="select balanced top-N from ranked signals")
    ap.add_argument("input", help="ranked.json")
    ap.add_argument("--n", type=int, default=10, help="opportunities per run")
    ap.add_argument("--floor", type=float, default=1.0,
                    help="minimum final_score to be eligible (drops filler in thin runs)")
    ap.add_argument("--peer-n", type=int, default=2,
                    help="max partnership-bucket (peer/competitor) picks to surface separately")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    with open(args.input) as f:
        ranked = json.load(f)
    top = select(ranked, args.n, args.floor, args.peer_n)
    with open(args.output, "w") as f:
        json.dump(top, f, indent=2)
    n_peer = sum(1 for s in top if s.get("bucket") == "partnership")
    n_engage = len(top) - n_peer
    by_plat = {}
    for s in top:
        by_plat[s["platform"]] = by_plat.get(s["platform"], 0) + 1
    spread = ", ".join(f"{k}:{v}" for k, v in by_plat.items())
    print(f"[select] engage {n_engage}/{args.n} + partnership {n_peer} (floor={args.floor}) "
          f"[{spread}] → {args.output}")


if __name__ == "__main__":
    main()
