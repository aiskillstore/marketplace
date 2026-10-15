#!/usr/bin/env python3
"""
fetch_posts.py — Extract X (Twitter) posts + their quoted posts into a
skill-ready dataset: raw JSON (fidelity) + normalized Markdown + downloaded media.

Scope (by design): original post + quoted post (if any) + all images/media.
NO threads / replies. Uses the official X API v2 (pay-per-use friendly).

THE "FLIP THE SWITCH" MODEL
  - posts.txt holds one post URL per line.
  - 1 line  -> single-post test.
  - 91 lines -> full run. Same command, nothing else changes.
  - Re-running within 24h UTC is billed once per post (X de-dups reads).

SETUP
  1. Put your X API v2 *Bearer Token* in .env  ->  X_BEARER_TOKEN=AAAA...
     (Developer Console > your app > Keys and tokens > "Bearer Token".
      Not the API Key/Secret, not a user Access Token.)
  2. Put post URLs in posts.txt (one per line; # comments allowed).
  3. python3 fetch_posts.py

OUTPUT (under ./data/)
  raw/<id>.json     trimmed API response for the post (re-processable, full fidelity)
  posts/<id>.md     normalized, skill-friendly Markdown (text + quote + media + alt text)
  media/<id>__*.jpg downloaded images at original resolution (mp4 for video)
  index.json        manifest of everything fetched, with per-post status

Stdlib only. No dependencies.
"""

import json, os, re, sys, time
import urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW, POSTS, MEDIA = DATA / "raw", DATA / "posts", DATA / "media"
ENV_FILE, POSTS_FILE = ROOT / ".env", ROOT / "posts.txt"
API = "https://api.x.com/2/tweets"
UA = "x-design-wisdom-extractor/1.0"

TWEET_FIELDS = ("created_at,text,author_id,conversation_id,referenced_tweets,"
                "public_metrics,entities,attachments,lang,note_tweet,article,"
                "possibly_sensitive,source")
MEDIA_FIELDS = "url,preview_image_url,type,alt_text,width,height,variants,duration_ms"
USER_FIELDS = "username,name,verified,verified_type,profile_image_url,description"
EXPANSIONS = ("attachments.media_keys,referenced_tweets.id,"
              "referenced_tweets.id.author_id,author_id,"
              "article.media_entities,article.cover_media")

STATUS_RE = re.compile(r"status(?:es)?/(\d{6,})")
NUMERIC_RE = re.compile(r"^\d{6,}$")


# ---------- input -----------------------------------------------------------

def load_bearer():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")  # .env wins over shell env
    tok = os.environ.get("X_BEARER_TOKEN", "").strip().strip('"').strip("'").strip()
    if tok[:7].lower() == "bearer ":   # tolerate a pasted "Bearer " prefix
        tok = tok[7:].strip()
    if not tok:
        sys.exit("ERROR: X_BEARER_TOKEN not set. Add it to .env (see .env.example).")
    return tok


def read_ids():
    if not POSTS_FILE.exists():
        sys.exit(f"ERROR: {POSTS_FILE} not found.")
    ids, seen = [], set()
    for line in POSTS_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = STATUS_RE.search(line)
        tid = m.group(1) if m else (line if NUMERIC_RE.match(line) else None)
        if not tid:
            print(f"  ! skipped (no tweet id found): {line}")
            continue
        if tid not in seen:
            seen.add(tid)
            ids.append(tid)
    if not ids:
        sys.exit("ERROR: no post URLs found in posts.txt (one URL per line).")
    return ids


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


# ---------- API -------------------------------------------------------------

def api_get(ids, bearer):
    qs = urllib.parse.urlencode({
        "ids": ",".join(ids),
        "tweet.fields": TWEET_FIELDS,
        "media.fields": MEDIA_FIELDS,
        "user.fields": USER_FIELDS,
        "expansions": EXPANSIONS,
    })
    req = urllib.request.Request(
        f"{API}?{qs}",
        headers={"Authorization": f"Bearer {bearer}", "User-Agent": UA},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            if e.code == 429:  # rate limited
                reset = e.headers.get("x-rate-limit-reset")
                wait = min(90, max(5, (int(reset) - int(time.time())) if reset else 15))
                print(f"  · rate limited; waiting {wait}s")
                time.sleep(wait)
                continue
            if e.code in (401, 403):
                sys.exit(f"ERROR {e.code}: auth/permission problem. Check the Bearer Token. "
                         f"Response: {body[:300]}")
            sys.exit(f"ERROR {e.code} from X API: {body[:400]}")
        except urllib.error.URLError as e:
            print(f"  · network error ({e}); retry {attempt + 1}/5")
            time.sleep(3)
    sys.exit("ERROR: repeated failures calling the X API.")


def index_includes(resp, media_by_key, users_by_id, tweets_by_id):
    inc = resp.get("includes", {})
    for m in inc.get("media", []):
        media_by_key[m["media_key"]] = m
    for u in inc.get("users", []):
        users_by_id[u["id"]] = u
    for t in inc.get("tweets", []):
        tweets_by_id.setdefault(t["id"], t)


# ---------- media -----------------------------------------------------------

def best_media_url(m):
    if m.get("type") == "photo" and m.get("url"):
        u = m["url"]
        return u + ("&" if "?" in u else "?") + "name=orig"  # original resolution
    variants = [v for v in m.get("variants", [])
                if v.get("content_type") == "video/mp4" and v.get("url")]
    if variants:
        return max(variants, key=lambda v: v.get("bit_rate", 0))["url"]
    return m.get("preview_image_url")


def download(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"  ! media download failed ({url[:60]}...): {e}")
        return False


def save_media(tweet, media_by_key, prefix):
    """Download a tweet's media. Returns list of (relpath, alt_text, kind)."""
    out = []
    keys = media_keys_of(tweet)
    for i, key in enumerate([k for k in keys if k in media_by_key], 1):
        m = media_by_key[key]
        u = best_media_url(m)
        if not u:
            continue
        ext = ".mp4" if (m.get("type") in ("video", "animated_gif") and u.endswith(".mp4")) else ".jpg"
        fn = f"{prefix}__{i}{ext}"
        if download(u, MEDIA / fn):
            out.append((f"../media/{fn}", (m.get("alt_text") or "").strip(), m.get("type")))
    return out


# ---------- rendering -------------------------------------------------------

def full_text(t):
    """Best available text: long-form note_tweet, else X Article body, else `text`."""
    nt = t.get("note_tweet") or {}
    if nt.get("text"):
        return nt["text"].strip()
    art = t.get("article") or {}
    if art.get("plain_text"):
        title = (art.get("title") or "").strip()
        body = art["plain_text"].strip()
        return f"{title}\n\n{body}".strip() if title else body
    return (t.get("text") or "").strip()


def media_keys_of(t):
    """All media keys for a tweet: attachments + X Article cover + article body images."""
    keys = list((t.get("attachments") or {}).get("media_keys", []))
    art = t.get("article") or {}
    cover = art.get("cover_media")
    if isinstance(cover, str):
        keys.append(cover)
    elif isinstance(cover, dict) and cover.get("media_key"):
        keys.append(cover["media_key"])
    for k in (art.get("media_entities") or []):
        if isinstance(k, str):
            keys.append(k)
        elif isinstance(k, dict) and k.get("media_key"):
            keys.append(k["media_key"])
    seen, out = set(), []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def yaml_val(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if v is None:
        return "null"
    if isinstance(v, list):
        return "[" + ", ".join(yaml_val(x) for x in v) + "]"
    s = str(v).replace('"', '\\"')
    return f'"{s}"'


def media_block(saved):
    lines = []
    for rel, alt, kind in saved:
        lines.append(f"\n![{alt or kind or 'image'}]({rel})")
        if alt:
            lines.append(f"*alt text: {alt}*")
    return "\n".join(lines)


def render(tid, t, media_by_key, users_by_id, tweets_by_id):
    author = users_by_id.get(t.get("author_id"), {})
    handle = author.get("username", "unknown")
    name = author.get("name", "")
    url = f"https://x.com/{handle}/status/{tid}"
    text = full_text(t)
    pm = t.get("public_metrics", {}) or {}
    primary_media = save_media(t, media_by_key, tid)

    # quoted / retweeted reference (we ignore replied_to = threads, by design)
    quoted_md, q_manifest = "", None
    for ref in (t.get("referenced_tweets") or []):
        if ref.get("type") not in ("quoted", "retweeted"):
            continue
        q = tweets_by_id.get(ref["id"])
        if not q:
            quoted_md = ("\n\n## Quoted post\n\n"
                         f"> _(referenced post {ref['id']} unavailable — deleted or protected)_")
            q_manifest = {"id": ref["id"], "type": ref.get("type"), "status": "unavailable"}
            break
        qa = users_by_id.get(q.get("author_id"), {})
        qhandle = qa.get("username", "unknown")
        qurl = f"https://x.com/{qhandle}/status/{ref['id']}"
        q_media = save_media(q, media_by_key, f"{tid}__q")
        quoted_md = (f"\n\n## Quoted post — @{qhandle} ({qa.get('name', '')})\n\n"
                     f"{qurl}\n\n{full_text(q)}\n" + media_block(q_media))
        q_manifest = {"id": ref["id"], "type": ref.get("type"), "author": qhandle,
                      "url": qurl, "media": [s[0] for s in q_media]}
        break

    fm = {
        "id": tid, "url": url, "author": f"@{handle}", "author_name": name,
        "created_at": t.get("created_at"), "lang": t.get("lang"),
        "likes": pm.get("like_count"), "reposts": pm.get("retweet_count"),
        "replies": pm.get("reply_count"), "quotes": pm.get("quote_count"),
        "bookmarks": pm.get("bookmark_count"), "impressions": pm.get("impression_count"),
        "media_count": len(primary_media),
        "is_article": bool(t.get("article")),
        "article_title": (t.get("article") or {}).get("title"),
        "has_quote": q_manifest is not None,
        "quoted_url": (q_manifest or {}).get("url"),
        "themes": [],          # <- filled during the curation phase
        "use_in_skill": True,  # <- curation toggle (drop weak posts without deleting data)
    }
    front = "---\n" + "\n".join(f"{k}: {yaml_val(v)}" for k, v in fm.items()) + "\n---\n"
    body = (f"# @{handle}" + (f" — {name}" if name else "") + "\n\n"
            f"{url}  ·  {t.get('created_at', '')}\n\n"
            f"{text}\n" + media_block(primary_media) + quoted_md + "\n")

    raw = {
        "requested_id": tid, "primary": t, "author": author,
        "quoted": tweets_by_id.get(q_manifest["id"]) if (q_manifest and "status" not in q_manifest) else None,
        "media": {k: media_by_key[k] for k in media_keys_of(t) if k in media_by_key},
    }
    manifest = {"id": tid, "status": "ok", "url": url, "author": handle,
                "chars": len(text), "media": len(primary_media),
                "has_quote": q_manifest is not None,
                "long_form": bool(t.get("note_tweet")),
                "is_article": bool(t.get("article"))}
    summary = (f"{len(text)} chars, {len(primary_media)} media"
               + (", +quote" if q_manifest else "")
               + (" [article]" if t.get("article") else "")
               + (" [long-form]" if t.get("note_tweet") else ""))
    return {"md": front + body, "raw": raw, "manifest": manifest, "summary": summary}


# ---------- main ------------------------------------------------------------

def main():
    bearer = load_bearer()
    ids = read_ids()
    for d in (RAW, POSTS, MEDIA):
        d.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {len(ids)} post(s) from the X API...\n")

    media_by_key, users_by_id, tweets_by_id, primaries, errors = {}, {}, {}, {}, []

    # Pass A — the requested posts (batched up to 100/request; 91 fits in one call).
    for batch in chunked(ids, 100):
        resp = api_get(batch, bearer)
        for t in resp.get("data", []):
            primaries[t["id"]] = t
        index_includes(resp, media_by_key, users_by_id, tweets_by_id)
        errors.extend(resp.get("errors", []))

    # Pass B — re-fetch quoted posts as primary so their media/author fully resolve
    # (expanded/included tweets don't always carry their own media into includes.media).
    need = []
    for t in primaries.values():
        for ref in (t.get("referenced_tweets") or []):
            if ref.get("type") not in ("quoted", "retweeted"):
                continue
            q = tweets_by_id.get(ref["id"])
            if q is None:
                need.append(ref["id"])
            else:
                if any(k not in media_by_key for k in media_keys_of(q)):
                    need.append(ref["id"])
    need = list(dict.fromkeys(need))
    if need:
        print(f"Resolving {len(need)} quoted post(s) for media/author...\n")
        for batch in chunked(need, 100):
            resp = api_get(batch, bearer)
            for t in resp.get("data", []):
                tweets_by_id[t["id"]] = t
            index_includes(resp, media_by_key, users_by_id, tweets_by_id)

    # Render in the original input order.
    manifest = []
    for tid in ids:
        t = primaries.get(tid)
        if not t:
            print(f"  ✗ {tid}: not returned (deleted / protected / bad id)")
            manifest.append({"id": tid, "status": "missing"})
            continue
        rec = render(tid, t, media_by_key, users_by_id, tweets_by_id)
        (RAW / f"{tid}.json").write_text(json.dumps(rec["raw"], indent=2, ensure_ascii=False))
        (POSTS / f"{tid}.md").write_text(rec["md"])
        manifest.append(rec["manifest"])
        print(f"  ✓ {tid}: {rec['summary']}")

    DATA.joinpath("index.json").write_text(
        json.dumps({"requested": len(ids),
                    "ok": sum(1 for m in manifest if m.get("status") == "ok"),
                    "posts": manifest, "api_errors": errors}, indent=2, ensure_ascii=False))

    ok = sum(1 for m in manifest if m.get("status") == "ok")
    print(f"\nDone: {ok}/{len(ids)} posts -> {POSTS}")
    print(f"      media -> {MEDIA}   manifest -> {DATA / 'index.json'}")
    if errors:
        print(f"      ({len(errors)} API error entr{'y' if len(errors)==1 else 'ies'} logged in index.json)")


if __name__ == "__main__":
    main()
