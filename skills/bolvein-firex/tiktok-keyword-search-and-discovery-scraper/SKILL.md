---
name: tiktok-keyword-search-and-discovery-scraper
description: "Search TikTok by keyword or phrase and get matching videos with engagement stats, author profiles, music metadata, hashtags, and location tags, with optional discovery expansion for more results. Output fields: rank, caption, playCount, likeCount, commentCount and more, as JSON rows. Use it for requests like \"TikTok keyword search scraper\", or a CSV/JSON export of public TikTok data."
---

# TikTok Keyword Search & Discovery Scraper

Search TikTok by keyword or phrase and get matching videos with engagement stats, author profiles, music metadata, hashtags, and location tags, with optional discovery expansion for more results.

- Actor: https://apify.com/vexaloom-labs/tiktok-keyword-search-and-discovery-scraper (ID `vexaloom-labs~tiktok-keyword-search-and-discovery-scraper`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/tiktok-keyword-search-and-discovery-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- TikTok keyword search scraper
- a repeatable export of public TikTok data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `postId`: Post ID
- `rank`: Rank
- `searchType`: Search Type
- `caption`: Caption
- `createdAt`: Created At
- `author`: Author
- `playCount`: Views
- `likeCount`: Likes
- `commentCount`: Comments
- `shareCount`: Shares
- `postUrl`: Post URL

All 13 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `searchType` | string | yes | videos | Videos: keyword video search. Photos: slideshow/photo search. Hashtags: hashtag metadata plus its top videos (uses the Hashtags field). |
| `queries` | array | no |  | Keywords or phrases to search for (searchType=videos or photos). Each query is searched independently. |
| `hashtags` | array | no |  | Hashtags to look up (searchType=hashtags). The # is optional, e.g. coffee or #coffee. |
| `maxResultsPerQuery` | integer | no | 30 | Maximum posts to collect per query or hashtag, before filters. TikTok itself usually returns about 150-220 posts per query even when you ask for more. |
| `sortBy` | string | no | relevance | Client-side sort applied after collecting results. TikTok's web search does not support server-side sorting, so this only reorders the posts TikTok returned. |
| `publishedWithin` | string | no | all | Client-side filter that drops posts older than the selected window, based on each post's creation time. |
| `minDurationSeconds` | integer | no |  | Drop videos shorter than this. Leave blank for no minimum. |
| `maxDurationSeconds` | integer | no |  | Drop videos longer than this. Leave blank for no maximum. |
| `excludeAds` | boolean | no | false | Drop posts TikTok flags as paid advertisements. |
| `minLikeCount` | integer | no |  | Drop posts with fewer likes than this. Leave blank for no minimum. |
| `minViewCount` | integer | no |  | Drop posts with fewer plays/views than this. Leave blank for no minimum. |
| `uniqueAuthors` | boolean | no | false | Keep at most one post per creator, so the results read like a creator shortlist. When a sort is selected, the top-ranked post from each creator is kept. |
| `maxPostsPerAuthor` | integer | no |  | Optional cap on how many posts one creator may contribute. Ignored when One Post Per Author is on. |
| `enableExpansion` | boolean | no | false | After each keyword search, run extra searches derived from its own results: related searches, its top hashtags and its most-reused sound. |

3 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "queries": [
    "viral"
  ],
  "maxResultsPerQuery": 25,
  "searchType": "videos"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxResultsPerQuery` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~tiktok-keyword-search-and-discovery-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~tiktok-keyword-search-and-discovery-scraper/runs" \
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
