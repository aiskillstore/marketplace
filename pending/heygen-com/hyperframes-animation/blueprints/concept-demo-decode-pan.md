---
id: concept-demo-decode-pan
role: concept-demo
duration_seconds: [6, 10]
phases: 4
visual_arc: text-decode → scene-pan → cursor-track
uses_rules: [hacker-flip-3d, camera-cursor-tracking, discrete-text-sequence]  # discrete-text-sequence = smooth-slice variant
element_roles:
  shot1_static: Context-setting text that fades in (tagline, slogan)
  shot1_accent: Accent word that decrypts via hacker-flip 3D (the hook)
  shot2_interactive: Interactive element (search bar, input field) with cursor-tracked typing
when_to_use:
  - Two visually distinct shots connected by a cinematic transition
  - First shot reveals text dramatically (decode / decrypt)
  - Second shot demonstrates product interaction (typing, search, input)
  - "Reveal the concept → show it in action" flow
when_not_to_use:
  - Single scene, no transition — see brand-reveal-assemble-zoom or takeover-ticker-displace
  - Shots should cross-fade rather than pan
  - No text decode in the first shot
  - Second shot is static (no dynamic tracking)
triggers: [decode effect, decrypt, scene transition, search bar typing, horizontal pan, show then demonstrate]
---

# Concept-Demo · Decode & Pan (HyperFrames)

This is a "tease → reveal → demonstrate" emotional arc: the viewer reads a static phrase, then the accent word decrypts in front of them like an old flap-display — the _concept_ has just been declared. Before they can dwell, the camera pans sideways into a second shot where the product itself starts typing, answering "and here's what it does." Shot 1 is the hook; the pan is the bridge; Shot 2 is the proof.

Four phases on one paused GSAP timeline. The pan is the only place two unrelated rules' end-states have to align in screen space, and it's the failure-prone joint.

## When to Use

- Promo has two narrative beats: concept reveal, then product demo
- First beat needs a dramatic text effect (decode / decrypt)
- Second beat shows interactive behavior (typing, searching, input)
- Need spatial continuity between beats (pan, not cut)

## Orchestration

This scene combines three rules plus one inline phase, threaded together by a horizontal "shot strip" that the camera slides through.

- **Phase 1 — Shot 1 entry**: no rule, inline `fromTo` on `.shot1-content` (`opacity: 0 → 1`, `y: RISE_DIST → 0`, `power2.out`). This is a context-setting fade-rise — too small a motion to deserve its own rule, and giving it `back.out` would compete with the decode's elasticity in Phase 2.
- **Phase 2 — accent word decode**: use [hacker-flip-3d](../rules/hacker-flip-3d.md) at the rule's default `transform-origin: bottom` (flap-display look). Reason for the default here: the accent word reads as a "verdict landing" — the bottom-hinge flap feels mechanical and authoritative, where a top hinge would feel like the text is falling away from the viewer just when we want it to arrive. The static phrase next to it stays still — only the accent word gets the 3D treatment, so visual hierarchy reads cleanly.
- **Phase 3 — horizontal pan + parallax + Shot 2 entry**: no rule, this is the blueprint's core glue. Three concurrent tweens at the same timeline position, all sharing `PAN_DUR`. See "Phase 3 Seam" below for the pan-ease constraint and the parallax math.
- **Phase 4 — cursor-tracked typing**: use [camera-cursor-tracking](../rules/camera-cursor-tracking.md) in its **continuous-typing-driver variation** (the one called out in that rule's Variations section, not the default `maxWidth` form). Reason: the cursor's screen X has to feed the _parent strip's_ `x` transform, not just the world container's, because the strip is already carrying the Shot 1→Shot 2 pan. Two cameras nested would be untenable. The typing driver itself is [discrete-text-sequence](../rules/discrete-text-sequence.md) in its **smooth-slice variation** (continuous typewriter, no typos). We don't want the human-typing chaos here — the demo is selling product confidence, not realism.

## Phase Timing

| Phase | Start ≥                               | Internal duration                   | Notes                                                             |
| ----- | ------------------------------------- | ----------------------------------- | ----------------------------------------------------------------- |
| 1     | `0` (or end of previous scene)        | `ENTRY_DUR`                         | Static text + accent placeholder both fade in together            |
| 2     | `ENTRY_START + ENTRY_DUR` (no buffer) | `FLIP_STAGGER × (N − 1) + FLIP_DUR` | Decode starts the instant entry lands — no breath, builds urgency |
| 3     | `FLIP_END + ~0.2s`                    | `PAN_DUR`                           | Decode needs to _visually settle_ before the camera tears away    |
| 4     | `PAN_START + PAN_DUR + ~0.15–0.2s`    | until `TOTAL_DURATION − dwell`      | Eye needs a beat to find the bar before reading typing            |

Phase 1 → Phase 2 has **no gap** on purpose. The accent slot is already in its final layout position during Phase 1 (the flip rotates from `90°` to `0°` in place, no translation), so kicking the decode the instant the fade lands stacks the two beats into one continuous "here it comes — and there it is." Inserting a buffer here makes the decode feel detached from the phrase.

The 0.2s gap between Phase 2 and 3 is the most failure-prone one. `back.out` on the per-glyph flip overshoots and rebounds (see [hacker-flip-3d](../rules/hacker-flip-3d.md)'s default ease); if you pan while the last glyph is still settling, the strip is sliding sideways while one character is still rotating, and the eye reads it as a glitch. The 0.2s is roughly the spring tail of the last character's `back.out(FLIP_BOUNCE)` — pad it more if you pick a larger `FLIP_BOUNCE`.

The 0.15–0.2s gap between Phase 3 and 4 is a reading buffer, not a spring buffer. The pan ends cleanly (`power3.inOut` has no overshoot), but the viewer's eye needs ~150ms to re-anchor on Shot 2's bar before typing starts. Cut this gap and the first few characters get missed.

## Initial DOM Nesting (Horizontal Shot Strip)

The "shot strip" architecture is the spatial backbone — both Phase 3 (pan) and Phase 4 (cursor tracking) tween the same `.strip` element, so the order of layers below it must not bake any pan offset into Shot 2's internal world space.

```
.viewport            (overflow: hidden — clips off-screen shots)
  .strip             (flex row; Phase 3 + Phase 4 both tween its x)
    .shot.shot1
      .shot1-content (Phase 1 fade-rise target; Phase 3 parallax target)
        .shot1-row
          .shot1-static          (static phrase, no animation)
          .shot1-accent          (Phase 2 hacker-flip container)
            .flip-glyph × N      (one per char of accentWord)
    .shot.shot2
      .shot2-bar     (Phase 3 fade-scale target; cursor sits here in Phase 4)
        .search-text (Phase 4 typing target; smooth-slice variation)
        .search-cursor
```

Each `.shot` is exactly `VIEWPORT_W` wide with `flex-shrink: 0`; the strip width is therefore implicit (`shots × VIEWPORT_W`) and the pan distance equals one `VIEWPORT_W`. Letting flex compress the shots would silently shrink the pan distance and the camera would over-shoot in Shot 2.

`.shot2-bar` ships with `opacity: 0` and `transform-origin: left center` so Phase 3's `back.out` scale lands the bar correctly when it arrives. The bar's width is pre-allocated from a font probe before the timeline registers — see Phase 4 Seam.

## Phase 3 Seam: The Pan (Strip + Parallax + Shot 2 Entry)

Three tweens fire at the same timeline position, all sharing `PAN_DUR`:

1. `.strip` tweens `x: 0 → -VIEWPORT_W` with `power3.inOut` (the camera)
2. `.shot1-content` tweens `x: 0 → -PARALLAX_DIST` with `power3.inOut` (the near-plane, moves faster than the camera so depth reads)
3. `.shot1-content` _also_ tweens `opacity: 1 → 0` with `power2.out`, duration `PAN_DUR × FADE_RATIO` — the fade finishes before the pan does so the eye is on Shot 2 well before the strip stops
4. `.shot2-bar` tweens `opacity: 0 → 1` and `scale: ENTRY_SCALE_FROM → 1` with `back.out(ENTRY_BOUNCE)` over `PAN_DUR` (the landing)

**The pan ease is the most common point of failure here.** `back.out` on the _strip_ reads as a UI bounce — the viewer's brain says "menu sliding in," not "camera moving." Use `power3.inOut` (slow start, slow finish — feels cinematic) or `power2.out` (quicker, snappier — feels like a UI swipe but still not a bounce). Reserve `back.out` for the `.shot2-bar` _entry_, where overshoot reads as the bar landing into place.

The parallax is additive: `.shot1-content`'s `x` displacement is _on top of_ the strip's `x`. When the strip has moved `-VIEWPORT_W` and `.shot1-content` has moved an extra `-PARALLAX_DIST`, the Shot 1 layer has effectively moved `-(VIEWPORT_W + PARALLAX_DIST)` in world space — so it leaves the frame faster than the camera passes it, which is what "near plane moves faster" means optically. `PARALLAX_DIST` in the 15–25% of viewport width range reads as strong depth without throwing Shot 1 away.

`FADE_RATIO` should land Shot 1's opacity at 0 around the 30–50% mark of the pan — fading later leaves stale content on screen during the climax, fading earlier kills the parallax (you can't perceive depth on an invisible layer).

## Phase 4 Seam: Cursor-Tracked Typing Inside the Already-Panned Strip

This is the joint that the rule alone can't solve. [camera-cursor-tracking](../rules/camera-cursor-tracking.md) describes a `.world` container that translates inside a `.viewport`. In this scene, the strip _is_ the world — and it's already at `x: -VIEWPORT_W` from Phase 3. Phase 4's tracking offset has to add to that, not replace it.

The piecewise camera handoff:

```js
// In an onUpdate driven by a typing-progress tween (smooth-slice form):
const charsTyped = Math.floor(progress * FULL_TEXT.length);
const typedWidth = measuredCharOffsets[charsTyped]; // pre-measured per-char left edges
const cursorWorldX = BAR_LEFT_MARGIN + PADDING_LEFT + typedWidth;
const targetScreenX = CURSOR_TARGET_FRACTION * VIEWPORT_W;
const trackingStripX = -VIEWPORT_W + (targetScreenX - cursorWorldX);
const finalStripX = Math.min(STRIP_BASE_X + INITIAL_OFFSET, trackingStripX);
gsap.set(".strip", { x: finalStripX });
```

Three things matter and the rule does not say them because they only make sense in this composite scene:

- **`STRIP_BASE_X = -VIEWPORT_W`** by construction (Phase 3 ended there). The `Math.min` baseline is that value plus `INITIAL_OFFSET` (typically 0), not 0.
- **Per-character offsets are pre-measured once** from the full target string, then stored as an array. Measuring `getBoundingClientRect()` on a growing text node per frame works but adds layout cost on every seek; the array form is O(1) per frame.
- **`Math.min` (not an `if` branch).** The handoff between "static" and "tracking" is mathematically continuous: while the cursor is left of the target screen X, `trackingStripX` is _less negative_ than the baseline, so `Math.min` returns the baseline. The instant the cursor crosses, `trackingStripX` overtakes it and tracking begins — no jump. An `if (charsTyped > threshold)` branch will visibly snap on the boundary character.

The bar's pixel width must be pre-allocated from a real font measurement before the timeline registers, so the typing doesn't reflow the bar (which would invalidate `measuredCharOffsets`):

```js
const probe = document.createElement("span");
probe.style.cssText =
  "position:absolute; left:-99999px; white-space:pre; " +
  `font: ${BAR_FONT_WEIGHT} ${BAR_FONT_SIZE}px ${BAR_FONT_STACK};`;
probe.textContent = FULL_TEXT;
document.body.appendChild(probe);
const fullTextWidth = probe.getBoundingClientRect().width;
probe.remove();
document.querySelector(".shot2-bar").style.width =
  PADDING_LEFT + fullTextWidth + CURSOR_VIS_W + PADDING_RIGHT + "px";
```

Build the timeline **synchronously** without a `document.fonts.ready` gate — that gate causes worker-race flicker on parallel-frame renders. See [camera-cursor-tracking](../rules/camera-cursor-tracking.md#critical-constraints) for the rationale; this is a hard constraint inherited from that rule. Fallback-font measurement error of a few percent is recoverable; missing timeline registration is not.

If the typing finishes before `TOTAL_DURATION`, extend the dwell with the rule's GSAP-driven finite-yoyo cursor blink so the GSAP timeline and the root composition's `data-duration` end together. CSS `@keyframes blink infinite` will flicker non-deterministically under HF's seek-by-frame.

## Key Values to Choose (Not Already in the Rules)

Only values **specific to this blueprint** below; standard parameters (`FLIP_DUR`, `FLIP_STAGGER`, `CURSOR_TARGET_FRACTION`, `BAR_FONT_SIZE`, etc.) live in the referenced rules.

- **`VIEWPORT_W` / `VIEWPORT_H`**: must equal the scene root's `data-width` / `data-height` and are the per-shot width on the strip. Any mismatch makes the pan over- or under-shoot by exactly that delta.
- **`PARALLAX_DIST`**: extra pixels Shot 1 content travels beyond the strip. 15–25% of `VIEWPORT_W` reads as cinematic depth; over 30% feels like Shot 1 is being thrown away, under 10% reads as no parallax at all.
- **`FADE_RATIO`**: 0.3–0.5 of `PAN_DUR`. Shot 1's opacity reaches 0 at this fraction — fade later and stale content sits on the climax; fade earlier and the parallax has nothing visible to move.
- **`PAN_DUR`**: 0.5–1.0s. Under 0.4s reads as a whip-pan (disorienting between two distinct shots); over 1.2s drags the bridge.
- **`ENTRY_SCALE_FROM`**: 0.7–0.9 on the bar. Smaller exaggerates the landing; the `back.out(ENTRY_BOUNCE)` ease assumes some headroom, so don't go above 0.95 or the overshoot has nothing to do.
- **`STATIC_WEIGHT` vs `ACCENT_WEIGHT`**: discrete font weights, but with `ACCENT_WEIGHT > STATIC_WEIGHT` so the accent word reads as dominant even before it decodes. The decode then _confirms_ a hierarchy the eye already saw — pleasant, not surprising.
- **`BAR_LEFT_MARGIN`**: 40–120 px from the left edge of Shot 2. This is where the empty bar sits before tracking starts; pick it visually, the Phase 4 math compensates for whatever you choose.
- **`INITIAL_OFFSET`**: usually 0 (bar sits where `BAR_LEFT_MARGIN` puts it). Non-zero values pre-shift the bar in screen space if the bar needs to feel "already mid-frame" at the start of typing.

## Critical Constraints (ordered by failure frequency)

- **Pan ease is `power3.inOut` or `power2.out`, never `back.out`** — overshoot on the strip reads as a UI menu, not a camera. Reserve `back.out` for `.shot2-bar` entry inside Shot 2.
- **Phase 4 uses `Math.min`, not an `if` branch** — the static→tracking handoff must be mathematically continuous, or the camera snaps on the boundary character.
- **Pre-allocate the bar's width from a real font probe before timeline registration** — letting the bar grow with the typed text invalidates the per-character offset array and the cursor falls behind by ~1 character.
- **Build the timeline synchronously, no `document.fonts.ready` gate** — see [camera-cursor-tracking constraints](../rules/camera-cursor-tracking.md#critical-constraints); worker-race flicker is unacceptable.
- **`STRIP_BASE_X = -VIEWPORT_W` is the baseline for Phase 4, not 0** — Phase 3 ended the strip there. Forgetting this resets the camera to Shot 1 the instant typing starts.
- **`.shot { width: VIEWPORT_W; flex-shrink: 0 }`** — without `flex-shrink: 0`, flex compresses both shots into one viewport, pan distance becomes wrong, parallax silently breaks.
- **Cursor blink via finite GSAP yoyo, not CSS `@keyframes blink infinite`** — CSS animation clocks don't sync with HF's per-frame seek.
- **Phase 1 → Phase 2: no gap; Phase 2 → Phase 3: ≥ 0.2s; Phase 3 → Phase 4: ≥ 0.15s** — see Phase Timing for the per-gap rationale.
- **Three concurrent tweens in Phase 3 must share `PAN_DUR`** — pan, parallax, and Shot 2 entry are read as one cinematic event; differing durations decouple them visually.

## Spring → Ease Selection

Four phases, four feels. The complete spring → ease mapping table lives in [hyperframes-animation/SKILL.md](../SKILL.md); this blueprint's defaults:

- Phase 1 settle → `power2.out`
- Phase 2 character flip → `back.out(FLIP_BOUNCE)` (rule default)
- Phase 3 camera pan + parallax + Shot 1 fade → `power3.inOut` (pan/parallax), `power2.out` (fade)
- Phase 3 Shot 2 landing → `back.out(ENTRY_BOUNCE)` (mild overshoot)
- Phase 4 typing driver → `"none"` (linear); camera tracking driven by `gsap.set` in `onUpdate`, no ease

## Golden Sample

- [concept-demo-decode-pan.html](../examples/concept-demo-decode-pan.html) — runnable composition with concrete values for every named constant above. Single paused GSAP timeline drives all four phases; the strip's `x` is shared between Phase 3's pan tween and Phase 4's `gsap.set` cursor tracking. Run it first, then change values — far faster than building from scratch.
