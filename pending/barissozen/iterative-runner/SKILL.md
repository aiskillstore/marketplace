---
name: iterative-runner
description: Runs Claude in a retry loop until tests pass or task completes. Use for TDD loops, overnight builds, or any task needing repeated iteration until success. Triggers on: loop until done, keep trying, retry until pass, TDD loop, iterate until tests pass.
---

# Iterative Runner

Runs Claude in a persistent loop that keeps retrying until tests pass or the task is complete.

## When to Use

- Running TDD loops that iterate until all tests pass
- Overnight builds that need to keep trying until successful
- Any task requiring repeated attempts until completion criteria are met
- Automated retry for flaky or complex implementations

## Core Concept

```bash
while :; do cat PROMPT.md | claude ; done
```

Keep iterating until task is complete.

## Workflow

### Step 1: Define Completion Criteria

Specify clear success conditions:
- All tests passing
- No linter errors
- Specific output marker (e.g., `<promise>DONE</promise>`)

### Step 2: Set Safety Limits

Always use `--max-iterations` to prevent infinite loops.

### Step 3: Run the Loop

```bash
# Basic loop
iterative-runner "Build feature X" --completion-promise "DONE" --max-iterations 30

# TDD loop
iterative-runner "Implement feature using TDD.
1. Write failing test
2. Implement to pass
3. Run tests
4. Fix if failing
5. Repeat

Output <promise>DONE</promise> when all tests green." --max-iterations 50
```

## Prompt Best Practices

1. **Clear completion criteria** - Define what "done" means
2. **Incremental goals** - Break into phases
3. **Self-correction** - Include retry logic
4. **Escape hatch** - Always use --max-iterations

## Template

```
Implement [FEATURE].

Requirements:
- [Requirement 1]
- [Requirement 2]

Success criteria:
- All tests passing
- No linter errors

After 15 failed iterations:
- Document blockers
- List attempted approaches

Output <promise>COMPLETE</promise> when done.
```
