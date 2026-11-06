---
name: netease-cloud-music-song-chart-and-playlist-scraper
description: "Search NetEase Cloud Music songs, fetch song details by URL, pull an artist's top songs or album list, browse playlists by genre, or get any top-100 chart. Returns artist, album, duration, cover art, and popularity for each track. Output fields: name, artist, album, rankPosition, playlistName and more, as JSON rows. Use it for requests like \"NetEase Cloud Music song, chart scraper\", or a CSV/JSON export of public NetEase Cloud Music data."
---

# NetEase Cloud Music Song, Chart & Playlist Scraper

Search NetEase Cloud Music songs, fetch song details by URL, pull an artist's top songs or album list, browse playlists by genre, or get any top-100 chart. Returns artist, album, duration, cover art, and popularity for each track.

- Actor: https://apify.com/dataspryva/netease-cloud-music-song-chart-and-playlist (ID `dataspryva~netease-cloud-music-song-chart-and-playlist`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/netease-cloud-music-song-chart-and-playlist-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- NetEase Cloud Music song, chart scraper
- a repeatable export of public NetEase Cloud Music data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `name`: Name
- `artist`: Artist
- `album`: Album
- `rankPosition`: Rank Position
- `chartName`: Chart Name
- `playlistName`: Playlist Name
- `durationSec`: Duration Sec

All 9 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | search | What to fetch. Each mode reads its own list field. |
| `searchQueries` | array | no | ["周杰伦"] | Free-text queries (mode=search). One or more artist, song, album or playlist names. |
| `searchType` | string | no | song | Which catalog entity to search for (mode=search). |
| `songUrls` | array | no | [] | music.163.com song URLs or bare song IDs, e.g. 186016. |
| `artistIds` | array | no | [] | Artist IDs, music.163.com artist URLs, or exact artist names. |
| `artistOrder` | string | no | hot | Order the artist's song catalogue by popularity or release time (mode=byArtist). |
| `albumUrls` | array | no | [] | music.163.com album URLs or bare album IDs. |
| `playlistUrls` | array | no | [] | music.163.com playlist URLs or bare playlist IDs. Full tracklists are read. |
| `playlistCat` | string | no | 华语 | NetEase playlist genre, scene or mood to browse (mode=byPlaylist). |
| `toplistIds` | array | no | [] | Chart IDs, music.163.com toplist URLs, or Chinese/English chart names. Use `all` or leave empty for every current chart. |
| `maxTracksPerChart` | integer | no | 0 | Limit tracks read from each chart before the global max items cap (mode=byToplist). 0 reads every track. |
| `commentUrls` | array | no | [] | Song, album, playlist or chart URLs/IDs. A bare ID is treated as a song; use `album:123`, `playlist:123` or `chart:123` to be explicit. |
| `commentOrder` | string | no | recommended | Recommended comments or NetEase's hot-comment selection (mode=comments). |
| `maxCommentsPerItem` | integer | no | 100 | Maximum top-level comments read per song, album, playlist or chart (mode=comments). NetEase stops anonymous pagination around 1,100. |

14 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "maxItems": 25,
  "mode": "search",
  "maxCommentsPerItem": 25
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~netease-cloud-music-song-chart-and-playlist/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/dataspryva~netease-cloud-music-song-chart-and-playlist/runs" \
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
