#!/usr/bin/env python3
"""LinkedIn adapter → OpportunitySignal[]  (COOKIELESS ONLY).

Hard rule: this skill only ever uses logged-out / public LinkedIn actors. A cookie/session actor
*is* the user's account making automated requests — the exact thing that gets accounts banned. The
human engages manually from their real account, so we never need their session. This adapter
**refuses cookie input** by design. See references/DECISIONS.md.

Two cookieless paths, both via APIFY_API_TOKEN, emitting the same OpportunitySignal:
  • DISCOVERY (topics)  → apimaestro keyword search actor (one keyword per run; "explore").
  • MONITORING (profiles) → harvestapi/linkedin-profile-posts via targetUrls ("exploit" — watch
    specific people you already care about). Takes profile URLs directly; no member-URN dance.

Usage:
    python3 linkedin_adapter.py --config config.json -o raw_linkedin.json
    python3 linkedin_adapter.py --topics "voice ai,sdr automation" --profiles https://linkedin.com/in/foo -o out.json

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

# A cookieless / public post-search actor (confirmed on Apify, advertises "no login required").
# Escape hatch — also cookieless, same token: set DELTA_ENGAGE_LI_ACTOR=harvestapi~linkedin-post-search
# IMPORTANT: must be a logged-out actor — never one that takes li_at / session cookies.
APIFY_COOKIELESS_ACTOR = os.environ.get(
    "DELTA_ENGAGE_LI_ACTOR", "apimaestro~linkedin-posts-search-scraper-no-cookies"
)
# Cookieless profile-posts actor — takes profile URLs directly (targetUrls). Used for seed-profile
# monitoring ("exploit"). Also no login/cookies required.
APIFY_PROFILE_ACTOR = os.environ.get(
    "DELTA_ENGAGE_LI_PROFILE_ACTOR", "harvestapi~linkedin-profile-posts"
)

COOKIE_KEYS = ("cookie", "cookies", "li_at", "sessionCookie", "session_cookie", "jsessionid")


def _load_config(path):
    if not path:
        return {}
    with open(path) as f:
        return json.load(f)


def _assert_cookieless(actor_input: dict):
    """Guardrail: refuse to run if anyone tries to smuggle a session cookie into the actor input."""
    lowered = {k.lower() for k in actor_input}
    bad = lowered & set(COOKIE_KEYS)
    if bad:
        print(f"REFUSED: cookie-based input detected ({sorted(bad)}). This skill is cookieless-only "
              "by design — see references/DECISIONS.md.", file=sys.stderr)
        sys.exit(3)


def _date_filter(days):
    """Map a day window to the actor's date_filter enum: '', past-1h, past-24h, past-week,
    past-month (no longer window exists, so anything > a month is capped at past-month)."""
    if days <= 1:
        return "past-24h"
    if days <= 7:
        return "past-week"
    return "past-month"


def _run_actor(token, actor, actor_input):
    """Start one actor run, poll to completion, return its dataset items."""
    import requests
    _assert_cookieless(actor_input)
    run = requests.post(
        f"https://api.apify.com/v2/acts/{actor}/runs",
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
    if not st or st["status"] != "SUCCEEDED":
        print(f"[linkedin] run status: {st and st.get('status')}", file=sys.stderr)
        return []
    return requests.get(f"https://api.apify.com/v2/datasets/{st['defaultDatasetId']}/items",
                        params={"token": token, "format": "json"}, timeout=60).json()


def _vanity_from_url(url):
    """Extract the /in/<vanity> handle from a LinkedIn profile URL. Returns "" for non-profile
    URLs (e.g. /company/ pages) so the caller falls back to the author's display name."""
    if not url or "/in/" not in url:
        return ""
    return url.split("/in/", 1)[-1].split("?", 1)[0].split("/", 1)[0]


def _to_signal(d, source):
    author = d.get("author", {}) or {}
    stats = d.get("stats", {}) or {}
    posted = d.get("posted_at", {}) or {}
    # posted_at.date looks like "2026-06-11 20:22:21" (treat as UTC)
    ts = posted.get("date", "")
    if ts and " " in ts and "T" not in ts:
        ts = ts.replace(" ", "T") + "Z"
    author_url = author.get("profile_url", "")
    handle = _vanity_from_url(author_url) or author.get("name", "")
    text = d.get("text", "") or ""
    return make_signal(
        platform="linkedin",
        post_url=d.get("post_url", "") or "",
        author_handle=handle,
        author_url=author_url,
        text=text,
        title=text[:120],
        timestamp=ts,
        score=stats.get("total_reactions", 0) or 0,
        num_comments=stats.get("comments", 0) or 0,
        topic_tags=d.get("hashtags", []) or [],
        source_provider=source,
        raw_id=str(d.get("activity_id") or d.get("full_urn") or d.get("post_url", "")),
    )


def search_apify_cookieless(token, topics, profiles, max_items, days):
    """The apimaestro cookieless actor takes ONE keyword per run, so we loop over topics and
    aggregate. (Profile-URL monitoring needs LinkedIn member URNs, which this actor takes as
    `member_urns` — URL→URN resolution isn't wired yet; see DECISIONS. Topic search covers cold
    start regardless.)"""
    keywords = [t.strip() for t in topics if t.strip()][:5]  # cap runs to control spend
    if not keywords:
        print("[linkedin] no topic keywords to search (this actor is keyword-driven).",
              file=sys.stderr)
        return []
    per_kw = max(10, max_items // max(1, len(keywords)))
    date_filter = _date_filter(days)
    out = []
    for kw in keywords:
        items = _run_actor(token, APIFY_COOKIELESS_ACTOR, {
            "keyword": kw,
            "sort_type": "date_posted",   # freshest first; recency matters for engagement
            "date_filter": date_filter,
            "page_number": 1,
            "total_posts": per_kw,
        })
        for d in items:
            out.append(_to_signal(d, "apify_cookieless"))
        print(f"[linkedin] keyword '{kw}': {len(items)} posts", file=sys.stderr)
    return out


def _profile_posted_limit(days):
    """Map a day window to harvestapi's postedLimit enum:
    any, 1h, 24h, week, month, 3months, 6months, year."""
    if days <= 1:
        return "24h"
    if days <= 7:
        return "week"
    if days <= 31:
        return "month"
    if days <= 93:
        return "3months"
    return "year"


def _profile_post_to_signal(d):
    """Map a harvestapi/linkedin-profile-posts item to OpportunitySignal. Reaction/comment counts
    only populate when scrapeReactions/scrapeComments are on (extra cost) — otherwise best-effort,
    so seed-profile posts rank on recency + fit, which is what matters for known people."""
    author = d.get("author", {}) or {}
    posted = d.get("postedAt", {}) or {}
    social = d.get("socialContent", {}) or {}
    author_url = (author.get("linkedinUrl", "") or "").split("?", 1)[0]
    handle = author.get("publicIdentifier") or _vanity_from_url(author_url) or author.get("name", "")
    text = d.get("content", "") or ""
    # counts are best-effort across possible field names
    score = (social.get("numLikes") or social.get("reactionsCount")
             or d.get("reactionsCount") or d.get("numLikes") or 0)
    comments = d.get("comments")
    num_comments = (social.get("numComments") or d.get("commentsCount")
                    or (len(comments) if isinstance(comments, list) else 0) or 0)
    return make_signal(
        platform="linkedin",
        post_url=d.get("linkedinUrl", "") or d.get("shareUrl", ""),
        author_handle=handle,
        author_url=author_url,
        text=text,
        title=text[:120],
        timestamp=posted.get("date", ""),
        score=score,
        num_comments=num_comments,
        topic_tags=[],
        source_provider="apify_cookieless_profile",
        raw_id=str(d.get("id") or d.get("entityId") or d.get("linkedinUrl", "")),
    )


def monitor_profiles_cookieless(token, profiles, max_posts_per, days):
    """Seed-profile monitoring via harvestapi/linkedin-profile-posts. Takes profile URLs directly
    (targetUrls) — no member-URN resolution needed. One run covers all profiles."""
    urls = [p.strip() for p in profiles if p.strip()]
    if not urls:
        return []
    items = _run_actor(token, APIFY_PROFILE_ACTOR, {
        "targetUrls": urls,
        "maxPosts": max_posts_per,
        "postedLimit": _profile_posted_limit(days),
        "scrapeReactions": False,   # flip on (with maxReactions) if engagement counts are needed
        "scrapeComments": False,
    })
    out = [_profile_post_to_signal(d) for d in items if d.get("type", "post") == "post"]
    print(f"[linkedin] monitored {len(urls)} seed profile(s): {len(out)} posts", file=sys.stderr)
    return out


def main():
    ap = argparse.ArgumentParser(description="LinkedIn adapter (cookieless) → OpportunitySignal[]")
    ap.add_argument("--config")
    ap.add_argument("--topics", help="comma-separated (overrides config topics)")
    ap.add_argument("--profiles", help="comma-separated LinkedIn profile URLs (overrides config)")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--max-items", type=int, default=60, help="cap for keyword discovery")
    ap.add_argument("--max-posts-per", type=int, default=5,
                    help="recent posts to pull per monitored seed profile")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    cfg = _load_config(args.config)
    topics = args.topics.split(",") if args.topics else cfg.get("topics", [])
    profiles = (args.profiles.split(",") if args.profiles
                else cfg.get("seed_accounts", {}).get("linkedin_profiles", []))
    if not topics and not profiles:
        print("error: no topics or profiles (provide --topics/--profiles or a config)",
              file=sys.stderr)
        sys.exit(2)

    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        print("error: set APIFY_API_TOKEN (LinkedIn uses cookieless Apify actors; no session "
              "cookie is ever used — see references/DECISIONS.md).", file=sys.stderr)
        sys.exit(1)

    # DISCOVERY (topics) + MONITORING (seed profiles), merged. normalize.py dedups across them.
    signals = search_apify_cookieless(token, topics, profiles, args.max_items, args.days)
    if profiles:
        signals += monitor_profiles_cookieless(token, profiles, args.max_posts_per, args.days)

    with open(args.output, "w") as f:
        json.dump(signals, f, indent=2)
    print(f"[linkedin] wrote {len(signals)} signals → {args.output}")


if __name__ == "__main__":
    main()
