---
name: groove-utilities-stats
description: "Quantified compound-loop dashboard: lessons captured vs graduated, adherence streaks, and task velocity. Use to see whether the workflow is actually compounding."
license: MIT
allowed-tools: Read Glob Grep Bash(git:*) Bash(beans:*) Bash(gh:*) Bash(linear:*) Bash(jq:*) Bash(python3:*) Bash(chmod:*) AskUserQuestion
metadata:
  author: andreadellacorte
  bash: true
---

<!-- groove:managed — do not edit; changes will be overwritten by groove update -->

# groove-utilities-stats

Use $ARGUMENTS to specify the period: `week` (default), `month`, or `all`.

## Bash fast-path

This skill has a bash script at `scripts/stats.sh`. Run it directly for faster, model-free execution:

```bash
bash .agents/skills/groove-utilities-stats/scripts/stats.sh week
```

(Pass `week`, `month`, or `all` to match $ARGUMENTS.) If the script exits 0, report its stdout and stop — do not continue with the steps below. If it exits non-zero, continue with the markdown steps (exit 3 means it printed the local metrics but the `linear`/`github` task counts still need to be computed below; exit 1 means no `.groove/`).

## Outcome

A read-only dashboard is printed to the conversation quantifying compound-loop health for the period: the **compound funnel** (lessons captured vs graduated), **adherence** (daily-log coverage, streak, rollup freshness, ratings), and **velocity** (task open/closed, commits). No files are written. This answers "is the workflow compounding / am I keeping the rhythm" — for qualitative patterns, it points to `/groove-utilities-memory-retrospective`.

## Acceptance Criteria

- Compound funnel shown: lessons captured (total + in period), graduated (total + in period), graduation rate
- Adherence shown: daily-log coverage over the last `memory.review_days` business days, current streak, weekly/monthly rollup freshness, ratings count + average
- Velocity shown: task open/closed counts (if a task backend is configured) and commit count in the period
- Output goes to the conversation only; nothing is written
- Absent data sources are skipped with sensible "n/a"/"NA" placeholders rather than errors

## Steps

(Model fallback — the bash fast-path above does this deterministically. Reproduce the same output format.)

1. Memory path is always `.groove/memory/`. If `.groove/` is absent, stop with an install hint.

2. Read `.groove/index.md` frontmatter: `tasks.storage` (backend; legacy key `tasks.backend`) and `memory.review_days` (default 5).

3. Determine date range from $ARGUMENTS: `week` = last 7 days, `month` = last 30 days, `all` = everything. Call the start `<since>`.

4. **Compound funnel**:
   - Captured: count `## YYYY-MM-DD` dated entries across `.groove/memory/learned/*.md` (exclude `signals.md`) — total, and those with date ≥ `<since>`.
   - Graduated: count `[graduated YYYY-MM-DD]` markers across the same files — total, and those ≥ `<since>`.
   - Graduation rate = graduated_total / captured_total as a percentage (`n/a` if none captured).

5. **Adherence**:
   - Daily-log coverage: of the last `review_days` business days (Mon–Fri, ending today), how many have `.groove/memory/daily/YYYY-MM-DD.md`.
   - Streak: consecutive most-recent business days (back from today) that have a daily log; stop at the first gap.
   - Rollup freshness: `weekly` is `fresh` if a `.groove/memory/weekly/<ISO-year>-W<ISO-week>.md` exists for the current or previous week, else `stale`; `monthly` likewise for `.groove/memory/monthly/YYYY-MM.md`.
   - Ratings: parse `.groove/memory/learned/signals.md` table rows (`| YYYY-MM-DD | N/5 | note |`) with date ≥ `<since>`; report count and average (and a `▁▂▄▆█` sparkline if ≥ 3).

6. **Velocity**:
   - Commits: `git log --oneline --since=<since>` count.
   - Tasks, by `tasks.storage`:
     - `beans`: open = `beans list --json --no-status completed --no-status scrapped | jq length`; closed = `--status completed` + `--status scrapped`; best-effort open mistakes/promises = count of non-terminal children under the "Mistakes"/"Promises" epics.
     - `linear`: via the linear CLI/MCP — assigned issues grouped into open vs done.
     - `github`: `gh issue list --assignee @me --state all` grouped into open vs closed.
     - `none`: omit task counts (show commits only).

7. Print the dashboard in the **Output format** below.

## Output format

```
## Groove Stats — <period> (<start> to <today>)

### 🔁 Compound funnel
Lessons captured: <N> (<n> this <period>)   Graduated: <G> (<g> this <period>)
Graduation rate: <pct>

### 📿 Adherence
Daily logs: <x>/<review_days> business days   Streak: <s> days
Rollups: weekly <fresh|stale>, monthly <fresh|stale>
Ratings: <c> in period | avg <a>/5  <sparkline>

### 🚀 Velocity
Tasks: <open> open / <closed> closed   Commits: <k> in period
Open: <m> mistakes, <p> promises

_For qualitative patterns and learnings, run `/groove-utilities-memory-retrospective`._
```

## Constraints

- Read only — never write to any file (no memory, no AGENTS.md, no config).
- Skip any absent data source with a one-line `n/a`/`NA` rather than erroring; parse tables and dates defensively.
- Paths are hardcoded under `.groove/memory/` (not configurable), consistent with the rest of groove.
- This skill complements `/groove-utilities-memory-retrospective` (qualitative reflection) — do not duplicate its narrative; cross-link it.
