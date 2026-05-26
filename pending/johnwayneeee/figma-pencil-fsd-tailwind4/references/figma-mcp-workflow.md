# Figma MCP Workflow

Use Figma MCP to pull design context before generating code. Do not screenshot-translate: extract structure, variables, and components from the source.

## When this path applies

- The design lives in Figma and the project has Figma MCP configured.
- The user has selected a frame, component, or page in Figma.
- Code Connect mappings may or may not exist; both flows are supported.

## What to extract

In this order:

1. Selected node tree (frame, component, instance). Always work from a selection, not the whole file.
2. Local variables (color, number, string, boolean) and variable collections — these are the design tokens.
3. Component definitions and instances. Resolve instances back to the source component.
4. Code Connect mappings, if available. They override any inferred code mapping.
5. Layout primitives: auto layout direction, gap, padding, alignment, sizing rules (hug/fill/fixed).
6. Local assets exposed by MCP (image URLs, SVG payloads). Use them directly; do not invent placeholders.

## Before generating code

- Confirm scope: which frame, which screen, which component. Refuse to "translate the whole file".
- Produce a short plan: tokens to register, primitives to reuse, FSD layer for each block, states to cover.
- Reconcile variables with project tokens. Each Figma variable should map to an existing semantic token (see `tailwind-tokens.md`) or be flagged for design review. Do not silently add new tokens.
- Identify which Figma components correspond to existing primitives in the project's component library. Reuse them.

## Generation rules

- Auto layout → Flexbox utilities (`flex`, `gap-*`, `p-*`). Do not translate auto layout into absolute positioning.
- Constraints (fill/hug/fixed) → width/height utilities (`w-full`, `w-fit`, `w-[Npx]` only when truly fixed).
- Variable references → semantic Tailwind utilities (`bg-surface`, `text-foreground`), never the raw hex/oklch from the variable's current value.
- Text styles → typography utilities tied to tokens (`text-sm font-medium leading-tight`), not raw `font-size` literals.
- Effects (shadow, blur) → token-backed utilities when the design system defines them; arbitrary values only as last resort.
- Local image assets → consume the MCP-provided URL or import path. Never invent placeholder URLs.

## Responsive intent

Figma frames are usually a single breakpoint. Before coding:

- Ask which breakpoints the design covers (mobile / tablet / desktop, or named breakpoints).
- If only one breakpoint is provided, code that breakpoint and stub responsive behavior with documented assumptions (e.g. "stack on `<md`, side-by-side on `md+`"). Do not invent unverified responsive rules.

## What the generated code should reflect

- Layer structure that mirrors the Figma component hierarchy where reasonable.
- Spacing, sizing, and alignment driven by auto layout values.
- Colors, radii, typography sourced from variables → tokens.
- Reuse of project components in place of re-implemented primitives.
- Documented assumptions where the design is ambiguous.

## Anti-patterns

- Translating one Figma frame into a single monolithic component without FSD decomposition.
- Copying raw hex values when a variable was attached to the layer.
- Producing placeholder images when MCP returned the real asset.
- Marking the entire generated tree as a client component because one button is interactive.
- Inventing tokens from one-off Figma layer styles.
