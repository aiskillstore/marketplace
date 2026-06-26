---
id: metric-video-text-pivot
role: metric
duration_seconds: [5, 8]
phases: 4
visual_arc: video-center → video-slides-aside → text-typing → stat-reveal
uses_rules: [3d-text-depth-layers, sine-wave-loop]
element_roles:
  video: Product demo video that starts centered, then slides to make room for the stat
  typing_text: Character-by-character typed lines, with accent-colored keywords
  stat: Giant metric label rendered with 3D depth layers
  pill: Gradient background pill that scales in behind a closing phrase
when_to_use:
  - Scene transitions from showing a feature to stating its impact
  - Metric needs dramatic typographic treatment, not just a number overlay
  - Video provides context, text provides the "so what" payoff
  - Pivot from visual demonstration to textual impact statement
when_not_to_use:
  - Video should remain the focal point throughout
  - Stat is secondary information (use overlay)
  - Scene is purely typographic with no video
triggers:
  [
    accuracy rate,
    engagement increase,
    show feature then stat,
    video moves aside,
    big number reveal,
    metric emphasis,
  ]
---

# Metric · Video Text Pivot (HyperFrames)

This is a "show → yield → pivot → stamp" emotional arc: the product video lands centered and breathes, claiming the viewer's full attention; then it slides aside _into_ the space the stat fills, so the viewer reads it as a single weight-transfer rather than two events; then both visual citizens clear out and kinetic text types into the vacated center, with accent words carrying the meaning the video used to carry; finally a gradient pill snaps shut around the closing line, sealing the impact statement as one graphic.

Single paused GSAP timeline. Four phases, but the second and third phase each pair an exit with a same-anchor entrance, so the timeline reads as two beats not four.

## When to Use

- Two narrative beats: "see the feature" then "see the impact"
- Stat / metric needs dramatic, frame-filling typographic treatment (not an overlay)
- Video provides context and must remain visible during the stat reveal — it slides, doesn't cut
- Not for: video-as-focal-point throughout, secondary stats, purely typographic scenes

## Orchestration

Four phases, two rules, three inline patterns. The inline patterns dominate because most of the scene is bespoke layout choreography, not motif reuse.

- **Phase 1 — video enters + floats**: inline `power3.out` scale/opacity tween on `.video-pos` for the entry. The float (a small `y` bob) is [sine-wave-loop](../rules/sine-wave-loop.md) in its **multiplicative `onUpdate` form**, written to `.video-float` (the middle wrapper). The rule's `fromTo` + yoyo form would not survive the Phase 2 slide tween — see Phase 1 seam below.
- **Phase 2 — video slide + stat reveal**: video gets an inline `power3.out` `x` + `scale` slide on `.video-pos`. Stat enters with an inline `back.out(STAT_BOUNCE_FACTOR)` on `.stat-pos`. The stat's 3D type uses [3d-text-depth-layers](../rules/3d-text-depth-layers.md) in its **static-depth variation** (layers built at composition setup, no cascade, no depth-grow tween); the cascade default would fight the bounce entry. The stat's breath is again [sine-wave-loop](../rules/sine-wave-loop.md) in its multiplicative onUpdate form, gated to the Phase 2 window only.
- **Phase 3 — pivot (both exit + typing enters)**: three concurrent inline tweens at `PIVOT_AT` — video exit, stat exit, typing-stage fade/scale entry. The character-by-character typing itself is inline: a single proxy tween advances `idx: 0 → totalChars` with `ease: "none"`, and `onUpdate` slices five pre-segmented spans by index. We are deliberately _not_ using `discrete-text-sequence` — that rule models discrete state swaps (typos, corrections), not a clean character stream through segmented spans. See "Rule gap" in the report.
- **Phase 4 — pill stamp**: inline `power3.out` on `.pill-bg` `scaleX: 0 → 1` + `scaleY: PILL_INITIAL_SCALE_Y → 1`. The glow halo (`.pill-glow`) fades on the same anchor with a longer `power2.out` duration so the silhouette resolves before the bloom registers.

## Phase Timing

| Phase | Start ≥                                             | Internal duration                        | Notes                                                                     |
| ----- | --------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------- |
| 1     | `VIDEO_ENTRY_AT` (≥ 0)                              | `VIDEO_ENTRY_DUR`                        | Float starts at t=0 and runs continuously, gated by Phase 2/3 window      |
| 2     | `VIDEO_ENTRY_AT + VIDEO_ENTRY_DUR + ~1.0s`          | `max(VIDEO_SLIDE_DUR, STAT_ENTRY_DUR)`   | The ~1s gap is the "breathing room" — see seam                            |
| 2b    | `SLIDE_AT + STAT_ENTRY_DUR + ~0.1s`                 | until `PIVOT_AT`                         | Stat breath activates here, gated off at `PIVOT_AT`                       |
| 3     | `STAT_BREATH_START + ~0.5s`                         | `EXIT_DUR` + `TYPING_STAGE_DUR` + typing | Pivot starts here; `TYPING_START_AT = PIVOT_AT + TYPING_STAGE_DUR`        |
| 4     | `TYPING_START_AT + (BOUNDS.accent2End / TYPE_RATE)` | `PILL_DUR`                               | Anchored to the character index where line 2 begins — derived, not chosen |

The ~1s gap before Phase 2 (`SLIDE_AT − VIDEO_ENTRY_AT − VIDEO_ENTRY_DUR ≥ 1.0s`) is the most-tuned gap in the blueprint: shorter and the float never registers as "alive," so the slide reads as the video's first action rather than its second; longer and the scene drags. The 0.1s gap between stat entry end and breath start is the standard `back.out` settle buffer (overshoot tail and sine cannot coexist — same constraint as Phase 5 of brand-reveal). The ~0.5s minimum between breath start and `PIVOT_AT` exists to make the breath _visible_ — at least one half-cycle has to land before the exit.

The pill anchor (`PILL_AT`) is not chosen, it's derived from the typing index. The full formula:

```
PILL_AT = TYPING_START_AT + (BOUNDS.accent2End / TYPE_RATE)
        = (PIVOT_AT + TYPING_STAGE_DUR) + (line1Length / TYPE_RATE)
```

so the pill snaps in _at the instant_ line 2's first character types. Anchoring it earlier reads as the pill predicting the phrase; later reads as the pill catching up. Pick `TYPE_RATE` first, then this anchor falls out.

## Initial DOM Nesting (Critical)

Every moving element gets **three nested wrappers**: outer `-pos` carries the GSAP entry/slide/exit tween, middle `-float` (or `-breath`) carries the onUpdate-driven continuous motion, inner `-tilt` carries a static CSS 3D rotation. This is the structural seam unique to the blueprint — without the separation, the float's `y` onUpdate would clobber the slide's `x` tween (and vice versa) every frame.

```
.stage
  .video-pos          ← Phase 1 entry, Phase 2 slide, Phase 3 exit
    .video-float      ← onUpdate: y (sine-wave float, gated by t < PIVOT_AT)
      .video-tilt     ← CSS: rotateY(VIDEO_TILT_Y) rotateX(VIDEO_TILT_X) — static
        .video-content
          <video />
  .stat-pos           ← Phase 2 back.out entry, Phase 3 exit
    .stat-breath      ← onUpdate: scale (sine-wave breath, gated to Phase 2 window)
      .stat-tilt      ← CSS: rotateY(STAT_TILT_Y) rotateX(STAT_TILT_X) — static, opposite-Y sign vs video
        .depth-stack  ← 3d-text-depth-layers (static variation, built once)
  .typing-stage       ← Phase 3 fade+scale entry
    .typing-tilt      ← CSS: rotateY(TYPING_TILT_Y) — static
      .line1 (5 spans: main / accent / suffix / accent2 / cursor1)
      .line2-wrap
        .pill-bg      ← Phase 4 scaleX/scaleY entry
        .pill-glow    ← Phase 4 opacity fade
        .line2-content (line2 span + cursor2)
```

The video-tilt and stat-tilt should use **opposite-sign `rotateY`** values (e.g. video `+14°`, stat `-14°`) — this reads as "two surfaces angled toward camera" rather than "two surfaces in the same plane." Same-sign tilts make the slide look like a flat layer-shuffle.

Accent colors are static CSS — `.seg.accent { color: {accentColor} }`. No per-frame color tween, no glow envelope on accent spans. The pill carries all the chromatic punch.

## Phase 1 Seam: Float Must Be Multiplicative AND Gated

The video's float uses [sine-wave-loop](../rules/sine-wave-loop.md)'s onUpdate form, not its `fromTo` + yoyo form — and not because of stylistic preference. Phase 2 will tween `.video-pos`'s `x` from center to `VIDEO_SLIDE_X`. If the float lived on the same element via `fromTo + yoyo`, GSAP would reapply the float's `from` state every yoyo cycle and snap `.video-pos` back to its un-slid position. Putting the float on the middle wrapper (`.video-float`) and writing its `y` via `onUpdate` keeps `.video-pos`'s `x` slot free for the slide tween.

The float must also be **time-gated** inside the shared scene-ticker onUpdate — it should stop firing once the video exits in Phase 3, otherwise it keeps writing `y` to an off-screen `.video-float` forever and burns CPU. Gate it with `if (t < PIVOT_AT)`. This is one of two gated continuous motions in the scene (the other is the stat breath); together they're why we use a single shared scene-ticker onUpdate rather than three separate tweens.

## Phase 2 Seam: Slide and Stat-Entry Share an Anchor

Both tweens fire at the same `SLIDE_AT` position on the timeline. This is the scene's signature beat: the slide _creates_ the space the stat _fills_, so the eye reads them as one weight transfer. If `SLIDE_AT` for the stat lags the video slide by even 0.1s, the empty space briefly registers as "something is missing" before the stat lands, killing the illusion. Stack them on the exact same anchor.

The stat enters from `(STAT_ENTRY_X, STAT_ENTRY_Y_OFFSET, STAT_ENTRY_SCALE)` with `back.out(STAT_BOUNCE_FACTOR)`. `STAT_ENTRY_Y_OFFSET` (40–80 px below final) exists specifically to give the `back.out` overshoot something to _travel_; without a y offset, the bounce reads as a pure scale-pulse rather than a "thrown into place" stamp. The stat's final position is the _space the video vacated_ — `STAT_ENTRY_X ≈ 0.55–0.65 × viewport width` and `VIDEO_SLIDE_X ≈ 0.25–0.35 × viewport width` are mirror-image anchors around the viewport midline.

## Phase 2 Seam: Static-Depth Variation of 3d-text-depth-layers

The stat uses [3d-text-depth-layers](../rules/3d-text-depth-layers.md) in its **static-depth variation** — all layers built at composition setup time with their final offsets, no per-layer cascade, no `DEPTH_GROW_DUR` tween. Reason: the stat _enters as one object_ via the `back.out` bounce on `.stat-pos`. A per-layer cascade firing during the bounce overshoot produces visible inter-layer jitter as layers fade in at different progress points of the spring. The static variation keeps the stack visually coherent inside the bounce.

The depth-stack lives inside `.stat-tilt`, _not_ `.stat-pos` or `.stat-breath`. Putting it inside `.stat-tilt` means the CSS rotation applies to the entire stack uniformly — if the depth-stack were outside the tilt, each layer's per-layer translate offset would not get rotated, breaking the depth illusion.

## Phase 2 Seam: Stat Breath Gating

The stat breath is [sine-wave-loop](../rules/sine-wave-loop.md)'s multiplicative onUpdate form, written to `.stat-breath` (the middle wrapper). Unlike a typical idle breath that runs until composition end, _this_ breath must be **gated off** at `PIVOT_AT`. After `PIVOT_AT`, Phase 3's exit tween on `.stat-pos` controls the stat — but breath is on `.stat-breath`, which is the inner wrapper, so an ungated breath would keep writing `scale` to the wrapper inside an opacity-faded `.stat-pos`. The visible result: a faint scale-shimmer continues _after_ the stat is gone, only noticeable if you look closely, but it's also a wasted onUpdate forever.

```js
// Inside the shared scene-ticker onUpdate (single tween, ease: "none"):
const t = tl.time();
if (t > STAT_BREATH_START && t < PIVOT_AT) {
  const breath = 1 + Math.sin((t - STAT_BREATH_START) * STAT_BREATH_FREQ) * STAT_BREATH_AMP;
  gsap.set(".stat-breath", { scale: breath });
}
```

`STAT_BREATH_START − SLIDE_AT − STAT_ENTRY_DUR ≥ 0.1s` is the standard back.out settle gap — the breath's sine starts at zero offset (`sin(0) = 0`) so it composes cleanly with `.stat-breath`'s implicit `scale: 1.0`, but only if it isn't fighting the bounce tail.

## Phase 3 Seam: Typing-Stage Entry Must Finish Before Characters

Three things fire at `PIVOT_AT`: video exit, stat exit, typing-stage fade+scale entry. The characters of line 1 do **not** fire at `PIVOT_AT` — they fire at `TYPING_START_AT = PIVOT_AT + TYPING_STAGE_DUR`. The reason: the typing-stage `scale: 0.85–0.95 → 1` is small enough that characters typed during the scale-in would draw mid-zoom and look like they're being letterpress-stamped at a wrong scale. Let the stage land, _then_ type.

The typing itself is inline because no rule covers this exact shape — five pre-existing DOM spans (main / accent / suffix / accent2 / line2), one proxy tween advancing a single `idx` value, an `onUpdate` that slices each span's `textContent` by its segment-relative offset.

```js
// Boundaries derived from SEG.*.length — never hard-code character counts.
const BOUNDS = {
  mainEnd:    SEG.main.length,
  accentEnd:  SEG.main.length + SEG.accent.length,
  suffixEnd:  /* ...etc */,
  accent2End: /* end of line 1 — also when line 2 begins */,
  line2End:   /* total chars */,
};

// One proxy, ease: "none". Each segment gets sliced by clamping (idx − segmentStart) into [0, segmentLength].
```

The single source of truth is `BOUNDS.line2End / TYPE_RATE` for total typing duration. Hard-coding character counts (rather than deriving from `SEG.x.length`) is how this scene most often breaks during copy edits — one extra word in `SEG.accent` and the cursor desyncs.

## Phase 3 Seam: Cursor Blink Switches Spans By Index

Two cursor elements (`cursor1`, `cursor2`) exist because cursor1 sits at the end of line 1 (after accent2) and cursor2 sits inside the pill on line 2. Only one is visible at a time, switched by the current typing index:

```js
const cursorVisible = Math.floor(t * CURSOR_BLINK_HZ * 2) % 2 === 0 ? 1 : 0;
cursor1.style.opacity = i < BOUNDS.accent2End ? cursorVisible : 0;
cursor2.style.opacity = i >= BOUNDS.accent2End && i < BOUNDS.line2End ? cursorVisible : 0;
```

The blink itself is deterministic from `tl.time()` — required by the universal HF determinism rule, not unique to this blueprint. What _is_ unique: the index-based span switching, which means the cursor blink is co-driven by both `t` (for the blink) and `i` (for _which_ cursor blinks). Both must come from the same onUpdate.

## Phase 3 → 4 Seam: Pill Anchor Is Derived

`PILL_AT = TYPING_START_AT + BOUNDS.accent2End / TYPE_RATE`. This is the most important derived constant in the scene — pick `TYPE_RATE` and `SEG.*` contents, and `PILL_AT` falls out. Do **not** tune `PILL_AT` independently as a free parameter; it must track the typing index. If `TYPE_RATE` changes (e.g. dropping from 30 to 20 chars/sec for dramatic effect), `PILL_AT` must be recomputed in the same revision.

`PILL_DUR` should finish _before_ line 2 finishes typing (i.e. `PILL_AT + PILL_DUR < TYPING_START_AT + BOUNDS.line2End / TYPE_RATE`) so the pill frames the phrase as it lands rather than catching up after it has landed.

## Key Values to Choose (Not Already in the Rules)

Only listing values specific to this blueprint; standard rule parameters (`SCALE_AMP`, `Y_AMP_PX`, `LAYER_COUNT`, `OFFSET_X`, `BACK_ALPHA_*` — all in the linked rules) live there.

- **VIDEO_SLIDE_X / STAT_ENTRY_X** — mirror-image around viewport midline. Video slides to `~0.25–0.35 × W`, stat lands at `~0.55–0.65 × W`. Asymmetric placements make one element look "demoted" rather than "yielded to."
- **VIDEO_TILT_Y vs STAT_TILT_Y** — opposite sign. Same sign reads as flat layers, not surfaces.
- **STAT_ENTRY_Y_OFFSET** — 40–80 px below final. Smaller → bounce reads as a scale pulse; larger → reads as gravity-dropped.
- **TYPE_RATE** — 20–40 chars/sec; 30 ≈ "1 char/frame at 30 fps." Once chosen, recompute `PILL_AT` (it derives from this).
- **SEG.\*** — the five-span split of line 1 + line 2. Edit copy here, not in the BOUNDS computation. BOUNDS rebuilds from `SEG.*.length` automatically.
- **PILL_INITIAL_SCALE_Y** — 0.4–0.6 vertical squash. Lower than 0.4 reads as a horizontal line snapping outward (good for "stamp" feel); near 1.0 pre-empts the climax.
- **PILL_GLOW_DUR** — `PILL_DUR + 0.1–0.3s`. The lag is the visual "bloom after silhouette" trick; equalize them and the glow feels like part of the silhouette instead of a halo.

## Critical Constraints (ordered by failure frequency)

- **`PILL_AT` is derived, not chosen** — `PILL_AT = TYPING_START_AT + BOUNDS.accent2End / TYPE_RATE`. Whenever `TYPE_RATE` or `SEG.*` changes, `PILL_AT` must be recomputed in the same edit. The most common edit failure is bumping `TYPE_RATE` without touching `PILL_AT`.
- **Three nested wrappers per moving element** — `-pos` / `-float`-or-`-breath` / `-tilt`. Collapse any two and the float / breath onUpdate clobbers the slide / exit tween every frame. This is the most common structural bug.
- **Stat breath must be gated to `STAT_BREATH_START < t < PIVOT_AT`** — otherwise breath keeps writing `scale` to `.stat-breath` forever, including after the stat opacity-fades out in Phase 3.
- **Video float must be gated to `t < PIVOT_AT`** — same reason as the stat breath.
- **Video slide and stat entry share `SLIDE_AT` exactly** — even a 0.1s offset between them kills the weight-transfer illusion.
- **Static-depth variation of 3d-text-depth-layers, not cascade** — the per-layer cascade fights the `back.out` bounce.
- **`depth-stack` lives inside `.stat-tilt`** — outside, the CSS rotation doesn't apply to back layers' offsets and the depth illusion breaks.
- **BOUNDS derives from `SEG.*.length`** — never hard-code character counts. Copy edits desync the cursor otherwise.
- **Opposite-sign Y tilts on video vs stat** — same-sign reads as a flat layer-shuffle, not two angled surfaces.
- **Typing characters start at `TYPING_START_AT`, not `PIVOT_AT`** — letting them type during the typing-stage scale-in produces wrong-scale glyphs mid-zoom.

## Spring → Ease Selection

Four feels, four ease choices. Full spring → ease table lives in [hyperframes-animation/SKILL.md](../SKILL.md); blueprint defaults:

- Video entry / slide / exit and pill scale → `power3.out` (different durations; same family makes the timeline read coherent)
- Stat entry → `back.out(STAT_BOUNCE_FACTOR)`, 1.4 soft → 2.0 firm → 2.8 cartoony (the stat usually wants firm-to-cartoony)
- Pill glow → `power2.out` (softer than `power3.out` so the bloom lags the silhouette)
- Continuous motions (float, breath, cursor blink) → onUpdate `Math.sin` / floor-mod

## Golden Sample

- [metric-video-text-pivot.html](../examples/metric-video-text-pivot.html) — runnable composition with all placeholders filled in, single paused GSAP timeline, all four phases. Run this first, then change values — much faster than building from scratch.
