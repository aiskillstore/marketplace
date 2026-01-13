---
name: executing-plans
description: Execute implementation plans with batch processing and review checkpoints. Use when given a plan document.
---

# Executing Plans

Execute implementation plans systematically with quality gates between batches.

## When to Use

- When given a plan document to implement
- After writing-plans skill produces a plan
- For batch execution with human checkpoints

## The Five-Step Process

### Step 1: Load and Review Plan

1. Read the plan document carefully
2. Identify potential issues or ambiguities
3. Raise concerns with user **before** beginning work
4. Create TodoWrite with all tasks if plan seems sound

**If issues found:** Stop and clarify before proceeding

### Step 2: Execute Batch

Default batch size: **3 tasks**

For each task in batch:

1. Update status to `in_progress`
2. Execute each step as written
3. Run specified verifications
4. Mark as `completed` only when verified

### Step 3: Report

After completing a batch:

```markdown
## Batch Complete

**Tasks Completed:** [List]

**Verifications:**

- Task 1: [Pass/Fail] - [Details]
- Task 2: [Pass/Fail] - [Details]
- Task 3: [Pass/Fail] - [Details]

**Issues Found:** [If any]

Ready for feedback.
```

### Step 4: Continue

1. Incorporate any requested changes
2. Execute next batch
3. Repeat cycle

### Step 5: Complete Development

After all tasks finished and verified:

1. Run full test suite
2. Announce completion
3. Transition to finishing workflow (merge/PR decision)

## Critical Rules

### STOP Immediately When:

- Blockers (missing dependencies, failed tests)
- Plan gaps preventing progress
- Unclear instructions
- Repeated verification failures (2+ on same task)

**When blocked:** Ask for clarification, don't force through.

### Return to Step 1 When:

- User updates the plan
- Approach needs fundamental revision
- Architecture issues discovered

### Never:

- Skip verifications
- Force through blockers
- Batch completions (mark done one at a time)
- Proceed with unresolved critical issues

## Batch Size Guidelines

| Scenario          | Batch Size   |
| ----------------- | ------------ |
| Simple tasks      | 3-5          |
| Complex tasks     | 1-2          |
| High-risk changes | 1            |
| User preference   | As specified |

## Integration with Other Skills

- **test-driven-development:** Each task follows TDD
- **systematic-debugging:** If tests fail, use debugging skill
- **code-review:** Request review after significant batches
