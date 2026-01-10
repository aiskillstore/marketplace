---
name: verification-before-completion
description: |
  Force verification before claiming success or completion. Prevents false "it works" claims.
  Triggers when about to say "done", "complete", "works", "fixed", or "the implementation is ready".
  Requires actually running builds/tests and showing output before claiming success.
---

# Verification Before Completion

Force verification before claiming success or completion. Prevents false "it works" claims.

## Purpose

Claude often claims things "work" or are "complete" without actually verifying. This skill ensures
actual verification happens before any success claim.

## Triggers

Activate this skill when you're about to say ANY of:

- "Done"
- "Complete"
- "Finished"
- "Works"
- "Fixed"
- "The implementation is ready"
- "This should work"
- "I've implemented..."

## NEVER Claim Success Without

### For Code Changes

- [ ] `dotnet build` passes (no errors)
- [ ] `dotnet test` passes (or explicit reason why skipped)
- [ ] No new warnings introduced
- [ ] Actually ran the code and showed output

### For Factual Claims

- [ ] Verified against assertions.yaml
- [ ] WebSearch if claim involves dates/versions/status
- [ ] Source cited

### For "It Works" Claims

- [ ] Actually executed the code
- [ ] Showed the output to user
- [ ] Tested at least one edge case

### For "Bug Fixed" Claims

- [ ] Reproduced the original bug
- [ ] Applied the fix
- [ ] Verified bug no longer occurs
- [ ] Ran regression tests

## Red Flag Thoughts (REJECT THESE)

| If you're about to say... | Stop and... |
|---------------------------|-------------|
| "This should work" | Actually test it |
| "The fix is complete" | Run the build |
| "I've implemented the feature" | Show test output |
| "The bug is fixed" | Reproduce - fix - verify |
| ".NET 10 preview supports..." | WebSearch to verify version |
| "This is the correct approach" | Cite source or run tests |

## Output Format

Before ANY completion claim, show:

```markdown
## Verification Checklist

### Build Status

- [ ] `dotnet build` - [PASS/FAIL]
- [ ] `dotnet test` - [PASS/FAIL/SKIPPED: reason]

### Verification Steps Performed

1. [What you actually did]
2. [What output you saw]
3. [What edge case you tested]

### Confidence

[high/medium/low] - [why]

### Ready to Claim Complete

[YES/NO] - [if NO, what's missing]
```

## Anti-Pattern Examples

**WRONG:**

```text
"I've fixed the null reference bug. The implementation is complete."
[No build run, no test run, no verification shown]
```

**CORRECT:**

```text
"Let me verify the fix...

$ dotnet build
Build succeeded.

$ dotnet test --filter "NullReferenceTests"
Passed! 3/3 tests passing.

Verification complete. The null reference bug is fixed."
```

**WRONG:**

```text
"This React component should render correctly now."
```

**CORRECT:**

```text
"Let me verify...

$ npm run dev
[Shows browser screenshot or console output]

Component renders correctly. Tested:
- Initial load
- Empty state
- Error state

Verification complete."
```

## Integration

This skill is the FINAL checkpoint before claiming completion:

```text
[all other skills] - analysis complete
     |
[implementation] - code written
     |
[verification-before-completion] - THIS SKILL
     |
     +-- Run build
     +-- Run tests
     +-- Show output
     +-- THEN claim success
     |
[Present to user] - "Ready to proceed?"
```

## The Golden Rule

> **If you didn't run it, you don't know if it works.**
> **If you didn't verify it, don't claim it's complete.**
