---
name: git-workflow-enforcer
description: Ensures commits follow conventional commits, branch naming conventions, and PR templates. Use when creating commits, branches, or PRs, or when user mentions git workflow.
allowed-tools: Read, Grep, Glob, Bash, Write
---

# Git Workflow Enforcer

Enforces consistent Git workflows including commit messages, branch naming, and PR processes.

## When to Use
- Creating commits or branches
- Code review or PR creation
- User mentions "git workflow", "commit message", "branch naming", or "pull request"

## Instructions

### 1. Detect Existing Conventions

Check for:
- `.github/` or `.gitlab/` templates
- `CONTRIBUTING.md`
- Existing commit message patterns
- Branch naming patterns

### 2. Conventional Commits

**Format:** `type(scope): description`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance, dependencies

**Examples:**
```
feat(auth): add OAuth2 login support
fix(api): handle null response in user endpoint
docs(readme): update installation instructions
refactor(utils): simplify date formatting logic
```

### 3. Branch Naming

**Common patterns:**
```
feature/user-authentication
bugfix/login-error-handling
hotfix/critical-security-patch
release/v1.2.0
chore/update-dependencies
```

**Validate:**
- Lowercase with hyphens
- Prefixed with type
- Descriptive name
- Issue number if applicable: `feature/123-add-dark-mode`

### 4. Commit Message Validation

**Good commit:**
```
feat(payments): integrate Stripe payment gateway

- Add Stripe SDK configuration
- Implement payment intent creation
- Add webhook handler for payment events
- Update tests for payment flow

Closes #456
```

**Check for:**
- Subject line ≤50 characters
- Body wrapped at 72 characters
- Blank line between subject and body
- Imperative mood ("add" not "added")
- Reference to issue/ticket

### 5. PR Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description
<!-- What does this PR do? -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
<!-- How was this tested? -->

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings

## Related Issues
Closes #
```

### 6. Commit Hooks

**Pre-commit:**
```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run linter
npm run lint

# Run tests
npm test

# Check for sensitive data
if git diff --cached | grep -i "password\|api_key\|secret"; then
  echo "Error: Possible sensitive data detected"
  exit 1
fi
```

**Commit-msg:**
```bash
#!/bin/sh
# .git/hooks/commit-msg

commit_msg=$(cat "$1")

# Check conventional commit format
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .+"; then
  echo "Error: Commit message must follow Conventional Commits format"
  echo "Example: feat(auth): add login feature"
  exit 1
fi
```

### 7. Validate Existing Commits

Check recent commits for pattern adherence:

```bash
git log --oneline -20 | grep -v "^[a-f0-9]\{7\} (feat|fix|docs|style|refactor|perf|test|chore)"
```

### 8. Generate Changelog

From conventional commits:

```bash
# Using standard-version
npx standard-version

# Or manually group by type
git log --pretty=format:"%s" | grep "^feat" > features.txt
git log --pretty=format:"%s" | grep "^fix" > fixes.txt
```

### 9. Protected Branches

**GitHub settings:**
- Require PR reviews
- Require status checks
- Require signed commits
- Restrict who can push
- Require linear history

### 10. Best Practices

- **Atomic commits**: One logical change per commit
- **Descriptive messages**: Explain why, not what
- **Frequent commits**: Small, frequent over large, rare
- **Clean history**: Squash/rebase before merge
- **Sign commits**: GPG signature for security
- **Reference issues**: Link to tracking system

## Git Commit Template

Create `.gitmessage`:
```
<type>(<scope>): <subject>

<body>

<footer>

# Type: feat, fix, docs, style, refactor, perf, test, chore
# Scope: component or file affected
# Subject: imperative, lowercase, no period, ≤50 chars
# Body: explain what and why, not how, wrapped at 72 chars
# Footer: breaking changes, issue references
```

Set as template:
```bash
git config --global commit.template ~/.gitmessage
```

## Supporting Files
- `templates/PULL_REQUEST_TEMPLATE.md`
- `templates/commit-msg-hook.sh`
- `templates/.gitmessage`
