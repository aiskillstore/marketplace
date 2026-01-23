---
name: implementation-review
description: Automatically trigger review agents after task completion. Use when strategic-planner finishes planning tasks (calls plan-consultant) or when main agent completes coding tasks in /implement workflow (calls code-reviewer). Triggers on phrases like "plan complete", "implementation done", "coding finished", "ready for review".
---

# Implementation Review Skill

## Purpose

This skill ensures quality gates are enforced during the EPIC workflow by automatically invoking the appropriate review agents after task completion.

## Review Triggers

### 1. Plan Review (Strategic-Planner Completion)

**Trigger Conditions:**
- `strategic-planner` agent has completed its planning tasks
- A strategy or implementation plan has been generated
- Keywords: "plan complete", "strategy ready", "planning done", "roadmap finalized"

**Action:** Delegate to `plan-consultant` agent for plan review

**Review Focus:**
- Plan completeness and feasibility
- Risk identification
- Alternative approaches consideration
- Alignment with project goals

### 2. Code Review (Main Agent Implementation Completion)

**Trigger Conditions:**
- Main agent has completed coding tasks in `/implement` workflow
- Implementation code has been written (after TDD Green phase)
- Keywords: "implementation complete", "coding done", "feature implemented", "code ready"

**Action:** Delegate to `code-reviewer` agent for code review

**Review Focus:**
- Code quality and maintainability
- Security vulnerabilities
- Performance considerations
- Adherence to project standards

## Workflow Integration

```
EPIC Workflow with Reviews:

[Explore] -> [Plan] -> PLAN REVIEW -> [Implement] -> CODE REVIEW -> [Commit]
                           |                              |
                    plan-consultant               code-reviewer
```

## Instructions

### When Strategic-Planner Completes:

1. Detect completion signal from strategic-planner agent
2. Collect the generated plan/strategy document
3. Invoke `plan-consultant` agent with the plan for review
4. Report review findings back to main workflow
5. If critical issues found, flag for plan revision before proceeding

### When Main Agent Completes Coding:

1. Detect completion of implementation tasks (TDD Green phase complete)
2. Identify all files modified during implementation
3. Invoke `code-reviewer` agent with the changed files
4. Report review findings back to main workflow
5. If critical issues found, flag for code revision before commit

## Agent Delegation

| Completion Event | Review Agent | Purpose |
|-----------------|--------------|---------|
| `strategic-planner` done | `plan-consultant` | Validate implementation strategy |
| Main agent coding done | `code-reviewer` | Validate code quality |

## Review Report Format

After each review, expect a structured report:

```markdown
## Review Summary
- **Reviewer:** [agent-name]
- **Rating:** [1-10]
- **Status:** [APPROVED / NEEDS REVISION / BLOCKED]

## Findings
- [Finding 1]
- [Finding 2]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]

## Action Items
- [ ] [Required action if any]
```

## Constraints

- DO NOT skip reviews - they are mandatory quality gates
- DO NOT proceed to next EPIC phase if review status is BLOCKED
- DO NOT modify code during review - only report findings
- Reviews should complete within reasonable time to not block workflow

## Examples

### Example 1: Plan Review Trigger

```
User: The strategic-planner has completed the implementation strategy for T001.