---
id: problem-mockup-overwhelm
role: problem
duration_seconds: [4, 6]
phases: 4
visual_arc: mockups-appear → icons-scatter → morph-to-avatar → bubbles-overwhelm
uses_rules: [card-morph-anchor, sine-wave-loop, svg-icon-enrichment]
element_roles:
  mockups: 3 product / platform mockups establishing the familiar context
  icons: Platform / social icons scattered around mockups for density
  morph_container: Center mockup that scales down + crossfades into the avatar
  avatar: Character that represents the viewer / user
  bubbles: Task / problem text bubbles surrounding the avatar
when_to_use:
  - Frame a problem by showing familiar complexity (too many platforms / tasks)
  - Transition from "tools" to "person" — products → user experience
  - Problem should feel physically overwhelming (surrounded by tasks)
when_not_to_use:
  - Problem is abstract, can't be shown with mockups
  - No character / avatar representation needed
  - Scene should stay product-focused
triggers: [too many platforms, overwhelmed creator, complex workflow, surrounded by tasks]
---

# Problem · Mockup Overwhelm (HyperFrames)

This is a "familiar tools → person inside them → person crushed by them" arc: three product mockups assemble into something the viewer recognises, platform icons scatter in to amplify "lots of surface area," then the centre mockup collapses into the viewer's avatar and task bubbles close in from all sides. The emotional payoff is recognition followed by claustrophobia.

Single paused timeline, four phases. The non-trivial seam is Phase 3, where the rule's `width`/`height` morph is forbidden by HF and we substitute a six-tween orchestration that reads as one event.

## When to Use

- Problem-framing scene where the viewer must first see "too many tools" before seeing "the person stuck with them"
- Narrative needs a literal swap of subject (product → user) rather than a cut
- The closing beat should feel surrounded, not zoomed-into — avatar stays put while bubbles invade

## Orchestration

Four phases, three rules referenced, and one inline pattern (radial bubble entry). The rule selection here is more about _substitution_ than _application_ — the canonical morph rule asks for width/height tweens that HF forbids, so we re-cast it through GSAP transform aliases.

- **Phase 1 — mockups assemble**: inline staggered `back.out` spring-ins on `.mockup-left` / `.mockup-center` / `.mockup-right`, plus a finite [sine-wave-loop](../rules/sine-wave-loop.md) per mockup. We use the rule's **`onUpdate` multiplicative form** because each mockup's resting `scale` is set during entry (centre = 1, sides ≈ 0.86); float must compose onto that resting scale, never overwrite it (`fromTo` + yoyo would re-tween to its `from` state on every cycle and undo the entry). Amplitudes stay near the low end of the rule's range — these are background context, not headlines.
- **Phase 2 — icons scatter**: use [svg-icon-enrichment](../rules/svg-icon-enrichment.md) **only for its DOM contract** (icons as targets with `scale` / `opacity` only, positions pre-baked in CSS). We are _not_ using any of the rule's internal-parts patterns (rotation / pulse / dash-flow) — the icons here are platform logos used as density markers, not animated dials. The only motion is a staggered `back.out` entry plus the same multiplicative float as the mockups. See "Phase 2 seam" for the icon-enrichment gap.
- **Phase 3 — morph to avatar**: use [card-morph-anchor](../rules/card-morph-anchor.md) in a **non-uniform transform-alias substitution** of its canonical width/height tween. The rule's "old content fades out, container morphs, new content fades in, optional final fade reveals next-shot-anchor" pattern is intact end-to-end — but every dimension change becomes `scaleX`/`scaleY` on the container and the anchor is the avatar layer rendered underneath. See "Phase 3 seam" for the derivation and the aspect-mismatch trap.
- **Phase 4 — bubbles overwhelm**: inline radial layout (no rule — a tight one-off pattern). `BUBBLE_TASKS` array of `{label, angle}` pairs, positions baked once at script load via `Math.cos`/`sin`, then a staggered `back.out` entry on `.task-bubble`. Each bubble gets the same multiplicative-float idle as the mockups. The radial geometry is unique to this scene and not worth ruling.

## Phase Timing

Boundaries in seconds. Design pass: pick `MORPH_DUR`, then walk backwards to `MOCKUPS_APPEAR` and forwards to `BUBBLES_START` from the gap rules below.

| Phase | Start ≥                                           | Internal duration                     | Notes                                                   |
| ----- | ------------------------------------------------- | ------------------------------------- | ------------------------------------------------------- |
| 1     | `0` (or end of previous scene)                    | `MOCKUP_ENTRY_DUR + 2·STAGGER`        | Three spring-ins, last one anchors phase end            |
| 2     | `phase1_end + ~0.1s`                              | `ICON_ENTRY_DUR + (n−1)·ICON_STAGGER` | Tight stagger; cluster reads as one event               |
| 3     | `phase2_end + ICON_READ_TIME` (`~0.6–1.0s` dwell) | `MORPH_DUR`                           | Dwell required so density registers before it dissolves |
| 4     | `MORPH_TRIGGER + BUBBLES_START_FRAC · MORPH_DUR`  | bubble stagger + dwell to end         | Must start after avatar layer is fading in              |

The `~0.1s` gap between Phase 1 and 2 lets the last mockup's `back.out` overshoot rebound before icons start popping; without it the cluster reads as still-arriving when the icons land on top. The `ICON_READ_TIME` dwell (Phase 2 → 3) is the most important pacing knob in the scene: too short and "lots of platforms" never lands as a thought; too long and the morph feels like a separate scene. 0.6–1.0s is the comfortable range. The Phase 4 start is _fractional_ against `MORPH_DUR` (not a separate constant) so that as you tune `MORPH_DUR` the bubbles automatically slide with it — see Phase 3 seam for why `BUBBLES_START_FRAC > AVATAR_LAYER_IN_FRAC` is mandatory.

## Initial DOM Nesting

Two parallel layers, both kept in the DOM the entire scene; visibility is gated by opacity (seek can move time backward, conditional rendering would flicker):

```
#root
  .bg                                ← static
  .mockup-cluster                    ← Phase 1–3 (fades during morph tail)
    .mockup-left  / .mockup-right    ← Phase 1 entry + float
    .mockup-center                   ← Phase 1 entry + Phase 3 morph subject
      .mockup-center-content         ← fades during first ~40% of morph
    .platform-icon (× n)             ← Phase 2 entry + concurrent exit
  .avatar-with-bubbles               ← starts opacity:0, fades in mid-morph
    .avatar                          ← Phase 3 pop target
    .task-bubble (× 6–8)             ← Phase 4 radial entry (built at script load)
  .vignette                          ← static
```

`.mockup-center` carries z-index **above** `.avatar` (e.g. 25 > 20). The avatar only becomes visible when `.mockup-center` opacity reaches 0 — this is what sells the "one object morphing" illusion. **Use DOM order + opacity, never `z-index` tween** (see [card-morph-anchor's "don't snap z-index mid-fade"](../rules/card-morph-anchor.md#critical-constraints)).

## Phase 2 Seam: Why svg-icon-enrichment Without Internal Parts

The rule assumes the icon has named internal children (clock-hand, rec-dot, data-flow) that get the animation. Here the platform icons are flat logos — there's nothing inside to rotate or pulse. We reference the rule because its DOM/contract (each icon as a separate selector target, positions pre-baked as CSS `left`/`top`, GSAP touches only `scale` / `opacity` / `x` / `y`) is exactly what we need. The four signature motion patterns in the rule are not applied. **Flag for later**: the rule could grow a "decorative cluster" variation that documents this no-internal-parts usage; today, an agent reading the rule alone wouldn't know it covers this case.

The source blueprint also references a `shared-scene-ticker-for-multiple-sine-motions` subsection on the rule — that subsection doesn't exist. For 6–10 floating icons + 8 floating bubbles + avatar breath, the right collapse is a single `phase: { p: 0 }` tween whose `onUpdate` writes `sin(p + offset_i)` into each element. Doing it as N independent yoyos works but spends N tweens for what is one clock.

## Phase 3 Seam: Aspect-Mismatched Morph + Concurrent Exits + Avatar Handoff

This is the core of the scene and the section worth re-reading. [card-morph-anchor](../rules/card-morph-anchor.md) tweens `width` / `height` / `borderRadius` / `background` in lockstep, then crossfades old/new content, then optionally fades the container to reveal `.next-shot-anchor`. Two things change in this blueprint:

**1. The width/height tween becomes a scaleX/scaleY tween.** HyperFrames forbids tweening `width` / `height` (they cause layout reflows and are off the allowlist). The substitution:

```
MORPH_END_SCALE_X = AVATAR_DIAMETER / MOCKUP_CENTER_W
MORPH_END_SCALE_Y = AVATAR_DIAMETER / MOCKUP_CENTER_H
```

The most common mistake is to derive a single uniform `MORPH_END_SCALE = AVATAR_DIAMETER / MOCKUP_CENTER_W` and apply it to both axes. That only works if mockup and avatar share an aspect ratio — and they almost never do (mockup is a phone, ~9:16; avatar is a circle, 1:1). Uniform scale on a phone aspect → the "circle" stays an ellipse at morph end and the handoff to the round avatar pops. **Use independent `scaleX` / `scaleY`**, derived from each axis independently.

`borderRadius` tween is paint-only and allowed; tween to `"50%"` so the corner-rounding tracks the actual post-scale dimensions rather than baking a pixel value that drifts when `MOCKUP_CENTER_W` changes.

**2. The content fade-out and final-fade phases of the rule are augmented with concurrent sibling exits.** The rule fades only `.content-old` during the first portion of the morph; here we fade `.mockup-center-content` _and_ `.mockup-left` _and_ `.mockup-right` _and_ `.platform-icon` in the same window. These are three separate `tl.to(...)` calls at the same `MORPH_TRIGGER` position, sharing `power2.out`. The constraint is that exits run **concurrent with the morph**, not before (would feel premature, like the scene aborted) and not after (would feel detached, like an outro layered on the climax). `EXIT_DUR_FRAC` of 0.5 (so exits complete halfway through the morph, leaving the morph container alone for its final shape and handoff tail) reads as a clean dissolve.

**3. The `.next-shot-anchor` of the rule is `.avatar-with-bubbles`, gated by a fractional handoff.** Three derived constants must satisfy:

```
AVATAR_POP_DUR  < (1 − HANDOFF_TAIL_FRAC) · MORPH_DUR      // avatar at full scale before the handoff fade fires
AVATAR_LAYER_IN_FRAC ≈ 0.5                                  // layer opacity starts halfway through morph
BUBBLES_START_FRAC   > AVATAR_LAYER_IN_FRAC                 // avatar visible before bubbles arrive
```

The avatar pops (`scale: 0 → 1` with `back.out`) starting at `MORPH_TRIGGER` — the same instant as the morph, not after. By the time `.mockup-center` reaches `opacity: 0` at `MORPH_TRIGGER + (1 − HANDOFF_TAIL_FRAC) · MORPH_DUR`, the avatar is already at full scale underneath. Reversing this order (avatar pop _after_ mockup fade) introduces a single frame where neither object is visible — reads as a flicker.

The rule's "❗ next-shot-anchor must be pixel-identical" caveat applies: `.avatar`'s final `width × height` (a circle of `AVATAR_DIAMETER`) must match the morph container's _visually scaled_ end size (`MOCKUP_CENTER_W · MORPH_END_SCALE_X` × `MOCKUP_CENTER_H · MORPH_END_SCALE_Y`). Because both axes are derived from `AVATAR_DIAMETER`, this is automatic _if you keep both `scaleX` and `scaleY` derived_ — bake them as `const` rather than recomputing per frame.

## Key Values to Choose (Not Already in the Rules)

Standard parameters (`OLD_FADE_FRAC`, `FINAL_FADE_FRAC`, `SCALE_AMP`, `Y_AMP_PX`, `BOUNCE_FACTOR`, etc.) are in the referenced rules; pick from their ranges. Only listing what this blueprint _introduces_:

- **AVATAR_DIAMETER**: 180–280 px. Must match `.avatar`'s actual CSS dimensions exactly (see Phase 3 seam — any mismatch pops at handoff).
- **MOCKUP_CENTER_W / MOCKUP_CENTER_H**: 250–360 px wide, phone or card aspect. Constraint: `AVATAR_DIAMETER / MOCKUP_CENTER_W` and `AVATAR_DIAMETER / MOCKUP_CENTER_H` should both land in 0.3–0.8; outside that range the morph reads as either a snap or a crawl.
- **ICON_READ_TIME**: 0.6–1.0s dwell between icon entries settling and `MORPH_TRIGGER`. Below 0.6s "lots of platforms" doesn't register; above 1.0s the scene drifts.
- **BUBBLE_TASKS**: 6–8 entries, each `{label, angle}`. Angles arranged with visual closure around the centre (cardinal + ordinal directions). Labels 3–6 words — these are _labels_, not sentences.
- **BUBBLE_RADIUS**: distance from canvas centre to each bubble centre. Constraint: all bubbles must clear the safe area (≥ 60 px from canvas edges) at maximum scale; bubble width must not exceed the radial arc gap to neighbours, or adjacent bubbles overlap.
- **BUBBLES_START_FRAC**: 0.5–0.7. Must be > `AVATAR_LAYER_IN_FRAC` so the avatar is already visible when bubbles arrive (see Phase 3 seam).
- **EXIT_DUR_FRAC**: 0.4–0.6. Below 0.4 mockups/icons vanish before the morph commits; above 0.6 they linger into the avatar reveal.

## Critical Constraints (ordered by failure frequency)

- **`scaleX` and `scaleY` derived independently from `AVATAR_DIAMETER`** (see Phase 3 seam). Single uniform scale on aspect-mismatched morphs is the highest-traffic failure mode — the final shape is an ellipse, and the round avatar handoff pops.
- **`.mockup-center` z-index > `.avatar` z-index, gated by opacity** (see DOM nesting). Reversing order or snapping z-index mid-tween produces a visible flicker.
- **Concurrent exits, not sequential**: non-centre mockups and platform icons exit _during_ the morph at the same `MORPH_TRIGGER`, sharing duration ≈ `EXIT_DUR_FRAC · MORPH_DUR`. Sequential exits read as detached outros.
- **Avatar pop fires at `MORPH_TRIGGER`, not after**: must reach full scale before the morph container's handoff fade. Constraint: `AVATAR_POP_DUR < (1 − HANDOFF_TAIL_FRAC) · MORPH_DUR`.
- **`BUBBLES_START_FRAC > AVATAR_LAYER_IN_FRAC`**: bubbles must not arrive before the avatar is at least fading in, or they appear to orbit nothing.
- **Bake every derived constant**: `MORPH_END_SCALE_X`, `MORPH_END_SCALE_Y`, bubble `x` / `y` positions, `BUBBLES_START`. Per-frame recomputation drifts and `Math.random` / `Date.now` / `performance.now` are forbidden anyway.
- **6–8 bubbles**: fewer fails to convey overwhelm; more breaks the radial composition into clutter.
- **Tween only allowlisted transforms** (`x` / `y` / `scale` / `scaleX` / `scaleY` / `rotation` / `opacity`) + `borderRadius` (paint-only) + `background` (paint-only). Never `width` / `height` / `left` / `top`.
- **Idle floats are multiplicative `onUpdate`** on the mockups, icons, avatar, and bubbles — not `fromTo` + yoyo (would re-tween entry states on every cycle). For ≥ 8 simultaneous floats, consolidate into one shared phase tween.
- **`borderRadius: "50%"`** rather than a baked pixel value — keeps the final corner-rounding aspect-correct against whatever post-scale dimensions land.

## Spring → Ease Selection

Four entry feels, one morph driver, one continuous loop. The full mapping lives in [hyperframes-animation/SKILL.md](../SKILL.md); this blueprint's choices:

- Phase 1 mockup entries → `back.out(ENTRY_BOUNCE)` (subtle overshoot; 1.2–1.6)
- Phase 2 icon entries → `back.out(ICON_BOUNCE)` (snappier; 1.4–1.8 so the cluster reads as alive)
- Phase 3 morph driver → `power3.out` (no overshoot — avoid `back.out` / `elastic.out` here; per [card-morph-anchor](../rules/card-morph-anchor.md#how-to-choose-values), overshoot fights the dimensional change)
- Phase 3 avatar pop → `back.out(AVATAR_BOUNCE)` (1.2–1.6, slightly firmer than mockups so it reads as a new subject)
- Phase 4 bubble entries → `back.out(BUBBLE_BOUNCE)` (1.2–1.6)
- All idle floats → `Math.sin` via `onUpdate` (phase tween `ease: "none"` — see [sine-wave-loop](../rules/sine-wave-loop.md#critical-constraints))

## Golden Sample

- [problem-mockup-overwhelm.html](../examples/problem-mockup-overwhelm.html) — runnable 6-second composition. Three phone-shell mockups, nine scattered platform icons, aspect-mismatched morph (`MORPH_END_SCALE_X ≈ 0.69`, `MORPH_END_SCALE_Y ≈ 0.34`) into a cyan-teal avatar circle, eight task bubbles in radial layout. Single paused GSAP timeline; one shared phase tween drives every float. Open it, change `AVATAR_DIAMETER` or `MOCKUP_CENTER_W`, and watch the morph re-derive — faster than building from scratch.
