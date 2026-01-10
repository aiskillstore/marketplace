---
name: recovery
description: Recover session state from memory-keeper after context loss.
---

# Recovery Skill

Restore session state from memory-keeper checkpoints after context is lost or when starting a new session.

## When to Use

- Starting a new session on existing work
- After context was exhausted
- When asked "what was I working on?"
- When asked to "recover" or "restore" context
- After `/clear` or session restart

## Recovery Actions

### 1. Load Recent Context

```
context_get(limit: 50, sort: "created_desc")
```

### 2. Get Context Summary

```
context_summarize()
```

### 3. Find Progress Items

```
context_get(category: "progress", limit: 20)
```

### 4. Find High Priority Items

```
context_get(priority: "high", limit: 10)
```

### 5. Reconstruct State

From the retrieved context, extract:
- `current-task`: What was being worked on
- `files-modified`: Files that were changed
- `implementation-progress`: How far along
- `next-action`: What needs to happen next
- `blockers`: Any known issues

## Recovery Output Format

Present the recovered state clearly:

```markdown
## Session Recovered

### Previous Task
<current-task value>

### Progress
<implementation-progress value>

### Files Modified
<list of files-modified>

### Blockers/Issues
<any blockers found>

### Recommended Next Action
<next-action value>

### Recent Checkpoints
1. <checkpoint 1 name>: <description>
2. <checkpoint 2 name>: <description>

---

Ready to continue. Confirm to proceed with: <next-action>
```

## Recovery Checklist

- [ ] Load all recent context items
- [ ] Identify the current/last task
- [ ] Find all files that were modified
- [ ] Determine progress percentage/phase
- [ ] Locate the next action to take
- [ ] Check for any blockers
- [ ] Verify todo list state if available
- [ ] Present summary to user
- [ ] Get confirmation before proceeding

## If No Context Found

If memory-keeper has no relevant context:

```markdown
## No Previous Context Found

No checkpoints or progress items found in memory-keeper.

Possible reasons:
- This is a new session with no prior work
- Previous session did not checkpoint (work may be lost)
- Memory was cleared

To start fresh, describe what you'd like to work on.
```

## Partial Recovery

If only some context is found:

```markdown
## Partial Recovery

Found limited context from previous session:

### Available Information
<whatever was found>

### Missing Information
- [ ] Current task (not found)
- [ ] Files modified (not found)
- etc.

Would you like to:
1. Continue with available context
2. Start fresh
3. Provide additional context manually
```
