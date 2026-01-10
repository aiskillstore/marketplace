# Advanced Git Operations

Git bisect, cherry-pick, worktrees, reflog, and conflict resolution.

## Git Bisect

Find the commit that introduced a bug using binary search.

### Basic Bisect

```bash
# Start bisect
git bisect start

# Mark current commit as bad
git bisect bad

# Mark known good commit
git bisect good v1.0.0

# Git checks out middle commit, test it, then:
git bisect good  # if this commit is OK
git bisect bad   # if this commit has the bug

# Repeat until git finds the culprit
# "abc123 is the first bad commit"

# End bisect session
git bisect reset
```

### Automated Bisect

```bash
# Run a test script automatically
git bisect start HEAD v1.0.0
git bisect run npm test
# Git will find first failing commit automatically

# With custom script
git bisect run ./test-for-bug.sh
# Script should exit 0 (good) or 1 (bad)
```

### Bisect Commands

```bash
# Skip current commit (can't test it)
git bisect skip

# View bisect log
git bisect log

# Replay a bisect session
git bisect replay bisect.log

# Visualize remaining commits
git bisect visualize
```

---

## Cherry-Pick

Apply specific commits to current branch.

```bash
# Apply single commit
git cherry-pick abc123

# Apply multiple commits
git cherry-pick abc123 def456

# Apply range of commits (exclusive start)
git cherry-pick abc123..xyz789

# Apply range (inclusive)
git cherry-pick abc123^..xyz789
```

### Cherry-Pick Options

```bash
# Stage only, don't commit
git cherry-pick -n abc123

# Edit commit message
git cherry-pick -e abc123

# Record original commit in message
git cherry-pick -x abc123
# Adds: "(cherry picked from commit abc123)"

# Preserve original author
git cherry-pick --signoff abc123
```

### Handling Conflicts

```bash
# Continue after resolving conflicts
git cherry-pick --continue

# Abort cherry-pick
git cherry-pick --abort

# Skip current commit
git cherry-pick --skip
```

---

## Worktrees

Work on multiple branches simultaneously without stashing.

```bash
# Create worktree for existing branch
git worktree add ../project-hotfix hotfix-branch

# Create worktree with new branch
git worktree add ../project-feature -b new-feature

# Create worktree from specific commit
git worktree add ../project-v1 v1.0.0

# List worktrees
git worktree list

# Remove worktree
git worktree remove ../project-hotfix

# Prune stale worktree info
git worktree prune
```

### Worktree Workflow

```bash
# Main repo at ~/project
# Need to work on hotfix while keeping feature work
cd ~/project
git worktree add ~/project-hotfix hotfix-branch

# Work in hotfix
cd ~/project-hotfix
# ... make fixes, commit, push ...

# Back to main work
cd ~/project
git worktree remove ~/project-hotfix
```

---

## Reflog (Recovery)

Find and recover "lost" commits.

```bash
# Show reflog (all HEAD movements)
git reflog

# Show reflog for specific branch
git reflog show feature-branch

# Show reflog with dates
git reflog --date=relative
```

### Recovery Scenarios

#### Recover Deleted Branch

```bash
git reflog
# Find commit hash before deletion
git checkout -b recovered-branch abc123
```

#### Undo a Rebase

```bash
git reflog
# Find commit before rebase started (look for "rebase: start")
git reset --hard HEAD@{5}
```

#### Recover After Hard Reset

```bash
git reflog
# Find the commit you want
git reset --hard HEAD@{1}
```

#### Find Lost Commits

```bash
# Show all dangling commits
git fsck --lost-found

# Check reflog for specific date
git reflog --date=local | grep "Dec 15"
```

---

## Conflict Resolution

```bash
# See which files have conflicts
git status

# View conflict markers in file
cat file.txt
# <<<<<<< HEAD
# your changes
# =======
# their changes
# >>>>>>> branch-name
```

### Resolution Strategies

```bash
# Use merge tool
git mergetool

# Accept all changes from one side
git checkout --ours file.txt    # Keep current branch
git checkout --theirs file.txt  # Keep incoming branch

# Accept both (for non-overlapping changes)
git checkout --merge file.txt
```

### After Resolving

```bash
# Stage resolved file
git add file.txt

# Continue operation
git rebase --continue   # During rebase
git merge --continue    # During merge
git cherry-pick --continue  # During cherry-pick
```

### Conflict Prevention

```bash
# Before merging, check for conflicts
git merge --no-commit --no-ff feature-branch
git diff --cached  # Review what would be merged
git merge --abort  # If you don't want to proceed

# Rebase frequently to avoid big conflicts
git fetch origin
git rebase origin/main
```
