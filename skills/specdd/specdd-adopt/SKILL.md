---
name: specdd-adopt
description: Use when Agent needs to add SpecDD to a project or update SpecDD framework files through the CLI before normal SpecDD work begins.
license: Apache-2.0
---

# SpecDD Adopt

Use this skill to help a repository adopt SpecDD through the `specdd` CLI.
If `.specdd/bootstrap.md` already exists, use this skill only for operator-requested framework bootstrap updates; use `specdd-author` for spec authoring or another task-specific SpecDD skill.

## Workflow

1. Check whether the target repository already has `.specdd/bootstrap.md` or existing `.sdd` contracts.
2. If no bootstrap exists and the operator asked to add SpecDD, use the `specdd-cli` skill and the `specdd` CLI to initialize bootstrap files.
3. If bootstrap files exist and the operator asked to update SpecDD framework files, use the `specdd-cli` skill and the `specdd` CLI to update them.
4. If the CLI is unavailable, report that setup or update is blocked until the CLI is available.
5. After CLI initialization, and after CLI update only when framework files changed, read the active bootstrap chain before proposing or creating local `.sdd` specs.
6. If the target is already a SpecDD project and the operator did not ask for framework updates, switch to `specdd-author` or the relevant task-specific skill.
7. Inspect only the repo shape needed for initial boundaries: top-level directories, docs, manifests, tests, and major entry points.
8. Propose the smallest useful initial shape, usually a root project spec before narrower child specs.
9. Create `.sdd` files only when the user explicitly requested or approved that adoption scope.

## Adoption Rules

- Use the CLI to add or update SpecDD framework bootstrap files when the operator asks for setup or framework updates.
- Do not manually install, update, edit, or copy SpecDD framework bootstrap files outside the CLI.
- Do not change implementation files unless the user explicitly asks for implementation work too.
- Use path-based ownership, explicit `References`, and `Can modify` or `Owns` to make proposed authority discoverable.
- Include only sections that add useful local authority, constraints, behavior, tasks, or context.
- Do not present guessed behavior as an active contract; label assumptions or ask for confirmation.
- Keep proposed or created specs short, local, behavioral, and constraint-oriented.

## Reporting

Report whether the repository was already bootstrapped, CLI setup or update status, the adoption scope, specs proposed or created, and any setup left to the user.
