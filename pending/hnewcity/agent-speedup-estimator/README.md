# agent-speedup-estimator

For installation, language switching and the full reference, see the [project README](https://github.com/hnewcity/agent-speedup-estimator#readme). This folder is the self-contained skill package; keep `scripts/` and `data/` with `SKILL.md` when installing it.

Is your computer slowing down your coding agents, and would a new one help?

This tool reads the Claude Code and Codex transcripts already on your disk, splits agent working time into **model time** (remote, unchanged by hardware) and **local tool time** (builds, tests, installs, scripts), and projects how much faster the local part would run on a faster machine.

It works as an agent skill (see `SKILL.md`) or as a plain command line tool.

## Usage

```bash
python scripts/agent_speedup.py --out ./agent-speedup-report
python scripts/agent_speedup.py --days 30 --target "Apple M4 Pro" --lang en
python scripts/agent_speedup.py --list-cpus
```

Output: `report.md`, a self-contained `report.html` (charts, table views, no network access), and `summary.json`.

Requirements: Python 3.9+, standard library only. Reading Codex sessions that Codex has compressed (`.jsonl.zst`) needs Python 3.14+ or `pip install zstandard`.

## What it reads

| Agent | Location | Timing source |
|---|---|---|
| Claude Code | `~/.claude/projects/**/*.jsonl` (or `$CLAUDE_CONFIG_DIR`) | message timestamps, `tool_use` to `tool_result` gaps |
| Codex | `~/.codex/sessions` and `archived_sessions` (or `$CODEX_HOME`) | `item_completed` start and end times, per-turn `task_complete` |

Transcript records are parsed locally in memory, and commands are inspected for classification. Prompts, replies, raw commands, transcript paths and session IDs are excluded from report output. Reports include activity dates and hardware details. Privacy tests cover both adapters using synthetic records.

## How the estimate works

1. Each tool call is placed in a category (tests, build, install, scripts, git, file access, network, waiting, and so on).
2. Overlapping calls share wall time within each session. Time beyond a per-command cap stays fixed in the conservative and expected scenarios; the optimistic scenario scales it too. Concurrent sessions are summed.
3. Each category has a CPU share and a disk share that scale with hardware, given as conservative, expected and optimistic priors in `data/sensitivity.json`.
4. Speedup for a category is `1 / ((1 - cpu - disk) + cpu / s_cpu + disk / s_disk)`, where `s_cpu` blends the single-core and multi-core Geekbench 6 ratios by how parallel the category is.
5. Estimated model time is held fixed. This assumes remote model inference and local tool execution; it does not model local LLMs, GPU upgrades or remote build machines.

The sensitivity shares are assumptions. Change them in `data/sensitivity.json`, or pass your own file with `--sensitivity`.

## Data

`data/cpu_scores.json` lists Geekbench 6 scores with a source URL per entry. A CPU with no readable score is left out of the table, never estimated there.

The baseline for your current computer is resolved without asking you:

1. An exact match in the score table.
2. A documented stand-in chip from `data/proxies.json`.
3. An estimate from your thread count (`fallback` in `data/proxies.json`).

Options 2 and 3 are flagged in the report, and the conservative and optimistic cases shift the baseline in both directions to cover the error. If you know your real scores, `--current-gb6 SINGLE MULTI` replaces all of this. A target chip that is not in the table can be added with `--custom-target NAME SINGLE MULTI`.

## Tests

```bash
python -m unittest discover -s tests
```
