# Motion rules

Built in three.js 0.160.0 with Line2 / LineSegments2 fat lines, pinned, with an import map (the line addons import
the bare name `three`). No AI image or video generation for the drawing or its motion.

## Principles

- **Motion means something.** Each move is what the real object does (a needle settles, a lid lifts, a key turns,
  an instrument swings) or what a camera does (push, pull, pan). One idea per move.
- **It lands once.** The illustration builds on entry, makes its move, and holds.
- **Two clocks,** after Hairline:
  - *Tween* for discrete moves: 700 ms on `cubic-bezier(.32,.72,0,1)`. Retarget from where it is, never from the
    start. Stagger related parts by 60 to 200 ms.
  - *Spring* for physical settling: k 100, c 18, integrated per frame. Hairline's m 1 is critically damped
    (overshoot about 0.1°, invisible); use m 2 for a visible overshoot of about 5° on a 60° swing. It overshoots a little and settles,
    which suits needles, balances and swinging parts. Use it only where the real object would overshoot.
- **Camera zoom** interpolates scale logarithmically and the centre linearly.

## Moves

| Move | How | Timing |
|---|---|---|
| Draw-on | each line's visible segment count grows from 0; order segments left to right on screen; dashed lines fade in instead | each line 700 ms on the tween curve, line starts spread 500 ms first to last, so about 1200 ms in all (the kernel's values) |
| Arrival | start at scale 0.96 and settle while fading up | 700 ms tween |
| Part move (lid lifts, key turns) | after draw-on reaches about 70% | 700 ms tween, parts staggered |
| Settle (needle, beam) | spring from an offset (e.g. −60°) to rest | spring; lands in about 1.2 to 1.6 s |
| Idle | a degree or two of drift over a minute | never noticeable as motion |
| Camera push or pan | lerp the view | 1250 to 1400 ms, cubic in-out |

## Intro types (the user chooses)

The intro is selectable, not fixed. Ask the user which one they want, or offer two to compare. In code it is one
setting, `INTRO`, which a `?intro=` URL parameter overrides, so they can be compared side by side. Each one ends on
the same finished drawing, then the hero makes its move.

No dead time: drag, zoom and reset work from the first frame, and from the first frame a hover on the hero or a press
cuts the hero's own move short (a hero that has not arrived yet answers as soon as it is on screen). The figure goes
live at once (`onLive` runs then, once), the parts still in flight keep landing (the stack, or the draw-on, plays to its
end, with `K.stacking` true until it does), and its state eases from the intro's pose into the live one over 400 ms, so
`state()` need not match its intro and live branches. Untouched, the intro plays to `liveAt` as before.

| Intro | What happens | Status |
|---|---|---|
| `draw` | each line draws on, left to right across the screen | built (the compass, the starter) |
| `stack` | the object is assembled in ordered layers, and each part arrives along the axis it mounts on: parts on a top face drop from above, parts on a front face slide in from the front (a camera's windows and lens rings, ring after ring, back to front), parts on a side come from that side (a compass's pivot pins). Each layer carries a `from` vector, the outward normal of the face it attaches to, travels about 15 to 25% of the object's size on the 700 ms tween, already drawn, staggered about 120 to 180 ms; about 1.6 to 2 s in all; no bounce on parts, the spring is for the hero only; nothing passes through anything on its way in | built (the compass, the camera, the starter) |

### Planning the stack for each illustration

The stack is not one generic animation. Work it out for each object from how that kind of object is really put
together, before you write any code, and write the plan down as an assembly table:

| Layer | Parts | Mounts on | `from` |
|---|---|---|---|

1. **Name the object's type** and how such things are assembled. Use real assembly order, not screen order.
2. **Find the base,** the part everything else is fixed to (a body, a foot, a floor, a chassis). It comes first,
   from above or rising from its footprint.
3. **Give every other part its mounting face** on a part that is already there, and its `from` vector, the outward
   normal of that face. A part arrives only after the part it mounts on.
4. **Stack along each axis in order.** Coaxial parts go innermost first (lens mount, then the focus ring, then the
   front ring). Nested parts go outer frame first, then what it holds (a gimbal ring, then the bowl in it).
5. **The hero comes last,** then makes its own move.

Patterns by type:

| Type | Base | Typical order and directions |
|---|---|---|
| Camera or front-facing device (camera, radio, phone) | body | body from above → top plate from above → front windows and panels from the front → the optics ring by ring along their axis, from the front → top controls from above |
| Instrument on a stand (compass, theodolite, telescope, globe) | foot or tripod | foot → uprights from above → pivots sideways along the pivot axis → the ring or cradle from above → the instrument from above → the hero (needle, telescope) |
| Container (safe, chest, box, drawer unit) | carcass | carcass → trays or drawers sliding in from the front → hinges from the side → lid from above → lock or key from the front |
| Building or stepped structure (stepwell, tower, stair) | ground slab | courses bottom to top, each from above; openings and doors from the front |
| Mechanism (balance, clock, gear train, lever) | frame | frame → axles along their own axis → parts threaded onto the axles from the axle's end → the beam, hands or pointer last |
| Vehicle or wheeled thing | chassis | chassis → wheels sideways along the axle → body from above → fittings from their faces |

If an object fits none of these, reason it out from steps 1 to 5. If the plan has a part arriving through
another part, or before what it mounts on, the plan is wrong. Fix the plan, not the timing.

More ideas to try later, each still one plain move:

- `extrude`: every footprint is drawn flat on the ground first, then all the solids rise to their heights together.
- `assemble`: the parts start pulled apart along their own axes (an exploded view) and slide together.
- `blueprint`: dashed construction lines and axes appear first, then the solids form on them, then the guides fade.
- `sweep`: a plane passes across the object and leaves the finished drawing behind it.

Before adding one, check it fits the object (stack suits things built in layers, like a stepwell or a chest of
trays; assemble suits mechanisms) and it doesn't compete with the hero's move.

## Hand-overs (when several illustrations share a page or deck)

- Default: the outgoing drawing fades over about 450 ms while the incoming one arrives.
- Related objects can hand over in one move (a surveyor's theodolite pulls back and slides left while a map grows
  from the point it was sighting).
- Only the outgoing and incoming drawings exist. Hide and stop every other one at once.
- Going backwards, the drawing is simply there in its final state.

## Scrub (scroll stories)

A host can drive a figure's progress instead of its clock: one object that assembles, then opens, as the page
scrolls. `fig.scrub(t, { open, split })` (or embedded `{type: 'scrub', t, split?, open?}`, or `?intro=scrub` to start
at 0) maps t in [0, 1] onto the stack intro, parts arriving in ASSEMBLY order, for 0 to `split` (default 0.75), and
onto the hero's click, from rest to its `opened` state, for `split` to 1. While scrubbing the figure plays no intro
and no motion of its own and takes no hover; `scrub(null)` hands it back and replays. The figure needs nothing new:
a good ASSEMBLY order and an `opened` state are the whole story.

- One step of text per moment; give each step the t it shows when its text reaches the middle of the screen. The
  last step is t = 1, the opened state.
- The host eases t toward the scroll (a fifth of the gap a frame); with reduced motion it sets t directly. The
  figure's own reduced-motion rule does not apply: the reader is moving it.
- Examples: site/stories/espresso.html and suitcase.html, with site/stories/story.js.

## Reduced motion

With `prefers-reduced-motion: reduce` or `?reduced=1`: no moves, no draw-on; the final state appears at once (a
250 ms fade at most).

## Capture hook

`?freeze=MS` stops the clock MS after the start. Under headless Chrome drive frames with `setTimeout` (about every
50 ms) while frozen; virtual time runs timers more reliably than animation frames.
