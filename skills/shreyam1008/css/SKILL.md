---
name: css
description: "Implements or debugs CSS layout, responsive sizing, cascade, selectors, and styling performance. Use for concrete stylesheet work; visual-system design and UX reviews belong to web-design-guidelines."
---

# CSS

Modern CSS removed the need for most hacks and heavy frameworks. Lean on the platform: layout engines, custom properties, layers, and container queries.

## Layout: pick the right engine

- **Flexbox** for one-dimensional layout (a row or column, distribution along one axis).
- **Grid** for two-dimensional layout (rows *and* columns), and for overlapping/area-based layouts.
- Avoid absolute positioning for layout; reserve it for overlays/badges.
- Use `gap` for spacing between items instead of margins on children.
- Fix overflow at its cause instead of hiding it with `overflow: hidden`. Check intrinsic minimum sizes, flexible tracks, and wrapping; use `display: block` on canvas/images when their inline baseline gap is unwanted. Preserve intentional clipping for visual effects.
- Prefer **logical properties** (`margin-inline`, `padding-block`, `inset`) so layouts adapt to writing direction.

```css
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); gap: 1rem; }
```

## Responsive without breakpoint soup

- **Container queries** (`container-type: inline-size` + `@container`) let components respond to *their* space, not the viewport — prefer these for reusable components.
- Intrinsic sizing: `min()`, `max()`, `clamp()` for fluid type/spacing (`font-size: clamp(1rem, 0.5rem + 2vw, 1.5rem)`).
- Choose viewport units by behavior: `svh` for a stable unobscured minimum, `lvh` for the expanded viewport, and `dvh` only when resizing with browser chrome is desirable. Do not blanket-replace `vh`/`vw`; dynamic units can resize during scroll.
- Set `aspect-ratio` on media to reserve space and prevent layout shift (CLS).
- **Subgrid** (`grid-template-columns: subgrid`) aligns nested grid items (card titles/footers) to the parent's tracks.
- Use viewport breakpoints only for page-level layout shifts.

## Tame the cascade

- **Cascade layers** (`@layer reset, base, components, utilities;`) give predictable ordering without specificity wars.
- Keep specificity low and flat: prefer single classes; avoid IDs and deep descendant selectors.
- Use `:where()` for zero-specificity grouping; `:is()` to shorten selectors.
- Nesting is native now — nest shallowly; deep nesting recreates specificity problems.
- Prefer **`@scope`** over `:not()`/deep descendants when proximity should win (e.g. theming): `@scope (.card) to (.content) { … }`.

## Style state with the platform, not JS

- **`:has()`** styles a parent from its children — replaces JS class-toggling: `label:has(:checked)`, `form:has(:invalid)`, `.card:has(img)`. Scope it to a close container (broad `body:has()` triggers more recalc); don't nest `:has()`.
- For critical `:has()` UI, add an `@supports not selector(:has(*))` class-based fallback.
- `:focus-visible` shows focus when browser heuristics indicate it is useful, including text inputs focused by a pointer; it is not strictly keyboard-only. `accent-color` and `scroll-snap` can also replace common JS.
- `text-wrap: balance` for headings, `text-wrap: pretty` for body — used deliberately, never on `*` (cost).

## Design tokens & theming

- Define tokens as custom properties on `:root`; theme by overriding them (e.g. under `[data-theme="dark"]` or `@media (prefers-color-scheme)`).
- Build scales (color, space, radius, type) as variables; never sprinkle raw magic values.
- `color-scheme` + relative color / `color-mix()` for systematic variants.

```css
:root { --space-2: .5rem; --accent: oklch(0.7 0.15 250); }
[data-theme="dark"] { --bg: #111; --fg: #eee; }
```

## Performance

- Prefer **`transform`** and **`opacity`** for motion; they often avoid layout/paint, but compositing is not guaranteed. Verify the Layers/Performance trace, and avoid layout properties in hot animation loops.
- Use `will-change` sparingly and remove it after the animation.
- Pair `content-visibility: auto` with a realistic `contain-intrinsic-size` to reduce scrollbar/CLS jumps. Audit accessibility and forced-render DOM reads before broad use.
- Avoid expensive filters/large box-shadows on many elements; avoid `@import` (blocks loading).
- Respect `@media (prefers-reduced-motion: reduce)`.

## Maintainability

- Co-locate styles with components; keep a single source of truth for tokens.
- With Tailwind/utility CSS: use the configured tokens/theme, extract repeated clusters into components, don't fight the cascade with `!important`.
- Watch selector specificity collisions between class-based and element-based rules (a common source of "padding randomly disappears").

## Reference

- **`GoogleChrome/modern-web-guidance-src`** (the CSS guidance; retrievable via `npx modern-web-guidance@latest`).
- MDN CSS reference; web.dev: "Learn CSS", "Learn Responsive Design".
- Specs: Cascade Layers, Container Queries, Nesting, `@scope`, `:has()`, `color-mix()`/relative color.
- Josh Comeau "CSS for JS"; Kevin Powell (modern CSS patterns).
