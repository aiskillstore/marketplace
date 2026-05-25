# Tailwind 4 Tokens

This reference is specific to Tailwind CSS v4. If the project still uses v3, fall back to the project's existing config and skip the v4-only sections.

## What changed in v4

- Configuration is CSS-first. A JS config file is optional and usually empty.
- Tokens are declared in CSS via `@theme { ... }` and become utilities automatically.
- Entry point is a single `@import "tailwindcss";`, not three v3 directives.
- Dark mode is opt-in via `@custom-variant dark (...);`.
- Colors default to OKLCH so cross-channel mixing stays perceptually correct.
- Container queries (`@container`, `@max-*`, `@min-*`) are built in.

If the generated code still uses a JS config with `theme.extend`, three `@tailwind` directives, or `darkMode: 'class'` in JS, it is v3 style and must be rewritten.

## Where tokens live

- One global stylesheet owns all tokens. The exact path depends on the project's conventions (commonly a global stylesheet inside the entry or the design-system layer).
- Tokens are declared inside a single `@theme` block. Avoid splitting the same token group across files.
- Component files never declare tokens; they only consume utilities generated from `@theme`.

```css
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --color-background: oklch(1 0 0);
  --color-foreground: oklch(0.18 0 0);
  --color-surface: oklch(0.98 0 0);
  --color-muted: oklch(0.6 0 0);
  --color-border: oklch(0.92 0 0);
  --color-primary: oklch(0.65 0.2 250);
  --color-primary-foreground: oklch(1 0 0);
  --color-destructive: oklch(0.62 0.22 25);

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
}
```

Anything declared in `@theme` is exposed both as a CSS variable (`var(--color-primary)`) and as a Tailwind utility (`bg-primary`, `text-primary`, `rounded-md`).

## Preferred semantic groups

Use semantic names, not raw color names. The exact list depends on the design system; a common baseline:

- `background`, `foreground`
- `surface`, `surface-foreground`
- `muted`, `muted-foreground`
- `border`, `ring`
- `primary`, `primary-foreground`
- `secondary`, `secondary-foreground`
- `accent`, `accent-foreground`
- `destructive`, `destructive-foreground`
- `success`, `warning`, `info`

Pair every fill token with its `*-foreground` counterpart so contrast is always available without recomputation.

## Rules

- Prefer semantic tokens over raw hex/oklch values in components.
- Each meaning resolves to exactly one token. No `primary-2`, `surface-alt`, `muted-soft` drift.
- Do not add a new token unless the design system explicitly defines it. If a value is one-off, use an arbitrary utility (`bg-[oklch(0.7_0.1_140)]`) and leave a `TODO(design)` comment for the design team to decide whether to promote it.
- Light and dark themes share the same token names. Override values inside the project's chosen dark variant (commonly a `.dark` selector), never invent parallel tokens.

```css
.dark {
  --color-background: oklch(0.18 0 0);
  --color-foreground: oklch(0.98 0 0);
  --color-surface: oklch(0.22 0 0);
}
```

## Inline styles

Inline `style={{ ... }}` is allowed only for values that are not knowable at author time: dynamic position, scroll progress, computed transforms, animated values driven by JS. Static dimensions, colors, spacing, and radii must always go through utilities or arbitrary values, never inline.

## Anti-patterns

- Keeping a v3 JS config with `theme.extend` in a v4 project.
- Declaring color literals inside components instead of consuming tokens.
- Creating a new token per screen instead of reusing the semantic system.
- Using `dark:bg-zinc-900` style overrides on every component instead of a single dark-variant theme override.
- Using inline `style` for static styling that a utility could express.
