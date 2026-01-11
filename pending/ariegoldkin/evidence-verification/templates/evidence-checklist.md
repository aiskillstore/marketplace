# Evidence Collection Checklist

Use this checklist to ensure complete evidence collection before marking tasks complete.

## Basic Evidence (Minimum Required)

- [ ] **Verification executed** - At least one verification type run
- [ ] **Exit code captured** - 0 for success, non-zero for failure
- [ ] **Timestamp recorded** - When verification was run
- [ ] **Evidence stored** - Added to shared context or documented

## Test Evidence

- [ ] **Tests executed** - Test suite run
- [ ] **Test exit code** - Captured (0 = all passed)
- [ ] **Test results** - Passed/failed/skipped counts
- [ ] **Test duration** - Time taken to run
- [ ] **Coverage reported** - Percentage if available
- [ ] **Test output saved** - First 10-20 lines captured

## Build Evidence

- [ ] **Build executed** - Build command run
- [ ] **Build exit code** - Captured (0 = success)
- [ ] **Build duration** - Time taken to build
- [ ] **Artifacts created** - List of output files/sizes
- [ ] **Build errors** - Count of errors (should be 0)
- [ ] **Build warnings** - Count of warnings
- [ ] **Build output saved** - Key lines captured

## Code Quality Evidence

- [ ] **Linter executed** - ESLint, Ruff, Clippy, etc.
- [ ] **Linter exit code** - Captured (0 = no errors)
- [ ] **Linter errors** - Count (should be 0)
- [ ] **Linter warnings** - Count
- [ ] **Type checker run** - TypeScript, mypy, etc. (if applicable)
- [ ] **Type errors** - Count (should be 0)
- [ ] **Security scan** - OWASP checks (if applicable)

## Deployment Evidence (Production)

- [ ] **Pre-deployment checks** - All tests/builds pass
- [ ] **Deployment executed** - Deployment command run
- [ ] **Deployment exit code** - Captured (0 = success)
- [ ] **Environment verified** - Correct deployment target
- [ ] **Health check** - Application responds correctly
- [ ] **Smoke tests** - Basic functionality verified
- [ ] **Error rate** - Below acceptable threshold
- [ ] **Rollback verified** - Rollback capability tested

## Documentation

- [ ] **Evidence template used** - Used appropriate template
- [ ] **Context updated** - Evidence added to shared context
- [ ] **Evidence files stored** - Logs saved in `.claude/quality-gates/evidence/`
- [ ] **Completion message** - Includes evidence summary

## Quality Standards Met

**Minimum (Choose ONE):**
- [ ] Tests pass OR build succeeds OR linter passes

**Production-Grade (ALL must pass):**
- [ ] Tests pass (exit 0)
- [ ] Coverage ≥70%
- [ ] Build succeeds (exit 0)
- [ ] No critical linter errors
- [ ] Type checker passes

**Gold Standard (ALL must pass):**
- [ ] Tests pass (exit 0)
- [ ] Coverage ≥80%
- [ ] Build succeeds (exit 0)
- [ ] No linter warnings
- [ ] Type checker passes
- [ ] Security scan passes
- [ ] Performance within thresholds
- [ ] Accessibility audit passes

---

## Quick Start

1. Run verification commands (tests, build, lint)
2. Capture exit codes (0 = success)
3. Document results using templates
4. Add evidence to shared context
5. Include evidence summary in completion message
6. Only mark complete if evidence shows success

---

## Example Evidence Summary

```markdown
## Task Complete: Implement User Login

**Evidence:**
- ✅ Tests: Exit 0 (15 passed, 0 failed, coverage 89%)
- ✅ Build: Exit 0 (bundle created: 245 KB)
- ✅ Linter: Exit 0 (0 errors, 1 warning)
- ✅ Types: Exit 0 (no type errors)

**Timestamp:** 2025-11-02 14:30:22
**Quality Standard:** Production-Grade ✅

Ready for review.
```
