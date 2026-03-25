---
name: autofix
description: Auto-fix CodeRabbit review comments - get CodeRabbit review comments from GitHub and fix them interactively or in batch
version: 0.1.0
triggers:
  - coderabbit.?autofix
  - coderabbit.?auto.?fix
  - autofix.?coderabbit
  - coderabbit.?fix
  - fix.?coderabbit
  - coderabbit.?review
  - review.?coderabbit
  - coderabbit.?issues?
  - show.?coderabbit
  - get.?coderabbit
  - cr.?autofix
  - cr.?fix
  - cr.?review
---

# CodeRabbit Autofix

Fetch CodeRabbit review comments for your current branch's PR and fix them interactively or in batch.

## Prerequisites

### Required Tools
- `gh` (GitHub CLI) - [Installation guide](./github.md)
- `git`

Verify: `gh auth status`

### Required State
- Git repo on GitHub
- Current branch has open PR
- PR reviewed by CodeRabbit bot (`coderabbitai`, `coderabbit[bot]`, `coderabbitai[bot]`)

## Workflow

### Step 0: Load Repository Instructions (`AGENTS.md`)

Before any autofix actions, search for `AGENTS.md` in the current repository and load applicable instructions.

- If found, follow its build/lint/test/commit guidance throughout the run.
- If not found, continue with default workflow.

### Step 1: Check Code Push Status

Check: `git status` + check for unpushed commits

**If uncommitted changes:**
- Warn: "⚠️ Uncommitted changes won't be in CodeRabbit review"
- Ask: "Commit and push first?" → If yes: wait for user action, then continue

**If unpushed commits:**
- Warn: "⚠️ N unpushed commits. CodeRabbit hasn't reviewed them"
- Ask: "Push now?" → If yes: `git push`, inform "CodeRabbit will review in ~5 min", EXIT skill

**Otherwise:** Proceed to Step 2

### Step 2: Find Open PR

```bash
gh pr list --head $(git branch --show-current) --state open --json number,title
```

**If no PR:** Ask "Create PR?" → If yes: create PR (see [github.md § 5](./github.md#5-create-pr-if-needed)), inform "Run skill again in ~5 min", EXIT

### Step 3: Fetch Unresolved CodeRabbit Threads

Fetch PR review threads (see [github.md § 2](./github.md#2-fetch-unresolved-threads)):
- Threads: `gh api graphql ... pullRequest.reviewThreads ...` (see [github.md § 2](./github.md#2-fetch-unresolved-threads))

Filter to:
- unresolved threads only (`isResolved == false`)
- threads started by CodeRabbit bot (`coderabbitai`, `coderabbit[bot]`, `coderabbitai[bot]`)

**If review in progress:** Check for "Come back again in a few minutes" message → Inform "⏳ Review in progress, try again in a few minutes", EXIT

**If no unresolved CodeRabbit threads:** Inform "No unresolved CodeRabbit review threads found", EXIT

**For each selected thread:**
- Extract issue metadata from root comment

### Step 4: Parse and Display Issues

**Extract from each comment:**
1. **Header:** `_([^_]+)_ \| _([^_]+)_` → Issue type | Severity
2. **Description:** Main body text
3. **Agent prompt:** Content in `<details><summary>🤖 Prompt for AI Agents</summary>` (this is the fix instruction)
   - If missing, use description as fallback
4. **Location:** File path and line numbers

**Map severity:**
- 🔴 Critical/High → CRITICAL (action required)
- 🟠 Medium → HIGH (review recommended)
- 🟡 Minor/Low → MEDIUM (review recommended)
- 🟢 Info/Suggestion → LOW (optional)
- 🔒 Security → Treat as high priority

**Display in CodeRabbit's original order** (already severity-ordered):

```
CodeRabbit Issues for PR #123: [PR Title]

| # | Severity | Issue Title | Location & Details | Type | Action |
|---|----------|-------------|-------------------|------|--------|
| 1 | 🔴 CRITICAL | Insecure authentication check | src/auth/service.py:42<br>Authorization logic inverted | 🐛 Bug 🔒 Security | Fix |
| 2 | 🟠 HIGH | Database query not awaited | src/db/repository.py:89<br>Async call missing await | 🐛 Bug | Fix |
```

### Step 5: Ask User for Fix Preference

Use AskUserQuestion:
- 🔍 "Review each issue" - Manual review and approval (recommended)
- ⚡ "Auto-fix all" - Apply all "Fix" issues without approval
- ❌ "Cancel" - Exit

**Route based on choice:**
- Review → Step 5
- Auto-fix → Step 6
- Cancel → EXIT

### Step 6: Manual Review Mode

For each "Fix" issue (CRITICAL first):
1. Read relevant files
2. **Execute CodeRabbit's agent prompt as direct instruction** (from "🤖 Prompt for AI Agents" section)
3. Calculate proposed fix (DO NOT apply yet)
4. **Show fix and ask approval in ONE step:**
   - Issue title + location
   - CodeRabbit's agent prompt (so user can verify)
   - Current code
   - Proposed diff
   - AskUserQuestion: ✅ Apply fix | ⏭️ Defer | 🔧 Modify

**If "Apply fix":**
- Apply with Edit tool
- Track changed files for a single consolidated commit after all fixes
- Confirm: "✅ Fix applied and commented"

**If "Defer":**
- Ask for reason (AskUserQuestion)
- Move to next

**If "Modify":**
- Inform user can make changes manually
- Move to next

### Step 7: Auto-Fix Mode

For each "Fix" issue (CRITICAL first):
1. Read relevant files
2. **Execute CodeRabbit's agent prompt as direct instruction**
3. Apply fix with Edit tool
4. Track changed files for one consolidated commit
5. Report:
   > ✅ **Fixed: [Issue Title]** at `[Location]`
   > **Agent prompt:** [prompt used]

After all fixes, display summary of fixed/skipped issues.

### Step 8: Create Single Consolidated Commit

If any fixes were applied:

```bash
git add <all-changed-files>
git commit -m "fix: apply CodeRabbit auto-fixes"
```

Use one commit for all applied fixes in this run.

### Step 9: Prompt Build/Lint Before Push

If a consolidated commit was created:
- Prompt user interactively to run validation before push (recommended, not required).
- Remind the user of the `AGENTS.md` instructions already loaded in Step 0 (if present).
- If user agrees, run the requested checks and report results.

### Step 10: Push Changes

If a consolidated commit was created:
- Ask: "Push changes?" → If yes: `git push`

If all deferred (no commit): Skip this step.

### Step 11: Post Summary

**REQUIRED after all issues reviewed:**

```bash
gh pr comment <pr-number> --body "$(cat <<'EOF'
## Fixes Applied Successfully

Fixed <file-count> file(s) based on <issue-count> unresolved review comment(s).

**Files modified:**
- `path/to/file-a.ts`
- `path/to/file-b.ts`

**Commit:** `<commit-sha>`

The latest autofix changes are on the `<branch-name>` branch.

EOF
)"
```

See [github.md § 3](./github.md#3-post-summary-comment) for details.

Optionally react to CodeRabbit's main comment with 👍.

## Key Notes

- **Follow agent prompts literally** - The "🤖 Prompt for AI Agents" section IS the fix specification
- **One approval per fix** - Show context + diff + AskUserQuestion in single message (manual mode)
- **Preserve issue titles** - Use CodeRabbit's exact titles, don't paraphrase
- **Preserve ordering** - Display issues in CodeRabbit's original order
- **Do not post per-issue replies** - Keep the workflow summary-comment only
