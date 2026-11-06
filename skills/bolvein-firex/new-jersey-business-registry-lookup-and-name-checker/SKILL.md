---
name: new-jersey-business-registry-lookup-and-name-checker
description: "Look up New Jersey registered businesses by name, keyword or entity ID, and check whether a candidate business name is available for a new filing. Returns entity ID, entity type, city and incorporation date. Output fields: businessName, entityTypeAbbr, entityTypeFull, city, incorporatedDate and more, as JSON rows. Use it for requests like \"New Jersey business entity search\", \"business name availability check\", or a CSV/JSON export of public NJ business registry data."
---

# New Jersey Business Registry Lookup & Name Checker

Look up New Jersey registered businesses by name, keyword or entity ID, and check whether a candidate business name is available for a new filing. Returns entity ID, entity type, city and incorporation date.

- Actor: https://apify.com/vexaloom-labs/new-jersey-business-registry-lookup-and-name (ID `vexaloom-labs~new-jersey-business-registry-lookup-and-name`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/new-jersey-business-registry-lookup-and-name-checker.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Stop checking business filings one name at a time](https://www.youtube.com/shorts/tGV77V4rMqk)

## When to use

Use this skill when the user wants:

- New Jersey business entity search
- business name availability check
- a repeatable export of public NJ business registry data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `businessName`: Business Name
- `entityId`: Entity Id
- `entityTypeAbbr`: Entity Type Abbr
- `entityTypeFull`: Entity Type Full
- `city`: City
- `incorporatedDate`: Incorporated Date
- `incorporatedMonth`: Incorporated Month
- `isAvailable`: Is Available
- `documentCount`: Document Count

All 10 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | byName | What to fetch. |
| `businessNames` | array | no | ["Amazon"] | One or more names (mode=byName, availability). Name search is a prefix match: 'Amazon' finds names starting with Amazon, and a leading 'The' is ignored. |
| `keywordSearches` | array | no | [] | One or more keyword phrases (mode=byKeyword). Each phrase is split into words, and every word must appear in the business name; up to 5 words per phrase and 20 phrases. |
| `entityIds` | array | no | [] | Exact 10-digit New Jersey entity IDs (mode=byEntityId, documents). Invalid IDs are reported in the run status instead of being dropped silently. Up to 200 IDs. |
| `linkType` | string | no | principal | Which free Business Records Service search to use (mode=byLinkedName). |
| `linkedName` | string | no |  | Last name, business name, registered-agent name, or previous/alternate name to search (mode=byLinkedName). |
| `linkedFirstName` | string | no |  | Optional first name when linkType=principal (mode=byLinkedName). |
| `linkedMiddleName` | string | no |  | Optional middle name when linkType=principal (mode=byLinkedName). |
| `linkedCity` | string | no |  | Optional city filter for principal or registered-agent searches (mode=byLinkedName). |
| `entityTypes` | array | no | [] | Keep only these New Jersey entity types. Empty means no filter. Filters run on every page, not only after the 500-row display cap. |
| `cityFilter` | string | no |  | Keep only businesses whose on-file city matches exactly (case-insensitive). Leave blank for all cities. |
| `maxItems` | integer | no | 100 | Hard cap on emitted records (1-500, the source's display limit). Applied exactly, including when it is above 200. |

Example (`references/example-input.json`):

```json
{
  "mode": "byKeyword",
  "keywordSearches": [
    "roofing"
  ],
  "maxItems": 25
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~new-jersey-business-registry-lookup-and-name/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~new-jersey-business-registry-lookup-and-name/runs" \
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
