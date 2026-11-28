# Readout style

The same model as a printed instrument (`style: 'readout'`, `?style=readout`), taking the brand colour the same way as
the Brand style (`brand.md`). It lives in its own add-on file, `kernel/styles/readout.js` (MIT, like the engine), which
the kernel imports once, the first time a figure asks for Readout. The walls carry a material printed in wall space:
binary digits on one side, the same data as cells on the other, so the object reads as code and machinery.

- **One quiet line on every outline,** one width, on Linejig's plate (`--plate`) with a faint static grain. Tops stay
  empty.
- **The walls are printed, by the way they face.** Walls turned to the left carry rows of `0` and `1` in mono; walls
  turned to the right carry the shadow side (`shade`). Both use one cell grid in wall space: u along the wall's top
  edge, v down from it. They foreshorten with the wall and stay fixed to it as the view turns. The digits are one size
  across the figure.
- **A band, not a fill.** Up to three rows hang from each wall's top edge. The first is crisp, at about the edges'
  strength, and the next fade; the rest of the wall is plate. Small walls get no texture, and walls too narrow for digits get cells.
- **Grey only; the colour is the hero's.** The hero is flat brand colour (top, side a step dimmer, no edge lines) with a
  soft bloom of its own shape behind it and a small engraved X on its largest top.
- **A dashed footprint** under every figure that doesn't draw its own: the base in its own frame (a circle for a round
  base, a rounded rect for a boxy one), grown by one margin, with parts that stick out left off.
- The digits scroll slowly along the wall (8 CSS px a second); they stand still under reduced motion and `?freeze`.
  Nothing reacts to the pointer, and the texture never rebuilds a frame.

Settings (`createFigure({ readout })`, `?readout=band:2,shade:rules`, `?shade=bits|rules|dots`, or
`{type: 'readout', value}`; all live, no rebuild):

| Option | Range | Default | What it does |
| --- | --- | --- | --- |
| `shade` | bits, rules, dots | bits | the shadow side: the digits' data as filled cells, fine lines along the wall, or one dot per cell |
| `row` | 0.006 to 0.03 | 0.016 | the row pitch as a share of the plate's width (one size for the figure) |
| `rowMin`, `rowMax` | 4 to 12, 8 to 20 px | 7, 15 | the row pitch held in this range of CSS px |
| `band` | 1 to 8 | 3 | rows of texture under each wall's top edge |
| `bandFade` | 0.2 to 1 | 0.72 | each row's strength relative to the row above |
| `minCells` | 0 to 200 | 14 | a wall side under this many cells gets no texture |
| `narrow` | 0 to 8 | 3 | a digit wall under this many cells wide shows cells instead |
| `density` | 0 to 1 | 0.8 | the share of cells kept on a big wall (a fixed per-cell dropout) |
| `denseFrom`, `denseTo` | 0 to 2000, 10 to 5000 | 80, 600 | wall sizes in cells where the thinning starts and is full |
| `digitA`, `shadeA` | 0 to 1 | 1, 1 | the digits' and the shadow side's strength |
| `bitSize`, `dotSize` | 0.2 to 0.9, 0.1 to 0.8 | 0.72, 0.34 | a cell's square and a dot's diameter, as a share of the cell width |
| `rulesPerRow` | 1 to 6 | 3 | rules: lines per row |
| `scroll` | 0 to 40 px/s | 8 | how fast the digits move along the wall |
| `grain` | 0 to 0.2 | 0.05 | the plate's grain (0.7 of it on white) |
| `foot`, `footRadius` | 0 to 0.4, 0 to 0.5 | 0.09, 0.12 | the footprint's margin and corner radius, as shares of the base's size |
| `dash`, `gap` | 2 to 20 px | 8, 6 | the footprint's dash and gap |

**Ink and glow.** A part with `fillTone: 'ink'` is solid ink, near-black in both themes with a lighter edge on the dark
plate, and carries no wall texture. The hero's bloom follows the figure's glow option (`glow: false` or `0..1`,
`?glow=0..1`).

**Dark-first.** Readout is drawn for the dark plate. On white it holds (darker digits and cells, edges a step lighter),
but it is calmer and the glow is a light tint.

**Export.** PNG and bitmap exports include the walls and grain. The vector exports (`svg`, `vector`) do not: they carry
the lines, fills and glow only.

**Engine.** Readout uses two generic hooks of the kernel: `solid()` puts `o.solid = { F, ring, w0, w1 }` on its
silhouette, and `build()` asks a style extension for its own meshes per primitive (`primMesh(p, z, N, t0)`). A figure
that builds its own prisms (with `o.top`) still gets walls: Readout finds the extrusion from the fill and the cap.
