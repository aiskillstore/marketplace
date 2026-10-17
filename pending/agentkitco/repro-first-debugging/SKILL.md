---
name: repro-first-debugging
description: Debug by reproducing the failure first, then forming and testing hypotheses before editing code. Use when asked to fix a bug, a failing test, a crash or unexpected behavior.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Reproduce first, then fix

Goal: fix the cause, prove the fix, and avoid editing on a guess.

## Process

1. **Restate the failure** in one line: expected behavior, actual behavior, where it was seen. Ask for the error text, steps or input if they are missing. Do not start from a vague description.
2. **Reproduce it.** Run the failing test or the smallest command that triggers it. Capture the exact output. If you cannot reproduce it, stop and report what you tried; do not "fix" something you cannot see fail.
3. **Shrink it.** Reduce to the smallest input or test that still fails. Prefer turning the reproduction into an automated failing test in the project's test framework.
4. **List hypotheses.** Write two or three plausible causes, each with the evidence that would confirm or kill it. Rank by likelihood and cost to check.
5. **Test the hypotheses, cheapest first.** Read the code path, add temporary logging or assertions, bisect (`git bisect` or by reverting suspects), check recent changes (`git log -p -- <path>`). Record what each check showed. Remove temporary logging afterwards.
6. **Fix the cause, not the symptom.** Make the smallest change that explains the evidence. If the fix needs a workaround, say so and why.
7. **Prove it.** The failing test now passes; run the nearby tests and the full suite if fast. Show the before and after output.
8. **Look for siblings.** Search for the same pattern elsewhere (`rg`) and report, but do not change unrelated code without asking.

## Report

```
Failure: <expected vs actual>
Reproduction: <command> -> <output summary>
Root cause: <what and why, with file:line>
Evidence: <the checks that confirmed it, and the hypotheses ruled out>
Fix: <summary of the change>
Verification: <failing test now passes; commands and results>
Related risks: <similar code found, not changed>
```

## Rules

- No code edits before step 2 succeeds, unless the user explicitly asks for a blind fix.
- Never delete or weaken a test to make it pass.
- Never claim success without showing a command that failed before and passes now.
- If three hypotheses fail, stop and report what you know and what you need.
