---
name: amazon-customer-review-and-rating-summary-scraper
description: "Get Amazon customer reviews and a product-level rating summary by product URL, keyword, or category, with star-rating and sort filters, across 23 Amazon domains. Output fields: productAsin, ratingScore, reviewTitle, reviewDescription, isVerified and more, as JSON rows. Use it for requests like \"Amazon review scraper\", \"Amazon rating summary\", \"product review export\", or a CSV/JSON export of public Amazon data."
---

# Amazon Customer Review & Rating Summary Scraper

Get Amazon customer reviews and a product-level rating summary by product URL, keyword, or category, with star-rating and sort filters, across 23 Amazon domains.

- Actor: https://apify.com/vexaloom-labs/amazon-customer-review-and-rating-summary-scraper (ID `vexaloom-labs~amazon-customer-review-and-rating-summary-scraper`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/amazon-customer-review-and-rating-summary-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Stop copying Amazon reviews; sort them in a sheet](https://www.youtube.com/shorts/WhVOks5q4MU)

## When to use

Use this skill when the user wants:

- Amazon review scraper
- Amazon rating summary
- product review export
- a repeatable export of public Amazon data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `productAsin`: ASIN
- `ratingScore`: Rating
- `reviewTitle`: Title
- `reviewDescription`: Review Description
- `isVerified`: Verified
- `reviewedIn`: Reviewed In
- `reviewReaction`: Review Reaction
- `variant`: Variant
- `reviewImages`: Review Images
- `reviewId`: Review ID
- `helpfulCount`: Helpful
- `reviewDate`: Date
- `reviewLocation`: Location
- `sentimentHint`: Sentiment
- `wordCount`: Words
- `hasImages`: Has Images
- `imageCount`: Image Count
- `reviewUrl`: Review URL
- `isVineVoice`: Vine
- `reviewVideos`: Review Videos

All 28 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `productUrls` | array | no |  | Amazon product URLs (/dp/, /gp/product/, /gp/aw/d/, /product/) or bare 10-character ASINs, on any supported Amazon domain. |
| `keywords` | array | no | [] | Search terms used to discover products when `productUrls` is empty (e.g. "wireless earbuds"). Each keyword contributes up to `maxProductsToDiscover` products. |
| `categoryUrls` | array | no | [] | Advanced discovery: Amazon `/s?...` search URLs or `/b?node=...` category URLs. Used only when `productUrls` is empty. |
| `maxProductsToDiscover` | integer | no | 5 | Maximum products discovered from each keyword or category URL (1-50). Ignored when `productUrls` is supplied. |
| `country` | string | no | amazon.com | Amazon storefront to use for bare ASINs, discovery, and products whose URL does not carry a domain. Product URLs keep their own domain. |
| `maxReviews` | integer | no | 100 | Hard cap per product after merging and deduplication (1-2000). The product-page sample alone yields about 8-13 rows; the optional extended feed can add 100-800+ for popular US… |
| `extendedHistory` | boolean | no | true | Merge Amazon's public extended review feed for each ASIN (no login): up to 100 rows per star/sort bucket, typically 100-800+ unique reviews for popular US products, deduplicated… |
| `mergeMarketplaces` | array | no | [] | Fetch the same product on these additional Amazon marketplaces and merge their deduplicated product-page reviews. Empty = the product's own marketplace only. |
| `sortBy` | string | no | helpful | Order of the returned reviews: most helpful first, or most recent first. |
| `filterByStar` | string | no |  | Keep only reviews with this rating. `positive` keeps 4-5 stars and `critical` keeps 1-2 stars. Applied after merging, so narrow filters can legitimately return few or no rows. |
| `verifiedPurchasesOnly` | boolean | no | false | Keep only reviews carrying Amazon's Verified Purchase badge. Applied server-side in the extended feed (and cookie mode) and client-side for product-page rows. |
| `filterKeywords` | array | no | [] | Keep only reviews whose title or text contains at least one of these keywords (case-insensitive). Empty = no keyword filter. |
| `reviewsNewerThan` | string | no |  | Keep only reviews dated on or after this date (YYYY-MM-DD or any ISO date). Reviews whose localized date cannot be parsed are kept. Empty = no date filter. |
| `mediaReviewsOnly` | boolean | no | false | Keep only reviews that include at least one reviewer-uploaded image or video. |

4 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "keywords": [
    "wireless earbuds"
  ],
  "country": "amazon.com",
  "maxProductsToDiscover": 2,
  "maxReviews": 20,
  "includeAggregates": true
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxProductsToDiscover` = 2, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~amazon-customer-review-and-rating-summary-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~amazon-customer-review-and-rating-summary-scraper/runs" \
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
