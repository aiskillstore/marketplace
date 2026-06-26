---
id: comparison-split-cards
role: comparison
duration_seconds: [4, 6]
phases: 3
visual_arc: title-entry → cards-split-enter → badges-attach
uses_rules: [split-tilt-cards, sine-wave-loop]
element_roles:
  title: Scene heading with accent keyword establishing the concept
  left_card: Left feature card with positive rotateY tilt (faces right)
  right_card: Right feature card with negative rotateY tilt (faces left)
  badges: Floating pill badges that attach near each card with supporting context
when_to_use:
  - Two complementary features shown side-by-side
  - Comparison or A/B presentation of related capabilities
  - Message is "X + Y together" (paired concepts of equal weight)
  - Need visual balance with 3D depth on both sides
when_not_to_use:
  - More than 2 items to compare (use a different layout)
  - Items are sequential, not parallel (use step indicators)
  - Cards contain interactive elements (use workflow-approve-press)
triggers: [two features, side by side, comparison, dual capabilities, paired concepts]
---

# Comparison · Split Cards (HyperFrames)

A "concept → dual proof" emotional arc: the title states the idea, then two cards arrive from opposite wings with mirrored 3D tilts so the eye reads them as equal weight, and finally a pair of pill badges land at the cards' inner edges to punctuate them. The whole scene runs on one paused GSAP timeline with a single shared scene-ticker for all idle motion, so cards and badges share one rhythm instead of competing on three independent clocks.

## When to Use

- Two paired features of equal weight, presented simultaneously rather than sequentially
- Premium "book-open" depth feel from mirrored card tilts adds value to the comparison
- Badges or short labels need to attach visually to each card, not float in empty space

## Orchestration

Three phases, two rules. The middle phase is the heaviest.

- **Phase 1 — title slide-down**: inline. A single `power3.out` opacity/`y` tween. Making this a rule would be overengineering — there's no orchestration to share. Direction is `y: -TITLE_RISE → 0` so the title drops in from above the final position; that direction matters because the cards in Phase 2 come from the _sides_, and a downward-arriving title plus side-arriving cards forms a non-conflicting T-shape of motion vectors.
- **Phase 2 — split cards entry**: use [split-tilt-cards](../rules/split-tilt-cards.md), but in a **two-layer DOM variation** the rule's template doesn't show: `.card-pos` carries the slide-in `x` and `scale` and the idle `y`; `.card-tilt` (a child) carries the static `rotationY` plus the idle rotation float. The rule's single-layer template tweens both on the same element, which works for its yoyo bob but conflicts here because Phase 2's entry `x` and Phase 3's continuous `y` would land on the same element and the sine ticker would overwrite the entry's final state. Splitting the transforms across two layers means each tween owns one alias and nothing collides. The tilts are mirrored per the rule (`+BASE_TILT` left, `-BASE_TILT` right) and shadow direction follows from the rule's tilt-shadow principle.
- **Phase 3 — badges attach**: inline `back.out(BOUNCE_FACTOR)` spring per badge. This is the **floating-badge variation** of split-tilt-cards' "Asymmetric content density" section — badges live on the stage, NOT inside the card divs, so they don't inherit the cards' `rotationY`. One inline tween per badge; making it a rule would not earn its keep.
- **Continuous (from `t = 0`) — shared scene-ticker**: use [sine-wave-loop](../rules/sine-wave-loop.md) in its **`onUpdate` form driven by `tl.time()`** (not the rule's preferred "drive a phase tween that starts at IDLE_START_TIME" form). One onUpdate writes y/rotation onto both cards and y onto both badges. The reason for choosing `tl.time()` over the rule's `phase` tween is laid out in the seam section below; the reason for one onUpdate instead of three is also there.

## Phase Timing

All boundaries in seconds. Pick each phase's internal duration first; back-derive starts from the gap constraints below.

| Phase | Start ≥                            | Internal duration | Notes                                                                   |
| ----- | ---------------------------------- | ----------------- | ----------------------------------------------------------------------- |
| 1     | `0`                                | `TITLE_DUR`       | `TITLE_AT` typically 0.1–0.3s; lower = punchier opener, higher = breath |
| 2L    | `TITLE_AT + TITLE_DUR * 0.5`       | `ENTRY_DUR`       | Intentional overlap: title's tail and cards' beginnings co-arrive       |
| 2R    | `LEFT_AT + 0.1–0.4s`               | `ENTRY_DUR`       | Small stagger; 0 reads mechanical, >0.4s fragments the pair             |
| 3L    | `RIGHT_AT + ENTRY_DUR + BADGE_GAP` | `BADGE_ENTRY_DUR` | Let `power3.out` tail settle on the cards before badges punctuate       |
| 3R    | `BADGE_LEFT_AT + 0.2–0.4s`         | `BADGE_ENTRY_DUR` | Mirror the card stagger feel                                            |
| Idle  | `0` (runs the whole composition)   | `TOTAL_DUR`       | `sin(0) = 0` ⇒ the float is invisible during entries                    |

Two gaps deserve specific reasoning.

The **Phase 1→2 overlap** is deliberate: `LEFT_AT` lands while the title is still tweening (`TITLE_AT + TITLE_DUR * 0.5 ≤ LEFT_AT < TITLE_AT + TITLE_DUR`). Read separately, "title done THEN cards" feels like two beats; read overlapped, the title's tail and the cards' wings read as one arrival. If `LEFT_AT > TITLE_AT + TITLE_DUR`, the scene develops dead air.

The **Phase 2→3 gap** (`BADGE_GAP` ≈ 0.1–0.3s) is the inverse: badges must NOT overlap the card entry. Cards use `power3.out` which decays smoothly — popping a `back.out` badge on top of a card that's still moving makes the badge's overshoot read as the card jittering. 0.1s feels continuous, 0.3s reads as deliberate punctuation. Pick higher when the scene is editorial, lower when it's snappy.

The **idle ticker starts at `t = 0`**, not at "entry end + buffer" as the rule defaults. This works only because `sin(0) = 0`: at composition start, every floating offset evaluates to zero, so the cards' `y` is 0 and the badges' `y` is 0 — meaning the entry tweens see no floating contribution to fight. By the time entries end, the sine is already mid-cycle and the float is naturally visible. The alternative (gating idle to start after entry settles) would require setting a separate idle-start time per element; running from `t = 0` shares one phase across the whole stage.

## DOM Nesting (the two-layer card)

The two-layer structure inside each card is the difference between this blueprint and the rule's single-layer template — keep it strict:

```
.cards-row                ← single perspective parent (rule's `perspective` principle)
  .card.card-left
    .card-pos             ← Phase 2 entry x, scale; idle y
      .card-tilt          ← static rotationY (+BASE_TILT); idle rotation float
        .card-image / .card-label / .card-subtitle
  .card.card-right
    .card-pos             ← Phase 2 entry x, scale; idle y
      .card-tilt          ← static rotationY (−BASE_TILT); idle rotation float
        ...
.badge.badge-left         ← stage-level, NOT inside .card (rule's badge variation)
.badge.badge-right
```

The rule's "Shadow direction must match tilt" still applies — left card's box-shadow falls right, right card's falls left. `.card-tilt` needs `transform-style: preserve-3d` because it has nested transformed children that should render in the 3D plane.

## Phase 2 Seam: Why two layers, not one

If you tween `x`, `scale`, AND `rotationY` on the same element (`.card`) — which is what the rule's template implies — then the Phase 2 entry tween and the continuous sine-ticker both want write access to that element's transform alias bucket. The entry tween animates `x: -SLIDE_DIST → 0`; the ticker writes `y: sin(t * FLOAT_Y_SPEED) * FLOAT_Y_AMP`. GSAP merges these correctly _for one frame_, but the rotation float (`rotationY: ±BASE_TILT + sin(...) * FLOAT_R_AMP`) wants the same alias the entry tween's mirrored `rotationY` would otherwise drive. Separate the concerns:

- `.card-pos` owns translation (`x` for entry, `y` for float) and `scale` (entry only). The ticker writes only `y`.
- `.card-tilt` owns `rotationY` (static + float). The ticker writes only `rotationY`.

The static tilt is set once at composition init via `gsap.set('.card-left .card-tilt', { rotationY: BASE_TILT })` and the float adds onto it inside onUpdate: `gsap.set(leftTilt, { rotationY: BASE_TILT + Math.sin(t * FLOAT_R_SPEED) * FLOAT_R_AMP })`. The `BASE_TILT` term must be re-added every frame because `gsap.set` writes absolute values, not deltas.

## Phase 3 Seam: Badge anchoring

Badges are absolutely positioned on the stage at each card's **inner edge** — the edge between the card and the gap, not the outer corner and not floating in empty viewport space. The eye must read them as belonging to their card. A rule of thumb: a badge's outer edge should overlap its card by 10–20% of badge width so it visually attaches rather than orbits.

Badges are NOT nested inside `.card-left` / `.card-right` because that would inherit `rotationY` and tilt the badge off-axis with the card — see split-tilt-cards' "Don't put badges inside the card divs" constraint. The trade-off is that the badge's `x` / `y` no longer auto-follow the card's idle float; the shared ticker handles that explicitly by writing a small `y` onto the badge.

## Idle Seam: One onUpdate, six writes

Five DOM nodes participate in the idle (two `.card-pos`, two `.card-tilt`, two `#badge-*`). The naive structure is five independent `tl.to(...{ onUpdate })` tweens, each evaluating its own sine and writing one alias. That fires five callbacks per frame, with five separate transform-write barriers.

The blueprint uses one `tl.to({ tick: 0 }, { tick: 1, duration: TOTAL_DUR, ease: 'none', onUpdate })` over the full composition. Inside the callback, read `tl.time()` once, evaluate four sines (cards-y, cards-rotation, badges-y, plus the `Math.PI` phase-opposed companions), and issue six `gsap.set` calls. The browser batches the transform writes within a single tick — measurably cheaper than five independent tweens, and conceptually the cards and badges share one clock.

The two **per-card opposition (`+ Math.PI` between left and right)** isn't optional: synchronized floating makes the pair look conveyor-belted. Opposed floating makes them feel like two living things sharing a rhythm. The badges are typically in-phase with each other (both pop in the same direction) because they read as a pair of satellites, not as another comparison axis — but opposing them is a valid stylistic choice if the scene wants extra differentiation.

The four sine frequencies are intentionally non-harmonic. `FLOAT_Y_SPEED` and `FLOAT_R_SPEED` for cards differ by ~25% so the y bob and the rotation wobble don't visibly sync into a single rocking motion. `BADGE_Y_SPEED` runs faster than the card y so badges feel like lighter satellites — heavy bodies move slowly, light bodies move faster. Tune `BADGE_Y_AMP < FLOAT_Y_AMP` for the same reason: a badge that out-bobs its card looks like a balloon escaping.

## Key Values to Choose (Not Already in the Rules)

Standard parameters (`BASE_TILT` range, `BOUNCE_FACTOR` range, `FLOAT_AMP` range, `SCALE_AMP` range) live in the referenced rules. The values unique to this blueprint:

- **TITLE_RISE** — pixels above resting position the title starts from. 24–64 px; below 24 barely reads as motion, above 64 reads as "dropped from offscreen" rather than "slid into place from just above."
- **ENTRY_SCALE** — initial scale of each card before settling to 1. 0.7–0.95. Lower combined with the side-slide reads as "popping into focus from a distance"; higher reads as a near-flat lateral slide. Couples with `SLIDE_DIST`: high slide + high entry scale reads as conveyor-belt, low slide + low entry scale reads as zoom-pop.
- **BADGE_GAP** — settle beat between cards finishing entry and badges starting (0.1–0.3s). See Phase 2→3 gap reasoning above.
- **GLOW_OPACITY** — opacity of the dual-glow ambient (0.08–0.18). Below 0.08 invisible; above 0.18 the glow competes with the card content. The two glow colors are usually the comparison's two brand accents, one centered at 30%, one at 70% — the layout's symmetry axis is at 50%, so the glows reinforce the side-identity without bleeding into each other.

## Critical Constraints (ordered by failure frequency)

- **Two layers per card (`.card-pos` outside `.card-tilt`)**: collapsing into one layer is the most common mistake. The static tilt and the rotation float both want `rotationY`; the entry `x`/`scale` and the idle `y` both want the position bucket. Two layers, two scopes. See Phase 2 seam.
- **Badges on the stage, not inside cards**: nesting badges inside `.card-*` makes them inherit the tilt and the float — they end up tilted off-axis and translated twice. Position absolutely on the stage at each card's inner edge.
- **Cards entered opposite-direction with phase-opposed float (`+ Math.PI`)**: left enters from `-x`, right from `+x`; left floats sin(t), right floats sin(t + π). Same direction or same phase makes the pair look mechanical.
- **`BADGE_GAP ≥ 0.1s` between card entry end and badge entry start**: badges popping while cards are still settling reads as card jitter, not badge bounce.
- **Sine ticker runs continuously from `t = 0`, not gated**: the invariant `sin(0) = 0` is what makes this safe — gating to start after entry would require per-element start times and lose the shared phase.
- **`BADGE_Y_AMP ≤ FLOAT_Y_AMP`**: a badge that out-bobs its card looks like a runaway accessory.
- **Equal card width + shared single `perspective` parent**: per-card perspective produces inconsistent depth, and unequal widths break the comparison symmetry that the whole layout is selling.
- **Idle ticker writes only one alias per element**: `y` on `.card-pos`, `rotationY` on `.card-tilt`, `y` on badges. Mixing in `scale` or `opacity` inside the ticker would overwrite the entry's final state.

## Spring → Ease Selection

Three different feels across the three phases — full mapping table lives in [hyperframes-animation/SKILL.md](../SKILL.md).

- Phase 1 title settle → `power3.out`
- Phase 2 card entries → `power3.out` (consistency: the scene's "arriving" feel)
- Phase 3 badge pops → `back.out(BOUNCE_FACTOR)` (the only spring with overshoot — earns the punctuation)
- Continuous idle → `Math.sin(tl.time() * …)` in onUpdate, ticker tween uses `ease: 'none'`

## Golden Sample

- [comparison-split-cards.html](../examples/comparison-split-cards.html) — runnable composition with concrete values for every constant above. Single paused GSAP timeline drives all three phases over `TOTAL_DUR` seconds, with the shared scene-ticker handling cards-and-badges floating. Start here, then change values.
