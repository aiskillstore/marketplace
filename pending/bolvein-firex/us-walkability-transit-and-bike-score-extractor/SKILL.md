---
name: us-walkability-transit-and-bike-score-extractor
description: "Looks up Walk Score, Transit Score, and Bike Score for any US city or street address, returning each 0-100 score with its rating label and nearby amenity categories. Output fields: address, city, walkScore, transitScore, bikeScore and more, as JSON rows. Use it for requests like \"Walk Score for a list of addresses\", \"walkability score lookup\", \"transit score\", or a CSV/JSON export of public Walk Score data."
---

# US Walkability, Transit & Bike Score Extractor

Looks up Walk Score, Transit Score, and Bike Score for any US city or street address, returning each 0-100 score with its rating label and nearby amenity categories.

- Actor: https://apify.com/dataspryva/us-walkability-transit-and-bike-score-extractor (ID `dataspryva~us-walkability-transit-and-bike-score-extractor`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/us-walkability-transit-and-bike-score-extractor.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Compare walk, transit, and bike scores by listing](https://www.youtube.com/shorts/yCT9c3LRopU)

## When to use

Use this skill when the user wants:

- Walk Score for a list of addresses
- walkability score lookup
- transit score
- a repeatable export of public Walk Score data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `address`: Address
- `locationType`: Location Type
- `city`: City
- `state`: State
- `zipCode`: Zip Code
- `walkScore`: Walk Score
- `walkDescription`: Walk Description
- `transitScore`: Transit Score
- `transitDescription`: Transit Description
- `bikeScore`: Bike Score
- `bikeDescription`: Bike Description
- `nearbyAmenities`: Nearby Amenities

All 13 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | byCity | What to look up. |
| `addresses` | array | no | [] | US street addresses, e.g. '1 Beach St, San Francisco, CA 94133'. walkscore.com/score/... URLs are also accepted. |
| `cities` | array | no | ["Seattle, WA"] | Cities as 'Seattle, WA', 'Seattle-WA', or a walkscore.com city URL. |
| `neighborhoods` | array | no | [] | Neighborhoods as 'Ballard, Seattle, WA' or a walkscore.com neighborhood URL. |
| `state` | string | no | WA | US state whose city table to read. |
| `includeNeighborhoods` | boolean | no | true | Add the city page's neighborhood ranking table to each city record. |
| `maxItems` | integer | no | 50 | Maximum records to emit (state summary counts as one). |

Example (`references/example-input.json`):

```json
{
  "mode": "byCity",
  "cities": [
    "Seattle, WA"
  ],
  "state": "WA",
  "includeNeighborhoods": true,
  "maxItems": 25
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~us-walkability-transit-and-bike-score-extractor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~us-walkability-transit-and-bike-score-extractor/runs" \
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
