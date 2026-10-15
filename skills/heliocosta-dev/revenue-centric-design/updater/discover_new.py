#!/usr/bin/env python3
"""
discover_new.py — OPTIONAL. List @richardrx ORIGINAL posts made since the skill's
coverage date that aren't in the skill yet, so you don't have to hunt for new URLs.

It prints CANDIDATES only — you still curate which are worth adding (step 2). By
default it applies NO topical filter, so personal / off-topic posts appear too.
Pass --rank to have Claude tag each candidate on-topic / off-topic with a one-line
reason, so the list comes pre-triaged.

Paste the good ones into new_posts.txt, then run update.py.

Uses the X API v2 user-timeline endpoint (a few reads = pennies). --rank also needs
`pip install anthropic` + an API key (or `ant auth login`).
Setup: X_BEARER_TOKEN in updater/.env. Stdlib only unless --rank is used.
"""

import argparse
import datetime
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

import fetch_posts as fp
import skill_lib as sl

API = "https://api.x.com/2"
RANK_MODEL = "claude-opus-4-8"

SCOPE = (
    "The skill 'Revenue-Centric Design' curates @richardrx's product-design wisdom for "
    "SaaS/startups: conversion & landing pages, checkout/forms, onboarding/activation, "
    "churn/retention, pricing & monetization psychology, dashboards/data visualization, "
    "behavioral-science tactics, product/feature strategy, positioning/ICP/go-to-market, "
    "AI-era differentiation, and metrics/experimentation. OFF-topic = purely personal, "
    "life updates, memes, "
    "politics, banter with no product/design lesson, or promos with no reusable insight."
)


def get(url, bearer):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {bearer}", "User-Agent": "rcd-skill-discover/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def collect(bearer, start):
    """All @richardrx original posts since `start` not already cited in the skill."""
    uid = get(f"{API}/users/by/username/{sl.AUTHOR}", bearer)["data"]["id"]
    included = sl.included_ids()
    out, token = [], None
    while True:
        params = {"max_results": "100", "exclude": "replies,retweets",
                  "tweet.fields": "created_at,text", "start_time": start}
        if token:
            params["pagination_token"] = token
        resp = get(f"{API}/users/{uid}/tweets?" + urllib.parse.urlencode(params), bearer)
        for t in resp.get("data", []):
            if t["id"] not in included:
                out.append(t)
        token = resp.get("meta", {}).get("next_token")
        if not token:
            break
    return sorted(out, key=lambda x: x["id"], reverse=True)


def rank(candidates):
    """{id: (on_topic_bool, reason)} via Claude. Empty dict if anthropic/key unavailable."""
    try:
        import anthropic
        from pydantic import BaseModel
    except ImportError:
        print("  (--rank needs `pip install anthropic`; showing unranked)\n")
        return {}

    class Verdict(BaseModel):
        index: int
        on_topic: bool
        reason: str

    class Ranking(BaseModel):
        verdicts: list[Verdict]

    listing = "\n\n".join(
        f"[{i}] {(t.get('text') or '').strip()[:600]}" for i, t in enumerate(candidates))
    try:
        resp = anthropic.Anthropic().messages.parse(
            model=RANK_MODEL, max_tokens=4000,
            system=("Classify each numbered post as on-topic or off-topic for this skill. "
                    + SCOPE + " Return one verdict per index with a one-line reason."),
            messages=[{"role": "user", "content": listing}],
            output_format=Ranking,
        )
    except anthropic.APIError as e:
        print(f"  (--rank failed: {e}; showing unranked)\n")
        return {}
    parsed = resp.parsed_output
    if not parsed:
        return {}
    return {candidates[v.index]["id"]: (v.on_topic, v.reason)
            for v in parsed.verdicts if 0 <= v.index < len(candidates)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rank", action="store_true",
                    help="tag each candidate on-topic/off-topic via Claude (needs anthropic + API key)")
    args = ap.parse_args()

    bearer = fp.load_bearer()
    _e, latest, _n = sl.coverage()
    if latest is None:
        sys.exit("No coverage found (empty references?).")
    start = datetime.datetime.combine(latest, datetime.time()).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Scanning @{sl.AUTHOR} posts since {latest} (skill's latest) not yet included...\n")
    try:
        candidates = collect(bearer, start)
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR {e.code} from X API: {e.read().decode()[:200]}")
    except (urllib.error.URLError, KeyError) as e:
        sys.exit(f"ERROR contacting X API: {e}")

    if not candidates:
        print("✓ Nothing new — the skill is up to date with @richardrx's recent posts.")
        return

    tags = rank(candidates) if args.rank else {}
    header = f"{len(candidates)} candidate post(s) not in the skill"
    if tags:
        on = sum(1 for c in candidates if tags.get(c["id"], (True, ""))[0])
        header += f"  ({on} tagged on-topic)"
    print(header + ":\n")
    for t in candidates:
        first = (t.get("text") or "").replace("\n", " ")[:90]
        tag = ""
        if t["id"] in tags:
            ok, why = tags[t["id"]]
            tag = f"   [{'ON-topic' if ok else 'off-topic?'}] {why}"
        print(f"  {sl.post_url(t['id'])}{tag}")
        print(f"      {t.get('created_at', '')[:10]}  {first}…\n")
    print("Curate the worthwhile ones into new_posts.txt, then run `python update.py`.")


if __name__ == "__main__":
    main()
