---
name: website-contact-page-email-and-phone-crawler
description: "Crawl a website's contact, about and team pages and collect its public emails, phone numbers, and social media profile links in one normalized record per site. Output fields: websiteUrl, status, emails, primaryEmail, phones and more, as JSON rows. Use it for requests like \"Find emails and phone numbers from a list of websites\", \"website email extractor\", \"contact page scraper\", or a CSV/JSON export of public Any website data."
---

# Website Contact Page Email & Phone Crawler

Crawl a website's contact, about and team pages and collect its public emails, phone numbers, and social media profile links in one normalized record per site.

- Actor: https://apify.com/nimbryxo-studio/website-contact-page-email-and-phone-crawler (ID `nimbryxo-studio~website-contact-page-email-and-phone-crawler`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/website-contact-page-email-and-phone-crawler.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [The email is already on the website](https://www.youtube.com/shorts/MHdeuiVwMZA)

## When to use

Use this skill when the user wants:

- Find emails and phone numbers from a list of websites
- website email extractor
- contact page scraper
- a repeatable export of public Any website data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's README (Output section):

- `websiteUrl`: Website Url
- `status`: Status
- `companyName`: Company Name
- `emails`: Emails
- `primaryEmail`: Primary Email
- `roleEmails`: Role Emails
- `namedEmails`: Named Emails
- `emailDetails`: Email Details
- `phones`: Phones
- `primaryPhone`: Primary Phone
- `phoneDetails`: Phone Details
- `socialLinks`: Social Links
- `socialProfiles`: Social Profiles
- `address`: Address
- `contactPageUrl`: Contact Page Url
- `contactForms`: Contact Forms
- `pagesCrawled`: Pages Crawled
- `pagesCrawledUrls`: Pages Crawled Urls
- `maxDepthReached`: Max Depth Reached
- `skippedByRobots`: Skipped By Robots

All 26 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `urls` | array | yes |  | Websites to scan for public contact details. You can paste full URLs or bare domains; duplicates are removed. |
| `maxPagesPerSite` | integer | no | 20 | Maximum number of pages to fetch per website. Contact, about, team and imprint pages are prioritised. |
| `maxConcurrency` | integer | no | 5 | How many pages of the same website may be fetched in parallel. |
| `maxSitesConcurrency` | integer | no | 3 | How many websites are scanned in parallel. Lower this if you hit rate limits. |
| `requestTimeoutSecs` | integer | no | 15 | Maximum time to wait for one page before trying the next proxy tier. |
| `defaultCountry` | string | no |  | ISO 3166-1 alpha-2 country used to interpret phone numbers written without an international prefix. Leave empty to infer from the website domain. |
| `useProxy` | boolean | no | false | Start with the Apify proxy ladder instead of trying direct requests first. The actor always retries blocked requests through the proxy ladder automatically. |
| `smartPrioritise` | boolean | no | true | Try common contact, about, team, imprint and support paths first, and queue contact-like links ahead of other internal links. |
| `respectRobotsTxt` | boolean | no | true | Skip pages that the website's robots.txt disallows. Turn this off only when you own the site or have permission to crawl it. |
| `useSitemap` | boolean | no | true | Read sitemap.xml and robots.txt sitemap entries to find contact and about pages that are not linked from the homepage. |
| `renderFallback` | boolean | no | true | If plain HTML contains no email or phone, render up to two pages in a headless browser to capture contacts loaded by JavaScript. |
| `onlyWithContacts` | boolean | no | false | Drop records for websites where no email, phone, social profile or contact form was found. |
| `includeNamedEmails` | boolean | no | true | Include personal addresses such as jane.smith@company.com. When off, only role addresses such as info@, sales@ and support@ are kept. |

Example (`references/example-input.json`):

```json
{
  "urls": [
    "https://apify.com",
    "https://n8n.io"
  ],
  "maxPagesPerSite": 10
}
```

The input passes the Actor's input schema (checked at every publish). The run size follows the number of inputs you pass.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~website-contact-page-email-and-phone-crawler/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~website-contact-page-email-and-phone-crawler/runs" \
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
