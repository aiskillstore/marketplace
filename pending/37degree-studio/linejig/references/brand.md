# Brand style

The Brand style draws the figure in quiet grey lines with its hero as a solid part in the user's brand colour.
Set it with `style: 'brand'`, `?style=brand` or `{type: 'style', value: 'brand'}`; the old name `accent` still works.
Everything else (the model, the assembly, the hero, the motion) is the line-art figure from the `linejig` skill,
unchanged.

## Brand colour

The brand style takes one colour, the user's brand colour (`brand: { color: '#hex' }`, `?brand=hex`, or a
`{type:'brand', value}` message from the host). Orange `#f5821f` is only the default. Every tone is derived from it:
top face = the colour itself, unchanged, on both plates. The other tones are HSL steps measured from the approved
orange (`#f5821f`): on a dark plate the side is hue −6, lightness −7 (`#e0560f`), the edge hue +3, lightness +17
(`#ffb36b`), with an additive glow behind the part and never over it. On a light plate a colour reads paler, so the top gets a
little more saturation (+8), the side is darker (lightness −7), strokes on the colour are clearly darker (lightness
−17), and a soft glow (normal blending, about 0.3) sits behind the part. Never light edges on white: they wash it out. The outline tint is the colour at 15% over a dark plate, 8% over white. An optional
second colour (`color2`) sets the outline level. If the colour is too close to the plate, only the edge is pushed;
the user's colour is never altered. No gradient on the hero: a lighter end washed it out.

When a figure is made for a brand, ask for the brand colour (or read it from the brand's tokens) and pass it in;
never guess a brand's colour.


## Brand

From a reference the user supplied (an isometric model selector: a housing with a slot of stacked cards, the front
card glowing orange, input and output tiles on a rail).

- **The base is the line style:** the same camera, rounded solids filled with the ground, fine-line edges and creases,
  on the dark plate. Grey lines are quieter than in the line style: edges in `edge`, most detail in `lo`.
- **The hero is the only colour.** It is a solid object in the accent, not an outline:
  - top face lighter, side faces darker: a flat two-tone shade from the face normal, with no lighting model and no
    gradient across a face;
  - edges in a lighter tint of the accent;
  - a soft glow behind it, an additive blurred halo of about 40 to 60 px at 1440 wide, at low opacity. It is the only
    glow in the drawing. A figure can turn it off or down (`glow: false` or `glow: 0..1`, `?glow=0..1`), for a large
    hero the halo would muddy.
  - In a family hero (keys, cards in a slot, chairs), the member that is active (hovered, pressed, selected) takes the
    accent, and the rest stay grey. The resting accent member, if any, is the one the message is about.
- **Ink parts stay ink.** A part with `fillTone: 'ink'` is near-black with ink edges in both themes (a lighter edge on
  the dark plate), never the brand colour and never the hero, wherever it sits.
- **Two levels of accent.** *Solid* for the active hero, as above. *Outline* for a secondary state (the item
  that is next, in flight or just passed, like the upstream tile in the reference): accent edges plus a very dark
  accent tint on its faces (about 12 to 18% accent over the plate), and no glow. At most one outline part at a time.
- **The plate is near-black, not pure black:** about `#111111`, with grey edges `#7c7c7c` (4.5:1), `mid` `#606060`
  (3:1) and detail (`lo`) `#4a4a4a`: a step under the lineart greys, so the object reads clearly while the orange leads.
- **Default brand colour:** orange. Top `#f5821f`, side `#e0560f`, edge `#ffb36b`, glow `#ff6a00` at 0.35 to 0.5. On a
  light plate: top `#f5821f` with a little more saturation, side and edges darker, and a soft glow
  (normal blending, about 0.3) behind it.
- **Labels are allowed in this style,** and only here: short words or a small icon engraved flat on a part's top
  face (a model name on a card, a file name on a tile). Sans, all on the face plane, so they foreshorten with it.
  Grey (`mid`) on grey parts, white on the hero. A label names what the part is; it never explains or instructs, so
  calls to action still belong to the host page (the action event).
- **Context, optional:** the object may sit in its system. That means a rail or lines running in and out, with
  neighbour tiles at reduced tone that fade to the plate at the edges, so the eye stays on the centre. A **dashed
  footprint** on the ground around the main object marks it as the selected or active one.
- **Context in detail** (the reference's pipeline):
  - The **rail** is a track of two parallel lines on the ground, running diagonally through the plate along one world
    axis, past the main object.
  - **Tiles** on the rail are rounded square blocks with two inset rings on the top (a bevel, then a recessed
    panel). A small line icon sits centred in the panel, with an optional label under it, both on the face plane.
    Inputs sit upstream of the main object and outputs downstream, in reading order.
  - The **main object** stands on a wider, thin **base plate** whose side edges carry short vertical seam ticks. The
    **dashed footprint** sits on the ground just outside the base plate.
  - Optional motion: tiles drift slowly along the rail into the main object and out the other side. The one about to
    enter takes the outline accent.
- **Small honest hardware** reads well here: corner screws with a cross head, a slot, a bezel. Keep them in `lo`.
- **Frame, optional:** thin grid lines at the plate's edges, very faint, like a canvas panel.


## Which part takes the colour

The colour goes on **the part the message is about**. Usually that is the control you act on, not the thing that
responds, when the two are different parts. But when the message is about the contents, the contents take the colour:
the empty inbox's letter glows, not the envelope's flap, even though you open the flap. On the
camera the shutter button is orange and the lens stays in line; pressing the button makes the lens and shutter answer.
Glass, openings and the centre of a coloured part (a lens's glass, a magnifier's glass, a window) stay the plate
colour, so they read as clear. Most objects have one part that is both (a needle, a drawer, a key), and then it is
simply that part. Check every figure for this: rare, but it happens.


## Recolouring live

The host can recolour a figure in Brand or Dots live: `{type: 'brand', value: '#hex'}` (or `{color, color2}`). The
kernel rederives every brand tone and redraws; a figure in line art keeps the colour for later and shows none.

## Lesson

A derived palette that moves the base colour (lifting the top, darkening the side by 14% in OKLCH, a gradient,
light edges and glow on white) made the orange brown on dark and washed out on white. The user's own colour goes on
the top face unchanged; only small measured steps move the other tones. Measure the rendered pixels before showing.

