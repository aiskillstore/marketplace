#!/usr/bin/env python3
"""
update.py — incremental update for the Revenue-Centric Design skill.

Flow:
  1. Read candidate post URLs from new_posts.txt.
  2. DELTA = candidates NOT already cited in references/*.md (the skill is the manifest).
  3. Fetch only the new posts via the X API (reusing the proven fetch_posts.py).
  4. Stage, per new post: staging/posts/<id>.md (normalized) + downloaded media +
     staging/prompts/<id>.md (the distillation spec pre-filled with this post).

Then a human (or distill.py) drafts the principle, reviews it, pastes it into the
right references/<theme>.md, copies any kept image into ../assets/, and runs
refresh_meta.py. See updater/README.md.

Setup: put your X API v2 Bearer Token in updater/.env  ->  X_BEARER_TOKEN=AAAA...
Stdlib only (imports the sibling fetch_posts.py + skill_lib.py).
"""

import sys
from pathlib import Path

import fetch_posts as fp
import skill_lib as sl

HERE = Path(__file__).resolve().parent
NEW_POSTS = HERE / "new_posts.txt"
STAGING = HERE / "staging"
S_POSTS, S_MEDIA, S_PROMPTS = STAGING / "posts", STAGING / "media", STAGING / "prompts"
DISTILL_SPEC = HERE / "prompts" / "distill.md"


def read_candidates():
    if not NEW_POSTS.exists():
        sys.exit(f"ERROR: {NEW_POSTS} not found. Add candidate post URLs, one per line.")
    ids, seen = [], set()
    for line in NEW_POSTS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = fp.STATUS_RE.search(line)
        tid = m.group(1) if m else (line if fp.NUMERIC_RE.match(line) else None)
        if not tid:
            print(f"  ! skipped (no tweet id): {line}")
            continue
        if tid not in seen:
            seen.add(tid)
            ids.append(tid)
    return ids


def main():
    candidates = read_candidates()
    included = sl.included_ids()
    delta = [c for c in candidates if c not in included]
    already = len(candidates) - len(delta)
    print(f"Candidates: {len(candidates)}  |  already in skill: {already}  |  NEW: {len(delta)}")

    if not delta:
        print("\n✓ Nothing new to add — the skill already covers every post in new_posts.txt.")
        return

    bearer = fp.load_bearer()
    for d in (S_POSTS, S_MEDIA, S_PROMPTS):
        d.mkdir(parents=True, exist_ok=True)
    fp.MEDIA = S_MEDIA  # redirect the fetcher's media downloads into staging/

    media_by_key, users_by_id, tweets_by_id, primaries, errors = {}, {}, {}, {}, []
    print(f"\nFetching {len(delta)} new post(s)...")
    for batch in fp.chunked(delta, 100):
        resp = fp.api_get(batch, bearer)
        for t in resp.get("data", []):
            primaries[t["id"]] = t
        fp.index_includes(resp, media_by_key, users_by_id, tweets_by_id)
        errors.extend(resp.get("errors", []))

    # Pass B — resolve quoted-post media/authors (same logic as a full extraction).
    need = []
    for t in primaries.values():
        for ref in (t.get("referenced_tweets") or []):
            if ref.get("type") not in ("quoted", "retweeted"):
                continue
            q = tweets_by_id.get(ref["id"])
            if q is None or any(k not in media_by_key for k in fp.media_keys_of(q)):
                need.append(ref["id"])
    need = list(dict.fromkeys(need))
    for batch in fp.chunked(need, 100):
        resp = fp.api_get(batch, bearer)
        for t in resp.get("data", []):
            tweets_by_id[t["id"]] = t
        fp.index_includes(resp, media_by_key, users_by_id, tweets_by_id)

    spec = DISTILL_SPEC.read_text()
    staged = 0
    for tid in delta:
        t = primaries.get(tid)
        if not t:
            print(f"  ✗ {tid}: not returned (deleted / protected / bad id)")
            continue
        rec = fp.render(tid, t, media_by_key, users_by_id, tweets_by_id)
        (S_POSTS / f"{tid}.md").write_text(rec["md"])
        imgs = sorted(p.name for p in S_MEDIA.glob(f"{tid}__*"))
        img_line = ", ".join(str(S_MEDIA / n) for n in imgs) or "none"
        (S_PROMPTS / f"{tid}.md").write_text(
            spec
            + "\n\n---\n\n# NEW POST TO DISTILL\n\n"
            + f"Post id: {tid}  ·  date (from id): {sl.snowflake_date(tid).date()}\n"
            + f"Images to view (transcribe only informational ones): {img_line}\n\n"
            + rec["md"]
        )
        print(f"  ✓ {tid}: staged — {rec['summary']}")
        staged += 1

    print(f"\nStaged {staged} new post(s) under {STAGING}/")
    print("Next steps:")
    print("  1. Distill each staging/prompts/<id>.md — run it through Claude (or `python distill.py`),")
    print("     review the draft, then paste the principle into the right references/<theme>.md (newest-first).")
    print("     Copy any `../assets/<file>` image it keeps from staging/media/ into ../assets/.")
    print("  2. Run `python refresh_meta.py` to sync counts + coverage dates in README/SKILL.")
    print("     (posts.txt is a manual rebuild manifest — append the new URLs there too.)")
    if errors:
        print(f"  ({len(errors)} API error entr{'y' if len(errors) == 1 else 'ies'} returned)")


if __name__ == "__main__":
    main()
