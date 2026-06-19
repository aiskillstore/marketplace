"""OpportunitySignal — the normalized schema every adapter emits and the pipeline consumes.

Keeping one shared schema is what makes adapters swappable: a dying provider is a one-file change,
not a rewrite, because nothing downstream ever sees a provider's raw shape. normalize/rank/select/
digest all speak OpportunitySignal and nothing else.

A signal is a plain dict (JSON-friendly) with these keys:

    platform        str    "reddit" | "linkedin" | "x"
    post_url        str    canonical URL to the post
    author_handle   str    username / profile handle (no leading @)
    author_url      str    profile URL if known, else ""
    text            str    post body / title (the thing we judge relevance on)
    title           str    short title or first line for display (may equal text[:120])
    timestamp       str    ISO-8601 UTC of the post, e.g. "2026-06-10T14:03:00Z"
    score           int    upvotes (reddit) / reactions (linkedin) / likes (x), as rendered
    num_comments    int    comment/reply count as rendered
    topic_tags      [str]  detected topic/pain tags (adapter best-effort; may be [])
    source_provider str    which provider produced it, e.g. "reddit_official", "apify_cookieless"
    raw_id          str    provider-native id, for dedup stability

Fields added later in the pipeline (not by adapters):
    fit_score             int    0-10, written by the model per references/ranking.md
    engagement_potential  float  0-1, written by rank.py
    final_score           float  fit_score * engagement_potential, written by rank.py
    rank_reason           str    short machine note, written by rank.py
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

PLATFORMS = ("reddit", "linkedin", "x")

REQUIRED_KEYS = (
    "platform", "post_url", "author_handle", "text", "timestamp",
    "score", "num_comments", "source_provider", "raw_id",
)


def make_signal(
    platform: str,
    post_url: str,
    author_handle: str,
    text: str,
    timestamp: str,
    score: int = 0,
    num_comments: int = 0,
    *,
    author_url: str = "",
    title: str = "",
    topic_tags=None,
    source_provider: str = "",
    raw_id: str = "",
) -> dict:
    """Build a normalized signal dict with sane defaults. Adapters should funnel through this so
    the shape is guaranteed identical regardless of provider."""
    if platform not in PLATFORMS:
        raise ValueError(f"unknown platform {platform!r}; expected one of {PLATFORMS}")
    text = (text or "").strip()
    return {
        "platform": platform,
        "post_url": post_url or "",
        "author_handle": (author_handle or "").lstrip("@").strip(),
        "author_url": author_url or "",
        "text": text,
        "title": (title or text[:120]).strip(),
        "timestamp": timestamp or "",
        "score": int(score or 0),
        "num_comments": int(num_comments or 0),
        "topic_tags": list(topic_tags or []),
        "source_provider": source_provider or "",
        "raw_id": str(raw_id or post_url or ""),
    }


def validate(signal: dict) -> list[str]:
    """Return a list of problems with a signal (empty list = valid). Cheap guardrail for adapters."""
    problems = []
    for k in REQUIRED_KEYS:
        if k not in signal:
            problems.append(f"missing key: {k}")
    if signal.get("platform") not in PLATFORMS:
        problems.append(f"bad platform: {signal.get('platform')!r}")
    if not signal.get("text"):
        problems.append("empty text")
    return problems


def parse_ts(ts: str):
    """Parse an ISO-8601 timestamp to an aware datetime (UTC). Returns None if unparseable."""
    if not ts:
        return None
    s = ts.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        # try epoch seconds
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc)
        except (ValueError, OSError):
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def age_hours(signal: dict, now: datetime | None = None) -> float:
    """Hours since the post was made. Large number if timestamp is missing/unparseable (so old/
    unknown posts rank low rather than crashing)."""
    now = now or datetime.now(timezone.utc)
    dt = parse_ts(signal.get("timestamp", ""))
    if dt is None:
        return 1e6
    return max(0.0, (now - dt).total_seconds() / 3600.0)


# --- platform normalization of reach -------------------------------------------------------------
# Upvotes and reactions are not the same unit. These rough divisors put them on a comparable log
# scale so a LinkedIn post with 40 reactions and a Reddit post with 120 upvotes read similarly.
# Tunable; deliberately conservative.
_REACH_DIVISOR = {"reddit": 1.0, "linkedin": 0.35, "x": 0.6}


def reach_score(signal: dict) -> float:
    """Log-scaled, platform-normalized reach in roughly [0, 1+]."""
    raw = max(0, int(signal.get("score", 0)))
    div = _REACH_DIVISOR.get(signal.get("platform"), 1.0)
    # log1p compresses; divide to normalize a "good" post toward ~1.0
    return math.log1p(raw * div) / math.log1p(150.0)
