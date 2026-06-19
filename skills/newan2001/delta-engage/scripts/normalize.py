#!/usr/bin/env python3
"""normalize.py — merge raw signals across platforms, validate, and dedup.

Takes one or more adapter output files (each a JSON list of OpportunitySignal) and produces one
merged, deduped list. Dedup is two-pass:

  1. Exact dedup on (platform, raw_id) and on normalized post_url — the same post pulled twice.
  2. Theme collapse — near-duplicate *posts* (same author + very similar text) are collapsed so a
     cross-poster or a reposted thread doesn't eat multiple slots. This is conservative: it only
     collapses when text overlap is high, because losing a genuinely distinct post is worse than
     keeping a near-dup the ranker can sort out.

Deterministic and fast — this is logistics, not judgment, so it's a script the model never has to
reason through.

Usage:
    python3 normalize.py raw_reddit.json raw_linkedin.json -o signals.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib.opportunity_signal import validate  # noqa: E402

_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall((text or "").lower()))


def _norm_url(url: str) -> str:
    if not url:
        return ""
    u = url.split("?")[0].split("#")[0].rstrip("/")
    return u.lower()


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / len(a | b)


def load_all(paths):
    signals = []
    for p in paths:
        with open(p) as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"warn: {p} is not a JSON list, skipping", file=sys.stderr)
            continue
        signals.extend(data)
    return signals


def dedup(signals, theme_threshold=0.82):
    # pass 1: exact dedup
    by_key = {}
    for s in signals:
        problems = validate(s)
        if problems:
            print(f"warn: dropping invalid signal ({'; '.join(problems)})", file=sys.stderr)
            continue
        key = (s["platform"], s.get("raw_id") or _norm_url(s.get("post_url", "")))
        url = _norm_url(s.get("post_url", ""))
        # prefer the record with more engagement signal if collision
        if key in by_key:
            if (s.get("score", 0) + s.get("num_comments", 0)) > \
               (by_key[key].get("score", 0) + by_key[key].get("num_comments", 0)):
                by_key[key] = s
            continue
        # also catch same-url under different ids
        dup_url = next((k for k, v in by_key.items() if url and _norm_url(v.get("post_url", "")) == url), None)
        if dup_url:
            continue
        by_key[key] = s
    exact = list(by_key.values())

    # pass 2: theme collapse (same author + high text overlap)
    kept = []
    token_cache = [(_tokens(s.get("text", "")), s) for s in exact]
    used = [False] * len(token_cache)
    for i, (toks_i, s_i) in enumerate(token_cache):
        if used[i]:
            continue
        group = [s_i]
        for j in range(i + 1, len(token_cache)):
            if used[j]:
                continue
            toks_j, s_j = token_cache[j]
            same_author = (s_i.get("author_handle", "").lower() ==
                           s_j.get("author_handle", "").lower() and s_i.get("author_handle"))
            if same_author and _jaccard(toks_i, toks_j) >= theme_threshold:
                used[j] = True
                group.append(s_j)
        # keep the most-engaged representative of the theme group
        rep = max(group, key=lambda x: x.get("score", 0) + x.get("num_comments", 0))
        if len(group) > 1:
            rep = dict(rep)
            rep["_theme_collapsed"] = len(group)
        kept.append(rep)
        used[i] = True
    return kept


def main():
    ap = argparse.ArgumentParser(description="merge + dedup raw signals across platforms")
    ap.add_argument("inputs", nargs="+", help="adapter output JSON files")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--theme-threshold", type=float, default=0.82,
                    help="text-overlap threshold for collapsing same-author near-dups (0-1)")
    args = ap.parse_args()

    raw = load_all(args.inputs)
    deduped = dedup(raw, args.theme_threshold)
    with open(args.output, "w") as f:
        json.dump(deduped, f, indent=2)
    print(f"[normalize] {len(raw)} raw → {len(deduped)} after dedup → {args.output}")


if __name__ == "__main__":
    main()
