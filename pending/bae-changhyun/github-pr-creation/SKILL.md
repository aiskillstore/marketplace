---
name: github-pr-creation
description: MUST use this skill when user asks to create PR, open pull request, submit for review, or mentions "PR 생성/만들기". This skill OVERRIDES default PR creation behavior. Analyzes commits, validates task completion, generates Conventional Commits title and description, suggests labels.
---

# GitHub PR Creation

Creates Pull Requests with task validation, test execution, and Conventional Commits formatting.

## Quick Start

```bash
# 1. Verify GitHub CLI
gh --version && gh auth status

# 2. Gather information
git log develop..HEAD --oneline
git diff develop --stat
git rev-parse --abbrev-ref HEAD

# 3. Run project tests
make test  # or: pytest, npm test

# 4. Create PR
gh pr create --title "..." --body "..." --base develop --label feature
```

## Core Workflow

### 1. Verify Environment

```bash
gh --version && gh auth status
```

If not installed: `brew install gh` then `gh auth login`

### 2. Confirm Target Branch

**Always ask user**:
```
I'm about to create a PR from [current-branch] to [target-branch]. Is this correct?
- feature branch → develop (90% of cases)
- develop → master/main (releases)
```

### 3. Gather Information

```bash
# Current branch
git rev-parse --abbrev-ref HEAD

# Commits since base branch
git log [base-branch]..HEAD --oneline

# Files changed
git diff [base-branch] --stat

# Remote tracking status
git status -sb
```

### 4. Search for Task Documentation

Look for task files in these locations:
1. `.kiro/specs/*/tasks.md`
2. `docs/specs/*/tasks.md`
3. `specs/*/tasks.md`
4. Any `tasks.md` in project root

### 5. Analyze Commits

For each commit, identify:
- **Type**: feat, fix, refactor, docs, test, chore, ci, perf, style
- **Scope**: component/module affected (kebab-case)
- **Task references**: look for `task X.Y`, `Task X`, `#X.Y` patterns
- **Breaking changes**: exclamation mark (!) or `BREAKING CHANGE` in body

### 6. Run Tests

Detect and run project tests:
- Makefile: `make test`
- package.json: `npm test`
- Python: `pytest`

**Tests MUST pass before creating PR.**

### 7. Determine PR Type

| Branch Flow | PR Type | Title Prefix |
|-------------|---------|--------------|
| feature/* → develop | Feature | `feat(scope):` |
| fix/* → develop | Bugfix | `fix(scope):` |
| hotfix/* → main | Hotfix | `hotfix(scope):` |
| develop → main | Release | `release:` |
| refactor/* → develop | Refactoring | `refactor(scope):` |

### 8. Generate PR Content

**Title format**: `<type>(<scope>): <description>`
- Type: dominant commit type (feat > fix > refactor)
- Scope: most common scope from commits (kebab-case)
- Description: imperative, lowercase, no period, max 50 chars

**Body structure**:
```markdown
## Summary
- Key change 1
- Key change 2

## Changes
- List of specific changes

## Test Plan
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing done

## Related
- Refs: Task N, Issue #X
```

### 9. Suggest Labels

| Commit Type | Labels |
|-------------|--------|
| feat | feature, enhancement |
| fix | bug, bugfix |
| refactor | refactoring, tech-debt |
| docs | documentation |
| ci | ci/cd |
| security | security |

Check available labels: `gh label list`

### 10. Create PR

**Show content to user first**, then:

```bash
gh pr create --title "[title]" --body "$(cat <<'EOF'
[body content]
EOF
)" --base [base_branch] --label [labels]
```

## Information Gathering Checklist

Before generating PR, ensure you have:

- [ ] Current branch name
- [ ] Base branch confirmed with user
- [ ] List of commits with types and scopes
- [ ] Files changed summary
- [ ] Task documentation (if exists)
- [ ] Test results (must pass)
- [ ] Available labels in repo

## Important Rules

- **NEVER** modify repository files (read-only analysis)
- **ALWAYS** confirm target branch with user
- **ALWAYS** run tests before creating PR
- **ALWAYS** show PR content for approval before creating
- **NEVER** create PR without user confirmation
- **ALWAYS** use HEREDOC for body to preserve formatting

## Related Skills

- **git-commit** - Commit message format and conventions
- **pr-merge** - For merging existing PRs
- **pr-review** - For handling PR review comments
