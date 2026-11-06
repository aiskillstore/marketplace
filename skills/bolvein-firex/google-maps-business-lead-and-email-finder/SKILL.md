---
name: google-maps-business-lead-and-email-finder
description: "Find business leads on Google Maps by category, keyword, or location and collect name, address, phone, website, rating, review count, and coordinates. Optionally adds emails and social links found on each business's own website. Output fields: name, googleBusinessCategories, phoneNumber, email, reviewScore and more, as JSON rows. Use it for requests like \"Google Maps leads with emails\", \"Google Maps scraper\", \"local business leads\", or a CSV/JSON export of public Google Maps data."
---

# Google Maps Business Lead & Email Finder

Find business leads on Google Maps by category, keyword, or location and collect name, address, phone, website, rating, review count, and coordinates. Optionally adds emails and social links found on each business's own website.

- Actor: https://apify.com/dataspryva/google-maps-business-lead-and-email-finder (ID `dataspryva~google-maps-business-lead-and-email-finder`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/google-maps-business-lead-and-email-finder.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Watch the Short](https://www.youtube.com/shorts/ofD2844kDPQ)

## When to use

Use this skill when the user wants:

- Google Maps leads with emails
- Google Maps scraper
- local business leads
- a repeatable export of public Google Maps data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `name`: Business
- `googleBusinessCategories`: Categories
- `street`: Street
- `city`: City
- `state`: State / region
- `zip`: Postal code
- `country`: Country
- `countryCode`: Country code
- `phoneNumber`: Phone
- `url`: Website
- `email`: Email
- `emails`: Emails
- `reviewScore`: Rating
- `reviewsNumber`: Reviews
- `placeId`: Place ID
- `featureId`: Feature ID
- `googleMapsUrl`: Google Maps
- `priceLevel`: Price level
- `plusCode`: Plus Code
- `location`: Coordinates

All 39 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | no | searchPlaces | Search Google Maps, look up specific places, or enrich a list of websites you already have. |
| `searchQueries` | array | no |  | Natural-language searches such as 'coffee shops in Austin TX'. Include the place in each phrase, or use the location field below. |
| `locationQuery` | string | no |  | Adds a shared location to every search phrase, for example 'Austin, TX, USA'. Leave empty when your phrases already name the place. |
| `category` | string | no | bakery | Business category such as bakery, dentist or plumber. Used when keyword and search phrases are empty. |
| `keyword` | string | no |  | Custom search term such as 'boutique coffee' or 'pet grooming'. Takes priority over category. |
| `state` | string | no | All | US state for the search. Choose 'All' for nationwide. Ignored for non-US countries. |
| `country` | string | no | US | Country for the search. Other countries can be named directly in a search phrase. |
| `websites` | array | no |  | Websites to read for contact details, one per line. Bare domains such as example.com are accepted. |
| `placeUrls` | array | no |  | Google Maps place links copied from the address bar or a previous export. |
| `placeIds` | array | no |  | Canonical Google Place IDs starting with 'ChIJ'. |
| `max_results` | integer | no | 100 | Maximum number of leads to save. Google returns a ranked window of roughly 150-220 businesses per search phrase, so a larger request may end when that window ends. |
| `minRating` | number | no |  | Keep only businesses rated at least this value (1.0-5.0). Leave empty for any rating. |
| `extractEmails` | boolean | no | true | Visit each business website for public emails, phone numbers and social profiles. Turn off for a faster Maps-only run. |
| `maxEmailsPerWebsite` | integer | no | 5 | Maximum email addresses to keep for one business website. |

6 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "searchPlaces",
  "searchQueries": [
    "restaurants in New York, NY"
  ],
  "max_results": 20,
  "extractEmails": true,
  "onlySaveResults": "onlyWithContacts"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `max_results` = 20, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~google-maps-business-lead-and-email-finder/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~google-maps-business-lead-and-email-finder/runs" \
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
