---
name: google-shopping-price-comparison-and-deal-finder
description: "Search Google Shopping by keyword and collect product prices, discounts, merchant names, ratings, and delivery info across 48 countries for price monitoring and deal tracking. Output fields: title, price, merchant, rating, reviewCount and more, as JSON rows. Use it for requests like \"Google Shopping price comparison\", \"price monitoring\", \"deal tracking\", or a CSV/JSON export of public Google Shopping data."
---

# Google Shopping Price Comparison & Deal Finder

Search Google Shopping by keyword and collect product prices, discounts, merchant names, ratings, and delivery info across 48 countries for price monitoring and deal tracking.

- Actor: https://apify.com/vexaloom-labs/google-shopping-price-comparison-and-deal-finder (ID `vexaloom-labs~google-shopping-price-comparison-and-deal-finder`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/google-shopping-price-comparison-and-deal-finder.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- Google Shopping price comparison
- price monitoring
- deal tracking
- a repeatable export of public Google Shopping data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Product
- `price`: Price
- `currency`: Currency
- `merchant`: Merchant
- `rating`: Rating
- `reviewCount`: Reviews

All 46 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | no | search | What to collect: keyword search, product lookup by ID/viewer URL, deals, or a department category. |
| `queries` | array | no |  | Product keywords for search/deals mode. Ignored in product mode; optional in category mode. |
| `productIds` | array | no |  | Google Shopping catalog IDs, product IDs, product viewer URLs, or legacy /shopping/product/ URLs. Used in product mode. |
| `category` | string | no |  | Google Shopping department for category mode. |
| `countryCode` | string | no | us | Country used for the Google domain, UULE location and price hint. The actual currency is always detected from the response, never relabelled. |
| `languageCode` | string | no | en | Interface and result language (hl parameter). |
| `sortBy` | string | no |  | Client-side sort of the collected rows. Google ignores server-side sort on this page. |
| `condition` | string | no |  | Condition hint sent to Google and verified when the result card shows a condition. |
| `minPrice` | integer | no |  | Minimum price in the detected local currency. Applied through a shoprs filter and verified on every output row. |
| `maxPrice` | integer | no |  | Maximum price in the detected local currency. Applied through a shoprs filter and verified on every output row. |
| `onSale` | boolean | no | false | Ask Google for discounted products and keep rows with an observed original price or discount. |
| `freeShipping` | boolean | no | false | Ask Google for free-shipping products and keep rows whose delivery text says free. |
| `minRating` | string | no | 0 | Minimum product rating (0-5). Applied through a shoprs rating chip and verified on every output row. |
| `store` | string | no |  | Optional store name to bias and verify, e.g. Best Buy or Amazon. |

3 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "search",
  "queries": [
    "wireless earbuds"
  ],
  "countryCode": "us",
  "maxResultsPerQuery": 25,
  "includePriceHistory": false
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxResultsPerQuery` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~google-shopping-price-comparison-and-deal-finder/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~google-shopping-price-comparison-and-deal-finder/runs" \
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
