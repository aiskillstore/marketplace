# Whiteboard Pipeline — Cookbook

From raw idea to a finished scribe: turning art into drawable paths, authoring draw order, handwriting, the marker hand asset, pacing to narration, and the build sequence.

## 1. Convert art to drawable single-stroke SVG

Draw-on animates strokes, not fills. The art must be open paths in the order a hand would draw them.

- **Author as line art**: in Illustrator/Inkscape draw with the pen tool as open strokes. Set fill to none, stroke to a real weight. Each visible line = one `<path>`.
- **Tracing a raster**: auto-trace gives filled compound shapes — the wrong thing. Either redraw the centerlines by hand, or trace, then run a centerline/stroke extraction so each region becomes a single stroke.
- **Filled shapes**: a solid blob has no stroke to animate. Draw its outline as a stroke (draws on), then reveal the fill behind it after the outline completes (see fill-after-outline in draw-on-recipes).
- **One path, one lift**: keep a line continuous where a real pen wouldn't lift; split into separate `<path>` elements only at natural pen lifts.
- **Normalize**: add `pathLength="1"` to every drawable path so a single 0→1 progress drives any length identically.

Quick check that a path is drawable:

```js
const p = document.querySelector("#stroke");
console.log(p.getTotalLength());          // finite, >0 → has a stroke to draw
console.log(getComputedStyle(p).fill);    // should be "none" for a pure stroke
```

## 2. Author the draw order

The hand draws one tip at a time, in document order. Order the SVG so paths appear in the sequence a person would draw them.

- Top-to-bottom, left-to-right within a drawing, the way you'd sketch it.
- Structure before detail: outline first, then interior lines, then shading.
- Group each logical drawing in a `<g data-beat="1">` so the build loop can play beats in order and hold between them.
- Keep handwriting blocks as their own groups, glyphs in reading order inside.

## 3. Handwriting / stroke fonts

- **Stroke fonts**: handwriting fonts (Caveat, Patrick Hand, Shadows Into Light, Architects Daughter) read as marker handwriting. Load via `@font-face`; split AFTER `document.fonts.ready` so line breaks are correct.
- **Glyphs to paths**: convert text to outlines, then to centerline strokes, and draw each glyph's path in writing order for true per-letter draw-on.
- **Fast fake**: keep live `<text>`, clip it with a rectangle, and sweep the clip left-to-right while the hand rides the edge — looks written without per-glyph paths.
- **Cadence**: handwriting draws fast (150–250ms/letter); don't draw letters at illustration speed or it drags.

## 4. The marker hand asset

- A PNG or SVG of a hand holding a marker. The **nib** (pen tip) must be at a known, fixed point in the art.
- **Calibrate the nib once**: drop the hand on a test path, screenshot at a few `t`, and adjust the `NIB` offset (or GSAP `alignOrigin`) until the tip rides exactly on the line. Reuse that offset everywhere.
- **One hand for the whole piece** for consistency. Mirror with `scaleX(-1)` only if a left hand is needed (re-measure the nib after mirroring).
- Add a soft drop shadow under the hand for depth; remove/fade it during holds when the hand is lifted off the board.
- Keep the hand on top of everything (`z`-order / last in the SVG) so it's never drawn over.

## 5. Pace draw time to the VO line

Draw-on duration tracks the spoken line, not a fixed timer (same VO math as the explainer-video skill).

- Baseline VO pace ~2.3 words/sec; set a drawing's total draw time to roughly the duration of the line it illustrates.
- A label the narrator names should finish drawing right as the word is spoken.
- Add a 0.4–1.0s hold after each element lands; move the hand off-board during the hold.
- Slow the hand on emphasis strokes; speed minor connective lines.
- Never let the hand idle on a finished board while narration continues — lift it or start the next beat.

```
seconds_to_draw ≈ line_words / 2.3          // match the narrated line
hold_after      ≈ 0.4–1.0s                  // beat to let it land
```

## 6. Storyboard → board build sequence

```
BEAT 01 | VO: "Every project starts with one idea."
  DRAW : lightbulb outline (1.0s) → fill glow (0.4s)
  HOLD : 0.6s, hand lifts off-board
BEAT 02 | VO: "...that grows into a plan."
  DRAW : arrow from bulb → box (0.5s), handwriting "PLAN" (0.8s)
  HOLD : 0.6s
WIPE   : clear board left→right (0.6s) before the next section
BEAT 03 | ...
```

Build rules:

- One beat = one VO line = one drawing/handwriting element. Split a beat that has two ideas.
- Elements draw in narration order, one at a time — never two tips at once.
- Outline → fill → label, within a beat.
- Consistent erase grammar (always wipe the same direction) between sections; clear before the board over-clutters.
- Reduced-motion: render the completed board (all strokes at offset 0, hand hidden) as a static frame.

## 7. Finish checklist

- [ ] Every drawable path is an open stroke with `fill:none` (or fill revealed after its outline).
- [ ] Paths/groups ordered in true draw order; animated in document order.
- [ ] Nib offset calibrated; hand tip rides the line at every sampled `t`.
- [ ] Hand lifts between strokes/beats; no sliding across blank board.
- [ ] Handwriting uses a stroke font, drawn in reading order, at letter cadence.
- [ ] Each beat's draw time matches its VO line; hold after each.
- [ ] One consistent wipe/erase grammar between sections.
- [ ] Reduced-motion shows the finished board with no drawing animation.

---
Order the strokes the way a hand would, glue the nib to the tip, and the board draws itself. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=explainer-video-skills&utm_content=skill_footer&utm_term=whiteboard-animation)** — the AI motion agent for editable, on-brand motion graphics.
