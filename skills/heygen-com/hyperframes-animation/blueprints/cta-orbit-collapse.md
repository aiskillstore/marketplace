---
id: cta-orbit-collapse
role: cta
duration_seconds: [5, 8]
phases: 5
visual_arc: icons-orbit → cursor-click → collapse → demo-appears → demo-floats
uses_rules: [orbit-3d-entry, cursor-click-ripple, center-outward-expansion, sine-wave-loop]
element_roles:
  orbit_icons: 3D-entry icons representing categories / use-cases, orbiting the centerpiece
  center_cta: Central CTA element (input bar, button) that receives the click
  cursor: Animated cursor that moves to the CTA and clicks with ripple feedback
  demo: Product demo (video / image) that appears from the collapse point and floats
when_to_use:
  - Show product versatility (works for many categories / use-cases)
  - Icons represent different content types, genres, modes, or technology surfaces
  - User-click metaphor triggers transformation from categories → result
  - "Many options → one action → one result" narrative compression
when_not_to_use:
  - Categories have no distinct iconography (use a text list)
  - No user-action metaphor — product works automatically
  - Scene is purely informational
triggers: [works for any genre, multiple categories, click to generate, versatile tool, one click result]
---

# CTA · Orbit Collapse (HyperFrames)

This is a "scope → choice → consequence → product" emotional arc: the viewer first sees a ring of categories drifting around an empty CTA (the product handles many things), a cursor walks in and decisively clicks (the user picks one), the orbit implodes toward the click point (the choice consumes the options), and the demo springs out of that collapse point as the answer. A final breathing yoyo says "this is what you get."

One paused GSAP timeline, five phases. Phase 1 (orbit) and Phase 3 (collapse) share a single master `onUpdate` clock — they cannot be independent tweens, see Phase 1↔3 seam.

## When to Use

- Versatility scene: the product handles many categories, and you need the eye to feel that span before the pivot
- The transformation from "options" to "result" should feel **physical** — a click pulls the icons inward, not a fade
- A cursor click drives the narrative pivot (versus a zoom, a wipe, a swap)
- Total duration sits in 5–8 s; shorter and the orbit doesn't register as ambient

## Orchestration

Each phase, the rule (or `inline`) that drives it, and why this variation:

- **Phase 1 — orbit entry**: use [orbit-3d-entry](../rules/orbit-3d-entry.md) for the per-icon 3D flip-in (`back.out(ENTRY_BACK)`, mild end of the rule's range). **But the orbit motion itself is NOT taken from the rule's per-item `onUpdate`** — it's folded into the master clock in Phase 3, because the same clock must also drive the collapse. See Phase 1↔3 seam.
- **Phase 2 — cursor click**: use [cursor-click-ripple](../rules/cursor-click-ripple.md) end to end — cursor move (`back.out(CURSOR_BACK)` for a calm settle, since the click must read as deliberate not darting), depression yoyo on cursor + CTA button, and the rule's **keyframed attack-decay ripple variation** (the explicit `0 → peak → 0` envelope), because the click is the narrative climax and a linear fade reads as weak. Single ring — the orbit is already busy enough that multiple rings would muddy the moment.
- **Phase 3 — collapse**: use [center-outward-expansion](../rules/center-outward-expansion.md) in its **reversed driver form** — the rule's `progress * (target - center)` math run with progress going `0 → 1` becomes the inward path. The reversal is the only thing we keep; the rule's per-item tweens are replaced by the same master `onUpdate` that runs the orbit (see Phase 1↔3 seam). Ease: `back.out(COLLAPSE_BACK)` consumed via `gsap.parseEase` (see Phase 3 ease seam).
- **Phase 4 — demo entry**: inline single `fromTo` with `back.out(DEMO_BACK)` on `.demo` from `scale: 0` to `scale: 1`. One tween, no orchestration — making this a rule would be overengineering, same call as the brand-reveal hero pop.
- **Phase 5 — demo floats**: use [sine-wave-loop](../rules/sine-wave-loop.md) in its **simple `fromTo` + finite yoyo form** (not the multiplicative `onUpdate` form). The demo settles at exact `scale: 1` after Phase 4 (no outer-wrapper zoom is composing onto it), so a direct `y` + `rotation` yoyo is the simplest expression. If you change Phase 4 so the demo lands at a non-1 scale, switch to the rule's multiplicative form — see Phase 5 seam.

## Phase Timing

| Phase | Start ≥                                      | Internal duration                   | Notes                                                               |
| ----- | -------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------- |
| 1     | `0`                                          | `(N-1) * ENTRY_STAGGER + ENTRY_DUR` | Orbit clock starts at t=0 even before flips finish                  |
| 2     | `last-entry-finish + ~0.3s settle gap`       | `CURSOR_MOVE + decision_pause`      | Settle gap lets the orbit read as ambient before the cursor arrives |
| 3     | `CLICK_AT`                                   | `COLLAPSE_DUR`                      | Orbit and collapse share one `onUpdate` — see seam                  |
| 4     | `CLICK_AT + COLLAPSE_DUR − COLLAPSE_OVERLAP` | `DEMO_DUR`                          | **Negative gap (overlap)** — energy transfer, not a hard cut        |
| 5     | `DEMO_AT + DEMO_DUR + ~0.2s IDLE_TAIL`       | `TOTAL − IDLE_START`                | Spring tail must finish before sine takes over                      |

The Phase 1 → 2 settle gap (≥ 0.3 s after the last icon lands) is what lets the orbit read as **ambient motion** rather than "still entering" — without it, the cursor's entry overlaps the cascade and the viewer doesn't know what to look at. The Phase 2 → 3 transition has no gap by design: the click instant IS the collapse pivot. The Phase 3 → 4 step is intentionally **negative** (`COLLAPSE_OVERLAP`, 0.05–0.20 s) — the demo entry begins just before the collapse fully completes so the click reads as energy transferring into the demo, not as two separate events. The Phase 4 → 5 gap (`IDLE_TAIL`, ~0.2 s) is the same logic as every other spring→sine handoff: `back.out` decays to near-zero velocity but never literally zero, and a sine wave starting on top of that produces visible chatter.

## Initial DOM Nesting (Critical)

Each icon needs **three nested wrappers** because three independent sources write to it: the master `onUpdate` writes orbit-position to the outermost layer, the same `onUpdate` writes collapse scale/opacity to the middle layer, and the per-icon entry `fromTo` writes 3D rotation to the innermost layer. Tweening the same property on the same element from two sources is undefined behavior in GSAP, so these cannot share an element.

```
.icon-pos        ← outermost — orbit x/y (from master onUpdate)
  .icon-collapse ← middle    — collapse scale/opacity (from master onUpdate)
    .icon-entry  ← innermost — 3D flip rotateX/rotateY/z/scale/opacity (per-icon tween)
      <svg> + label
```

`perspective` is applied to `.icon-pos` (the layer that owns the orbit transform) so the inner 3D rotation has depth — without it the flip-in reads as 2D scale. The orbit's elliptical radii (`RADIUS_X`, `RADIUS_Y`) are baked into the `onUpdate` math, not into per-icon CSS.

The cursor sits at `z-index: 999` and the ripple at `z-index ≈ 6` — between the CTA card and the cursor. This ordering matters more here than in a plain `cursor-click-ripple` scene because the orbiting icons can pass in front of the CTA at any angle; without the explicit cursor z-index the cursor flickers behind icons mid-move.

## Phase 1↔3 Seam: One Master `onUpdate` for Orbit + Collapse

This is the blueprint's core glue and the single most important decision in the file. **The orbit must keep advancing while the radius shrinks** — otherwise the icons "snap" inward in a way that doesn't read as collapse. So orbit angle and collapse radius are computed in the **same** `onUpdate` that runs continuously from t=0 through the end of Phase 3:

```js
const COLLAPSE_EASE = gsap.parseEase(`back.out(${COLLAPSE_BACK})`);
const ORBIT_END = DEMO_AT; // master clock stops once icons are gone

tl.to(
  { tick: 0 },
  {
    tick: 1, // unused — this is just a clock target
    duration: ORBIT_END,
    ease: "none",
    onUpdate: () => {
      const t = tl.time();
      const collapseLinear = Math.max(0, Math.min(1, (t - CLICK_AT) / COLLAPSE_DUR));
      const collapseEased = COLLAPSE_EASE(collapseLinear); // proxy spring
      const radiusFactor = 1 - collapseEased; // 1 → 0 over Phase 3
      const collapseScale = 1 - collapseEased * COLLAPSE_SCALE_DEPTH;

      // Two-segment opacity envelope — see Opacity Knee seam below
      const o = collapseEased;
      const collapseOpacity =
        o < OPACITY_KNEE_T
          ? 1 - o * ((1 - OPACITY_KNEE) / OPACITY_KNEE_T)
          : (OPACITY_KNEE * (1 - o)) / (1 - OPACITY_KNEE_T);

      ICONS.forEach(({ sel, initialAngle, entryDelay }) => {
        const localT = Math.max(0, t - entryDelay);
        const angle = initialAngle + localT * ORBIT_SPEED;
        gsap.set(`${sel}.icon-pos`, {
          x: Math.cos(angle) * RADIUS_X * radiusFactor,
          y: Math.sin(angle) * RADIUS_Y * radiusFactor,
        });
        gsap.set(`${sel} .icon-collapse`, { scale: collapseScale, opacity: collapseOpacity });
      });
    },
  },
  0,
);
```

Three things are doing real work here and won't be obvious if you skim:

**`tl.time()`, not the proxy tween's progress.** The orbit must be a pure function of the timeline clock so HF seek lands deterministically at every frame. Using the proxy tween's `progress` would be equivalent under play but drifts under seek-after-pause.

**`gsap.parseEase` instead of a separate eased proxy tween.** A proxy tween (`tl.to(driver, { v: 1, ease: 'back.out(...)' })`) and `gsap.parseEase('back.out(...)')(progress)` produce identical values for the same progress fraction, but `parseEase` is anchored to `tl.time()` directly. A sibling proxy tween can drift from the master clock after seek, leaving the orbit and collapse out of step by a frame.

**`entryDelay` shows up in `localT`, not in a conditional `if (t < entryDelay) skip`.** Each icon's orbit phase advances from the moment that icon's entry tween fires, not from t=0 — so icons that flipped in later are at an earlier angle on the orbit when the collapse begins. This is what gives the orbit its "cascade-into-motion" feel. A naive `if` gate around the `gsap.set` produces a hard jump when each icon's gate opens.

## Phase 3 Ease Seam: Two-Segment Opacity Knee

The `[1 → OPACITY_KNEE → 0]` opacity envelope is what makes the collapse read as **energy converging** rather than pop-vanish. A linear `1 → 0` fade across the collapse duration looks like the icons are simply being deleted — fine for a transition but wrong for a click-driven implosion. The knee form keeps icons mostly opaque through `OPACITY_KNEE_T` (typically 0.7–0.9 of the collapse), then drops sharply to 0 at the end — visually, the icons stay solid as they accelerate inward and only dissolve at the moment of impact.

The two segments meet at `(OPACITY_KNEE_T, OPACITY_KNEE)`. The first segment is a line from `(0, 1)` to that point; the second is a line from there to `(1, 0)`. Both segments are computed against `collapseEased` (post-`back.out`), not `collapseLinear` — so the dissolve also gets the spring's late-stage slowdown, which makes the energy-release feel more deliberate.

## Phase 3↔4 Seam: Collapse Origin = Demo Origin (Exactly)

The demo's CSS-centering offsets must align **exactly** with the viewport-center point the icons collapse toward. The icons collapse to `(0, 0)` in `.icon-pos` translate-space, which (because of the rule's `xPercent: -50, yPercent: -50` centering) maps to the centroid of `.orbit-stage`. The demo uses `left: 50%; top: 50%` plus `xPercent: -50, yPercent: -50` (via GSAP, since the demo also takes a scale tween).

This match must be exact. The eye is extremely good at picking up a few-pixel misalignment between the collapse target and the demo entry point — it reads as a teleport rather than emergence. If `.orbit-stage` is not the full viewport (e.g. a fixed-size centered stage), the demo must live inside the same stage container, not as a sibling — otherwise their viewport-center math differs by the stage's offset.

`COLLAPSE_OVERLAP` (0.05–0.20 s) controls how much the demo entry overlaps the tail of the collapse. Too small (< 0.05) and the click reads as two disconnected events; too large (> 0.20) and the icons appear to pass _through_ the visible demo, breaking the energy-transfer illusion.

## Phase 4↔5 Seam: Why the Simple Yoyo (Not Multiplicative)

[sine-wave-loop](../rules/sine-wave-loop.md) has two implementation forms: a simple `fromTo + yoyo` and a multiplicative `onUpdate` that adds the breath onto an existing scale. We pick the simple form here because Phase 4 lands the demo at exact `scale: 1` with no outer wrapper composing onto it (unlike brand-reveal's hero, which has a `.zoom-scale` parent). The yoyo's `from` of `y: 0, rotation: 0` matches the demo's settled state at `IDLE_START`, so `sin(0) = 0` translates directly into "no jump at the seam."

The repeat count is computed to land **before** the composition ends:

```js
const halfCycles = Math.max(0, Math.floor((TOTAL - IDLE_START) / HALF_CYCLE) - 1);
```

The `-1` keeps a half-cycle of buffer — without it, you risk the last visible frame catching the demo mid-breath. HyperFrames forbids `repeat: -1`, so this finite computation is mandatory.

If you later add a scale overshoot that leaves the demo at, say, `scale: 1.05` after Phase 4 settles, switch to sine-wave-loop's multiplicative form — the simple yoyo would re-tween from `scale: 1`, undoing the overshoot.

## Key Values to Choose (Not Already in the Rules)

Only listing parameters unique to this blueprint — standard ranges (`ENTRY_DUR`, `STAGGER`, `RADIUS_X`, `BOUNCE_FACTOR`, etc.) live in the referenced rules.

- **COLLAPSE_OVERLAP** (0.05–0.20 s): the negative gap between Phase 3 and Phase 4. Tune by eye against the demo's spring overshoot — a stiffer `DEMO_BACK` wants a smaller overlap, a softer one tolerates more.
- **COLLAPSE_SCALE_DEPTH** (0.3–0.7): how far each icon shrinks during the collapse (`1 → 1 - depth`). Low values keep icons visible at the moment of impact (reads as "they were absorbed"); high values let them disappear into the click point (reads as "they were consumed"). Pick by narrative intent.
- **OPACITY_KNEE / OPACITY_KNEE_T** (knee 0.3–0.6, knee_t 0.7–0.9): the kink in the two-segment opacity envelope. A high `knee_t` with a moderate `knee` is the "energy converging then released" curve. Lower `knee_t` reads as a normal fade.
- **N (icon count)**: 4–12 is the comfort range. The `2π / N` angular spacing must leave room for the icon glyph plus label — measure the worst case (icon directly above or below CTA, where label sits closest to the CTA card).
- **CURSOR_TARGET (X, Y)**: must align with the **visual centroid of the CTA button**, not the CTA card center. A 4-pixel miss reads as missing the button.

## Critical Constraints (ordered by failure frequency)

- **Three nested wrappers per icon — never collapse them**. Tweening orbit position, collapse scale, and 3D flip on the same element produces silent GSAP last-write-wins behavior. This is the failure people hit first and stare at longest.
- **`COLLAPSE_BACK > ENTRY_BACK`**: the collapse must feel snappier than the entry, otherwise the click feels uncaused — the eye reads the cascade and the implosion as one continuous motion instead of cause-and-effect. The narrative pivot lives in this contrast.
- **Demo origin matches collapse center exactly**: see Phase 3↔4 seam. A few-pixel misalignment reads as a teleport.
- **Orbit angle is a function of `tl.time()`, not proxy tween progress**: see Phase 1↔3 seam. The proxy form drifts under HF seek.
- **One master `onUpdate` for orbit + collapse, not two tweens**: independent tweens cannot keep orbit advancing while radius shrinks. The blueprint's name (orbit-collapse) is implementing exactly this composition.
- **Orbit speed constant before and during collapse** — only radius shrinks. Slowing the orbit during collapse breaks the "snappy contraction" feel; speeding it up looks like the icons spin into a drain.
- **Cursor `z-index: 999`**: orbiting icons can pass in front of the CTA at any angle and will occlude a non-elevated cursor.
- **Ripple `z-index` between CTA and cursor** (~6): above the CTA card, below the cursor.
- **CTA button visibly depresses on click**: the press-scale tween on `.cta-button` is the causal trigger. Without it, the collapse feels uncaused even though the cursor lands on target.
- **Phase 5 simple yoyo assumes demo settles at scale 1**: if you change Phase 4's spring to leave residual scale, switch to the multiplicative form in sine-wave-loop.

## Spring → Ease Selection

Five spring-shaped beats, four `back.out` coefficients plus one sine yoyo. Full mapping table lives in [hyperframes-animation/SKILL.md](../SKILL.md); the intent-to-ease pairing here is:

- Phase 1 icon flip → `back.out(ENTRY_BACK)` (calm arrive, low end of range)
- Phase 2 cursor move → `back.out(CURSOR_BACK)` (calm settle)
- Phase 3 collapse → `back.out(COLLAPSE_BACK)` via `gsap.parseEase` (snappy — must exceed `ENTRY_BACK`)
- Phase 4 demo spring → `back.out(DEMO_BACK)` (snappy arrive with overshoot)
- Phase 5 breath → `sine.inOut` yoyo with finite repeat

## Golden Sample

- [cta-orbit-collapse.html](../examples/cta-orbit-collapse.html) — runnable 6.5-second composition with concrete values for every named constant above. Demonstrates the three-wrapper icon anatomy and the `gsap.parseEase` pattern for a spring-shaped driver consumed inside a master `onUpdate`. Run it first, then change values — much faster than building from scratch.
