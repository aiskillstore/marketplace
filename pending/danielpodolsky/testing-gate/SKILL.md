---
name: Testing Gate
description: Gate 6 - Verify tests exist and cover critical paths. Issues result in WARNINGS (encourages tests, doesn't block).
---

# Gate 6: Testing Verification

> "Tests are proof of understanding. If you can't test it, do you really understand it?"

## Purpose

This gate encourages juniors to write tests for their features. Unlike the Ownership Gate, this does NOT block completion - it issues warnings to encourage the testing habit.

## Gate Status

- **PASS** — Tests exist and cover critical paths
- **WARNING** — No tests or insufficient coverage (can proceed with note)

**Note:** This gate does NOT block. The goal is to build the testing habit through encouragement, not enforcement.

---

## Gate Questions

Ask in sequence:

### Question 1: Test Existence
> "What tests did you write for this feature?"

**Looking for:**
- At least one test file exists
- Tests are actually running (not skipped)
- Tests are meaningful (not just `expect(true).toBe(true)`)

**If no tests:**
> "I noticed there aren't tests for this feature. Testing isn't required to complete, but it's a habit worth building. What would you test if you had time?"

### Question 2: Coverage Strategy
> "What does your test prove about this feature?"

**Looking for:**
- Happy path covered
- At least one edge case considered
- Error states (if applicable)

**Follow-up:**
> "If I broke [specific part], which test would catch it?"

### Question 3: Test Quality
> "Show me your most important test. What behavior does it verify?"

**Looking for:**
- Testing behavior, not implementation
- Clear test names
- AAA pattern (Arrange, Act, Assert)

---

## Response Templates

### If PASS (Tests Exist)

```
✅ TESTING GATE: PASSED

Nice work including tests! I see you covered:
- [Specific test they wrote]
- [Edge case they handled]

Key strength: [Something they did well]

Consider adding: [One suggestion for future]

Moving to code review...
```

### If WARNING (No Tests)

```
⚠️ TESTING GATE: WARNING

No tests found for this feature. That's okay - we can proceed.

But here's why tests matter:
1. **Interview Gold**: "I implemented tests for critical flows..."
2. **Confidence**: Know your changes don't break things
3. **Documentation**: Tests show how code should be used

Quick win for next time:
- Test the happy path first
- Add one edge case
- That's already better than most!

Proceeding to code review...
```

### If WARNING (Weak Tests)

```
⚠️ TESTING GATE: WARNING

Tests exist but could be stronger:

**Issue**: [What's missing or weak]
**Question**: "If [scenario], would your tests catch it?"

This doesn't block you, but consider:
- [Specific improvement suggestion]

Proceeding to code review...
```

---

## What Makes a Good Test Suite?

| Level | Coverage | Characteristics |
|-------|----------|-----------------|
| Minimal | 1-2 tests | Happy path only |
| Good | 3-5 tests | Happy path + main edge cases |
| Strong | 5-10 tests | Happy path + edge cases + error states |
| Interview-Ready | Full pyramid | Unit + Integration + E2E for critical flows |

---

## Socratic Guidance

If they want to add tests but don't know where to start:

1. "What's the ONE thing that would be really bad if it broke?"
2. "What input would a user never send but a hacker might?"
3. "What happens when the server is slow or returns an error?"

---

## Stack-Specific Hints

| Stack | Suggestion |
|-------|------------|
| Vite + React | "Vitest + React Testing Library is fast and integrated" |
| Next.js | "Vitest or Jest works great with Next" |
| API/Backend | "Test your endpoints with supertest or native HTTP" |
| Python | "pytest is the standard - simple and powerful" |

---

## Interview Connection

> "Testing is interview gold."

When they pass this gate with tests:
- Note it for their STAR story
- "You can talk about your testing strategy in interviews"
- "What percentage coverage did you achieve?" (for resume)

When they skip tests:
- "Next time, even 2-3 tests makes a huge difference for your portfolio"
- "Employers love seeing test files in your repo"

---

## Why WARNING Not BLOCKING?

1. **Encouragement > Enforcement**: Build the habit through positive reinforcement
2. **Some features are trivial**: Not everything needs tests
3. **Time constraints exist**: Production pressure is real
4. **Learning curve**: Testing has a learning curve; don't block progress

The goal is to make testing feel valuable, not punitive.
