---
name: parallel-agents
description: Dispatch multiple agents to work on independent problems concurrently. Use when facing 3+ independent failures or tasks.
---

# Dispatching Parallel Agents

Assign separate agents to independent problem domains simultaneously for faster resolution.

## When to Use

- 3+ test failures across different files/subsystems
- Multiple independent tasks that don't share state
- Investigations that won't interfere with each other
- Failures from unrelated root causes

## When NOT to Use

- Failures are interconnected
- Tasks share state or create conflicts
- Agents would modify the same files
- You lack context to properly scope tasks

## Implementation Steps

### 1. Group by Domain

Organize failures/tasks into independent categories:

```markdown
Group A: Authentication tests (3 failures)
Group B: API endpoint tests (2 failures)
Group C: UI component tests (4 failures)
```

### 2. Define Focused Tasks

Each agent receives:

| Field       | Description                      |
| ----------- | -------------------------------- |
| Scope       | Specific files/tests to focus on |
| Goal        | Clear success criteria           |
| Constraints | What NOT to change               |
| Output      | Expected deliverable             |

### 3. Dispatch Concurrently

**IMPORTANT**: Launch all tasks in a **single message** (no `run_in_background`). Multiple Task calls in the same message automatically run in parallel, and Claude waits for all to complete.

```
# All three tasks run in parallel automatically when in the same message
Task(test-engineer, prompt="Fix auth test failures in src/auth/*.test.ts")
Task(test-engineer, prompt="Fix API test failures in src/api/*.test.ts")
Task(frontend-developer, prompt="Fix UI test failures in src/components/*.test.tsx")
# Claude waits for all to complete, then continues
```

**Avoid `run_in_background: true`** unless you need to do other work while waiting. Task IDs must be captured and used within the same response.

### 4. Integrate Results

1. Review all agent outputs (available after parallel completion)
2. Verify no conflicts between changes
3. Run full test suite
4. Merge changes

## Effective Agent Prompts

**Good prompt:**

```
Fix the 3 failing tests in src/auth/login.test.ts:
- "should reject invalid email format"
- "should require password min length"
- "should handle network errors"

Error messages attached. Identify root causes - don't just increase timeouts.
Constraints: Don't modify src/api/* files.
Output: Summary of fixes with test results.
```

**Bad prompt:**

```
Fix all the tests
```

## Prompt Template

```markdown
## Task: [Specific description]

**Scope:** [Files/tests to focus on]

**Failures:**

- [Test name]: [Error message]
- [Test name]: [Error message]

**Goal:** [What success looks like]

**Constraints:**

- Don't modify [files]
- Preserve [behavior]

**Output:**

- Summary of root causes found
- Changes made
- Verification results
```

## Common Pitfalls

| Mistake         | Problem                   | Solution               |
| --------------- | ------------------------- | ---------------------- |
| Vague scope     | Agent changes wrong files | Specify exact paths    |
| Missing context | Agent can't diagnose      | Include error messages |
| No constraints  | Conflicting changes       | Define boundaries      |
| Unclear output  | Can't verify success      | Specify deliverables   |

## Benefits

- Reduces investigation time through parallelization
- Each agent maintains narrow focus
- Minimizes cross-agent interference
- Solves multiple problems concurrently

## Background Execution

For long-running tasks where you need to continue working, use `run_in_background: true`.

### Pattern: Background + Foreground

```
# Long-running audit in background
audit_task = Task(security-auditor,
  prompt="Full security audit",
  run_in_background: true)

# Continue with implementation work
Task(frontend-developer, prompt="Build login form")

# Later, get audit results
TaskOutput(audit_task.id, block: true)
```

### Pattern: Multiple Background Tasks

```
# Launch multiple background tasks
task1 = Task(test-engineer, prompt="...", run_in_background: true)
task2 = Task(code-reviewer, prompt="...", run_in_background: true)

# Do other work...

# Collect all results
result1 = TaskOutput(task1.id, block: true)
result2 = TaskOutput(task2.id, block: true)
```

### When to Use Background vs Foreground

| Scenario                   | Mode                      | Why                          |
| -------------------------- | ------------------------- | ---------------------------- |
| Quick tasks (< 1 min)      | Foreground                | Simpler, immediate results   |
| Long audit/analysis        | Background                | Continue working             |
| Multiple independent tasks | Foreground (parallel)     | Auto-waits for all           |
| Security + Implementation  | Background + Foreground   | Overlap work                 |

### Important Notes

- Task IDs are only valid within the same response
- Always use `block: true` when retrieving results with TaskOutput
- Prefer foreground parallel (single message, multiple Tasks) when possible
- Background tasks should be collected before the response ends
