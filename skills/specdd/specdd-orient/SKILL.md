---
name: specdd-orient
description: Use when Agent needs to get oriented in a SpecDD project before later work, while making no edits.
license: Apache-2.0
---

# SpecDD Orient

Use this skill to prepare for later tasks in a SpecDD project. Do not edit files.
Do not perform deep analysis unless the user asks for it.

## Skill Scope

Use this skill only for projects that already have a root `.specdd/bootstrap.md` and are therefore SpecDD projects.

If `.specdd/bootstrap.md` is missing, do not continue with this skill. Use `specdd-adopt` only when the operator explicitly asks to add or adopt SpecDD in a new or existing non-SpecDD project.

## Bootstrap Resolution

Ensure you know the active bootstrap chain for the target project. If it is not already reliable in the current context, read bootstrap files in this exact order:

1. `.specdd/bootstrap.md`
2. `.specdd/bootstrap.project.md`, if it exists
3. `.specdd/bootstrap.local.md`, if it exists

Apply them in that order. Later files may narrow or specialize earlier rules, but must not silently weaken project contracts, inherited constraints, or write authority.

Do not reread bootstrap files merely because another SpecDD skill or workflow phase starts. Reread the specific bootstrap file only when the active project root changes, a bootstrap file may have changed, or you need exact bootstrap text for a decision, quote, comparison, authorization, or report.

## Orientation Scope

This orientation-only scope is deliberately lighter than normal SpecDD spec
chain resolution because this skill makes no edits and may not have a concrete
target path.

Use it only for this skill:

1. Read the bootstrap chain and the root or main project spec named by it.
2. Read immediately relevant top-level specs needed to understand repository authority.
3. Inspect explicitly applicable or requested spec files only.

Do not treat this orientation context as write authority or as the effective
spec chain for future work. For any later concrete task, rerun normal SpecDD
spec-chain resolution for the target path, task, behavior, or changed files.

## Workflow

1. Identify the root or main project spec named by the bootstrap chain.
2. Read the root project spec and any immediately relevant top-level specs needed to understand repository authority.
3. Inspect the repository shape lightly: top-level files, major directories, and explicitly applicable or requested spec
   files.
4. When useful and available, consider consulting the `specdd-cli` skill for CLI-assisted orientation; treat any output as orientation context only.
5. Check current git status so future edits can distinguish existing work from new changes.
6. Report that orientation is complete and summarize only what is needed for readiness.

## Boundaries

- Do not edit files.
- Do not implement, review, refactor, or plan unless the user asks for that next.
- Do not infer write authority for future tasks beyond what the active bootstrap and specs say.
- Do not treat sibling or nearby specs as authority unless the active bootstrap, a governing spec, or the user request
  selects them.
- Do not turn observations from orientation into permanent project contracts.

## Report

Keep the response short. Include the bootstrap/spec files read, the main project
authority found, and any immediate blocker to accepting follow-up tasks.
