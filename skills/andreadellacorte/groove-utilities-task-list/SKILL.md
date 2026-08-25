---
name: groove-utilities-task-list
description: "List active tasks in the configured backend. Use to see current task status."
license: MIT
allowed-tools: Read Write Edit Glob Grep Bash(git:*) Bash(beans:*) Bash(gh:*) Bash(linear:*) Bash(npx:*) AskUserQuestion
metadata:
  author: andreadellacorte
---

# groove-utilities-task-list

## Outcome

A consolidated view of active, ready tasks from the configured backend is displayed to the user. Blocked and in-progress tasks are clearly distinguished. Output is suitable for daily start context.

## Acceptance Criteria

- Tasks are shown grouped by status (in-progress, ready/todo, blocked)
- Blocked tasks show what they are waiting on
- In-progress tasks are listed first
- Output is concise enough to scan at a glance

## Constraints

- Read `.groove/index.md` frontmatter to determine `tasks.backend` and `tasks.list_limit` (default 15)
- If `tasks.backend: none`, print a friendly no-op message and exit
- Backend mappings:
  - `beans`: run `skills/groove-utilities-task-list/scripts/list-tasks-by-priority.sh [LIMIT]` with LIMIT from `tasks.list_limit` (or 15), then parse and format output (group by status: in-progress, todo, blocked)
  - `linear`: use linear CLI or MCP to fetch assigned, active issues
  - `github`: run `gh issue list --assignee @me --state open`
- If backend CLI is not installed or unreachable, error clearly with install hint (see `/groove-utilities-task-install`)
- Do not modify any tasks during list
