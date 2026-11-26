# Dots style

The same model as a dot matrix (`style: 'dots'`, `?style=dots`), taking the brand colour the same way as the Brand
style (`brand.md`). The kernel renders the figure offscreen in ink codes
(red: ink, green: the hero's share, blue: the outline's share), reduces each screen cell to one value, and draws one
mark per cell. The grid is in screen space, so cells keep their size when zoomed.

- **Tone is dot size.** Edge lines become rows of the largest dots in the grey ramp (`hi` to `mid`); solids get an even
  halftone, sparse on the top face and denser on the sides, in `lo`, so they still read as 3D. Empty cells stay plate.
- **The hero's dots are the brand colour,** and only the hero's. The accent fade still crossfades between members.
- **Ink parts are ink dots.** A part with `fillTone: 'ink'` is drawn in near-black dots (`--ink`) in both themes,
  grown until they close the grid so it reads solid; on the dark plate its edge dots are a lighter grey. It is never
  the brand colour.
- **No glow.** The cursor swells dots within about 40 px by 1.25 times, eased.
- A cell takes the strongest ink within about a cell of its centre, with a soft falloff, so a line moving across the
  grid grows one dot as it shrinks the next instead of popping.

Settings (`createFigure({ dots })`, `?dots=shape:square,cell:8`, or `{type: 'dots', value}`; all live, no rebuild):

| Option | Range | Default | What it does |
| --- | --- | --- | --- |
| `shape` | circle, square, diamond, line, cross, or a registered name | circle | the mark; line is a short dash along the cell's diagonal; `registerDotShape(name, glsl)` (exported by `linejig-pro.js`; import it from there before the figure mounts) adds one, GLSL that sets the signed distance `d` from `l`, `r`, `ink`, `dsize`, `sw` |
| `cell` | 2 to 16 px | 3.5 | the cell size in CSS px |
| `size` | 0.3 to 1 | 0.78 | the largest mark, as a fraction of the cell |
| `gap` | 0 to 8 px | 0 | extra space between cells, apart from the mark size |
| `contrast` | 0.5 to 2 | 1 | how strongly tone maps to size |
| `threshold` | 0 to 0.5 | 0.05 | below this ink, no mark |
| `angle` | 0 to 45 degrees | 0 | turns the grid |
| `swell`, `radius` | 0 to 2, 0 to 120 px | 1, 40 | the cursor swell (1 is 1.25 times) and its reach |
| `faces` | bool | true | faces as halftone; false leaves only the edges as dots |
| `jitter` | 0 to 0.5 | 0 | a small random offset per mark, for a printed feel |
| `heroOnly` | bool | false | only the hero in dots; the rest stays lineart |
| `tint` | bool | false | every mark in the brand colour: edges in the colour itself (held to 3:1 on the plate), detail and faces the same hue a step lighter on white, a step dimmer on black, never a brown or grey mix |
| `auto` | bool | true | adapt the cell to the object's size on screen (below) |
| `across` | 40 to 300 | 180 | with `auto`, about how many cells span the object |

**Size-adaptive.** With `auto`, the cell is about the object's on-screen width over `across` (180; never under 2 CSS px or 1.5
device px, never over `cell`), eased over 150 ms as it zooms or resizes, so a small plate gets finer cells and full
screen keeps the set look. Below a 500 px object the face halftone thins and the hero's dots get a minimum size, so
edges and the hero's silhouette carry it; glass and openings stay empty.

With the floor grid on (`grid: true`, from the `linejig` skill), the grid becomes faint dots.

