---
name: prove-it-ran
description: Verify that tests, builds and checks actually ran and exercised the changed code, before claiming a task is done. Use before reporting completion, or when asked to prove tests ran or verify a fix.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Prove it ran

Goal: never say "done" or "tests pass" on the strength of belief. Show evidence that the checks ran, covered the change, and would have caught a failure.

## Procedure

1. **List the claims** you are about to make ("the bug is fixed", "all tests pass", "the build succeeds", "no lint errors").
2. **For each claim, run the command now**, from a clean state of your edits, and capture the output. Do not rely on output from earlier in the session if you edited files since.
3. **Confirm the check really ran:**
   - Test runners: the output shows a test count above zero, and the new or changed tests appear by name or file. "0 tests", "no tests found" or "skipped" is not a pass.
   - Check the exit code, not just the wording (`echo $?` right after the command, or the runner's summary line).
   - Make sure the runner picked up your files: right directory, right config, test file matches the naming pattern.
4. **Confirm it covers the change.** For a bug fix, the test must fail without the fix: temporarily revert the fix (`git stash` the source change only, or comment it out), run the test, see it fail, restore, see it pass. If you cannot do this, say so.
5. **Check for silent skips.** Search output for `skipped`, `xfail`, `pending`, `todo`, and your own `.only`/`.skip`/`pytest.mark.skip` leftovers (`rg "\.only\(|\.skip\(|xit\(|fdescribe|pytest.mark.skip"`).
6. **Run the wider checks** the project defines (lint, type check, build). Report exact commands.
7. **Report in a table** and be explicit about anything you did not or could not run.

## Report

```
| Claim | Command | Evidence (count / exit code / key line) | Verified |
|---|---|---|---|
| Fix works | <cmd> | 1 failing before, passes after | yes |
| Suite passes | <cmd> | 212 passed, 0 failed, exit 0 | yes |
| Lint clean | <cmd> | not run: no lint script | no |
```

## Rules

- "Should work" and "looks right" are not evidence. Replace them with a command and its output or say you did not verify.
- Never edit a test, snapshot or threshold only to turn a check green. If a test is wrong, say why and ask.
- Report failures in full, including ones that look unrelated. Mark pre-existing failures as such only if you confirmed them on a clean checkout.
- If something cannot be run here (needs credentials, a device, production), list it under "Not verified" with how the user can check.
