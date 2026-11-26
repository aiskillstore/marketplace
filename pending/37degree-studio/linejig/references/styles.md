# Style: line art

Every figure from this skill is drawn in **line art**: white and black only, the grey ramp, `hi` for the hero, no
colour, no glow and no text. It is the kernel's default (`style: 'lineart'`; the old name `line` still works), so a
figure needs no setting for it.

The other styles restyle the same drawing, each in its own reference: Brand (`brand.md`, the hero as a solid part in a
brand colour, with a soft halo and short engraved labels), Dots (`dots.md`, the drawing as a halftone dot matrix),
Readout (`readout.md`, walls printed with binary digits, dark-first) and Pencil (`pencil.md`, drawn by hand in
graphite). `SKILL.md`, "Style", says how to switch and how to take the brand colour. Shadow (below) works in every style.

## Which part is the hero

The hero is **the part the message is about**. Usually that is the control you act on, not the thing that responds,
when the two are different parts. But when the message is about the contents, the contents are the hero: the empty
inbox's letter, not the envelope's flap, even though you open the flap. On the camera the shutter button is the hero
and the lens answers it. Glass, openings and the centre of a part (a lens's glass, a magnifier's glass, a window)
stay the plate colour, so they read as clear. Most objects have one part that is both (a needle, a drawer, a key),
and then it is simply that part. The hero takes `hi`, the brightest tone; everything else steps down the ramp.

## Floor grid

`grid: true` (or `?grid=1`, `{type: 'grid', value: true}`) lays a square grid on the ground (z 0) under the object,
about 2.2 times its footprint, cells about an eighth of it on a 1-2-5 step. Thin `lo` lines fade to nothing by
distance and before the plate's edges, and the grid turns with the object. It fades in over 400 ms before the intro.
Off by default.


## Shadow

`shadow: true` (or `?shadow=1`, `{type: 'shadow', value: true}`) adds a soft cast shadow and contact shadows. It's off
by default, and the add-on (`addons/shadow.js`, beside the engine) loads only when a figure turns it on. One light, fixed
to the world, sits in front of the object, above and a little to the left, so every shadow falls behind it and turns
with the floor when you orbit. Overlaps never darken twice, and shadows fade before the plate's edge. In line art the
shadow is a neutral grey from the tone ramp. Use it where the object sits on something and depth helps; leave it off
for floating or flat objects.

- Every filled part casts. `{cast: false}` on `K.add`, `K.layer` or an `ASSEMBLY` row leaves a part out (wires, glows);
  `cast: true` lets a line-only part, such as a rod, cast.
- The ground (z 0, or `ground: z`) receives. `K.receiver?.(F, ring, w)` declares another surface that takes shadows (a
  sheet of paper, a desk top). Keep the `?.` so the figure still works without the add-on. Thin flat solids on the
  ground receive by themselves, and a part never shadows a surface in its own `ASSEMBLY` row.
- `light: [x, y, z]` sets a figure's own light direction. `fitShadow: true` fits the plate round the shadow too.


## Rules

- One hero (or one family), and the hero is where the eye goes: the brightest tone.
- No colour, no glow, no text, no logos, companies, products or people.
- Reduced motion: the final state at once.
