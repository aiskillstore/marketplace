---
id: workflow-approve-press
role: workflow
duration_seconds: [4, 6]
phases: 4
visual_arc: headline-entry → steps-progress → video-demo → button-press-confirm
uses_rules: [press-release-spring]
element_roles:
  headline: Top concept statement with one emphasized accent word
  video_demo: Center product video / animation showing the feature
  step_indicators: Left-flank 3D-tilted step list with pending → active → complete states
  action_button: Right-flank 3D-tilted button that receives the press and changes state
when_to_use:
  - Scene emphasizes user control over an automated process
  - Multi-step workflow needs visualization (e.g. generate → review → approve)
  - Button press is the narrative climax (user confirms / approves)
  - Left-right 3D symmetry flanks a center demo
when_not_to_use:
  - Workflow has more than 3-4 steps (cannot read in a ~5s scene)
  - No user-action metaphor needed (fully automated)
  - Scene is purely informational without interaction
triggers:
  [review and approve, step-by-step workflow, user control, approve button, with-you metaphor]
---

# Workflow · Approve & Press (HyperFrames)

This is an "agency → confirmation" arc: the headline announces the verb, the demo shows what the system is doing, the step list ticks through pending → active → complete to remind the viewer "you're inside the loop," and the right-flank button takes the press as the payoff — color flips green, a checkmark stamps, the scene ends saying "you approved it." The 3D-tilted left/right flanks frame the demo like a cockpit, so the user-action feels grounded in the device.

A single paused GSAP timeline drives everything. State transitions that would be `if (frame < N)` in an imperative renderer become snap `tl.set({ attr })` toggles at concrete timeline positions, so any seek lands on a deterministic state.

## When to Use

- Feature scene that emphasizes user agency ("AI works with you, not just for you")
- The workflow can be shown in 2–3 steps; 4+ steps will not read in ~5s
- A button press serves as the narrative payoff (not a passing gesture)
- Not for: fully automated stories, pure-information scenes, or scenes whose climax is something other than a confirm

## Orchestration

Four phases. Only Phase 4 is rule-driven; everything else is inline because each is a single tween or a snap state machine — wrapping them in their own rule would be overengineering.

- **Phase 1 — headline drop**: inline. One `fromTo` with `back.out(HEADLINE_BOUNCE)`, sliding from a small negative y to 0. Keep the bounce on the editorial end (≤1.4) — a title that oscillates reads as marketing-y, not workflow-y.
- **Phase 2 — center demo scale-in**: inline. One `to` from `DEMO_ENTRY_SCALE` to `1`, eased with `power3.out`. The demo enters quietly because it is the _background_ of the scene — the steps and button are the foreground story; an overshoot here would steal focus from Phase 3.
- **Phase 3 — step indicators**: inline, split into two layers driven from the same timeline. (a) A staggered `tl.to(".step", { x: 0, opacity: 1, stagger: { each: STEP_STAGGER, from: "start" } }, STEPS_START)` slides the rows in from the left. (b) A series of `tl.set(".step-N", { attr: { "data-state": "…" } })` fires at `STEPS_START` / `STEP_ACTIVE_T2` / `STEP_ACTIVE_T3` to flip the discrete state. **CSS responds to `[data-state]`**; the timeline never animates state. See "Phase 3 seam: snap state machine" below.
- **Phase 4 — button press climax**: use [press-release-spring](../rules/press-release-spring.md) in its **"state change at release (approve / confirm pattern)" variation** — the button's terminal state is `{successColor}` + checkmark, not a return to rest. We also follow the rule's **color-shift-during-press** variation for the bg/glow transition. The press dip itself follows the rule's default linear `power1.in/out` (the rule explains why); the checkmark uses the rule's `back.out(CHECK_BOUNCE)` stamp. The rule's burst + bg-glow layers are optional embellishments and this blueprint omits them by default — the workflow's quiet, in-app aesthetic doesn't want a hero-CTA pyrotechnic moment.

The button's pre-press life — entry pop and ambient glow pulse — is also inline. Both predate the press and don't share the rule's state-continuity contract, so they live alongside the rule's tweens rather than inside the rule's scope. See "Phase 4 seam: pre-press life" below.

## Phase Timing

| Phase   | Start ≥                                     | Internal duration                        | Notes                                        |
| ------- | ------------------------------------------- | ---------------------------------------- | -------------------------------------------- |
| 1       | `0.1–0.3s` (opening beat of empty frame)    | `HEADLINE_END − HEADLINE_START`          | Headline lands fully before demo dominates   |
| 2       | `HEADLINE_END − ~0.05s` (overlap)           | `VIDEO_DUR`                              | Slight overlap on tail = flow, not cut       |
| 3a      | `VIDEO_START + ~0.15s`                      | `numSteps × STEP_STAGGER`                | First step appears as demo finishes settling |
| 3b      | `STEPS_START` (active-1), then `+readDwell` | snap (zero duration)                     | `readDwell` ≥ 1.0–1.5s between transitions   |
| 4 entry | `STEP_ACTIVE_T(last) + ~0.1s`               | `BTN_ENTRY_DUR`                          | Button pops as last step goes active         |
| 4 press | `BUTTON_ENTER + BTN_ENTRY_DUR + ~0.2s`      | `PRESS_DUR` (= `PRESS_DIP_DUR + return`) | Button must settle before press fires        |

Why the gaps are what they are. The −0.05s overlap from Phase 1 to 2 is the "two beats read as flow" trick — large enough that the demo's first frame is already visible while the headline is still settling, but not so large that the eye sees them as one event. The +0.15s gap to Phase 3 exists because the demo's `power3.out` decays to near-zero velocity, not actually zero; starting the staggered step entry on top of an unsettled scale produces faint chatter on each step's left edge. The +1.0–1.5s `readDwell` between step state changes is human-perception driven, not motion-driven: the viewer needs to actually read the active step label before it becomes complete, otherwise the state machine reads as a blink. The +0.2s gap before `PRESS_FRAME` is the most critical timing constant in the scene — the button enters with `back.out(BTN_ENTRY_BOUNCE)` and its spring tail oscillates past 1.0 for ~0.15–0.2s; firing the press on top of that residual motion makes the dip "skip" because GSAP layers velocities on the same property.

## Initial DOM Nesting

The scene's structure is "three columns around a center demo." The only non-obvious bit is where `perspective` lives:

```
#root
  .bg                 ← background gradient
  .headline-wrap      ← Phase 1 target (top center)
    .headline
      .accent         ← emphasized word
  .demo-wrap          ← Phase 2 target (center)
    .demo-frame
      <video>
  .steps-flank        ← perspective + rotateY(+FLANK_TILT_DEG) HERE
    .step[data-step][data-state]   ← Phase 3 targets (×N)
      .step-circle
        .step-num
        .step-check (svg)
      .step-label
  .button-flank       ← perspective + rotateY(-FLANK_TILT_DEG) HERE
    .btn-press        ← Phase 4 press target (scale)
      .btn            ← color/glow target; --btn-glow-blur CSS var
        .btn-check    ← Phase 4 checkmark stamp (scale)
        .btn-label
  .ambient, .vignette ← pointer-events: none overlays
```

`perspective(FLANK_PERSPECTIVE)` lives **directly on `.steps-flank` and `.button-flank`**, not on `#root`. A perspective declared far up the tree distorts depth proportions on the inner content — the steps' inner circles end up rendered at the wrong apparent depth from the camera and the tilt no longer looks symmetrical with the button side. This is the most common "why does my 3D look weird" failure in this blueprint.

The button has two transform layers because the press tween writes `scale` to `.btn-press` while the color/glow tween writes `backgroundColor` and a CSS var to `.btn`. Putting both on one element means the color tween's GPU compositing fights the scale tween — visible as a faint flicker at the press frame.

## Phase 3 Seam: Snap State Machine

Step state is **a discrete CSS attribute, never an animated property**. The timeline only flips `data-state`; CSS does all the visual mapping (border color, fill, checkmark visibility):

```
STEPS_START        → step-1: pending → active        (snap, same frame as 3a entry)
STEP_ACTIVE_T2     → step-1: active  → complete
                     step-2: pending → active        (simultaneous)
STEP_ACTIVE_T3     → step-2: active  → complete
                     step-3: pending → active        (terminal — no T4)
```

The final step intentionally has no `T(N+1)` — the press itself is the implicit completion. This is the scene's narrative point: the system did its part, you completed it.

**Do not use CSS `transition` to soften the state flip.** A `transition` interpolates on its own clock independent of HF seek, so when the renderer jumps backward (e.g. seeking to t=1.0 for a frame after rendering t=3.0), the transition replays out-of-order and the captured frame catches a half-coloured circle. Visual easing of the state change must come from a tween on the timeline, not from CSS.

The `readDwell` between `STEP_ACTIVE_T2` and `STEP_ACTIVE_T3` is the only place a viewer can register the active state of step 2. Below ~1.0s the active label is unreadable; above ~1.5s the scene starts to drag. 1.2s is the sweet spot for most copy.

## Phase 4 Seam: Pre-Press Life (Entry Pop + Pulsing Glow)

The button's entry and its ambient glow are **not** part of the press-release-spring rule — they live before its `PRESS_START` and are unique to this blueprint.

- **Entry pop** at `BUTTON_ENTER`: a single `back.out(BTN_ENTRY_BOUNCE)` tween from `scale: 0` to `1` on `.btn-press`. The bounce factor is on the firm side (1.2–1.6) because the button is announcing itself as the next interactive target. Constraint: `PRESS_FRAME ≥ BUTTON_ENTER + BTN_ENTRY_DUR + ~0.2s` so the entry spring fully settles before the press fires (see timing prose above).
- **Pulsing glow** from `BUTTON_ENTER` until scene end: drives the CSS custom property `--btn-glow-blur`, which the button's `box-shadow` declaration reads. **`boxShadow` strings are not GSAP-tweenable**, so the only practical way to animate a glow's blur radius on a timeline is via a CSS var that the shadow rule consumes. Standard pattern:

```js
const PULSE_HALVES = Math.max(2, Math.floor((SCENE_END - BUTTON_ENTER) / (PULSE_PERIOD / 2)));
tl.fromTo(
  ".btn",
  { "--btn-glow-blur": GLOW_BLUR_MIN },
  {
    "--btn-glow-blur": GLOW_BLUR_MAX,
    duration: PULSE_PERIOD / 2,
    ease: "sine.inOut",
    yoyo: true,
    repeat: PULSE_HALVES - 1,
  },
  BUTTON_ENTER,
);
```

`repeat: -1` is forbidden by the HF render contract (rendered frame count is finite and known up-front), so the repeat count is **derived from remaining scene time**. The `Math.max(2, …)` guard handles the degenerate case where the scene is so short that `BUTTON_ENTER` is near `SCENE_END` — without it, `PULSE_HALVES` could go to 0 or 1 and the yoyo wouldn't return.

## Phase 4 Seam: Press → Confirm

The press itself is the rule's "approve / confirm" variation. The seam to think about is how this blueprint's adjacent layers feed each other at three timeline positions:

```
PRESS_FRAME                : scale 1 → PRESS_SCALE       (linear  power1.out, dip)
PRESS_FRAME + PRESS_DIP_DUR: scale PRESS_SCALE → 1       (linear  power1.in,  return)
PRESS_FRAME + PRESS_DUR  ≡ CHECK_POP:
                              .btn      backgroundColor: accent → success (power2.out)
                              .btn-label textContent     snap to confirmedLabel (tl.set)
                              .btn-check scale 0 → 1     (back.out(CHECK_BOUNCE))
```

`CHECK_POP` is **derived**, not assigned independently: `CHECK_POP = PRESS_FRAME + PRESS_DUR`. Assigning it as a separate constant is the single most common refactor regression in this scene — the moment it drifts from `PRESS_FRAME + PRESS_DUR` the checkmark stamps before the button has finished returning, and the green flash arrives mid-dip. The rule's state-continuity principle covers the dip→return seam (end value of (1) = start value of (2)); the _checkmark_ seam is this blueprint's responsibility because it's the rule's "approve" variation point.

The label `textContent` swap is a `tl.set`, not a tween, because text content is non-interpolable — any "transition" would be a flicker. Snapping it at exactly `CHECK_POP` rides under the checkmark's pop and reads as a single confirmation event.

A small detail: `CHECK_BOUNCE` (1.4–2.0) is intentionally firmer than `HEADLINE_BOUNCE` (≤1.4). The headline is the scene's editorial top; the checkmark is its punctuation — a punctuation mark _should_ read as more emphatic than the title.

## Key Values to Choose (Not Already in the Rules)

Listing only parameters unique to this blueprint. For `PRESS_SCALE`, `BOUNCE_FACTOR`, `CHECK_BOUNCE`, `CHECK_POP_DUR`, the burst layer, and the bg-glow layer — see the [press-release-spring rule](../rules/press-release-spring.md).

- **FLANK_TILT_DEG**: 12–18°, left = `+`, right = `-`. Above ~20° the inner step / button content distorts unreadably; below ~10° the cockpit framing disappears and the layout reads as flat columns.
- **FLANK_PERSPECTIVE**: 600–1000 px. Smaller = stronger depth (button feels closer to camera); larger = subtler. Both flanks must share the same value or the symmetry breaks.
- **STEP_STAGGER**: 0.3–0.7s between consecutive step entries. Calibrate so all N step entries finish before `STEP_ACTIVE_T2`, otherwise step 1 starts ticking active while step 3 is still sliding in.
- **STEP_ACTIVE_T2 / STEP_ACTIVE_T3**: separated by `readDwell` of 1.0–1.5s. Drives the scene's perceptual pacing.
- **PRESS_DIP_DUR**: 0.08–0.15s, intentionally shorter than the return half. `PRESS_DIP_DUR < PRESS_DUR / 2` is the rule of thumb — the dip reads as "instant," the return as "spring."
- **PULSE_PERIOD**: 0.8–1.5s for the ambient glow. Faster reads as urgent ("press me!"), slower as confident ambient.
- **SCENE_END**: ≥ `CHECK_POP + 0.5–1.0s` dwell. A confirmed-state hold below ~0.5s reads as "flashed and gone."

## Critical Constraints (ordered by failure frequency)

- **`CHECK_POP` must be derived, never assigned**: `CHECK_POP = PRESS_FRAME + PRESS_DUR`. Drift here breaks the entire approve climax.
- **`PRESS_FRAME ≥ BUTTON_ENTER + BTN_ENTRY_DUR + ~0.2s`**: the entry spring's tail must finish before the press, or velocities layer on the same `scale` property.
- **Perspective lives on `.steps-flank` / `.button-flank`, not `#root`**: putting it on a distant ancestor distorts inner content depth and breaks left/right symmetry.
- **`.btn-press` and `.btn` are two separate layers**: scale on the outer, color/glow on the inner — combining them produces a press-frame flicker.
- **Step state is snap, no CSS `transition`**: transitions interpolate on their own clock and break under HF seek.
- **Label text swap is `tl.set`, not a tween**: text is non-interpolable.
- **Pulsing glow `repeat` is finite, derived from remaining scene time**: `repeat: -1` is forbidden.
- **Glow blur is driven via a CSS variable**: `boxShadow` strings are not GSAP-tweenable; only `--btn-glow-blur` is.
- **2–3 steps maximum**: a 4-step state machine cannot be read in a ~5s scene.
- **Video asset must out-survive the scene**: muted, long enough to cover from `VIDEO_START` through `SCENE_END` (or be a non-terminating sub-composition).

## Spring → Ease Selection

Six distinct feels live in this scene; full mapping is in [SKILL.md](../SKILL.md). This blueprint's choices:

- Phase 1 editorial drop → `back.out(HEADLINE_BOUNCE)` (low bounce, ≤1.4)
- Phase 2 cinematic ease → `power3.out`
- Phase 4 dip + return → `power1.out` then `power1.in` (mechanical, per rule)
- Phase 4 checkmark stamp → `back.out(CHECK_BOUNCE)` (firm, 1.4–2.0)

## Golden Sample

- [workflow-approve-press.html](../examples/workflow-approve-press.html) — runnable composition with concrete values for every named constant above; single paused GSAP timeline drives all four phases. Start from this and tune values; building from scratch is much slower than diffing against the sample.
