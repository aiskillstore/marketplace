---
name: specdd-explain
description: Use when Agent needs to explain a SpecDD spec, target, behavior, or effective spec chain without editing it.
license: Apache-2.0
---

# SpecDD Explain

Use this skill to explain SpecDD contracts to a human. Keep the explanation
succinct and clear while including enough depth to understand the feature,
module, workflow, or file governed by the spec.

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

1. Identify the requested spec, target path, feature, behavior, or changed file.
2. Ensure the active bootstrap chain and applicable spec chain are known.
3. When useful and available, consider consulting the `specdd-cli` skill for CLI-assisted spec discovery; explain from exact specs when exact contract text matters, not from CLI summaries alone.
4. Read or reread explicit `References` only when they materially affect the explanation.
5. Explain what the contract means in plain language, not line by line.
6. Separate direct spec requirements from reasonable inference, missing context, and underspecified behavior.

## Explanation Rules

- Explain the purpose, scope, ownership, allowed changes, important behavior, boundaries, dependencies, scenarios,
  examples, tasks, and completion criteria that matter to the request.
- Preserve `Must`, `Must not`, `Forbids`, `Depends on`, public contracts, and write authority instead of softening them.
- Keep framework mechanics brief unless the user asks how SpecDD resolution works.
- Do not invent behavior, guarantees, workflows, or user stories beyond the active specs.
- Do not edit files unless the user explicitly asks for a spec or implementation change.
- If the user asks about one spec only, avoid expanding into sibling specs unless the active spec references them or
  they are needed to avoid a misleading explanation.

## Output

Prefer short sections such as:

- What this is
- Scope
- Behavior
- Boundaries
- Open or unclear points

Use prose or compact bullets. Quote sparingly. When something is inferred rather
than specified, label it as an inference.
