---
name: planning-with-trello
description: Use when planning features, organizing sprints, or syncing work with Trello boards.
---

# Trello-Aware Planning

## Board Structure (7 Lists Max)

1. **Intake/Backlog** - New ideas, not selected for work
2. **Planned/Ready** - Selected for upcoming work
3. **In Progress** - Active development
4. **Review/Testing** - Under review
5. **Deployed/Done** - Completed
6. **Issues/Tech Debt** - Bugs, improvements
7. **Notes/Ops Log** - Decisions, notes

## Card Title Format

```
[Stack] Task Name
```

Examples: `[CLI] Add MCP server`, `[Docs] Update README`

## Effort Labels

| Size | Description | Complexity |
|------|-------------|------------|
| S | Few hours | 0-25 |
| M | Half-full day | 26-50 |
| L | Multiple days | 51+ |

## Stack Labels

| Label | Use For |
|-------|---------|
| Frontend (green) | React, UI |
| Backend (blue) | Flask, API |
| Worker (purple) | Background jobs |
| Bug/Issue (orange) | Bugs |
| AI/ML (black) | Models, LLM |

## Workflow

### 1. Create Plan

```bash
bpsai-pair plan new <slug> --type feature --title "Title"
```

### 2. Add Tasks

Break into 1-2 day units with acceptance criteria.

### 3. Sync to Trello

```bash
# Preview
bpsai-pair plan sync-trello <plan-id> --dry-run

# Sync to Planned/Ready (recommended for sprints)
bpsai-pair plan sync-trello <plan-id> --target-list "Planned/Ready"
```

### 4. Execute Tasks

Follow managing-task-lifecycle skill for starting/completing.

## Commands

```bash
bpsai-pair plan list                    # List plans
bpsai-pair plan status <plan-id>        # Plan status
bpsai-pair plan sync-trello <plan-id>   # Sync to Trello
bpsai-pair task list --plan <plan-id>   # Tasks in plan
```
