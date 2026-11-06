---
name: reddit-multi-mode-scraper-for-posts-comments-and-profiles
description: "Pick one of five modes to pull subreddit posts, full comment threads, user profiles, keyword search results or curated community listings from Reddit, each with deep post/comment filters. No account or API key needed. Output fields: subreddit_prefixed, title, author, score, commentCount and more, as JSON rows. Use it for requests like \"Reddit posts and comments scraper\", \"subreddit export\", \"Reddit keyword search\", or a CSV/JSON export of public Reddit data."
---

# Reddit Multi-Mode Scraper for Posts, Comments & Profiles

Pick one of five modes to pull subreddit posts, full comment threads, user profiles, keyword search results or curated community listings from Reddit, each with deep post/comment filters. No account or API key needed.

- Actor: https://apify.com/nimbryxo-studio/reddit-multi-mode-scraper-for-posts-comments (ID `nimbryxo-studio~reddit-multi-mode-scraper-for-posts-comments`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/reddit-multi-mode-scraper-for-posts-comments-and-profiles.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

Short video breakdown:
- [Your customers are describing the problem for free](https://www.youtube.com/shorts/3TmxkUNaB0U)

## When to use

Use this skill when the user wants:

- Reddit posts and comments scraper
- subreddit export
- Reddit keyword search
- a repeatable export of public Reddit data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `subreddit_prefixed`: Subreddit prefixed
- `title`: Title
- `author`: Author
- `score`: Score
- `commentCount`: Comment Count
- `source`: Source
- `createdAt`: Created At
- `permalink`: Permalink

All 9 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | subreddit | What to scrape: a subreddit listing, post URLs with comments, a user profile, or keyword search. |
| `source` | string | no | auto | auto uses live Reddit first and the Arctic Shift archive for depth/bulk or as a fallback. archive is faster and cheaper but lags live Reddit by several hours; live never uses… |
| `subreddits` | array | no | ["programming"] | Subreddits to scrape (mode=subreddit). Accepts names, r/ names or URLs. |
| `postUrls` | array | no | [] | Post URLs, comment URLs, share links or bare post IDs (mode=post). |
| `usernames` | array | no | [] | Reddit usernames to scrape (mode=profile). Accepts names, u/ names or profile URLs. |
| `searchQuery` | string | no |  | Keyword or phrase to search for (mode=search). Reddit search syntax such as "exact phrase", author:name, subreddit:name and -exclude is supported by live search. |
| `maxItems` | integer | no | 50 | Hard cap on all records pushed by the run, across every target. |
| `maxPosts` | integer | no | 25 | Posts per subreddit, keyword or profile section. |
| `maxComments` | integer | no | 100 | Comments per post, keyword, or profile comment section. 0 disables comment records. |
| `maxDepth` | integer | no | 6 | Deepest reply level to emit (0 = top-level comments only). |
| `includeComments` | boolean | no | true | Emit comment records for each post. Disable to fetch only the parent post. |
| `includePost` | boolean | no | true | Emit the post record before its comments. |
| `sort` | string | no | hot | Post/listing sort. Search accepts relevance, hot, top, new or comments; other modes use hot, new, top, rising, controversial or best. |
| `timeFilter` | string | no | day | Time window for top/controversial sorts and search. |

53 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "mode": "subreddit",
  "subreddits": [
    "smallbusiness"
  ],
  "sort": "top",
  "timeFilter": "week",
  "maxItems": 25,
  "maxPosts": 10,
  "maxComments": 20,
  "includeComments": true
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~reddit-multi-mode-scraper-for-posts-comments/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/nimbryxo-studio~reddit-multi-mode-scraper-for-posts-comments/runs" \
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
