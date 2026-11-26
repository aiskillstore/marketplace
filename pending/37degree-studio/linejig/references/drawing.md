# Drawing rules

These follow the Hairline figure kernel (Lucas Marques, MIT): https://hairline.lucasmarkes.com, published on npm as
`@lucasmarkes/hairline`. Its kernel's index comment lists the primitives, and its figures show how small a figure
is (about 100 lines). Borrow the rules, not the code: this skill draws in three.js.

## 1. Camera and plate

- **Orthographic 2:1 axonometric:** azimuth 45°, `k = sin(elevation) = 0.5`. One camera for the whole drawing, so
  any camera move starts and ends in the same projection.
- World space: x and y on the ground, z up. With this camera the corner with the largest x + y is nearest the viewer.
- **Plate:** 5:4 (Hairline draws in a 400 × 320 viewBox). The object is centred and its box fills about 60 to 75% of
  the plate's width (Hairline's boxes come out 230 to 310 wide, 180 to 245 tall). Fit with the object's most extreme
  pose (the lid fully open, the needle at its widest swing), so it never leaves the plate mid-move.
- The plate scales to its container; on a phone it simply gets smaller. Lines stay 1 px.

## 2. Rounded solids

- Build from **rounded footprints**: a rounded rectangle (corner radius at most half the shorter side) or a circle,
  extruded from z0 to z1 into a prism.
- Each prism draws **two things**: its **silhouette** (the outline of the whole solid as seen) and **one crease
  ring** inset slightly (Hairline: 0.6 to 2.2 world units) from the top edge. The crease gives the top a thickness
  without adding edges. Keep the inset under half the shorter side, or the crease turns inside out.
- **Enough structure to name the object at a glance,** and no more. Usually 8 to 12 solids. Keep the parts that
  make its silhouette specific (a compass's gimbal and yoke, a safe's hinges and handle), not just its generic shape.
  Too few parts reads as a placeholder; the first compass at 3 to 4 solids was "too simple".
- **Secondary detail lives in `lo`:** tick rings, rose points, panel seams and other flat marks lying on a surface are
  single `lo` (or `mid`) lines, so the drawing stays quiet while it reads as real. Drop the finest marks at small
  sizes if they turn to noise.
- No rivets, hatching, engraving, texture, shading, gradient or glow.

In three.js: a prism is an extruded `Shape` (or a `CylinderGeometry` for a circle) with a ground-coloured fill mesh,
plus fat-line loops for the silhouette and crease. A silhouette can be taken from `EdgesGeometry` (crease angle
about 35°) for straight-sided parts, or built from the footprint ring at z0 and z1 plus the two side tangents for
round ones.

## 3. Hidden lines: fill with the ground

Fill every face with the plate colour and draw back to front, so a near part covers a far one exactly. No
hidden-line maths. In three.js, give fills `polygonOffset` (factor 1, units 2) so lines on their edges win the depth
test, or order with `renderOrder` by x + y.

## 4. One line width, and fewer lines when dense

Every line is the same fine line: about 0.9 to 1 px on screen, non-scaling (`LineMaterial`, `worldUnits: false`,
`resolution` set to the canvas size in CSS px times the pixel ratio). Round joins and caps. Never thicken a line to
make it important; change its tone.

**When the drawing gets dense** (many repeated parts, such as keycaps, piano keys, windows on a facade or the slats
of a shutter), use **one line in place of two**:

- Drop the crease ring on repeated parts; the outline of the top face is enough.
- Draw one line per real edge. No parallel lines tracing the same rim three or four times.
- If a second line is truly needed (a plate band, a dish), draw it at the **minimum width, about 0.5 px** on screen,
  in `lo`, so the drawing stays easy to look at.

Check dense areas at 2× zoom: they should read calmly, not as a hatch of parallel lines. (The first keyboard had a
crease on every cap and four lines on the case rim; it read as noise.)

## 5. Tones

| Tone | Use |
|---|---|
| `plate` | the ground, and the fill of every face |
| `edge` | silhouettes |
| `mid` | the default line: creases, inner edges |
| `lo` | dim lines: background parts, flat marks, glass |
| `hi` | the one bright highlight: the part that carries the message (a needle, a key, a door) |
| dashed | a guide or axis, in `lo` |
| dot | a small filled dot, in `hi` or `mid` |
| `ink` | a solid near-black part (`fillTone: 'ink'`): eyes, a pupil, a key's black cap |

One `hi` part per drawing.

**Ink.** `fillTone: 'ink'` (on `K.add(..., { fillTone: 'ink' })`, or as the last argument of
`K.solid(F, rings, w0, w1, silTone, creaseTone, { fillTone: 'ink' })`) fills a part near-black (`--ink`, `#161616`) in
**both** themes, where `hi` flips light on the dark plate. On the dark plate its lines take `--ink-edge`, a thin step
lighter (`#6b6c72`), so it reads against `#111111`; on white they are ink too. Every style honours it on any part: it is
never the hero and never takes the brand colour. Use it for what is black in the real object, sparingly.

**Glow.** A figure may turn its style's hero glow off or down: `glow: false` or `glow: 0..1` in the figure definition,
or `?glow=0..1`. The default (1) is the style's own glow; line art has none. Turn it off where a large hero would be
muddied by it. Contrast must step clearly: `hi` > `edge` > `mid` > `lo` against the plate.

## 6. Palette: white and black, the same for every illustration

Every illustration uses this one palette (the kernel's `linejig.css`). No per-illustration colours: a near-white
plate in light, a near-black plate in dark, a grey ramp, and the `hi` tone at the far end of the ramp. An embed may set its plate to the host's surface
with `?plate=<light>,<dark>` (`integration.md`), and the ramp stays as it is.

| Tone | Light | Dark |
|---|---|---|
| plate | `#f7f7f8` | `#111111` |
| hi | `#17171a` | `#e6eaf0` |
| edge | `#6a6a72` | `#a8aab1` |
| mid | `#8f8f97` | `#797b82` |
| lo | `#b6b6bc` | `#4f5056` |

Contrast against the plate is about hi 16 to 18, edge 5 to 8, mid 3 to 4.5, lo 2 to 2.5. These are steeper than
Hairline's own defaults, which are tuned for small figures in cards and read too faint at large sizes (both the
compass and the camera had to be brightened). The host page around a figure should use the same plate colour, so
the figure sits seamlessly on it.

Switch with `prefers-color-scheme`, or a `data-theme` / `?theme=` override. Grain is not used.
