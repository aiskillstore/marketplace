---
name: linejig
description: Draws interactive 3D line illustrations in three.js. One object is built from a few rounded solids and drawn in an isometric view (2:1 axonometric) with one fine line width, in line art (white and black, hierarchy by tone) or in the Brand, Dots, Readout and Pencil styles, so all figures keep a consistent illustration style. It builds in (stack or draw-on), then its one hero part (a needle, a lid, the keys of a keyboard) answers hover and click, and the user can drag to turn and zoom it. No captions, leader labels, logos or generated images. Use it whenever someone asks for an interactive 3D illustration, a line-art, isometric, halftone, pencil-sketch or brand-colour object illustration, an animated three.js line drawing, a draw-on or assembly animation, an illustration for an empty state, 404 page, onboarding step, slide or hero, or to add, change, restyle or embed a figure from the Linejig gallery, even if they only say "add a drawing here".
---

# Linejig

<!-- Product name: "Linejig", always one word, capital L. The skill id `linejig` is the front matter `name` and the
     folder name. Site URL: every https://linejig.com link in this folder is the current site; when the main domain
     changes, replace it in every file here. -->

Linejig draws one object per illustration as interactive 3D line art in three.js, on a shared engine that keeps every
figure in the same style. Everything this skill needs is in this folder.

## Habits that hold for every figure

- **Is there one already?** Before drawing, check the gallery manifest (https://linejig.com/illustrations.json; the gallery
  is https://linejig.com/library.html and each figure lives at https://linejig.com/<id>/). Use one only if it shows the thing the page is about, literally.
- **Concept: one object, three options.** Write three concepts, recommend one in a sentence, and wait for the user
  to pick, unless they said "just draw it". After the pick, do not stop again until the drawing is checked.
- **A silhouette you can name at thumbnail size,** with features that change the outline, not only sit inside it.
- **Logical motion.** Everything moves in the real order of cause and effect: parts assemble the way the real
  thing is put together, and the hero does what the real part does.
- **Name what it shows, never whose it is:** no logos, companies, products or people, in the drawing or its words.
- **No long dashes** anywhere in the words.

The drawing rules follow the Hairline figure kernel by Lucas Marques (MIT): https://hairline.lucasmarkes.com and
the npm package `@lucasmarkes/hairline`.

## Before you draw: think first

The user judges the idea before the execution.

1. Say what the drawing sits beside, in one sentence.
2. Write three concepts (`references/metaphors.md`): "Object Z, hero H, because ..., its intro and its one move M."
   If one needs a caption to be understood, drop it. Recommend one and wait for the pick.
3. If the user sent references, explain how each works before you build.

## What stays out

These hold in line art; the styles change only what `## Style` says.

- **No text in the illustration.** No leaders, pointer dots, numbers on parts, captions, headings, labels or "Fig."
  marks. If the host page needs words, they are the page's job, not the drawing's.
- **No small detail.** No rivets, bands, hatching, engraving, textures, shading, gradients or glow.
- **No AI images or video,** and no tracing of generated pictures. Everything is drawn in code.

## The kernel

Every figure is built on the shared kernel, https://linejig.com/kernel/linejig.js (MIT; its header comment is the API;
read it there, or at `site/kernel/linejig.js` when working in the source repo). A figure file
holds only its model, its `ASSEMBLY` table and its `HERO` handlers, about 100 to 150 lines:

```js
import { createFigure } from '../kernel/linejig.js';
createFigure({ id, center, fit: { points }, ASSEMBLY, model(K, st) { ... }, state(K) { ... }, HERO: { onHover, onLeave, onClick } });
```

The kernel owns the camera and fit, the palette and styles, rounded prisms and painter fill, the line width and
0.5 px widths, the tween and spring, both intros, orbit, zoom, hit testing, cursors, reduced motion, capture hooks,
the embed contract, the **action event** (`HERO.action`, posted when the hero's move reaches its open state, so an
empty state or onboarding step can hand off to its host page) and `?mode=turntable` (no hand, a slow swing for
loading screens and recorded loops). Import `https://linejig.com/kernel/linejig.js` and link
`https://linejig.com/kernel/linejig.css`, with the three.js import map, as `scripts/starter.html` does.
Every other style is an MIT add-on file beside it (Brand and Dots in `linejig-pro.js`, Readout in `styles/readout.js`,
Pencil in `styles/pencil.js`): the kernel loads a style's file by itself, once, only when a figure asks for that style,
so a line-art page never downloads it.
To see finished figures, open them from the gallery and read their source.

## Style

A figure draws in **line art** (`references/styles.md`), the kernel's default: white and black only, the grey ramp,
`hi` for the hero, text-free. Four more styles restyle the same drawing with one setting; the model, the assembly and
the hero stay the same, so a figure made in one style works in every style.

1. **Brand** (`references/brand.md`): quiet grey lines, and the hero as a solid part in the user's brand colour
   (orange `#f5821f` by default) with a soft glow behind it. Short labels may sit engraved on part tops; optionally
   the object sits in context on a rail with a dashed footprint.
2. **Dots** (`references/dots.md`): the same drawing as a screen-space dot matrix, tone as dot size, the hero's dots
   in the brand colour, with a cursor swell.
3. **Readout** (`references/readout.md`): quiet lines on a dark grained plate, the walls printed with a band of binary
   digits on one side and the same data as cells on the other, the hero in the brand colour with a soft bloom. Dark-first.
4. **Pencil** (`references/pencil.md`): the drawing by hand in graphite on the plate as paper, pencil strokes with
   pressure and overshoot, tone as hatching in each face's plane, the hero in a brand-coloured pencil; silver on dark.

Switch with `style: 'lineart' | 'brand' | 'dots' | 'readout' | 'pencil'` in `createFigure`, `?style=` on a figure page,
or `{type: 'style', value}` after `ready` (the old names `line` and `accent` still work). Until a style's file arrives
the figure draws line art, and a figure that opens in another style sends `ready` only once it is in. A page may also
import the file itself to have the style at once.

### The brand colour

- Brand, Dots, Readout and Pencil take one colour: `brand: { color: '#hex' }`, `?brand=<hex>` (no `#`), or
  `{type: 'brand', value: '#hex'}` live. The kernel derives every other tone from it; pass it as it is.
- **Ask for it, never guess.** On a component library (shadcn/ui or any token theme) the primary token (`--primary`)
  is the likely source, but only once the user confirms it is their brand colour. Convert the computed colour to
  hex for both themes.
- The colour goes on the part the message is about (`references/brand.md`, "Which part takes the colour").

### What changes from line art

- **Colour:** white, black, the grey ramp and the one brand colour on the hero. No other colours.
- **Glow:** only the soft halo behind the hero, in Brand and Readout. None in Dots or Pencil.
- **Text:** only in Brand, and only short words engraved flat on a part's top face to name that part. Never in
  Dots, never a caption, a leader or a call to action. Readout's digits are a wall texture, not words.
- **Hatching:** only in Pencil, as its tone.

### Check the styles

On top of `references/verify.md`: capture every style (`?style=lineart`, `?style=brand`, `?style=dots`,
`?style=readout` and `?style=pencil`), and in Brand at least one colour besides orange (`?brand=2f6bff`), on both
plates. On white the hero must read clean and bright, not muddy; on black, not brown. Measure the rendered pixels.

## The look, in brief

Full rules and values in `references/drawing.md`.

- **Few rounded solids.** Build the object from a handful of rounded footprints (rounded rectangles, circles)
  extruded into prisms. Each prism shows its silhouette and one crease ring just inside its top edge. Use enough
  parts (usually 8 to 12) that the object reads as that specific object, and carry secondary detail (ticks, seams,
  rose points) as quiet `lo` lines rather than more weight.
- **One camera.** Orthographic 2:1 axonometric: azimuth 45°, sin(elevation) 0.5. The object is centred and fills
  about 60 to 75% of a 5:4 plate.
- **Filled with the ground.** Every face is filled with the plate colour and drawn back to front, so near parts
  hide far ones.
- **One line width.** About 1 px on screen for every line, at any size (three.js `LineMaterial`,
  `worldUnits: false`). When the drawing is dense, use one line in place of two; a second line, if truly needed, is
  about 0.5 px in `lo`.
- **White and black.** A near-white plate in light, a near-black plate in dark, and a grey ramp. No colour.
- **Hierarchy by tone only.** Five tones: `plate` (ground and fills), `edge` (silhouettes), `mid` (default lines),
  `lo` (dim and background lines) and `hi`, the one bright highlight on the one part that matters. Plus dashed
  guides and dots. The drawing sets no other colour.

## The hero part

Every illustration has **one hero part**, or one family of identical parts that each work the same way (the keys
of a keyboard): the part that carries the message (a compass's needle, a safe's lid, a
key, a balance's beam). Decide it while thinking, before you build, and write it down with the object: "Object Z,
hero H, because ...". The hero is the `hi` part, it makes the one move, and it is the only part that answers the
user. Everything else stays simple and still, and only moves as the whole object when the user turns or zooms it.

## Interaction, in brief

Full rules in `references/interaction.md`. After the intro lands:

- **Turn:** drag orbits the camera within limits, then springs back to the rest view after about 2 s.
- **Zoom:** wheel or pinch, toward the pointer, 0.8× to 2.5×; double-click resets. Lines stay 1 px.
- **Hero:** hovering makes the hero respond the way the real part would (the needle turns toward the pointer like a
  magnet and springs back on leave); a click gives it a kick. The cursor is the only hint: no text, no UI.

## Motion, in brief

Full rules in `references/motion.md`.

- **three.js 0.160.0**, Line2 / LineSegments2 fat lines, pinned, with an import map (the kernel does the rest).
- **The intro is the user's choice, `stack` by default:** `draw` (lines draw on) or `stack` (the object builds from the ground up, one
  layer at a time), with more ideas in `references/motion.md`. One `INTRO` setting, overridable with `?intro=`.
- **One move that means something,** and it lands once: the intro plays, then the object does the thing it is
  for (a needle settles, a lid lifts, a key turns, a telescope swings) or the camera pushes in or pans.
- **Timing.** A 700 ms tween on `cubic-bezier(.32,.72,0,1)` for discrete moves; a spring (k 100, c 18, m 1) for
  things that should overshoot a little and settle, like a needle. Draw-on about 1200 ms, left to right.
- **End on the drawing.** Hold still or idle very slowly (a degree or two over a minute).
- **Reduced motion** (`prefers-reduced-motion` or `?reduced=1`): show the final state at once.
- **Capture hooks:** `?freeze=MS` stops the clock MS after the start; `?click=ID@MS` clicks the hero at MS.

## Workflow

1. Think (above): message, object, hero part, its one move and its hover response. For the `stack` intro, also
   write the object's assembly table (type, base, each part's mounting face and `from` direction; see
   `references/motion.md`, "Planning the stack").
2. Build on the kernel from `scripts/starter.html`: replace the placeholder model, `ASSEMBLY` and `HERO`
   with yours (mark the hero's row `hero: true`), assign tones, set the move. Never copy kernel code into a figure.
3. Render frozen frames at the start, middle and end of the move, in both palettes, at desktop and phone width
   (`references/verify.md`). Look hard; fix and rerender.
4. Check the console for errors. Ship with pinned library versions.
5. **Lock it into the gallery** (only when working in the source repo) once the user approves it (they say it's
   locked, final or approved). Build it in
   `site/<id>/index.html` in the source repo, then add one entry to the gallery manifest
   `site/illustrations.json` (`id`, `name`, `path`, `category`, `message`, `hero`, `hover`, `click`, `intros`,
   `locked`, `date`, and `action: {id, label}` if the hero hands off) and nothing else; the gallery at
   `site/library.html` groups entries by `category` (the manifest's `categories` list). To show the user a figure
   before approval, add it with `locked: false`: the gallery shows it tagged draft (`?drafts=0` hides drafts). Once
   approved, set `locked: true`, push, and redeploy the site's Vercel project. The kernel keeps the embed contract, so the
   gallery can drive every figure.

## Using it with what you already have

Most figures go into a product that already has a look. Full notes in `references/integration.md`.

- **On a component library** (shadcn/ui, or any token-based theme): the surface token the figure sits on becomes the
  plate (`?plate=<light>,<dark>`), the ink stays the kernel's grey ramp, the frame sits in a card at 5:4, and a class-based
  dark mode is passed on with `?theme=` and the `theme` message.
- **From the user's own illustration or SVG:** read it for the object and its parts, rebuild each shape as a kernel
  footprint (the kernel has no SVG import, so nothing is traced automatically), drop small detail and every word,
  choose the hero part, and give it hover and click like any other figure.

## The source repo

The gallery, the kernel source and the figure pages live in the Linejig source repo (`site/kernel/linejig.js`,
`site/<id>/`, `site/illustrations.json`). Steps marked "only when working in the source repo" apply only there;
everywhere else, import the published kernel from https://linejig.com/kernel/.

## Lessons (do not repeat these)

- **Shallow ideas get rejected** however well drawn. Think first.
- **Detail is not quality.** Early drawings carried rivets, bands and three line weights; the simpler
  line art reads better small and animates cleaner.
- **No AI generation** for the drawings or their motion; the user rejected it.
- **Stop what is not on screen.** A drawing left running showed over other slides (a balance figure on a deck). When an
  illustration leaves, hide it and stop its loop.

## References

- `references/metaphors.md`: choosing an object for a message, with an example set.
- `references/drawing.md`: camera, rounded prisms, painter fill, the one width, the five tones, palettes.
- `references/motion.md`: moves, timings, springs, draw-on, reduced motion, hand-overs.
- `references/styles.md`: line art, which part is the hero, the floor grid and the shadow.
- `references/brand.md`: the brand colour and its derived tones, the Brand style, which part takes the colour,
  recolouring live, and the lesson on muddy colour.
- `references/dots.md`, `references/readout.md`, `references/pencil.md`: each style and every setting.
- `references/interaction.md`: the hero part, hover and click responses, orbit, zoom, hit testing, cursors.
- `references/verify.md`: headless Chrome capture, frozen frames, console errors.
- `references/integration.md`: on top of a component library (tokens, cards, dark mode), and from the user's own
  illustration or SVG.
- https://linejig.com/kernel/linejig.js: the kernel; its header is the API.
- https://linejig.com/illustrations.json: the gallery manifest; each entry's `path` is a figure page to read.
- `scripts/starter.html`: a minimal figure on the kernel with a placeholder object. Open it, or capture with
  `?freeze=MS`.
