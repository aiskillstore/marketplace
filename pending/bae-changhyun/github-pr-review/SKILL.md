---
name: github-pr-review
description: MUST use this skill when user asks to resolve PR comments, handle review feedback, fix review comments, or mentions "리뷰 코멘트/피드백". This skill OVERRIDES default behavior. Fetches comments via GitHub CLI, classifies by severity, applies fixes with user confirmation, commits with proper format, replies to threads.
---

# GitHub PR Review

Resolves Pull Request review comments with severity-based prioritization, fix application, and thread replies.

## Quick Start

```bash
# 1. Check project conventions
cat CLAUDE.md 2>/dev/null | head -50

# 2. Get PR and repo info
PR=$(gh pr view --json number -q '.number')
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')

# 3. Fetch comments
gh api repos/$REPO/pulls/$PR/comments

# 4. For each comment: read → analyze → fix → verify → commit → reply

# 5. Run tests
make test

# 6. Push when all fixes verified
git push
```

## Pre-Review Checklist

Before processing comments, verify:

1. **Project conventions**: Read `CLAUDE.md` or similar
2. **Commit format**: Check `git log --oneline -5` for project style
3. **Test command**: Identify test runner (`make test`, `pytest`, `npm test`)
4. **Branch status**: `git status` to ensure clean working tree

## Core Workflow

### 1. Fetch PR Comments

```bash
PR=$(gh pr view --json number -q '.number')
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
gh api repos/$REPO/pulls/$PR/comments
```

### 2. Classify by Severity

Process in order: CRITICAL > HIGH > MEDIUM > LOW

| Severity | Indicators | Action |
|----------|------------|--------|
| CRITICAL | "security", "vulnerability", "injection" | Must fix |
| HIGH | "High Severity", "high-priority" | Should fix |
| MEDIUM | "Medium Severity", "medium-priority" | Recommended |
| LOW | "style", "nit", "minor" | Optional |

### 3. Process Each Comment

For each comment:

**a. Show context**
```
Comment #123456789 (HIGH) - app/auth.py:45
"The validation logic should use constant-time comparison..."
```

**b. Read affected code and propose fix**

**c. Confirm with user before applying**

**d. Apply fix if approved**

**e. Verify fix addresses ALL issues in the comment**

### 4. Commit Changes

Use proper format for review fixes:

```bash
git add <files>
git commit -m "$(cat <<'EOF'
fix(scope): address review comment #ID

Brief explanation of what was wrong and how it's fixed.
Addresses review comment #123456789.
EOF
)"
```

**Review fix commit rules**:
- First line: `type(scope): subject` (max 50 chars)
- Types: `fix`, `refactor`, `security`, `test`, `style`, `perf`
- Reference the comment ID in body

### 5. Reply to Thread

```bash
COMMIT=$(git rev-parse --short HEAD)
gh api repos/$REPO/pulls/$PR/comments \
  --input - <<< '{"body": "Fixed in '"$COMMIT"'. [brief description].", "in_reply_to": 123456789}'
```

**Standard Reply Templates**:

| Situation | Template |
|-----------|----------|
| Fixed | `Fixed in [hash]. [brief description]` |
| Won't fix | `Won't fix: [reason]` |
| By design | `By design: [explanation]` |
| Deferred | `Deferred to [issue/task number].` |
| Acknowledged | `Acknowledged. [brief note]` |

### 6. Run Tests

```bash
make test  # or project-specific command
```

All tests must pass before pushing.

### 7. Push

```bash
git push
```

### 8. Submit Review (Optional)

```bash
# Approve the PR
gh pr review $PR --approve --body "All review comments addressed. Ready to merge."

# Or request changes if issues remain
gh pr review $PR --request-changes --body "Addressed X comments, Y issues remain."

# Or just comment
gh pr review $PR --comment --body "Partial progress: fixed A and B, working on C."
```

## Batch Commit Strategy

Organize commits by impact:

| Change Type | Strategy |
|-------------|----------|
| Functional (CRITICAL/HIGH) | Separate commit per fix |
| Cosmetic (MEDIUM/LOW) | Single batch commit |

**Workflow:**
1. Fix CRITICAL/HIGH → separate commits each
2. Collect all cosmetic fixes
3. Apply cosmetics → single `style:` commit
4. Run tests once
5. Push all together

## Pre-Merge Checklist

Before closing/merging PR:

- [ ] All CRITICAL and HIGH comments addressed
- [ ] All MEDIUM comments addressed or justified skip
- [ ] Replies posted to all resolved threads
- [ ] Tests passing
- [ ] Linting passing
- [ ] CI checks green
- [ ] No unresolved conversations

## Reply to Threads API

**Important**: Use `--input -` with JSON for `in_reply_to`:

```bash
# Correct syntax
gh api repos/$REPO/pulls/$PR/comments \
  --input - <<< '{"body": "Fixed in abc123.", "in_reply_to": 123456789}'
```

## Important Rules

- **ALWAYS** read project conventions before starting
- **ALWAYS** confirm before modifying files
- **ALWAYS** verify ALL issues in multi-issue comments are fixed
- **ALWAYS** run tests before pushing
- **ALWAYS** reply to resolved threads using standard templates
- **ALWAYS** submit formal review after addressing all comments
- **NEVER** skip HIGH/CRITICAL comments without explicit user approval
- **Functional fixes** → separate commits (one per fix)
- **Cosmetic fixes** → batch into single `style:` commit

## Related Skills

- **git-commit** - Commit message format and conventions
- **pr-merge** - Execute merge after review is complete
- **pr-create** - For creating PRs
