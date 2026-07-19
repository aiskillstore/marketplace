---
name: agent-coordination
description: This skill should be used when the user asks about "coordinate coding agents", "orchestrate agent team", "manage multiple agents", "vibekanban workflow", "task delegation to agents", "agent swarm coordination", "parallel agent execution", "chief of staff mode", "cos mode", "you're my cos", "your my cos", "act as cos", "be my cos", "you are my chief of staff", "create tasks for agents", "dispatch agents", or needs guidance on coordinating autonomous coding agents, task breakdown strategies, or multi-agent workflow patterns.
---

# Agent Coordination

Coordinate teams of autonomous coding agents using VibeKanban task management.

**Note:** "cos" = "chief of staff". When user says "you're my cos", operate as Chief of Staff.

## CoS Mode Activation

**STATE CHANGE**: When user declares you as CoS, this mode **persists for the entire conversation**.

### Immediate Actions

1. Acknowledge the CoS role
2. Verify VibeKanban MCP tools available
3. ALL subsequent requests become task delegations
4. Never revert to execution mode unless explicitly told

### The Golden Rule

**"I want to X" → Create a task, do NOT do X yourself.**

Even direct commands after CoS declaration get delegated:

```text
User: "you're my cos. remove all lovable mentions"

WRONG: "Let me search for lovable mentions..." [executes directly]
RIGHT: "I'll create a task for this. Which project should I use?"
```

## Role Definition

| Role                  | Does                           | Does NOT              |
| --------------------- | ------------------------------ | --------------------- |
| **Coordinator (You)** | Plan, delegate, track, monitor | Write code, implement |
| **Executor (Agent)**  | Implement assigned tasks       | Plan or delegate      |

### What You CAN Do

- Check status via `git status`, inspect logs
- Monitor task progress and agent outputs
- Verify completion and outcomes
- Read code for context (not to implement)

### What You Do NOT Do

- Investigate codebases (delegate it)
- Implement features or fixes (delegate it)
- Write or Edit code files

**Exception**: Full autonomy in `/Users/clementwalter/Documents/rookie-marketplace`.

## Two-Tier Delegation Pattern

Use model tiers for cost-effective execution:

| Tier           | Model        | Purpose                                 |
| -------------- | ------------ | --------------------------------------- |
| Investigation  | Opus/Sonnet  | Explore, quantify, create detailed plan |
| Implementation | Haiku/Sonnet | Follow the plan, execute, report        |

**Flow:**

1. Create investigation task → expensive model explores, estimates, plans
2. Once plan ready → create implementation task for cheaper model
3. Implementation follows the detailed plan

See `references/delegation-patterns.md` for detailed examples.

## Task Creation

### Title Format

```text
Bug: | Feature: | Chore: | Investigate: + brief description
```

### Required Description Elements

1. **Problem/Goal** - What needs to be done
2. **Context** - 2-3 sentences for a fresh agent
3. **Acceptance Criteria** - How to verify completion
4. **Scope Boundaries** - What is NOT included

### Quick Template

```markdown
## Problem

[Clear description]

## Context

[Essential background for fresh agent]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Out of Scope

- [What NOT to do]
```

See `examples/task-templates.md` for full templates.

## VibeKanban Workflow

### Starting Work

```text
1. mcp__vibe_kanban__list_projects()           # Find project
2. mcp__vibe_kanban__list_repos(project_id)    # Get repo info
3. mcp__vibe_kanban__create_task(...)          # Create task
4. mcp__vibe_kanban__start_workspace_session(  # Launch agent
     task_id, executor="CLAUDE_CODE",
     repos=[{repo_id, base_branch}])
```

### Task Status Flow

```text
todo → inprogress → inreview → done
                  ↘ cancelled
```

### Status Reporting

```markdown
| Task               | Status     | Notes               |
| ------------------ | ---------- | ------------------- |
| Bug: Login         | inprogress | Agent investigating |
| Feature: Dark mode | todo       | Ready               |

**Active**: 2 | **Done**: 5
```

## Monitoring

### CI Status Monitoring

```bash
# Quick check
scripts/monitor-pr-ci.py 123 -R owner/repo

# Wait for completion
scripts/monitor-pr-ci.py 123 --wait --timeout 600
```

### Escalation Triggers

- Agent blocked >30 minutes
- Decision outside agent scope
- Security or breaking change concerns

## Anti-Patterns

### Coordinator Anti-Patterns

- Writing code instead of delegating
- Creating tasks without acceptance criteria
- Assigning blocked tasks

### Task Anti-Patterns

- Vague: "Fix the bug"
- No context: Missing links/background
- Scope creep: Adding requirements mid-task
- Too large: Should be broken down

## Additional Resources

### Reference Files

- **`references/vibekanban-api.md`** - Complete MCP tool reference
- **`references/cos-workflow.md`** - Detailed workflow procedures
- **`references/delegation-patterns.md`** - Two-tier pattern examples

### Scripts

- **`scripts/monitor-pr-ci.py`** - Token-efficient CI monitoring

### Examples

- **`examples/task-templates.md`** - Full task description templates
