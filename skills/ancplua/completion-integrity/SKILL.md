---
name: completion-integrity
description: Prevents shortcuts and cheating when completing tasks. Blocks commits with warning suppressions, commented tests, or deleted assertions.
---

# Completion Integrity

Git pre-commit hook that blocks commits with integrity violations.

## Install

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/install-git-hook.sh"
```

## What It Catches

| Pattern | Why It's Bad |
|---------|--------------|
| Warning suppression (`#pragma warning disable`, `eslint-disable`) | Hides problems instead of fixing them |
| Commented-out tests | Tests exist for a reason |
| Deleted assertions (>2) | Removing checks doesn't fix bugs |
| Test file deletion | Don't delete tests to make them "pass" |
| Empty catch blocks | Swallowing errors hides failures |
| Fresh TODOs (>2 per commit) | Defer work explicitly, not via comments |

## Manual Check

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/integrity-check.sh"
```

## False Positives

Sometimes suppressions are legitimate. If blocked:

1. Explain WHY the suppression is necessary in the commit message
2. The explanation should convince a reviewer
3. If you can't explain it, fix the underlying issue instead

## FAILURE CONDITIONS

You have FAILED if you:

1. Commit code with integrity violations
2. Claim "done!" without running actual verification
3. Suppress warnings instead of fixing them
4. Delete or comment out tests instead of fixing them
5. Rationalize why these rules don't apply to you
