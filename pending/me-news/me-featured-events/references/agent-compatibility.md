# Agent compatibility

Use the bundled Node.js scripts as the source of truth on every agent. The scripts require Node.js 18+, use only built-in modules, and do not require an LLM.

## Shared behavior

All agents must use the same state file and commands:

```bash
node <skill-dir>/scripts/init-subscription.mjs --state <workspace>/memory/me-featured-events.json [--types ai,web3] [--regions hong-kong]
node <skill-dir>/scripts/poll-new-events.mjs --state <workspace>/memory/me-featured-events.json
node <skill-dir>/scripts/record-delivery.mjs --state <workspace>/memory/me-featured-events.json --status success
node <skill-dir>/scripts/record-delivery.mjs --state <workspace>/memory/me-featured-events.json --status failed --error "delivery error"
node <skill-dir>/scripts/daily-upcoming.mjs --state <workspace>/memory/me-featured-events.json
```

- Non-empty stdout is the message to deliver verbatim.
- Empty stdout means no message. Do not replace it with a status update.
- Non-zero exit means failure. Surface the stderr summary and do not claim success.
- After non-empty poll output is delivered, record `success` only when the delivery tool confirms success. Record `failed` on a confirmed failure. An unknown result must remain pending and be retried.
- `daily-upcoming.mjs` does not advance the changes cursor and does not use delivery feedback.
- Never let two poll processes write the same state file concurrently.

## CLI validation

- Unknown options and duplicate options are errors; do not silently ignore them.
- `--limit` must be an integer from 1 through 100.
- `--hours` must be an integer from 1 through 8784.
- `--start-date` and `--end-date` must use `YYYY-MM-DD`, represent real calendar dates, appear together, be ordered, and span at most 366 inclusive days.
- Do not combine `--hours` with a date range.
- `--timezone` must be a valid IANA time-zone identifier.

## Recoverable initialization

`init-subscription.mjs` persists the `/changes` baseline with `initialization_status: pending` before requesting upcoming events. If a later step fails, rerun the same command. It resumes the saved cursor instead of requesting a newer baseline. Do not delete the state file or change types, regions, or timezone while initialization is pending.

## Scheduler adapters

### OpenClaw

Schedule `poll-new-events.mjs` every 5 minutes and `daily-upcoming.mjs` at 10:00 in `Asia/Shanghai`. The incremental job must inspect the message-tool result and run `record-delivery.mjs` with the matching status. Do not use a plain Command Cron that automatically forwards stdout but cannot run a post-delivery success or failure command.

### Hermes Agent

Use an agent Cron for the incremental job so it can inspect delivery success and record feedback. A native no-agent/script Cron is acceptable only when it supports a post-delivery hook with a reliable status. The daily job may remain a no-agent/script Cron.

### Codex

For Codex Automations, instruct the incremental task to run the poll, publish non-empty stdout, inspect the publication result, and record delivery feedback. For Codex CLI or an operating-system scheduler, use a delivery wrapper that returns a reliable exit status before calling the feedback script.

### Claude Code

Claude Code CLI is not a persistent scheduler. Use a system scheduler or CI workflow with a delivery command whose result controls `record-delivery.mjs`. Do not acknowledge delivery merely because the poll command succeeded.

## Installation locations

The portable package is the directory containing `SKILL.md`; install or link it into the agent's normal Skill directory:

- Codex: `~/.codex/skills/me-featured-events`
- Claude Code: `~/.claude/skills/me-featured-events`
- Hermes Agent: `~/.hermes/skills/me-featured-events`
- OpenClaw: its configured workspace or shared skills directory

Do not copy channel credentials into the Skill directory or state file.
