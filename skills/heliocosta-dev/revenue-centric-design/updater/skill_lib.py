#!/usr/bin/env python3
"""
skill_lib.py — shared helpers for the Revenue-Centric Design skill updater.

The skill is SELF-DESCRIBING: the set of included posts, the coverage date range,
and the per-theme principle counts are all derived from references/*.md — there is
no separate manifest to drift out of sync. Post dates come from the tweet ID itself
(Twitter Snowflake), so computing coverage needs zero API calls.

Stdlib only.
"""

import re
import datetime
from pathlib import Path

# --- repo layout (updater/ lives inside the skill repo root) ----------------
REPO = Path(__file__).resolve().parent.parent
REFERENCES = REPO / "references"
ASSETS = REPO / "assets"
README = REPO / "README.md"
SKILL_MD = REPO / "SKILL.md"
CHANGELOG = REPO / "CHANGELOG.md"

AUTHOR = "richardrx"

# The 12 curated themes: (slug == references/<slug>.md, human title).
THEMES = [
    ("conversion-and-landing-pages", "Conversion & Landing Pages"),
    ("checkout-and-forms", "Checkout & Forms"),
    ("onboarding-and-activation", "Onboarding & Activation"),
    ("revenue-centric-design", "Revenue-Centric Design"),
    ("pricing-and-monetization", "Pricing & Monetization"),
    ("churn-and-retention", "Churn & Retention"),
    ("dashboards-and-data-viz", "Dashboards & Data Visualization"),
    ("behavioral-science-toolkit", "Behavioral Science Toolkit"),
    ("product-strategy-and-features", "Product Strategy & Features"),
    ("positioning-icp-and-gtm", "Positioning, ICP & GTM"),
    ("ai-era-differentiation", "AI-Era Differentiation"),
    ("metrics-and-experimentation", "Metrics & Experimentation"),
]

# Matches the author's own source posts (ignores any quoted-author URLs).
SRC_RE = re.compile(rf"{AUTHOR}/status/(\d+)")
HEADING_RE = re.compile(r"^## ", re.M)

# Twitter/X Snowflake epoch (2010-11-04T01:42:54.657Z).
_SNOWFLAKE_EPOCH_MS = 1288834974657


# --- tweet id <-> date (Snowflake) ------------------------------------------

def snowflake_date(tweet_id) -> datetime.datetime:
    """UTC datetime a tweet id was created, decoded from the Snowflake id."""
    ms = (int(tweet_id) >> 22) + _SNOWFLAKE_EPOCH_MS
    return datetime.datetime.fromtimestamp(ms / 1000, tz=datetime.timezone.utc)


def post_url(tweet_id) -> str:
    return f"https://x.com/{AUTHOR}/status/{tweet_id}"


# --- reading the skill's own content ----------------------------------------

def reference_files():
    """references/<slug>.md paths, in THEMES order (only those that exist)."""
    return [(slug, title, REFERENCES / f"{slug}.md")
            for slug, title in THEMES
            if (REFERENCES / f"{slug}.md").exists()]


def included_ids_by_theme() -> dict:
    """{slug: [tweet_id, ...]} — the author's posts cited in each theme file."""
    out = {}
    for slug, _title, path in reference_files():
        out[slug] = SRC_RE.findall(path.read_text())
    return out


def included_ids() -> set:
    """Every author post id currently in the skill (across all themes)."""
    ids = set()
    for slug, _title, path in reference_files():
        ids.update(SRC_RE.findall(path.read_text()))
    return ids


def principle_counts() -> dict:
    """{slug: number of `## ` principle entries} per theme."""
    return {slug: len(HEADING_RE.findall(path.read_text()))
            for slug, _title, path in reference_files()}


def coverage():
    """(earliest_date, latest_date, unique_post_count) from included ids."""
    ids = included_ids()
    if not ids:
        return None, None, 0
    dates = [snowflake_date(i) for i in ids]
    return min(dates).date(), max(dates).date(), len(ids)


def totals():
    """Convenience bundle used by refresh_meta and reporting."""
    counts = principle_counts()
    earliest, latest, n_posts = coverage()
    return {
        "principle_counts": counts,
        "principles_total": sum(counts.values()),
        "themes_total": len(counts),
        "posts_total": n_posts,
        "earliest": earliest,
        "latest": latest,
    }
