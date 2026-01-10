# GitHub Flow Guide

A simplified branching model for continuous deployment and fast iteration.

## Overview

GitHub Flow is a lightweight, branch-based workflow designed for teams that deploy regularly. It's simpler than Gitflow and ideal for continuous deployment scenarios.

## Core Principles

1. **Anything in `main` is deployable**
2. **Create branches from `main`**
3. **Commit to branches frequently**
4. **Open PRs early for discussion**
5. **Merge only after review**
6. **Deploy immediately after merging**

## Branch Structure

```
main ─────●───●───●───●───●───● (always deployable)
          │   │   │   │   │
          └─feature─┴─fix─┘
```

### Main Branch (`main`)
- **Single source of truth**
- **Always in deployable state**
- **Protected from direct pushes**
- **Deploys trigger on merge**

### Feature Branches
- Short-lived (hours to days)
- Named descriptively
- Based on `main`
- Merge back to `main` via PR

## The Workflow

### 1. Create a Branch

Start from `main` with a descriptive name:

```bash
# Update main
git checkout main
git pull origin main

# Create branch
git checkout -b feature/add-user-avatar

# Or for a fix
git checkout -b fix/login-timeout
```

**Branch naming:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code improvements
- `test/description` - Test additions

### 2. Add Commits

Make changes and commit frequently:

```bash
# Work on your changes
git add .
git commit -m "feat(user): add avatar upload component"

git add .
git commit -m "feat(user): add avatar cropping"

git add .
git commit -m "test(user): add avatar upload tests"
```

**Commit best practices:**
- Commit early and often
- Write meaningful commit messages
- Keep commits atomic
- Push regularly for backup

```bash
git push -u origin feature/add-user-avatar
```

### 3. Open a Pull Request

Open PR early for visibility and discussion:

```bash
# Push branch
git push -u origin feature/add-user-avatar

# Create PR
gh pr create --title "Add user avatar upload" \
  --body "Implements #42: user avatar upload with cropping"
```

**PR best practices:**
- Open early for feedback
- Use PR templates
- Link related issues
- Add screenshots for UI changes
- Request specific reviewers

### 4. Review and Discuss

Collaborate through PR comments:

- **Author**: Respond to feedback, push fixes
- **Reviewers**: Comment on code, approve/request changes
- **CI**: Runs automated tests

```bash
# Address feedback
git add .
git commit -m "fix(user): address review feedback"
git push
```

### 5. Deploy and Test

Deploy to a preview/staging environment:

- CI/CD deploys PR branch to preview URL
- Manual testing on preview
- Automated E2E tests run
- Performance checks

Many teams use:
- Vercel/Netlify preview deployments
- Kubernetes namespaces per PR
- Feature branch environments

### 6. Merge

Once approved and tested:

```bash
# Squash merge (recommended)
gh pr merge --squash

# Or regular merge
gh pr merge --merge
```

**Merge options:**
- **Squash merge**: Condenses all commits into one (cleaner history)
- **Merge commit**: Preserves all commits (full history)
- **Rebase merge**: Linear history without merge commits

### 7. Deploy to Production

Merging to `main` triggers production deployment:

1. CI runs final tests
2. Build creates production artifact
3. Deployment to production
4. Post-deploy verification
5. Monitor for issues

## Best Practices

### Keep Branches Short-Lived

- **Target: 1-3 days maximum**
- Smaller PRs are easier to review
- Less likely to have merge conflicts
- Faster feedback cycle

If work takes longer:
- Break into smaller PRs
- Use feature flags for partial work
- Ship incrementally

### Write Good PRs

```markdown
## Summary
Brief description of changes

## Changes
- Added avatar upload component
- Implemented image cropping
- Added file size validation

## Testing
- Unit tests added
- Manual testing on staging

## Screenshots
[Before/After screenshots]

## Related Issues
Closes #42
```

### Use Labels and Projects

Organize PRs with:
- Type labels: `feature`, `bug`, `docs`
- Priority labels: `critical`, `high`, `low`
- Status labels: `needs-review`, `approved`
- Project boards for tracking

### Protect Main Branch

GitHub branch protection rules:
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require linear history (optional)
- ✅ Include administrators

### Automate Everything

**CI checks on every PR:**
- Linting
- Unit tests
- Integration tests
- Build verification
- Security scanning

**Automated deployments:**
- Preview/staging on PR open
- Production on merge to main
- Automatic rollback on failure

## Handling Releases

GitHub Flow doesn't have explicit release branches. Options:

### Option 1: Tag-Based Releases
```bash
# After merge, tag for release
git tag -a v1.2.0 -m "Release 1.2.0"
git push origin v1.2.0

# Or use GitHub Releases
gh release create v1.2.0 --generate-notes
```

### Option 2: Continuous Releases
- Every merge to main is a release
- Use automatic versioning (semantic-release)
- Deploy continuously

### Option 3: Release Trains
- Collect merges over time
- Cut releases on schedule
- Tag at release time

## Hotfixes

Emergency fixes follow the same flow:

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b fix/critical-security-issue

# Make the fix
git commit -m "fix(security): patch XSS vulnerability"

# Push and create PR with urgency labels
git push -u origin fix/critical-security-issue
gh pr create --title "URGENT: Fix XSS vulnerability" \
  --label "critical" --label "security"

# Get quick review and merge
# Deploy happens automatically
```

For critical issues:
- Add `critical` or `hotfix` labels
- Notify team in Slack/Teams
- Get expedited review
- Consider pair programming

## Feature Flags

For long-running features:

```javascript
// Feature flag implementation
if (featureFlags.isEnabled('new-avatar-upload')) {
  return <NewAvatarUpload />;
} else {
  return <LegacyAvatarUpload />;
}
```

**Benefits:**
- Merge incomplete features
- Test in production
- Gradual rollout
- Easy rollback

**Tools:**
- LaunchDarkly
- Split
- Unleash
- Simple env variables

## Comparison with Gitflow

| Aspect | GitHub Flow | Gitflow |
|--------|-------------|---------|
| Branches | main + feature | main, develop, feature, release, hotfix |
| Complexity | Low | High |
| Deploy frequency | Continuous | Scheduled |
| Release process | Tag or continuous | Release branches |
| Best for | Web apps, SaaS | Versioned software |

## When GitHub Flow Works Best

✅ **Ideal for:**
- Continuous deployment
- Web applications
- SaaS products
- Small to medium teams
- Fast iteration cycles
- Feature flag usage

❌ **Less suitable for:**
- Multiple production versions
- Scheduled releases
- Long-lived feature branches
- Complex release processes
- Strict versioning requirements

## Common Pitfalls

### Long-Lived Branches
**Problem**: Branches open for weeks
**Solution**: Break into smaller PRs, use feature flags

### Main Branch Breaks
**Problem**: Bad merge breaks production
**Solution**: Better CI, required checks, auto-rollback

### Incomplete Features in Main
**Problem**: Half-done features visible to users
**Solution**: Feature flags, better planning

### Poor PR Descriptions
**Problem**: Reviewers don't understand changes
**Solution**: PR templates, clear guidelines

## Migration to GitHub Flow

### From Gitflow:
1. Finish all release/hotfix branches
2. Merge develop to main
3. Delete develop branch
4. Set main as default
5. Update branch protection
6. Set up CD pipeline
7. Implement feature flags

### From No Process:
1. Protect main branch
2. Require PRs
3. Set up CI/CD
4. Document process
5. Train team

## Related Resources

- [branching-strategies.md](./branching-strategies.md) - Strategy comparison
- [gitflow-guide.md](./gitflow-guide.md) - More complex alternative
- [worktree-patterns.md](./worktree-patterns.md) - Parallel development
