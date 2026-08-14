---
name: instagram-api-endpoints
description: Full parameter reference for every Instagram endpoint on instagram.fetcher.sh — path params, query params, required flags, and enum values, straight from the live OpenAPI contract.
---

# Instagram — full endpoint reference

Base URL: `https://instagram.fetcher.sh`. All 16 endpoints are `GET`,
authenticated with either `Authorization: Bearer bby_live_...` (credits) or
an x402 payment — see [`SKILL.md`](../SKILL.md) for the payment flow. Path
parameters are written as `{param}`; substitute the real value. `?` marks an
optional query param. Every endpoint on this host is a flat $0.004/call.

This file lists every parameter that exists. It does not describe response
fields — the response shape is generated at request time from the live
handlers, so the authoritative machine-readable version is always
[`/openapi.json`](https://instagram.fetcher.sh/openapi.json). Treat any field
name you haven't seen in an actual response as unverified.

## Profiles

| Endpoint | Params |
| --- | --- |
| `/api/user/handle/{handle}` | none |
| `/api/userid/{handle}` | none |
| `/api/user/{id}` | none |
| `/api/user/search` | `query` (required) · `cursor`? |

`/api/user/handle/{handle}` is the hero endpoint — it returns the full
profile in one call. `/api/userid/{handle}` is a lighter-weight lookup when
you only need the numeric ID, not the full profile, before calling one of the
`/api/user/{id}/...` endpoints below.

## User content

| Endpoint | Params |
| --- | --- |
| `/api/user/{id}/posts` | `cursor`? |
| `/api/user/{id}/posts/tagged` | `cursor`? |
| `/api/user/{id}/reels` | `cursor`? |
| `/api/user/{id}/stories` | none |
| `/api/user/{id}/followers` | `cursor`? |
| `/api/user/{id}/followings` | `cursor`? |

`{id}` is the numeric ID from either profile lookup above, not the `@handle`.
Stories return whatever is currently active on the account — there's no
archive/history param, since Instagram itself only exposes the live set.

## Posts

| Endpoint | Params |
| --- | --- |
| `/api/post/code/{code}` | none |
| `/api/post/{id}/comments` | `cursor`? |

`{code}` is the shortcode segment from a post URL
(`instagram.com/p/{code}/`) — use this when you have a link, not a numeric
post ID.

## Hashtags, audio, and locations

| Endpoint | Params |
| --- | --- |
| `/api/hashtag/{name}/posts` | `cursor`? · `page`? |
| `/api/hashtag/{name}/reels` | none |
| `/api/audio/{id}/posts` | `cursor`? |
| `/api/location/{id}/posts` | `tab`? · `cursor`? · `page`? |

`{name}` for hashtags is the tag text without the `#`. `tab` on the location
endpoint selects which content section to read (Instagram's own location
page tabbing) — leave unset for the default view.

## See also

- [`scenarios.md`](scenarios.md) — one worked `curl` per endpoint
- [`faq.md`](faq.md) — task-oriented "how do I..." answers
- [`comparison.md`](comparison.md) — fetcher.sh vs. the official Instagram Graph API vs. a browser scraper
