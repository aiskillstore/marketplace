---
name: managing-task-lifecycle
description: Use when starting, pausing, completing, or transitioning task status in the development workflow.
---

# PairCoder Task Lifecycle

## Decision Tree: Which Command to Use?

```
Is Trello connected? (check: bpsai-pair trello status)
│
├── YES → Use `ttask` commands (primary)
│   ├── Start:    bpsai-pair ttask start TRELLO-XX
│   ├── Complete: bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"
│   └── Block:    bpsai-pair ttask block TRELLO-XX --reason "..."
│
└── NO → Use `task update` commands
    ├── Start:    bpsai-pair task update TASK-XXX --status in_progress
    ├── Complete: bpsai-pair task update TASK-XXX --status done
    └── Block:    bpsai-pair task update TASK-XXX --status blocked
```

**Rule of thumb:** If you see TRELLO-XX IDs, use `ttask`. If you only have TASK-XXX IDs, use `task update`.

## CRITICAL: Always Use CLI Commands

Task state changes MUST go through the CLI to trigger hooks (Trello sync, timers, state updates).

**Never** just edit task files or say "marking as done" - run the command.

## Automatic Hooks

When you change task status via CLI, these hooks fire automatically:

### On `task update --status in_progress`:
- `start_timer` - Begins time tracking
- `sync_trello` - Moves card to "In Progress"
- `update_state` - Updates state.md current focus

### On `task update --status done`:
- `stop_timer` - Stops timer, records duration
- `record_metrics` - Records token usage and costs
- `record_velocity` - Tracks sprint velocity
- `sync_trello` - Moves card to "Deployed/Done"
- `update_state` - Updates state.md
- `check_unblocked` - Identifies newly unblocked tasks

### On `task update --status blocked`:
- `sync_trello` - Moves card to "Issues/Tech Debt"
- `update_state` - Updates state.md

**You don't need to manually update Trello, start/stop timers, or refresh state.md - hooks handle it.**

## Starting a Task

```bash
bpsai-pair task update TASK-XXX --status in_progress
```

This will:
- Update task file status
- Move Trello card to "In Progress" list
- Start timer (when implemented)
- Update state.md current focus

## During Work (Progress Updates)

```bash
bpsai-pair ttask comment TASK-XXX "Completed API endpoints, starting tests"
```

This adds a comment to the Trello card without changing status. Use for:
- Milestone updates
- Noting decisions
- Progress visibility for team

## Completing a Task

### For Trello Projects (Recommended)

Use `ttask done` - it handles everything in one command:

```bash
bpsai-pair ttask done TRELLO-XX --summary "What was accomplished" --list "Deployed/Done"
```

This single command will:
- ✓ Move Trello card to "Deployed/Done" list
- ✓ Auto-check ALL acceptance criteria items
- ✓ Add completion summary to card
- ✓ Update local task file status
- ✓ Trigger all completion hooks (timer, metrics, state.md)

**You do NOT need to also run `task update --status done`** - `ttask done` handles it.

### For Non-Trello Projects

Use `task update`:

```bash
bpsai-pair task update TASK-XXX --status done
```

This will:
- Update task file status
- Trigger completion hooks (timer, metrics, state.md)

### Common Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|------------------|
| Using only `task update` on Trello projects | Doesn't check AC on Trello card | Use `ttask done` instead |
| Using both commands on Trello projects | Unnecessary duplication | Just use `ttask done` |
| Using `ttask` on non-Trello projects | Commands won't work | Use `task update` |

## Quick Reference

### Local Task Commands (`task`)

Use these for status changes - they trigger all hooks.

| Action | Command |
|--------|---------|
| Start task | `bpsai-pair task update TASK-XXX --status in_progress` |
| Complete task | `bpsai-pair task update TASK-XXX --status done` |
| Block task | `bpsai-pair task update TASK-XXX --status blocked` |
| Show next task | `bpsai-pair task next` |
| Auto-assign next | `bpsai-pair task auto-next` |
| List all tasks | `bpsai-pair task list` |
| Show task details | `bpsai-pair task show TASK-XXX` |

### Trello Card Commands (`ttask`)

Use these for direct Trello operations.

| Action | Command |
|--------|---------|
| List Trello cards | `bpsai-pair ttask list` |
| Show card details | `bpsai-pair ttask show TRELLO-XX` |
| Start card | `bpsai-pair ttask start TRELLO-XX` |
| **Complete card** | `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"` |
| Check acceptance item | `bpsai-pair ttask check TRELLO-XX "item text"` |
| Add progress comment | `bpsai-pair ttask comment TRELLO-XX "message"` |
| Block card | `bpsai-pair ttask block TRELLO-XX --reason "why"` |
| Move card to list | `bpsai-pair ttask move TRELLO-XX "List Name"` |

### When to Use `task` vs `ttask`

**For Trello-connected projects (preferred):**

| Scenario | Command |
|----------|---------|
| Starting a task | `ttask start TRELLO-XX` |
| Progress updates | `ttask comment TRELLO-XX "message"` |
| Completing a task | `ttask done TRELLO-XX --summary "..." --list "Deployed/Done"` |
| Blocking a task | `ttask block TRELLO-XX --reason "..."` |

**For non-Trello projects:**

| Scenario | Command |
|----------|---------|
| Starting a task | `task update TASK-XXX --status in_progress` |
| Completing a task | `task update TASK-XXX --status done` |
| Blocking a task | `task update TASK-XXX --status blocked` |

**Key insight:** `ttask` commands handle both Trello AND local state. You don't need to run `task update` after `ttask done` - it handles everything.

## Task Status Values

| Status | Meaning | Trello List |
|--------|---------|-------------|
| `pending` | Not started | Backlog / Planned |
| `in_progress` | Currently working | In Progress |
| `blocked` | Waiting on something | Issues / Blocked |
| `review` | Ready for review | Review |
| `done` | Completed | Deployed / Done |

## Workflow Checklist

### When Starting a Task
1. Run: `bpsai-pair task update TASK-XXX --status in_progress`
2. Verify Trello card moved
3. Read the task file for implementation plan
4. Begin work

### During Work
1. Add progress comments: `bpsai-pair ttask comment TASK-XXX "status update"`
2. Commit frequently with task ID in message

### When Completing a Task

**For Trello projects:**
1. Ensure tests pass: `pytest -v`
2. Find card ID: `bpsai-pair ttask list`
3. Complete: `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"`
4. Update state.md with what was done
5. Commit changes with task ID in message

**For non-Trello projects:**
1. Ensure tests pass: `pytest -v`
2. Complete: `bpsai-pair task update TASK-XXX --status done`
3. Update state.md with what was done
4. Commit changes with task ID in message

## Validation Scripts

Use these scripts to validate before completion:

### Validate Task File Format

```bash
python .claude/skills/managing-task-lifecycle/scripts/validate_task_status.py TASK-XXX
```

Checks: frontmatter, required fields, valid status, acceptance criteria section.

### Check Completion Readiness

```bash
python .claude/skills/managing-task-lifecycle/scripts/check_completion.py TASK-XXX
```

Runs: task file validation, tests, linting, git status.

**Validation loop:** Run → fix issues → re-run until all checks pass.

## Trello Sync Commands

```bash
# Check Trello connection status
bpsai-pair trello status

# Sync plan to Trello (creates/updates cards)
bpsai-pair plan sync-trello PLAN-ID

# Force refresh from Trello
bpsai-pair trello refresh
```

## Full CLI Reference

See [reference/all-cli-commands.md](reference/all-cli-commands.md) for complete command documentation.
