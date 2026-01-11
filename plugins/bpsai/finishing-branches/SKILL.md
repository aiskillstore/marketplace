---
name: finishing-branches
description: Use when work is complete and ready for integration, merge, or PR creation.
---

# Finish Branch

## Pre-Merge Checklist

### 1. Run All Checks

```bash
bpsai-pair ci                 # Tests + linting in one command
bpsai-pair validate           # Check project structure
```

### 2. Security Scan

```bash
bpsai-pair security scan-secrets --staged   # Check for leaked secrets
```

### 3. Review Changes

```bash
git diff main...HEAD --stat
git diff main...HEAD | grep -E "print\(|breakpoint|TODO|FIXME"
```

### 4. Update Task Status

Follow managing-task-lifecycle skill for two-step completion.

### 5. Create PR

```bash
bpsai-pair github auto-pr     # Auto-creates PR from branch, detects TASK-xxx
```

## PR Template

```markdown
## Summary
Brief description.

## Changes
- Added X
- Modified Y
- Fixed Z

## Testing
- [ ] Unit tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] No debug statements
- [ ] Documentation updated
- [ ] Task status updated
```

## Post-Merge

```bash
git checkout main
git pull origin main
git branch -d <feature-branch>
```

## Quick Finish

```bash
pytest && ruff check . && git add -A && git commit -m "[TASK-XXX] Description" && git push
```
