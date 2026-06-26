---
id: takeover-ticker-displace
role: takeover
duration_seconds: [5, 8]
phases: 4
visual_arc: text-assembly → ticker-cycle → hero-displacement → idle
uses_rules: [vertical-spring-ticker, reactive-displacement, sine-wave-loop]
element_roles:
  text_group: Combined typewriter + ticker that builds textual context, then gets displaced as a unit
  hero: Visual element (logo, icon, product) that enters from off-screen and takes over by pushing text away
when_to_use:
  - Text cycles through multiple options before a hero takes over
  - Hero feels like it has physical "weight" — it pushes content aside
  - Transition from text to visual should be a physical collision, not a fade
when_not_to_use:
  - Text and hero coexist throughout — see brand-reveal-assemble-zoom
  - Camera zoom required (this uses entry translation)
  - Multiple hero elements enter simultaneously
  - Text should exit voluntarily (fade / slide)
triggers:
  [rolling text then logo, push text away, slot machine, text cycles, logo enters forcefully]
---

# Takeover · Ticker Displace (HyperFrames)

This is a "context-build → cycling beat → collision → idle" arc: a typewriter lays down a lead-in phrase, an accent word ticks through a slot-machine of options to suggest "many things this could be," then a hero crashes in from off-screen and physically shoves the text aside — saying "actually, this is what it is." The hero then settles into ambient breathing so the climax doesn't go dead.

One paused GSAP timeline, four phases. The two non-adjacent rules (ticker, displacement) hand off through a shared parent transform; sine-wave-loop closes out as a multiplicative idle.

## When to Use

- Scene has a static lead-in phrase + a cycling accent word, all of which should be physically replaced (not faded) by a hero
- The takeover should read as a collision — the hero arrives with momentum and the text reacts to it
- Final frame is the hero alone with subtle idle motion
- Not for: hero and text coexist throughout (see [brand-reveal-assemble-zoom](brand-reveal-assemble-zoom.md)), camera-zoom narrowing, or multi-hero entries

## Orchestration

This scene chains four motions; each maps to a rule or an inline pattern:

- **Phase 1 — typewriter lead-in**: inline, no rule. The lead-in is one static phrase, so we use the **smooth-slice variation** at the bottom of [discrete-text-sequence](../rules/discrete-text-sequence.md) (continuous `Math.floor(progress)` slice, not the state-array form). The full rule's machinery is overkill for a single phrase with no typos or pauses. See "Phase 1 Seam" for the one-character pop guard.
- **Phase 2 — accent-word ticker**: use [vertical-spring-ticker](../rules/vertical-spring-ticker.md) for the rolling accent word. The rule's default footer-reveal at the tail is NOT used — Phase 3 takes its place. `STEPS` here is the number of _options_ the hero is going to replace; pick 2–3 (more reads as filler).
- **Phase 3 — hero crashes in, text-group ejected**: this is the blueprint's core glue and the only non-trivial seam. Use [reactive-displacement](../rules/reactive-displacement.md), but **NOT** its default `back.out` driver-with-derived-onUpdate form. We want the source's "heavy mass" feel (the hero lands rather than zips), which is best expressed in GSAP as a longer `HERO_DUR` with `power2.out` — three independent tweens sharing the same start time. See "Phase 3 Seam" below.
- **Phase 4 — hero idle breathing**: use [sine-wave-loop](../rules/sine-wave-loop.md) in its **multiplicative `onUpdate` form**, and specifically the **dual-frequency variation** (different periods on `scale` and `rotation`). The hero lands at `HERO_FINAL_SCALE > 1` from Phase 3's overshoot — the breath must compose onto that final scale, not yoyo around 1. See "Phase 4 Seam" below.

## Phase Timing

All boundaries are in seconds.

| Phase | Start ≥                                          | Internal duration                     | Notes                                                                               |
| ----- | ------------------------------------------------ | ------------------------------------- | ----------------------------------------------------------------------------------- |
| 1     | `0`                                              | `TYPE_DUR`                            | Smooth slice; `TYPE_START_LEN` ≥ 1 to avoid 1-char pop                              |
| 2     | `TYPE_END + ~1.0s` (`READ_BEAT`)                 | `(STEPS-1) × STEP_SPACING + STEP_DUR` | Reader needs ~1s on the static phrase before the ticker steals attention            |
| 3     | `TICKER_END + ~0.8s` (`SETTLE_BEAT`)             | `HERO_DUR`                            | Last ticker word must read; `back.out` tail must settle before collision            |
| 4     | `DISPLACE_AT + HERO_DUR + ~1.0s` (`SPRING_TAIL`) | `TOTAL - IDLE_START`                  | `power2.out` decays slowly — start sine too soon and it fights the perceived spring |

The `READ_BEAT` (~1s) between Phase 1 and 2 is non-negotiable — without it, the static phrase is still being absorbed when the ticker starts rolling, and the viewer reads neither. The `SETTLE_BEAT` (~0.8s) between Phase 2 and 3 is the most-skipped value in this blueprint: the last ticker word lands with a `back.out` overshoot that takes ~0.4s to fully damp, plus the eye needs at least 0.4s to read it. Anything less and the takeover feels like a hard cut. The `SPRING_TAIL` (~1.0s) between Phase 3 and 4 is the largest gap because `power2.out` over `HERO_DUR` (0.8–1.2s) has a long visual tail even after the tween mathematically ends — sine started during that tail produces visible chatter on scale.

## Initial DOM Nesting

The displacement target is the **parent flex row**, not the typewriter or ticker individually. That's what makes Phase 3 work as a single collision rather than three desynced reactions, and it's the most common structural mistake in this blueprint.

```
.stage                       ← absolute fill, overflow: hidden
  .text-group                ← Phase 3 push + fade target (single transform)
    .typewriter
      .typewriter-text       ← Phase 1 smooth-slice target
    .ticker-window           ← height = ITEM_HEIGHT, overflow: hidden
      .ticker-stack          ← Phase 2 translateY target
        .ticker-item × N
  .hero                      ← z-index: 20; Phase 3 entry + Phase 4 breath target
```

`.stage` is `position: absolute; inset: 0; overflow: hidden` — Phase 3 throws both `.text-group` and `.hero` past the frame edge; without `overflow: hidden` they leak into adjacent scenes. `.hero` carries `z-index: 20` explicitly (not relying on DOM order) — during the brief overlap window in Phase 3, the hero must be in front, otherwise the text's fading edges peek through.

## Phase 1 Seam: Smooth-Slice Variation (rule gap)

The frontmatter of [discrete-text-sequence](../rules/discrete-text-sequence.md) describes the multi-state `{text, t}` array form, but the smooth-slice form (a single tween from `0` to `FULL_TEXT.length`, `onUpdate` writes `FULL_TEXT.slice(0, Math.floor(progress))`) is what we use here. One sentence: tween a `{progress}` proxy linearly with `ease: 'none'`, `Math.floor` the result, only write `textContent` when the slice actually changed (avoids React-style re-render thrash).

Set `TYPE_START_LEN ≥ 1` — starting from 0 produces a single-character flash on the first frame as the viewport renders before any tween has fired. Starting from 1 hides this.

## Phase 2 Seam: Suppressing the Rule's Footer

[vertical-spring-ticker](../rules/vertical-spring-ticker.md) ships with a trailing `.brand` footer reveal — omit it here. Phase 3's collision replaces that beat. Also: the rule scopes everything inside its own `.stack` flex column; in this blueprint the ticker is one cell of a flex row (`.text-group`) sharing space with the typewriter, so use only the rule's `.ticker` + `.ticker-stack` markup, not its outer `.stack` wrapper. `ITEM_HEIGHT` must equal both the container height and per-item height exactly — covered in the rule, but worth re-checking because the row context makes height mismatches less visually obvious during dev.

Pick `STEPS = optionCount − 1` (you can't roll past your last item) and `STEP_SPACING ≤ STEP_DUR` for the additive-spring "click click" cadence the rule describes. The accent word's `font-weight` + `color` should distinguish it from the typewriter — readers should perceive "static base + rotating accent," not "two strings being equally typed."

## Phase 3 Seam: Collision (the blueprint's core glue)

The rule's default form uses a single `back.out` driver tween with `onUpdate` deriving both intruder and victim positions from `driver.p`. We **deliberately diverge** from that here, for two reasons.

**Why `power2.out` instead of `back.out`:** the source pattern this blueprint emulates uses a heavy-mass spring (the hero feels weighty, lands rather than bounces). `back.out` overshoots and rebounds, which reads as "lightweight + springy" — the wrong physical metaphor. A longer `HERO_DUR` (0.8–1.2s) with `power2.out` gives the gentle high-inertia deceleration that reads as mass.

**Why three independent tweens instead of one driver:** with `power2.out` (no overshoot, no oscillation), the math `driver.p × victimEnd` and `(driver.p × N)` produce monotonic linear-ish progress with no rebound — so we can express each motion as its own tween and let GSAP's clock keep them in sync. They must all start at `DISPLACE_AT` exactly; drift their start times by even a frame and the collision reads as two events.

```js
tl.fromTo(
  ".hero",
  { x: OFFSCREEN_X, scale: HERO_START_SCALE, rotation: HERO_START_ROT, opacity: 0 },
  {
    x: 0,
    scale: HERO_FINAL_SCALE,
    rotation: 0,
    opacity: 1,
    duration: HERO_DUR,
    ease: "power2.out",
  },
  DISPLACE_AT,
);

tl.to(
  ".text-group",
  { x: PUSH_DIST, duration: HERO_DUR * PUSH_FRACTION, ease: "power2.out" },
  DISPLACE_AT,
);

tl.to(
  ".text-group",
  { opacity: 0, duration: HERO_DUR * FADE_FRACTION, ease: "power2.out" },
  DISPLACE_AT,
);
```

`PUSH_FRACTION = 0.4–0.5` and `FADE_FRACTION ≤ PUSH_FRACTION` — these recreate the rule's `VICTIM_FRACTION` for the victim's exit. The text completes its push at roughly half the hero's duration, so by the time the hero centers the text is gone. If `PUSH_FRACTION ≥ 0.7` the two motions look parallel rather than causal — the most common failure mode.

**Direction coupling:** `sign(OFFSCREEN_X) = -sign(PUSH_DIST)`. The hero enters from positive X → text shoves into negative X. Same axis, opposite signs. Reverse either and the momentum-transfer metaphor breaks.

## Phase 4 Seam: Multiplicative Breath at Non-1 Scale

Phase 3 leaves the hero at `scale: HERO_FINAL_SCALE` (typically 1.0–1.4 — overshoot is part of "landing"). The breath must multiply onto this resting state, not yoyo around 1. [sine-wave-loop](../rules/sine-wave-loop.md)'s multiplicative `onUpdate` form does exactly this; the `fromTo` + yoyo form would re-apply `scale: 1` on every cycle, erasing the impact landing.

Use the **dual-frequency variation** (two separate `Math.sin` calls in one `onUpdate`, one driving scale, one driving rotation). The rule documents the multi-octave version primarily for scale-stacking; here we want scale + rotation oscillating _independently_, with **incommensurate periods** (no simple integer ratio). Why: synchronized scale-and-rotation reads as a single "tilt-pulse" beat — mechanical. Incommensurate periods (e.g. `SCALE_PERIOD = 1.7s`, `ROTATE_PERIOD = 2.3s`) keep the two cycles drifting against each other, which is what reads as "alive but resting."

Compute idleTime as `Math.max(0, tl.time() - IDLE_START)` inside the onUpdate so that timeline seeks before `IDLE_START` don't produce negative-phase sine values.

## Key Values to Choose (Not Already in the Rules)

Only parameters specific to this blueprint:

- **HERO_FINAL_SCALE**: 1.0 (no impact, feels light) → 1.2 (visible presence at rest) → 1.4 (heavy landing). Phase 4 breath multiplies onto this, so values >1.4 combined with `SCALE_AMP` >0.04 can push the hero past safe raster resolution.
- **PUSH_DIST**: 100–300 px, sign opposite `OFFSCREEN_X`. Smaller than half the viewport — this isn't an exit, it's a shove; the text is gone via opacity, not via leaving the frame.
- **PUSH_FRACTION / FADE_FRACTION**: 0.4–0.5 and `FADE_FRACTION ≤ PUSH_FRACTION` so the fade leads the push by a hair (text gets ghostly before it finishes sliding, not after).
- **READ_BEAT / SETTLE_BEAT / SPRING_TAIL**: ~1.0s, ~0.8s, ~1.0s respectively. These are the inter-phase buffers; do NOT shrink them to fit a tight `TOTAL` — extend `TOTAL` instead.
- **SCALE_PERIOD / ROTATE_PERIOD**: pick two values in 1.5–2.3s with NO integer ratio (e.g. 1.7 and 2.3, not 1.5 and 3.0). This is what produces organic breathing rather than mechanical pulsing.

## Critical Constraints (ordered by failure frequency)

- **Three Phase-3 tweens share `DISPLACE_AT` exactly** — drifting start times destroys the collision read. The most common bug: agents stagger them by 0.05s "to feel more natural" and the result feels less collisional, not more.
- **`PUSH_FRACTION ≤ ~0.6`** — beyond this the push reads as parallel motion, not reaction. 0.4–0.5 is the sweet spot.
- **Phase 4 breath multiplies, never yoyos around 1** — would erase `HERO_FINAL_SCALE` and undo Phase 3's landing. See Phase 4 Seam.
- **`sign(OFFSCREEN_X) = −sign(PUSH_DIST)`** — momentum transfer requires opposite signs on the same axis.
- **`SCALE_PERIOD : ROTATE_PERIOD` is non-integer** — equal or simple-ratio periods lock and read as mechanical.
- **`.hero` z-index ≥ 20 (explicit, not DOM-order)** — during the Phase 3 overlap window the text's fading edges will peek through otherwise.
- **Push the `.text-group` parent, not its children individually** — children inherit the parent transform and stay locked together; pushing them separately desynchronizes the collision.
- **Ticker container height = item height = `ITEM_HEIGHT`** — covered in the rule but worth re-checking in this blueprint's row layout where partial-item overflow can read as a row-baseline issue rather than a ticker bug.

## Spring → Ease Selection

Four phases, four feels. Full table in [hyperframes-animation/SKILL.md](../SKILL.md):

- Phase 1 typewriter: `ease: "none"` (linear, sine isn't involved — the discreteness comes from `Math.floor`)
- Phase 2 ticker steps: `back.out(BOUNCE_FACTOR)` per step (the rule's default)
- Phase 3 collision: `power2.out` over a long `HERO_DUR` (heavy-mass equivalent; NOT `back.out`)
- Phase 4 idle: dual `Math.sin` in one `onUpdate`, incommensurate periods

## Golden Sample

- [takeover-ticker-displace.html](../examples/takeover-ticker-displace.html) — runnable composition with concrete values for every named constant above; single paused GSAP timeline drives all four phases. Run this first, then change values — much faster than building from scratch.
