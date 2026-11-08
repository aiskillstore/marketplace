---
name: zillow-for-sale-rent-and-sold-listing-extractor
description: "Search Zillow by city, state or ZIP for active, rental or recently sold listings, with pricing, Zestimate, agent, school, tax and price history for each property. Output fields: address, price, soldPrice, beds, baths and more, as JSON rows. Use it for requests like \"Zillow for-sale, rental and sold listings\", \"Zillow scraper\", \"real estate comps\", or a CSV/JSON export of public Zillow data."
---

# Zillow For-Sale, Rent & Sold Listing Extractor

Search Zillow by city, state or ZIP for active, rental or recently sold listings, with pricing, Zestimate, agent, school, tax and price history for each property.

- Actor: https://apify.com/nimbryxo-studio/zillow-for-sale-rent-and-sold-listing-extractor (ID `nimbryxo-studio~zillow-for-sale-rent-and-sold-listing-extractor`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/zillow-for-sale-rent-and-sold-listing-extractor.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [The Listing Was Gone Before The Portal Email](https://www.youtube.com/shorts/bNjKOMdRlSY)

## When to use

Use this skill when the user wants:

- Zillow for-sale, rental and sold listings
- Zillow scraper
- real estate comps
- a repeatable export of public Zillow data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `address`: Address
- `price`: Price
- `soldPrice`: Sold Price
- `beds`: Beds
- `baths`: Baths
- `sqft`: Sqft
- `propertyType`: Type
- `status`: Status
- `daysOnZillow`: Days
- `url`: URL

All 58 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | BUY | Search active for-sale listings, rentals, or recently sold listings. |
| `search` | string | no |  | City, ZIP, neighborhood, county or state to search (for example 'Houston, TX' or '77002'). |
| `maxItems` | integer | no | 50 | Maximum number of records for the whole run across all sources (1-5000). |
| `endPage` | integer | no | 5 | Maximum search result pages per search task (1-24). Zillow returns up to 41 listings per page. |
| `startUrls` | array | no | [] | Property detail URLs, /apartments/ building URLs, or Zillow search page URLs. Search URLs keep their own filters and mode. |
| `zpids` | array | no |  | Zillow property IDs or URLs containing _zpid. Each ZPID is resolved to its canonical detail page. |
| `addresses` | array | no |  | Full street addresses to resolve to Zillow property pages, for example '1306 Castle Ct, Houston, TX 77006'. |
| `priceMin` | integer | no |  | Minimum listing price in US dollars. |
| `priceMax` | integer | no |  | Maximum listing price in US dollars. |
| `bedsMin` | string | no | any | Minimum number of bedrooms. |
| `bathsMin` | string | no | any | Minimum number of bathrooms. |
| `sqftMin` | integer | no |  | Minimum living area in square feet. |
| `sqftMax` | integer | no |  | Maximum living area in square feet. |
| `lotSizeMin` | string | no | any | Minimum lot size in square feet. |

19 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "BUY",
  "search": "Austin, TX",
  "maxItems": 25,
  "scrapeDetails": true,
  "daysOnZillow": "7",
  "sortBy": "newest"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~zillow-for-sale-rent-and-sold-listing-extractor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~zillow-for-sale-rent-and-sold-listing-extractor/runs" \
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
