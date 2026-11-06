---
name: indeed-global-job-scraper-with-company-salary-reports
description: "Search Indeed jobs across 62 countries by keyword, location, or filters for job type, remote status, experience, education, and salary. Returns full descriptions, structured salaries, and each employer's ratings and salary-by-title reports. Output fields: positionName, displayTitle, company, rating, salary and more, as JSON rows. Use it for requests like \"Indeed job scraper with salaries\", \"job postings export\", \"salary data by title\", or a CSV/JSON export of public Indeed data."
---

# Indeed Global Job Scraper with Company Salary Reports

Search Indeed jobs across 62 countries by keyword, location, or filters for job type, remote status, experience, education, and salary. Returns full descriptions, structured salaries, and each employer's ratings and salary-by-title reports.

- Actor: https://apify.com/nimbryxo-studio/indeed-global-job-scraper-with-company-salary (ID `nimbryxo-studio~indeed-global-job-scraper-with-company-salary`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/indeed-global-job-scraper-with-company-salary-reports.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [The salary data is already public](https://www.youtube.com/shorts/33f3pNEO6Oc)

## When to use

Use this skill when the user wants:

- Indeed job scraper with salaries
- job postings export
- salary data by title
- a repeatable export of public Indeed data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `positionName`: Job title
- `displayTitle`: Display title
- `company`: Company
- `rating`: Rating
- `location`: Location
- `salary`: Salary
- `jobType`: Job type
- `remoteWorkType`: Workplace
- `postedAt`: Posted
- `isRepost`: Repost
- `isSponsored`: Sponsored
- `easyApply`: Easy apply
- `url`: Indeed link

All 42 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `position` | string | no |  | Job title, skill or keywords, e.g. `web developer`, `nurse`. Search one company's jobs with `company:Amazon`, titles only with `title:(data analyst)`; quotes, OR and -exclusions… |
| `location` | string | no |  | City, region or postal code, e.g. `San Francisco`, `Austin, TX`, `10001`, `London`. Leave empty to search the whole country. |
| `company` | string | no |  | Only jobs from one employer, e.g. `Amazon`, `Visa`, `DocuSign`. The name is resolved to Indeed's employer key so the company filter is applied by Indeed itself, then verified per… |
| `locationShards` | array | no |  | Optional list of extra locations to search separately with the same keywords and filters, e.g. `New York, NY`, `Chicago, IL`, `Remote`. |
| `country` | string | no | US | Indeed country site to search. Results come in the site's language and salaries in its currency. |
| `maxItemsPerSearch` | integer | no | 100 | Maximum number of jobs to save for each search (the keyword search and each search URL). Indeed's cursor stops at roughly 1,000 fetched rows, including duplicates; use… |
| `maxItems` | integer | no |  | Optional hard cap across every search and pasted job URL. The run stops as soon as this many jobs are saved. Leave empty for no global cap. |
| `shardByDate` | boolean | no | false | Run each keyword search five times, for the last 1, 3, 7, 14 and 30 days, and remove duplicates. Useful for freshness coverage when you need more than one cursor walk per search. |
| `jobType` | string | no |  | Employment type. |
| `workplaceType` | string | no |  | Where the work happens. |
| `datePosted` | string | no |  | Only jobs added to Indeed within this period. |
| `experienceLevel` | string | no |  | Required experience level. |
| `educationLevel` | string | no |  | Required education. |
| `salaryMin` | integer | no |  | Only jobs whose salary range reaches at least this yearly amount, in the country's currency (hourly and monthly pay is converted to yearly). |

9 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "position": "account executive",
  "location": "Austin, TX",
  "country": "US",
  "maxItems": 25,
  "datePosted": "7",
  "includeCompanyRatings": true
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~indeed-global-job-scraper-with-company-salary/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~indeed-global-job-scraper-with-company-salary/runs" \
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
