---
name: cron-schedule-planner
description: "Builds an overview of GitHub Actions `schedule` cron expressions across multiple repositories and helps spread CPU-intensive jobs (Docker Compose, Testcontainers, Kind/k3s, matrix builds) into less contended slots. Use when the user asks 'when do my cron actions run?', 'do my scheduled builds collide?', 'when should the Testcontainers build run?', or wants a cron schedule overview/distribution report across repos. Scans via `gh` (no local checkouts required) or local checkouts, converts UTC to a local timezone, classifies job intensity, and writes a Markdown report with an hourly histogram, collisions and concrete cron redistribution suggestions."
---

# Cron Schedule Planner

Collects GitHub Actions `on.schedule` cron expressions across repositories,
classifies how resource-intensive each workflow is, converts the UTC cron times
to a local timezone, and produces a Markdown report with an hourly histogram,
collisions and concrete redistribution suggestions.

Read-only: the script never edits workflows. Suggestions are applied only after
the user confirms.

## Instructions

### Step 1: Decide the repository scope

- Default: all repositories of the authenticated `gh` user (no local checkouts
  needed).
- `--owner <owner>` to scan a different owner.
- `--repo <owner/repo>` (repeatable) for an explicit list.
- `--local <dir>` to scan local checkouts instead of the GitHub API.

### Step 2: Run the script

```bash
bash scripts/cron-schedule-planner.sh
```

Common variants:

```bash
# Specific owner, Swiss local time, report in target/
bash scripts/cron-schedule-planner.sh --owner dboeckli --tz Europe/Zurich

# Local checkouts (no GitHub API)
bash scripts/cron-schedule-planner.sh --local ~/projects/referenzen

# A few explicit repos
bash scripts/cron-schedule-planner.sh --repo dboeckli/ai-agent-skills --repo dboeckli/camel-first
```

### Step 3: Present the results

The script prints the hourly histogram, collisions and suggestions, and writes
`target/cron-schedule-overview.md`. Summarise:

- how many repos / scheduled entries were found,
- the most crowded UTC hours (collisions),
- which high-intensity jobs sit in crowded hours.

### Step 4: Apply suggestions only after confirmation

The redistribution suggestions are heuristic (they move high-intensity jobs out
of crowded hours into empty ones, keeping the minute and day fields). Present
them as a diff and change workflow files **only after explicit confirmation**.
Never edit automatically.

## Options

| Option                | Meaning                                                         |
| --------------------- | --------------------------------------------------------------- |
| `--owner <owner>`     | GitHub owner to scan (default: authenticated user)              |
| `--repo <owner/repo>` | explicit repo (repeatable); disables owner scan                 |
| `--local <dir>`       | scan local checkouts under `<dir>` instead of GitHub            |
| `--tz <zone>`         | local timezone for the `Local` column (default `Europe/Zurich`) |
| `--limit <n>`         | max repos for the owner scan (default 200)                      |
| `--out <file>`        | Markdown report (default `target/cron-schedule-overview.md`)    |
| `--no-report`         | console only, no report file                                    |
| `--top <n>`           | max redistribution suggestions (default 5)                      |
| `--queue-stats`       | add observed queue time per UTC hour (via `gh run list`)        |
| `--runs <n>`          | max runs per repo for queue stats (default 50)                  |

## Output

`target/cron-schedule-overview.md`:

- **Scheduled workflows** table: repo, workflow, cron (UTC), UTC time, local
  time, frequency, intensity, evidence.
- **Runs per UTC hour** histogram (bars).
- **Runs per frequency / weekday**.
- **Collisions** — UTC hours with two or more scheduled runs.
- **Observed queue time per UTC hour** (with `--queue-stats`) — average and max
  wait between `createdAt` and `startedAt` across recent runs, as an empirical
  contention signal.
- **Redistribution suggestions** — high-intensity jobs in crowded hours moved
  to empty ones; with `--queue-stats` the empty hours with the lowest observed
  queue are preferred.

## Classification

Intensity is derived heuristically from the workflow content. See
`references/classification-and-timezones.md` for the exact patterns and the
UTC/timezone rules.

- **high** — Docker Compose, Testcontainers, service containers (`services:`),
  Kind/k3s cluster, matrix builds.
- **medium** — Maven/Gradle full builds, Docker image builds.
- **low** — lint/format/validate and other meta workflows.

## Examples

### Example 1: Are my scheduled builds colliding?

User says: "Do my scheduled GitHub Actions builds collide?"

Actions:

1. Run `bash scripts/cron-schedule-planner.sh --owner <owner>`
2. Report the crowded UTC hours and the high-intensity jobs in them
3. Point to `target/cron-schedule-overview.md`

Result: Collision overview across all repos with concrete evidence.

### Example 2: When should the Testcontainers build run?

User says: "When should I schedule the Testcontainers build?"

Actions:

1. Run the planner and locate the crowded hours (collisions)
2. Recommend one of the empty hours from the suggestions
3. Offer the concrete cron diff, apply only after confirmation

Result: A low-contention slot and a ready-to-apply cron change.

## Troubleshooting

### `gh: not found` or authentication error

The script needs an authenticated `gh`. Run `gh auth status`; if that fails, the
user must authenticate. Alternatively use `--local <dir>` with local checkouts.

### Empty report

No workflow in scope has an `on.schedule` entry. Check the repo scope
(`--owner`, `--repo`, `--local`) and that the workflows actually define
`schedule:` crons.

### Times look off by one hour

Cron is always UTC. Local times are computed for the current date, so
daylight-saving transitions can shift them by one hour. Re-run after a DST
change or adjust manually.

### `--queue-stats` shows little or no data

GitHub reports `startedAt` equal to `createdAt` for most runs (no recorded
queue), so the signal is sparse. Increase `--runs` to include older runs.
Treat large gaps with care: they can come from approval gates, concurrency
limits or manual runs, not only runner contention.
