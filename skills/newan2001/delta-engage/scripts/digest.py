#!/usr/bin/env python3
"""digest.py — render the twice-weekly brief from the selected set + the model's angles.

The selected posts come from select.py (top.json). The angles come from the model (per
references/angles.md) as a small JSON map keyed by signal raw_id (or post_url) → angle fields.
This script just stitches them into the digest template so formatting is consistent and the model
doesn't re-derive layout every run. Judgment (the angle text) stays with the model; layout is
logistics, so it lives here.

angles.json shape (model writes this):
    {
      "<raw_id or post_url>": {
        "why": "one honest sentence tying it to the ICP",
        "posture": "question-led|experience-led|respectful-challenge",
        "angle": "the one-line strategy",
        "draft": "the ready-to-use reply, in the user's voice, no fabrication",
        "watch_out": "optional caveat / Reddit safety note, e.g. 'r/X bans links; personalize before posting'"
      }, ...
    }

Usage:
    python3 digest.py top.json --angles angles.json -o digest.md
    python3 digest.py top.json -o digest.md          # angles optional; placeholders if absent
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "digest_template.md")


def _age_str(ts: str) -> str:
    from lib.opportunity_signal import parse_ts  # local import keeps top clean
    dt = parse_ts(ts)
    if not dt:
        return "age unknown"
    hrs = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    if hrs < 1:
        return "just now"
    if hrs < 24:
        return f"{hrs:.0f}h ago"
    return f"{hrs/24:.0f}d ago"


def render(top, angles):
    import sys
    sys.path.insert(0, os.path.dirname(__file__))

    with open(TEMPLATE_PATH) as f:
        template = f.read()

    today = datetime.now(timezone.utc).strftime("%a %d %b %Y")
    by_plat = {}
    for s in top:
        by_plat[s["platform"]] = by_plat.get(s["platform"], 0) + 1
    spread = " · ".join(f"{v} {k}" for k, v in by_plat.items())

    def block(i, s):
        key = s.get("raw_id") or s.get("post_url", "")
        a = angles.get(key) or angles.get(s.get("post_url", "")) or {}
        why = a.get("why", "_[add why this cleared the bar]_")
        posture = a.get("posture", "")
        angle = a.get("angle", "_[add the one-line angle per references/angles.md]_")
        draft = a.get("draft", "_[draft the reply per references/angles.md]_")
        watch = a.get("watch_out", "")
        author = s.get("author_handle") or "unknown"
        loc = f"r/{s['topic_tags'][0]}" if s["platform"] == "reddit" and s.get("topic_tags") \
            else f"@{author}"
        intent = s.get("intent", "")
        tag = f" · {intent}" if intent else ""
        head = (f"### {i}. [{s['platform'].upper()}] {loc} · fit {s.get('fit_score','?')}/10{tag} · "
                f"{_age_str(s.get('timestamp',''))}")
        lines = [head,
                 # title may be truncated for display; the URL must NEVER be — a LinkedIn link
                 # without its trailing -activity-<id>- won't resolve (don't add a cap here).
                 f"**{s.get('title','').strip() or s.get('text','')[:100]}**  ",
                 f"{s.get('post_url','')}  ",
                 f"_↑{s.get('score',0)} · {s.get('num_comments',0)} comments_  ",
                 f"**Why it cleared the bar:** {why}  ",
                 f"**Angle{f' ({posture})' if posture else ''}:** {angle}  ",
                 "",  # blank line so the comment stands apart and is easy to spot/copy
                 f"**Comment (edit before posting):**  ",
                 f"> {draft}  "]
        if watch:
            lines.append(f"> ⚠️ **Safety:** {watch}  ")
        return "\n".join(lines)

    # split engage (your ICP: buyers/KOLs) from partnerships (peers/competitors)
    engage = [s for s in top if s.get("bucket") != "partnership"]
    partners = [s for s in top if s.get("bucket") == "partnership"]
    body = ("\n\n".join(block(i, s) for i, s in enumerate(engage, 1))
            if engage else "_No ICP opportunities cleared the bar this run._")
    if partners:
        body += ("\n\n## 🤝 Peers & partnerships\n"
                 "_Not buyers — other practitioners/competitors worth a relationship or collab, "
                 "not a pitch. Engage to start a conversation._\n\n"
                 + "\n\n".join(block(i, s) for i, s in enumerate(partners, len(engage) + 1)))
    return (template
            .replace("{{DATE}}", today)
            .replace("{{COUNT}}", str(len(top)))
            .replace("{{SPREAD}}", spread or "—")
            .replace("{{OPPORTUNITIES}}", body))


def main():
    ap = argparse.ArgumentParser(description="render the engagement digest")
    ap.add_argument("input", help="top.json (selected set)")
    ap.add_argument("--angles", help="angles.json (model-written); optional")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    with open(args.input) as f:
        top = json.load(f)
    angles = {}
    if args.angles and os.path.exists(args.angles):
        with open(args.angles) as f:
            angles = json.load(f)

    md = render(top, angles)
    with open(args.output, "w") as f:
        f.write(md)
    print(f"[digest] wrote {len(top)} opportunities → {args.output}")


if __name__ == "__main__":
    main()
