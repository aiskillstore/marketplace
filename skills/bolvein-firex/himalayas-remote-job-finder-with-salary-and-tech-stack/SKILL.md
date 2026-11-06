---
name: himalayas-remote-job-finder-with-salary-and-tech-stack
description: "Search Himalayas remote job listings by keyword or company and get salary range, employment type, tech stack and job page link for each role. Output fields: title, company, salaryMin, salaryMax, salaryPeriod and more, as JSON rows. Use it for requests like \"Himalayas remote job\", or a CSV/JSON export of public Himalayas data."
---

# Himalayas Remote Job Finder with Salary & Tech Stack

Search Himalayas remote job listings by keyword or company and get salary range, employment type, tech stack and job page link for each role.

- Actor: https://apify.com/vexaloom-labs/himalayas-remote-job-finder-with-salary-and-tech (ID `vexaloom-labs~himalayas-remote-job-finder-with-salary-and-tech`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/himalayas-remote-job-finder-with-salary-and-tech-stack.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- Himalayas remote job
- a repeatable export of public Himalayas data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `company`: Company
- `employmentType`: Employment Type
- `seniority`: Seniority
- `salaryMin`: Salary Min
- `salaryMax`: Salary Max
- `salaryPeriod`: Salary Period
- `salaryCurrency`: Salary Currency
- `salaryAnnualMin`: Salary Annual Min
- `salaryAnnualMax`: Salary Annual Max
- `location`: Location
- `skills`: Skills
- `postedAt`: Posted At
- `jobUrl`: Job Url

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | searchJobs | What to scrape. `searchJobs` runs a keyword search with filters. `browseAll` walks the newest-updated feed. `byCompany` returns a company's open roles. |
| `searchQuery` | string | no |  | Free-text keyword search (mode=searchJobs). Leave blank to page through the newest searchable listings. Himalayas caps keyword searches at 5,000 results. |
| `companySlug` | string | no |  | Canonical company slug or Himalayas company URL, e.g. `stripe` or `https://himalayas.app/companies/stripe`. Comma-separate several slugs, e.g. `stripe,vercel`. |
| `jobUrls` | array | no | [] | Himalayas job page URLs, e.g. `https://himalayas.app/companies/stripe/jobs/senior-engineer`. Closed or invalid URLs are skipped. |
| `country` | string | no |  | Only jobs open to this country. Leave blank for any country. Worldwide jobs are included unless Exclude worldwide is on. |
| `worldwide` | boolean | no | false | Only jobs with no country restrictions. Overrides the country filter. |
| `excludeWorldwide` | boolean | no | false | When a country is set, exclude jobs that are open worldwide. Requires country. |
| `seniority` | array | no | [] | Keep jobs at any of these seniority levels. Leave empty for all levels. |
| `employmentType` | string | no |  | Keep jobs of this employment type. Leave blank for all types. |
| `timezone` | string | no |  | Keep jobs that accept this UTC offset, e.g. `-5`, `UTC-5` or `UTC+05:30`. Leave blank for any timezone. |
| `categories` | array | no | [] | Keep jobs whose categories, parent categories or tech tags contain any of these terms (case-insensitive), e.g. `python`, `react`, `developer`. |
| `minSalary` | integer | no |  | Annualised salary floor. Hourly, weekly and monthly pay is converted to a yearly figure before comparison. Use salaryCurrency to compare in a specific currency. |
| `maxSalary` | integer | no |  | Annualised salary ceiling. Jobs whose annualised range starts above this value are excluded. |
| `salaryCurrency` | string | no |  | Only compare and keep jobs paid in this currency. Leave blank to compare each listing in its own currency (no conversion is applied). |

4 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "searchQuery": "software engineer",
  "maxItems": 25,
  "mode": "searchJobs"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~himalayas-remote-job-finder-with-salary-and-tech/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~himalayas-remote-job-finder-with-salary-and-tech/runs" \
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
