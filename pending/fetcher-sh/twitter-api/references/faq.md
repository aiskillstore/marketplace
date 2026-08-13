---
name: twitter-api-faq
description: Frequently asked questions about the Twitter/X API on fetcher.sh — search, followers, monitoring, and rate limits, answered with exact endpoints.
---

# Twitter / X API alternative — FAQ

## Getting started

### Do I need a Twitter/X developer account or OAuth app?

No. `twitter.fetcher.sh` is a separate read-only proxy — you authenticate to
*it*, not to X. No developer account, no app review, no OAuth flow.

### What payment methods are supported?

Prepaid credits (`Authorization: Bearer bby_live_...`) or x402 micropayments
in USDC on Base, Polygon, Arbitrum, Monad, or Solana — see the [`fetcher`
skill](../../fetcher/SKILL.md) for setup.

### Is there a rate limit?

No fixed per-minute cap enforced by fetcher.sh itself — cost is the limiter:
each call is billed individually (credits or x402), so throughput is bounded
by your budget and by the upstream page latency, not by a quota.

## Search

### How do I search tweets by keyword?

`GET /api/search?query=...` on `twitter.fetcher.sh`. `query` accepts the same
advanced operators X's own search bar does (`from:`, `since:`, `min_faves:`,
`filter:`, etc.) — see [`scenarios.md`](scenarios.md).

### How do I search only a date range?

Add `since:YYYY-MM-DD` and `until:YYYY-MM-DD` to the `query` string — there's
no separate `startDate`/`endDate` param, it's all one search string.

### Can I filter search results to only tweets with media or links?

Yes, using X's own operators inside `query`: `filter:media` for tweets with
images/video, `filter:links` for tweets containing a URL. Combine with other
operators the same way you'd combine them in X's own search bar.

### Can I look up multiple tweets in one call?

No — `/api/tweet/{id}` takes one ID per request. There's no batch/bulk
lookup endpoint on this host; loop over IDs if you need several.

## Profiles, followers, and lists

### How do I get a user's follower list?

`GET /api/user/{id}/followers`, where `{id}` is the numeric ID from
`GET /api/handle/{handle}`. Paginate with the returned `cursor` until the
response stops returning one.

### Can I export followers to CSV directly?

Not server-side. Fetcher.sh returns JSON; paginate through
`/api/user/{id}/followers` and write the pages to a CSV yourself. There's no
built-in export job.

### How do I get a Twitter List's tweets or members?

`GET /api/list/{id}/tweets` and `GET /api/list/{id}/members`, where `{id}` is
the numeric list ID from a `x.com/i/lists/{id}` URL.

## Tweets and engagement

### What's the cheapest way to look up one specific tweet I already have the ID for?

`GET /api/tweet/{id}` — $0.002/call, the cheapest endpoint on this host.

### How do I get replies to a specific tweet, not the whole thread?

`GET /api/tweet/{id}/replies`. This returns the reply set for that tweet
specifically, separate from `/api/user/{id}/replies` (a user's own reply
activity across tweets).

### Can I get quote tweets for a given tweet?

There's no dedicated quote-tweets endpoint on this host — only
`/api/tweet/{id}/replies` (replies) and `/api/tweet/{id}/retweeters` (who
retweeted). If you need quote tweets specifically, that's a gap in the
current endpoint set, not something to work around with a different param.

## Monitoring and discovery

### How do I monitor a hashtag or account for new tweets?

There's no webhook or streaming endpoint. Poll `/api/search` (for a hashtag
or `from:` query) on a schedule — e.g. a cron job every few minutes — and
diff against the tweet IDs you've already seen.

### How do I find trending topics?

`GET /api/trends?country=United%20States`. `country` takes a full country
name, not an ISO code.

### Can an agent discover these endpoints without reading this file?

Yes — `twitter.fetcher.sh/mcp` exposes `search_endpoints`, `describe_endpoint`,
and `fetch_data` as MCP tools, so an MCP-connected agent can explore the API
live instead of relying on this document.

### Where's the authoritative schema if this doc goes stale?

`https://twitter.fetcher.sh/openapi.json` and `https://twitter.fetcher.sh/llms.txt`
are generated from the live route handlers and always match production.

## Naming

### Does `twitter-api` cover both "Twitter" and "X" branding?

Yes — this skill and its sibling [`x-api`](../../x-api/SKILL.md) hit
the exact same host and endpoints; `x-api` just leads with "X" wording so
agents searching either term find a match.

## See also

- [`endpoints.md`](endpoints.md) — full parameter reference
- [`scenarios.md`](scenarios.md) — worked `curl` examples
- [`comparison.md`](comparison.md) — fetcher.sh vs. the official X API vs. a browser scraper
