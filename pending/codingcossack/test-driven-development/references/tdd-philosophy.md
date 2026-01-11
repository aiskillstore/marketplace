# TDD Philosophy and Rationalizations

**Load this reference when:** Encountering resistance to TDD, rationalizing skipping TDD, or needing to explain why test-first matters.

## Contents

- Why Order Matters
- Common Rationalizations (with rebuttals)
- The Sunk Cost Problem
- Refactoring and TDD

## Why Order Matters

### "I'll write tests after to verify it works"

Tests written after code that pass don't prove they would have caught the bug. You have no evidence the test actually validates the requirement because:
- You never saw it fail against missing functionality
- The test may be coupled to implementation, not behavior
- You test what you built, not what's required
- Edge cases you forgot remain untested

Test-first forces you to see the test fail, proving it actually tests something real.

### "I already manually tested all the edge cases"

Manual testing is ad-hoc:
- No record of what you tested
- Can't re-run when code changes
- Easy to forget cases under pressure
- "It worked when I tried it" ≠ comprehensive

Automated tests are systematic. They run the same way every time.

### "Deleting X hours of work is wasteful"

Sunk cost fallacy. The time is already gone. Your choice now:
- Delete and rewrite with TDD (X more hours, high confidence)
- Keep it and add tests after (30 min, low confidence, likely bugs)

The "waste" is keeping code you can't trust.

### "TDD is dogmatic, being pragmatic means adapting"

TDD IS pragmatic:
- Finds bugs before commit (faster than debugging after)
- Prevents regressions (tests catch breaks immediately)
- Documents behavior (tests show how to use code)
- Enables refactoring (change freely, tests catch breaks)

"Pragmatic" shortcuts = debugging in production = slower.

### "Tests after achieve the same goals - it's spirit not ritual"

No. Tests-after answer "What does this do?" Tests-first answer "What should this do?"

Tests-after are biased by your implementation. You test what you built, not what's required. You verify remembered edge cases, not discovered ones.

Tests-first force edge case discovery before implementing.

30 minutes of tests after ≠ TDD. You get coverage, lose proof tests work.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "Keep as reference, write tests first" | You'll adapt it. That's testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |
| "Test hard = design unclear" | Listen to test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD faster than debugging. Pragmatic = test-first. |
| "Manual test faster" | Manual doesn't prove edge cases. You'll re-test every change. |
| "Existing code has no tests" | You're improving it. Add tests for existing code. |

## The Sunk Cost Problem

When you've written **new code** without tests:

1. **The code exists but is unverified** - You don't know if it works correctly
2. **Adding tests after biases them** - You test what you built, not what's required
3. **You'll rationalize keeping it** - "Just adapt while writing tests" = testing after

The solution for new code you wrote: Delete completely. Don't keep as reference. Implement fresh from tests.

**This does NOT apply to legacy/inherited code.** For existing systems with no tests, use characterization tests to capture current behavior first, then refactor behind that safety net.

## Refactoring and TDD

Refactoring does not require a new failing test. By definition:
- Refactoring = changing structure without changing behavior
- Tests stay green throughout
- No new failing test needed

The "failing test first" rule applies to **behavior changes**, not structural improvements. The refactor step in Red-Green-Refactor is explicitly a "keep tests green" phase.

This feels wasteful but produces verified code. The alternative produces code you can't trust.
