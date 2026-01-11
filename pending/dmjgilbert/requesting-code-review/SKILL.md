---
name: requesting-code-review
description: Request and process code reviews with proper context. Use after completing significant implementation work.
---

# Requesting Code Reviews

Review early, review often - catch issues before they compound.

## When Reviews Are Required

| Scenario                          | Timing             |
| --------------------------------- | ------------------ |
| Each task in subagent-driven work | After each task    |
| Major feature completion          | Before integration |
| Before merging to main            | Pre-merge          |
| When stuck on a problem           | As needed          |
| Before refactoring                | Pre-refactor       |
| After complex bug fix             | Post-fix           |

## How to Request Review

### 1. Gather Context

```bash
# Get commit range for review
git log --oneline -5
git diff main..HEAD --stat
```

### 2. Dispatch Reviewer

```
Task(code-reviewer, prompt="
Review the changes in commits [base]..[head]

**What was implemented:**
[Description of changes]

**Requirements reference:**
[Link or description of requirements]

**Areas of concern:**
[Any specific areas you want extra attention]

**Files changed:**
[List key files]
")
```

### 3. Process Feedback

| Severity  | Action Required                            |
| --------- | ------------------------------------------ |
| Critical  | Fix immediately - blocks all other work    |
| High      | Resolve before proceeding to next task     |
| Medium    | Address in current session if time permits |
| Low/Minor | Document for future improvement            |

## Review Request Template

```markdown
## Code Review Request

**Commits:** [base-sha]..[head-sha]
**Branch:** [branch-name]

### Summary

[1-2 sentences on what changed]

### Changes by File

| File         | Change Type    | Description    |
| ------------ | -------------- | -------------- |
| path/to/file | Added/Modified | [What changed] |

### Requirements

[Link to issue/spec or brief description]

### Testing Done

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

### Areas Needing Attention

- [Specific concern 1]
- [Specific concern 2]

### Questions for Reviewer

- [Any specific questions]
```

## Handling Feedback

### Agree with Feedback

1. Acknowledge the issue
2. Fix immediately (Critical/High) or document (Medium/Low)
3. Respond with what was changed

### Disagree with Feedback

1. **Never** dismiss without explanation
2. Provide technical justification with evidence
3. Reference code patterns or documentation
4. Explain trade-offs considered
5. Be open to being wrong

### Example Response

```markdown
## Review Response

### Critical Issues

- **[File:Line]**: Fixed - [what was changed]

### High Priority

- **[File:Line]**: Fixed - [what was changed]

### Disagreement: [Issue]

I believe [current approach] is correct because:

1. [Technical reason]
2. [Evidence from codebase]
   However, open to discussion if I'm missing something.

### Deferred

- **[Minor issue]**: Added to tech debt tracker for future
```

## Integration Points

- After **executing-plans** batches
- After **systematic-debugging** fixes
- Before **finishing branches** (merge/PR)
