# Interactive Rebase Patterns

Clean up commit history before merging.

## Basic Rebase

```bash
# Rebase last N commits
git rebase -i HEAD~5

# Rebase onto main
git rebase -i main

# Commands in interactive rebase:
# pick   - use commit as-is
# reword - edit commit message
# edit   - stop to amend commit
# squash - meld into previous commit (keep message)
# fixup  - meld into previous (discard message)
# drop   - remove commit
```

## Common Rebase Workflows

### Squash Feature Commits

```bash
# Squash all feature commits into one
git rebase -i main
# Change all but first 'pick' to 'squash'

# Example edit:
# pick abc123 Add feature base
# squash def456 Fix typo
# squash ghi789 Add tests
# squash jkl012 Polish UI
```

### Reorder Commits

```bash
git rebase -i HEAD~3
# Move lines to change order

# Before:
# pick abc123 Add tests
# pick def456 Add feature
# pick ghi789 Fix bug

# After (reordered):
# pick def456 Add feature
# pick ghi789 Fix bug
# pick abc123 Add tests
```

### Edit a Commit Mid-History

```bash
git rebase -i HEAD~5
# Change 'pick' to 'edit' for target commit

# Git stops at that commit
# Make changes
git add .
git commit --amend
git rebase --continue
```

### Split a Commit

```bash
git rebase -i HEAD~3
# Change 'pick' to 'edit' for commit to split

# Git stops at that commit
git reset HEAD^  # Undo commit but keep changes
git add file1.js
git commit -m "Part 1: Add file1"
git add file2.js
git commit -m "Part 2: Add file2"
git rebase --continue
```

## Rebase Safety

```bash
# Continue after resolving conflicts
git rebase --continue

# Skip current commit (use with caution)
git rebase --skip

# Abort if things go wrong
git rebase --abort

# Check reflog if you need to recover
git reflog
```

## Rebase vs Merge

| Scenario | Use |
|----------|-----|
| Feature branch → main | Rebase for clean history |
| Shared/public branches | Merge (don't rewrite history) |
| Long-lived feature branch | Rebase onto main periodically |
| After code review changes | Rebase to clean up |

## Autosquash

```bash
# Create fixup commit (will auto-squash)
git commit --fixup=abc123

# Create squash commit with message
git commit --squash=abc123

# Rebase with autosquash
git rebase -i --autosquash main
# Fixup commits auto-positioned after their targets
```

## Rebase Configuration

```bash
# Enable autosquash by default
git config --global rebase.autosquash true

# Use vim for rebase editor
git config --global sequence.editor vim

# Preserve merge commits during rebase
git rebase -i --rebase-merges main
```
