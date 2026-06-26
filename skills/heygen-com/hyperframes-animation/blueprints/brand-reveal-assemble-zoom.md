---
id: brand-reveal-assemble-zoom
role: brand-reveal
duration_seconds: [4, 6]
phases: 5
visual_arc: wide-composition → companion-exit → tight-focus → idle
uses_rules: [discrete-text-sequence, coordinate-target-zoom, sine-wave-loop]
element_roles:
  companion: Supporting element (tagline, slogan, intro text) that provides context then exits
  hero: Focal element (logo, icon, product image) that remains and receives camera focus
when_to_use:
  - Brand / logo / product reveal needs context-then-focus flow
  - Wide-shot → close-up cinematic narrowing
  - Two elements share screen, one dominates the final frame
when_not_to_use:
  - All elements remain throughout (no exit phase)
  - Scene is purely text-based, no visual hero
  - Multiple elements need equal focus
  - Interactive elements required — see cta-morph-press
triggers: [brand reveal, zoom into logo, text leads to, wide to close-up, hero focus]
---

# Brand Reveal · Assemble & Zoom (HyperFrames)

This is a "context → focus → idle" emotional arc: the viewer first watches the companion text type itself out and understands what they're looking at; then the hero (logo / icon) pops in to declare where the focus lies; companion yields its space, the layout's center of gravity collapses toward the hero, and the camera pushes in for a close-up; finally the hero settles into a subtle breathing motion, saying "this is the brand, it lives here."

The whole thing runs on a single paused GSAP timeline. Five phases, no hard cuts — every adjacent pair gets a 0.06–0.3s breath of buffer to absorb the previous phase's spring tail.

## When to Use

- Need a progressive narrowing from wide composition to tight close-up on a hero
- A supporting element (slogan, category word, tagline) appears first to give context, then exits
- Final frame is a close-up of the hero with subtle ambient motion
- Not for: all elements equally important, pure text scenes, or scenes requiring interaction (use cta-morph-press)

## Orchestration

This scene weaves four kinds of motion together; each maps to a rule or an inline pattern:

- **Phase 1 — companion typing**: use [discrete-text-sequence](../rules/discrete-text-sequence.md), but in its **monotonic simplified form** (a string of `tl.set` calls, not the reverse-search `onUpdate`). Brand-reveal companions usually don't have the dramatic stuff — no typos, no backspaces — they're just "one phrase that builds out quickly." The full SEQUENCE array machinery from the rule is overkill. Still, drop at least one pacing hold in the middle so the cadence doesn't read as machine-typed.
- **Phase 2 — hero pop**: no rule needed, just inline a single `back.out(BOUNCE_FACTOR)` tween that springs the hero from `scale: 0` to `scale: 1`. One tween, no orchestration — making this a rule would be overengineering. For a rubberier feel, swap to `elastic.out(amp, period)`.
- **Phase 3 — companion exit + layout recenter**: the "glue" unique to this blueprint, not covered by any rule. Three concurrent tweens at the same timeline position, sharing `duration` and `ease` (companion fade-slides, `.recenter-shift` pulls brand-group toward the viewport center). See "Phase 3 seam" below.
- **Phase 4 — zoom into hero**: use [coordinate-target-zoom](../rules/coordinate-target-zoom.md), **but its default offset derivation doesn't fit here.** The rule's formula assumes a row of N equal-width cards; our layout is the three-piece "companion + brand text + hero icon" assembly, which needs its own offset derivation. See "Phase 4 seam" below.
- **Phase 5 — hero breathing**: use [sine-wave-loop](../rules/sine-wave-loop.md) in its **multiplicative `onUpdate` form** (the one in the rule's GSAP Timeline section), **not** `fromTo` + yoyo. Phase 2 already set hero's scale to `1.0` and Phase 4 pushed an outer wrapper to `TARGET_SCALE` — the breath must multiply onto hero's existing scale, never overwrite it. See "Phase 5 seam" below.

## Phase Timing

All boundaries are in seconds. Design pass: pick each phase's internal duration first, then back-derive its start time from the constraints below.

| Phase | Start ≥                           | Internal duration      | Notes                                                      |
| ----- | --------------------------------- | ---------------------- | ---------------------------------------------------------- |
| 1     | `0` (or end of previous scene)    | `TEXT_END - 0`         | Monotonic sequence. End must precede `POP_START`           |
| 2     | `TEXT_END + ~0.06s`               | `POP_DUR`              | Tiny gap so companion settles before pop fires             |
| 3     | `POP_START + POP_DUR + ~0.2s`     | `SLIDE_DUR`            | Let `back.out` spring tail settle                          |
| 4     | `SLIDE_START + SLIDE_DUR + ~0.3s` | `ZOOM_DUR`             | Let recenter visually land before zooming                  |
| 5     | `ZOOM_START + ZOOM_DUR + ~0.1s`   | `TOTAL - BREATH_START` | Zoom spring tail must finish; otherwise sine fights spring |

The 0.06s gap between Phase 1 and 2 exists so "typing done → next beat" reads as two events, not one. The 0.2s gap between Phase 2 and 3 is the most critical: `back.out` overshoots past 1.0 and rebounds — pull the layout while that tail is still settling and the hero appears to jitter. The 0.1s gap between Phase 4 and 5 is the same idea: `power2.out` decays to near-zero velocity but never literally zero, and a sine wave starting on top of that produces visible chatter.

## Initial DOM Nesting (Critical)

Phase 3 and Phase 4 each need their own wrapper to carry their transform, for the reason stated directly in [coordinate-target-zoom's "Transform order" principle](../rules/coordinate-target-zoom.md#key-principles): scale must wrap translate, never the other way around — otherwise the translation gets multiplied by the outer scale and the hero "drifts and accelerates." This blueprint adds one extra layer (`.recenter-shift`) beyond what the rule shows, because Phase 3's recenter shift and Phase 4's counter-translate are two different motions and cannot share an element.

```
.zoom-scale        ← Phase 4 scale
  .zoom-translate  ← Phase 4 counter-translate
    .recenter-shift ← Phase 3 layout recenter
      .layout-row
        .companion         ← fixed width, right-aligned, lighter font-weight
          .companion-text  ← Phase 1 typing target
        .brand-group
          .brand-text      ← heavier font-weight; fades + slides out during Phase 4
          .hero            ← Phase 2 pop target + Phase 5 breath target
```

`.companion` is a fixed-width container with `justify-content: flex-end` and `white-space: nowrap`. The reason maps directly to [discrete-text-sequence's "fixed-width container" principle](../rules/discrete-text-sequence.md#key-principles): as characters appear, content length grows; without a fixed width, brand-group gets shoved around as the companion's edge moves. With a fixed width, overflow gets pushed off the container's left edge (not into the brand). The design-time obligation is therefore `COMPANION_WIDTH ≥ widthOf(longest SEQUENCE state)` — otherwise text leaks past the viewport.

Brand text uses a heavier `font-weight` than the companion. Even while companion is still on screen, the hero side must read as dominant — otherwise the Phase 3 "weight transfer" feels abrupt rather than inevitable.

## Phase 3 Seam: Companion Exit + Recenter

This step has no existing rule — it's the blueprint's core glue. Three tweens fire at the same timeline position, sharing `SLIDE_DUR` and `power3.out`:

1. `.companion` fade-slides out (`opacity → 0, x → COMPANION_EXIT_X`)
2. `.recenter-shift` pulls left by `FINAL_RECENTER_OFFSET`, bringing brand-group to the horizontal midline
3. (Optional) brand text picks up a slight "dragged toward center" lateral slide

**`FINAL_RECENTER_OFFSET` is the most common point of failure in this blueprint.** Theoretical baseline: shift left by half the (companion + gap) width:

```
FINAL_RECENTER_OFFSET ≈ -(COMPANION_WIDTH + COMPANION_GAP) / 2
```

But in practice you'll always find the hero ending up slightly off-center to the left. Reason: brand text's visual center of mass isn't its geometric midpoint (bold weights, serifs, letter-spacing all bias the perceived center). Tuned values are usually smaller in magnitude than the theoretical baseline. **Tune by eye, then bake the result as a `const` — never recompute per frame.** The Phase 4 zoom multiplies everything by 5×+, so any sub-pixel drift in this value becomes visible jitter.

## Phase 4 Seam: Zoom into Hero (offset derivation)

The default offset derivation in [coordinate-target-zoom](../rules/coordinate-target-zoom.md) assumes "N equal-width cards in a horizontal row" — that formula doesn't apply here. Our layout is `companion + gap + brandText + heroGap + hero`, with the hero not at center. The hero's distance from viewport center after Phase 3 has to be derived separately:

```
baseHeroOffset = (COMPANION_WIDTH + COMPANION_GAP + brandTextWidth + HERO_GAP) / 2
HERO_FINAL_OFFSET_X = baseHeroOffset + FINAL_RECENTER_OFFSET
counterTranslateX  = -HERO_FINAL_OFFSET_X     // feeds .zoom-translate's x tween
```

**`baseHeroOffset` does NOT include `HERO_SIZE`** — the `S` in "total flex width" cancels against the `S/2` in "icon center to row center distance":

```
Total flex width  T = C + G + B + L + S
Icon center         = C + G + B + L + S/2
Layout center       = T / 2
Offset = (C + G + B + L + S/2) − T/2
       = C/2 + G/2 + B/2 + L/2
       = (C + G + B + L) / 2
```

Including `S` would make the counter-translation overshoot, leaving the icon center-left after zoom.

**`brandTextWidth` must be measured with a hidden DOM probe after `document.fonts.ready`, then baked.** Before fonts load, `getBoundingClientRect()` uses fallback metrics — easily off by 10–30 px, which becomes tens of visible pixels after a 5× zoom. The standard DOM probe (placed before timeline registration):

```js
await document.fonts.ready;
const probe = document.createElement("span");
probe.style.cssText =
  "position:absolute; left:-99999px; white-space:pre; " +
  `font: ${BRAND_WEIGHT} ${BRAND_FONT_SIZE}px ${BRAND_FONT_STACK};`;
probe.textContent = BRAND_TEXT;
document.body.appendChild(probe);
const brandTextWidth = probe.getBoundingClientRect().width;
probe.remove();
// Use brandTextWidth to compute HERO_FINAL_OFFSET_X, bake as const
```

The zoom itself (outer scale + inner counter-translate tweens) follows [coordinate-target-zoom's critical constraints](../rules/coordinate-target-zoom.md#critical-constraints) verbatim: shared `ZOOM_DUR` + ease, no recomputing offset in onUpdate, `transform-origin: 50% 50%`.

During the zoom, brand text fades + slides out (duration `ZOOM_DUR * 0.3–0.5`, finishing well before the zoom climax) — otherwise at 5× scale it fills the frame and covers the hero.

## Phase 5 Seam: Why Breath Must Be Multiplicative

The multiplicative `onUpdate` form in [sine-wave-loop](../rules/sine-wave-loop.md) (`gsap.set(hero, { scale: HERO_FINAL_SCALE * (1 + sin(ω) * AMP) })`) isn't a recommendation here — it's a **hard requirement**:

- Phase 2 tweens hero's scale to `1.0` (or `HERO_FINAL_SCALE`) — this is hero's resting state
- Phase 4 pushes `.zoom-scale` (outer wrapper) to `TARGET_SCALE` — but this is on the wrapper, **not** on hero itself
- Phase 5 must let hero breathe **on top of its own resting scale** — so it has to multiply onto `HERO_FINAL_SCALE` as a baseline

Using the rule's alternative `fromTo` + yoyo form here would re-tween hero from 0 to 1, undoing Phase 2's final state (even if "0 to 1" looks identical on paper, GSAP's from-state gets re-applied on every yoyo cycle, killing the post-pop scale).

`SCALE_AMP` 0.02–0.04 (product photography → small; stylized logo → large), `ROTATE_AMP` 0–2°, `SCALE_PERIOD` ~1.5–2s reads as natural breathing — ranges live in the rule, pick by scene.

## Key Values to Choose (Not Already in the Rules)

Only listing the parameters **unique to this blueprint** below; standard parameters (`POP_DUR`, `BOUNCE_FACTOR`, `SCALE_AMP`, etc.) — go to the referenced rule.

- **COMPANION_WIDTH**: theoretical floor = width of the longest SEQUENCE state in companion font (measure with a probe); 30–50% of viewport width is the practical range. Too small → text leaks past viewport; too large → `FINAL_RECENTER_OFFSET` grows with it and Phase 3 drags.
- **FINAL_RECENTER_OFFSET**: theoretical `-(COMPANION_WIDTH + COMPANION_GAP) / 2`, but tuned value is typically smaller in magnitude. **Must be tuned by eye and baked as a const**, never per-frame (see Phase 3 seam).
- **TARGET_SCALE**: 3× (modest) → 5.5× (cinematic) → 8× (extreme close-up). Constraint: hero source resolution ≥ `HERO_SIZE × TARGET_SCALE`, otherwise rasters go soft.
- **BRAND_EXIT_X**: magnitude ≥ half viewport width — ensures brand text clears the frame before zoom climax.
- **BRAND_FADE_RATIO**: 0.3–0.5; brand text disappears before zoom's halfway mark, leaving the climax framed on hero alone.

## Critical Constraints (ordered by failure frequency)

- **Bake all pre-calculated offset constants**: `FINAL_RECENTER_OFFSET`, `HERO_FINAL_OFFSET_X`, `HERO_FINAL_OFFSET_Y` are all `const`. Per-frame recomputation → sub-pixel drift → visible jitter at 5× zoom.
- **Scale wraps translate** (see DOM nesting): `.zoom-scale` outer, `.zoom-translate` inner. Reversed → translation gets multiplied by scale → hero drifts during zoom.
- **Companion container width ≥ max text width**: overflow during assembly is invisible, but explodes at the final state.
- **`baseHeroOffset` excludes heroSize**: see Phase 4 seam derivation.
- **Breath must be multiplicative**: see Phase 5 seam.
- **Breath gate: BREATH_START ≥ zoom end + 0.1s**: sine and spring tail cannot coexist.
- **Measure brand text after `document.fonts.ready`**: otherwise hero offset is off by 10–30 px.
- **Three nested wrappers only tween GSAP transform aliases** (`x` / `y` / `scale` / `rotation`) — never `width` / `height` / `left` / `top`.
- **Single paused timeline**: `gsap.timeline({ paused: true })`, registered to `window.__timelines[data-composition-id]`.

## Spring → Ease Selection

Four phases, four spring feels, four ease choices. The complete spring → ease mapping table lives in [hyperframes-animation/SKILL.md](../SKILL.md); this blueprint's defaults are:

- Phase 2 elastic pop → `back.out(BOUNCE_FACTOR)` (swap to `elastic.out` for rubberier feel)
- Phase 3 tight exit → `power3.out`
- Phase 4 cinematic push → `power2.out`
- Phase 5 continuous oscillation → `onUpdate Math.sin`

## Golden Sample

- [brand-reveal-assemble-zoom.html](../examples/brand-reveal-assemble-zoom.html) — runnable 5-second composition with concrete values for every named constant above; single paused GSAP timeline drives all five phases. Run this first, then change values — much faster than building from scratch.
