---
name: flow-finishing-branch
description: "Decide how to complete a development branch: merge, PR, squash, or cleanup."
---

# Flow Finishing Branch - 分支完成决策

## Overview

When development work is complete, you need to decide how to integrate it. This skill guides that decision.

## Decision Options

### A) Fast-forward Merge

```yaml
When to use:
  - Small changes (< 5 files)
  - Single developer
  - No review needed
  - Clean commit history

Command:
  git checkout main
  git merge --ff-only feature/xxx
  git branch -d feature/xxx

Pros:
  - Fast
  - Clean history
  - No merge commit

Cons:
  - No review record
  - No CI verification
```

### B) Create PR (Recommended)

```yaml
When to use:
  - Team projects
  - Need review record
  - CI verification required
  - Production code

Command:
  git push -u origin feature/xxx
  gh pr create --title "..." --body "..."

Pros:
  - Review record
  - CI verification
  - Discussion thread
  - Audit trail

Cons:
  - Takes longer
  - Requires reviewer
```

### C) Squash and Merge

```yaml
When to use:
  - Many small commits
  - Messy commit history
  - Want single commit in main

Command:
  gh pr merge --squash

Pros:
  - Clean main history
  - Single logical commit
  - Hides WIP commits

Cons:
  - Loses detailed history
  - Harder to bisect
```

### D) Cleanup Only

```yaml
When to use:
  - Work was abandoned
  - Experiment failed
  - Requirements changed

Command:
  git checkout main
  git branch -D feature/xxx
  git push origin --delete feature/xxx  # if pushed

Pros:
  - Clean slate
  - No dead branches

Cons:
  - Work is lost (unless needed later)
```

## Decision Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                    Decision Matrix                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Files Changed    Review Needed    History Clean    Action  │
│  ─────────────    ─────────────    ─────────────    ──────  │
│  < 5              No               Yes              A) FF   │
│  < 5              No               No               C) Sq   │
│  Any              Yes              Yes              B) PR   │
│  Any              Yes              No               C) Sq   │
│  N/A              N/A              N/A (abandoned)  D) Del  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Pre-Completion Checklist

Before choosing any option, verify:

```yaml
□ All tests pass
□ Build succeeds
□ No lint errors
□ Documentation updated (if needed)
□ EXECUTION_LOG.md updated
□ No uncommitted changes
```

## The Process

```yaml
1. Verify completion
   → Run tests, build, lint
   → Check all tasks done

2. Assess the work
   → How many files changed?
   → Is review needed?
   → Is commit history clean?

3. Choose option
   → Use decision matrix
   → Default to PR if unsure

4. Execute
   → Run appropriate commands
   → Verify success

5. Cleanup
   → Delete local branch
   → Delete remote branch (if not PR)
```

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "PR is overkill" | PR provides audit trail. Use it. |
| "I'll review my own code" | Self-review misses issues. Get another pair of eyes. |
| "History doesn't matter" | History helps debugging. Keep it clean. |
| "Just merge it" | Verify first. Merge second. |

## Integration with flow-release

This skill is used in `/flow-release` to decide branch handling:

```yaml
/flow-release execution:
  1. Verify all gates pass
  2. Load this skill
  3. Present options to user
  4. Execute chosen option
  5. Update status
```

## Cross-Reference

- [flow-release.md](../../commands/flow-release.md) - Release command
- [verification-before-completion](../verification-before-completion/SKILL.md) - Verification skill

---

**[PROTOCOL]**: 变更时更新此头部，然后检查 CLAUDE.md
