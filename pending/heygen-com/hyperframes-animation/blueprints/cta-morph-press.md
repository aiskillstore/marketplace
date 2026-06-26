---
id: cta-morph-press
role: cta
duration_seconds: [4, 6]
phases: 4
visual_arc: hero-entrance → morph-swap → cursor-approach → press-react
uses_rules: [sine-wave-loop, scale-swap-transition, physics-press-reaction]
element_roles:
  hero: Initial focal element (logo, brand lockup, product) that establishes presence then exits via shrink-fade
  cta: Interactive target (button, card, link) that enters via bouncy scale-swap at the hero's position
  cursor: Pointer that enters from off-screen along a spring path, then performs a physical click
when_to_use:
  - Scene transitions from brand presence to a call-to-action
  - Two elements occupy the same screen position sequentially (morph illusion)
  - Simulated user interaction (cursor click) on the final element
  - Hero should feel "alive" before transforming (breathing idle)
when_not_to_use:
  - Hero and CTA coexist on screen — see brand-reveal-assemble-zoom
  - CTA enters from off-screen — see takeover-ticker-displace
  - No click interaction — use scale-swap-transition alone
  - Multiple CTAs need sequential interaction
triggers:
  [logo morphs into button, CTA animation, cursor clicks button, brand to action, morph transition]
---

# CTA · Morph & Press (HyperFrames)

This is a "presence → action" arc: the hero establishes the brand for a beat or two — alive but resting, just a faint rotational breath on the logo — then condenses into a smaller, brighter CTA at the same screen center; a cursor arrives from off-stage and lands a physical click on it. The viewer's eye is moved from "this is who we are" to "and this is what you do."

Four phases on a single paused GSAP timeline. The morph (Phase 2) and the click (Phase 4) are the headline beats; Phases 1 and 3 are the setup and approach that make those beats legible.

## When to Use

- Scene arc moves from brand identity to user action
- Two elements share the same screen center but appear sequentially (morph)
- Final beat is a simulated click interaction with physical feedback
- Hero needs subtle ambient motion before transformation

## Orchestration

Each phase maps to one rule (or an inline pattern) — pick the variation that fits this scene's specific constraints, not the rule's default:

- **Phase 1 — hero entrance + breath**: inline `power3.out` fade-and-rise for the entrance, plus [sine-wave-loop](../rules/sine-wave-loop.md) in its **rotation-only, scope-restricted** variation. The rule's main form breathes scale + y on the entire focal element; here we deliberately apply it **only to `.hero-logo`**, not the whole hero. Reason: the hero's `scale` gets overwritten by the Phase 2 morph exit, and a scale-breath on the hero itself would fight that tween in the overlap. Rotation alone reads as alive, and scoping it to the logo keeps the title text rock-stable. Scale-breath below ~0.012 is under the perception threshold anyway — skip it without regret.
- **Phase 2 — morph swap**: use [scale-swap-transition](../rules/scale-swap-transition.md), but **without the rule's `inset: 0` card-in-fixed-wrap container**. Hero and CTA are flex-centered siblings here, not stacked cards. They still share `transform-origin: 50% 50%` (which is what actually sells the morph), but their footprint is governed by flex and intrinsic content size, not a `SWAP_WRAP_W × SWAP_WRAP_H` box. The CTA's `position: absolute` keeps it from displacing the hero in the document flow during the brief overlap. See "Phase 2 seam" below.
- **Phase 3 — cursor approach**: no rule — inline. [physics-press-reaction](../rules/physics-press-reaction.md) does include an APPROACH sub-phase, but its default lands the cursor dead-center on the button (`BUTTON_CENTER`) with `power2.inOut`. This scene wants a **`power2.out` deceleration from off-screen** (cursor "arrives" rather than "passes through"), and the landing point must be **a few px off the button's geometric center** so the click reads as human, not scripted. Cursor opacity also hard-cuts in via a near-zero-duration `fromTo` — see "Phase 3 seam."
- **Phase 4 — press + release**: use [physics-press-reaction](../rules/physics-press-reaction.md), but **only the PRESS_DOWN + RELEASE portion** — Phase 3 has already handled the APPROACH inline. The press fires with the rule's signature `["#cta", "#cursor"]` single-target-array tween so both elements compress in perfect lockstep. See "Phase 4 seam" for why we lean on GSAP's auto-overwrite rather than composing scales manually.

## Phase Timing

All boundaries are in seconds.

| Phase | Start ≥                             | Internal duration                  | Notes                                                        |
| ----- | ----------------------------------- | ---------------------------------- | ------------------------------------------------------------ |
| 1     | `0.1–0.4s` (`INTRO_START`)          | `INTRO_DUR` (0.35–0.7s)            | Breath rotation runs from `t=0`, invisible until entry fades |
| 2     | `INTRO_START + INTRO_DUR + 1–2s`    | `MORPH_EXIT_DUR` / `MORPH_ENT_DUR` | The 1–2s presence-dwell is the most important gap here       |
| 3     | `MORPH_AT + MORPH_ENT_DUR + ~0.1s`  | `CURSOR_PATH_DUR` (0.7–1.4s)       | CTA's back.out tail must settle before the cursor enters     |
| 4     | `CURSOR_ENTER_AT + CURSOR_PATH_DUR` | `CLICK_DOWN_DUR + CLICK_UP_DUR`    | **Exactly equal**, not "greater than" — see Phase 3→4 seam   |

The 1–2s **presence-dwell** between Phase 1 and Phase 2 is the gap that almost everyone gets wrong by making it too short. Morphing the hero away half a second after it lands robs the brand of any actual presence — the viewer registers the morph as the headline and forgets the hero ever existed. Dwell long enough that the breath rotation completes most of a cycle (so the viewer's eye notices the aliveness) before transforming.

The `~0.1s` between Phase 2 and Phase 3 is the same idea as brand-reveal's `back.out` settling gap: the CTA's overshoot is still oscillating fractionally for a few frames after its nominal duration, and a cursor entering during those frames "shakes the camera." Wait for the spring tail.

The `CLICK_DOWN_AT == CURSOR_ENTER_AT + CURSOR_PATH_DUR` constraint between Phase 3 and Phase 4 is **a strict equality, not a buffer**. The viewer perceives "cursor lands" and "button compresses" as a single causal event; any gap, even one frame, reads as the cursor pausing then clicking. Bind these two values to the same expression in code.

After the release, hold at least one full second of climax dwell (`TOTAL_DUR ≥ CLICK_UP_AT + CLICK_UP_DUR + 1s`) so the spring rebound is legible — otherwise the comp ends mid-overshoot and the press never quite "lands."

## Initial DOM Nesting

The relevant fact is that hero and CTA are **siblings sharing the same flex-centered viewport position**, not stacked `inset:0` cards as in `scale-swap-transition`'s default. The cursor is a third sibling living at scene-root level, free to translate anywhere.

```
.stage  (flex; align/justify center; relative)
├── #hero
│     ├── .hero-text
│     └── .hero-logo   ← Phase 1 breath target (rotation only)
├── #cta  (position: absolute; z-index 10)
│     └── .cta-text    ← reveals after container reaches recognizable scale
└── #cursor (position: absolute; z-index 100)
```

The CTA's `position: absolute` is essential — without it, the CTA would push the hero out of the flex layout the moment it materialises, and both elements would shift sideways instead of morphing in place. Hero stays in flow; CTA layers on top.

## Phase 1 Seam: Why Breath Lives on `.hero-logo`, Not `.hero`

The breath rotation uses the `onUpdate` form from [sine-wave-loop](../rules/sine-wave-loop.md) but written against `tl.time()` directly (not a phase-tween from 0 → 2π), and the target is **the logo sub-element only**. Three reasons stack here:

1. The Phase 2 morph exit tweens `#hero { scale: EXIT_SCALE }`. If the breath were also writing `scale` onto `#hero`, the two tweens would race and GSAP's auto-overwrite would silently drop one.
2. Scoping breath to the logo lets the hero's title text stay rigid — moving text reads as instability, not life.
3. Pure rotation at `±2–6°` is enough to communicate "alive but resting"; adding a sub-threshold scale-breath only complicates the morph exit math without adding perceptible motion.

This is a one-sentence variation of `sine-wave-loop` worth flagging: the rule's main example writes both scale and y; the rotation-only sub-element form is a real pattern but barely shown.

## Phase 2 Seam: Same Center, Different Container Topology

[scale-swap-transition](../rules/scale-swap-transition.md) assumes both swap targets share an `inset: 0` parent inside a fixed `SWAP_WRAP_W × SWAP_WRAP_H` wrap. This scene breaks that assumption because the hero is a typographic group whose intrinsic width depends on `{Brand}` — pre-locking a wrap size would either crop the brand or pad the CTA with dead space.

The substitute: both elements rely on the parent `.stage`'s `align-items: center; justify-content: center` for centering, and `#cta` is taken out of flow with `position: absolute` so its existence doesn't perturb the hero. Both still need `transform-origin: 50% 50%` (the rule's central principle), and `z-index: 10` on the CTA (above hero) so the hero's fade tail doesn't bleed through.

The morph reads as **condensation** only when `ctaTotalWidth < heroGroupWidth`. Inverted, the same scale-swap reads as expansion (small thing becoming big thing) which is the wrong narrative for "brand condenses into a focused action." `CTA_MAX_REL_HERO` (0.5–0.8) is the safety rail; values above 0.8 visibly invert the illusion. Measure both widths after `document.fonts.ready` if you want this guaranteed at render time.

Inside the CTA, the inner text reveals at `MORPH_AT + 0.17s` (or `~0.3 × MORPH_ENT_DUR`) **after** the container has scaled past the early micro-frames of the `back.out`. Revealing text during the early bounce makes it pop at micro-scale and look like a glitch.

## Phase 3 Seam: Cursor Entry — Hard-Cut Opacity, Offset Landing

Two scene-specific tricks the rule doesn't spell out:

**Hard-cut opacity.** Real cursors don't fade in — they're either there or not. Implement with a near-zero-duration `fromTo`:

```js
tl.fromTo(
  "#cursor",
  { opacity: 0 },
  { opacity: 1, duration: HARD_CUT_DUR, ease: "none" },
  CURSOR_ENTER_AT,
);
```

`HARD_CUT_DUR` lives in the 0.001–0.01s range — small enough to read as instant under HF's frame-stepped seek, but non-zero so it produces an actual step change in the seekable timeline rather than a `set()` that might be missed during a reverse seek.

**Offset landing, not dead-center.** The cursor's target is the button's center **plus** a small (`±30–150 px`) offset on both axes — typically a hair right and below. Real cursors land where eye + hand coordinate, which biases slightly toward the visible mass of the button rather than its geometric midpoint. Dead-center lands too perfectly and reads as scripted.

```js
const CURSOR_TARGET_X = W / 2 + CURSOR_TARGET_OFFSET_X_PX;
const CURSOR_TARGET_Y = H / 2 + CURSOR_TARGET_OFFSET_Y_PX;
```

`W` and `H` are the composition's `data-width` / `data-height`. The starting point lives `CURSOR_OFFSCREEN_X_PX / Y_PX` beyond `W` and `H` — far enough that the spring approach reads as inbound motion, not a teleport. Path duration sits at 0.7–1.4s; faster reads as urgent, slower as deliberate.

## Phase 4 Seam: Synchronized Press via Single Target Array

The press is the only place in this blueprint where two elements must move in literal lockstep. The mechanism that guarantees that is using a single GSAP target array:

```js
tl.to(
  ["#cta", "#cursor"],
  { scale: 1 - PRESS_INTENSITY, duration: CLICK_DOWN_DUR, ease: "power3.out" },
  CLICK_DOWN_AT,
);
tl.to(["#cta", "#cursor"], { scale: 1.0, duration: CLICK_UP_DUR, ease: "power2.out" }, CLICK_UP_AT);
```

The temptation is to split this into per-element tweens with subtly different eases ("the cursor should feel slightly heavier than the button"). Don't. Any desync, even a few frames, breaks the illusion that the two are touching — the cursor floats off the button surface. One array, one ease, one duration, one start time.

By the time `CLICK_DOWN_AT` fires, the CTA's `back.out` entrance has long since settled at `scale: 1`. The press tween's `scale: 1 - PRESS_INTENSITY` overwrites cleanly via GSAP's `overwrite: "auto"`, and `scale: 1.0` overwrites back on release. No manual scale composition needed — that's only required when two tweens overlap in time, and here they don't.

## Key Values to Choose (Not Already in the Rules)

Only the parameters this blueprint introduces; for sizing ratios, eases, BOUNCE_FACTOR, PRESS_INTENSITY ranges, see the linked rules.

- **CTA_MAX_REL_HERO**: 0.5–0.8. Maximum ratio of CTA width to hero group width. Above 0.8 the morph inverts and reads as expansion — wrong narrative.
- **CURSOR_TARGET_OFFSET_X_PX / Y_PX**: ±30–150 px. Small non-zero offsets from viewport center for the cursor's landing point. Zero reads as scripted; ±200+ misses the button.
- **CURSOR_OFFSCREEN_X_PX / Y_PX**: 50–300 px beyond the composition edge. Cursor's starting position. Larger values make the approach more dramatic; too small and the cursor "pops in from the edge."
- **HARD_CUT_DUR**: 0.001–0.01s. Near-zero duration that creates a step change in opacity rather than a fade. Must be non-zero to survive frame-stepped seeking.
- **MORPH_FADE_DUR**: 25–40% of `MORPH_EXIT_DUR`. Hero's opacity fades faster than its scale shrinks, so it's gone before it lands at small scale (otherwise you see a tiny ghost-hero behind the CTA).
- **LOGO_ROT_AMP_DEG**: 2–6°. Breath rotation amplitude on the logo only. Bigger reads as a wobble; smaller is below the perception threshold.

## Critical Constraints (ordered by failure frequency)

- **`CLICK_DOWN_AT === CURSOR_ENTER_AT + CURSOR_PATH_DUR`** — exact equality, not "approximately." Bind these in code via the same expression. Any gap breaks the cursor-lands-and-clicks single-event perception.
- **Presence-dwell ≥ 1s before morph** — the most common mistake is making `MORPH_AT - (INTRO_START + INTRO_DUR)` too small. Without dwell, the hero never registers as the brand.
- **Single target array for the press** (`["#cta", "#cursor"]`, not two tweens) — desynced press = floating cursor = no contact illusion.
- **Cursor hard-cut, not fade** — a 0.4s fade-in cursor reads as a ghost; use `HARD_CUT_DUR` in the 0.001–0.01s range.
- **Breath rotation on `.hero-logo` only**, never on `#hero` — Phase 2's morph exit overwrites the hero's scale; breath on the same element would race.
- **CTA `position: absolute`** — without it, the appearing CTA shifts the hero out of flex flow at `MORPH_AT` and the morph "jumps sideways."
- **CTA z-index above hero** (`z-index: 10`) — hero's fade tail at opacity 0.3–0.5 will bleed through the popping CTA otherwise.
- **Cursor z-index above CTA** (`z-index: 100`) — during the press, the cursor must visibly sit on top of the button.
- **CTA total width < hero group width** (enforced by `CTA_MAX_REL_HERO`) — inverted ratios make the morph read as expansion, breaking the narrative.
- **Cursor landing offset from dead-center** — dead-center reads as scripted; ±30–150 px sells humanness.
- **`CLICK_UP_AT > CLICK_DOWN_AT + CLICK_DOWN_DUR`** — reversed timing inverts the press into a "lift-then-press" misplay.
- **Climax dwell ≥ 1s after release** — comps ending mid-spring rebound never feel like the press "landed."

## Spring → Ease Selection

Four distinct feels; the full mapping table lives in [hyperframes-animation/SKILL.md](../SKILL.md). This blueprint's defaults:

- Phase 1 hero entrance → `power3.out`; breath rotation → `onUpdate Math.sin`
- Phase 2 hero exit → `power3.out`; CTA pop-in → `back.out(BOUNCE_FACTOR)`
- Phase 3 cursor approach → `power2.out` (deceleration into landing)
- Phase 4 press down → `power3.out`; release → `power2.out`

## Golden Sample

- [cta-morph-press.html](../examples/cta-morph-press.html) — runnable four-phase composition on a single paused GSAP timeline. Run this before tuning values from scratch; most of the cursor-offset and dwell numbers are easier to dial in by changing constants than by deriving from text.
