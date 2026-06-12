---
name: specdd-task
description: Use when Agent needs to find, add, interpret, organize, or update SpecDD `Tasks` entries.
license: Apache-2.0
---

# SpecDD Task

Use this skill for `Tasks` sections in `.sdd` files.

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

1. Ensure the applicable spec chain for the requested scope is known, including inherited constraints.
2. Focus task handling on task-bearing specs that apply to the requested scope.
3. When useful and available, consider consulting the `specdd-cli` skill to find task-bearing specs or validate edited specs; read or reread governing specs directly when exact task or authority text is needed.
4. Treat parent tasks as planning context unless the user targets them directly.
5. Update task status only in the currently targeted spec unless instructed otherwise.

## Task Handling

- Add tasks only when they are local, actionable, and consistent with inherited constraints.
- Keep task text concise and implementation-oriented.
- Mark `[x]` only after the work and relevant checks are complete.
- Use `[!]` for blocked work and `[?]` for unresolved design decisions.
- Use `[-]` only when the task is intentionally skipped and the reason is clear.
- Do not use tasks to override `Must`, `Must not`, `Forbids`, or write authority.
- Do not complete unrelated tasks while handling a requested task.

When reporting, list task ids or exact task text, status changes, verification,
and any task that remains blocked or uncertain.
