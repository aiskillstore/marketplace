# Coherent visual-system decisions

Use for theme creation or repeated visual inconsistencies. Start by finding the
existing tokens and components; a new theme or tooling pipeline is not implied.

## Tokens with a purpose

Use primitive scales for raw values, semantic roles for intent, and component
tokens only where a component needs an independent contract. Repeated values do
not all need three levels of indirection.

```css
:root {
  --color-surface: #fff;
  --color-text: #16181d;
  --color-accent: #5944b5;
  --space-control: .75rem;
}
[data-theme="dark"] {
  --color-surface: #17151d;
  --color-text: #eeeaf5;
}
```

Components should consume the roles that need to vary together. Keep supported
themes mapped to those roles, and verify contrast in their actual combinations.
Do not add dark mode solely because the system can support it.

## Make the choices coherent

- Define background, surface, text, border, accent, and status roles. Preserve
  status meaning independently of brand color, and provide non-color signals.
- Choose typography for the content and brand. Keep families and weights
  purposeful, use comfortable reading measure and line height, and test long
  headings and text zoom before fixing a type scale.
- Reuse a spacing rhythm across related surfaces. Let content needs determine
  exceptions instead of forcing every dimension onto an arbitrary grid.
- Map radius, borders, and elevation to component relationships. An overlay
  needs a different separation cue from a resting card.
- Make motion communicate state or continuity; provide reduced-motion behavior.
  Shared durations/easings help repeated interactions feel consistent.

Keep the source of truth close to the code that consumes it. Extend an existing
CSS-variable, Tailwind, or token-file approach rather than introducing another.
Add a style guide or component showcase only when its maintenance value is part
of the task. Verify a representative screen before propagating changes.

References: [Material Design foundations](https://m3.material.io/foundations),
[Design Tokens Community Group](https://www.designtokens.org/).
