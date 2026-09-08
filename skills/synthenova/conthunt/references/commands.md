# ContHunt command reference

## Authentication

```text
conthunt login
conthunt logout
conthunt whoami --json
```

Authentication resolution order is `--token`, `CONTHUNT_TOKEN`, then the credential saved by `conthunt login`.

## Installation and updates

```text
conthunt install skill
conthunt update
conthunt update --json
```

`install skill` delegates to the public skills installer using `npx skills add Synthenova/conthunt-cli --skill conthunt -g`. It does not inspect or rewrite skill files itself.

The CLI checks its release channel at most once every 24 hours and writes an available-update notice to stderr. Stable installations follow stable releases; development installations follow development prereleases. The update command verifies the release checksum before replacing the installed binary.

## SearchAgent

```text
conthunt agent-search start <brief> [--filters <json>] [--request-key <uuid>] --json
conthunt agent-search status <run-id> --json
conthunt agent-search get <run-id> --json
conthunt agent-search wait <run-id> --json
```

SearchAgent can issue multiple paid searches while exploring and refining a niche. Its completed result contains its final answer and selected ContHunt search IDs. Keep the generated request key when a start outcome is uncertain; retrying with that same key prevents a duplicate start.

## Searches and media

```text
conthunt search start <query> [--tiktok] [--instagram] [--youtube]
  [--tiktok-query <text>] [--tiktok-date <value>] [--tiktok-sort <value>] [--tiktok-region <CC>]
  [--instagram-query <text>] [--instagram-date <value>]
  [--youtube-query <text>] [--youtube-upload-date <value>] [--youtube-sort <value>] [--youtube-region <CC>]
  --json
conthunt search list --json
conthunt search status <search-id> --json
conthunt search get <search-id> --json
conthunt search wait <search-id> --json
conthunt download url <media-asset-id> --json
conthunt download file <media-asset-id> -o <path> --json
conthunt analyze start <media-asset-id> --json
conthunt analyze status <media-asset-id> --json
conthunt analyze get <media-asset-id> --json
conthunt analyze wait <media-asset-id> --json
```

Search defaults to TikTok, Instagram Reels, and YouTube Shorts when no platform flag is supplied. A platform-specific option implicitly selects its platform.

- TikTok always runs Keyword plus Top. Top is filtered to videos and the combined result is deduplicated. Defaults: `last-3-months`, `relevance`, `US`.
- Instagram defaults to `last-month`; valid dates are `last-week`, `last-month`, and `last-year`.
- YouTube is always Shorts with extras enabled. Defaults: `this_year`, `relevance`, `US`.
- Region is a provider proxy location, not proof of the video's origin.
- There is no result-count flag. Use the provider cursors returned by search results for pagination.

Controlled values:

```text
--tiktok-date yesterday|this-week|this-month|last-3-months|last-6-months|all-time
--tiktok-sort relevance|most-liked|date-posted
--instagram-date last-week|last-month|last-year
--youtube-upload-date today|this_week|this_month|this_year
--youtube-sort relevance|popular
```

## Boards and insights

```text
conthunt board list --json
conthunt board create <name> --json
conthunt board get <board-id> --json
conthunt board items <board-id> --json
conthunt board delete <board-id> --json
conthunt board add <board-id> <content-item-id> [<content-item-id> ...] --json
conthunt board remove <board-id> <content-item-id> --json
conthunt insights start <board-id> --json
conthunt insights status <board-id> --json
conthunt insights get <board-id> --json
conthunt insights wait <board-id> --json
```

## Deep research

```text
conthunt research start <brief> [--title <title>] [--board <id>] [--search <id>] --json
conthunt research send <chat-id> <message> --json
conthunt research status <chat-id> --json
conthunt research get <chat-id> --json
conthunt research wait <chat-id> --json
conthunt research watched <chat-id> [--search <search-id>] [--question <question-id>] [--cursor <cursor>] [--limit N] --json
conthunt research evidence <chat-id> <content-item-id> --json
conthunt research list --json
```

Research is multi-turn on one research chat ID. Do not send another turn while its status is active. `get` returns the completed answer and selected search metadata. `watched` pages through analyzed videos and can filter by finalized search or order by a research-question score. `evidence` returns the selected video's question-aware Markdown evidence.

## Trending

```text
conthunt trending youtube --json
conthunt trending tiktok --json
conthunt trending niches --json
```

Trending is an immediate GET, not a background job.

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Success; an active `status` is still successful |
| 1 | Job failure or unexpected API/transport error |
| 2 | Invalid command or flag |
| 3 | Authentication missing or rejected |
| 4 | Result or asset is not ready |
| 5 | Resource not found |
| 6 | Access denied |
