# Pencil style

The same model drawn by hand in graphite (`style: 'pencil'`, `?style=pencil`), with the hero in a brand-coloured pencil. The kernel loads `styles/pencil.js` the first time a figure asks for it. The style draws every line itself, as a pencil stroke, through the engine's `primLines` hook, and builds tone from hatching through `primMesh`. Fills stay plate, so near parts still hide far ones.

- **One pencil.** Outlines are 1.3 CSS px and hatching 0.8 px at every size. Pressure varies within a stroke, never between strokes.
- **A hand, not a plotter.**
  - A stroke lands, swells and lifts.
  - It runs past a sharp corner (overshoot), growing with the corner's sharpness, so nothing pops as the view turns.
  - Silhouettes get a faint second pass.
  - Light construction lines run past long straight edges.
  - Keep retrace and overshoot faint: heavy ones read as doubled lines and leaks.
- **Tone is stroke density, never a grey fill.** Faces turned away from the light carry hatching, and darker ones add a cross layer and a soft smudge.
  - The light sits up and to the left of the viewer.
  - A light tone is a few whole lines, added between lines as the tone deepens, never scattered specks.
  - Lit faces stay paper.
- **Ink is heavy pressure.** A part with `fillTone: 'ink'` is the one solid fill: near-black (`--ink`) in both themes, under the paper's tooth, with its own pencil outline (half strength on the dark plate, so it reads as a lighter edge). It is never hatched and never the hero.
- **Texture stays on the part.**
  - On a solid, hatching is in the face's own u and v: diagonal on flat walls, along the axis on round ones.
  - On a plain fill (a lathe body, a sphere), it is printed round a vertical axis through the part, so it turns with the part.
  - Strokes are seeded by the part's identity, never by build order.
- **The plate is the paper.** The graphite breaks on a paper tooth fixed to the page in CSS px, repeating every 256 px. A page that tiles `paperTile({ plate, amt, dark })` (exported by `styles/pencil.js`) as its background gets one continuous sheet behind every figure. The plate colour stays `--plate`.
- **The hero is a coloured pencil:** outline, hatching and a light burnished layer, at the brand's own hue, with an eraser-clean highlight lifted out of its lit faces.
  - It fades in and out with the engine's accent fade (220 ms in, 260 ms out).
  - Its outline is a pressed step darker on white and a step lighter on black, so it never reads brown.
- **Boil** (on by default) redraws each stroke in place 7 times a second, like hand-drawn animation.
  - It eases out while the view turns and comes back once it rests.
  - It never runs under reduced motion, `?freeze` or an export.

**Dark paper.** On the dark plate the pencil is silver on black. A white pencil draws the light, not the shadow, so the hatching moves to the lit faces, and the edges press a little harder to stay as present as on white. The hero is a step lighter, so orange never turns brown on black.

Settings (`createFigure({ pencil })`, `?pencil=hatch:0.5,boil:false`, or `{type: 'pencil', value}`; all live, no rebuild):

| Option | Range | Default | What it does |
| --- | --- | --- | --- |
| `pressure` | 0 to 1 | 0.15 | how much a stroke swells and lifts along its length; 0 is an even line |
| `wobble` | 0 to 3 px | 0 | the hand's drift along a stroke |
| `overshoot` | 0 to 12 px | 4 | how far a stroke runs past a sharp corner; 0 makes corners meet |
| `retrace` | 0 to 1 | 0.3 | the faint second pass on silhouettes |
| `construct` | bool | true | light construction lines past long straight edges |
| `constructLen` | 0 to 60 px | 22 | how far they run past the corner |
| `hatch` | 0 to 2 | 0.7 | hatching density; 0 leaves outlines only |
| `spacing` | 2 to 10 px | 3.1 | hatch line spacing at the plate's fitted size |
| `angle` | 0 to 180 degrees | 134 | the hatching's angle in each face's plane, from the face's horizontal |
| `cross` | 20 to 90 degrees | 58 | the cross layer's turn from the first |
| `grain` | 0 to 1 | 0.65 | how much the graphite breaks on the paper's tooth |
| `paper` | 0 to 1 | 0.5 | the tooth shown on the plate itself |
| `smudge` | 0 to 1 | 0.65 | soft graphite in the deepest shadows |
| `eraser` | 0 to 1 | 0.35 | the eraser-clean highlight on the hero's lit faces (white plate) |
| `heroBase` | 0 to 1 | 0.3 | the hero's light burnished layer under its hatching |
| `boil` | bool | true | redraw in place, hand-animated |
| `boilAmp` | 0 to 2 px | 0.4 | how far a redrawn stroke lands from the last |
| `fps` | 2 to 12 | 7 | boil frames per second |

Exports: the PNG export draws Pencil, with boil held still. The vector and SVG export get the engine's own lines, without hatching.
