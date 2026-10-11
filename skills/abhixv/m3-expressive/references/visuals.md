# Visual reference library

`visuals/` holds **2,587 official images from m3.material.io** — component anatomy diagrams with
lettered or numbered callouts, size/measurement specs, state grids, placement diagrams, do/don't pairs, and
full-UI example screens. Read them when a written spec is ambiguous or when you need to see how
something is actually composed.

## How to find an image

Every image is indexed in **`visuals/INDEX.tsv`** — one row per image:

```
<relative path>\t<official caption>
```

The caption is Material's own caption or alt text, so **grep the index by what you want to see**, not
by filename:

```
grep -i "container"      visuals/INDEX.tsv        # anatomy diagrams — captions list part names
grep -i "don't"          visuals/INDEX.tsv        # every documented anti-pattern
grep -i "measurement"    visuals/INDEX.tsv        # dp specs
grep -iE "placement|position|alignment" visuals/INDEX.tsv
grep -i "^components_toolbars/" visuals/INDEX.tsv  # everything for one component
```

Filenames are derived from the caption, so plain globbing also works:
`visuals/components_buttons/*shape*`.

## Folder layout

One folder per M3 page, named after its route with `/` replaced by `_`:

| Folder prefix | Contents |
|---|---|
| `building-with-m3-expressive/` | the M3 Expressive announcement visuals — the seven tactics, before/after pairs |
| `components_*` | 37 component pages — anatomy, sizes, states, placement, do/don't |
| `styles_*` | color, typography, shape, motion, elevation, spacing, icons |
| `foundations_layout_*` | breakpoints (previously window size classes), canonical layouts, scaffold, grids, RTL |
| `foundations_interaction_*` | states, gestures, inputs, selection |
| `foundations_xr_*` | XR design and components |
| `develop_*` | platform pages |

## The highest-value image sets

- **Full-UI reference screens** — `foundations_layout_canonical-examples/` (list-detail, feed,
  supporting pane, etc.) and `foundations_layout_layout-overview/` (80 images: regions, panes,
  per-window-size arrangements). These are the "ready-made UI" references: complete, real screens
  showing correct region colors, navigation choice, and pane structure at each size.
- **Component anatomy** — callout diagrams in each `components_*` folder, lettered (`A.`, `B.`) more
  often than numbered. No caption uses the word "anatomy", so search part names (`container`, `label`).
  The callouts map to the anatomy lists in `components/*.md`.
- **Measurement specs** — search `measurement`, `size`, `padding`, `height` in INDEX.tsv.
- **State grids** — search `enabled` or `hovered`; each shows enabled / disabled / hovered / focused /
  pressed (and dragged / selected where applicable) side by side.
- **Do/don't pairs** — search `don't` and `avoid`. These are the fastest way to check a design against
  the guidelines.
- **Shape library** — `styles_shape/` (the 35 shapes, the corner radius scale, optical roundness).
- **Type scale** — `styles_typography/` (the scale diagram, emphasized vs baseline, variable axes,
  editorial treatments).
- **Color roles** — `styles_color_roles/` and `styles_color_system/` (all 45 swatches, role pairings,
  contrast levels, correct vs incorrect mappings).

## Using them well

- Captions are Material's own words — quote them rather than paraphrasing what you think you see.
- A diagram's numbered callouts are meaningless without the matching anatomy list; read the component
  reference alongside the image.
- These are **PNG/JPG/GIF renders of the guidelines**, not source assets. Don't treat pixel-measured
  values as spec — the numbers in `tokens.md` and `components/*.md` are authoritative.
- Images were captured from m3.material.io in July 2026. If a user's platform version differs, the
  written specs age better than the renders.
