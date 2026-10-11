---
name: m3-expressive
description: Use when designing or implementing UI with Material Design 3 or M3 Expressive — Material components, motion springs, shape morphing, emphasized typography, color roles, adaptive layouts. Also for Material You, Jetpack Compose / MDC-Android / Flutter / web Material UI, making a UI feel "expressive", or reviewing a design against M3 guidelines.
---

# Material 3 Expressive

M3 Expressive is an **evolution of Material 3**, not a new version — M3 is not deprecated and this
isn't "M4". It adds features, updated components, and design tactics for emotionally impactful UX.
The Usability guidelines name its design tactics as **containment, size, shape, color, and
typography** — a non-exhaustive list; the blog's seven tactics also cover **motion** and component
flexibility.

Backed by Material's most-researched update since 2014 (46 studies, 18,000+ participants).
The headline finding is that this is a **usability** mechanism, not a decorative one: participants
spotted key UI elements **up to 4× faster** in expressive screens. So every expressive choice must
answer one question — **does this guide attention to what matters on this screen?** If not, it's noise.

## Source contract — read this before writing any spec

M3 has exact published values. Stating a plausible-sounding number instead of the real one is the
main way this work goes wrong, and it is invisible to the reader.

**Every number, token name, and component name you state comes from this skill's references.** Look it
up. `tokens.md` has the numeric bedrock; `components/*.md` has per-component placement and behavior;
`component-tokens.md` has the per-component dp geometry — including the measurements m3.material.io
publishes only inside images, so check there before concluding a value is unavailable.

When a value you need is genuinely not in M3, write it as **two labelled parts**:

> **From M3:** button label uses `label large` (14sp / 20sp / 0.1sp tracking, Medium).
> **My design decision (not in M3):** 12dp gap between the two action buttons.

That split is the deliverable's shape. It costs one clause and it is the difference between a spec
someone can build from and a spec that quietly invents a design system.

M3 publishes **no** stagger values, **no** per-component choreography timings, and **no** reduce-motion
scheme-swap rule. Those are always your design decisions.

## Quick reference

| Decision | Answer |
|---|---|
| Motion scheme | **Expressive** for most products, hero moments, key interactions. **Standard** only for utilitarian products. |
| Spring type | Moves/rotates/resizes/re-corners → **spatial** (bounces). Color/opacity → **effects** (never overshoots). |
| Spring speed | **Default** for most. Fast = small components. Slow = full-screen. |
| Corner radius | 10-step scale: 0 / 4 / 8 / 12 / 16 / **20** / 28 / **32** / **48** / full. Bold = new in Expressive. |
| Nested radii | `inner = outer − padding`. Never reuse the parent's radius. |
| Emphasized type | Swap `md.sys.typescale.X` → `md.sys.typescale.emphasized.X`. Same size, heavier weight. Not on by default. |
| Where emphasized goes | Selection, actions, headlines, editorial. Badges, primary buttons, extended FAB, selected list/menu items. |
| Accent role | **Primary** = most important. **Secondary** = no immediate attention. **Tertiary** = small elements needing special emphasis. |
| Region colors | Body = `surface`. Navigation = `surface container`. Same roles at every breakpoint. |
| Text color | `on surface` (or `on surface variant`). Links = `primary`, underlined. |
| Contrast | 3:1 large text, 4.5:1 small text. Roles guarantee 3:1 pairs. |
| Abstract shapes | Decorative and image elements only. **Never** on text-heavy containers. Use sparingly. |
| Hero moments | **One or two per product.** More is overwhelming. |

## The seven expressive tactics

Each is one axis you can push. Depth and failure modes in `references/expressive-tactics.md`.

1. **Use a variety of shapes** — mix round and square for tension; break the surrounding shape style to
   draw attention. Small shapes make essential actions look unimportant.
2. **Apply rich and nuanced colors** — mix primary/secondary/tertiary on key elements; build hierarchy
   with surface tones. Without contrast, everything blends.
3. **Guide attention with typography** — emphasized styles, heavier weights, larger sizes, spacing.
4. **Contain content for emphasis** — group into containers; give the most important content ample
   space and the brightest surface.
5. **Add fluid and natural motion** — shape morph, surface effects, expressive springs.
6. **Leverage component flexibility** — shift components by context; adapt to foldables and large
   screens via canonical layouts.
7. **Combine tactics for hero moments** — brief, surprising, and rare.

## Where to look

| Need | File |
|---|---|
| Any exact number — type scale, radii, springs, elevation, contrast | `references/tokens.md` |
| Per-component dp — container heights/widths, icon sizes, internal spacing, shape + elevation assignments | `references/component-tokens.md` |
| The tactics in depth, research findings, what shipped | `references/expressive-tactics.md` |
| Motion schemes, spatial vs effects, customization levels | `references/motion.md` |
| 35 shapes, morphing, tension, optical roundness, cut corners | `references/shape.md` |
| Roles, baseline/emphasized, editorial treatments, variable axes | `references/typography.md` |
| Color roles, pairing rules, contrast levels, do/don't | `references/color.md` |
| Baseline scheme, static vs dynamic, harmonization, advanced customization | `references/color-schemes.md` |
| Transition patterns, direction rules, legacy easing + duration tokens | `references/transitions.md` |
| Buttons, toggle, icon, split, segmented, button groups | `references/components/buttons.md` |
| FAB, extended FAB, FAB menu | `references/components/fabs.md` |
| Navigation bar / rail / drawer, tabs | `references/components/navigation.md` |
| App bars, toolbars | `references/components/bars.md` |
| Cards, carousel, lists, dividers, sheets, dialogs | `references/components/containment.md` |
| Checkbox, radio, switch, slider, chips, text fields, search | `references/components/input.md` |
| Badges, progress, loading indicator, snackbar, tooltip, menus, pickers | `references/components/feedback.md` |
| Breakpoints (formerly window size classes), canonical layouts, scaffold, grids, RTL | `references/layout.md` |
| States, gestures, inputs, selection, usability, accessibility | `references/interaction.md` |
| Elevation, spacing, icons, design tokens, customization | `references/foundations.md` |
| Compose / Views / Flutter / web availability, APIs, migration | `references/platforms.md` |
| **2,587 official images** — anatomy, measurements, do/don't, full-UI screens | `references/visuals.md` |

To re-scrape m3.material.io when Material ships an update:
`node scripts/refresh-m3.js pages <dir>` and `… images <dir>`. The site is an Angular SPA — fetching a
guideline URL directly returns an empty shell, so don't try; the script's header explains the real
content path and where the numeric token values come from.

Component references carry the discriminating rule ("use this instead of its sibling when…"), anatomy,
every size variant with dp values, placement and spacing, states, color and type role mapping, and
do/don't rules. **Read the relevant one before speccing a component** — the sibling-choice rules are
the part that is hardest to guess and easiest to get wrong.

## Common mistakes

| Mistake | Correct |
|---|---|
| Bouncy fade or color change | Opacity and color take **effects** springs — damping 1.0, no overshoot, in both schemes. |
| Hand-authored durations for expressive motion | Use spring tokens. Web: convert via the table in `tokens.md`. |
| Same corner radius on a container and its child | `inner = outer − padding`. |
| Large or full corners on information-dense components like cards | They clip content. Use a smaller step. |
| Abstract library shapes on text containers | Decorative and image elements only. |
| Emphasized type used as the whole scale | Baseline and emphasized are **used together**; emphasized marks the exception. |
| `outline` on dividers, or on multi-element components like cards | Use `outline variant`. |
| `outline variant` to define a target's boundary | Use `outline`, or a color with 3:1 against surface. |
| `container` roles on text or icons | Containers are fills only. Use the paired `on *` role. |
| Fixed accent colors where contrast matters | They don't adapt to theme. Use `primary`/`secondary`/`tertiary`. |
| Surface color derived from elevation | M3 surfaces are **tone-based**; the +1…+5 overlay model is gone. |
| Different region colors on tablet vs phone | Region role mappings stay constant across breakpoints. |
| Hero moments on every screen | One or two per product. |
| Promising a feature on the user's platform | Availability is uneven — check `platforms.md`. Compose M3 Expressive APIs are still experimental until Compose 1.5.0; MDC-Android and web are in maintenance mode. |
