---
name: tiktok-api
description: >-
  A TikTok API alternative on fetcher.sh — pay-per-call in USDC via x402, or
  prepaid credits with a Bearer key, no login and no app review. Use when the
  user wants to search TikTok posts by keyword and sort by most-liked or most
  recent within a date range, look up a post by its share URL or ID, scrape a
  TikTok profile by @username, pull a user's posts, followers, or followings,
  fetch a hashtag's posts, pull posts using a specific sound/music track, get
  posts from a location, or read a post's comments and comment replies. Also
  covers TikTok trend tracking, hashtag monitoring, influencer discovery,
  competitor content analysis, and TikTok data pipelines without official
  TikTok API access or a scraping browser.
keywords:
  - tiktok
  - tiktok-api
  - tiktok-api-alternative
  - tiktok-data
  - social-media
  - social-listening
  - hashtag-tracking
  - x402
  - ai-agent
---

# TikTok API

TikTok data on demand: keyword post search with sort/date filters, profile
lookup by handle, followers and followings, hashtag and music/sound feeds,
location-based posts, and comment threads — one plain HTTP GET per call, paid
as you go. No login, no session cookies, no browser automation, no TikTok
developer app review.

Base URL: `https://tiktok.fetcher.sh`

## Quick reference

| | |
| --- | --- |
| Base URL | `https://tiktok.fetcher.sh` |
| Auth | `Authorization: Bearer bby_live_...` or x402 (USDC) |
| Price | $0.004/call (flat) |
| Endpoints | 13, all `GET` |
| MCP | `https://tiktok.fetcher.sh/mcp` |
| Machine-readable | `/openapi.json` · `/llms.txt` · `/skill.md` |

## Which endpoint do I need?

| I want to... | Call |
| --- | --- |
| Search posts by keyword (optionally most-liked/recent) | `GET /api/post/search` |
| Look up a post by its share URL | `GET /api/post?url=...` |
| Look up a profile by @username | `GET /api/user/handle/{username}` |
| Get a user's posts, followers, or followings | `GET /api/user/{id}/posts` / `/followers` / `/followings` |
| Get a post's comments | `GET /api/post/{id}/comments` |
| Find posts under a hashtag | `GET /api/hashtag/{id}/posts` |
| Find posts using a specific sound | `GET /api/music/{id}/posts` |

Full param details for every row: [`references/endpoints.md`](references/endpoints.md).

## Authentication

Two ways to pay, same data — full mechanics in the [`fetcher`
skill](../fetcher/SKILL.md):

```bash
# 1. Prepaid credits (recommended — get a key at https://fetcher.sh/topup
#    or via POST /api/credits/topup, see the fetcher skill)
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/search?keyword=hello"

# 2. x402 pay-per-call — omit the header; a GET with no payment returns 402
#    with machine-readable payment requirements (USDC on Base, Polygon,
#    Arbitrum, Monad, or Solana). @x402/fetch signs and retries automatically.
```

Every response is `{ "status": number, "message": string, "data": ... }`; the
HTTP status mirrors `status`.

## Endpoints (13 — all GET, $0.004/call)

| Endpoint | What it returns |
| --- | --- |
| `/api/post/search` | Posts matching a keyword; sort and date-range filters |
| `/api/post` | A single post resolved from its share URL |
| `/api/post/{id}` | A single post by ID |
| `/api/post/{id}/comments` | A post's comments |
| `/api/post/{id}/comments/{commentId}/replies` | Replies to a comment |
| `/api/user/handle/{username}` | Profile by @username |
| `/api/user/{id}/posts` | A user's posts |
| `/api/user/{id}/followers` | A user's followers |
| `/api/user/{id}/followings` | Accounts a user follows |
| `/api/hashtag/handle/{name}` | Hashtag metadata by name |
| `/api/hashtag/{id}/posts` | Posts under a hashtag |
| `/api/music/{id}/posts` | Posts using a sound/music track |
| `/api/location/{locationId}/posts` | Posts tagged at a location |

`{id}` / `{username}` / `{name}` are path parameters. Optional query params
(`cursor`, `region`) paginate or geo-scope results; `keyword` (search) and
`url` (post lookup) are required where they appear.

## Scenarios

**Most liked posts this month:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=ai agent" -G \
  --data-urlencode "sortType=MOST_LIKED" \
  --data-urlencode "dateRange=THIS_MONTH" \
  "https://tiktok.fetcher.sh/api/post/search"
```

**Posted yesterday, most recent first:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=crypto payments" -G \
  --data-urlencode "sortType=DATE_POSTED" \
  --data-urlencode "dateRange=YESTERDAY" \
  "https://tiktok.fetcher.sh/api/post/search"
```

Other `sortType` values: `RELEVANCE`. Other `dateRange` values: `ALL_TIME`,
`THIS_WEEK`, `LAST_THREE_MONTHS`, `LAST_SIX_MONTHS`.

**Look up a post by its share URL, or directly by ID:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" -G \
  --data-urlencode "url=https://www.tiktok.com/@username/video/1234567890123456789" \
  "https://tiktok.fetcher.sh/api/post"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789"
```

**A post's comments and comment replies:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789/comments"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/1234567890123456789/comments/9876543210/replies"
```

**A profile by @handle, then its posts, followers, and followings:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/handle/khaby.lame"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6935741396776976390/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6935741396776976390/followers"
```

**A hashtag's metadata, then its posts:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/hashtag/handle/fyp"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/hashtag/1234567890/posts"
```

**Posts using a specific sound, and posts from a location:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/music/1234567890123456789/posts"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/location/1234567890123456789/posts"
```

## MCP

```json
{
  "mcpServers": {
    "tiktok": {
      "url": "https://tiktok.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

Free: `search_endpoints`, `describe_endpoint`, `check_balance`. Paid:
`fetch_data` (any endpoint above), `topup_credits`, plus the named shortcut
`tiktok_post_search`. Drop the `headers` block to pay per call with x402
instead — see the [`fetcher` skill](../fetcher/SKILL.md) for the full flow.

## Errors

- `400` — missing/invalid parameter (message names it)
- `401` — unknown or rotated key
- `402` — payment required (x402 challenge) or `topup_required` (credits
  exhausted)
- `404` — not a priced path
- No rate limits; no refunds on upstream failures (settlement precedes
  delivery)

## Reference

- Deep dives: [`references/endpoints.md`](references/endpoints.md) (every
  param) · [`references/scenarios.md`](references/scenarios.md) (one `curl`
  per endpoint) · [`references/faq.md`](references/faq.md) ·
  [`references/comparison.md`](references/comparison.md) (vs. the official
  TikTok API and a browser scraper)
- Task guides: [viral post search](../../task-guides/tiktok-viral-post-search.md) ·
  [profile and followers](../../task-guides/tiktok-profile-and-followers.md)
- Slash command: [`/tiktok-search`](../../commands/tiktok-search.md)
- Full agent setup: <https://tiktok.fetcher.sh/skill.md>
- OpenAPI 3.1 contract: <https://tiktok.fetcher.sh/openapi.json>
- Condensed catalog: <https://tiktok.fetcher.sh/llms.txt>
- Payment, credits, and MCP deep dive: [`fetcher` skill](../fetcher/SKILL.md)
- Site: <https://tiktok.fetcher.sh>
