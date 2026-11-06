---
name: workday-careers-site-job-listings-extractor
description: "Pull job postings from any company's Workday careers site: title, location, requisition ID, posting and start dates, time type, remote status and full description. Filter by keyword, location or posting date. Output fields: title, tenant, location, postedOn and more, as JSON rows. Use it for requests like \"Workday careers site job listings scraper\", or a CSV/JSON export of public Workday data."
---

# Workday Careers Site Job Listings Extractor

Pull job postings from any company's Workday careers site: title, location, requisition ID, posting and start dates, time type, remote status and full description. Filter by keyword, location or posting date.

- Actor: https://apify.com/nimbryxo-studio/workday-careers-site-job-listings-extractor (ID `nimbryxo-studio~workday-careers-site-job-listings-extractor`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/workday-careers-site-job-listings-extractor.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- Workday careers site job listings scraper
- a repeatable export of public Workday data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `tenant`: Tenant
- `location`: Location
- `postedOn`: Posted On
- `timeType`: Time Type
- `workplaceType`: Workplace Type

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | careerSite | How to find jobs. 'Scrape career site URLs' accepts careers pages or job URLs. 'Scrape a tenant by name' uses tenant + site. 'Scrape specific job URLs' requires /job/... |
| `startUrls` | array | no | ["`https://salesforce.wd12.myworkdayjobs.com/External_Career_Site"]` | Public Workday careers-site or job URLs (mode=careerSite or jobDetail). Paste the URL from your browser; both myworkdayjobs.com and myworkdaysite.com are supported. |
| `tenant` | string | no |  | Workday tenant name, for example 'nvidia' or 'capitalone' (mode=tenant). You can also paste the full careers URL here or use 'tenant/site'. |
| `site` | string | no |  | Optional career site identifier shown in the URL after the tenant host, for example 'NVIDIAExternalCareerSite' or 'External_Career_Site' (mode=tenant). It is case-sensitive. |
| `region` | string | no | auto | Workday data-center region. Leave 'auto' to detect it, or set wd1, wd3, wd5, wd12, wd103, and similar when you already know it (mode=tenant). |
| `searchText` | string | no |  | Optional keyword passed to the site's own job search, for example 'engineer' or 'marketing'. Workday searches titles and descriptions. |
| `locations` | array | no | [] | Optional locations to keep. Use names such as 'United States', 'New York', 'Remote' or 'US, CA, Santa Clara'; the actor matches them against the site's own location filters. |
| `jobFamilies` | array | no | [] | Optional job families or categories to keep, for example 'Engineering', 'Sales' or 'Finance'. Names come from the site's own Job Category filter; IDs are also accepted. |
| `remoteOnly` | boolean | no | false | Keep only postings the employer explicitly marks as remote. Hybrid and onsite postings are excluded. This turns on full detail fetching. |
| `postedWithin` | string | no | any | Keep jobs posted within this window. 'Any time' applies no date filter. Use Posted After for an exact cutoff date. |
| `postedAfter` | string | no |  | Optional exact cutoff date in YYYY-MM-DD form. When both Posted Within and Posted After are set, the stricter cutoff wins. |
| `startDateFrom` | string | no |  | Optional YYYY-MM-DD cutoff for the role's start date. Only applies when the posting publishes a start date. This turns on full detail fetching. |
| `scrapeDetails` | boolean | no | true | Fetch each posting's public job page for the full description, exact posting date, employment type, work model and every location. |
| `includeJobFamily` | boolean | no | true | Add each job's family or category (for example Engineering or Sales). This uses the site's own Job Category filter and is skipped automatically when a site has no such filter. |

2 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "scrapeDetails": false,
  "includeJobFamily": false,
  "maxItems": 25,
  "mode": "careerSite"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~workday-careers-site-job-listings-extractor/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~workday-careers-site-job-listings-extractor/runs" \
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
