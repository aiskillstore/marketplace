---
name: specdd-refactor
description: Use when Agent needs to refactor code, tests, docs, specs, or project structure while preserving active SpecDD behavior.
license: Apache-2.0
---

# SpecDD Refactor

Use this skill for structure changes that should not change specified behavior.

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

## Spec Chain Resolution

Before planning, editing, reviewing, testing, or reporting on a target, ensure the effective spec chain for that target is known:

1. Identify the target path, task, behavior, or changed files.
2. Resolve the effective spec chain using the active bootstrap rules.
3. Include same-directory basename specs when applicable.
4. Walk ancestor specs from the selected content root to the target.
5. Read explicit `References` only when they affect the requested work.
6. Read or reread the specific governing specs needed for the current decision when exact contract text is not already reliable in context.
7. Identify the nearest local spec that grants write authority before any edit.

Do not infer authority from similar filenames, nearby files, symbols, module names, or conventions unless the active bootstrap or a governing spec explicitly defines that mapping.

Do not reread an entire chain just because a workflow phase changed. Reopen the narrowest relevant spec when you need to apply, quote, compare, authorize, report, or edit against exact text, when the target scope changes, when a governing spec may have changed, or when earlier context came only from CLI output or a summary.

## Workflow

1. Identify public contracts, scenarios, invariants, dependencies, and forbidden boundaries.
2. Confirm write authority for every file that would move or change.
3. Prefer small mechanical steps with verification between risky changes.
4. Run baseline checks before refactoring when practical, then rerun after.

## Refactor Rules

- Preserve behavior described by active specs.
- Do not move responsibility across spec boundaries unless the specs or user request require it.
- Do not widen dependencies or add forbidden imports.
- Do not rename public symbols, paths, or contracts unless explicitly in scope.
- Update specs, docs, and tests only when the refactor changes structure they describe.

If behavior must change to complete the request, stop treating it as a pure
refactor and resolve authority for the behavior change.
