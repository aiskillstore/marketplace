---
name: tiktok-api-faq
description: Frequently asked questions about the TikTok API on fetcher.sh — viral search, followers, monitoring, and rate limits, answered with exact endpoints.
---

# TikTok API alternative — FAQ

## Getting started

### Do I need a TikTok developer account or app review?

No. `tiktok.fetcher.sh` is a separate read-only proxy — you authenticate to
*it*, not to TikTok. No developer account, no app review.

### What payment methods are supported?

Prepaid credits (`Authorization: Bearer bby_live_...`) or x402 micropayments
in USDC on Base, Polygon, Arbitrum, Monad, or Solana — see the [`fetcher`
skill](../../fetcher/SKILL.md) for setup.

### Is there a rate limit?

No fixed per-minute cap enforced by fetcher.sh itself — cost is the limiter:
each call is billed individually (credits or x402), so throughput is bounded
by your budget and by the upstream page latency, not by a quota.

## Search and discovery

### How do I find viral or trending posts for a keyword?

`GET /api/post/search?keyword=...&sortType=MOST_LIKED&dateRange=THIS_WEEK`
(or `THIS_MONTH`) on `tiktok.fetcher.sh`. See
[`scenarios.md`](scenarios.md).

### Can I filter search by video duration or resolution?

No — `/api/post/search` only exposes `sortType`, `dateRange`, and `region`.
There's no duration or resolution filter on this host; you'd have to filter
client-side using fields returned in the response.

### How do I look up a post if I only have the TikTok link, not the ID?

`GET /api/post?url=<the full tiktok.com URL>` — no need to parse the video ID
out of the URL yourself.

### How do I find all posts using a specific sound?

`GET /api/music/{id}/posts`, where `{id}` is the sound's numeric ID (visible
in the sound's TikTok URL).

## Profiles and followers

### How do I get a creator's follower list?

`GET /api/user/{id}/followers`, where `{id}` is the numeric ID from
`GET /api/user/handle/{username}`. Paginate with the returned `cursor` until
the response stops returning one.

### Can I export followers to CSV directly?

Not server-side. Fetcher.sh returns JSON; paginate through
`/api/user/{id}/followers` and write the pages to a CSV yourself. There's no
built-in export job.

### Can I get a user's liked posts?

No — there's no liked-posts endpoint on this host, only `/api/user/{id}/posts`
(what they posted). TikTok itself also hides most accounts' likes tab by
default, which is part of why it isn't exposed here.

## Comments

### How do I get comments on a video, including replies?

`GET /api/post/{id}/comments` for top-level comments, then
`GET /api/post/{id}/comments/{commentId}/replies` for the replies under a
specific comment.

## Monitoring and regional scope

### How do I monitor a hashtag for new posts?

There's no webhook or streaming endpoint. Poll `/api/hashtag/{id}/posts` (or
`/api/post/search` with `sortType=DATE_POSTED`) on a schedule and diff
against the post IDs you've already seen.

### Does `region` filter results to one country?

Where it's accepted (search, hashtag/music/location posts, user posts),
`region` is a 2-letter country code that scopes/localizes the underlying
TikTok request — it's optional everywhere it appears, not required.

## Discovery and reference

### Can an agent discover these endpoints without reading this file?

Yes — `tiktok.fetcher.sh/mcp` exposes `search_endpoints`, `describe_endpoint`,
and `fetch_data` as MCP tools, so an MCP-connected agent can explore the API
live instead of relying on this document.

### Where's the authoritative schema if this doc goes stale?

`https://tiktok.fetcher.sh/openapi.json` and `https://tiktok.fetcher.sh/llms.txt`
are generated from the live route handlers and always match production.

## See also

- [`endpoints.md`](endpoints.md) — full parameter reference
- [`scenarios.md`](scenarios.md) — worked `curl` examples
- [`comparison.md`](comparison.md) — fetcher.sh vs. the official TikTok API vs. a browser scraper
