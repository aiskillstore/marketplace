---
name: tiktok-api-endpoints
description: Full parameter reference for every TikTok endpoint on tiktok.fetcher.sh — path params, query params, required flags, and enum values, straight from the live OpenAPI contract.
---

# TikTok — full endpoint reference

Base URL: `https://tiktok.fetcher.sh`. All 13 endpoints are `GET`,
authenticated with either `Authorization: Bearer bby_live_...` (credits) or
an x402 payment — see [`SKILL.md`](../SKILL.md) for the payment flow. Path
parameters are written as `{param}`; substitute the real value. `?` marks an
optional query param. Every endpoint on this host is a flat $0.004/call.

This file lists every parameter that exists. It does not describe response
fields — the response shape is generated at request time from the live
handlers, so the authoritative machine-readable version is always
[`/openapi.json`](https://tiktok.fetcher.sh/openapi.json). Treat any field
name you haven't seen in an actual response as unverified.

## Search

| Endpoint | Params |
| --- | --- |
| `/api/post/search` | `keyword` (required) · `cursor`? · `region`? · `sortType`? (`RELEVANCE`, `MOST_LIKED`, `DATE_POSTED`) · `dateRange`? (`ALL_TIME`, `YESTERDAY`, `THIS_WEEK`, `THIS_MONTH`, `LAST_THREE_MONTHS`, `LAST_SIX_MONTHS`) |

This is the hero endpoint — `sortType=MOST_LIKED` plus a `dateRange` is the
combination for a "what's viral" query; leave both unset for TikTok's default
relevance ranking.

## Profiles

| Endpoint | Params |
| --- | --- |
| `/api/user/handle/{username}` | none |

Returns the numeric user ID needed by every `/api/user/{id}/...` endpoint
below.

## Users

| Endpoint | Params |
| --- | --- |
| `/api/user/{id}/posts` | `region`? · `cursor`? |
| `/api/user/{id}/followers` | `cursor`? |
| `/api/user/{id}/followings` | `cursor`? |

`{id}` is the numeric ID from the handle lookup, not the `@username`.

## Posts

| Endpoint | Params |
| --- | --- |
| `/api/post` | `url` (required) |
| `/api/post/{id}` | `region`? |
| `/api/post/{id}/comments` | `cursor`? |
| `/api/post/{id}/comments/{commentId}/replies` | `cursor`? |

`/api/post` takes a full TikTok video URL directly — useful when you have a
link but not the numeric video ID. `/api/post/{id}` needs just the ID (the
number in the URL). `{commentId}` for replies comes from a comment object
returned by `/api/post/{id}/comments`.

## Hashtags, sounds, and locations

| Endpoint | Params |
| --- | --- |
| `/api/hashtag/handle/{name}` | none |
| `/api/hashtag/{id}/posts` | `region`? · `cursor`? |
| `/api/music/{id}/posts` | `region`? · `cursor`? |
| `/api/location/{locationId}/posts` | `cursor`? · `region`? |

`/api/hashtag/handle/{name}` resolves a hashtag name (no `#`) to the numeric
ID needed by `/api/hashtag/{id}/posts`. `region` on any endpoint is a 2-letter
country code (e.g. `US`) and filters/localizes results where TikTok supports
it — it's optional everywhere it appears.

## See also

- [`scenarios.md`](scenarios.md) — one worked `curl` per endpoint
- [`faq.md`](faq.md) — task-oriented "how do I..." answers
- [`comparison.md`](comparison.md) — fetcher.sh vs. the official TikTok API vs. a browser scraper
