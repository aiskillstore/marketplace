---
name: google-trends-interest-and-related-query-scraper
description: "Get interest-over-time, interest-by-region, and related topics/queries for any keyword, location, time range and Google surface, with side-by-side comparison for up to five keywords. Output fields: searchTerms, title, geoName, averageInterest, growthPercent and more, as JSON rows. Use it for requests like \"Export Google Trends data\", \"Google Trends scraper\", \"related queries\", or a CSV/JSON export of public Google Trends data."
---

# Google Trends Interest & Related Query Scraper

Get interest-over-time, interest-by-region, and related topics/queries for any keyword, location, time range and Google surface, with side-by-side comparison for up to five keywords.

- Actor: https://apify.com/vexaloom-labs/google-trends-interest-and-related-query-scraper (ID `vexaloom-labs~google-trends-interest-and-related-query-scraper`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/google-trends-interest-and-related-query-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [See the demand curve before the keyword tool](https://www.youtube.com/shorts/gDZBpA25UB8)

## When to use

Use this skill when the user wants:

- Export Google Trends data
- Google Trends scraper
- related queries
- a repeatable export of public Google Trends data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `searchTerms`: Terms
- `title`: Trending term
- `geoName`: Location
- `timeRangeLabel`: Time label
- `hoursLabel`: Window
- `categoryName`: Category
- `searchTypeLabel`: Type label
- `averageInterest`: Avg
- `volumeText`: Volume
- `growthPercent`: Growth %
- `exploreUrl`: URL
- `trendingUrl`: Trends URL

All 36 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | no | interest | What to scrape. 'Interest over time & related queries' is the Google Trends Explore view (keywords required). 'Trending now' lists what is spiking in a country right now. |
| `searchTerms` | array | no |  | One or more search terms to analyze (mode=interest). Each term becomes its own dataset row, or enable Comparison mode to compare up to 5 terms side by side. |
| `compareMode` | boolean | no | false | Compare all search terms on one shared 0-100 scale in a single row (Google Trends comparison view, maximum 5 terms). Off means each term is scraped independently. |
| `startUrls` | array | no |  | Paste Google Trends links to scrape them directly: explore links (trends.google.com/trends/explore?q=..., including www.google.com/trends/... |
| `geo` | string | no |  | Country, state/region or metro area to analyze. Leave empty for worldwide. Trending Now uses the country part of this location. |
| `timeRange` | string | no | today 12-m | Time window for the interest data (mode=interest). 'now' ranges return minute-level points; 'today' ranges return day/week points. Choose 'Custom range' to enter exact dates below. |
| `customDateRange` | string | no |  | Only used when 'Time range' = 'Custom range': 'YYYY-MM-DD YYYY-MM-DD' (e.g. '2024-01-01 2024-12-31') or 'YYYY-MM-DDTHH YYYY-MM-DDTHH' for hourly granularity. |
| `category` | string | no | 0 | Google Trends category filter (mode=interest). 0 = All categories. |
| `searchType` | string | no |  | Which Google surface to query (mode=interest). Web Search is the default. |
| `geoResolution` | string | no |  | Breakdown level for 'interest by region' (mode=interest). Auto lets Google pick the right level for the location; other levels are applied when the location supports them. |
| `trendingHours` | string | no | 24 | How far back the Trending Now list goes (mode=trending). |
| `trendingCategory` | string | no | all | Filter the Trending Now list to one of Google's trending categories (mode=trending). |
| `includeTrendingNews` | boolean | no | true | Attach news headlines, links and sources from Google's Trending RSS feed to trending items whose titles it covers (about ten highlighted stories per country, anywhere in the list). |
| `maxItems` | integer | no | 100 | Maximum dataset records per run: each interest row counts as one record, each trending item as one record. Remaining work stops once the limit is reached. |

Example (`references/example-input.json`):

```json
{
  "mode": "interest",
  "searchTerms": [
    "ai agents",
    "n8n"
  ],
  "geo": "US",
  "timeRange": "today 3-m",
  "maxItems": 50
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 50, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~google-trends-interest-and-related-query-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~google-trends-interest-and-related-query-scraper/runs" \
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
