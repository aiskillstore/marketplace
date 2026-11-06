---
name: booking-com-hotel-price-and-amenity-search-scraper
description: "Search Booking.com for a destination and dates, and collect each property's price, rating, review count, amenities, and breakfast info for the stay you specify. Output fields: name, price, pricePerNight, rating, reviewCount and more, as JSON rows. Use it for requests like \"Booking.com hotel prices for your dates\", \"hotel rate shopping\", \"Booking.com scraper\", or a CSV/JSON export of public Booking.com data."
---

# Booking.com Hotel Price & Amenity Search Scraper

Search Booking.com for a destination and dates, and collect each property's price, rating, review count, amenities, and breakfast info for the stay you specify.

- Actor: https://apify.com/nimbryxo-studio/booking-com-hotel-price-and-amenity-search-scraper (ID `nimbryxo-studio~booking-com-hotel-price-and-amenity-search-scraper`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/booking-com-hotel-price-and-amenity-search-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Compare hotel prices before your weekly check](https://www.youtube.com/shorts/jQWhZPI54SI)

## When to use

Use this skill when the user wants:

- Booking.com hotel prices for your dates
- hotel rate shopping
- Booking.com scraper
- a repeatable export of public Booking.com data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `name`: Hotel
- `price`: Stay total
- `pricePerNight`: Per night
- `currency`: Currency
- `rating`: Rating
- `reviewCount`: Reviews
- `reviewWord`: Score word
- `stars`: Stars
- `propertyType`: Type
- `city`: City
- `country`: Country
- `freeCancellation`: Free cancellation
- `breakfastIncluded`: Breakfast
- `topAmenities`: Top amenities
- `url`: URL

All 45 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | no | search | Search a destination, or load specific Booking.com hotel URLs. |
| `destination` | string | no |  | City, region or landmark to search, e.g. Paris, New York or Tokyo. Required in search mode. |
| `startUrls` | array | no | [] | Booking.com hotel page URLs, used in details mode. Copy links from a search result or your browser. |
| `checkIn` | string | no |  | Check-in date as YYYY-MM-DD. Leave empty to use tomorrow. |
| `checkOut` | string | no |  | Check-out date as YYYY-MM-DD. Leave empty to use a 3-night stay. |
| `adults` | integer | no | 2 | Number of adult guests. |
| `rooms` | integer | no | 1 | Number of rooms needed. |
| `propertyType` | string | no | all | Keep only one Booking.com property type, or search all types. |
| `minReviewScore` | number | no | 0 | Minimum guest score from 0 to 10. The actor applies Booking.com's score filter and then keeps only properties at or above this exact score. |
| `stars` | string | no | 0 | Keep only properties with this star rating, or any star rating. |
| `freeCancellation` | boolean | no | false | Return properties with at least one free-cancellation rate. |
| `breakfast` | boolean | no | false | Return properties with a breakfast-included rate. |
| `pool` | boolean | no | false | Return properties that have a swimming pool. |
| `minPrice` | number | no |  | Optional lower bound for the nightly price in the chosen currency. |

7 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "search",
  "destination": "Paris",
  "checkIn": "2026-12-01",
  "checkOut": "2026-12-03",
  "adults": 2,
  "rooms": 1,
  "currency": "USD",
  "maxItems": 20,
  "includeRooms": false
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 20, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~booking-com-hotel-price-and-amenity-search-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~booking-com-hotel-price-and-amenity-search-scraper/runs" \
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
