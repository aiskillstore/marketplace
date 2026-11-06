---
name: airbnb-listing-price-and-location-finder
description: "Search Airbnb by location and stay dates for listing price, rating, Superhost and verification status, GPS coordinates, and photos per property. Output fields: name, nightlyPrice, totalPrice, rating, reviewCount and more, as JSON rows. Use it for requests like \"Airbnb price scraper\", \"short-term rental comps\", \"Airbnb listings by city\", or a CSV/JSON export of public Airbnb data."
---

# Airbnb Listing Price & Location Finder

Search Airbnb by location and stay dates for listing price, rating, Superhost and verification status, GPS coordinates, and photos per property.

- Actor: https://apify.com/nimbryxo-studio/airbnb-listing-price-and-location-finder (ID `nimbryxo-studio~airbnb-listing-price-and-location-finder`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/airbnb-listing-price-and-location-finder.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Price the market, not the gut](https://www.youtube.com/shorts/aVEDRMB3vsU)

## When to use

Use this skill when the user wants:

- Airbnb price scraper
- short-term rental comps
- Airbnb listings by city
- a repeatable export of public Airbnb data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `name`: Name
- `nightlyPrice`: Nightly price
- `totalPrice`: Stay total
- `currency`: Currency
- `rating`: Rating
- `reviewCount`: Reviews
- `location`: Location
- `roomType`: Room type
- `url`: URL

All 30 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | no | search | Search discovers listings by location or map area. Details loads the listing URLs or IDs you provide. |
| `location` | string | no |  | City, region, country or neighborhood, e.g. New York, Paris, SoHo. Airbnb's own location lookup validates the name before searching (mode=search). |
| `placeId` | string | no |  | Optional Google/Airbnb place ID (e.g. ChIJOwg_06VPwokRYv534QaPC8g). Takes precedence over the resolved location and skips text matching (mode=search). |
| `neighborhood` | string | no |  | Optional neighborhood to combine with Location, e.g. SoHo + New York (mode=search). |
| `bbox` | object | no |  | Search inside a map rectangle instead of a named location. Use decimal degrees: swLat, swLng (south-west corner) and neLat, neLng (north-east corner), plus an optional zoom… |
| `listingUrls` | array | no |  | Airbnb room URLs, e.g. `https://www.airbnb.com/rooms/23222680` (mode=details). |
| `listingIds` | array | no |  | Numeric Airbnb listing IDs, e.g. 23222680. You can mix these with listing URLs (mode=details). |
| `checkIn` | string | no |  | Stay start date in YYYY-MM-DD format. Leave both dates empty to use Airbnb's displayed quote (search) or to skip the price quote (details). |
| `checkOut` | string | no |  | Stay end date in YYYY-MM-DD format. Must be after the check-in date. |
| `adults` | integer | no | 1 | Number of adult guests (1-16). |
| `children` | integer | no | 0 | Number of children aged 2-12 (0-15). |
| `infants` | integer | no | 0 | Number of infants under 2 (0-5). |
| `pets` | integer | no | 0 | Number of pets (0-5). |
| `minPrice` | integer | no | 0 | Lowest nightly price to include, in the selected currency. 0 means no minimum. |

15 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "search",
  "location": "Miami, FL",
  "checkIn": "2026-12-01",
  "checkOut": "2026-12-03",
  "adults": 2,
  "maxListings": 20
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxListings` = 20, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~airbnb-listing-price-and-location-finder/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~airbnb-listing-price-and-location-finder/runs" \
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
