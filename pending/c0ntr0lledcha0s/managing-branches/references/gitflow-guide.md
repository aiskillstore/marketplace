# Gitflow Workflow Guide

Complete guide to implementing and using the Gitflow branching model.

## Overview

Gitflow is a branching model designed around scheduled releases. It assigns specific roles to branches and defines how they interact.

## Branch Types

### Main Branch (`main`)
- **Purpose**: Production-ready code
- **Lifetime**: Permanent
- **Access**: Merge only via release/hotfix
- **Tags**: All releases tagged here

### Develop Branch (`develop`)
- **Purpose**: Integration branch for features
- **Lifetime**: Permanent
- **Access**: Direct commits discouraged, merge via feature/bugfix
- **State**: Latest development changes

### Feature Branches (`feature/*`)
- **Purpose**: New features development
- **Lifetime**: Duration of feature work
- **Base**: `develop`
- **Merge to**: `develop`
- **Naming**: `feature/issue-42-auth`, `feature/user-dashboard`

### Release Branches (`release/*`)
- **Purpose**: Release preparation
- **Lifetime**: Release prep period (1-2 weeks typical)
- **Base**: `develop`
- **Merge to**: `main` AND `develop`
- **Naming**: `release/2.0.0`, `release/2024-Q1`

### Hotfix Branches (`hotfix/*`)
- **Purpose**: Emergency production fixes
- **Lifetime**: Hours to days
- **Base**: `main`
- **Merge to**: `main` AND `develop`
- **Naming**: `hotfix/security-fix`, `hotfix/2.0.1`

### Support Branches (`support/*`) (Optional)
- **Purpose**: Long-term support for old versions
- **Lifetime**: Duration of support contract
- **Base**: Tagged release on `main`
- **Merge to**: Stay separate

## Workflows

### Feature Development

**Starting a feature:**
```bash
# Ensure develop is up to date
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/issue-42-user-auth

# Or with the command
/branch-start feature issue-42-user-auth
```

**Working on a feature:**
```bash
# Make changes and commit
git add .
git commit -m "feat(auth): add login form component"

# Push to remote for backup/collaboration
git push -u origin feature/issue-42-user-auth
```

**Finishing a feature:**
```bash
# Update develop
git checkout develop
git pull origin develop

# Merge feature (with merge commit)
git merge --no-ff feature/issue-42-user-auth

# Push develop
git push origin develop

# Clean up
git branch -d feature/issue-42-user-auth
git push origin --delete feature/issue-42-user-auth

# Or with the command
/branch-finish feature/issue-42-user-auth
```

**Best practices:**
- Keep features small (1-2 weeks max)
- Commit frequently
- Pull from develop regularly to avoid conflicts
- Use `--no-ff` to preserve branch history

### Release Preparation

**Starting a release:**
```bash
# Ensure develop is up to date
git checkout develop
git pull origin develop

# Create release branch
git checkout -b release/2.0.0

# Or with the command
/release-branch 2.0.0
```

**Release preparation tasks:**
1. Bump version numbers
2. Update CHANGELOG
3. Fix last-minute bugs
4. Update documentation
5. Final testing

```bash
# Bump version
npm version 2.0.0 --no-git-tag-version

# Update changelog
# Edit CHANGELOG.md

# Commit changes
git commit -am "chore(release): prepare 2.0.0"
```

**Finishing a release:**
```bash
# Merge to main
git checkout main
git pull origin main
git merge --no-ff release/2.0.0

# Tag the release
git tag -a v2.0.0 -m "Release 2.0.0"

# Merge to develop
git checkout develop
git merge --no-ff release/2.0.0

# Push everything
git push origin main develop --tags

# Clean up
git branch -d release/2.0.0
git push origin --delete release/2.0.0

# Or with the command
/release-finish 2.0.0
```

**Best practices:**
- No new features in release branch
- Only bug fixes and documentation
- Keep release prep short (1-2 weeks)
- Test thoroughly before finishing

### Hotfix Workflow

**Starting a hotfix:**
```bash
# Start from main (production)
git checkout main
git pull origin main

# Create hotfix branch
git checkout -b hotfix/critical-security-fix

# Or with worktree for isolation
git worktree add ../worktrees/hotfix -b hotfix/critical-security-fix main

# Or with the command
/hotfix-start critical-security-fix
```

**Fixing the issue:**
```bash
# Make the fix
git add .
git commit -m "fix(security): patch XSS vulnerability"

# Test thoroughly
npm test
```

**Finishing the hotfix:**
```bash
# Merge to main
git checkout main
git merge --no-ff hotfix/critical-security-fix

# Tag the hotfix
git tag -a v2.0.1 -m "Hotfix 2.0.1"

# Merge to develop (or release if one exists)
git checkout develop
git merge --no-ff hotfix/critical-security-fix

# Push everything
git push origin main develop --tags

# Clean up
git branch -d hotfix/critical-security-fix
git push origin --delete hotfix/critical-security-fix

# Or with the command
/hotfix-finish critical-security-fix
```

**Best practices:**
- Keep hotfixes minimal
- Test on staging before production
- Document in changelog
- Always merge to both main AND develop
- If release branch exists, merge there instead of develop

## Merge Strategies

### Feature to Develop
- Use `--no-ff` (no fast-forward)
- Preserves branch history
- Creates merge commit
- Easy to see feature boundaries

### Release to Main
- Use `--no-ff`
- Always tag after merge
- Never fast-forward

### Develop to Main
- **Never merge directly!**
- Always go through release branch

## Common Scenarios

### Multiple Releases in Progress

When maintaining multiple versions:
```bash
# v2.x.x is main, but need v1.x.x patch
git checkout -b support/1.x v1.5.0  # From the tag
git checkout -b hotfix/1.5.1 support/1.x
# Fix and merge back to support/1.x
```

### Long-Running Feature

For features taking more than 2 weeks:
```bash
# Regularly merge develop into feature
git checkout feature/big-feature
git merge develop

# Or rebase (cleaner history)
git rebase develop
```

### Release Bug Fix

During release preparation:
```bash
git checkout release/2.0.0
git checkout -b bugfix/release-bug
# Fix the issue
git checkout release/2.0.0
git merge --no-ff bugfix/release-bug
git branch -d bugfix/release-bug
```

### Concurrent Releases

If preparing 2.0.0 while 1.5.x needs a hotfix:
```bash
# Hotfix goes to main as usual
# Then merge to release/2.0.0 instead of develop
git checkout release/2.0.0
git merge hotfix/1.5.1
# Later, release/2.0.0 will merge to develop
```

## Branch Protection Rules

### For `main`:
- Require pull request before merging
- Require status checks to pass
- Require linear history (optional)
- Restrict who can push
- No force pushes

### For `develop`:
- Require pull request (optional for small teams)
- Require status checks to pass
- Allow force push with lease (for rebasing)

### For `release/*` and `hotfix/*`:
- Restrict creation to maintainers
- Require approval for merges

## Version Numbering

Follow Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

```
v2.0.0  - Major release from release/2.0.0
v2.0.1  - Hotfix from hotfix/2.0.1
v2.1.0  - Minor release from release/2.1.0
```

## Automation Opportunities

### Git Hooks
- Pre-push: Validate branch naming
- Commit-msg: Enforce conventional commits
- Pre-merge: Run tests

### CI/CD Integration
- Auto-deploy develop to staging
- Auto-deploy main to production
- Run tests on all branches
- Build artifacts on release branches

### GitHub Actions
```yaml
on:
  push:
    branches: [main, develop, 'release/**', 'hotfix/**']
  pull_request:
    branches: [main, develop]
```

## Troubleshooting

### Forgot to Create Release Branch
```bash
# If changes went directly to main
git checkout main
git checkout -b release/2.0.0
# Continue with release process
```

### Wrong Base Branch
```bash
# Feature was based on main instead of develop
git checkout feature/wrong-base
git rebase --onto develop main
```

### Merge Conflicts
```bash
# During feature finish
git checkout develop
git merge --no-ff feature/xyz
# If conflicts, resolve then:
git add .
git commit
```

## Related Resources

- [branching-strategies.md](./branching-strategies.md) - Strategy comparison
- [github-flow-guide.md](./github-flow-guide.md) - Simpler alternative
- [worktree-patterns.md](./worktree-patterns.md) - Parallel development
