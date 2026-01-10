# Monorepo Workflow

> Reference doc for nx-monorepo skill. Covers trunk-based dev, PR stacking, code review.

## Overview

This skill provides expert-level (L3-L4) capabilities for trunk-based development, PR workflows, code review, and change management.

**Skill Level**: Principal (E5/L4)
**Matrix Coverage**: W.1.x (TBD), W.2.x (PR Stacking), W.3.x (Code Review), W.4.x (Change Mgmt)

## Trunk-Based Development

### Core Rules

```
1. SINGLE TRUNK: All devs commit to main
2. SHORT-LIVED BRANCHES: Max 24 hours
3. CONTINUOUS INTEGRATION: Commit daily
4. FEATURE FLAGS: Ship incomplete behind flags
```

### Daily Workflow

```bash
git checkout main && git pull --rebase
git checkout -b feat/small-change
# ... make changes ...
git commit -m "feat(scope): description"
git push -u origin feat/small-change
gh pr create --fill
gh pr merge --squash --delete-branch
```

## PR Stacking

### When to Stack

- Feature requires > 400 lines
- Multiple logical units
- Need early feedback on foundation

### Graphite Workflow

```bash
gt create -m "feat: add types"      # PR #1
gt create -m "feat: implement"      # PR #2 (stacked)
gt create -m "feat: add UI"         # PR #3 (stacked)
gt submit --stack                   # Submit all
gt sync                             # After merge, rebase
```

### Manual Stacking

```bash
git checkout -b feat/base
git push && gh pr create

git checkout -b feat/next
git push && gh pr create --base feat/base

# After base merges:
git checkout feat/next
git rebase main
git push --force-with-lease
gh pr edit --base main
```

## Code Review

### PR Title Format

```
type(scope): description

feat(auth): add OAuth support
fix(api): handle null user
refactor(ui): extract Button
docs(readme): add setup guide
```

### Review Checklist

```
[ ] Understand context (PR description, issues)
[ ] High-level: approach makes sense?
[ ] Code quality: readable, clear logic?
[ ] Correctness: does what it claims?
[ ] Testing: tests present and adequate?
[ ] Monorepo: boundaries respected?
```

### Comment Conventions

```
🚫 Blocking: must fix
💡 Suggestion: consider changing
❓ Question: need clarification
🔧 Nitpick: optional improvement
✨ Praise: good work
```

## Breaking Changes

### Protocol

```markdown
## Breaking Change: @myorg/auth v2.0

**Change:** Removed legacyLogin()

### Migration
// Before
legacyLogin(user, pass)
// After
login({ user, pass })

### Timeline
- Day 0: Announcement
- Day 5: Deprecation warning
- Day 15: Removal

### Approvals
- [ ] @owner-team
- [ ] @affected-team
```

### Deprecation Pattern

```typescript
/**
 * @deprecated Use login() instead. Removed in v2.0.
 */
export function legacyLogin() {
  console.warn('legacyLogin is deprecated');
  return login(...arguments);
}
```

## Quick Reference

```bash
# Trunk-based
git checkout main && git pull --rebase
git checkout -b feat/change
gh pr create --fill
gh pr merge --squash

# Stacking (Graphite)
gt create -m "message"
gt submit --stack
gt sync

# Review
gh pr checkout 123
gh pr review --approve
gh pr review --request-changes
```
