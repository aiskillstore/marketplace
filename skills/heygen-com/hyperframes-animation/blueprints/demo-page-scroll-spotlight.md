---
id: demo-page-scroll-spotlight
role: demo
duration_seconds: [5, 9]
phases: 4
visual_arc: page-entry → scroll-to-feature → keyword-highlight → pop-out-emphasis
uses_rules: [3d-page-scroll, asr-keyword-glow]
element_roles:
  page_card: Full webpage recreation rendered as a tilted 3D card
  scroll_content: Page content that scrolls within the clipped card
  highlight_elements: Specific page elements that glow and scale when mentioned in voiceover
  spotlight: Radial gradient overlay that dims non-highlighted areas
when_to_use:
  - Demonstrate a specific feature within its natural UI context
  - Voiceover names features that should highlight in sync
  - Show the product "in action" without a screen recording
  - 3D perspective adds premium feel
when_not_to_use:
  - Product has no webpage or UI to recreate
  - Feature is best shown via actual screen recording
  - Scene only needs a single static product image
triggers: [show the feature, product demo, highlight on page, webpage in 3D, scroll to feature]
---

# Demo · Page Scroll Spotlight (HyperFrames)

A "this is the product, this is the part that matters" arc: the tilted page coasts in like a held-up phone, voiceover names a couple of features and those words flare on the header, then the page rolls upward to reveal the section being demoed, and one element finally lifts off the surface to claim the climax. Premium-demo register — never cuts, never screen-records.

One paused GSAP timeline drives all four phases. Phases 3 and 4 overlap on purpose; everything else has a small breath of buffer.

## When to Use

- Feature demo where voiceover walks through capabilities by name and the headline words should react
- Product has a real DOM-rendered webpage component (a screenshot cannot be highlighted element-by-element)
- The demo should feel premium (3D depth + spotlight) rather than flat (a captured recording)
- Skip if no headline keywords need to glow (use plain `3d-page-scroll` instead) or if only one static product shot is needed

## Orchestration

Four phases, two rules plus two small inline patterns. The rules carry the bulk; the seams between them are the work.

- **Phase 1 — page card entry**: inline. The [3d-page-scroll](../rules/3d-page-scroll.md) rule starts the card already on screen — it doesn't speak to how the card arrives. We add a single `scale: CARD_ENTRY_FROM_SCALE → 1.0` with `power2.out` on `.page-card`, plus staggered `opacity` fade-ins on navbar / title / CTA. Critical: the card's static tilt is **already baked in by `gsap.set()`** before the entry tween starts — see "Phase 1 Seam" below. A spring (`back.out`) here would look like a pop-up modal, not a phone held up to the camera, so `power2.out` is the only correct ease.
- **Phase 2 — keyword glow on header**: use [asr-keyword-glow](../rules/asr-keyword-glow.md) in its **karaoke variation** (the rest of the headline stays dim, attacked words pop bright). Default subtle glow reads as ambient on top of the tilted page and gets lost; karaoke gives the words enough contrast to feel narrated. We diverge from the rule on one mechanical point: each word's envelope is driven by **two `tl.fromTo`/`tl.to` tweens on a CSS variable `--glow`** instead of the rule's single-driver `onUpdate` over all words. See "Phase 2 Seam" for why.
- **Phase 3 — scroll to the feature section**: use [3d-page-scroll](../rules/3d-page-scroll.md) — the rule's main payload. One thing to override from the rule's default: ease is **`power2.inOut`**, not `power3.out`. Reason in this scene: the scroll is symmetrical — it has to start gently (we're already at a held-up frame, a hard onset reads as a jump cut) and decelerate symmetrically into where the pop will happen. The rule's `power3.out` is right when scroll is the climax; here the pop is the climax, so the scroll has to be a transit not a landing.
- **Phase 4 — pop-out + spotlight**: inline, but re-uses the **`--glow` CSS variable mechanic from asr-keyword-glow**, repurposed for a non-text element. A pair of attack + decay tweens drive `.pop-target { --glow: 0 → 1 → POP_REST_LEVEL }`; CSS `calc()` on that same element derives `translateZ` and `scale` from `--glow`, and a parallel `opacity` tween on `.spotlight` dims the surrounding card. This is the climax — one tween-pair per visual effect would split the source of truth across three timeline calls; one `--glow` driving everything via `calc()` keeps it monotonic and audit-able. See "Phase 4 Seam".

## Phase Timing

All seconds, local to the scene.

| Phase | Start ≥                                              | Internal duration                | Notes                                                          |
| ----- | ---------------------------------------------------- | -------------------------------- | -------------------------------------------------------------- |
| 1     | `0`                                                  | `CARD_ENTRY_DUR`                 | Card scale + element fades; staggered offsets within           |
| 2     | First keyword's ASR `start` (≥ Phase 1 end + ~0.1s)  | per-word ASR windows             | First glow attack starts ~0.1s after title fade finishes       |
| 3     | Last keyword attack end + ~0.2s                      | `SCROLL_DUR`                     | Lets the last karaoke peak read before the page starts moving  |
| 4     | `SCROLL_AT + SCROLL_DUR * 0.6` (intentional overlap) | `POP_ATTACK_DUR + POP_DECAY_DUR` | Pop attacks **during** the scroll's tail — eye-leading handoff |

Three of these gaps deserve a word each. Phase 1 → 2: ~0.1s after `TITLE_FADE_AT + TITLE_FADE_DUR` so the title is fully readable before the first word flares — start the glow on top of a still-rising opacity and the eye reads it as a fade-in artifact, not narrator emphasis. Phase 2 → 3: ~0.2s after the **last word's attack peak** (not its release end — karaoke rest is the held state and stays through the scroll, which is exactly the breadcrumb-trail effect we want). Phase 3 → 4: the pop **deliberately overlaps** the scroll's last ~40%. The rule normally puts pop-equivalent motions after a scroll lands; here we want the viewer's eye to be drawn to where the scroll _is going to land_ before it arrives, so the pop attacks while the scroll is still moving. This is the only intentional overlap in the scene.

## Initial DOM Nesting

The `transform-style: preserve-3d` chain is the only structural constraint, and it's already in the [3d-page-scroll](../rules/3d-page-scroll.md) rule. The one twist this blueprint adds: the pop target sits **inside `.scroll-content`**, not as a sibling — it has to translate with the page when Phase 3 scrolls, then independently translateZ when Phase 4 fires.

```
.perspective-wrap          ← perspective set here
  .page-card               ← static tilt via gsap.set(); transform-style: preserve-3d; overflow: hidden
    .scroll-content        ← Phase 3 tweens this element's y
      .page-navbar         ← Phase 1 fade
      .page-hero
        .hero-title
          .kw[data-glow-start data-glow-end] ← Phase 2 targets (one per glowable word)
      .page-features
      .page-carousel
        .pop-target        ← Phase 4 target; transform-style: preserve-3d required HERE too
    .spotlight             ← Phase 4 opacity fade; SIBLING to .scroll-content, NOT child
```

`.spotlight` must be a sibling of `.scroll-content` (not a child) — otherwise Phase 3's scroll translates the spotlight out of the card along with the content, and it dims the wrong region. Same `transform-style: preserve-3d` chain must reach `.pop-target` — `.page-card` sets it, but if any intermediate wrapper resets `transform-style`, `.pop-target`'s translateZ flattens to zero.

## Phase 1 Seam: Tilt Set via gsap.set(), Not CSS

The [3d-page-scroll](../rules/3d-page-scroll.md) rule's CSS sets tilt declaratively. That works only when no other tween touches `.page-card`'s transform. In **this** blueprint Phase 1 tweens `.page-card { scale: ... → 1.0 }`, and GSAP's scale tween overwrites the full transform matrix — declared CSS rotation goes with it, and the card lands flat. Fix: own the entire transform in GSAP:

```js
gsap.set(".page-card", {
  rotateY: CARD_TILT_Y,
  rotateX: CARD_TILT_X,
  scale: CARD_ENTRY_FROM_SCALE,
});
tl.to(".page-card", { scale: 1.0, duration: CARD_ENTRY_DUR, ease: "power2.out" }, 0);
```

GSAP composes subsequent `scale` tweens against the rotation it owns, so the tilt survives. Removing the `gsap.set()` and putting the rotation back in CSS is the single most common Phase 1 failure mode.

`CARD_TILT_Y` and `CARD_TILT_X` are **set once** here. Do not animate them in any later phase — the page is a camera setup, not a flip card. A tweened tilt makes the demo read as a UI animation rather than a held-up product.

## Phase 2 Seam: Two-Tween Envelope per Word, Not Single Driver

The [asr-keyword-glow](../rules/asr-keyword-glow.md) rule recommends a single driver tween with an `onUpdate` callback iterating every word. That pattern is correct when the per-word envelope is purely runtime-derived; we use a two-tween variant here:

```js
document.querySelectorAll(".kw").forEach((kw) => {
  const start = +kw.dataset.glowStart;
  const end = +kw.dataset.glowEnd;
  const peak = start + (end - start) / 2;
  const restAt = end + KEYWORD_SUSTAIN;
  tl.fromTo(
    kw,
    { "--glow": 0 },
    { "--glow": 1, duration: peak - start, ease: "power2.out" },
    start,
  );
  tl.to(kw, { "--glow": KEYWORD_REST_LEVEL, duration: restAt - peak, ease: "power2.out" }, peak);
});
```

Two reasons for the divergence. First, the glow timestamps live in DOM (`data-glow-start` / `data-glow-end`) rather than in a JS `TIMINGS` object — easier for the upstream script-to-DOM step to populate per-word and easier to audit by inspecting the page. Second, the climax pop in Phase 4 uses the **same** `--glow` CSS-variable mechanism, so keeping Phase 2 on `--glow` tweens means the whole scene shares one variable-driven mental model. The trade-off is more tweens on the timeline; with 4–8 keywords it's still well under the rule's "60+ words gets unwieldy" threshold.

Flagged rule gap: `asr-keyword-glow` documents the single-driver `onUpdate` pattern only. The `--glow` CSS-variable variant used here is not covered by the rule; we treat it as the rule's "karaoke" payload re-expressed on a CSS variable.

## Phase 3 Seam: SCROLL_DISTANCE Comes From the Page, Not From a Range

`SCROLL_DISTANCE` is not a tunable — it's a **measured geometric fact** of the page layout. The target is the vertical center of `.page-carousel` (where `.pop-target` lives) landing at roughly 60–70% of the card's visible height (the position where the spotlight's gradient ellipse is centered — see Phase 4). Measure with a one-off `getBoundingClientRect()` at design time, bake the result as `const SCROLL_DISTANCE = …`, never recompute.

Why bake: at the 3D tilt the card uses, sub-pixel scroll drift looks like a vibration, not a scroll — every `Math.random`-free deterministic system has to land on the same pixel every play.

The rule's default ease for this property is `power3.out`. We override to **`power2.inOut`** here for the reason in Orchestration: the scroll isn't the climax. Keep the same ease across this single scroll — no second scroll in this blueprint, so the rule's "same ease across multi-phase scroll" caveat doesn't apply.

## Phase 4 Seam: One Variable, Three Visual Effects

`.pop-target` carries a CSS variable `--glow` (initial value 0). Three CSS effects all key off it:

```css
.pop-target {
  --glow: 0;
  transform-style: preserve-3d;
  transform:
    translateZ(calc(var(--glow) * var(--pop-translate-z)))
    scale(calc(1 + var(--glow) * var(--pop-scale-boost)));
  box-shadow:
    0 0 calc(var(--glow) * 25px) {accentColorRgba},
    0 calc(20px + var(--glow) * 40px) 60px rgba(0, 0, 0, 0.6);
  border: 3px solid {accentColorBorderRgba};
}
```

GSAP only tweens `--glow`; CSS does the derivation. Two tweens shape the envelope — attack to 1, decay to `POP_REST_LEVEL`:

```js
tl.fromTo(
  ".pop-target",
  { "--glow": 0 },
  { "--glow": 1, duration: POP_ATTACK_DUR, ease: "power2.out" },
  POP_AT,
);
tl.to(
  ".pop-target",
  { "--glow": POP_REST_LEVEL, duration: POP_DECAY_DUR, ease: "power2.out" },
  POP_END - POP_DECAY_DUR,
);
tl.to(".spotlight", { opacity: 1, duration: SPOTLIGHT_FADE_DUR, ease: "power2.out" }, POP_AT);
```

The single-variable-many-effects pattern matters here because three separate tweens (one each for `translateZ`, `scale`, `box-shadow`) all racing the same window create round-off skew across CSS engines; one tween on a value the CSS reads through `calc()` is bit-exact across frames.

`POP_REST_LEVEL` is intentionally higher than `KEYWORD_REST_LEVEL` (0.3–0.7 vs 0.1–0.3) — the pop target stays in focus for the rest of the scene, whereas keywords are a breadcrumb. Letting the pop decay all the way back to `--glow: 0` looks like the climax got walked back.

The spotlight gradient is centered roughly at the same screen position the pop target lands at after Phase 3's scroll — typically `40% 60%` of the card. If you change `SCROLL_DISTANCE`, also re-center the `radial-gradient(... at X% Y% ...)` to match, otherwise the spotlight illuminates an empty region of the page.

## Key Values to Choose (Not Already in the Rules)

Only parameters unique to this blueprint; for the standard ranges of `MAX_BLUR`, `MAX_SCALE_BOOST`, `REST_LEVEL`, `SCROLL_DUR`, `tiltYDeg`, etc., go to the linked rules.

- **CARD_ENTRY_FROM_SCALE**: 0.90–0.98. Lower reads as a punchier zoom-in; higher as a gentle settle. Must be < 1.0.
- **CARD_ENTRY_DUR**: 0.6–1.2s. Shorter feels tech-y; longer feels cinematic.
- **NAVBAR_FADE_AT / TITLE_FADE_AT / CTA_FADE_AT**: strict ordering `0 ≤ NAVBAR_FADE_AT < TITLE_FADE_AT < CTA_FADE_AT < SCROLL_AT`, with ~0.15–0.35s stagger between each. Reads as "page settles into focus" rather than "everything lands at once."
- **KEYWORD_SUSTAIN**: 0.3–0.8s. Seconds after each word's ASR `end` before its decay completes. Tune by checking that the last-spoken word is still readably bright when the next word peaks.
- **POP_AT**: must satisfy `POP_AT < SCROLL_AT + SCROLL_DUR` — intentional overlap with the scroll tail.
- **POP_ATTACK_DUR**: 0.4–0.9s. The pop reads as deliberate at the long end, snappy at the short end.
- **POP_END**: must satisfy `POP_END ≤ data-duration` and `POP_END > POP_AT + POP_ATTACK_DUR`. Leave ≥0.8s after `POP_END` for visual dwell on the lit pop target — same "climax dwell" reasoning the keyword-glow rule names.
- **POP_DECAY_DUR**: 0.2–0.6s.
- **POP_REST_LEVEL**: 0.3–0.7. Higher than `KEYWORD_REST_LEVEL` because the pop target holds the frame.
- **POP_TRANSLATE_Z**: 40–120px peak Z translation. Above ~100 starts to feel like the element is detaching from the card.
- **POP_SCALE_BOOST**: 0.05–0.25 additive scale.
- **SPOTLIGHT_FADE_DUR**: 0.3–0.7s.

## Critical Constraints (ordered by failure frequency)

- **Tilt set via `gsap.set()`, not CSS** (see Phase 1 Seam). The scale tween in Phase 1 erases CSS-declared rotation — this is the single highest-frequency bug in this blueprint.
- **`SCROLL_DISTANCE` is measured, not tuned**: derive from the actual page geometry at design time, bake as `const`. Don't compute per-frame from `getBoundingClientRect()`.
- **Spotlight gradient center matches `.pop-target` post-scroll position**: change `SCROLL_DISTANCE` ⇒ re-center the gradient. Mismatch leaves the spotlight illuminating empty page.
- **`.spotlight` is a sibling of `.scroll-content`, not a child**: otherwise Phase 3 scrolls the spotlight out of the card with the content.
- **`transform-style: preserve-3d` continues onto `.pop-target`**: any intermediate wrapper that resets it flattens the Phase 4 translateZ to zero.
- **Pop overlap is intentional, not a bug**: `POP_AT < SCROLL_AT + SCROLL_DUR`. If a future review pulls `POP_AT` past the scroll end "to be safe," the eye-leading handoff is lost.
- **Page must be DOM, not a screenshot**: screenshots can't be element-highlighted (the rule already states this; restating because a tempting shortcut is to drop in a static image of the page).
- **Shadow X-offset sign matches tilt sign** (the [3d-page-scroll](../rules/3d-page-scroll.md) rule's principle). Negative tilt-Y ⇒ positive shadow X-offset.

## Spring → Ease Selection

Four eases, four feels. Full mapping table lives in [hyperframes-animation/SKILL.md](../SKILL.md); the picks for this blueprint:

- Phase 1 entry / fades → `power2.out` (settling)
- Phase 2 glow attack & decay → `power2.out` (fast onset, slow settle)
- Phase 3 scroll → `power2.inOut` (symmetrical transit, **not** `power3.out` — see Orchestration)
- Phase 4 pop attack & decay → `power2.out`

## Golden Sample

- [demo-page-scroll-spotlight.html](../examples/demo-page-scroll-spotlight.html) — 4-phase, ~9-second scene with concrete values for every named constant above. Run this first, then change values — much faster than building from scratch.
