# Pencil Workflow

Pencil keeps the design source (`.pen` file) next to the code. This path is less mature than Figma MCP — treat it as the secondary route and document assumptions liberally.

## When this path applies

- The design lives in a `.pen` file checked into the repository or workspace.
- The user is editing both code and design in the same project.
- No Figma source is available, or Pencil is the project's chosen source of truth.

## Workflow

1. Locate the `.pen` file in the workspace. Confirm its scope (one screen vs. multiple).
2. Inspect the design before coding:
   - Read the layer tree.
   - List Pencil variables (colors, spacing, typography). These are the candidate tokens.
   - List reusable components and instances. These are the candidate primitives.
3. Reconcile Pencil variables with project tokens (`tailwind-tokens.md`). Map each Pencil variable to an existing semantic token or flag it for design review. Do not silently create new tokens.
4. Decompose the design into FSD layers before generating code (`fsd-mapping.md`).
5. Generate code from the structured plan, not directly from a screenshot of the design.
6. Refactor the result into the target file layout. Pencil-generated code often produces a single component; split it.
7. Commit the `.pen` file alongside the code change when the design is part of the source of truth.

## Generation rules

- Pencil variables → Tailwind tokens via `@theme`. Never paste the raw color value from a variable into a component.
- Pencil components → reuse the project's existing primitives where the role matches. Wrap only when the project primitive needs domain-specific behavior.
- Layout primitives in Pencil → Flexbox/Grid utilities. Translate stack direction, gap, and padding into utility classes, not absolute positioning.
- Local assets in `.pen` → exported into the repository's asset directory and referenced from there.

## Responsive intent

Pencil designs are typically a single breakpoint. Confirm with the user which breakpoints the design must support, and stub responsive behavior with documented assumptions when the design does not specify.

## Best practices

- Treat the `.pen` file as editable source, not a screenshot.
- Keep design and code commits together when they describe the same change.
- Prefer one `.pen` per screen or per feature rather than a single mega-file.

## Anti-patterns

- Translating a `.pen` file into one monolithic component with no FSD decomposition.
- Pasting raw color/spacing values from Pencil into Tailwind classes instead of mapping to tokens.
- Treating the `.pen` file as throwaway and not committing it.
- Reinventing primitives that the project's component library already ships.

## Status

This path is experimental compared to Figma MCP. If both sources exist for the same screen, prefer Figma MCP unless the user explicitly requests Pencil.
