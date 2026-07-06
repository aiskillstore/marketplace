# Astryx fallback — components Quanta doesn't have (`type: "app"` builds ONLY)

Quanta is always first. When the app genuinely needs a complex interactive
component Quanta lacks — date picker, calendar, date-range picker, sortable
data table, multiselect autocomplete/combo-box, color picker, OTP input,
tree/disclosure — use **Astryx** (`@astryxdesign/core`), Meta's open-source
React + StyleX design system, which is preinstalled in the template and themed
to the Higgsfield brand. Websites (`type: "website"`) never use it.

## The rules

1. **Quanta first.** If Quanta ships the component (Button, Modal, Tabs,
   Select, Dropdown, Input, Textarea, Sidebar, Chip, Badge, Loader, Media,
   Grid, …), Astryx is the wrong answer. Astryx covers the gaps only.
2. **Never restyle.** The Higgsfield look comes from the bundled theme
   (`@higgsfield/astryx-theme-higgsfield` — dark-first monochrome surfaces,
   lime `#D1FE17` accent, monochrome primary button, Inter / Inter Display /
   IBM Plex Mono). Do not fork the theme, override its tokens, or add a light
   mode — apps are dark-only, so the theme runs in `mode="dark"`. Layout-only
   positioning on your own wrappers is fine.
3. **License.** Astryx (`@astryxdesign/*`) is MIT and consumed as an npm
   dependency — free to ship in generated apps. The Higgsfield theme package
   is first-party (vendored in the template), not a third-party asset.

## The recipe

Astryx styles via StyleX + a `<Theme>` provider (NOT Tailwind), so it
coexists cleanly with Quanta's Tailwind layer — no CSS-layer wiring needed.
`@astryxdesign/core` and the theme are already installed. Two steps:

1. Wrap the subtree that uses the fallback component in the themed provider,
   pinned to dark (do this once, high in the route/layout — not per component):

```tsx
import { Theme } from "@astryxdesign/core";
import { higgsfieldTheme } from "@higgsfield/astryx-theme-higgsfield";

<Theme theme={higgsfieldTheme} mode="dark">
  {/* Quanta-built screen; Astryx fallback components live inside */}
</Theme>
```

For production/SSR the template ships the pre-built theme CSS, imported once
in `app/src/styles.css` (`@higgsfield/astryx-theme-higgsfield/theme.css`) with
the theme's `/built` export on the provider — the template already wires this;
don't re-derive it.

2. Import the component from `@astryxdesign/core` and use it as-is:

```tsx
import { DatePicker } from "@astryxdesign/core";
```

## Consistency checks when mixing

- Standalone actions stay Quanta `Button` — one button system per screen.
  Astryx buttons only appear as built-in parts of a fallback component (e.g.
  a date picker's confirm), where the theme already styles them.
- The theme's accent is the brand lime via `--color-accent`; Astryx's `Button`
  `variant="primary"` is monochrome (there is no lime button slot — the lime
  CTA is always Quanta `marketingPrimary`). `destructive` is the red confirm.
- Icons inside Astryx slots are still Material Symbols (the app's one icon
  family) — pass your own icon nodes where a slot allows, rather than Astryx's
  defaults.
