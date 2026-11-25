---
name: whiteboard-animation
description: This skill should be used when the user asks to "make a whiteboard animation", "draw-on explainer", "VideoScribe style", "hand-drawn explainer video", "animate a sketch being drawn", "do a doodle/scribe video", "show a hand drawing the illustration", or "animate handwriting appearing on a whiteboard". Covers SVG stroke draw-on, a marker hand that follows the path tip, staggered reveal, erase/wipe transitions, and narrated export.
version: 0.1.0
---

# Whiteboard Animation

The VideoScribe / Doodly look: a hand draws illustrations and handwriting onto a board, stroke by stroke, while narration explains. Build it from animated SVG paths that draw themselves plus a marker hand that tracks the drawing tip, then sequence elements so the board fills up in narration order.

## When to use

- A "scribe" / doodle explainer where a hand draws art and text onto a whiteboard.
- Animating a sketch or logo being drawn live, line by line.
- Handwriting that writes itself in, synced to a voiceover.
- Turning a static illustration into a guided, stroke-by-stroke reveal.

## Core mechanic: SVG stroke draw-on

A path "draws itself" by animating `stroke-dashoffset` from its full length down to 0 — the dash gap shrinks, exposing the stroke from start to end.

```js
const path = document.querySelector("#stroke");
const len  = path.getTotalLength();
path.style.strokeDasharray  = len;       // one dash as long as the whole path
path.style.strokeDashoffset = len;       // pushed fully out of view = invisible
path.getBoundingClientRect();            // force reflow before transitioning
path.style.transition       = "stroke-dashoffset 1.2s linear";
path.style.strokeDashoffset = "0";       // draws start → end
```

Use `pathLength="1"` on the `<path>` to normalize: then `stroke-dasharray:1; stroke-dashoffset:1` draws any path regardless of real length, and a single eased value (0→1) is the draw progress. `linear` (or a very gentle ease) reads as a steady hand; avoid `ease-in-out` on long strokes — it makes the marker lurch.

## The marker hand follows the tip

The illusion lives or dies on the hand sitting at the exact point being drawn. Sample the path at the current draw progress and place the hand image there each frame; the pen-nib of the hand asset must align to the path point (offset the image so its tip, not its corner, lands on the point).

```js
const hand = document.querySelector("#hand");   // <img>/<g>, tip at its top-left "nib"
const NIB = { x: 6, y: 4 };                      // nib offset inside the hand art
function drawOn(path, hand, dur = 1200) {
  const len = path.getTotalLength(), t0 = performance.now();
  path.style.strokeDasharray = len;
  (function frame(now) {
    const k = Math.min(1, (now - t0) / dur);     // 0→1 progress
    path.style.strokeDashoffset = len * (1 - k); // expose start→tip
    const p = path.getPointAtLength(len * k);    // current tip in SVG coords
    hand.setAttribute("transform", `translate(${p.x - NIB.x} ${p.y - NIB.y})`);
    if (k < 1) requestAnimationFrame(frame);
  })(t0);
}
```

`getPointAtLength(len * k)` is the workhorse: it returns the on-path coordinate at the same progress driving `strokeDashoffset`, so the nib stays glued to the growing stroke. Lift the hand (fade out, jump to the next start) between separate strokes so it doesn't slide across blank board.

## Reveal order — the board fills up

Sequence elements the way a person would draw the scene, in narration order: each illustration and each handwriting block draws in, holds, then the next begins. Stagger strokes within one drawing; hold a beat after each element lands before moving the hand on. One drawing = one beat of the VO. Don't draw two things at once — the eye (and the single hand) can only follow one tip.

| Step | Mechanism |
|---|---|
| Draw a stroke | `stroke-dashoffset` len→0, hand at `getPointAtLength(len*k)` |
| Multi-stroke drawing | stagger strokes; hand hops to each new stroke's start |
| Handwriting | per-letter/word strokes drawn in reading order, hand following |
| Hold | pause hand off-board after element completes (0.4–1.0s) |
| Next element | move/fade hand to next start; begin its draw-on |
| Erase / clear | wipe or reverse-draw to clear the board for the next section |

## Converting art to drawable paths

Draw-on needs **single-stroke, open paths in draw order** — not filled compound shapes.

- Author or trace line art as open strokes (Illustrator/Inkscape: outline, not fill). A filled blob has no "stroke" to animate; convert fills to a centerline stroke or draw an outline path and fill it after the outline completes.
- Order matters: the `<path>` elements should appear in the SVG in the order a hand would draw them — animate them in document order.
- Long continuous lines look most natural; break only where a real pen would lift.
- For solid color regions: draw the outline stroke first, then fade/grow the fill in behind it (`opacity` or a clip-reveal) so it reads as "colored in after."
- Handwriting: use a stroke/handwriting font, convert glyphs to paths, then draw each glyph's path in stroke order. Or fake it: mask the word and sweep a reveal left-to-right with the hand riding the mask edge.

## Marker hand asset

A PNG/SVG of a hand holding a marker, with the nib at a known point. Measure the nib offset once (`NIB` above) and reuse it. Keep one hand asset for the whole piece for consistency. Mirror it (`scaleX(-1)`) only if you need a left hand. Add a faint shadow under the hand for depth; drop it during holds when the hand is "off."

## Erase / wipe transitions

Between sections, clear the board so it doesn't get cluttered:

- **Wipe**: animate a `clip-path` (or a white rectangle) across the filled group to wipe it away, hand optionally "erasing."
- **Reverse draw-on**: run `strokeDashoffset` 0→len to un-draw, hand following backward.
- **Fade + redraw**: cross-fade the old group out and start the next group's draw-on.

Keep one clear grammar (always wipe left-to-right, say) so transitions feel deliberate.

## Pacing to narration

Draw-on duration should track the spoken line, not a fixed timer. Estimate from VO at ~2.3 words/sec; set each drawing's total draw time to roughly the length of the line it illustrates, plus a short hold. A label that the VO names should finish drawing right as the word is spoken. Slow the hand for emphasis lines; speed minor connective strokes. Never let the hand idle on a finished board while narration continues — move it off or start the next element.

## Output checklist

- Every stroke is a single open path in draw order; nothing pops in fully formed.
- The hand nib sits exactly on the draw tip throughout each stroke (no float, no lag).
- Hand lifts cleanly between separate strokes/elements; no sliding across blank board.
- Elements draw in narration order, one at a time; each holds before the next.
- Handwriting draws in reading order; fills appear after their outline.
- Erase/wipe grammar is consistent; the board never over-clutters.
- Draw timing tracks the VO line it illustrates.
- `prefers-reduced-motion`: show the completed board (all strokes at offset 0, hand hidden) without the drawing animation.

## Deliver & verify (standalone HTML)

> **Packaged helper** (`scripts/`): `scripts/seek-shot.sh anim.html 0 1.5 3` freezes the `?t=N` harness and screenshots each moment; `scripts/contact-sheet.sh sheet.png frame-*.png` tiles them for one-glance review. See `scripts/README.md`.

For a self-contained whiteboard scene (draw-on illustration, handwriting, a short scribe beat) the deliverable is **one HTML file that opens directly in a browser** — no build step, no render pipeline. A single file is the right tier for web motion; don't reach for a bundler when one file does the job. (For a full narrated scribe video with baked VO, build it as a Remotion composition and verify via `remotion still` — see explainer-video.)

**Output contract:**
- One `.html` file: SVG inline (paths in draw order, `pathLength="1"` or measured length), the hand asset inline or as a data-URI, and the draw-on driver in one inline `<script>`.
- All drawing on **one master timeline** (GSAP `tl`, or one rAF clock) so the whole sequence has a single playhead you can seek — `strokeDashoffset` AND the hand position both driven by the same progress value.
- Include the seek harness below so any moment can be frozen for screenshots. Freezing at `t` shows exactly how much of the path is drawn — the verification leans on this.

**Seek harness — freeze an exact moment for screenshots.** `?t=N` seeks the master timeline to `N` seconds and pauses, so a screenshot lands on a still, deterministic frame mid-draw.

```html
<script>
  // ... build your master timeline as `tl` (drawOn calls placed on it) ...
  const t = new URLSearchParams(location.search).get("t");
  if (t !== null) { tl.pause(); tl.seek(parseFloat(t)); }  // frozen at t seconds
  // no ?t → plays normally
  window.__ready = true;            // ready signal for headless wait
  console.log("duration", tl.duration());
</script>
```

**Verify loop — render → freeze → screenshot → check:**
1. Open the file at moments across the timeline — start, a frame mid-draw, end:
   `…/scribe.html?t=0`, `?t=<dur/2>`, `?t=<dur>`. Read `tl.duration()` from the console for the end time. Pick at least one `t` in the *middle of a stroke* — that is where the hand-on-tip illusion is proven or broken.
2. Headless-screenshot each frozen frame:
   ```bash
   npx playwright screenshot --wait-for-timeout=500 "file://$PWD/scribe.html?t=1.2" frame-mid.png
   ```
3. **INSPECT** each still — check **fidelity**: at a mid-stroke `t` the hand nib sits exactly on the leading tip of the drawn portion (not ahead, not behind, not floating); the path is drawn only up to the tip; at `?t=<dur>` every stroke completes cleanly with no gaps, no overshoot, no leftover dash. Check **artifacts**: hand sliding across blank board between strokes, nib offset wrong (tip floats off the line), strokes drawing out of order, fills appearing before their outline, clipped/off-canvas drawings, FOUC before fonts load.
4. Iterate: adjust `NIB`, stroke order, durations, and re-screenshot until each frozen frame looks like a hand mid-draw.

**Before you finish:**
1. Opens standalone in a browser — no console errors, no missing CDN/assets.
2. One master timeline; `?t=N` freezes correctly and `strokeDashoffset` + hand position share one progress value.
3. Screenshotted at start / mid-stroke / end — hand nib on the tip throughout, strokes complete cleanly at the end, draw order correct.
4. Hand lifts between strokes; no sliding across blank board.
5. `prefers-reduced-motion` shows the completed board (all strokes drawn, hand hidden) without the drawing animation.

For a narrated, frame-deterministic export, port the same draw-on (drive `strokeDashoffset` and the hand transform from `useCurrentFrame()/fps`) into a Remotion composition and render to MP4/GIF — see the explainer-video skill for the render-stills → encode loop.

## Reference files

- `references/draw-on-recipes.md` — runnable draw-on mechanics: `getTotalLength`/`getPointAtLength` hand-follows-path, GSAP `DrawSVGPlugin` and `MotionPathPlugin` variants, multi-stroke staggering, per-glyph handwriting, fill-after-outline, erase/wipe and reverse-draw transitions, and the Remotion frame-driven port.
- `references/whiteboard-pipeline.md` — turning art into drawable single-stroke SVGs, draw-order authoring, handwriting/stroke fonts, the marker hand asset and nib calibration, pacing draw time to the VO line, and the storyboard-to-board build sequence.
