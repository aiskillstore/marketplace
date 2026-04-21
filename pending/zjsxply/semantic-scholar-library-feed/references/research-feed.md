# Research Feed Workflow

## Goal

Use this workflow when the user needs to inspect, export, or page through authenticated Semantic Scholar `Research Feeds`.

## SSR bootstrap

The stable bootstrap path is:

- `https://www.semanticscholar.org/me/recommendations`

With a valid login cookie set, this page returns SSR HTML instead of only a client shell. The HTML contains:

- visible recommendation cards
- folder state
- `var DATA = '...'`

Decode order for `var DATA`:

1. base64 decode
2. URL decode
3. JSON parse

The key SSR snapshot is:

- `GET_LIBRARY_FOLDERS_RECOMMENDATIONS`

Important fields inside that snapshot:

- `resultData.days`
- `resultData.nextWindowUTC`
- `path`

The `path` contains the active `folderIds` and the current `windowUTC`.

## Real API path

Do not request the SSR `path` directly against the site root. The live JSON endpoint is:

- `/api/1/library/folders/recommendations?folderIds=...&windowUTC=...`

When multiple folders are active, repeat the `folderIds` query key instead of packing them into one comma-separated value. Example:

- `/api/1/library/folders/recommendations?folderIds=13895811&folderIds=11740605&windowUTC=1773029456`

Directly requesting `/library/folders/recommendations?...` returns `404`.

## Pagination rule

Use `nextWindowUTC` from the current response as the `windowUTC` of the next request. This is more reliable than clicking `View Older Recommendations` in the DOM.

Do not rely on adding `windowUTC` to `/me/recommendations`. That did not switch the SSR window in the verified runs.

## Stop conditions

Stop pagination when any of these is true:

1. `days` is empty.
2. `nextWindowUTC` is missing or `null`.
3. The next `windowUTC` repeats a previously seen value.

The tested account naturally ended on a window that still had data but returned `nextWindowUTC = null`.

## Persistence rule

Write output incrementally after every successful window. Do not wait for the entire crawl to finish. This avoids losing progress if later windows slow down or the user interrupts the run.

## Useful fields for local screening

The feed API already includes enough metadata for a first-pass paper filter:

- `days[].date`
- `days[].papers[].libraryFolderId`
- `days[].papers[].paper.id`
- `days[].papers[].paper.slug`
- `days[].papers[].paper.title.text`
- `days[].papers[].paper.paperAbstract.text`
- `days[].papers[].paper.links`
- `days[].papers[].paper.primaryPaperLink`

Prefer deduplicating by `paper.id`, with `title.text` only as fallback.

## CLI entry points

- `ssr-dump`: inspect decoded SSR snapshots
- `feed-crawl`: bootstrap from SSR and paginate the feed API

Typical pattern:

```bash
python3 scripts/semantic_scholar_cli.py feed-crawl \
  --output /tmp/research-feed.json
```
