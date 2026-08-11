---
name: gjalla-test-audit
description: Audit a test suite to find tests that give false confidence — tests that encode bugs, duplicate coverage, or are so heavily mocked they can't catch real regressions. Use to improve robustness, audit coverage, or harden a risky area.
---

# Test Audit

Deep review of test suite quality to find tests that give false confidence, encode bugs, duplicate coverage, or are so heavily mocked they can't catch real regressions.

## Process

At a high level, you'll follow the steps below, then cross-reference load-bearing code with test imports. Importance can be ranked by production blast radius (which code is most depended-on — if you use gjalla, impact and change history surface this), recent bug history, and how deterministic the failure mode is.

### Phase 1: Orient

Understand the project's test infrastructure before diving in.

1. **Map test structure**: Find all test directories, count files per directory, identify naming conventions (`.test.ts`, `.pglite.test.ts`, `.integration.test.ts`, etc.)
2. **Identify test layers**: Which tests use real databases (PGlite, SQLite)? Which mock the ORM? Which mock at the service boundary? Which use `@vitest-environment node` vs `jsdom`?
3. **Identify critical components**: What are the security boundaries, data access layers, and core business logic? These are where false confidence is most dangerous.

### Phase 2: Hunt for anti-patterns

Launch parallel investigations across test layers. For each test file, read BOTH the test AND the source code it claims to test. The anti-patterns to find:

#### Anti-pattern 1: Reimplemented logic tests
Tests that never import the real code. Instead they redefine the logic inline and test their own copy. Signals:
- `@vitest-environment node` with no component/hook imports
- Local functions named `simulate*` or `handle*` that mirror source code
- Test file has zero imports from `src/` or source directories

These tests will NEVER catch a regression because they don't exercise the real code.

#### Anti-pattern 2: Tautological mock tests
Tests that mock the entire database/ORM chain with hardcoded returns, then assert those same hardcoded values. Signals:
- `mockReturnValue` / `mockResolvedValue` on `db.select().from().where()` chains
- Queue-based mock infrastructure (`_setSelectQueue`, `pushSelectResult`)
- Assertions like `expect(result).toEqual(mockReturnValue)` where `mockReturnValue` is what the mock was set up to return
- Builder pattern mocks where `.from()`, `.where()`, `.innerJoin()` all ignore their arguments

**Key test**: Could a bug in the real code (wrong table, wrong column, wrong WHERE clause, wrong JOIN) cause this test to fail? If no, the test is tautological.

#### Anti-pattern 3: Tests encoding wrong behavior
Tests whose assertions verify incorrect behavior that happens to match buggy source code. Signals:
- Test fixtures using field names that don't match the source (e.g., test uses `assignedTier` but source reads `subscriptionTier`)
- Inconsistent thresholds between services tested independently
- Mock return values that paper over logic the test claims to verify
- Test names that say one thing but assert another (e.g., "returns 403" but asserts `toBe(404)`)

**Key test**: Does the test's mock data match what real upstream code actually produces? Or was it hand-crafted to match the (possibly buggy) function under test?

#### Anti-pattern 4: Redundant companion tests
Tests that are fully covered by a more rigorous companion file. Signals:
- A `.test.ts` file that mocks the DB alongside a `.pglite.test.ts` file that tests real SQL for the same class
- An "integration" test that mocks at the same level as the "unit" test
- Multiple test files for the same source file with overlapping `describe`/`it` blocks

#### Anti-pattern 5: Placeholder tests
- `expect(true).toBe(true)`
- Tests with descriptive names but no real assertions
- Tests that call a mock and then assert the mock was called (tautology)

### Phase 3: Classify findings

Organize findings into tiers:

| Tier | Description | Action |
|------|-------------|--------|
| **Tier 1** | Tests that exercise zero real code (reimplemented logic, inline mock handlers) | Delete entire file |
| **Tier 2** | Files with mixed useful and tautological tests | Delete tautological sections, keep logic tests |
| **Tier 3** | Tautological tests that have a real companion (PGlite, integration) | Delete redundant mocked version |
| **Tier 4** | Tautological tests with NO real companion | Flag as dangerous false confidence. These need real tests written. |
| **Bugs** | Tests that encode wrong behavior in source code | Fix source code AND test |

### Phase 4: Report

Present findings as a structured report with:

1. **Tests encoding bugs** (highest priority) - these are masking real production issues
2. **Tier 1-3 deletions** with file paths and line counts
3. **Tier 4 gaps** - areas where coverage will honestly drop and needs real tests
4. **Impact analysis**: what gets more robust, what bugs may surface, coverage impact

### Phase 5: Clean up (if approved)

Execute in waves, running tests between each:

1. Delete Tier 1 files (zero real code tested)
2. Remove Tier 2 tautological sections
3. Remove Tier 3 redundant tests (where companion exists)
4. Fix tests encoding wrong behavior + fix source bugs
5. Run coverage to identify honest gaps
6. Write real tests for Tier 4 gaps (PGlite for DB-dependent code)

## Principles

- **A test that can't fail is worse than no test.** It inflates confidence without providing protection.
- **Mock at boundaries, not internals.** Mock external services (Supabase, Stripe, GitHub API). Don't mock your own database layer when you can use PGlite.
- **Round-trip tests catch key mismatches.** When function A writes data that function B reads, test them together using A's actual output as B's input. Hand-crafted fixtures can silently encode bugs.
- **Coverage numbers lie when tests are tautological.** A line is not "covered" if the mock intercepted every meaningful operation. Honest coverage comes from tests that exercise real code paths.
- **Delete before you write.** Remove false confidence first so the coverage report becomes an honest map of where you're strong and where you're exposed. Then fill gaps.
