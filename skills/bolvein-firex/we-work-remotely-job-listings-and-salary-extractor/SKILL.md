---
name: we-work-remotely-job-listings-and-salary-extractor
description: "Reads We Work Remotely category pages or keyword search results and follows each listing for salary range, employment type, skills, applicant region requirements, and company details. Output fields: title, company, category, salary, postedAt and more, as JSON rows. Use it for requests like \"We Work Remotely job listings scraper\", or a CSV/JSON export of public We Work Remotely data."
---

# We Work Remotely Job Listings & Salary Extractor

Reads We Work Remotely category pages or keyword search results and follows each listing for salary range, employment type, skills, applicant region requirements, and company details.

- Actor: https://apify.com/dataspryva/we-work-remotely-job-listings-and-salary-extractor (ID `dataspryva~we-work-remotely-job-listings-and-salary-extractor`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/we-work-remotely-job-listings-and-salary-extractor.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Stop copying remote salaries; put roles in one sheet](https://www.youtube.com/shorts/aJWSYR7WvXE)

## When to use

Use this skill when the user wants:

- We Work Remotely job listings scraper
- a repeatable export of public We Work Remotely data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `company`: Company
- `category`: Category
- `salary`: Salary
- `postedAt`: Posted At
- `url`: Url

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | browse | What to scrape. browse reads category feeds, search filters the full current inventory, byUrls accepts We Work Remotely links. |
| `categories` | array | no | [] | One or more categories. Leave empty to collect every category (recommended for the full inventory). |
| `searchTerm` | string | no |  | Words to match in the title, company, category or description. All words must match. Required in search mode. |
| `startUrls` | array | no | [] | Job, category, search, company or listing URLs. Mix freely. (mode=byUrls) |
| `employmentTypes` | array | no | [] | Employment types to keep. Leave empty for all. We Work Remotely publishes Full-Time and Contract roles. |
| `regions` | array | no | [] | Keep jobs open to one or more regions. Jobs open worldwide always match. Leave empty for all. |
| `countries` | array | no | [] | Keep jobs open to one or more countries (ISO-2 codes). Jobs open worldwide always match. Leave empty for all. |
| `postedWithin` | string | no | any | Keep jobs listed within this window. The listing date is the current (renewed) date, not the original post date. |
| `minSalary` | integer | no |  | Minimum annualized salary in USD. Jobs without a disclosed salary are kept unless requireSalary is on. Published currencies are not converted. |
| `maxSalary` | integer | no |  | Maximum annualized salary in USD. Jobs without a disclosed salary are kept unless requireSalary is on. Published currencies are not converted. |
| `requireSalary` | boolean | no | false | Only keep jobs with a confidently parsed salary range. Off by default so jobs that do not disclose pay are not lost. |
| `includeDescription` | boolean | no | true | Include the full description HTML and text. Salary is parsed even when this is off. |
| `cleanHtml` | boolean | no | true | Remove scripts, tracking pixels and unsafe attributes from descriptionHtml. |
| `includeDetails` | boolean | no | false | Also fetch each job's HTML page for extra structured fields. The public job XML (apply URL/email, company bio, exact dates) is always read. |

4 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "categories": [
    "remote-full-stack-programming-jobs"
  ],
  "includeCompanyProfile": false,
  "maxItems": 25,
  "mode": "browse"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~we-work-remotely-job-listings-and-salary-extractor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~we-work-remotely-job-listings-and-salary-extractor/runs" \
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
