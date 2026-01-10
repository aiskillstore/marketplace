---
name: autonomous-ci
description: Ensures Claude verifies both local tests AND remote CI before claiming completion. Use BEFORE any completion claims, commits, or pull requests. Mandatory verification with evidence.
---

# Autonomous CI Verification

## Overview

**Never claim success without CI verification.** This skill ensures Claude automatically verifies both local tests
AND remote CI before declaring work complete.

**Core Principle:** Evidence before claims. Always.

## When to Use This Skill

This skill is **MANDATORY** before:

- ANY completion claims
- ANY expressions of satisfaction ("Done!", "Fixed!", "Working now!")
- Committing code
- Creating pull requests
- Moving to next task
- Responding "should work" or similar phrases

## The Verification Protocol

```text
BEFORE claiming any completion:

1. RUN LOCAL VERIFICATION
   └─> Execute project-specific test command
   └─> Check exit code
   └─> If fails: Fix and repeat

2. COMMIT AND PUSH
   └─> Only if local tests pass
   └─> Push to remote repository

3. MONITOR CI (BLOCKING)
   └─> Find workflow run for commit
   └─> WAIT for completion (do not proceed)
   └─> Check all workflows in .github/workflows/

4. IF CI FAILS
   └─> Download failure logs
   └─> Analyze root cause
   └─> Fix the issue
   └─> REPEAT from step 1

5. ONLY WHEN ALL CI PASSES
   └─> Report success with evidence
```

## Available Tools

This skill uses scripts from the plugin directory:

### Local Verification

The plugin provides a generic test runner that auto-detects your project type:

```bash
# For .NET projects
dotnet test --configuration Release

# For Node.js projects
npm test

# For Python projects
pytest

# For Go projects
go test ./...
```

Claude will automatically detect your project type and run the appropriate command.

### CI Monitoring

After pushing, Claude will use GitHub CLI to monitor CI:

```bash
# Find and watch workflow run
gh run list --limit 1 --commit <sha>
gh run watch <run-id>

# Check final status
gh run view <run-id> --json conclusion
```

## Red Flags - STOP Immediately

If Claude catches itself thinking or about to say:

- ❌ "Should work now"
- ❌ "Tests pass locally, we're done"
- ❌ "I'll push and assume it works"
- ❌ "Let me commit this and move on"
- ❌ "The change is small, CI will pass"
- ❌ "Pushed! ✅" (without waiting for CI)

**STOP.** Run the verification protocol instead.

## The Workflow

### Step 1: Local Verification

```bash
# ALWAYS verify locally first
# For .NET:
dotnet build --configuration Release
dotnet test --no-build --configuration Release

# For Node.js:
npm run build
npm test

# For Python:
pytest

# ONLY proceed if exit code = 0
```

### Step 2: Commit and Push

```bash
# Only after local tests pass
git add .
git commit -m "Fix: issue description"
git push
```

### Step 3: Monitor CI (Blocking)

```bash
# Get commit SHA
COMMIT_SHA=$(git rev-parse HEAD)

# Find workflow run
RUN_ID=$(gh run list --commit "$COMMIT_SHA" --limit 1 --json databaseId -q '.[0].databaseId')

# Watch workflow (BLOCKS until complete)
gh run watch "$RUN_ID"

# Check conclusion
CONCLUSION=$(gh run view "$RUN_ID" --json conclusion -q .conclusion)

if [ "$CONCLUSION" = "success" ]; then
  echo "✅ CI passed"
else
  echo "❌ CI failed - analyzing logs"
  gh run view "$RUN_ID" --log-failed
fi
```

### Step 4: Handle Failures

When CI fails:

1. Download failure logs: `gh run view <run-id> --log-failed`
2. Analyze root cause
3. Fix the issue
4. **REPEAT from step 1** (run local tests again)

## Common Rationalizations (All Wrong)

| Excuse | Reality |
| ------ | ------- |
| "Tests passed locally" | CI environment may differ |
| "It's a small change" | Small changes break CI too |
| "I'm confident" | Confidence ≠ verification |
| "CI takes too long" | Waiting is mandatory |
| "I'll check later" | No. Check now. |
| "Just this once" | No exceptions. Ever. |

## Project-Specific Examples

### .NET Multi-Framework Projects

```bash
# Local verification
dotnet test --configuration Release

# This runs ALL target frameworks
# Example: net8.0, net9.0, net10.0
```

### Multi-Workflow Projects

For projects with multiple CI workflows (tests.yml, lint.yml, build.yml):

```bash
# Monitor ALL workflows
gh run list --commit <sha> --json databaseId,name,conclusion

# All must pass:
# ✅ tests.yml: success
# ✅ lint.yml: success
# ✅ build.yml: success
```

### Projects with Test Results Upload

Some projects upload test results to services like Codecov:

```bash
# Wait for primary workflow
gh run watch <run-id>

# Verify uploads completed
# Check workflow logs for "Upload complete" messages
```

## Success Criteria

Claude may ONLY claim completion when:

1. ✅ Local tests passed (verified by running them)
2. ✅ Code committed and pushed
3. ✅ CI workflow(s) found and monitored
4. ✅ ALL CI checks passed with status "success"
5. ✅ Claude has URLs/logs as evidence

## Reporting Success

When all checks pass, report with evidence:

```text
✅ Verification Complete

Local Tests: 159/159 passed
CI Status: All checks passed

Workflows:
  - tests.yml: ✅ success
    https://github.com/user/repo/actions/runs/12345
  - lint.yml: ✅ success
    https://github.com/user/repo/actions/runs/12346

Commit: abc123def
Timestamp: 2025-11-21 15:30:45

Work is verified complete.
```

## Why This Matters

From painful experience:

- "Should work" → CI fails → wasted time
- Skipping verification → broken main branch
- False completion → lost trust
- Claiming success without evidence → dishonesty

## Requirements

- **GitHub CLI** (`gh`) installed and authenticated
- **Git** repository with GitHub Actions
- Project with test suite

## The Bottom Line

**No shortcuts. No exceptions. No rationalizations.**

1. Run local tests
2. Push code
3. Wait for CI (blocking)
4. Fix failures and repeat
5. Only claim completion when CI passes

This is non-negotiable.
