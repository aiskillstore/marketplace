# Color

26 standard color roles in six groups (primary, secondary, tertiary, error, surface, outline), plus
inverse, scrim, shadow, and add-on roles — 45 color roles in total. Scheme generation, HCT, contrast levels: see `tokens.md`.

## Why roles, not colors

Color roles are "the numbers in a paint-by-number canvas" — the connective tissue between a UI
element and what color goes there. Three consequences:

- Roles are **mapped to Material components**. Custom components must be mapped to the same roles.
- Roles **ensure accessibility** — the system is built on accessible pairings guaranteeing a minimum
  **3:1** contrast.
- Roles are **tokenized**, so contrast levels and dynamic color work automatically.

**Apply colors only in the intended pairs and layering orders.** Improper combinations break contrast
— and they break *visibly* when a user changes the contrast level or dynamic color shifts. A button
using `primary` + `primary container` becomes illegible as the contrast level changes;
`primary` + `on primary` stays legible at every level.

## Naming grammar

| Term | Meaning |
|---|---|
| **Surface** | backgrounds and large, low-emphasis areas |
| **Primary / Secondary / Tertiary** | accent roles that emphasize or de-emphasize foreground elements |
| **Container** | fill color for foreground elements like buttons. **Never for text or icons.** |
| **On** | text/icons sitting *on top of* the paired parent color |
| **Variant** | lower-emphasis alternative to its non-variant pair |

## Choosing an accent group

Assign by importance and needed emphasis.

- **Primary** — most prominent components: FAB, high-emphasis buttons, active states. The most
  important elements.
- **Secondary** — elements that don't need immediate attention or emphasis: filter chips, selected
  state of a navigation icon, dismissive buttons, background of an inactive star.
- **Tertiary** — smaller elements needing *special* emphasis but not immediate attention: badges,
  notifications, input fields. Contrasting accents that balance primary and secondary. Applied at the
  designer's discretion, to support broader color expression.

Use caution when changing roles purely for visual effect.

### The four roles in each accent group

| Role | Use |
|---|---|
| `primary` | high-emphasis fills, text, icons against surface |
| `on primary` | text and icons against primary |
| `primary container` | standout fill against surface, for key components like a FAB |
| `on primary container` | text and icons against primary container |

Same shape for secondary (less prominent fills; container for recessive components like tonal
buttons) and tertiary (complementary fills; container for components like input fields).

## Error

`error` / `on error` / `error container` / `on error container`. Attention-grabbing, indicating
urgency — e.g. an incorrect password in a text field.

**Error is static by default in any dynamic color scheme** (it does not shift with the source color),
but it still adapts to light and dark theme.

## Surface

| Role | Use |
|---|---|
| `surface` | default background color |
| `on surface` | text and icons against any surface or surface container |
| `on surface variant` | lower-emphasis text and icons against any surface or surface container |

Five container levels by emphasis: `surface container lowest` · `low` · **`surface container`
(default)** · `high` · `highest`. The non-default levels are especially useful for **hierarchy and
nested containers on expanded screens**.

Most common combination: **`surface` for the body area, `surface container` for the navigation area.**
Text and icons use `on surface` / `on surface variant` on all surface types.

### Cross-window-size rule

**All color mappings — especially surface — should stay the same for a layout region across window
size classes.** The body area uses `surface` and the navigation area uses `surface container` on both
mobile and tablet. At larger sizes you may add other surface container colors for hierarchy, as long
as they are applied consistently.

### Default component mappings

- `surface container low` — elevated button, card
- `surface container` — top and bottom bars
- `surface container high` — FAB, basic dialog
- `surface container highest` — input label, off switch

Neutral components (navigation bars, menus, dialogs) default to specific surface container roles and
**can be remapped**.

## Inverse

`inverse surface` (background fills contrasting against surface) · `inverse on surface` (text/icons
on it) · `inverse primary` (actionable elements like text buttons on inverse surface).

Canonical use: a **snackbar** — inverse surface background, inverse on surface text, inverse primary
text button.

## Outline

- `outline` — **important boundaries**, e.g. a text field outline.
- `outline variant` — **decorative elements** such as dividers, and cases where other elements
  already provide 4.5:1 contrast.

Rules:

- **Don't use `outline` for dividers** — different contrast requirements. Use `outline variant`.
- **Don't use `outline` for components containing multiple elements**, such as cards. Use `outline variant`.
- **Don't use `outline variant` to create visual hierarchy or define the boundary of a target.** Use
  `outline`, or another color with 3:1 contrast against the surface.
- `outline variant` **is** acceptable on the border of targets like chips and buttons **provided the
  contents inside meet 4.5:1** contrast.

## Add-on roles

> Most products won't need these. If you aren't sure whether your product should use the add-on
> roles, it probably shouldn't.

**Fixed accent colors** — `primary/secondary/tertiary fixed` are fills against surface that **keep
the same tone in light and dark theme** (unlike container roles, which shift tone). `*-fixed-dim`
gives a stronger, deeper tone with the same fixed behavior. Text on them uses `on * fixed`, and
`on * fixed variant` for lower emphasis.

⚠️ **Fixed colors don't respond to theme, so they're likely to cause contrast issues. Avoid them
where contrast is necessary** — use `primary` / `secondary` / `tertiary` there instead.

**Bright and dim surfaces** — `surface dim` (dimmest in both themes) and `surface bright` (brightest
in both themes). Unlike `surface`, which inverts between themes, these **keep their relative
brightness across both themes**. Example: navigation rail on `surface dim`, chat window on
`surface bright`.

## Static vs dynamic

- **Static** — hand-picked or generated (e.g. Material Theme Builder), constant once assigned. The
  **baseline** scheme is the default static scheme and uses a hand-picked source color.
- **Dynamic** — one source color from wallpaper or in-app content generates an accessible scheme that
  updates when the source changes. Gives personalized UI, accessible contrast, user-controlled
  contrast, and automatic dark theme.

Three source options: user wallpaper (quantization), in-app content (album art, logo, video preview),
or hand-picked.

Three algorithms: **user-generated** (maps tones per system design choices + user preferences),
**content-based** (tones adjusted to match the source image while keeping accessible contrast), and
**custom colors** (closely match input colors — brand or semantic).

Migrating M2 → M3: start by mapping the **baseline** scheme onto the existing product, then switch to
dynamic color when ready.

Specific colors — semantic colors in particular — **can be set not to change dynamically.**

## The expressive color tactic

Material's dynamic color system already spans primary, secondary, and tertiary. Expressiveness comes
from **mixing** them:

- Mix accent roles on key components or visual elements to emphasize the main takeaway of a screen.
- Create visual hierarchy with **surface tones**.
- Use contrast between primary, secondary, and tertiary to **prioritize actions and simplify
  navigation**.
- Without contrast, elements blend together. Use contrast to emphasize the main takeaway.

## Contrast levels (May 2025)

Standard (default) · Medium (min 3:1) · High (7:1). Tokenized, applied automatically to both light and
dark theme. Custom components support them for free **if** they use proper role pairs
(e.g. `primary container` + `on primary container`).

Note on high contrast: it is applied to the **content** in a card, not the card container.

## August 2024 update — more colorful text and icons

In **light theme**, these roles became more colorful while keeping accessible contrast:
`on primary container`, `on secondary container`, `on tertiary container`, `on error container`.

Affected components: badges, bottom app bar, buttons, extended FAB, FAB, icon buttons, segmented
buttons, chips, lists, menus, navigation bar, navigation drawer, navigation rail, switches.

## February 2023 — tone-based surfaces

Tone-based surface roles **replaced** surfaces at +1 to +5 elevation. Surface color is no longer tied
to elevation. Alignment changes with Android SysUI: light theme default surface moved tone 99 → 98;
neutral palette chroma 4 → 6; dark theme surface roles slightly darkened.
