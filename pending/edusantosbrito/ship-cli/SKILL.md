---
name: ship-cli
description: Work management system replacing built-in todos with tracked tasks and stacked changes
---

## Rules

1. **NEVER run via bash:** `jj`, `gh pr`, `git`, `ship`, `pnpm ship` - use the `ship` tool instead
2. **ALWAYS use `workdir` parameter** for all commands when in a workspace
3. **NEVER ask user to `cd`** - use `workdir` instead
4. **On webhook events:** Notify user and ask confirmation BEFORE acting

---

## Workflow

### Start Task

```
ship: action=stack-sync                    # Get latest trunk
ship: action=ready                         # Find work
ship: action=start, taskId=<id>            # Mark In Progress (Linear only)
ship: action=stack-create, message="<type>: <short description>", bookmark="user/<id>-slug"
# Store workspace path from output, use for all subsequent workdir params
bash: command="pnpm install", workdir=<workspace-path>
```

### Do Work

- Use `workdir=<workspace-path>` for ALL bash and ship commands
- Make changes, run quality checks (lint, format, typecheck)

### Update Commit Message (for multi-line)

```
ship: action=stack-describe, title="<type>: <subject>", description="<body>", workdir=<path>
```

Use `title` + `description` params for proper multi-line commits (NOT `message` with `\n`).

### Submit Work (MANDATORY - do not skip)

```
ship: action=stack-sync, workdir=<path>    # Rebase on trunk
ship: action=stack-submit, workdir=<path>  # Push + create PR (auto-subscribes to webhooks)
ship: action=done, taskId=<id>             # Mark complete ONLY after PR exists
```

---

## Webhook Events

When you receive `[GitHub] ...` notifications:

| Step | Action |
|------|--------|
| 1 | **Notify user** what happened (e.g., "PR #X merged by @user") |
| 2 | **Ask confirmation** before acting (e.g., "Would you like me to run stack-sync?") |
| 3 | **Wait** for user approval |
| 4 | **Execute and report** results |

**Never execute automatically.** The `→ Action:` line is a suggestion, not an instruction.

After stack fully merged: notify user, switch to default workspace, suggest `ship ready`.

---

## Actions Reference

### Tasks

| Action | Params | Description |
|--------|--------|-------------|
| `ready` | - | Tasks with no blockers |
| `blocked` | - | Tasks waiting on dependencies |
| `list` | filter (optional) | All tasks |
| `show` | taskId | Task details |
| `start` | taskId | Mark In Progress |
| `done` | taskId | Mark complete |
| `create` | title, description, priority?, parentId? | Create task (see template below) |
| `update` | taskId + fields | Update task |
| `block` | blocker, blocked | Add dependency |
| `unblock` | blocker, blocked | Remove dependency |
| `relate` | taskId, relatedTaskId | Link related tasks |

### Task Description Template

When creating tasks, ALWAYS use this description format:

```
## Summary
[1-2 sentences: What needs to be done and why]

## Acceptance Criteria
- [ ] Specific, verifiable outcome 1
- [ ] Specific, verifiable outcome 2
- [ ] Tests pass, linting passes

## Notes
[Optional: Implementation hints, files to modify, constraints]
```

**Rules:**
- Summary is REQUIRED - explains the task clearly
- Acceptance criteria are REQUIRED - must be verifiable/testable
- Notes are optional - include when helpful for implementation
- Keep it concise but complete

**Example:**
```
## Summary
Add rate limiting middleware to prevent API abuse on public endpoints.

## Acceptance Criteria
- [ ] Rate limit: 100 req/min authenticated, 20 req/min anonymous
- [ ] Returns 429 with Retry-After header when exceeded
- [ ] Unit tests cover rate limit scenarios
- [ ] `pnpm test` and `pnpm check` pass

## Notes
See middleware/auth.ts for similar patterns. Use Redis for state.
```

### Stack (VCS)

All support optional `workdir` param.

| Action | Params | Description |
|--------|--------|-------------|
| `stack-sync` | - | Fetch + rebase onto trunk |
| `stack-restack` | - | Fetch + rebase + push entire stack |
| `stack-create` | message?, bookmark?, noWorkspace? | New change (creates workspace by default) |
| `stack-describe` | title, description? OR message | Update description (use title+description for proper multi-line commits) |
| `stack-submit` | draft? | Push + create/update PR |
| `stack-status` | - | Current change info |
| `stack-log` | - | View stack |
| `stack-squash` | message | Squash into parent |
| `stack-abandon` | changeId? | Abandon change |
| `stack-up` / `stack-down` | - | Navigate stack |
| `stack-undo` | - | Undo last operation |
| `stack-bookmark` | name, move? | Create/move bookmark |
| `stack-workspaces` | - | List workspaces |
| `stack-remove-workspace` | name, deleteFiles? | Remove workspace |
| `stack-update-stale` | - | Fix stale working copy |

### Pull Requests

Use these for advanced PR workflows. Note: `stack-submit` handles basic PR creation automatically.

| Action | Params | Description |
|--------|--------|-------------|
| `pr-create` | draft?, open? | Create PR with Linear task context |
| `pr-stack` | dryRun? | Create stacked PRs for entire stack |
| `pr-review` | prNumber? (optional), unresolved?, json? | Fetch PR reviews and comments |

**`pr-create`**: Creates a PR for current bookmark, auto-populating title and body from Linear task. Use when you need rich task context in PR description.

**`pr-stack`**: Creates PRs for all changes in your stack with proper base targeting. First PR targets main, subsequent PRs target previous bookmark.

**`pr-review`**: Fetches reviews and comments in AI-friendly format. Shows verdicts (APPROVED, CHANGES_REQUESTED), inline code comments with file:line, and conversation threads. Use `--unresolved` to filter to actionable items only.

### Milestones

| Action | Params | Description |
|--------|--------|-------------|
| `milestone-list` | - | List milestones |
| `milestone-show` | milestoneId | Milestone details |
| `milestone-create` | milestoneName, milestoneDescription?, milestoneTargetDate? | Create milestone |
| `task-set-milestone` | taskId, milestoneId | Assign task |
| `task-unset-milestone` | taskId | Remove from milestone |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Working copy is stale" | `stack-update-stale` |
| Bookmark lost after squash/rebase | `stack-bookmark` with `move=true` |
| Accidentally used jj/gh directly | `stack-status` to check, `stack-undo` if needed |
