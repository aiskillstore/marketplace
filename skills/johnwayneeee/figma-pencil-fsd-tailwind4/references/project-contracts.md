# Project Contracts

Local repository rules win over anything in this skill. This file describes how to detect and respect them. It is intentionally generic — no specific path, framework, or toolchain is required.

## When to use

- On every run, before generating code.
- Whenever the repository has its own architecture guide, design-system documentation, or linting rules that may differ from the defaults in this skill.

## What to check first

All items below are optional. Use what the repository actually provides; skip what it does not.

1. Architecture documents. Look for any file at the repository root or in a docs directory that describes architecture, contribution rules, or agent instructions (common names include `ARCHITECTURE.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `AGENTS.md`, or files under `docs/`). Read them before generating code.
2. Source folder structure. The names of FSD layers may differ from the canonical ones. Examples of possible variations:
   - A different name for `pages` (such as a page-view module).
   - A different name for `app-shell` (such as a layout slice inside `widgets`).
   - A different folder layout inside `entities` or `features`.
   Use the local names exactly. Do not normalize them to the skill's defaults.
3. Component library presence. Check for any installed or in-house primitive library (shadcn/ui, Radix, Mantine, Headless UI, a local design-system package, or similar). Reuse the existing primitives. Do not duplicate `Button`, `Input`, `Dialog`, and friends.
4. Token system location. Find where the project declares its design tokens (a global stylesheet, a design-system package, a theme file). Add tokens there, never inline in components.
5. Linting and import rules. Check for any configuration that encodes allowed import direction (ESLint, Biome, Steiger, dependency-cruiser, or equivalent). The project's rules win.
6. Module path aliases. Use whatever aliases the project defines in its TypeScript or bundler configuration; do not invent new ones.
7. Framework and version. Identify the host framework and adapt: the Server/Client split in `rsc-boundaries.md` and `fsd-mapping.md` applies only when the framework has that distinction.
8. Tailwind version. If the project uses Tailwind v3, fall back to v3 config and ignore the v4-only sections of `tailwind-tokens.md`. If the project does not use Tailwind at all, the token rules still apply conceptually — adapt them to the project's styling system.

## Rules

- Local naming for layers, slices, and folders overrides this skill's defaults.
- Local token names override the semantic baseline. If the project uses `bg-canvas` instead of `bg-background`, use `bg-canvas`.
- Local lint rules override generic FSD direction. If the project allows a non-canonical import, do not "fix" it.
- Local primitive libraries are the source of truth for `Button`, `Input`, and similar primitives. Reuse, do not re-implement.
- Local deployment and build constraints (RSC boundaries, edge runtime, static export, bundling targets) override generic recommendations.

## When the project has no contract

If none of the documents above exist:

- Apply the defaults from this skill.
- Leave a short note in the PR or commit describing the assumptions you applied (layer names, token names, framework split). Future contributors will need it.

## Goal

The skill stays generic enough to apply anywhere, but never overrides what the host repository has already decided.
