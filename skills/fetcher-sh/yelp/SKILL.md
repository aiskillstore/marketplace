---
name: yelp
description: >-
  A Yelp API alternative on fetcher.sh — pay-per-call in USDC via x402, or
  prepaid credits with a Bearer key, no Yelp Fusion API app approval. Use
  when the user wants to search local businesses by query and location
  sorted by rating or review count, fetch a business's full details by ID or
  by its Yelp URL handle/slug, or fetch a business's reviews. Also covers
  local business discovery, restaurant/service research, review sentiment
  input, and competitor monitoring for local businesses without Yelp Fusion
  API's app-approval process and daily call caps.
keywords:
  - yelp
  - yelp-api
  - yelp-api-alternative
  - local-business-data
  - restaurant-data
  - business-review-api
  - x402
  - ai-agent
---

# Yelp API

Local business search, business details, and reviews as clean JSON — one
plain HTTP GET per call, paid as you go. No Yelp Fusion API app approval, no
daily call cap, no API key request form.

Base URL: `https://yelp.fetcher.sh`

## Authentication

Two ways to pay, same data — full mechanics in the [`fetcher`
skill](../fetcher/SKILL.md):

```bash
# 1. Prepaid credits (recommended — get a key at https://fetcher.sh/topup
#    or via POST /api/credits/topup, see the fetcher skill)
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/search?query=ramen&location=San+Francisco"

# 2. x402 pay-per-call — omit the header; a GET with no payment returns 402
#    with machine-readable payment requirements (USDC on Base, Polygon,
#    Arbitrum, Monad, or Solana). @x402/fetch signs and retries automatically.
```

Every response is `{ "status": number, "message": string, "data": ... }`; the
HTTP status mirrors `status`.

## Endpoints (4 — all GET, $0.003/call)

| Endpoint | What it returns |
| --- | --- |
| `/api/search` | Businesses matching a query and location |
| `/api/place/{id}` | A business's full details by ID |
| `/api/place/handle/{handle}` | A business's full details by its Yelp URL handle/slug |
| `/api/place/{id}/reviews` | A business's reviews |

Required on search: `query`, `location`. Optional: `sortBy` (`recommended`,
`rating`, `reviewCount`), `page`. Reviews support `page`.

## Scenarios

**Highest rated first:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=ramen" -G \
  --data-urlencode "location=San Francisco" \
  --data-urlencode "sortBy=rating" \
  "https://yelp.fetcher.sh/api/search"
```

**Most reviewed first:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=tacos" -G \
  --data-urlencode "location=Austin, TX" \
  --data-urlencode "sortBy=reviewCount" \
  "https://yelp.fetcher.sh/api/search"
```

**A business's details by ID, or by its Yelp URL handle/slug:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/place/gary-danko-san-francisco"

curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://yelp.fetcher.sh/api/place/handle/gary-danko-san-francisco"
```

**A business's reviews, paginated:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "page=2" -G \
  "https://yelp.fetcher.sh/api/place/gary-danko-san-francisco/reviews"
```

## MCP

```json
{
  "mcpServers": {
    "yelp": {
      "url": "https://yelp.fetcher.sh/mcp",
      "headers": { "Authorization": "Bearer bby_live_..." }
    }
  }
}
```

Free: `search_endpoints`, `describe_endpoint`, `check_balance`. Paid:
`fetch_data` (any endpoint above), `topup_credits`, plus the named shortcut
`yelp_search`. Drop the `headers` block to pay per call with x402 instead —
see the [`fetcher` skill](../fetcher/SKILL.md) for the full flow.

## Errors

- `400` — missing/invalid parameter (message names it)
- `401` — unknown or rotated key
- `402` — payment required (x402 challenge) or `topup_required` (credits
  exhausted)
- `404` — not a priced path
- No rate limits; no refunds on upstream failures (settlement precedes
  delivery)

## Reference

- Full agent setup: <https://yelp.fetcher.sh/skill.md>
- OpenAPI 3.1 contract: <https://yelp.fetcher.sh/openapi.json>
- Condensed catalog: <https://yelp.fetcher.sh/llms.txt>
- Payment, credits, and MCP deep dive: [`fetcher` skill](../fetcher/SKILL.md)
- Site: <https://yelp.fetcher.sh>
