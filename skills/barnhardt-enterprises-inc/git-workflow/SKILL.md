---
name: git-workflow
description: Git workflow with worktrees and conventional commits.
---

# Git Workflow

## Branch Naming

```
feature/{issue}-{slug}   # New features
fix/{issue}-{slug}       # Bug fixes
refactor/{issue}-{slug}  # Code refactoring
docs/{issue}-{slug}      # Documentation
test/{issue}-{slug}      # Test additions
```

Examples:
- `feature/42-user-authentication`
- `fix/57-login-redirect-loop`
- `refactor/63-extract-api-client`

## Conventional Commits

```
feat: add user authentication
fix: resolve login redirect loop
refactor: extract API client
docs: update README with setup instructions
test: add unit tests for auth service
chore: update dependencies
```

With scope:
```
feat(auth): add OAuth2 support
fix(api): handle rate limit errors
refactor(ui): extract button component
```

Breaking changes:
```
feat!: change authentication API
feat(auth)!: remove password login
```

## Worktrees

```bash
# Create worktree for feature
git worktree add ../worktrees/feature-42-auth -b feature/42-auth

# List worktrees
git worktree list

# Remove worktree when done
git worktree remove ../worktrees/feature-42-auth

# Prune stale worktrees
git worktree prune
```

## Workflow Steps

### 1. Create Issue
```bash
gh issue create --title "Add user authentication" --body "..."
# Note the issue number (e.g., #42)
```

### 2. Create Branch in Worktree
```bash
git worktree add ../worktrees/feature-42-auth -b feature/42-auth
cd ../worktrees/feature-42-auth
```

### 3. Develop
```bash
# Make changes...
git add .
git commit -m "feat(auth): add login form component"
git commit -m "feat(auth): add authentication API"
git commit -m "test(auth): add unit tests for auth"
```

### 4. Push and Create PR
```bash
git push -u origin feature/42-auth
gh pr create --title "feat: add user authentication" --body "Closes #42"
```

### 5. Cleanup After Merge
```bash
cd ..  # Back to main repo
git worktree remove ../worktrees/feature-42-auth
git branch -d feature/42-auth
```

## Rebase Workflow

```bash
# Keep branch up to date with main
git fetch origin
git rebase origin/main

# Interactive rebase to clean up commits
git rebase -i origin/main
```

## Stashing

```bash
# Stash changes
git stash push -m "WIP: auth feature"

# List stashes
git stash list

# Apply and drop
git stash pop

# Apply specific stash
git stash apply stash@{1}
```

## Useful Aliases

```bash
# .gitconfig
[alias]
  co = checkout
  br = branch
  ci = commit
  st = status
  wt = worktree
  lg = log --oneline --graph --decorate
  last = log -1 HEAD
  unstage = reset HEAD --
```

## Protected Branch Rules

Main branch should have:
- Require pull request reviews
- Require status checks to pass
- Require linear history
- Do not allow force pushes
