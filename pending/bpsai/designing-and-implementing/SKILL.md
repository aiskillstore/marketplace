---
name: designing-and-implementing
description: Use when receiving feature requests, architectural discussions, or multi-step implementation needs that require design before coding.
---

# Design → Plan → Implement

## When to Use This Flow

Check if planning is needed:
```bash
bpsai-pair intent should-plan "user's request here"
```

Get flow recommendation:
```bash
bpsai-pair intent suggest-flow "user's request here"
```

Use this flow for: features, refactors, multi-step work.
Skip planning for: typo fixes, small bugs, documentation tweaks.

## Workflow

### 1. Clarify Requirements
- Restate the goal in 1-3 sentences
- Identify affected components
- Ask clarifying questions if ambiguous
- Research existing code patterns

### 2. Propose Approaches
Present 2-3 options with pros/cons and recommend one.

### 3. Create Plan

```bash
bpsai-pair plan new <slug> --type feature --title "Title"
```

### 4. Add Tasks

Task format in `.paircoder/tasks/`:
```yaml
---
id: TASK-XXX
title: Task title
status: pending
priority: P0  # P0=must, P1=should, P2=nice
complexity: 30  # 10-100 scale
---

## Objective
What this accomplishes.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Tests pass

## Dependencies
- Requires TASK-YYY (if any)
```

### 5. Sync to Trello

```bash
bpsai-pair plan sync-trello <plan-id> --target-list "Planned/Ready"
```

### 6. Implement Each Task

1. `bpsai-pair task update TASK-XXX --status in_progress`
2. Write tests first (see implementing-with-tdd skill)
3. Implement feature
4. Complete via managing-task-lifecycle skill

## Key Files

- Plans: `.paircoder/plans/`
- Tasks: `.paircoder/tasks/`
- State: `.paircoder/context/state.md`
- Project context: `.paircoder/context/project.md`

## Commands

```bash
bpsai-pair plan list              # List plans
bpsai-pair plan show <id>         # Show plan details
bpsai-pair task list --plan <id>  # Tasks in plan
bpsai-pair task next              # Next task to work on
```
