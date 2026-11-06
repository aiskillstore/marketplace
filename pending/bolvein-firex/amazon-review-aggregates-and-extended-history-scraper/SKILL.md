---
name: amazon-review-aggregates-and-extended-history-scraper
description: "Collect Amazon customer reviews and rating summaries by product URL, ASIN, or keyword across 19 marketplaces, with star-rating and sort filters, reviewer images, and an optional session for deeper review history. Output fields: productAsin, ratingScore, reviewTitle, reviewDescription, isVerified and more, as JSON rows. Use it for requests like \"Amazon reviews across marketplaces\", \"Amazon review history\", \"reviews by ASIN\", or a CSV/JSON export of public Amazon data."
---

# Amazon Review Aggregates & Extended History Scraper

Collect Amazon customer reviews and rating summaries by product URL, ASIN, or keyword across 19 marketplaces, with star-rating and sort filters, reviewer images, and an optional session for deeper review history.

- Actor: https://apify.com/dataspryva/amazon-review-aggregates-and-extended-history (ID `dataspryva~amazon-review-aggregates-and-extended-history`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/amazon-review-aggregates-and-extended-history-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- Amazon reviews across marketplaces
- Amazon review history
- reviews by ASIN
- a repeatable export of public Amazon data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `productAsin`: ASIN
- `reviewedProductAsin`: Reviewed Product Asin
- `ratingScore`: Rating
- `reviewTitle`: Title
- `reviewDescription`: Review Description
- `isVerified`: Verified
- `isVineVoice`: Is Vine Voice
- `reviewedIn`: Reviewed In
- `reviewReaction`: Review Reaction
- `variant`: Variant
- `reviewImages`: Review Images
- `reviewId`: Review ID
- `reviewUrl`: Review Url
- `helpfulCount`: Helpful
- `reviewDate`: Date
- `reviewLocation`: Location
- `sentimentHint`: Sentiment
- `wordCount`: Words
- `hasImages`: Has Images
- `imageCount`: Image Count

All 28 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `productUrls` | array | no |  | List of Amazon product URLs to scrape reviews from. Supports /dp/, /gp/product/, /gp/aw/d/ and /product/ URL formats across 19+ Amazon domains. A bare 10-character ASIN (e.g. |
| `keywords` | array | no | [] | Search keywords used to auto-discover products when `productUrls` is empty (e.g. "wireless earbuds"). |
| `categoryUrls` | array | no | [] | Advanced mode: supply your own Amazon `/s?...` or `/b?node=...` category/search URL(s) directly (used only when `productUrls` is empty). |
| `maxProductsToDiscover` | integer | no | 10 | Maximum number of products to discover per run from `keywords`/`categoryUrls`. Ignored when `productUrls` is supplied directly. |
| `extendedHistory` | boolean | no | true | Merge Amazon's public extended review feed for each ASIN (no login, no cookie): up to 100 reviews per star/sort bucket, and walking every bucket yields 100-850+ unique reviews for… |
| `mergeMarketplaces` | array | no | [] | Additional Amazon marketplaces whose product page is fetched for the same ASIN and whose reviews are merged (deduplicated by review ID and content). |
| `includeAggregates` | boolean | no | true | Emit one additional `amazon_review_aggregate` record per product with the product title, average rating, global ratings count, star histogram (plus derived per-star counts), and… |
| `country` | string | no | amazon.com | Amazon country domain to scrape from. URLs from a different domain are honored automatically. |
| `maxReviews` | integer | no | 100 | Hard cap on the number of reviews returned per product AFTER merging and deduplication (1-2000). |
| `sortBy` | string | no | helpful | How to sort the returned reviews: most helpful first, or most recent first. |
| `filterByStar` | string | no |  | Keep only reviews with this rating. `positive` keeps 4-5 star reviews; `critical` keeps 1-2 star reviews. |
| `verifiedPurchasesOnly` | boolean | no | false | Keep only reviews carrying Amazon's Verified Purchase badge. Applied server-side for the extended feed and client-side for product-page rows. |
| `filterKeywords` | array | no | [] | Keep only reviews whose title or text contains at least one of these keywords (case-insensitive). Empty = no keyword filter. |
| `reviewsNewerThan` | string | no |  | Keep only reviews dated on or after this date (e.g. 2026-01-15 or any ISO date). Reviews whose localized date cannot be parsed are kept. Empty = no date filter. |

3 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "productUrls": [
    "https://www.amazon.com/dp/B09X7MPX8L"
  ],
  "country": "amazon.com",
  "maxReviews": 30,
  "includeAggregates": true
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxProductsToDiscover` = 10, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~amazon-review-aggregates-and-extended-history/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~amazon-review-aggregates-and-extended-history/runs" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d @references/example-input.json)
RUN_ID=$(echo "$RUN" | jq -r '.data.id'); DATASET=$(echo "$RUN" | jq -r '.data.defaultDatasetId')
curl -s "https://api.apify.com/v2/actor-runs/$RUN_ID?waitForFinish=60" -H "Authorization: Bearer $APIFY_TOKEN" | jq -r '.data.status'
curl -s "https://api.apify.com/v2/datasets/$DATASET/items?format=json" -H "Authorization: Bearer $APIFY_TOKEN" > output.json
```

## Cost and limits

- Apify bills the Actor's usage on your account; the Actor's Pricing tab shows the current price.
- Keep the limit in the input small for a first run.

## Guardrails

- Public data only. Do not pass cookies, sessions or private account data.
- Do not use the output for spam, harassment or unlawful discrimination.
- Check the target site's terms and local law before running at scale.
