---
name: facebook-marketplace-listing-and-price-extractor
description: "Extract public Facebook Marketplace listings by city feed, category, keyword search, or direct item URL, with price, location, photos, delivery method, seller, and listing status per item. Output fields: title, price, city, state, locationText and more, as JSON rows. Use it for requests like \"Facebook Marketplace scraper\", \"Marketplace listings by city\", \"used item prices\", or a CSV/JSON export of public Facebook Marketplace data."
---

# Facebook Marketplace Listing & Price Extractor

Extract public Facebook Marketplace listings by city feed, category, keyword search, or direct item URL, with price, location, photos, delivery method, seller, and listing status per item.

- Actor: https://apify.com/nimbryxo-studio/facebook-marketplace-listing-and-price-extractor (ID `nimbryxo-studio~facebook-marketplace-listing-and-price-extractor`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/facebook-marketplace-listing-and-price-extractor.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- Facebook Marketplace scraper
- Marketplace listings by city
- used item prices
- a repeatable export of public Facebook Marketplace data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `price`: Price
- `city`: City
- `state`: State
- `locationText`: Location
- `condition`: Condition
- `deliveryTypes`: Delivery
- `seller`: Seller
- `primaryPhotoUrl`: Photo
- `listingUrl`: Listing URL

All 75 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | no | auto | What to scrape. auto uses startUrls when present and otherwise builds a keyword search. search builds a search from searchQueries plus location. |
| `startUrls` | array | no | [] | Marketplace search, city-category, global-category, city-feed, or /marketplace/item/ URLs. In mode=items, a bare numeric listing ID is also accepted. |
| `searchQueries` | array | no | [] | One to 20 keywords or phrases (mode=search or mode=auto without URLs). Each query becomes one source. |
| `location` | string | no |  | Marketplace location slug, city, postal code, or address used by keyword search (mode=search or mode=auto without URLs). Examples: nyc, Austin, Texas, 90210, London. |
| `country` | string | no | US | ISO 3166-1 alpha-2 country used when resolving a human location. Use GB for London, CA for Toronto, and so on. |
| `latitude` | number | no |  | Optional search center latitude. Provide longitude too. |
| `longitude` | number | no |  | Optional search center longitude. Provide latitude too. |
| `radiusKm` | integer | no | 65 | Search radius in kilometres for keyword or category search. URL mode keeps the radius in the URL unless you set this explicitly. |
| `category` | string | no | all | Marketplace category. If searchQueries is empty, the actor opens the city category feed (or the global category feed for a human location). |
| `categoryId` | string | no |  | Advanced numeric Facebook category ID. Takes precedence over category when set. |
| `sortBy` | string | no | relevance | Server-side sort where Marketplace supports it, plus a client-side re-sort by price or posting time. Rows without a price sort last. |
| `minPrice` | number | no |  | Only listings at or above this price. Rows without a price are dropped. |
| `maxPrice` | number | no |  | Only listings at or below this price. Rows without a price are dropped. |
| `condition` | string | no | any | Server-side condition filter in search/category modes. In deep mode the detail condition is checked too; fast URL rows without condition data are kept. |

13 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "search",
  "searchQueries": [
    "office chair"
  ],
  "location": "Austin, Texas",
  "maxItems": 25
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~facebook-marketplace-listing-and-price-extractor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~facebook-marketplace-listing-and-price-extractor/runs" \
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
