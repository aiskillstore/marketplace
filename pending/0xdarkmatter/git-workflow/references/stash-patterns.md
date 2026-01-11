# Stash Patterns

Save work temporarily without committing.

## Basic Stash Operations

```bash
# Save current changes
git stash

# Save with description
git stash push -m "WIP: feature X"

# Stash including untracked files
git stash -u

# Stash including ignored files
git stash -a

# Stash only staged changes
git stash push --staged
```

## Managing Stashes

```bash
# List all stashes
git stash list

# Show stash contents (summary)
git stash show stash@{0}

# Show stash contents (full diff)
git stash show -p stash@{0}

# Show stash with stats
git stash show --stat stash@{0}
```

## Applying Stashes

```bash
# Apply most recent stash (keep in stash list)
git stash apply

# Apply and remove from list
git stash pop

# Apply specific stash
git stash apply stash@{2}

# Apply specific stash and drop
git stash pop stash@{2}
```

## Removing Stashes

```bash
# Drop specific stash
git stash drop stash@{1}

# Drop most recent stash
git stash drop

# Clear all stashes
git stash clear
```

## Common Workflows

### Switch Branches Mid-Work

```bash
# Mid-feature, need to switch branches
git stash push -m "WIP: auth flow"
git checkout hotfix-branch
# ... fix bug, commit, push ...
git checkout feature-branch
git stash pop
```

### Partial Stashing

```bash
# Stash specific files
git stash push -m "WIP" -- file1.js file2.js

# Interactive stash (select hunks)
git stash push -p
# y - stash this hunk
# n - don't stash this hunk
# s - split into smaller hunks
# q - quit (stash selected hunks)
```

### Stash to Branch

```bash
# Create branch from stash
git stash branch new-feature stash@{0}
# Creates branch, checks it out, applies stash, drops stash
```

### Apply Stash to Different Branch

```bash
git checkout target-branch
git stash apply stash@{1}
# Resolve any conflicts
git add .
git commit
```

## Stash Conflicts

```bash
# If stash apply/pop has conflicts
git stash apply
# CONFLICT messages appear

# Resolve conflicts manually, then
git add .
git stash drop  # Remove the stash after resolving

# Or abort and keep stash
git checkout -- .  # Discard changes
```

## Tips

```bash
# Always use descriptive messages
git stash push -m "WIP: halfway through refactoring auth"

# Check what's in stash before applying
git stash show -p stash@{0}

# Don't let stash list grow too long
git stash list  # Review periodically
git stash drop stash@{5}  # Clean old stashes
```
