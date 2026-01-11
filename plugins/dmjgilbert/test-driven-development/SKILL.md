---
name: test-driven-development
description: Enforce RED-GREEN-REFACTOR cycle. Use when implementing features, fixing bugs, or writing any production code.
---

# Test-Driven Development

**Write the test first. Watch it fail. Write minimal code to pass.**

## The Iron Law

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

Any code written before its corresponding test must be deleted entirely - no exceptions for "reference" or "adapting" existing work.

## Red-Green-Refactor Cycle

### RED: Write Failing Test

1. Write ONE minimal failing test demonstrating desired behavior
2. Use clear naming that describes the behavior
3. Test real code, not mocks (mock only external dependencies)
4. Focus on ONE behavior per test

### Verify RED (CRITICAL)

Run tests and confirm:

- Test **fails** (not errors)
- Failure indicates missing feature
- Error message matches expectations

**If test passes immediately → DELETE IT** (it proves nothing)

### GREEN: Make It Pass

1. Implement the **simplest** code that passes the test
2. Avoid over-engineering
3. Don't add features not requested
4. Keep scope narrow

### Verify GREEN

- All tests pass
- No other tests broke

### REFACTOR: Clean Up

1. Clean up while ALL tests remain green
2. Remove duplication (DRY)
3. Improve naming
4. Extract helpers if needed

## Why Tests-First Matters

Tests written after code pass immediately, proving nothing about their validity. Tests-first:

- Force discovery of edge cases before implementation
- Provide systematic verification impossible with manual testing
- Document expected behavior

## Common Rationalizations (ALL REJECTED)

| Excuse                               | Why It's Wrong                                 |
| ------------------------------------ | ---------------------------------------------- |
| "Too simple to test"                 | Simple code still needs verification           |
| "I'll test after"                    | Tests-after pass immediately, proving nothing  |
| "Already manually tested"            | Manual testing isn't repeatable or documented  |
| "Deleting hours of work is wasteful" | Sunk cost fallacy - untested code is liability |

## When to Use TDD

**Always:** New features, bug fixes, refactoring, behavior changes

**Exceptions only:** Throwaway prototypes, generated code, config files (with permission)

## Red Flags Requiring Restart

- Code written before test
- Test passes immediately
- Can't explain why test should fail
- Rationalizing "just this once"

→ DELETE the code and recommence with failing test

## When 3+ Test Fixes Fail

**STOP.** This signals an architectural problem:

1. Return to investigation phase
2. Question whether the underlying pattern is sound
3. Discuss with user before attempting more fixes
