# Claude Code Cost Guard — Stop Claude Code Burning Your Credits

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-blueviolet)](https://github.com/kml11kml/cost-guard)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/kml11kml/cost-guard)

**Claude Code has no spending cap and shows no cost estimate before a run.** Users are publicly reporting burned weekly allowances and surprise bills. Cost Guard is a free Claude Code skill that estimates cost *before* big runs, enforces daily and per-task spending caps from a local ledger, and brakes error loops after 3 identical failures — so a runaway job stops itself instead of emptying your quota.

## The problem — real reports, November 2026

- In [anthropics/claude-code#110395](https://github.com/anthropics/claude-code/issues/110395), simple condition checks were built as full AI runs every 5 to 10 minutes, about **40,000 tokens each**. No cost estimate, no check of the weekly limit, no spending cap, no brake on repeated failures (one failure loop ran **39 times**). The weekly allowance of **361.6M tokens ran out in 3.83 days**, followed by **$45.61 of paid overage**.
- In a separate November 2026 incident, a developer's Stop hook refused to let Claude stop until tests passed and CI was green. The hook blocked **1,314 stops**, the session made **2,736 model calls in about 3 hours**, and the burn was priced at about **$335** at API list rates.

Both were preventable: estimate first, cap the spend, brake the loop.

## Quick start

```bash
# Install with the skills CLI
npx skills add kml11kml/cost-guard

# Or copy it manually
mkdir -p ~/.claude/skills
cp -r cost-guard ~/.claude/skills/cost-guard
```

Then ask Claude Code to estimate before any big run — the skill does the rest.

## How it works

| Step | What happens |
| --- | --- |
| **Estimate** | `cost_guard.py estimate` prices a run from token counts before it starts. `estimate_recurring.py` prices a recurring job: runs per day, tokens per day, days until the weekly allowance runs out. |
| **Cap** | A local ledger tracks spend per day and per task. Defaults: **$10/day, $5/task**. `cost_guard.py check` blocks (exit code 2) when a cap would be exceeded. |
| **Brake** | `cost_guard.py fail` counts identical failures by signature. The **3rd identical failure in a day** stops the loop and asks the user what to do next. |
| **Report** | Example hooks show spend at session start and end, and gate Bash calls when the cap is hit. |

## Worked example — the #110395 case, priced before building

```bash
python3 scripts/estimate_recurring.py \
  --interval-min 10 --tokens-per-run 40000 --weekly-allowance 361600000
```

Output: 144 runs a day, 5.76M tokens a day, allowance gone in ~63 days on
paper — but the real incident burned it in 3.83 days, because retries,
failure loops and overlapping jobs piled on top of the floor estimate. That
gap is the whole point: the estimate is a floor, not a ceiling, and that is
exactly why the skill says **never build a recurring job without stating runs
per day, tokens per day, and days until the allowance runs out**.

## Install (full)

```bash
# 1. Copy the skill into Claude Code's skills directory
mkdir -p ~/.claude/skills
cp -r cost-guard ~/.claude/skills/cost-guard

# 2. Optional: set your caps (defaults: $10/day, $5/task, loop limit 3)
mkdir -p ~/.cost-guard
cp ~/.claude/skills/cost-guard/config.example.json ~/.cost-guard/config.json
# then edit ~/.cost-guard/config.json

# 3. Optional: install the example hooks
# Merge hooks/hooks.json into ~/.claude/settings.json under the "hooks" key.
# Do NOT overwrite your existing settings.json -- merge the "hooks" object.
# Check what is active with:
python3 ~/.claude/skills/cost-guard/scripts/cost_guard.py config
```

## Usage

```bash
G=~/.claude/skills/cost-guard/scripts/cost_guard.py

# Estimate a run before starting it
python3 $G estimate --model sonnet --input 1000000 --output 500000

# Estimate a recurring job before building it
python3 ~/.claude/skills/cost-guard/scripts/estimate_recurring.py \
  --interval-min 10 --tokens-per-run 40000 --weekly-allowance 361600000

# Record a finished run (do this after every task)
python3 $G record --model sonnet --input 800000 --output 120000 --task "refactor-auth"

# See today's spend
python3 $G status
python3 $G status --task "refactor-auth"

# Gate an expensive step (exit 2 = blocked)
python3 $G check --task "refactor-auth" --est-cost 2.50

# Record a failure; the 3rd identical failure in a day brakes the loop
python3 $G fail --signature "tests-fail:auth" --task "refactor-auth"
```

## Why this skill

- **It answers a real, public complaint** — not a hypothetical. The incidents above are linked GitHub issues and reports from November 2026.
- **Stdlib only, no dependencies** — two Python scripts, one hooks file, plain JSON config. Nothing to install, nothing phoning home.
- **It says what it cannot do** — see the limits below. No fake savings figure, no invented users, no testimonials.

## FAQ

**Does it read my real Anthropic bill?**
No. It works off a local ledger of token counts you record. If you never record a run, the ledger stays at $0 while the real bill grows. See the limits below.

**Can a hook stop a model API call?**
No. Claude Code hooks gate tool calls and report at session start/end. They cannot intercept a model call or read token usage from the API. The guard blocks the *next tool step* and the *next run* — it does not reach inside an in-flight call.

**Can it guarantee I save money?**
No. It reduces surprise bills by forcing an estimate, a cap, and a loop brake before the expensive work. It never executes a payment and guarantees no saving.

**Is it financial advice?**
No. It is a cost-control tool, not financial advice.

## Honest limits — read before relying on it

- **Estimates, not billing.** The guard works off a local ledger of token counts you record. It cannot see your real Anthropic bill, plan quota, or usage limits.
- **Hooks cannot cap a model call.** Claude Code hooks gate tool calls and report at session start/end. They cannot intercept or stop a model API call, and they cannot read token usage from the API.
- **Prices change.** The scripts use API list prices from November 2026. Verify current pricing and update `~/.cost-guard/config.json` when they change. Cache reads are priced at 10% of the input price, which is an approximation.
- **A Stop hook must never block stopping unconditionally.** The $335 burn happened because a Stop hook kept sending Claude back. If a hook checks completion, read `stop_hook_active` from the hook input and exit 0 when it is true. The example Stop hook in this skill only prints a status report and never blocks.
- **No guarantee.** This skill reduces surprise bills. It does not guarantee any saving, and it never executes a payment.

## Files

| File | What it is |
| --- | --- |
| `SKILL.md` | The skill rules |
| `skill.yaml` | Skill metadata (name, version, description) |
| `README.md` | This file |
| `LICENSE` | MIT |
| `scripts/cost_guard.py` | Ledger + caps + loop brake (stdlib only) |
| `scripts/estimate_recurring.py` | Recurring-job estimator (stdlib only) |
| `hooks/hooks.json` | Example Claude Code hooks |
| `config.example.json` | Example caps and pricing |

## Custom work

Need this fitted to your setup — custom caps, team ledger, CI guardrails, or a full Claude Code workflow with cost controls? Custom skill, plugin, and MCP builds are available as a service. Open an issue in this repo with what you need and the budget range; quotes are $150–500 per project, 50% upfront in USDT, rest on delivery.

## Version

v0.1.0 — first version, 2026-11-21. Not financial advice. No verified savings figure; the incidents above are public bug reports, not this skill's results. No fake testimonials, no invented users.
