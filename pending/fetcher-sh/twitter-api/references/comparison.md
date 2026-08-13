---
name: twitter-api-comparison
description: How fetcher.sh's Twitter/X endpoints compare to the official X API and a self-hosted headless-browser scraper, qualitative and scoped to what each actually does.
---

# Twitter / X data access — comparing your options

Three ways to get X data programmatically. This is a qualitative comparison
of access models, not a pricing sheet — treat any specific competitor price
you see elsewhere as something to verify yourself, not something repeated
here.

## Official X API

- Requires a developer account, app review, and OAuth 2.0 or OAuth 1.0a
  credentials before your first call.
- Sold in fixed monthly tiers with a pre-allocated post/read cap, not
  pay-as-you-go — you pay for the tier whether you use it or not.
- Endpoint coverage and field availability vary by tier; some fields
  (e.g. full-archive search) are gated to the highest tiers.
- Best fit when you're building a product that needs guaranteed uptime SLAs,
  X's own ToS-sanctioned access, and predictable monthly billing.

## Headless-browser scraper (self-hosted)

- No API key at all — you drive a real browser (Playwright/Puppeteer) against
  x.com and parse the DOM or intercepted XHR responses yourself.
- You own and pay for the infrastructure (proxies, browser fleet, CAPTCHA
  handling, session/cookie rotation) and you own the maintenance burden when
  X changes its frontend.
- No fixed per-call price — cost is your compute + proxy bill, which scales
  with volume and gets more expensive as anti-bot defenses tighten.
- Best fit when you need something the same subdomain-per-service model
  doesn't expose yet, or you're already running scraping infra for other
  sites and want one more target.

## fetcher.sh (`twitter.fetcher.sh`)

- No developer account, no OAuth, no app review — authenticate to
  `twitter.fetcher.sh` itself with a Bearer key or an x402 payment.
- Pay per call: $0.002–$0.005/request depending on endpoint (see
  [`endpoints.md`](endpoints.md)), no monthly minimum, no tier to outgrow.
- Fixed endpoint set (search, profiles, tweets, timelines, followers, lists,
  trends) mirrored across 11 services with the same JSON envelope and the
  same MCP tool names — one integration pattern reused everywhere.
- Read-only, on-demand: no webhooks, no streaming, no writes/posting. If you
  need "notify me when X happens," you poll on a schedule yourself.
- Best fit when you want ad-hoc or moderate-volume reads without upfront
  account setup, and you're fine treating X as one of several data sources
  behind the same MCP/REST pattern.

## Named providers to benchmark against

Don't take any provider's framing (including this one) at face value — pull
the same data from each and compare the actual response. A few concrete
starting points, current as of this writing (verify pricing and limits
yourself before deciding, since all three change their terms independently
of this repo):

| Provider | Docs | What to check |
| --- | --- | --- |
| Official X API | [docs.x.com/x-api/overview](https://docs.x.com/x-api/overview) | Does your required field or date range need first-party access? |
| Apify Tweet Scraper | [apify.com/apidojo/tweet-scraper](https://apify.com/apidojo/tweet-scraper) | Does an Actor-based, dataset/export-oriented workflow fit your pipeline better than direct REST? |
| Bright Data X (Twitter) Scraper API | [docs.brightdata.com/datasets/scrapers/twitter/introduction](https://docs.brightdata.com/datasets/scrapers/twitter/introduction) | Do you need bulk async collection (1000s of URLs) more than single-call reads? |

## Build your own comparison

Pick one fixed test — the same handle, the same search query, the same
tweet ID — and run it against fetcher.sh and whichever provider above is a
candidate. Record, per provider:

- Which required fields actually came back (not just which fields the docs
  promise)
- Cost for the exact rows you kept, after discarding anything you didn't need
- Time from request to usable JSON
- What happens on the second and third call — does pagination stay stable,
  does a cached/rate-limited path kick in, does the price change

A five-minute test like this is worth more than any comparison table,
including this one.

## Quick decision guide

| Need | Pick |
| --- | --- |
| Building a product needing an official ToS-covered integration with SLAs | Official X API |
| One-off script, no account setup, pay only for what you call | fetcher.sh |
| Already running scraping infra, need something fetcher.sh doesn't expose | Headless browser |
| Same integration pattern across X, TikTok, Instagram, Reddit, etc. | fetcher.sh |

## See also

- [`endpoints.md`](endpoints.md) — full parameter reference
- [`scenarios.md`](scenarios.md) — worked `curl` examples
- [`faq.md`](faq.md) — task-oriented "how do I..." answers
