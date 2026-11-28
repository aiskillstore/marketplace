---
name: cost-guard
description: Stop Claude Code burning your credits — cost estimates before big runs, daily and per-task spending caps, error-loop brake.
---

# Cost Guard — Spending Caps and Loop Brakes for Claude Code

Use this skill whenever a task could get expensive: long runs, many files, subagents, scheduled or recurring jobs, or anything left running unattended. Never start an expensive run without an estimate and a cap.

Why this exists: users are publicly reporting Claude Code burning their credits with no cap and no estimate. In anthropics/claude-code#110395 a weekly allowance of 361.6M tokens ran out in 3.83 days plus $45.61 overage, because simple condition checks were built as full AI runs every 5 to 10 minutes with no cost estimate, no cap, and a failure loop that repeated 39 times. In a separate November 2026 incident a Stop hook that refused to let Claude stop burned about $335 in 3 hours across 2,736 model calls. Both were preventable with the rules below.

## Estimate before a big run

- Estimate the cost before any big run and show the user the number.
- For a one-off run use `scripts/cost_guard.py estimate --model sonnet --input N --output N`.
- For a recurring or scheduled job use `scripts/estimate_recurring.py --interval-min M --tokens-per-run N --weekly-allowance W`.
- Treat the recurring estimate as a floor, not a ceiling: retries, failure loops and overlapping jobs only push real spend above it.
- Wait for the user's yes when the estimate is above $2 or above their cap.
- Never build a recurring job without stating runs per day, tokens per day, and days until the allowance runs out.

## Set caps first, then record

- Set a daily cap and a per-task cap before the work starts. Defaults are $10 a day and $5 a task; change them in `~/.cost-guard/config.json` or with `COST_GUARD_DAILY_CAP` and `COST_GUARD_TASK_CAP`.
- Record every finished run with `scripts/cost_guard.py record --model M --input N --output N --task LABEL`.
- Check the cap before an expensive step with `scripts/cost_guard.py check --task LABEL --est-cost X`. A blocked check means stop and ask the user, not find a way around it.
- Show `scripts/cost_guard.py status` at the start and the end of a session.

## Brake error loops

- Give every repeated failure a stable signature and record it with `scripts/cost_guard.py fail --signature "area:what-failed"`.
- After 3 identical failures in one day, stop. Report what failed, what changed between tries, and ask the user what to do next.
- Never retry the same failing command without changing something first.
- Never write a Stop hook that blocks Claude from stopping unconditionally. A Stop hook that sends Claude back into the loop is how the $335 burn happened: each re-entry re-read the whole context, and the built-in 8-block limit resets whenever a tool call happens in between. If a hook must check completion, read `stop_hook_active` from the hook input and exit 0 when it is true.

## Ask before expensive operations

- Ask before anything that spends a lot at once: full-repo refactors, multi-agent workflows, long headless runs, and any job that runs while the user is away.
- Prefer the cheaper model when the job allows it. Say which model you picked and why.
- Keep the user informed while a long job runs: cost so far, cap remaining, and what happens next.

## Honest limits

- The guard works off a local ledger of token counts you record. It cannot see real billing, plan quotas, or usage limits.
- Claude Code hooks cannot cap a model API call. They can only gate tool calls and report at session start and end.
- All prices in the scripts are API list prices from November 2026. Verify current pricing before relying on them and update `config.json` when they change.
- This skill reduces surprise bills. It does not guarantee any saving and it never executes a payment.
