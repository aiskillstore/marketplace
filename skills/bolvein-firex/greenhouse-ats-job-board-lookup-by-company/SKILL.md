---
name: greenhouse-ats-job-board-lookup-by-company
description: "Pull every open role from one or more Greenhouse company boards, or look up specific postings by job ID, with location, department, employment type, salary, and apply link for each. Output fields: title, companySlug, companyName, location, departments and more, as JSON rows. Use it for requests like \"Greenhouse ATS job board\", or a CSV/JSON export of public Greenhouse data."
---

# Greenhouse ATS Job Board Lookup by Company

Pull every open role from one or more Greenhouse company boards, or look up specific postings by job ID, with location, department, employment type, salary, and apply link for each.

- Actor: https://apify.com/dataspryva/greenhouse-ats-job-board-lookup-by-company (ID `dataspryva~greenhouse-ats-job-board-lookup-by-company`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/greenhouse-ats-job-board-lookup-by-company.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- Greenhouse ATS job board
- a repeatable export of public Greenhouse data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `companySlug`: Company Slug
- `companyName`: Company Name
- `location`: Location
- `departments`: Departments
- `employmentType`: Employment Type
- `publishedAt`: Published At
- `updatedAt`: Updated At
- `applyUrl`: Apply Url
- `region`: Region

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | companyJobs | What to fetch: jobs from company boards, specific job URLs, or company board lookup. |
| `companies` | array | no |  | Board tokens, board URLs, embed URLs, job URLs, company names or domains. Examples: "stripe", "`https://job-boards.greenhouse.io/figma",` "Airbnb", "jobs.elastic.co". |
| `jobUrls` | array | no |  | Full Greenhouse job URLs to fetch one by one. A company board URL alone is not enough; include /jobs/. |
| `searchQuery` | string | no |  | Name or token text to match against the built-in company directory. Leave empty to resolve the Companies list instead. |
| `titleKeywords` | array | no |  | Keep jobs whose title contains any of these words (case-insensitive). |
| `excludeTitleKeywords` | array | no |  | Drop jobs whose title contains any of these words (case-insensitive). |
| `locations` | array | no |  | Keep jobs whose location or office contains any of these words, e.g. Remote, London, New York. |
| `departments` | array | no |  | Keep jobs in departments that contain any of these words, e.g. Engineering, Sales. |
| `workplaceType` | string | no | any | Keep remote, hybrid or on-site roles. Jobs without a stated arrangement are dropped when this is not Any. |
| `employmentType` | string | no | any | Keep full-time, part-time, contract, internship or temporary roles when the employer states it. |
| `publishedAfter` | string | no |  | Keep jobs first published on or after this date (YYYY-MM-DD). |
| `updatedAfter` | string | no |  | Keep jobs last updated on or after this date (YYYY-MM-DD). |
| `onlyWithSalary` | boolean | no | false | Keep only jobs with a published or clearly stated pay range. |
| `minAnnualSalary` | integer | no |  | Keep jobs whose base pay reaches at least this yearly amount. Hourly, monthly and weekly ranges are annualized. |

8 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "companies": [
    "airbnb"
  ],
  "maxItems": 25,
  "mode": "companyJobs",
  "searchQuery": "head of growth"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~greenhouse-ats-job-board-lookup-by-company/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~greenhouse-ats-job-board-lookup-by-company/runs" \
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
