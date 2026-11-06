---
name: google-maps-grid-based-market-saturation-scanner
description: "Cover a bounding box, circle, or custom polygon with a search grid to collect every business Google Maps exposes for a query, well beyond the usual 120-result cap on a single search. Output fields: name, categoryName, totalScore, reviewsCount, phone and more, as JSON rows. Use it for requests like \"Google Maps search beyond 120 results\", \"Google Maps grid search\", \"local market saturation\", or a CSV/JSON export of public Google Maps data."
---

# Google Maps Grid-Based Market Saturation Scanner

Cover a bounding box, circle, or custom polygon with a search grid to collect every business Google Maps exposes for a query, well beyond the usual 120-result cap on a single search.

- Actor: https://apify.com/dataspryva/google-maps-grid-based-market-saturation-scanner (ID `dataspryva~google-maps-grid-based-market-saturation-scanner`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/google-maps-grid-based-market-saturation-scanner.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Map HVAC competitors block by block](https://www.youtube.com/shorts/uom3-Fy_xFk)

## When to use

Use this skill when the user wants:

- Google Maps search beyond 120 results
- Google Maps grid search
- local market saturation
- a repeatable export of public Google Maps data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `name`: Name
- `categoryName`: Category
- `totalScore`: Rating
- `reviewsCount`: Reviews
- `address`: Address
- `phone`: Phone
- `website`: Website
- `placeId`: Place Id
- `featureId`: Feature Id
- `kgmid`: Kgmid
- `googleMapsUrl`: Google Maps Url
- `location`: Location
- `rankInCell`: Rank In Cell

All 29 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `searchQuery` | string | yes |  | Type of business to search for (e.g., 'pharmacy', 'restaurant', 'dentist'). |
| `locationName` | string | no |  | Name of a public Google Maps location (e.g., 'Brooklyn, NY'). Google resolves its real center anonymously, then the actor scans the user-controlled radiusKm around it. |
| `boundingBox` | object | no |  | Geographic bounding box defining the scan area. Provide north/south/east/west coordinates. |
| `circleCenter` | object | no |  | Center point for a circular scan area. Use with radiusKm. |
| `radiusKm` | number | no | 5 | Radius in kilometers for circular scan area (used with circleCenter or locationName). |
| `customGeolocation` | object | no |  | Custom GeoJSON Polygon defining the scan boundary. |
| `zoomLevel` | integer | no | 15 | Controls grid cell granularity. Higher = smaller cells, more thorough coverage. |
| `maxPlacesPerCell` | integer | no | 120 | Maximum businesses to collect from each grid cell (1–260; Google's ranked window for one cell reaches roughly 136–213 places). |
| `maxPagesPerCell` | integer | no | 13 | How many 20-result pages to read per cell. Deeper pages surface more businesses — page 1 finds about 20% of a cell's places, page 9 finds all of them. |
| `maxTotalResults` | integer | no | 10000 | Maximum total businesses to extract across all cells. Stops scanning when reached. |
| `deduplicateResults` | boolean | no | true | Remove duplicate businesses that appear in multiple adjacent grid cells. |
| `enrichDetails` | boolean | no | false | Open each place's page for extra fields (price level, Plus Code, photo sample, rating histogram, open/closed status). |
| `minRating` | number | no |  | Only include businesses with a rating at or above this value (1.0–5.0). Leave empty to include all. |
| `language` | string | no | en | Language for Google Maps interface and results. |

Example (`references/example-input.json`):

```json
{
  "searchQuery": "coffee shops",
  "locationName": "Denver, CO",
  "radiusKm": 2,
  "maxPlacesPerCell": 20,
  "maxTotalResults": 50
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxTotalResults` = 50, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~google-maps-grid-based-market-saturation-scanner/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~google-maps-grid-based-market-saturation-scanner/runs" \
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
