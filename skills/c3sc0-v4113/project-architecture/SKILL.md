---
name: project-architecture
description: "Trigger: UI change, layout, component architecture, state flow, theming, server/client boundary, Astro island. Keep Next.js or Astro apps server-first."
license: Apache-2.0
metadata:
  author: purrfold
  version: "1.0"
---

# Project Architecture Guardrails

## Activation Contract

Load this skill before changing UI, layout, component structure, state flow, theming, data display, or the server/client boundary of a Next.js or Astro app.

## Hard Rules

1. Detect the framework from the project before acting; never assume it.
2. Keep rendering server-first. Add client-side code only when the interaction cannot work without it, and keep that surface as small as possible.
3. Read the installed framework's own docs before changing framework APIs or project structure.
4. Follow `DESIGN.md` for visual and UX decisions when it exists.
5. Build from existing shadcn primitives and semantic tokens before writing custom markup or styles; load `shadcn-component-boundaries` when it is installed.
6. Make loading, empty, and error states explicit for every data display.
7. Add tests proportional to risk, using the test tooling the project already has.

## Decision Gates

| Project signal | Framework | Guidance |
| --- | --- | --- |
| `next` in `package.json` dependencies, or a `next.config.*` file | Next.js | [references/next.md](references/next.md) |
| `astro` in `package.json` dependencies, or an `astro.config.*` file | Astro | [references/astro.md](references/astro.md) |
| Both or neither | Unknown | Stop and ask which app the change targets |

## Execution Steps

1. Read `package.json` and list the root config files to detect the framework.
2. Load the matching reference and apply its boundary rules.
3. Search existing components, routes, and styles before creating new ones.
4. Implement the change with the smallest client-side surface that works.
5. Answer the pre-close checklist, then load `project-min-evaluation` when it is installed, or run the project's quality scripts.

Pre-close checklist:

- Did the change add unnecessary client-side surface?
- Does it follow `DESIGN.md`?
- Are loading, empty, and error states explicit?

## Output Contract

Report the detected framework, every server/client boundary added or moved (with its reason), and the checklist answers.

## References

- [references/next.md](references/next.md) — Next.js server/client boundary rules.
- [references/astro.md](references/astro.md) — Astro island boundary rules.
