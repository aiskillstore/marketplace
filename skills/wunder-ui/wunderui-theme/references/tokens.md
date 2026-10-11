# How the theme is derived

Source of truth: `apps/docs/lib/brand-theme.ts` in the WunderUI repository (the Theme Builder at https://wunderui.com/theme-builder). `scripts/theme.mjs` is a line-by-line port; `T make --parity` reproduces the Theme Builder's `theme.css` byte for byte.

## 1. The scale

The brand colour becomes **step 600**, unchanged. Every other step takes, in OKLCH:

- the **lightness** of the same step in WunderUI's indigo scale,
- the **hue** of the brand colour,
- the brand's **chroma**, scaled the way indigo's chroma changes from 600 to that step,

and is pulled back into sRGB by reducing chroma until it fits. Equal OKLCH lightness looks equally light, so a tint background or a dark text step behaves like indigo's for any hue.

| Step | Indigo reference | Used for |
|---|---|---|
| 50 | `#F4F5FF` | tint background (light) |
| 100–500 | `#EEEFFE` … `#777DF5` | dark-mode links, rings and tint text (400/300 first) |
| 600 | `#555CF3` | the brand colour: `--primary`, `--brand-primary`, `--chart-1`, `--sidebar-primary` |
| 700–900 | `#444AC2` … `#222561` | light-mode links and tint text when 600/800 are too light; 900 = tint background (dark) |
| 1000 | `#111231` | last resort for tint text |

Because step 600 is the input and the rest follow indigo's lightness, a very light brand colour (yellow) gives a scale where 500 is darker than 600. That is expected: 600 is the colour, the other steps are tuned for their jobs.

## 2. The token map

| Token | Light | Dark | Moves to, until it passes |
|---|---|---|---|
| `--primary`, `--brand-primary` | 600 | 600 | never — it is the brand colour |
| `--primary-foreground` (+ brand-, sidebar-) | white if ≥ 4.5:1 on 600, else the better of ink `#17181A` and white | same | — |
| `--text-link` | 600 | 400 | light 700 → 800 → 900 (4.5:1 on `#FFFFFF`); dark 300 → 200 → 100 (4.5:1 on page `#17181A` and card `#1C1D20`) |
| `--ring` (+ `--sidebar-ring`) | 600 | 400 | light 700 → 800 (3:1 on white); dark 300 → 200 (3:1 on page) |
| `--tint-indigo` | 50 | 900 | — (background) |
| `--tint-text-indigo` | 800 | 300 | light 900 → 1000 (4.5:1 on step 50); dark 200 → 100 (4.5:1 on step 900) |

`--tint-indigo` / `--tint-text-indigo` keep their names for compatibility: in WunderUI they are the brand tint (badges, selected rows, icon chips), whatever the brand hue.

## 3. Contrast pairs checked

| Pair | Minimum | Modes |
|---|---|---|
| Button text on primary | 4.5:1 | light, dark |
| Link on page | 4.5:1 | light, dark |
| Link on card | 4.5:1 | dark |
| Tint text on tint | 4.5:1 | light, dark |
| Focus ring on page | 3:1 (non-text) | light, dark |
| Accent text on accent (`check`, and `make` with `--accent`) | 4.5:1 | light, dark |

## 4. What the skill adds after the Theme Builder CSS

The Theme Builder CSS comes first, unchanged. A block marked `Added by the wunderui-theme skill` follows when needed:

- **Dark-mode corrections.** The Theme Builder writes light-only overrides (a moved link or tint text) into `:root, .light`. With the usual `<html class="dark">`, `:root` matches the html element too, has the same specificity as the library's `.dark` rule and comes later — so the light value would win in dark mode (for `#059669` the dark link would be `#056F4D` at 2.87:1). The block restates the dark value in `.dark`. `T check` shows the difference on any file.
- **Focus ring.** The Theme Builder checks the ring and reports the step it moved to, but writes it only in one case. The block writes the checked step (`--ring`, `--sidebar-ring`).
- **Accent** (`--accent`): `--brand-secondary`, `--brand-secondary-foreground` (library ink `#25272A` or white, whichever reads better) and `--chart-2`; in dark mode chart 2 is lifted like the library's own chart colours (OKLCH lightness +0.05, chroma ×0.9).
- **Radius** (`--radius`): WunderUI's radius scale is written into the utilities by Tailwind (`@theme inline`), so it changes through an `@theme inline` block (needs the file to be processed by Tailwind) plus `--radius` for the 3xl/4xl steps. Presets in px (sm / md / lg / xl / 2xl):

  | Preset | sm | md | lg | xl | 2xl | `--radius` |
  |---|---|---|---|---|---|---|
  | none | 0 | 0 | 0 | 0 | 0 | 0rem |
  | sm | 2 | 4 | 6 | 8 | 12 | 0.375rem |
  | md (default, nothing written) | 4 | 8 | 12 | 16 | 24 | 0.75rem |
  | lg | 6 | 10 | 16 | 20 | 28 | 1rem |
  | xl | 8 | 12 | 20 | 24 | 32 | 1.25rem |

- **Font** (`--font`): `--font-sans` (headings follow it). The font must be loaded by the project.

## 5. Scoped themes (`--scope .acme`)

CSS variables that reference other variables are resolved where they are declared, so overriding `--brand-600` on a wrapper would not change `--primary` (declared on `:root`). A scoped theme therefore declares the scale **and** every brand token on the wrapper:

- `.acme, .acme .light` — light values (nested `.light` sections included),
- `.dark .acme, .acme.dark, .acme .dark` — dark values.

Radius cannot be scoped (it is compiled into the utilities); the font can.
