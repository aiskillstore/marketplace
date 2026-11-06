---
name: amazon-multi-domain-product-price-and-detail-scraper
description: "Pull pricing, ratings, seller, variant and technical detail for Amazon products by URL or ASIN, across 21 country domains, with optional delivery postal-code targeting. Output fields: title, asin, price, stars, reviewsCount and more, as JSON rows. Use it for requests like \"Amazon price tracking\", \"Amazon product scraper\", \"ASIN price lookup\", or a CSV/JSON export of public Amazon data."
---

# Amazon Multi-Domain Product Price & Detail Scraper

Pull pricing, ratings, seller, variant and technical detail for Amazon products by URL or ASIN, across 21 country domains, with optional delivery postal-code targeting.

- Actor: https://apify.com/nimbryxo-studio/amazon-multi-domain-product-price-and-detail (ID `nimbryxo-studio~amazon-multi-domain-product-price-and-detail`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/amazon-multi-domain-product-price-and-detail-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [The buy box moved while you slept](https://www.youtube.com/shorts/SqsDoB0jyD8)

## When to use

Use this skill when the user wants:

- Amazon price tracking
- Amazon product scraper
- ASIN price lookup
- a repeatable export of public Amazon data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Product Title
- `asin`: ASIN
- `price`: Price
- `stars`: Rating
- `reviewsCount`: Reviews
- `inStock`: In Stock
- `brand`: Brand
- `url`: URL

All 9 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `productUrls` | array | no | [] | Amazon product URLs to scrape. Any mix of the 21 supported country domains is allowed, e.g. `https://www.amazon.com/dp/B0B8PD8TTP.` |
| `asins` | array | no | [] | Bare 10-character Amazon ASINs. Builds /dp/{ASIN} URLs on the selected marketplace, or on every domain listed in `domains` for cross-marketplace runs. |
| `searchTerms` | array | no | [] | Keyword queries to run on Amazon search pages. Price/rating/deal/condition/sort filters are applied as URL parameters. |
| `searchUrls` | array | no | [] | Full Amazon search URLs to pass through, including your own `i=`, `rh=`, `low-price`, and `s=` parameters. Pagination is added automatically. |
| `bestsellerUrls` | array | no | [] | Amazon bestseller /zgbs/ or /gp/bestsellers/ list URLs. Returns the ranked product cards, optionally enriched with product-detail fields. |
| `marketplace` | string | no | auto | Marketplace used for bare ASINs and keyword search terms. `auto` uses the first product URL's domain, or amazon.com. |
| `domains` | array | no | [] | Optional list of marketplaces (e.g. amazon.com, amazon.de) to run bare ASINs and search terms across. Leave empty to use `marketplace` only. |
| `language` | string | no | auto | Page language. `auto` uses the marketplace's own default. Explicit values set `?language=` and the matching Accept-Language header. |
| `currency` | string | no | auto | ISO currency for the displayed price. `auto` uses the marketplace currency. Note: Amazon converts display currency; it is not guaranteed local retail pricing. |
| `deliveryCountry` | string | no | auto | Optional country hint. When `postalCode` is empty, a representative local ZIP for that country is used. A country alone is not sent to Amazon. |
| `postalCode` | string | no |  | Local ZIP/postal code for the delivery location. The actor validates it against the marketplace format and skips the location change if it does not match. |
| `minPrice` | number | no |  | Minimum price for discovery (search) results. Leave empty for no lower bound. |
| `maxPrice` | number | no |  | Maximum price for discovery (search) results. Leave empty for no upper bound. |
| `minRating` | string | no | any | Minimum star rating for discovery results. `4` is the live-validated 4+ stars filter; lower values are best effort. |

17 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "searchTerms": [
    "wireless earbuds"
  ],
  "marketplace": "amazon.com",
  "maxItems": 25,
  "includeDetails": true,
  "dealsOnly": false
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~amazon-multi-domain-product-price-and-detail/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~amazon-multi-domain-product-price-and-detail/runs" \
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
