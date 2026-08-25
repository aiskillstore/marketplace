---
name: groove-utilities-memory-mistakes
description: "Log a workflow mistake, fix its root cause, and graduate the lesson to learned memory. Use when the agent makes an error you want to prevent recurring."
license: MIT
allowed-tools: Read Write Edit Glob Grep Bash(git:*) Bash(beans:*) AskUserQuestion
metadata:
  author: andreadellacorte
---

# groove-utilities-memory-mistakes

Use $ARGUMENTS as the mistake description if provided (e.g. `--list` to show open incidents only).

## Outcome

The workflow mistake is logged, its root cause is fixed in the relevant memory or learned file, and the lesson is graduated to `.groove/memory/learned/<topic>.md`. The incident is closed.

## Acceptance Criteria

- Incident is recorded with root cause and fix
- Permanent fix applied to `.groove/memory/learned/<topic>.md`
- Incident marked resolved

## Task backend

Read `tasks.backend` from `.groove/index.md`. Incidents are tracked as tasks in the configured backend. If no task backend is configured (`tasks.backend: none`), tell the user to run `/groove-utilities-task-install` first.

Incidents are stored as bugs under a shared "Groove Memory" milestone → "Mistakes" epic.

### Ensure parent hierarchy

Before any operation, resolve or create the parent epic:

1. Find or create the **Groove Memory** milestone:
   - `beans list -t milestone --search "Groove Memory" -q` — if non-empty, use first ID; otherwise `beans create "Groove Memory" -t milestone`
2. Find or create the **Mistakes** epic under that milestone:
   - `beans list -t epic --parent <milestone-id> --search "Mistakes" -q` — if non-empty, use first ID; otherwise `beans create "Mistakes" -t epic --parent <milestone-id>`

### `--list`

1. Resolve `<parent-id>`
2. `beans list --parent <parent-id> -t bug -s in-progress`
3. Display as numbered list: `1. [<id>] <title>`
4. If empty: print "No open incidents."

### Log and resolve an incident

1. Resolve `<parent-id>`
2. Get description from $ARGUMENTS or ask: "What mistake did I make?"
3. Ask: "Root cause — why did it happen?" (propose from context; user confirms)
4. Ask: "What fix should be applied?" (propose; user confirms)
5. `beans create "<description>" -t bug --parent <parent-id> -s in-progress`
6. Apply the fix immediately (edit the relevant file)
7. Ask: "Which learned topic? (e.g. `anti-patterns`, `tools`)" — suggest based on root cause
8. Append lesson to `.groove/memory/learned/<topic>.md` under `## YYYY-MM-DD` heading
9. `beans update <id> -s completed`
10. Report: "Incident resolved → learned/<topic>.md"

## Constraints

- Read `tasks.backend` from `.groove/index.md`; memory path is always `.groove/memory/`
- Requires a configured task backend — if `tasks.backend: none`, prompt user to install one
- Never auto-create incidents without user confirmation
- Root cause is required before resolving — do not skip the audit step
- Parent hierarchy is idempotent — always check before creating
- If the fix targets a `skills/` file: note that `skills/` is managed by groove:update; redirect fix to `learned/anti-patterns.md`
