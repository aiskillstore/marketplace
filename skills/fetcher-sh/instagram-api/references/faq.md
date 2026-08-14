---
name: instagram-api-faq
description: Frequently asked questions about the Instagram API on fetcher.sh — profiles, hashtags, followers, and monitoring, answered with exact endpoints.
---

# Instagram API alternative — FAQ

## Getting started

### Do I need an Instagram/Meta developer account or app review?

No. `instagram.fetcher.sh` is a separate read-only proxy — you authenticate
to *it*, not to Meta. No developer account, no app review, no Graph API
permissions to request.

### What payment methods are supported?

Prepaid credits (`Authorization: Bearer bby_live_...`) or x402 micropayments
in USDC on Base, Polygon, Arbitrum, Monad, or Solana — see the [`fetcher`
skill](../../fetcher/SKILL.md) for setup.

### Is there a rate limit?

No fixed per-minute cap enforced by fetcher.sh itself — cost is the limiter:
each call is billed individually (credits or x402), so throughput is bounded
by your budget and by the upstream page latency, not by a quota.

### Can I access a private account's posts?

No. Every endpoint here reflects what's publicly visible on the platform —
if an account or post isn't public, fetcher.sh can't see it either. There's
no login or session step that would grant private-account access.

## Profiles

### How do I look up a profile by @handle?

`GET /api/user/handle/{handle}` on `instagram.fetcher.sh` — this is the hero
endpoint and returns the full profile in one call. See
[`scenarios.md`](scenarios.md).

### How do I get just the numeric user ID for a handle?

`GET /api/userid/{handle}` — lighter-weight than the full profile lookup,
useful when the only thing you need next is the ID for a
`/api/user/{id}/...` call.

### How do I get a user's follower list?

`GET /api/user/{id}/followers`, where `{id}` is the numeric ID from either
profile lookup above. Paginate with the returned `cursor` until the response
stops returning one.

### Can I export followers to CSV directly?

Not server-side. Fetcher.sh returns JSON; paginate through
`/api/user/{id}/followers` and write the pages to a CSV yourself. There's no
built-in export job.

## Posts, reels, and stories

### How do I look up a post if I only have the Instagram link?

`GET /api/post/code/{code}`, where `{code}` is the shortcode segment from
`instagram.com/p/{code}/` — no numeric ID needed.

### Can I get a user's Stories archive/history?

No — `/api/user/{id}/stories` returns whatever is currently active on the
account, matching what Instagram itself exposes. There's no historical
stories endpoint.

### How do I distinguish a user's own posts from posts they're tagged in?

`/api/user/{id}/posts` is what they posted; `/api/user/{id}/posts/tagged` is
what other accounts posted and tagged them in.

### Does fetcher.sh host or download the actual media files?

No — responses return whatever metadata (including any media URLs) the
underlying page exposes; fetcher.sh doesn't host, re-encode, or proxy the
media itself. Treat any media URL in a response as pointing back to
Instagram's own infrastructure, not fetcher.sh's.

## Hashtags, audio, and locations

### How do I monitor a hashtag or location for new posts?

There's no webhook or streaming endpoint. Poll `/api/hashtag/{name}/posts`
or `/api/location/{id}/posts` on a schedule and diff against the post IDs
you've already seen — see the
[hashtag/location monitoring task guide](../../../task-guides/instagram-hashtag-and-location-monitoring.md).

### How do I find posts using a specific audio track?

`GET /api/audio/{id}/posts`, where `{id}` is the audio track's numeric ID
(visible in the track's Instagram URL).

## Discovery and reference

### Can an agent discover these endpoints without reading this file?

Yes — `instagram.fetcher.sh/mcp` exposes `search_endpoints`,
`describe_endpoint`, and `fetch_data` as MCP tools, so an MCP-connected agent
can explore the API live instead of relying on this document.

### Where's the authoritative schema if this doc goes stale?

`https://instagram.fetcher.sh/openapi.json` and
`https://instagram.fetcher.sh/llms.txt` are generated from the live route
handlers and always match production.

## See also

- [`endpoints.md`](endpoints.md) — full parameter reference
- [`scenarios.md`](scenarios.md) — worked `curl` examples
- [`comparison.md`](comparison.md) — fetcher.sh vs. the official Instagram Graph API vs. a browser scraper
