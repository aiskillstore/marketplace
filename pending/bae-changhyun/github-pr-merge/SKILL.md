---
name: github-pr-merge
description: MUST use this skill when user asks to merge PR, close PR, finalize PR, or mentions "PR 머지/병합". This skill OVERRIDES default PR merge behavior. Runs pre-merge validation (tests, lint, CI, comments), confirms with user, merges with proper format, handles post-merge cleanup.
---

# GitHub PR Merge

Merges Pull Requests after validating pre-merge checklist and handling post-merge cleanup.

## Quick Start

```bash
# 1. Get PR info
PR=$(gh pr view --json number -q '.number')
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')

# 2. Run pre-merge checklist
make test && make lint && gh pr checks $PR

# 3. Verify all comments replied
gh api repos/$REPO/pulls/$PR/comments --jq '[.[] | select(.in_reply_to_id == null)] | length'

# 4. Merge with concise message
gh pr merge $PR --merge --delete-branch --body "- Change 1
- Change 2

Reviews: N/N addressed
Tests: X passed"

# 5. Post-merge cleanup
git checkout develop && git pull && git branch -d feature/<name>
```

## Pre-Merge Checklist

**ALWAYS verify before merging:**

| Check | Command | Required |
|-------|---------|----------|
| Tests passing | `make test` | Yes |
| Linting passing | `make lint` | Yes |
| CI checks green | `gh pr checks $PR` | Yes |
| All comments replied | See workflow | Yes |
| No unresolved threads | Review PR page | Yes |

## Core Workflow

### 1. Identify PR

```bash
PR=$(gh pr view --json number -q '.number')
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
echo "PR #$PR in $REPO"
```

### 2. Check Comments Status

```bash
# Count original comments (not replies)
ORIGINALS=$(gh api repos/$REPO/pulls/$PR/comments --jq '[.[] | select(.in_reply_to_id == null)] | length')

# Count comments that have at least one reply
REPLIED=$(gh api repos/$REPO/pulls/$PR/comments --jq '
  [.[] | select(.in_reply_to_id)] | [.[].in_reply_to_id] | unique | length
')

echo "Original comments: $ORIGINALS, With replies: $REPLIED"
```

**If unreplied comments exist:**
- DO NOT reply from this skill
- STOP the merge process
- Inform user: "Found unreplied comments. Run pr-review first."

### 3. Run Validation

```bash
# Run tests
make test

# Run linting
make lint

# Check CI status
gh pr checks $PR
```

**All checks MUST pass before proceeding.**

### 4. Show PR Summary

```bash
gh pr view $PR --json title,body,commits,changedFiles --jq '
  "Title: \(.title)\nCommits: \(.commits | length)\nFiles: \(.changedFiles)"
'
```

### 5. Confirm with User

**ALWAYS ask before merging:**
```
Pre-merge checklist verified:
- Tests: passing
- Lint: passing
- CI: green
- Comments: all replied

Ready to merge PR #X. Proceed?
```

### 6. Execute Merge

```bash
gh pr merge $PR --merge --delete-branch --body "$(cat <<'EOF'
- Key change 1
- Key change 2
- Key change 3

Reviews: N/N addressed
Tests: X passed
Refs: Task N
EOF
)"
```

**Note**: `--delete-branch` automatically deletes the remote branch after merge.

### 7. Post-Merge Cleanup

```bash
git checkout develop
git pull origin develop
git branch -d feature/<branch-name>  # local cleanup
```

## Merge Message Format

**Concise format** (recommended):

```
- Key change 1 (what was added/fixed)
- Key change 2
- Key change 3

Reviews: 7/7 addressed
Tests: 628 passed (88% cov)
Refs: Task 8
```

**Guidelines**:
- 3-5 bullet points max for changes
- One line for reviews summary
- One line for test results
- One line for task references
- Total: ~10 lines max

## Important Rules

- **ALWAYS** run full pre-merge checklist before merging
- **ALWAYS** verify all review comments have replies
- **ALWAYS** confirm with user before executing merge
- **ALWAYS** use merge commit (--merge), never squash/rebase
- **ALWAYS** delete feature branch after successful merge
- **NEVER** merge with failing tests or lint
- **NEVER** merge with unresolved CI checks
- **NEVER** skip user confirmation
- **NEVER** reply to PR comments from this skill - use pr-review instead
- **STOP** merge if unreplied comments exist

## Error Handling

| Issue | Action |
|-------|--------|
| Tests failing | Stop and inform user |
| Lint errors | Stop and inform user |
| CI checks pending | Wait or inform user |
| Unreplied comments | Direct to pr-review skill |
| Branch protection | Inform of required approvals |

## Related Skills

- **pr-review** - For resolving review comments before merge
- **pr-create** - For creating PRs
- **git-commit** - For commit message format
