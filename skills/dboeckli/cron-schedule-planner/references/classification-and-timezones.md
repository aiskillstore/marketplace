# Classification and timezone rules

Detail for `cron-schedule-planner.sh`. The script keeps these rules in one
place so they can be reviewed and adjusted.

## Intensity heuristic

Patterns are checked in priority order; the first match wins and is reported as
the `Nutzt` (evidence) column.

| Intensity | Patterns (case-insensitive)                                                                                                                                       |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| high      | `docker compose` / `docker-compose` / `compose.yaml`; `testcontainers` / `withTestcontainers`; `services:` (service containers); `kind-action` / `k3s`; `matrix:` |
| medium    | `maven` / `mvn ` / `gradle`; `docker build` / `buildx`                                                                                                            |
| low       | everything else (lint, format, validate, meta workflows)                                                                                                          |

Notes:

- A `maven-build.yml` that also starts a Kind cluster is **high**, not medium —
  the priority order puts cluster/container patterns first.
- `services:` matches a job-level service container block and may also match
  comments; it is a heuristic, not a parser.
- Matrix builds are treated as high because they fan out to multiple parallel
  runners.

## Cron source

- Only `on.schedule[].cron` entries are collected.
- Multiple crons per workflow are supported (one row each).
- If `on.schedule[].timezone` is set, it is used as the source zone; otherwise
  the cron is treated as UTC (GitHub's default).

## Timezone conversion

- A cron time is converted via a reference date (today) to compute the current
  UTC offset: source zone → epoch → target zone.
- Default target zone is `Europe/Zurich`.
- Cron has no DST awareness; a fixed local offset for the current date is shown.
  Around DST transitions the local time can be off by one hour.

## Histogram and collisions

- The histogram counts scheduled entries per **UTC hour** (00–23), regardless
  of weekday.
- A collision is a UTC hour with **two or more** scheduled runs.
- Redistribution suggestions move **high-intensity** jobs out of crowded hours
  into hours with zero runs, keeping the minute and day fields unchanged.
- Suggestions are heuristic and do not model GitHub's shared runner pool;
  they reduce the user's own schedule density and avoid obvious stacking.

## Observed queue time (`--queue-stats`)

- For each repo, `gh run list --limit <runs> --json createdAt,startedAt` is
  queried and the wait `startedAt - createdAt` is aggregated per UTC hour.
- GitHub usually records `startedAt == createdAt`, so only runs that actually
  waited contribute; the signal is sparse. Increase `--runs` to reach further
  back.
- Large gaps can also come from approval gates, concurrency groups or manual
  runs — not only runner contention. Treat the numbers as a hint.
- When queue data exists, candidate (empty) hours are ordered by lowest average
  queue time before redistribution suggestions are produced.
- There is no public API for GitHub's shared runner-pool utilisation; queue
  time of your own runs is the only empirical proxy available.
