---
name: turbo-doctor
description: "Diagnose and fix broken Goldsky Turbo pipelines interactively. Triggers on: pipeline in error state, stuck starting, connection refused, not getting data, duplicate rows, missing fields, slow backfill, or any named pipeline misbehaving. Runs logs/status commands, identifies root cause, and offers fixes. For CLI syntax or error pattern lookup without an active problem, use /turbo-operations instead."
---

# Pipeline Doctor

## Boundaries

- Diagnose and fix EXISTING pipeline problems interactively.
- Do not build new pipelines — that belongs to `/turbo-builder`.
- Do not serve as a command reference. If the user only needs CLI syntax or error pattern lookup, use the `/turbo-operations` skill instead.

Systematically identify and resolve pipeline issues by following a structured diagnostic workflow.

## Mode Detection

Before running any commands, check if you have the `Bash` tool available:

- **If Bash is available** (CLI mode): Execute commands directly and parse output.
- **If Bash is NOT available** (reference mode): Output commands for the user to run. Ask them to paste the output back so you can analyze it and provide recommendations.

## Diagnostic Workflow

Follow these steps in order. Do not skip steps — each builds on the previous one.

### Step 1: Verify Authentication

Run `goldsky project list 2>&1` to check login status.

- **If logged in:** Note the current project and continue.
- **If not logged in:** Tell the user they need to authenticate. Use the `/auth-setup` skill for guidance. Do not proceed until auth is confirmed.

### Step 2: Identify the Pipeline

Run `goldsky turbo list` to show all pipelines.

Ask the user which pipeline they want to diagnose. If they already named one, confirm it exists in the list.

Note the pipeline's current status (running, paused, error, completed, starting).

### Step 3: Analyze Pipeline Status

Based on the status:

- **running** — Pipeline is active. Check if the issue is data quality, latency, or unexpected behavior. Proceed to Step 4.
- **error** — Pipeline has failed. This is the most common case. Proceed to Step 4 for log analysis.
- **paused** — Pipeline was manually paused. Ask if they want to resume it.
- **starting** — Pipeline is initializing. Ask how long it's been starting. If >10 minutes, check logs.
- **completed** — Job-mode pipeline finished. Ask what the expected vs actual behavior was.

### Step 4: Examine Logs

Run `goldsky turbo logs <pipeline-name> --tail 100 2>&1` to get recent logs.

Analyze the output for known error patterns. Reference the error patterns in the `/turbo-operations` skill, including:

- **Connection errors** — sink unreachable, auth failed, timeout
- **Schema errors** — column mismatch, type mismatch, missing columns
- **Resource errors** — OOM, disk full, rate limiting
- **Data errors** — deserialization failures, invalid block ranges
- **Configuration errors** — invalid YAML, unknown dataset, bad transform

### Step 5: Check Secrets (if applicable)

If logs show connection or authentication errors:

Run `goldsky secret list` to verify all required secrets exist.

Cross-reference with the pipeline YAML if available. Use the `/secrets` skill for guidance on creating or updating secrets.

### Step 6: Provide Diagnosis

Present your findings in this format:

```
## Diagnosis

**Pipeline:** [name]
**Status:** [status]
**Issue:** [one-line summary]

**Root cause:**
[Detailed explanation of what's wrong]

**Evidence:**
- [Log line or observation 1]
- [Log line or observation 2]

**Recommended fix:**
1. [Step 1]
2. [Step 2]

**Prevention:**
[How to avoid this in the future]
```

### Step 7: Offer to Fix

If the fix involves CLI commands (restart, update secrets, redeploy), offer to execute them. Always confirm with the user before making changes.

Common fixes:
- **Restart:** `goldsky turbo restart <name>` (or `--clear-state` for a fresh start)
- **Update secret:** `goldsky secret create <name>` and let the CLI prompt for the value (secrets are immutable — recreate to update). Avoid passing the credential inline via `--value`, which stores it in shell history; see the `/secrets` skill. Never echo a revealed secret back into the conversation.
- **Redeploy:** `goldsky turbo delete <name>` then `goldsky turbo apply <file.yaml>`
- **Resume:** `goldsky turbo resume <name>` (for paused pipelines)

## Important Rules

- Never guess at the problem. Always check logs and status first.
- If you're unsure, say so and suggest what additional information would help.
- For job-mode pipelines: remember they cannot be paused, resumed, or restarted — only deleted and redeployed.
- Always ask before running destructive commands (delete, restart --clear-state).
- If the issue is beyond what the CLI can diagnose, suggest contacting Goldsky support with the specific error messages.

## Related

- **`/turbo-operations`** — CLI commands, lifecycle operations, and error pattern reference
- **`/turbo-builder`** — Build and deploy new pipelines
- **`/turbo-pipelines`** — YAML configuration and architecture reference
- **`/secrets`** — Manage sink credentials
