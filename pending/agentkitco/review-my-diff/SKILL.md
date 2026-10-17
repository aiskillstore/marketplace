---
name: review-my-diff
description: Self-review your uncommitted or branch changes before opening a PR, with findings ranked by severity and backed by file and line evidence. Use when asked to review my changes, check my diff or get ready for review.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Review my diff before a human does

Goal: catch the problems a reviewer would catch, in order of how much they matter. You are reviewing, not rewriting: do not edit files unless asked.

## Steps

1. **Get the change.** Run `git status --short`, then `git diff` (unstaged) and `git diff --staged`. For a branch, find the base (`git merge-base HEAD origin/main` or the default branch) and run `git diff <base>...HEAD`. If the diff is huge, review it by directory and say so.
2. **State the intent** in one sentence, inferred from commit messages, branch name or the user's request. If you cannot tell, ask once.
3. **Read the whole diff, then the code around risky hunks** (callers, tests, config). A diff hides what it did not touch.
4. **Check in this order:**
   1. Correctness: wrong conditions, off-by-one, null/empty cases, error paths, concurrency, resource cleanup.
   2. Safety: input validation, auth checks, secrets, injection, destructive operations, migrations that lock or lose data.
   3. Tests: does a test fail without this change? Are the new branches covered? Any test that asserts nothing?
   4. Compatibility: public API, config, database, file formats, callers outside this repo.
   5. Maintainability: dead code, copy-paste, unclear names, debug leftovers (`console.log`, `print`, `TODO`, commented code).
   6. Scope: unrelated edits that should be a separate PR.
5. **Run what exists**: the project's tests, lint and type check, if they are quick. Report the exact commands and results. If you did not run something, say so.

## Output format

```
Intent: <one sentence>
Checks run: <commands and results, or "none">

BLOCKER (fix before merging)
- <file>:<line> <problem>. Why it matters: <consequence>. Suggested fix: <short>

SHOULD FIX
- <file>:<line> ...

NITS (optional)
- ...

Looks good
- <specific things that are right, so the author knows what to keep>

Questions for the author
- <things you could not determine from the code>
```

## Rules

- Every finding names a file and line, and says what breaks. No "consider improving readability" without a specific line.
- If you find nothing in a category, say "nothing found" rather than inventing a nit.
- Distinguish "I verified this" from "this looks suspicious". Do not claim a bug you did not trace.
- Never approve. End with a recommendation (ready, ready after fixes, or needs rework) and the reason.
