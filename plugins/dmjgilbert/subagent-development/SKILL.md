---
name: subagent-development
description: Execute plans using fresh subagent per task with code review between tasks. Use for high-quality iterative implementation.
---

# Subagent-Driven Development

Fresh subagent per task + review between tasks = high quality, fast iteration.

## When to Use

- Executing implementation plans in current session
- Tasks are largely independent
- Want continuous progress with quality gates
- Need isolation between task contexts

## When NOT to Use

- Plan needs initial review/revision
- Tasks have tight sequential dependencies
- Simple changes that don't need isolation

## The Process

### 1. Load Plan & Create Tasks

```
1. Read the plan document
2. Create TodoWrite with all tasks
3. Verify plan is sound before starting
```

### 2. For Each Task

**Dispatch Implementation Subagent:**

```
Task([appropriate-agent], prompt="
Implement Task N from the plan:

**Task:** [Task description]

**Requirements:**
- Follow TDD (write failing test first)
- Implement minimal code to pass
- Verify all tests pass
- Commit with descriptive message

**Output:**
- What was implemented
- Test results
- Any issues encountered
")
```

### 3. Code Review Checkpoint

After EACH task, dispatch reviewer:

```
Task(code-reviewer, prompt="
Review implementation of Task N:

**What was implemented:** [From subagent output]
**Commits:** [Range]
**Requirements:** [From plan]

Evaluate:
- Implementation vs requirements match
- Code quality and patterns
- Test coverage
- Critical/Important/Minor issues
")
```

### 4. Address Feedback

| Severity | Action                      |
| -------- | --------------------------- |
| Critical | Fix immediately, re-review  |
| High     | Fix before next task        |
| Medium   | Fix if quick, else document |
| Low      | Document for later          |

### 5. Mark & Continue

1. Update TodoWrite to mark task complete
2. Proceed to next task
3. Repeat cycle

### 6. Final Review

After all tasks complete:

```
Task(code-reviewer, prompt="
Final review of complete implementation:

**Plan:** [Reference]
**All commits:** [Full range]

Verify:
- Complete plan compliance
- Architectural soundness
- No regressions
- Ready for merge
")
```

### 7. Finish

Transition to merge/PR workflow.

## Critical Rules

### Never:

- Skip code reviews between tasks
- Proceed with unresolved Critical issues
- Run multiple implementation subagents in parallel
- Implement without plan task reference

### Always:

- Fresh subagent for each task (clean context)
- Review after each task (quality gate)
- Fix Critical/High before continuing
- Document deferred issues

## Quality Gate Template

```markdown
## Task N Review

**Status:** [Pass/Fail]

### Critical Issues

[None / List]

### High Priority

[None / List]

### Medium Priority

[None / List]

### Minor/Suggestions

[None / List]

### Verdict

- [ ] Proceed to next task
- [ ] Fix issues first
- [ ] Needs discussion
```

## Benefits

- Clean context for each task (no accumulated confusion)
- Built-in quality gates catch issues early
- Reviewable progress at each step
- Easy to pause/resume at task boundaries
