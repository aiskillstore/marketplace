---
name: startup-jobs-category-and-keyword-job-scraper
description: "Collect startup job listings from startup.jobs by category and keyword, with title, company, work mode, salary, job type, listing text, tags, and the listing link. Output fields: title, company, location, salary, postedAt and more, as JSON rows. Use it for requests like \"startup.jobs category scraper\", or a CSV/JSON export of public startup.jobs data."
---

# startup.jobs Category & Keyword Job Scraper

Collect startup job listings from startup.jobs by category and keyword, with title, company, work mode, salary, job type, listing text, tags, and the listing link.

- Actor: https://apify.com/vexaloom-labs/startup-jobs-category-and-keyword-job-scraper (ID `vexaloom-labs~startup-jobs-category-and-keyword-job-scraper`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/startup-jobs-category-and-keyword-job-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- startup.jobs category scraper
- a repeatable export of public startup.jobs data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `company`: Company
- `location`: Location
- `workplaceType`: Workplace Type
- `salary`: Salary
- `postedAt`: Posted At
- `url`: Url

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `category` | string | no | remote | Broad job category. Choose All categories to search everything, or Remote jobs for remote-only listings. |
| `role` | string | no |  | Specific role from the startup.jobs role taxonomy. When set, the category is ignored. |
| `keyword` | string | no |  | Matches job titles, company names and tags on startup.jobs. It does not search full description text. |
| `company` | string | no |  | Company name, slug or startup.jobs company URL (e.g. stripe or `https://startup.jobs/company/stripe`). |
| `location` | string | no |  | City or country name, or a startup.jobs location URL (e.g. United States, London, `https://startup.jobs/locations/germany`). Use Remote for remote jobs. |
| `workplaceType` | string | no |  | Filter by remote, hybrid or on-site work. |
| `employmentType` | string | no |  | Filter by full-time, part-time, contract or internship roles. |
| `experienceLevel` | string | no |  | Filter by the experience range published on the listing. Jobs without an experience level are excluded when this is set. |
| `minSalaryUsd` | integer | no |  | Only jobs whose published maximum salary is at least this amount in USD. Jobs without a published salary are excluded. |
| `maxSalaryUsd` | integer | no |  | Only jobs whose published minimum salary is at most this amount in USD. Jobs without a published salary are excluded. |
| `postedWithin` | string | no |  | Only include jobs published within this period. |
| `maxItems` | integer | no | 50 | Maximum number of jobs to return (1-500). |

Example (`references/example-input.json`):

```json
{
  "maxItems": 25,
  "location": "New York, NY",
  "keyword": "coffee shop"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~startup-jobs-category-and-keyword-job-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~startup-jobs-category-and-keyword-job-scraper/runs" \
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
