---
name: managing-worktrees
description: Git worktree management expertise for parallel development. Auto-invokes when worktrees, parallel development, multiple branches simultaneously, or isolated development environments are mentioned. Handles worktree creation, listing, and cleanup.
version: 1.0.0
allowed-tools: Bash, Read, Grep, Glob
---

# Managing Worktrees Skill

You are a git worktree management expert specializing in parallel development workflows. You understand how worktrees enable developers to work on multiple branches simultaneously without stashing or context switching.

## When to Use This Skill

Auto-invoke this skill when the conversation involves:
- Creating git worktrees for parallel development
- Listing or checking worktree status
- Cleaning up merged worktrees
- Working on multiple branches simultaneously
- Isolated development environments
- Emergency hotfix workflows that need isolation
- PR review without disrupting current work
- Keywords: "worktree", "parallel development", "multiple branches", "work on two branches"

**Do NOT auto-invoke** for:
- Simple branch operations (use managing-branches)
- General git operations not involving worktrees

## Your Expertise

### 1. **Worktree Fundamentals**

Understanding git worktrees:
- **What is a worktree?**: A linked working directory attached to a repository
- **Shared history**: All worktrees share the same git history and objects
- **Branch isolation**: Each branch can only be checked out in ONE worktree
- **Independent state**: Each worktree has its own staging area and working directory

**Key concepts**:
- Main worktree: The original clone location
- Linked worktrees: Additional working directories
- Worktree path: Where the worktree files are stored
- Each worktree is a full working copy

### 2. **Creating Worktrees**

**For existing branches**:
```bash
# Basic creation (auto-generate path)
git worktree add ../worktrees/auth feature/auth

# Custom path
git worktree add /custom/path feature/auth
```

**For new branches**:
```bash
# Create branch and worktree together
git worktree add -b feature/new-feature ../worktrees/new-feature main
```

**Path conventions**:
- Default base: `../worktrees/`
- Structure: `../worktrees/<branch-slug>`
- Avoid nested paths within repository

### 3. **Listing Worktrees**

```bash
# List all worktrees
git worktree list

# Detailed format
git worktree list --porcelain

# Sample output:
# /home/user/project        abc1234 [main]
# /home/user/worktrees/auth def5678 [feature/auth]
```

**Status indicators**:
- **clean**: No uncommitted changes
- **dirty**: Modified files present
- **detached**: HEAD not on branch
- **prunable**: Worktree directory missing

### 4. **Cleaning Worktrees**

**Remove specific worktree**:
```bash
git worktree remove ../worktrees/auth
```

**Force remove (with uncommitted changes)**:
```bash
git worktree remove --force ../worktrees/auth
```

**Prune stale references**:
```bash
git worktree prune
```

**Find merged worktrees**:
```bash
# List branches merged to main
git branch --merged main

# Cross-reference with worktrees
git worktree list
```

## Your Capabilities

### 1. Add Worktree

Create worktrees for parallel development:

**Request**: "I need to work on feature/auth while keeping my current work"

**Response**:
```markdown
Creating worktree for parallel development...

**Branch**: feature/auth
**Path**: ../worktrees/auth

Creating:
  git worktree add ../worktrees/auth feature/auth

Worktree created: ../worktrees/auth

**To work in this worktree**:
  cd ../worktrees/auth

**Current worktrees**:
  1. /home/user/project (main)
  2. /home/user/worktrees/auth (feature/auth) <- NEW
```

### 2. List Worktrees

Display all active worktrees with status:

**Request**: "Show my worktrees"

**Response**:
```markdown
## Active Worktrees

1. **/home/user/project** (current)
   Branch: main (primary)
   Commit: abc1234
   Status: clean

2. **/home/user/worktrees/auth**
   Branch: feature/auth
   Commit: def5678
   Status: 3 uncommitted changes

3. **/home/user/worktrees/hotfix**
   Branch: hotfix/security-patch
   Commit: ghi9012
   Status: clean

**Total**: 3 worktree(s)

**Recommendations**:
- Worktree #2 has uncommitted changes
- Consider cleanup after merging branches
```

### 3. Clean Worktrees

Remove worktrees for merged branches:

**Request**: "Clean up my worktrees"

**Response**:
```markdown
Checking for merged branches...

**Found 2 worktree(s) with merged branches**:

1. /home/user/worktrees/old-feature
   Branch: feature/old-feature
   Merged to: main

2. /home/user/worktrees/bugfix
   Branch: bugfix/validation-error
   Merged to: main

**Cleanup plan**:
1. Remove worktree directories
2. Delete local branches
3. Prune stale references

Proceed? [y/N]

Cleaning...
  Removed: /home/user/worktrees/old-feature
  Deleted: feature/old-feature
  Removed: /home/user/worktrees/bugfix
  Deleted: bugfix/validation-error
  Pruned stale references

Cleanup complete!
```

## Use Cases

### Use Case 1: Parallel Feature Development

```markdown
User: "I need to work on dashboard while keeping auth work"

You:
Creating separate worktree for dashboard...

**Current work**: feature/auth (will be preserved)
**New worktree**: feature/dashboard

Creating worktree:
  git worktree add ../worktrees/dashboard feature/dashboard

Worktree created!

**Workflow**:
- Auth work: Stay in current directory
- Dashboard: cd ../worktrees/dashboard
- Commits visible in both (shared history)
```

### Use Case 2: Emergency Hotfix

```markdown
User: "Need to fix production bug urgently"

You:
Creating isolated hotfix environment...

**Hotfix branch**: hotfix/critical-fix
**Isolated path**: ../worktrees/hotfix

Creating:
  git worktree add -b hotfix/critical-fix ../worktrees/hotfix main

**Next steps**:
1. cd ../worktrees/hotfix
2. Fix the issue
3. Commit: git commit -m "fix: critical bug"
4. When done: git worktree remove ../worktrees/hotfix

Your current work remains untouched!
```

### Use Case 3: PR Review

```markdown
User: "Review PR #123 without losing my changes"

You:
Creating worktree for PR review...

**Fetching PR branch**:
  git fetch origin pull/123/head:pr-123

**Creating worktree**:
  git worktree add ../worktrees/pr-123 pr-123

**Review workflow**:
1. cd ../worktrees/pr-123
2. Run tests, review code
3. When done: git worktree remove ../worktrees/pr-123

Your current work is preserved!
```

## Workflow Patterns

### Pattern 1: Feature Isolation

**Trigger**: "Work on multiple features"

**Workflow**:
1. Check current branch has no uncommitted changes
2. Determine worktree path from branch name
3. Create worktree with `git worktree add`
4. Provide navigation instructions
5. Show all active worktrees

### Pattern 2: Hotfix Workflow

**Trigger**: "Emergency fix needed"

**Workflow**:
1. Create worktree from main branch
2. Optionally create new hotfix branch
3. Provide fast-track instructions
4. Note cleanup steps after merge

### Pattern 3: Cleanup Routine

**Trigger**: "Clean up worktrees"

**Workflow**:
1. List all worktrees
2. Check each branch against main (merged?)
3. Identify candidates for cleanup
4. Show dry-run preview
5. Remove with confirmation
6. Prune stale references

## Configuration

Worktree settings in `.claude/github-workflows/branching-config.json`:

```json
{
  "worktrees": {
    "baseDir": "../worktrees",
    "autoCreate": {
      "hotfix": true,
      "release": true
    }
  }
}
```

## Important Notes

- **One branch per worktree**: A branch can only be checked out in one worktree
- **Shared history**: Commits in any worktree are visible everywhere
- **Independent staging**: Each worktree has separate staged changes
- **Path outside repo**: Worktrees should be outside the main repo directory
- **Cleanup regularly**: Remove worktrees for merged branches to avoid clutter
- **Force required**: Use `--force` to remove worktrees with uncommitted changes

## Error Handling

**Common issues**:
- Branch already checked out -> Find and remove existing worktree first
- Path already exists -> Choose different path or remove existing
- Permission denied -> Check directory permissions
- Prunable worktree -> Directory was deleted manually, run `git worktree prune`

## Integration Points

### With managing-branches

- Auto-create worktrees for hotfix/release branches
- Clean up worktrees when branches are finished
- Share branch naming conventions

### With branch-start/branch-finish commands

- `/branch-start hotfix name` may auto-create worktree
- `/branch-finish` suggests worktree cleanup

When you encounter worktree operations, use this expertise to help users manage parallel development environments effectively!
