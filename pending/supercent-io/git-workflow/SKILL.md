---
name: git-workflow
description: Manage Git workflows including commits, branches, merges, and collaboration. Use when working with Git repositories, creating commits, managing branches, or resolving conflicts.
metadata:
  tags: git, version-control, branching, commits, collaboration
  platforms: Claude, ChatGPT, Gemini
---


# Git Workflow

## When to use this skill
- Creating meaningful commit messages
- Managing branches
- Merging code
- Resolving conflicts
- Collaborating with team
- Git best practices

## Instructions

### Step 1: Branch management

**Create feature branch**:
```bash
# Create and switch to new branch
git checkout -b feature/feature-name

# Or create from specific commit
git checkout -b feature/feature-name <commit-hash>
```

**Naming conventions**:
- `feature/description`: New features
- `bugfix/description`: Bug fixes
- `hotfix/description`: Urgent fixes
- `refactor/description`: Code refactoring
- `docs/description`: Documentation updates

### Step 2: Making changes

**Stage changes**:
```bash
# Stage specific files
git add file1.py file2.js

# Stage all changes
git add .

# Stage with patch mode (interactive)
git add -p
```

**Check status**:
```bash
# See what's changed
git status

# See detailed diff
git diff

# See staged diff
git diff --staged
```

### Step 3: Committing

**Write good commit messages**:
```bash
git commit -m "type(scope): subject

Detailed description of what changed and why.

- Change 1
- Change 2

Fixes #123"
```

**Commit types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, no code change
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Example**:
```bash
git commit -m "feat(auth): add JWT authentication

- Implement JWT token generation
- Add token validation middleware
- Update user model with refresh token

Closes #42"
```

### Step 4: Pushing changes

```bash
# Push to remote
git push origin feature/feature-name

# Force push (use with caution!)
git push origin feature/feature-name --force-with-lease

# Set upstream and push
git push -u origin feature/feature-name
```

### Step 5: Pulling and updating

```bash
# Pull latest changes
git pull origin main

# Pull with rebase (cleaner history)
git pull --rebase origin main

# Fetch without merging
git fetch origin
```

### Step 6: Merging

**Merge feature branch**:
```bash
# Switch to main branch
git checkout main

# Merge feature
git merge feature/feature-name

# Merge with no fast-forward (creates merge commit)
git merge --no-ff feature/feature-name
```

**Rebase instead of merge**:
```bash
# On feature branch
git checkout feature/feature-name

# Rebase onto main
git rebase main

# Continue after resolving conflicts
git rebase --continue

# Abort rebase
git rebase --abort
```

### Step 7: Resolving conflicts

**When conflicts occur**:
```bash
# See conflicted files
git status

# Open files and resolve conflicts
# Look for markers:
<<<<<<< HEAD
Current branch code
=======
Incoming branch code
>>>>>>> feature-branch

# After resolving
git add <resolved-files>
git commit  # For merge
git rebase --continue  # For rebase
```

### Step 8: Cleaning up

```bash
# Delete local branch
git branch -d feature/feature-name

# Force delete
git branch -D feature/feature-name

# Delete remote branch
git push origin --delete feature/feature-name

# Clean up stale references
git fetch --prune
```

## Advanced workflows

### Interactive rebase

```bash
# Rebase last 3 commits
git rebase -i HEAD~3

# Commands in editor:
# pick: use commit
# reword: change commit message
# edit: amend commit
# squash: combine with previous
# fixup: like squash, discard message
# drop: remove commit
```

### Stashing changes

```bash
# Stash current changes
git stash

# Stash with message
git stash save "Work in progress on feature X"

# List stashes
git stash list

# Apply most recent stash
git stash apply

# Apply and remove stash
git stash pop

# Apply specific stash
git stash apply stash@{2}

# Drop stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

### Cherry-picking

```bash
# Apply specific commit
git cherry-pick <commit-hash>

# Cherry-pick multiple commits
git cherry-pick <hash1> <hash2> <hash3>

# Cherry-pick without committing
git cherry-pick -n <commit-hash>
```

### Bisect (finding bugs)

```bash
# Start bisect
git bisect start

# Mark current as bad
git bisect bad

# Mark known good commit
git bisect good <commit-hash>

# Git will checkout commits to test
# Test and mark each:
git bisect good  # if works
git bisect bad   # if broken

# When found, reset
git bisect reset
```

## Examples

### Example 1: Feature development workflow

```bash
# 1. Create feature branch
git checkout main
git pull origin main
git checkout -b feature/user-profile

# 2. Make changes
# ... edit files ...

# 3. Commit changes
git add src/profile/
git commit -m "feat(profile): add user profile page

- Create profile component
- Add profile API endpoints
- Add profile tests"

# 4. Keep up to date with main
git fetch origin
git rebase origin/main

# 5. Push to remote
git push origin feature/user-profile

# 6. Create Pull Request on GitHub/GitLab
# ... after review and approval ...

# 7. Merge and cleanup
git checkout main
git pull origin main
git branch -d feature/user-profile
```

### Example 2: Hotfix workflow

```bash
# 1. Create hotfix branch from production
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Fix the bug
# ... make fixes ...

# 3. Commit
git add .
git commit -m "hotfix: fix critical login bug

Fixes authentication bypass vulnerability

Fixes #999"

# 4. Push and merge immediately
git push origin hotfix/critical-bug

# After merge:
# 5. Cleanup
git checkout main
git pull origin main
git branch -d hotfix/critical-bug
```

### Example 3: Collaborative workflow

```bash
# 1. Update main branch
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Regular updates from main
git fetch origin
git rebase origin/main

# 4. Push your work
git push origin feature/new-feature

# 5. If teammate made changes to your branch
git pull origin feature/new-feature --rebase

# 6. Resolve any conflicts
# ... resolve conflicts ...
git add .
git rebase --continue

# 7. Force push after rebase
git push origin feature/new-feature --force-with-lease
```

## Best practices

1. **Commit often**: Small, focused commits
2. **Meaningful messages**: Explain what and why
3. **Pull before push**: Stay updated
4. **Review before commit**: Check what you're committing
5. **Use branches**: Never commit directly to main
6. **Keep history clean**: Rebase feature branches
7. **Test before push**: Run tests locally
8. **Write descriptive branch names**: Easy to understand
9. **Delete merged branches**: Keep repository clean
10. **Use .gitignore**: Don't commit generated files

## Common patterns

### Undo last commit (keep changes)

```bash
git reset --soft HEAD~1
```

### Undo last commit (discard changes)

```bash
git reset --hard HEAD~1
```

### Amend last commit

```bash
# Change commit message
git commit --amend -m "New message"

# Add files to last commit
git add forgotten-file.txt
git commit --amend --no-edit
```

### View history

```bash
# Detailed log
git log

# One line per commit
git log --oneline

# With graph
git log --oneline --graph --all

# Last 5 commits
git log -5

# Commits by author
git log --author="John"

# Commits in date range
git log --since="2 weeks ago"
```

### Find commits

```bash
# Search commit messages
git log --grep="keyword"

# Search code changes
git log -S "function_name"

# Show file history
git log --follow -- path/to/file
```

## Troubleshooting

### Accidentally committed to wrong branch

```bash
# 1. Create correct branch from current state
git branch feature/correct-branch

# 2. Reset current branch
git reset --hard HEAD~1

# 3. Switch to correct branch
git checkout feature/correct-branch
```

### Need to undo a merge

```bash
# If not pushed yet
git reset --hard HEAD~1

# If already pushed (creates revert commit)
git revert -m 1 <merge-commit-hash>
```

### Recover deleted branch

```bash
# Find lost commit
git reflog

# Create branch from lost commit
git checkout -b recovered-branch <commit-hash>
```

### Sync fork with upstream

```bash
# Add upstream remote
git remote add upstream https://github.com/original/repo.git

# Fetch upstream
git fetch upstream

# Merge upstream main
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

## Git configuration

### User setup

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Aliases

```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.lg 'log --oneline --graph --all'
```

### Editor

```bash
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "vim"           # Vim
```

## References

- [Pro Git Book](https://git-scm.com/book/en/v2)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)