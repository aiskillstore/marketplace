---
name: specdd-author
description: Use when Agent needs to author or revise SpecDD `.sdd` specs in an existing SpecDD project.
license: Apache-2.0
---

# SpecDD Author

Use this skill to create or improve specs in an existing SpecDD project.
If `.specdd/bootstrap.md` is missing, use `specdd-adopt` first.
Do not change implementation files unless the user explicitly asks for implementation work too.

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

1. Ensure existing ancestor specs for the target area are known before adding new specs; reread the nearest relevant spec when exact wording matters.
2. Identify the smallest useful spec boundary for the requested authoring work.
3. When useful and available, consider consulting the `specdd-cli` skill for CLI-assisted spec discovery or linting; read or reread relevant governing specs directly when exact contract text is needed.
4. Treat the user's explicit request as target scope, then create or edit `.sdd` files only inside authority granted by the active spec chain.
5. Keep specs short, local, behavioral, and constraint-oriented.

## Authoring Rules

- Prefer a root or nearest-area spec before adding narrow child specs.
- Use path-based ownership and explicit `References`; do not imply authority from similar names or nearby files.
- Include only sections that add useful local authority, constraints, behavior, tasks, or context.
- Use `Can modify` or `Owns` to make write authority discoverable.
- Do not copy the full SpecDD framework rules into project specs.
- Do not turn uncertain observations into durable contracts.
- If write authority, ownership, public behavior, or security scope is unclear, stop and ask.

## Reporting

Report the bootstrap files and specs used, specs created or changed, intended governing scope, and any unresolved authoring decisions.
