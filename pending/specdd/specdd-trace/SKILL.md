---
name: specdd-trace
description: Use when Agent needs to trace SpecDD specs to code, tests, docs, changed files, or coverage gaps.
license: Apache-2.0
---

# SpecDD Trace

Use this skill to explain how specs, files, tests, and changes relate. Do not
edit files unless the user explicitly asks for changes.

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

1. Inspect implementation, tests, or diffs needed to connect contracts to behavior.
2. Identify the reason each file or spec is included.
3. When useful and available, consider consulting the `specdd-cli` skill for CLI-assisted spec discovery; treat any output as read context, not authority.
4. Report missing links, stale specs, untested scenarios, or unclear authority.

## Trace Output

For each relevant item, identify:

- Why it was included, such as bootstrap, ancestor spec, nearest local spec, explicit reference, requested file, or
  changed file.
- The active constraints or behaviors it contributes.
- The code, tests, docs, or tasks that satisfy or fail to satisfy it.
- Any missing link, stale spec, untested scenario, or unclear authority.

Do not expand write authority. Referenced files remain read context unless the
active spec chain grants modification authority.
