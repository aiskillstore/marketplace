---
name: systematic-debugging
description: Four-phase root cause investigation before attempting fixes. Use when debugging bugs, test failures, or unexpected behavior.
---

# Systematic Debugging

**ALWAYS find root cause before attempting fixes. Symptom fixes are failure.**

## When to Use

- Encountering bugs or test failures
- Unexpected behavior in code
- Before proposing any fix

## The Four Phases

### Phase 1: Root Cause Investigation

Before proposing any solution:

1. **Read error messages thoroughly** - Don't skip warnings or stack traces; they often contain exact solutions
2. **Reproduce consistently** - Verify you can trigger the issue reliably with documented steps
3. **Check recent changes** - Examine `git diff`, dependencies, and configuration modifications
4. **Gather diagnostic evidence** - In multi-component systems, add instrumentation at component boundaries
5. **Trace data flow** - Backward trace from the error to find where bad values originate

### Phase 2: Pattern Analysis

Establish the pattern before fixing:

1. Locate similar **working** code in the codebase
2. Read reference implementations **completely** (not skimmed)
3. List **every difference** between working and broken code
4. Understand all dependencies and assumptions

### Phase 3: Hypothesis Testing

Apply scientific method:

1. State your hypothesis clearly: "I believe X is failing because Y, evidenced by Z"
2. Test with the **smallest possible change**
3. Change **only ONE variable** at a time
4. Verify results before proceeding

### Phase 4: Implementation

Fix the root cause systematically:

1. Create a failing test case first (TDD)
2. Implement a **single fix** addressing only the root cause
3. Verify the fix resolves the issue without breaking other tests
4. If fix doesn't work, return to Phase 1

## Red Flags - STOP Immediately

- Proposing fixes without understanding the issue
- Attempting multiple simultaneous changes
- Assuming problems without verification
- Skipping evidence gathering
- Making "quick fixes" before investigation

## When 3+ Fixes Fail

**STOP.** This signals an architectural problem, not a fixable bug:

1. Do not attempt another fix
2. Return to Phase 1
3. Question whether the underlying pattern/design is sound
4. Ask: "Should we refactor architecture vs. continue fixing symptoms?"

**Random fixes waste time and create new bugs. Quick patches mask underlying issues.**

## Results

Systematic approach: 15-30 minutes to resolution with 95% first-time success
vs. Trial-and-error: 2-3 hours of thrashing with 40% success and new bugs introduced
