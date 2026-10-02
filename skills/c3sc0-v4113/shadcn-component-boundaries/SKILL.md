---
name: shadcn-component-boundaries
description: "Trigger: components/ui, shadcn, component placement, common components, feature components, atomic design. Enforce registry and product component boundaries."
license: Apache-2.0
metadata:
  author: purrfold
  version: "1.0"
---

# shadcn Component Boundaries

## Activation Contract

Load this skill when creating, moving, wrapping, or reviewing UI components in a project that uses shadcn.

## Hard Rules

1. Resolve paths from `components.json` (its `aliases` for `components` and `ui`) or the installed shadcn skill's project-context command. Never assume `components/` versus `src/components/`.
2. Reserve the resolved `ui` directory for registry-managed primitives installed from shadcn or compatible registries.
3. Never place product-owned wrappers, composites, sections, domain components, or feature behavior in the `ui` directory.
4. Put reusable product-owned components under `common/` in the resolved components directory.
5. Put feature-owned components in a named feature folder or colocate them with that feature.
6. Compose: wrap a registry primitive from `common/` or a feature folder instead of adding product behavior to the primitive.
7. Keep dependencies one-way: feature → common → ui. The `ui` directory never imports from `common` or feature folders.
8. Use semantic tokens from the global stylesheet. Treat tokens as quarks and registry primitives as atoms; do not force molecule or organism names into paths.
9. When `@shadcn/lint` is configured, `shadcn/no-restyle` enforces the `ui` boundary: call sites may pass layout classes through `className`, but look comes from variants and sizes. Add a variant to the primitive instead of restyling at the call site.

## Decision Gates

| Component ownership | Destination |
| --- | --- |
| shadcn or compatible registry primitive | resolved `ui` directory |
| reusable product-owned component | `<components>/common/` |
| feature-specific component | `<components>/<feature>/` or feature colocation |
| route or page composition | framework route/page directory |
| theme token | global stylesheet variables |

## Execution Steps

1. Read `components.json` and resolve the `components` and `ui` aliases to directories.
2. Search installed primitives before creating custom markup.
3. Classify ownership and reuse scope with the table above.
4. Place the component; see [references/placement-examples.md](references/placement-examples.md) for edge cases.
5. Verify no product-owned file entered `ui` and no reverse import was introduced.

## Output Contract

State the ownership classification and final path for every component created or moved, and confirm the dependency direction holds.

## References

- [references/placement-examples.md](references/placement-examples.md) — worked placement decisions.
