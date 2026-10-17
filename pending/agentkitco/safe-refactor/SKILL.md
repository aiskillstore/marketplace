---
name: safe-refactor
description: Refactor in small, verified steps, with behavior locked by tests before any change. Use when asked to refactor, clean up, rename, extract or restructure code without changing behavior.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Refactor without changing behavior

Goal: improve structure while behavior stays identical, proven after every step.

## Before touching code

1. **State the goal and the boundary** in two lines: what gets better (readability, duplication, testability) and what must not change (public API, output format, performance envelope). Confirm with the user if the boundary is unclear.
2. **Find the safety net.** Locate the tests that cover the code. Run them and record the baseline (pass count, any pre-existing failures). Pre-existing failures are not yours to fix silently; list them.
3. **Close gaps.** If the code to change has no tests, write characterization tests first: run the code with realistic inputs, record what it currently does (even if odd), and assert exactly that. Commit or save these before refactoring.
4. **Check the blast radius.** Search for callers and dependents (`rg`), including tests, scripts, docs and config that mention the names you will change. Public or exported symbols need a deprecation path or an explicit go-ahead.

## During

- **One kind of change per step**: rename, or extract, or move, or inline. Never mix a refactor with a bug fix or a feature.
- **After every step** run the relevant tests plus type check or lint. If red, undo the step (`git restore` or revert your last edit) and try a smaller step. Do not debug forward through a broken refactor.
- **Keep diffs reviewable.** Aim for steps a person can review in minutes. Prefer several small commits if the user wants commits.
- **Do not "improve" while you are here**: unrelated formatting, dependency bumps and style changes go in a separate list at the end.
- Preserve behavior including error messages, ordering, logging and edge cases, unless the user says otherwise.

## Finish

Report: the steps taken, tests run and results, what you deliberately did not change, bugs or smells you noticed but left alone, and any behavior you are not sure is preserved (for example, code with no coverage that you could not exercise).

## Stop and ask when

- Tests cannot be run, or the baseline is red for reasons you cannot explain.
- The change needs a public API break.
- You find a real bug in the code being moved. Report it; fix it as its own change.
