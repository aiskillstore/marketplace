---
id: proof-logo-chain
role: social-proof
duration_seconds: [6, 10]
phases: 5
visual_arc: brand-decode → text-swap → logo-centers → avatars-network → brand-logos
uses_rules: [hacker-flip-3d, vertical-spring-ticker, coordinate-target-zoom, avatar-cloud-network]
element_roles:
  anchor: Logo that threads across all shots, repositioning as the visual link
  decode_text: Brand name revealed via hacker-flip alongside the anchor
  swap_text: Replacement text sliding in after the decode (the claim phrase)
  counter: Numeric/short label appearing with the avatar cloud
  avatars: User avatars on an elliptical ring around the anchor
  endorsement_logos: Partner / brand logos scrolling at the bottom
when_to_use:
  - Brand authority via multiple progressive proof points
  - Logo threads multiple shots as the visual link
  - 3-4 distinct claims packed in one continuous sequence
when_not_to_use:
  - Single-beat scene, no progression
  - No persistent brand element available
  - Authority from a single source only
triggers: [brand reveal, social proof, "#1 tool", million users, trusted by]
---

# Proof · Logo Chain (HyperFrames)

This is a "decode → claim → community → endorsement" arc: the brand name decrypts itself next to the logo (authority asserts itself); a claim phrase slot-machines into the same row (the specific boast lands); text yields and the logo glides to dead center (it has earned the stage); avatars cascade into orbit around it with connection lines drawing outward (community materializes); partner logos quietly scroll along the bottom (third-party validation, no fanfare). The logo is the only element on screen the whole time — it is the through-line that makes four claims feel like one statement.

Single paused GSAP timeline, five phases, every adjacent pair gets ~0.2-0.4s of breathing room because four different easings (`power3.out`, `back.out`, additive springs, dash-draw `power2.out`) cannot share boundaries cleanly.

## When to Use

- Authority / credibility scene that needs to stack 3-4 distinct proof points
- A brand logo is available and should anchor viewer attention across content changes
- The composition has 6-10s to breathe — under 6s and the recenter+cloud beats collide; over 10s the closing scroll drags
- Not for: single-beat scenes, scenes without a persistent brand element, or a single-source authority (use a simpler reveal)

## Orchestration

Five phases, four rules + one inline beat. The logo (`.anchor-logo`) is shared state between every phase — it is the only element that no rule "owns" exclusively.

- **Phase 1 — brand decode**: use [hacker-flip-3d](../rules/hacker-flip-3d.md) on the brand wordmark sitting in the right slot of the anchor row. The logo pops in via a plain inline `scale: 0 → 1` tween at `t=0` and the hacker-flip runs alongside it; we picked hacker-flip rather than typing or fade because the scene is announcing _who_ — the decryption framing reads as "this brand has been identified," which is the right opening register for a proof scene.
- **Phase 2 — claim swap**: use [vertical-spring-ticker](../rules/vertical-spring-ticker.md) for the ticker word inside the claim (e.g. "#1 in {TickerWord1} ↔ {TickerWord2}"), `STEPS = 1` — a single slot-machine click is enough to communicate "the claim varies but the brand persists." Everything else in this phase is **inline**: the brand wordmark slides out, the new claim phrase fades in, the row shifts left, all three tweens at the same timeline position. See "Phase 2 Seam" — the swap glue is the core unique content of this blueprint.
- **Phase 3 — logo recenters**: use [coordinate-target-zoom](../rules/coordinate-target-zoom.md) in its **shift-only variation** — we tween only the `.zoom-inner` counter-translate, we do **not** tween `.zoom-outer.scale`. There's no zoom here, just a translate; we still want the rule's "inner translates, outer scales" wrapper structure so an optional camera scale can be added later without rewiring. The text zone fades to 0 in parallel; the logo glides on `power2.out` toward true viewport center plus a small upward lift.
- **Phase 4 — avatar cloud**: use [avatar-cloud-network](../rules/avatar-cloud-network.md). The non-trivial bit is that this rule's `CENTER_X / CENTER_Y` constants must equal the logo's post-Phase-3 position — see "Phase 3 → 4 Seam." The hub element from the rule is replaced by (or rendered on top of) the existing `.anchor-logo`; do not let the rule mount its own hub or you end up with two centerpieces.
- **Phase 5 — brand endorsement strip**: **inline**, no rule. A staggered `back.out` entry on `.brand-logo` plus a finite `ease: "none"` x-tween on the strip. This isn't a rule because it's two tweens with no orchestration; making it one would be overengineering. Critical: the scroll uses a finite `duration` — see Critical Constraints; no `repeat: -1`.

## Phase Timing

All boundaries in seconds. Pick `DECODE_END` first (it's a function of charCount × stagger), back-derive the rest from the gaps below.

| Phase | Start ≥                                | Internal duration              | Notes                                                         |
| ----- | -------------------------------------- | ------------------------------ | ------------------------------------------------------------- |
| 1     | `0`                                    | `DECODE_END`                   | Equals `(charCount−1) × CHAR_STAGGER + FLIP_DURATION`         |
| 2     | `DECODE_END + ~0.3s`                   | `SWAP_DUR` (+ claim dwell)     | Three concurrent tweens share `SWAP_DUR` & `power3.out`       |
| 3     | `SWAP_TRIGGER + SWAP_DUR + ~1.0s`      | `RECENTER_DUR`                 | The 1s is **viewer reading time** for the claim, not a buffer |
| 4     | `RECENTER_TRIGGER + RECENTER_DUR`      | hub→avatars→lines→breath chain | No extra gap — rule's own hub fade absorbs the recenter tail  |
| 5     | `LOGOS_TRIGGER` (= `dur − SCROLL_DUR`) | `SCROLL_DUR`                   | Anchored to the _end_ of the comp, not Phase 4                |

Three of the four gaps deserve commentary because they are not interchangeable.

The `+0.3s` between Phase 1 and Phase 2 is hacker-flip's _settle frames_: after the final character flips to its target glyph there is still residual `power3.out` tail on the rotateX tween. Triggering the slide-out before that tail decays produces a visible double-motion on the last character. 0.3s is the smallest gap that reads as "decoded, _then_ the next beat" rather than one continuous transition.

The `+1.0s` between Phase 2 and Phase 3 is **not a spring-settle gap** — it is reading time. The claim phrase ("#1 in X for Y") is the densest piece of copy in the scene; if the logo starts moving while the viewer is still parsing it, both motions degrade. Tune by eye against the actual claim length: short claims ("Trusted by millions") can drop to 0.7s; long claims ("The #1 enterprise-grade workflow tool for engineering teams") need 1.2-1.5s.

Phase 4 follows Phase 3 with no explicit gap because [avatar-cloud-network](../rules/avatar-cloud-network.md)'s `HUB_FADE_START` is the first beat _inside_ the rule — it acts as the gap. If you stack a manual buffer on top, the cloud feels detached from the recentering.

Phase 5's start time anchors to the **end** of the composition (`compDuration − SCROLL_DUR`), not the end of Phase 4. The viewer should still be looking at the formed avatar network when the strip enters; a strip that lands during the cloud's idle breathing is far better than one that arrives 2s after everything stops moving.

## Initial DOM Nesting

Three wrapper layers. The middle one (`.anchor-shift`) is what Phase 2 tweens for the left-shift; the inner two are what Phase 1 and Phase 3 act on. Without `.anchor-shift` as a separate node, Phase 2's row-shift would compound onto Phase 3's logo-recenter and you'd have to subtract one from the other at design time — error-prone.

```
.anchor-stage              ← flex container, place-items: center
  .anchor-shift            ← Phase 2 x-tween (row left-shift)
    .anchor-logo (z:100)   ← Phase 1 scale pop, Phase 3 x/y translate
      img                  ← {heroAsset}, drop-shadow filter
    .anchor-text           ← Phase 3 opacity fade-to-0
      .phase1-text         ← Phase 1 hacker-flip target (per-char spans)
      .phase2-claim        ← Phase 2 fade-in, positioned absolutely at phase1-text's origin
        .claim-lead / .claim-mid / .claim-ticker  ← ticker = vertical-spring-ticker mount
```

`.phase2-claim` is `position: absolute` inside `.anchor-text` so it occupies the same coordinate as `.phase1-text` — that's what makes the swap read as "in place." If it were a sibling in the same flex row, the layout would jump as the brand fades out.

`.anchor-logo` carries `z-index: 100`. It must sit above the avatars (`z:2`) and the SVG connection lines (`z:1`) that Phase 4 introduces — without this, the lines visibly cross through the logo edge instead of terminating at it.

## Phase 2 Seam: The Three-Tween Swap

This phase has no rule of its own — the vertical-spring-ticker only owns the ticker word inside the claim. The actual swap (old text out, claim in, row shifts left) is inline glue and is the most failure-prone beat in the blueprint. Three tweens fire at the same timeline position, share `SWAP_DUR`, share `power3.out`:

```js
// 1. Old brand text exits right.
tl.to(
  ".phase1-text",
  { x: SLIDE_DIST, opacity: 0, duration: SWAP_DUR * EXIT_RATIO, ease: "power3.out" },
  SWAP_TRIGGER,
);

// 2. Whole row shifts left so the new (typically shorter) claim sits centered.
tl.to(
  ".anchor-shift",
  { x: RECENTER_OFFSET, duration: SWAP_DUR, ease: "power3.out" },
  SWAP_TRIGGER,
);

// 3. Claim fades in slightly after the exit starts.
tl.fromTo(
  ".phase2-claim",
  { opacity: 0 },
  { opacity: 1, duration: SWAP_DUR * FADE_RATIO, ease: "power2.out" },
  SWAP_TRIGGER + SWAP_DUR * FADE_DELAY_RATIO,
);
```

`RECENTER_OFFSET` is **the most common point of failure in this blueprint.** Theoretical baseline:

```
RECENTER_OFFSET ≈ -(claimWidth − brandWordmarkWidth) / 2
```

But the practical value is almost always smaller in magnitude than this baseline — the logo's optical center of mass pulls the perceived row center to its side, so the geometric center isn't the visual center. **Tune by eye after fonts are loaded, then bake as a `const`.** Do not derive it from `offsetWidth` at tween time: HF seeks every frame, and sub-pixel drift between sibling renders becomes visible jitter when an optional camera scale wraps the scene.

`EXIT_RATIO` ~0.5 and `FADE_DELAY_RATIO` ~0.25 are the empirical values that produce a clean handoff. The brand text needs to be ~50% gone by the midpoint of the swap; the claim fade-in starts a quarter of the way in so there is no moment of empty row.

## Phase 3 → Phase 4 Seam: Logo Position = Cloud Center

This is the single most-likely-to-drift coordinate in the entire blueprint. Phase 3 translates the logo from its Phase-2 position to true viewport center plus a small lift; Phase 4's avatar cloud places its hub and connection lines around `(CENTER_X, CENTER_Y)`. **These two coordinates must be derived from the same source.** Two patterns work:

```js
// Pattern A — bake from layout math at author time (recommended)
const CENTER_X = compositionWidth / 2;
const CENTER_Y = compositionHeight / 2 + VERTICAL_ADJUST; // VERTICAL_ADJUST is negative
const CENTER_OFFSET = -RECENTER_OFFSET + logoHalfWidth; // Phase 3's x-tween target on .anchor-logo

// Pattern B — measure the logo's rect after Phase 3 (NOT recommended)
// Requires playing the timeline to the Phase 3 endpoint, reading getBoundingClientRect(),
// then registering the cloud rule. Fragile because HF may not have laid out fully yet.
```

`VERTICAL_ADJUST` is a small negative number (~−3% to −6% of compositionHeight). It lifts the logo above the canvas midline so the elliptical ring sits _around_ the logo with breathing room below for the partner strip; without the lift, Phase 5's strip overlaps the lower-arc avatars.

If the cloud's `CENTER_X / CENTER_Y` and the logo's destination are off by even a few pixels, the connection lines miss the logo's edge — visible as either a gap (lines terminating in empty space) or a hairline overlap. Both are immediately legible as broken; bake from one source and reuse.

## Phase 5 Seam: Anchor to End, Not to Phase 4

The brand strip starts at `LOGOS_TRIGGER = compositionDuration − SCROLL_DUR`, **not** at the end of Phase 4. Phase 4's `BREATH_DUR` is sized to fill the remaining time after lines complete; the brand strip enters on top of that idle breathing, not after it. If the strip starts after the breathing ends, there's a dead beat in the middle of the scene that reads as "is this over?"

The strip uses a finite `duration` x-tween, not `repeat: -1`. For a continuous-looking scroll, oversize the strip to ~2× viewport width and let it travel just the visible distance — the trail of unseen logos preserves the illusion of "the list continues." Direction is negative (right-to-left); positive direction reads as content arriving rather than content existing.

Per-logo stagger uses `back.out(BOUNCE_FACTOR)` with a low coefficient (1.2-1.5). The pop is subtle on purpose — partner logos are validation, not the focal beat; a firm spring here would compete with the avatar network for attention.

## Key Values to Choose (Not Already in the Rules)

Only blueprint-unique parameters listed. Standard rule parameters (`FLIP_DURATION`, `CHAR_STAGGER`, `STEP_DUR`, `AVATAR_BOUNCE`, etc.) live in their rules — go there.

- **LOGO_SIZE**: 5-12% of viewport min-dimension. Under 5% loses presence; over 12% crowds the hacker-flip wordmark in Phase 1. The logo never changes size after Phase 1's `scale: 0 → 1` pop, so this is also its final on-screen size.
- **ANCHOR_GAP**: flex gap between logo and text zone in Phases 1-2, ~15-25% of `LOGO_SIZE`. Pairs visually with the logo's optical weight; smaller gaps make the pairing feel like a single mark, larger gaps make it feel like two separate elements.
- **RECENTER_OFFSET**: tuned by eye, baked as `const`. Theoretical baseline = `-(claimWidth − brandWordmarkWidth) / 2`; practical value typically 60-80% of that magnitude. See Phase 2 Seam.
- **CENTER_OFFSET**: derived once from `compositionWidth / 2 + (−RECENTER_OFFSET) + logoHalfWidth`, baked as `const`.
- **VERTICAL_ADJUST**: −3% to −6% of compositionHeight. Equals `cloudCenterY − compositionHeight / 2` exactly — both numbers must come from the same expression.
- **SLIDE_DIST**: 100-300 px positive; how far the old brand wordmark exits to the right. Smaller than viewport width is fine — the opacity tween in the same tween hides the late frames.
- **EXIT_RATIO / FADE_RATIO / FADE_DELAY_RATIO**: 0.5 / ~0.5 / ~0.25 are the empirical defaults. Tune EXIT_RATIO down if the brand text is long (it needs more time to clear) and FADE_DELAY_RATIO up if the claim is dense (defer its arrival a little).

## Critical Constraints (ordered by failure frequency)

- **`CENTER_X / CENTER_Y` and Phase 3's logo destination derive from the same source.** Independent derivations drift by a few pixels and the connection lines visibly miss the logo edge. This is the #1 failure mode.
- **`RECENTER_OFFSET` is a baked `const`.** Per-frame derivation (e.g. `phase2.offsetWidth − phase1.offsetWidth`) drifts sub-pixels across renders → visible jitter when wrapped by any camera scale.
- **Logo z-index ≥ 100, above avatars (z:2) and lines (z:1).** Otherwise the SVG connection lines appear to pass _through_ the logo edge instead of terminating at it.
- **`.phase2-claim` is positioned absolutely at `.phase1-text`'s origin.** As a sibling it would shift the row geometry when brand opacity drops to 0 — the swap would read as "old text out, layout jumps, new text in" rather than "in-place exchange."
- **Phase 5 uses finite duration, never `repeat: -1`.** Oversize the strip if you need the visual of continuous scroll. The HF render harness will not respect infinite repeats deterministically.
- **Phase 2 reading dwell ≥ 1.0s before Phase 3.** This is the most-violated _timing_ constraint, not a value constraint — agents tend to treat it as a spring-settle buffer and shrink it. It is viewer reading time and must be tuned to the actual claim length.
- **Phase 1 logo pop is inline, not a rule.** A single `scale: 0 → 1` `back.out` tween on `.anchor-logo` at `t=0`. Promoting this to a rule reference adds noise without adding orchestration.

## Spring → Ease Selection

Four distinct feels across the five phases. Full mapping table in [hyperframes-animation/SKILL.md](../SKILL.md); this blueprint's defaults:

- Phase 1 hacker-flip — `power3.out` per char (rule's default)
- Phase 2 swap — `power3.out` on exit + shift, `power2.out` on claim fade
- Phase 3 recenter — `power2.out` (smoother than power3 here; the logo glide should feel weighty, not snapped)
- Phase 4 avatar pop — `back.out(BOUNCE)` per avatar (rule's default)
- Phase 5 partner pop — `back.out(1.2-1.5)` low coefficient; scroll is `ease: "none"`

## Golden Sample

- [proof-logo-chain.html](../examples/proof-logo-chain.html) — runnable composition with concrete values for every named constant above; single paused GSAP timeline drives all five phases. Run it first, then change values — much faster than building from scratch.
