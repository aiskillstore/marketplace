---
id: hook-counter-burst
role: opening-hook
duration_seconds: [3, 5]
phases: 4
visual_arc: empty → icons-cluster → count-and-expand → camera-push
uses_rules:
  [counting-dynamic-scale, center-outward-expansion, multi-phase-camera, svg-icon-enrichment]
element_roles:
  counter: Central number counts 0 → target while growing in font size
  icons: 3-5 enriched SVG icons expand outward from center
  camera: Multi-phase zoom (pull-back → focus → push) wraps the scene
  background: Video or animated gradient with dark overlay for contrast
when_to_use:
  - Opening hook needs a single dramatic statistic
  - Statistic reinforced by 3-5 thematic icons
  - Scene must feel kinetic from frame 1
when_not_to_use:
  - Hook is text-driven, no numeric statistic
  - Product UI / demo footage is the focal point
  - Multiple numbers shown simultaneously
triggers: [opening hook, statistic, counting number, dramatic number, attention grabber]
---

# Hook · Counter Burst (HyperFrames)

A "scarcity → impact" emotional arc: the frame opens dark and empty, thematic icons puncture in clustered tightly at center as if held back, then the headline number explodes upward in size while the icons fling outward to meet their final marks — the count and the spread are the same beat — and a slow camera push closes the scene by leaning in for emphasis.

One paused GSAP timeline, four phases, deliberately overlapping so no frame is static.

## When to Use

- Opening scene needs a single dramatic statistic as the hook
- The statistic is reinforced by 3-5 thematic icons (e.g. clock, scissors, video, play)
- Scene must feel kinetic from frame 1 — no static moments
- Total duration short enough that the hook does not start to read as the main scene

## Orchestration

Four phases stack on the same timeline, with the most important coupling being Phase 3 — counter and icons share one tween envelope.

- **Phase 1 — cold open**: `inline`. Just background + dark overlay; nothing tweens. The icons exist in DOM but are pre-set to `scale: 0, opacity: 0` and pre-positioned at the cluster offset via `gsap.set` so they pop from the right place when their entry tween fires. The interesting thing about this phase: internal SVG animations from [svg-icon-enrichment](../rules/svg-icon-enrichment.md) — the rotating clock hand, pulsing record dot, flowing dashes — are already running invisibly underneath. See "Phase 1 seam" below.
- **Phase 2 — icon entries**: use [svg-icon-enrichment](../rules/svg-icon-enrichment.md) in its **per-icon staggered entry** form (each icon springs `scale: 0 → 1, opacity: 0 → 1` with a small rotation, ease `back.out(BOUNCE_FACTOR)`). Each icon's entry targets the inner `.icon-entry` wrapper, NOT the outer `.icon-pos` — because Phase 3 needs `.icon-pos`'s `x` / `y` channel free. See DOM tree.
- **Phase 3 — count + expansion (core glue)**: this is the blueprint's reason for existing. [counting-dynamic-scale](../rules/counting-dynamic-scale.md) drives the number; [center-outward-expansion](../rules/center-outward-expansion.md) drives the icons; both tweens are placed at the **same `COUNT_AT`, with identical `COUNT_DUR` and `COUNT_EASE`**. Because GSAP advances them in lockstep, no shared driver object is needed — the chord falls out for free. See "Phase 3 seam" below.
- **Phase 4 — multi-phase camera**: use [multi-phase-camera](../rules/multi-phase-camera.md) in its **focus-in pattern** (start < 1 → settle to 1 → push > 1). The pull-back is implicit: the scene begins at `CAMERA_SCALE_START < 1` set via `gsap.set` on `.camera`, so the icon cluster reads as "small and far" during Phase 1. We omit the rule's continuous drift overlay — at 3-5 seconds the drift is imperceptible and competes with the deliberate three-step scale rhythm. See "Phase 4 seam".

## Phase Timing

All boundaries are in seconds.

| Phase | Start ≥                                       | Internal duration                    | Notes                                                                        |
| ----- | --------------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| 1     | `0`                                           | until `ICON_ENTRY_AT_1`              | No tween fires; SVG enrichment loops are already turning underneath          |
| 2     | `ICON_ENTRY_AT_1` (≈ 0.1–0.25s)               | `(N - 1) × ICON_STAGGER + ENTRY_DUR` | Staggered; the last icon's entry must overlap, not precede, `COUNT_AT`       |
| 3     | `COUNT_AT`                                    | `COUNT_DUR`                          | Counter proxy + icon expansion tweens share start, duration, AND ease        |
| 4a    | `CAMERA_FOCUS_AT` (≈ 0.3–0.6s)                | `CAMERA_FOCUS_DUR`                   | Fires during Phase 2 — focus settle and icon entries can comfortably overlap |
| 4b    | `CAMERA_PUSH_AT ≥ COUNT_AT+COUNT_DUR + ~0.2s` | `CAMERA_PUSH_DUR`                    | Push only AFTER the count lands — let the eye read the final number first    |

There is no spring-tail breath between Phase 2 and Phase 3 — we _want_ the overlap so the eye never sees a still frame. The constraint is the opposite of `brand-reveal-assemble-zoom`'s "let spring settle": here the last icon's `back.out` rebound should still be visible as the count starts, which adds energy. The ~0.2s gap between Phase 3 end and Phase 4b matters: without it, the camera push competes with the counter's `power2.out` decel and the eye can't choose which to watch. Phase 4a (focus settle) deliberately starts inside Phase 2 so the camera is already moving when the icons land — same "no static frame" principle.

## Initial DOM Nesting

The two-wrapper-per-icon split is non-obvious and load-bearing — Phase 2's entry tween and Phase 3's expansion tween must not fight for the same transform channel.

```
.stage
  .bg                    ← background video / gradient
  .camera                ← Phase 4 scale (multi-phase camera)
    .icons-stage
      .icon-pos          ← Phase 3 expansion: gsap.set x/y to cluster, then tween to 0,0
        .icon-entry      ← Phase 2 entry: scale, opacity, rotation
          svg.icon-svg   ← svg-icon-enrichment internal motion targets children by id
    .counter-stage
      .counter-3d
        .counter-number  ← counting-dynamic-scale onUpdate writes text + font-size
        .counter-suffix
  .vignette              ← OUTSIDE .camera so it doesn't scale with the push
```

Each `.icon-pos`'s final `left` / `top` are written **once** in CSS (or by a one-shot `gsap.set` before timeline registration) as the icon's target layout position. GSAP only ever touches `x` / `y` on `.icon-pos` — never `left` / `top`. The cluster offset at t=0 is pre-applied by `gsap.set` as a negative `x` / `y` (toward center), then the Phase 3 tween animates back to `x: 0, y: 0`.

`.vignette` sits OUTSIDE `.camera` because the camera scale `> 1` in Phase 4b would otherwise crop the vignette and reveal the unvignetted corners.

## Phase 1 Seam: Live Icons Before They Appear

The headline trick of this scene: the rotating clock hand, the pulsing rec dot, the flowing dashes — every internal SVG animation defined by [svg-icon-enrichment](../rules/svg-icon-enrichment.md) — is placed at timeline position `0`, not gated by the icon's entry delay. The icons are invisible (`scale: 0, opacity: 0` on `.icon-entry`) but the SVG children underneath are already turning. When Phase 2 makes an icon visible, it doesn't _start_ moving — it has _been_ moving. The viewer perceives "alive thing arrives," not "static thing animates on landing."

```js
// At timeline position 0, NOT gated by entry delay
tl.to(minState, { deg: 360 * MIN_REVOLUTIONS, duration: TOTAL_DURATION, ease: "none", onUpdate: ... }, 0);
tl.to(pulseState, { p: Math.PI * 2 * PULSE_CYCLES, duration: TOTAL_DURATION, ease: "none", onUpdate: ... }, 0);
```

The rule documents these patterns but doesn't explicitly call out the "run while invisible during a cold open" use case — it's the blueprint's job to combine.

## Phase 3 Seam: One Chord, Two Tweens

The counter and the expansion are mathematically independent — counter writes text + font-size to one DOM node, expansion writes `x` / `y` to N icon nodes. But they must read as **one event**. The mechanism: place both tweens at the same `COUNT_AT` with identical `COUNT_DUR` and `COUNT_EASE`, and let GSAP's per-frame eased progress synchronize them. No shared `state` object, no master `onUpdate` dispatching to both — they advance in lockstep because they were configured identically.

The cluster offset is the interesting derivation. Each icon's final layout position is `(targetX, targetY)`. To start it at fraction `(1 - START_OFFSET)` of the way from target back toward center, we pre-set its `x` / `y` (relative to its CSS-fixed target position) to:

```js
gsap.set(`${sel}.icon-pos`, {
  x: (CENTER_X - targetX) * (1 - START_OFFSET),
  y: (CENTER_Y - targetY) * (1 - START_OFFSET),
});
tl.to(`${sel}.icon-pos`, { x: 0, y: 0, duration: COUNT_DUR, ease: COUNT_EASE }, COUNT_AT);
```

The `(1 - START_OFFSET)` factor (not `START_OFFSET` itself) is the part agents most often invert. `START_OFFSET = 0.4` means "icons begin 40% of the way out from center"; the pre-set offset toward center is therefore the remaining 60% of the path. Get the sign wrong and the icons start _past_ their targets and move inward.

**Why a separate `.to` per icon instead of one master proxy?** GSAP handles many simultaneous identically-eased tweens cheaply (compositor batches transform writes), and per-icon tweens are inspectable in DevTools. For 3-5 icons readability wins; for 50+ a single onUpdate with a manual lerp loop would be preferable.

The counter side uses the **proxy-object form** of [counting-dynamic-scale](../rules/counting-dynamic-scale.md) (`{ p: 0 } → { p: 1 }`, onUpdate writes text + font-size) rather than the rule's `state.value` form, only because we want `p` for compositional reasons — it could equivalently be driven by the rule's default state object.

## Phase 4 Seam: Why No Drift Overlay

[multi-phase-camera](../rules/multi-phase-camera.md)'s default includes a continuous sine drift on top of the phase scales. We deliberately omit it here. Two reasons specific to this scene:

1. **Three to five second comp**: drift only reads over time. Below ~6 seconds the eye doesn't register the slow sine — but the rotating SVG hands and pulsing dots already give continuous micro-motion underneath, so the camera doesn't need to.
2. **Three-step scale rhythm is the camera's job here** — `START → FOCUS → PUSH` is a discrete cinematic beat. A drift overlay blurs the moment of "push" because the translate is already moving when the scale starts.

`CAMERA_SCALE_START < 1` is mandatory: it provides the pull-back from which the focus-settle reads. This in turn forces `.scene` to use `overflow: hidden` (per the rule's constraint) so the inner edges revealed by `scale < 1` don't leak.

`CAMERA_PUSH_AT > COUNT_AT + COUNT_DUR + ~0.2s` is the second non-negotiable gate. If push starts during the count, the user sees scale change while reading digits — the scale wins and the number gets misread.

## Key Values to Choose (Not Already in the Rules)

Only parameters this blueprint introduces. Standard rule parameters (`BOUNCE_FACTOR`, `ENTRY_DUR`, `PULSE_CYCLES`, drift amps, etc.) live in the linked rules.

- **ICON_COUNT** — 3-5. Below 3 the cluster reads as accidental; above 5 the centre overlaps even at `START_OFFSET = 0.5` and looks like collision. Hard cap on this blueprint specifically.
- **START_OFFSET** — fraction of the path from center to target at which icons begin. `0.3-0.5`. Sub-0.3 reads as debris explosion; above 0.5 the outward motion vanishes. Used twice — in the `gsap.set` pre-position and conceptually in the chord coupling.
- **COUNT_AT** — when the count chord fires. Must satisfy `COUNT_AT > ICON_ENTRY_AT_1 + ICON_STAGGER` (so at least one icon is visible at chord start) and `COUNT_AT + COUNT_DUR < CAMERA_PUSH_AT - ~0.2s`. Practical range 0.4-0.7s for a 3-5s comp.
- **COUNT_DUR / COUNT_EASE** — pulled from [counting-dynamic-scale](../rules/counting-dynamic-scale.md)'s range, but with one extra constraint specific to this blueprint: the value used for the counter MUST equal the value used for every icon expansion `.to`. The rule's range still applies; the equality is unique to this scene.
- **CAMERA_SCALE_START** — must be `< 1` here (no other pattern works with the focus-in framing). `0.88-0.96`. Forces `overflow: hidden` on `.scene`.

## Critical Constraints (ordered by failure frequency)

The most common failures, top down:

- **Identical `duration` + `ease` on every Phase 3 tween (counter proxy AND each icon's `x` / `y` to `0`)**. Mismatched ease is the #1 way this scene falls apart — counter and icons drift visually out of phase even though they share a start time.
- **`(1 - START_OFFSET)` sign in the pre-position `gsap.set`**, NOT `START_OFFSET`. The fraction is "remaining distance to cover," not "starting fraction."
- **`CAMERA_PUSH_AT ≥ COUNT_AT + COUNT_DUR + ~0.2s`**. Camera push during the count makes the number unreadable.
- **Two-wrapper-per-icon split**. `.icon-pos` for Phase 3 x/y; `.icon-entry` for Phase 2 scale/opacity/rotation. Collapsing them into one element makes Phase 3 overwrite Phase 2's final state and icons re-appear at scale 1 abruptly.
- **SVG enrichment tweens placed at timeline `0`**, not gated by entry delay. Otherwise icons look static for one frame on landing before motion kicks in.
- **`font-variant-numeric: tabular-nums` on `.counter-number`** — required by [counting-dynamic-scale](../rules/counting-dynamic-scale.md) but doubly important here because the count overlaps with motion: any horizontal jitter from digit-width changes is amplified by the surrounding kinetic context.
- **`overflow: hidden` on `.scene`** — forced by `CAMERA_SCALE_START < 1`.
- **`.vignette` outside `.camera`** — the Phase 4b push would otherwise crop it.
- **`ICON_COUNT ≤ 5`** — beyond this even high `START_OFFSET` reads as collision at the cluster moment.

## Spring → Ease Selection

Three distinct feels, three eases. Full mapping table in [hyperframes-animation/SKILL.md](../SKILL.md).

- Phase 2 stiff icon entry → `back.out(BOUNCE_FACTOR)`
- Phase 3 counter + expansion chord → `power2.out` (default) or `power3.out` for stronger settle. **Avoid** `back.out` here — the rule already says it for the counter, but it applies to the icons too because they share the tween.
- Phase 4a / 4b camera transitions → `power2.out`; the push can step up to `power3.out` if you want the close to feel "deeper" than the settle.

## Golden Sample

- [hook-counter-burst.html](../examples/hook-counter-burst.html) — runnable 4-icon, ~4s composition with concrete values for every named constant. Start here, then change one parameter at a time.
