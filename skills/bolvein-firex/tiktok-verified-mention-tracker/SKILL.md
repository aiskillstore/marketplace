---
name: tiktok-verified-mention-tracker
description: "Find TikTok posts that tag a specific creator or brand handle, with each result checked against TikTok's own mention markup so you can tell a real @mention from a caption that merely contains the name. Output fields: targetUsername, postUrl, author.followerCount, playCount, likeCount and more, as JSON rows. Use it for requests like \"TikTok verified mention\", or a CSV/JSON export of public TikTok data."
---

# TikTok Verified Mention Tracker

Find TikTok posts that tag a specific creator or brand handle, with each result checked against TikTok's own mention markup so you can tell a real @mention from a caption that merely contains the name.

- Actor: https://apify.com/nimbryxo-studio/tiktok-profile-mention-scraper (ID `nimbryxo-studio~tiktok-profile-mention-scraper`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/tiktok-verified-mention-tracker.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- TikTok verified mention
- a repeatable export of public TikTok data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `targetUsername`: Tracked account
- `mentionType`: Mention type
- `postUrl`: Post
- `caption`: Caption
- `createdAt`: Posted
- `author.username`: Posted by
- `author.followerCount`: Author followers
- `playCount`: Views
- `likeCount`: Likes
- `commentCount`: Comments
- `shareCount`: Shares
- `postType`: Type

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `usernames` | array | yes |  | Brand or creator accounts whose mentions you want. Type a handle (nike), a handle with @ (@nike) or paste a profile link (`https://www.tiktok.com/@nike`). |
| `mentionFilter` | string | no | taggedOrCaption | Every saved post carries a mentionType label: 'tagged' (the caption contains TikTok's clickable tag of the account), 'captionText' (the caption types @handle without a working… |
| `excludeOwnPosts` | boolean | no | true | Leave out posts published by the tracked account itself, so you only see what other people say about it. |
| `datePosted` | string | no | anyTime | Only look at posts published in this period. |
| `postedAfter` | string | no |  | Exact cut-off date. Use a date (2026-10-01) or a relative age such as '3 days' or '2 weeks'. Works together with 'Posted within'; the stricter of the two applies. |
| `sortBy` | string | no | relevance | How saved posts are ordered for each account. 'Most liked' and 'Newest first' look at every post found before keeping the top ones. |
| `minPlayCount` | integer | no |  | Skip posts with fewer views than this. Leave empty to keep posts of any size. |
| `searchDepth` | string | no | standard | 'Standard' runs one search per account and reads every page TikTok returns. 'Deep' adds searches by plain handle, display name and #handle, a most-liked pass, several date ranges… |
| `searchCountry` | string | no | any | TikTok shows different posts in different countries. Pick a country to see the mentions people there get in their search results (for example Japan for Japanese posts). |
| `followRelatedVideos` | boolean | no | false | After searching, open TikTok's related videos for every post that tags the account and keep related posts that also mention it (repeating a few hops). |
| `maxResultsPerProfile` | integer | no | 50 | Stop after this many saved posts for each account. TikTok search usually yields tens to a few hundred posts per account, so very high values simply mean 'everything found'. |
| `maxItems` | integer | no |  | Optional limit across all accounts in this run. Leave empty for no overall limit. |
| `downloadVideos` | boolean | no | false | Download each saved video into this run's key-value store and add a permanent link to it (downloadedVideoUrl). |
| `addPostCountry` | boolean | no | false | Look up the country TikTok records for every saved post (locationCreated, e.g. US, BR, JP). Useful for market breakdowns of who mentions you. Adds a few seconds per post. |

Example (`references/example-input.json`):

```json
{
  "usernames": [
    "billieeilish"
  ],
  "maxResultsPerProfile": 3,
  "maxItems": 50
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 50, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~tiktok-profile-mention-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~tiktok-profile-mention-scraper/runs" \
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
