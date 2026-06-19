#!/usr/bin/env python3
"""X (Twitter) adapter → OpportunitySignal[]  — OPTIONAL, off by default.

Enabled only when config.platforms includes "x". No viable free-tier API fallback, so this runs
via an Apify X actor and needs APIFY_API_TOKEN. See references/DECISIONS.md (§X positioning).

Usage:
    python3 x_adapter.py --config config.json -o raw_x.json
    python3 x_adapter.py --topics "voice ai,cold email" -o out.json

Dependency: requests
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.opportunity_signal import make_signal  # noqa: E402

APIFY_X_ACTOR = os.environ.get("DELTA_ENGAGE_X_ACTOR", "apidojo~tweet-scraper")


def _load_config(path):
    if not path:
        return {}
    with open(path) as f:
        return json.load(f)


def search_apify_x(token, topics, max_items, days):
    import requests
    actor_input = {
        "searchTerms": [t.strip() for t in topics if t.strip()],
        "maxItems": max_items,
        "sort": "Latest",
        "tweetLanguage": "en",
    }
    run = requests.post(
        f"https://api.apify.com/v2/acts/{APIFY_X_ACTOR}/runs",
        params={"token": token}, json=actor_input, timeout=60,
    )
    run.raise_for_status()
    run_id = run.json()["data"]["id"]
    st = None
    for _ in range(90):
        time.sleep(5)
        st = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}",
                          params={"token": token}, timeout=30).json()["data"]
        if st["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
    ds_id = st["defaultDatasetId"]
    items = requests.get(f"https://api.apify.com/v2/datasets/{ds_id}/items",
                         params={"token": token, "format": "json"}, timeout=60).json()
    cutoff = time.time() - days * 86400
    out = []
    for d in items:
        author = d.get("author", {}) or {}
        out.append(make_signal(
            platform="x",
            post_url=d.get("url", "") or d.get("twitterUrl", ""),
            author_handle=author.get("userName", "") or d.get("username", ""),
            author_url=author.get("url", ""),
            text=d.get("text", "") or d.get("full_text", ""),
            title=(d.get("text", "") or "")[:120],
            timestamp=str(d.get("createdAt", "")),
            score=d.get("likeCount", d.get("favorite_count", 0)) or 0,
            num_comments=d.get("replyCount", 0) or 0,
            topic_tags=[h.get("text", "") for h in d.get("entities", {}).get("hashtags", [])]
            if isinstance(d.get("entities"), dict) else [],
            source_provider="x_apify",
            raw_id=str(d.get("id", d.get("url", ""))),
        ))
    return out


def main():
    ap = argparse.ArgumentParser(description="X adapter (optional) → OpportunitySignal[]")
    ap.add_argument("--config")
    ap.add_argument("--topics", help="comma-separated (overrides config topics)")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--max-items", type=int, default=60)
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    cfg = _load_config(args.config)
    if cfg and "x" not in cfg.get("platforms", []) and not args.topics:
        print("[x] 'x' not in config.platforms and no --topics given; nothing to do.",
              file=sys.stderr)
        with open(args.output, "w") as f:
            json.dump([], f)
        return
    topics = args.topics.split(",") if args.topics else cfg.get("topics", [])
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        print("error: set APIFY_API_TOKEN (X has no free-tier fallback — see DECISIONS).",
              file=sys.stderr)
        sys.exit(1)
    signals = search_apify_x(token, topics, args.max_items, args.days)
    with open(args.output, "w") as f:
        json.dump(signals, f, indent=2)
    print(f"[x] wrote {len(signals)} signals → {args.output}")


if __name__ == "__main__":
    main()
