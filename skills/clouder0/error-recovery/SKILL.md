---
name: error-recovery
description: Strategies for handling subagent failures with retry logic and escalation patterns.
allowed-tools: Read, Task
---

# Error Recovery Skill

Pattern for handling subagent failures gracefully with appropriate retry strategies.

## When to Load This Skill

- You are spawning subagents that may fail
- A subagent returned an error or unexpected output
- You need to decide whether to retry, escalate, or abort

## Failure Categories

| Category | Symptoms | Strategy |
|----------|----------|----------|
| **Transient** | Timeout, malformed output, parsing error | Simple Retry |
| **Context Gap** | "I don't have enough information", unclear task | Context Enhancement |
| **Complexity** | Partial completion, scope creep, tangents | Scope Reduction |
| **Boundary/Contract** | `status: blocked`, boundary_violation, contract_change | Escalation |
| **Fatal** | Repeated failures (3+), fundamental misunderstanding | Abort with Report |

## Retry Strategies

### Strategy 1: Simple Retry

For transient failures. Same prompt, up to 3 attempts.

```
# Track attempts
attempts: 0
max_attempts: 3

# On failure
IF attempts < max_attempts:
  attempts += 1
  Task(same_subagent_type, same_model, same_prompt)
ELSE:
  Mark as FAILED, move on
```

**Use when:**
- Output was malformed or truncated
- Timeout occurred
- Agent returned empty/null response

### Strategy 2: Context Enhancement

Add more information to help the agent succeed.

```
Task(
  subagent_type: "implementer",
  model: "sonnet",
  prompt: |
    ## PREVIOUS ATTEMPT FAILED

    Error: {error_message}
    Output received: {partial_output}

    ## ADDITIONAL CONTEXT

    Here is more information that may help:
    - Related file: @{additional_file_path}
    - Pattern to follow: {example_pattern}
    - Specific guidance: {clarification}

    ## ORIGINAL TASK

    {original_task_description}

    Output to: {output_path}
)
```

**Use when:**
- Agent said "I don't understand" or "unclear requirements"
- Agent made incorrect assumptions
- Agent asked questions in output

**Context to add:**
- Related code files the agent might need
- Similar implementations as examples
- Explicit clarification of ambiguous points
- Error message from previous attempt

### Strategy 3: Scope Reduction

Break the failing task into smaller, more manageable pieces.

```
# Original task failed
Task: "Implement full authentication system"

# Split into subtasks
Task(implementer, "Implement password hashing utility")
Task(implementer, "Implement session token generation")
Task(implementer, "Implement login endpoint")
Task(implementer, "Implement logout endpoint")
```

**Use when:**
- Agent completed partial work then failed
- Task description was too broad
- Agent went off on tangents
- Output shows confusion about scope

**Splitting guidelines:**
- Each subtask should be independently completable
- Each subtask should have clear boundaries
- Subtasks can run in parallel if no dependencies
- Recombine outputs after all subtasks complete

### Strategy 4: Escalation

Route to specialized agent for resolution.

```
# For boundary violations
Task(
  subagent_type: "contract-resolver",
  model: "sonnet",
  prompt: |
    A task is blocked due to boundary/contract issues.

    Blocked task output: memory/tasks/{task_id}/output.json
    Blocked reason: {blocked_reason}
    Current contracts: {contract_paths}

    Analyze impact and provide resolution.
    Output to: memory/contracts/resolution_{task_id}.json
)
```

**Escalation paths:**

| Failure Type | Escalate To | Action |
|--------------|-------------|--------|
| `blocked_reason: boundary_violation` | contract-resolver | Expand boundaries or redesign |
| `blocked_reason: contract_change` | contract-resolver | Modify contract, re-verify dependents |
| `blocked_reason: dependency_issue` | executor (self) | Re-check dependency status |
| Repeated implementation failures | architect | Reconsider design approach |

### Strategy 5: Abort with Report

When recovery is not possible, fail gracefully.

```json
{"tasks":[{"id":"{task_id}","status":"failed","failure_reason":"{specific reason}","attempts_made":3,"recovery_attempted":[{"strategy":"simple_retry","result":"same_error"},{"strategy":"context_enhancement","result":"different_error"},{"strategy":"scope_reduction","result":"subtasks_also_failed"}],"recommendation":"Task may need architectural redesign"}]}
```

**Use when:**
- 3+ retry attempts failed
- Different strategies all failed
- Fundamental misunderstanding of requirements
- Task is actually impossible given constraints

## Decision Tree

```
On Subagent Failure:
│
├─ Is output malformed/empty/timeout?
│  └─ YES → Strategy 1: Simple Retry (up to 3x)
│
├─ Did agent say "unclear" or ask questions?
│  └─ YES → Strategy 2: Context Enhancement
│
├─ Did agent complete partial work?
│  └─ YES → Strategy 3: Scope Reduction
│
├─ Is status "blocked" with boundary/contract reason?
│  └─ YES → Strategy 4: Escalation to contract-resolver
│
├─ Have we tried 3+ strategies already?
│  └─ YES → Strategy 5: Abort with Report
│
└─ Unknown error
   └─ Try Strategy 2 first, then escalate
```

## Retry State Tracking

Track retry attempts in the execution state file:

```json
{"tasks":[{"id":"task-001","status":"running","attempts":2,"last_error":"Timeout after 120s","retry_strategy":"simple_retry"},{"id":"task-002","status":"running","attempts":1,"last_error":"Needs access to src/config/db.ts","retry_strategy":"context_enhancement","context_added":["src/config/db.ts","src/types/config.ts"]}]}
```

## Integration with Executor Loop

```
# Enhanced execution loop
WHILE tasks remain incomplete:
  1. Read state file
  2. Find ready tasks
  3. Spawn ready tasks
  4. Check completed tasks:
     FOR each completed task:
       IF status == pre_complete:
         spawn verifier
       ELIF status == blocked:
         apply Strategy 4 (Escalation)
       ELIF status == failed:
         determine_failure_category()
         apply_appropriate_strategy()
         update_retry_state()
  5. Update state file
  6. IF all verified: EXIT
  7. IF all failed with no recovery: EXIT with failure report
```

## Principles

1. **Fail fast, recover smart** - Don't retry blindly; analyze the failure first
2. **Preserve partial work** - If agent completed 50%, don't discard it
3. **Escalate early** - Boundary/contract issues need resolver, not retries
4. **Track everything** - Log all attempts for reflection phase
5. **Know when to quit** - 3 failed strategies = abort, don't loop forever
