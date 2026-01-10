---
name: verification-before-completion
description: "Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always"
---

# Verification Before Completion

## Overview

This skill enforces a critical discipline: **never claim completion without fresh verification evidence**.

The most common failure mode for AI agents is claiming success without actually verifying. This skill prevents that by requiring explicit verification steps before any completion claim.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

## The Process

### Before ANY Completion Claim

```
1. IDENTIFY: What command proves this claim?
   → "Tests pass" requires: npm test / pytest / go test
   → "Build succeeds" requires: npm run build / make
   → "Lint clean" requires: npm run lint / eslint
   → "Type check passes" requires: tsc --noEmit / mypy

2. RUN: Execute the FULL command (fresh, complete)
   → Not cached results
   → Not partial output
   → Not "I ran it earlier"

3. READ: Full output, check exit code, count failures
   → Exit code 0 = success
   → Exit code non-zero = failure
   → Count actual pass/fail numbers

4. VERIFY: Does output confirm the claim?
   → "All tests pass" = 0 failures in output
   → "Build succeeds" = no errors, artifacts created
   → "No lint errors" = 0 problems found

5. ONLY THEN: Make the claim with evidence
   → Quote the relevant output
   → Include exit code
   → Show pass/fail counts
```

## Verification Commands by Context

### Flow Exit Gates

| Flow | Verification Command | Success Criteria |
|------|---------------------|------------------|
| /flow-prd | `validate-constitution --type prd` | Exit 0, no violations |
| /flow-epic | `validate-constitution --type epic` | Exit 0, no violations |
| /flow-dev | `npm test && npm run build` | All tests pass, build succeeds |
| /flow-qa | `npm test && npm run lint` | All pass, no blockers |
| /flow-release | `gh pr checks` | All checks pass |

### Common Development Tasks

| Claim | Required Verification |
|-------|----------------------|
| "Tests pass" | Run full test suite, show output |
| "Build succeeds" | Run build command, show output |
| "Lint clean" | Run linter, show 0 errors |
| "Type check passes" | Run type checker, show output |
| "No regressions" | Run affected tests, compare before/after |
| "Bug fixed" | Show failing test → fix → passing test |

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "I just ran it" | Run it again. Fresh evidence required. |
| "It was passing before" | Before ≠ now. Verify current state. |
| "The change is trivial" | Trivial changes break things. Verify. |
| "I'm confident it works" | Confidence ≠ evidence. Run the command. |
| "Tests are slow" | Slow tests > broken production. Run them. |
| "I'll verify after commit" | Verify BEFORE commit. Always. |
| "The CI will catch it" | You catch it first. Don't waste CI cycles. |
| "It's just documentation" | Doc changes can break builds. Verify. |

## Red Flags - STOP

If you find yourself:
- Saying "should work" without running verification
- Claiming "tests pass" without showing output
- Saying "I believe" instead of "I verified"
- Skipping verification "just this once"
- Trusting cached or stale results

**STOP. Run the verification command. Show the evidence.**

## Evidence Format

When claiming completion, always include:

```markdown
## Verification Evidence

**Command**: `npm test`
**Exit Code**: 0
**Output Summary**:
- Tests: 42 passed, 0 failed
- Coverage: 85%
- Duration: 12.3s

**Conclusion**: All tests pass. Ready for commit.
```

## Integration with CC-DevFlow

### Every Flow Exit Gate

```yaml
Exit Gate Verification:
  1. Identify required verification commands
  2. Run each command fresh
  3. Capture full output
  4. Verify success criteria met
  5. Document evidence in EXECUTION_LOG.md
  6. Only then proceed to next stage
```

### Task Completion

```yaml
Task Completion Verification:
  1. Run task-specific tests
  2. Verify acceptance criteria met
  3. Show evidence in task completion message
  4. Mark task complete only with evidence
```

## The Discipline

This skill is about **intellectual honesty**. It's easy to believe something works. It's harder to prove it.

The discipline is:
1. **Assume nothing** - Don't trust memory or intuition
2. **Verify everything** - Run the actual commands
3. **Show evidence** - Quote output, not beliefs
4. **Fresh results only** - No stale or cached data

## Cross-Reference

- Constitution Article I: Quality First (complete implementation)
- Constitution Article VI: Test-First Development (TDD)
- rationalization-library.md: Cross-Article rationalizations

---

**[PROTOCOL]**: 变更时更新此头部，然后检查 CLAUDE.md
