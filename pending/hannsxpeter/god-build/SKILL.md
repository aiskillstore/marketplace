---
name: god-build
description: Use for /god-build, "build it", "implement the plan", or continuing work in progress. Builds test-first.
argument-hint: "[slice or change]"
---

# /god-build

1. Read STATE.md and PLAN.md. Work from the next unchecked slice, the one the user named, or the requirements the request lists, kept under Goal in STATE.md. If there is none of these and the change is not trivial, run /god-plan first.
2. For each slice or requirement:
   - Write or extend a test for its check and watch it fail, then make it pass with the smallest change that fits the existing code.
   - Run the targeted tests directly while you work, and `npx -y @hxp-tools/godpowers@7 fast` after each slice (cheap, never recorded). The recorded check comes once, at the end. Never weaken, skip, or delete a test to get green.
   - Keep refactor slices apart from behavior slices; do not change behavior inside a refactor.
   - Tick the slice in PLAN.md, if there is one.
3. Independent slices that touch different files can go to subagents of your choice, run however you prefer, one slice each, with the slice text, the files involved, and the verify command. Before you start each one, say which model and effort you picked for its slice and why, then pass both explicitly (whichever your host accepts); never let it inherit yours. Size both to the slice: a small, fast model at low effort for mechanical slices, a stronger model or higher effort only where the logic is tricky. Run the full check yourself after they return (step 5).
4. Record lasting choices in DECISIONS.md as you make them. If a design choice turns out wrong, record the new decision and adjust the remaining slices.
5. When every slice is done, record the project check once on the final code: `npx -y @hxp-tools/godpowers@7 verify "<verify command>"`. Fix and re-run until it passes. Then set `stage: review` in STATE.md and suggest /god-review.
6. Report what changed, the verify result, and what is left.
