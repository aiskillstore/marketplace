# Blitz Command Reference

## Worktree Commands

```bash
# Create worktree with new branch from main
git worktree add .worktrees/NAME -b fix/NAME main

# List all worktrees
git worktree list

# Remove a worktree
git worktree remove .worktrees/NAME

# Clean stale worktree references (if manually deleted)
git worktree prune
```

## Issue Management

```bash
# Close multiple issues
gh issue close 1 2 3 --comment "Complete per audit"

# View issue details
gh issue view NUMBER

# List open issues
gh issue list --state open
```

## PR Commands

```bash
# Create PR from current branch
gh pr create --title "TITLE" --body "BODY"

# View PR with reviews
gh pr view NUMBER --json reviews

# Get last review body
gh pr view NUMBER --json reviews --jq '.reviews[-1].body'

# Post review to GitHub
gh api repos/OWNER/REPO/pulls/NUMBER/reviews \
  -f body="REVIEW_CONTENT" -f event="COMMENT"

# Squash merge and delete branch
gh pr merge NUMBER --squash --delete-branch
```

## Rebase Workflow

```bash
# Fetch latest main
git fetch origin main

# Rebase current branch onto main
git rebase origin/main

# Force push after rebase (safe version)
git push --force-with-lease

# If conflicts during rebase:
# 1. Fix conflicts
git add <fixed-files>
git rebase --continue
# Or abort:
git rebase --abort
```

## Branch Cleanup

```bash
# Delete local branch
git branch -D fix/NAME

# Sync main after merges
git checkout main && git pull

# Verify clean state
git worktree list
git branch
```

## Process Monitoring

```bash
# Check for orphaned processes
ps aux | grep -E "(node|cargo|npm)"

# Kill specific process
kill <PID>
```
