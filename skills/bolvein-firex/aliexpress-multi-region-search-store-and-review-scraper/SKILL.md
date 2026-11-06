---
name: aliexpress-multi-region-search-store-and-review-scraper
description: "Search AliExpress or fetch product, store, and review records by ID or URL across 18 regional storefronts and 42 currencies, with price, rating, and ship-from/ship-to filters. Output fields: title, salePrice, originalPrice, discountPercent, rating and more, as JSON rows. Use it for requests like \"AliExpress product search export\", \"AliExpress scraper\", \"dropshipping product research\", or a CSV/JSON export of public AliExpress data."
---

# AliExpress Multi-Region Search, Store & Review Scraper

Search AliExpress or fetch product, store, and review records by ID or URL across 18 regional storefronts and 42 currencies, with price, rating, and ship-from/ship-to filters.

- Actor: https://apify.com/vexaloom-labs/aliexpress-multi-region-search-store-and-review (ID `vexaloom-labs~aliexpress-multi-region-search-store-and-review`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/aliexpress-multi-region-search-store-and-review-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Spot repeat complaints in competitor reviews](https://www.youtube.com/shorts/lY2MQAk6oJA)

## When to use

Use this skill when the user wants:

- AliExpress product search export
- AliExpress scraper
- dropshipping product research
- a repeatable export of public AliExpress data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `productId`: Product Id
- `salePrice`: Sale Price
- `originalPrice`: Original Price
- `currencyCode`: Currency Code
- `discountPercent`: Discount Percent
- `rating`: Rating
- `ordersCount`: Orders Count
- `shipFromCountry`: Ship From Country
- `productUrl`: Product Url
- `isSponsored`: Is Sponsored

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | search | What to collect. search: keyword results. byProduct: product lookup by ID or URL. byStore: store lookup. byReviews: customer reviews. |
| `searchQueries` | array | no |  | One or more keywords, e.g. "phone case" or "wireless earbuds". Each query is scraped up to maxPages pages. |
| `productIds` | array | no |  | Numeric AliExpress product IDs or item URLs. Both 1005… and 3256… ID formats are accepted. |
| `storeIds` | array | no |  | Numeric store IDs or /store/… URLs. |
| `urls` | array | no |  | Any mix of search, item, store and review URLs. The mode is detected per URL. |
| `region` | string | no | US | Country used for prices, availability and the storefront locale. Global leaves the region to the requesting IP. |
| `currency` | string | no |  | Optional ISO-4217 currency. Leave blank to use the region's usual currency. The currency actually returned is recorded in every record. |
| `language` | string | no | en_US | Storefront language and the language used to translate review text. |
| `sortBy` | string | no | default | How keyword results are ordered. AliExpress does not expose a newest sort. |
| `priceMin` | number | no | 0 | Minimum price in the selected currency. 0 disables the lower bound. |
| `priceMax` | number | no | 0 | Maximum price in the selected currency. 0 disables the upper bound. |
| `ratingMin` | number | no | 0 | Minimum star rating from 0 to 5. Products without a rating are skipped when a threshold is set. |
| `shipFrom` | string | no |  | Only show items stocked in this country. Leave blank for any warehouse. |
| `freeShippingOnly` | boolean | no | false | Only show items advertised with free shipping. |

10 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "search",
  "searchQueries": [
    "phone case"
  ],
  "region": "US",
  "maxItems": 25,
  "maxPages": 1
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~aliexpress-multi-region-search-store-and-review/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~aliexpress-multi-region-search-store-and-review/runs" \
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
