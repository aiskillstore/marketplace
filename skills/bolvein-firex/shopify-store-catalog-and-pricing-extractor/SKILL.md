---
name: shopify-store-catalog-and-pricing-extractor
description: "Extract a Shopify store's product catalog with titles, prices, compare-at prices, variants, SKUs, images and stock availability from any custom or myshopify.com domain. Output fields: title, price, compareAtPrice, available, vendor and more, as JSON rows. Use it for requests like \"Scrape a Shopify store's products and prices\", \"Shopify product scraper\", \"competitor catalog export\", or a CSV/JSON export of public Shopify data."
---

# Shopify Store Catalog & Pricing Extractor

Extract a Shopify store's product catalog with titles, prices, compare-at prices, variants, SKUs, images and stock availability from any custom or myshopify.com domain.

- Actor: https://apify.com/nimbryxo-studio/shopify-store-catalog-and-pricing-extractor (ID `nimbryxo-studio~shopify-store-catalog-and-pricing-extractor`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/shopify-store-catalog-and-pricing-extractor.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [See competitor prices before Monday's meeting](https://www.youtube.com/shorts/398NV7q-K6w)

## When to use

Use this skill when the user wants:

- Scrape a Shopify store's products and prices
- Shopify product scraper
- competitor catalog export
- a repeatable export of public Shopify data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `price`: Price
- `currency`: Currency
- `compareAtPrice`: Compare at
- `available`: Available
- `vendor`: Vendor
- `productType`: Type
- `storeUrl`: Store
- `url`: Product URL

All 42 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | catalog | What to scrape. `catalog` walks the public product feed, `collection` walks specific collections, `product` fetches exact product handles, `search` uses the storefront search… |
| `storeUrls` | array | no |  | Store domains or URLs, e.g. `deathwishcoffee.com` or `https://www.allbirds.com`. Accepts custom domains and `*.myshopify.com`. |
| `startUrls` | array | no | [] | Store, collection or product URLs. In `auto` mode each URL selects its own job: `/products/` fetches one product, `/collections/` fetches a collection, any other store URL fetches… |
| `collectionHandles` | array | no | [] | Collection handles or collection URLs, e.g. `new-arrivals`, `sale`, or `https://store.com/collections/sale`. |
| `productHandles` | array | no | [] | Product handles or product URLs, e.g. `dark-roast-coffee` or `https://store.com/products/dark-roast-coffee`. |
| `searchQuery` | string | no |  | In-store search term. Shopify's public suggest endpoint returns at most 10 products per store and has no pagination. |
| `currency` | string | no | store | ISO 4217 code to pin prices to, e.g. `USD`, `EUR`, `GBP`. Use `store` to use the store's base currency from `/meta.json`. |
| `country` | string | no |  | Two-letter ISO country code passed as `?country=` to the storefront, e.g. `US`, `GB`, `DE`. |
| `vendor` | string | no |  | Keep products whose vendor contains this text (case-insensitive). |
| `productType` | string | no |  | Keep products whose product type contains this text (case-insensitive). |
| `tag` | string | no |  | Keep products with at least one tag containing this text (case-insensitive). |
| `minPrice` | number | no |  | Drop products whose lowest variant price is below this value. |
| `maxPrice` | number | no |  | Drop products whose lowest variant price is above this value. |
| `available` | string | no | any | Keep all products, only products with at least one purchasable variant, or only sold-out products. |

5 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "catalog",
  "storeUrls": [
    "https://deathwishcoffee.com"
  ],
  "maxItems": 50,
  "currency": "store",
  "available": "any",
  "includeDetails": false,
  "flattenVariants": false
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 50, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~shopify-store-catalog-and-pricing-extractor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~shopify-store-catalog-and-pricing-extractor/runs" \
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
