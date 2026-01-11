# Git Worktree Patterns

Git worktrees allow you to check out multiple branches simultaneously in different directories. This guide covers common patterns and best practices.

## What Are Worktrees?

A worktree is an additional working directory linked to your repository. Each worktree can have a different branch checked out, enabling parallel development without stashing or switching branches.

```bash
# Repository structure with worktrees
/home/user/
├── project/                    # Main worktree (main branch)
│   └── .git/                   # Shared git directory
└── worktrees/
    ├── feature-auth/           # Worktree (feature/auth branch)
    ├── hotfix-urgent/          # Worktree (hotfix/urgent branch)
    └── pr-review/              # Worktree (review-branch)
```

## Basic Commands

### Create Worktree

```bash
# New branch in new worktree
git worktree add -b feature/new-feature ../worktrees/new-feature main

# Existing branch in new worktree
git worktree add ../worktrees/auth feature/auth

# From remote branch
git worktree add ../worktrees/pr-123 origin/pr-123
```

### List Worktrees

```bash
git worktree list
# /home/user/project              abc1234 [main]
# /home/user/worktrees/auth       def5678 [feature/auth]
# /home/user/worktrees/hotfix     ghi9012 [hotfix/urgent]
```

### Remove Worktree

```bash
# Remove worktree (keeps branch)
git worktree remove ../worktrees/auth

# Force remove (even if dirty)
git worktree remove --force ../worktrees/auth

# Clean up stale references
git worktree prune
```

### Move Worktree

```bash
git worktree move ../worktrees/old-path ../worktrees/new-path
```

## Common Patterns

### Pattern 1: Emergency Hotfix

**Scenario**: You're working on a feature but need to fix a critical bug.

```bash
# You're in: /project on feature/big-feature with uncommitted changes

# Create isolated hotfix worktree
git worktree add -b hotfix/critical-bug ../worktrees/hotfix main

# Switch to hotfix
cd ../worktrees/hotfix

# Fix the bug, commit, create PR
git add .
git commit -m "fix(core): resolve critical memory leak"
git push -u origin hotfix/critical-bug

# Merge hotfix (via PR)
gh pr create --base main

# Return to feature work (unchanged!)
cd ../project

# Clean up after merge
git worktree remove ../worktrees/hotfix
git branch -d hotfix/critical-bug
```

**Benefits:**
- No stashing required
- Feature work untouched
- Complete isolation

### Pattern 2: PR Review

**Scenario**: Review a colleague's PR without losing your current work.

```bash
# Create worktree for the PR branch
git fetch origin pull/123/head:pr-123
git worktree add ../worktrees/pr-123 pr-123

# Navigate and review
cd ../worktrees/pr-123

# Run tests, examine code
npm test
npm start

# Add review comments via GitHub
gh pr review 123 --comment --body "Looks good!"

# Return to your work
cd ../project

# Clean up
git worktree remove ../worktrees/pr-123
git branch -D pr-123
```

### Pattern 3: Release Preparation

**Scenario**: Prepare a release while features continue on develop.

```bash
# Create release worktree
git worktree add -b release/2.0.0 ../worktrees/release-2.0.0 develop

# Work on release
cd ../worktrees/release-2.0.0

# Bump version, update changelog, final fixes
npm version 2.0.0 --no-git-tag-version
# Edit CHANGELOG.md
git commit -am "chore(release): prepare 2.0.0"

# Meanwhile, team continues on develop in main worktree

# Finish release
git checkout main
git merge --no-ff release/2.0.0
git tag v2.0.0
git checkout develop
git merge --no-ff release/2.0.0
git push origin main develop --tags

# Clean up
cd ../project
git worktree remove ../worktrees/release-2.0.0
```

### Pattern 4: Parallel Feature Development

**Scenario**: Work on multiple related features simultaneously.

```bash
# Create worktrees for each feature
git worktree add -b feature/auth ../worktrees/auth develop
git worktree add -b feature/api ../worktrees/api develop
git worktree add -b feature/ui ../worktrees/ui develop

# Work on each as needed
cd ../worktrees/auth
# ... auth work ...

cd ../worktrees/api
# ... api work ...

# They can even depend on each other
cd ../worktrees/ui
git merge ../worktrees/api  # Get API changes
```

### Pattern 5: Testing Different Branches

**Scenario**: Compare behavior between branches.

```bash
# Worktree for main/production
git worktree add ../worktrees/prod main

# Worktree for feature
git worktree add ../worktrees/feature feature/new-ui

# Run both simultaneously
cd ../worktrees/prod && npm start -- --port 3000 &
cd ../worktrees/feature && npm start -- --port 3001 &

# Compare in browser
open http://localhost:3000  # Production
open http://localhost:3001  # Feature
```

### Pattern 6: Documentation Updates

**Scenario**: Update docs for a release without affecting development.

```bash
# Create docs worktree from release tag
git worktree add ../worktrees/docs v2.0.0 --detach

# Or from a docs branch
git worktree add -b docs/update-api ../worktrees/docs main

# Update documentation
cd ../worktrees/docs
# Edit docs...
git commit -am "docs: update API documentation for v2.0.0"
```

## Best Practices

### Directory Organization

```bash
# Recommended structure
~/projects/
├── my-project/              # Main worktree (usually on develop or main)
│   ├── .git/
│   └── ...
└── worktrees/
    └── my-project/
        ├── hotfix/          # Hotfix worktrees
        ├── release/         # Release worktrees
        ├── review/          # PR review worktrees
        └── feature/         # Feature worktrees (if needed)
```

### Naming Conventions

```bash
# Clear, consistent naming
../worktrees/hotfix-security-patch
../worktrees/release-2.0.0
../worktrees/pr-123-review
../worktrees/feature-auth
```

### Cleanup Routine

```bash
# Regular cleanup script
#!/bin/bash

# List all worktrees
git worktree list

# Remove worktrees for merged branches
for worktree in $(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do
  branch=$(git -C "$worktree" branch --show-current)
  if git branch --merged main | grep -q "$branch"; then
    echo "Removing merged worktree: $worktree ($branch)"
    git worktree remove "$worktree"
    git branch -d "$branch"
  fi
done

# Prune stale entries
git worktree prune
```

### Configuration Tips

```bash
# Add worktrees to global gitignore
echo "worktrees/" >> ~/.gitignore_global
git config --global core.excludesfile ~/.gitignore_global

# Set up aliases
git config --global alias.wt "worktree"
git config --global alias.wta "worktree add"
git config --global alias.wtl "worktree list"
git config --global alias.wtr "worktree remove"
```

## Integration with Strategies

### Gitflow + Worktrees

```bash
# Release branch in dedicated worktree
git worktree add -b release/2.0.0 ../worktrees/release develop

# Hotfix in isolated worktree
git worktree add -b hotfix/critical ../worktrees/hotfix main

# Support branch for old version
git worktree add -b support/1.x ../worktrees/support-1.x v1.5.0
```

### GitHub Flow + Worktrees

```bash
# PR reviews in worktrees
git worktree add ../worktrees/pr-123 origin/feature/auth

# Emergency fixes
git worktree add -b fix/urgent ../worktrees/hotfix main
```

## Common Issues

### Issue: "Branch already checked out"

```bash
# Error
fatal: 'feature/auth' is already checked out at '/project'

# Solution 1: Use different branch
git worktree add ../worktrees/auth-review feature/auth-backup

# Solution 2: Detach in main worktree first
cd /project
git checkout --detach
cd -
git worktree add ../worktrees/auth feature/auth
```

### Issue: Stale Worktree References

```bash
# Error
fatal: '/old/path' is a worktree but the directory does not exist

# Solution
git worktree prune
```

### Issue: Deleted Branch in Worktree

```bash
# Error when trying to remove
Cannot remove worktree with a branch that no longer exists

# Solution
cd ../worktrees/broken
git checkout --detach
cd -
git worktree remove ../worktrees/broken
```

### Issue: Worktree in Dirty State

```bash
# Error
Cannot remove worktree with uncommitted changes

# Solution 1: Commit or stash changes
cd ../worktrees/dirty
git stash

# Solution 2: Force remove
git worktree remove --force ../worktrees/dirty
```

## Advanced Usage

### Bare Repository + Worktrees

For maximum flexibility, use a bare repository:

```bash
# Clone as bare
git clone --bare repo.git

# All branches are worktrees
cd repo.git
git worktree add ../main main
git worktree add ../develop develop
git worktree add ../feature-auth feature/auth
```

### Shared Git Hooks

All worktrees share the same hooks:

```bash
# Hooks are in the shared .git directory
ls /project/.git/hooks/

# They apply to all worktrees automatically
```

### Per-Worktree Configuration

```bash
# Set worktree-specific config
cd ../worktrees/feature
git config --worktree user.email "test@example.com"
```

## Automation Scripts

### Create Worktree Helper

```python
#!/usr/bin/env python3
# worktree-helper.py

import subprocess
import sys
import os

def create_worktree(branch_type, name):
    base_dir = "../worktrees"

    if branch_type == "feature":
        base = "develop"
        branch = f"feature/{name}"
    elif branch_type == "hotfix":
        base = "main"
        branch = f"hotfix/{name}"
    elif branch_type == "release":
        base = "develop"
        branch = f"release/{name}"
    else:
        print(f"Unknown type: {branch_type}")
        sys.exit(1)

    path = f"{base_dir}/{branch_type}-{name}"

    # Create worktree
    subprocess.run([
        "git", "worktree", "add",
        "-b", branch, path, base
    ])

    print(f"Created worktree: {path}")
    print(f"Branch: {branch}")
    print(f"cd {path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: worktree-helper.py <type> <name>")
        sys.exit(1)
    create_worktree(sys.argv[1], sys.argv[2])
```

### Cleanup Script

```bash
#!/bin/bash
# cleanup-worktrees.sh

echo "Current worktrees:"
git worktree list

echo ""
echo "Checking for merged branches..."

for worktree in $(git worktree list --porcelain | grep "^worktree" | awk '{print $2}'); do
    if [ "$worktree" = "$(pwd)" ]; then
        continue
    fi

    branch=$(git -C "$worktree" rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ -z "$branch" ] || [ "$branch" = "HEAD" ]; then
        continue
    fi

    if git branch --merged main | grep -q "$branch"; then
        echo "Merged: $worktree ($branch)"
        read -p "Remove? [y/N] " confirm
        if [ "$confirm" = "y" ]; then
            git worktree remove "$worktree"
            git branch -d "$branch"
        fi
    fi
done

echo ""
echo "Pruning stale references..."
git worktree prune

echo "Done!"
```

## Related Resources

- [branching-strategies.md](./branching-strategies.md) - Strategy overview
- [gitflow-guide.md](./gitflow-guide.md) - Gitflow with worktrees
- [github-flow-guide.md](./github-flow-guide.md) - GitHub Flow patterns
