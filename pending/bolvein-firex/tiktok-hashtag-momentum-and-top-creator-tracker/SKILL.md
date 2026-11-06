---
name: tiktok-hashtag-momentum-and-top-creator-tracker
description: "Reads TikTok Creative Center's trending-hashtag list for any country and returns rank, post and view counts, a day-by-day momentum curve, and top creators behind each trend. Output fields: rankIndex, hashtagName, publishCnt, vv and more, as JSON rows. Use it for requests like \"TikTok trending hashtags\", \"TikTok Creative Center hashtags\", \"TikTok trend tracker\", or a CSV/JSON export of public TikTok data."
---

# TikTok Hashtag Momentum & Top Creator Tracker

Reads TikTok Creative Center's trending-hashtag list for any country and returns rank, post and view counts, a day-by-day momentum curve, and top creators behind each trend.

- Actor: https://apify.com/dataspryva/tiktok-hashtag-momentum-and-top-creator-tracker (ID `dataspryva~tiktok-hashtag-momentum-and-top-creator-tracker`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/tiktok-hashtag-momentum-and-top-creator-tracker.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Catch rising TikTok hashtags before Friday](https://www.youtube.com/shorts/C3buLaYtlGg)

## When to use

Use this skill when the user wants:

- TikTok trending hashtags
- TikTok Creative Center hashtags
- TikTok trend tracker
- a repeatable export of public TikTok data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `rankIndex`: Rank
- `hashtagName`: Hashtag
- `publishCnt`: Post Count
- `vv`: Video Views

All 13 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | no | trendingHashtags | Choose 'Trending hashtags' for TikTok's ranked hashtag charts (post/view counts, popularity curve, creators) or 'Trending videos' for TikTok's ranked video charts (views… |
| `countries` | array | no | ["US"] | (mode=trendingHashtags) One or more markets to read the hashtag chart for. Each market adds its own ranked rows. |
| `periods` | array | no | ["7"] | (mode=trendingHashtags) Lookback windows in days. 7 shows recent spikes, 90 shows longer-term trends. Select one or more. |
| `includeOverallRanking` | boolean | no | true | (mode=trendingHashtags) Include each market's overall top-3 hashtag chart. Turn off to read only the industry charts selected below. |
| `scanAllIndustries` | boolean | no | true | (mode=trendingHashtags) Read all 19 industry charts for every market and window. This widens coverage from 3 to up to 60 hashtags per market and window, because each industry… |
| `industries` | array | no | [] | (mode=trendingHashtags) Specific industry charts to read when 'Scan all industries' is off. Ignored when scanning all industries. 19 public categories are available. |
| `includeCreatorLeaders` | boolean | no | false | (mode=trendingHashtags) Add creator rows that aggregate the creators TikTok credits across the collected hashtags, sorted by how many trends they appear in. |
| `minHashtagAppearances` | integer | no | 2 | (mode=trendingHashtags, creator leaderboard only) Only list creators credited on at least this many collected hashtag rows. |
| `videoCountries` | array | no | ["US"] | (mode=trendingVideos) Markets with a public TikTok trending-video chart. Select one or more. |
| `videoPeriods` | array | no | ["7"] | (mode=trendingVideos) Windows in days for the trending-video chart: 7 for videos created in the last week, 30 for the last month. |
| `videoSortBy` | string | no | views | (mode=trendingVideos) Metric used for the video ranking. |
| `videoOrganicOnly` | boolean | no | false | (mode=trendingVideos) Rank only organic (non-promoted) videos. TikTok returns a different ranking for organic-only charts. |
| `videoContentTags` | array | no | [] | (mode=trendingVideos) Query TikTok's video ranking by content tag and dedupe the videos. Each selected tag is a separate ranking read; 'All tags' also includes the unfiltered… |
| `weeksBack` | integer | no | 0 | (mode=trendingVideos) Add past weekly rankings by moving the chart end date back 7 days per step (0-4). Useful for comparing this week with earlier weeks. |

2 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "trendingHashtags",
  "countries": [
    "US"
  ],
  "periods": [
    "7"
  ],
  "maxItems": 25
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~tiktok-hashtag-momentum-and-top-creator-tracker/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~tiktok-hashtag-momentum-and-top-creator-tracker/runs" \
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
