---
name: god-plan
description: Use for /god-plan, "plan this", or before building a feature or product. Writes PLAN.md.
argument-hint: "[goal or change]"
---

# /god-plan

Size the plan to the work. When the request already lists its requirements, the plan is just the goal, those requirements with their "Done when" checks, and the slices. A new product gets every section.

1. Read STATE.md, PLAN.md and DECISIONS.md if they exist, and enough of the code to ground the plan in real files. For a large or unfamiliar codebase you may delegate the reading to a subagent of your choice and work from its draft. Before you start it, say which model and effort you picked and why, then pass both explicitly (whichever your host accepts); never let it inherit yours. A fast model at low effort is enough for reading.
2. Write `.godpowers/PLAN.md` with these sections:
   - `## Goal`: who it is for and what success looks like.
   - `## Requirements`: `- R1: <requirement>. Done when: <observable check>.` Each needs a check that a test or a person can run.
   - `## Non-goals`: what is deliberately out.
   - `## Design`: structure, data, interfaces, and failure handling that matter, naming real files.
   - `## Slices`: ordered thin end-to-end slices, `- [ ] 1. (behavior|refactor) <slice>: <how it is verified>`. One concern per slice, refactors separate from behavior changes, and each slice leaves the project working.
   - `## Open questions`: only ones that change the plan, each with who decides.
3. Append lasting choices (stack, data model, external services, trade-offs) to DECISIONS.md as `## YYYY-MM-DD: <decision>` with one line each for Context, Decision, and Why. Never edit old entries; add one that supersedes.
4. Put known risks in STATE.md, set `stage: build`, and name the first slice under Next.
5. Run `npx -y @hxp-tools/godpowers@7 lint` and fix any errors.
6. Ask the user only about open questions that block the first slice.
