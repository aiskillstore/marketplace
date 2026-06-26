---
id: messaging-multi-phrase
role: messaging
duration_seconds: [7, 8]
phases: 3
visual_arc: phrase-type → phrase-type → phrase-type (hard-cut between)
uses_rules: [dynamic-content-sequencing, context-sensitive-cursor]
element_roles:
  main_text: Contextual lead-in portion of each phrase, typed in primary color
  accent_text: Emphatic / highlighted portion, typed in accent color immediately after main
  cursor: Blinking cursor whose color reflects the active text segment
when_to_use:
  - Multiple text phrases displayed sequentially with typing rhythm
  - Each phrase has a dual-tone structure (neutral lead-in + colored emphasis)
  - Scene is purely text-driven, no visual hero
  - Phrase content varies in length, needs proportional screen time
  - "Statement after statement" cadence for layered messaging
when_not_to_use:
  - Text coexists with a visual hero — see brand-reveal-assemble-zoom or takeover-ticker-displace
  - Phrases should cross-dissolve, not hard-cut
  - Single phrase only — use [context-sensitive-cursor](../rules/context-sensitive-cursor.md) alone
  - Need camera movement / zoom between phrases — see concept-demo-decode-pan
triggers: [multiple phrases typing, sequential statements, typing with highlight, text carousel, dual-color text, rhythmic messaging]
---

# Messaging · Multi-Phrase (HyperFrames)

A "statement, then statement, then statement" arc: each phrase types itself out from a neutral lead-in into a colored emphasis word, holds long enough that the eye can park on the keyword, then hard-cuts to the next. The viewer's rhythm is reset every cut — there is no momentum carried across phrases, on purpose. The only continuous thread is the blinking cursor, whose color silently swaps as the typing crosses into the accent segment.

The whole thing runs on a single paused GSAP "clock" tween with one `onUpdate` — phrase content, character count, cursor color, and blink are all pure functions of `tl.time()`.

## When to Use

- Scene delivers multiple messaging beats through text alone (no visual hero)
- Each beat has a neutral lead-in followed by an emphasized keyword
- Content length varies between phrases and timing should adapt automatically
- Hard-cut cadence is part of the design — phrases do not cross-dissolve
- Not for: text + visual hero, single phrase scenes, or rhythms with camera movement

## Orchestration

Two rules compose here, but they don't run side-by-side — they collapse into a single `onUpdate` because all of their state is a function of the same `tl.time()`. The split is conceptual, not architectural:

- **Phase scheduling** uses [dynamic-content-sequencing](../rules/dynamic-content-sequencing.md), but in a **per-character-typing variation** the rule itself only hints at. The rule's standard form swaps each entry's content as a block (set `title` / `body` `textContent` on entry transition); we instead derive a `charIdx` _inside_ the active entry and progressively reveal `textMain` then `textAccent`. The `TIMELINE` pre-compute is exactly the rule's `start[i] = sum of durations 0..i-1` pattern; the per-entry duration formula changes from "`BASE + length * SEC_PER_CHAR + hold`" to "`(mainLen + accentLen) * charSpeed + hold`" — there is no `BASE_DURATION` floor because every phrase has enough characters that the charSpeed floor is meaningful. See "Phase 1→N Seam".
- **Cursor styling** uses [context-sensitive-cursor](../rules/context-sensitive-cursor.md), but with **two crucial deviations from the rule's `SEQUENCE` form**. First, segments aren't authored as discrete `{t, segment, color}` entries — they're derived from the typing progress within the active phrase (`charIdx >= mainLen` → accent segment). Second, the blink is a **modulo square wave** (`(t % BLINK_CYCLE) < BLINK_CYCLE / 2`), not the rule's sin-sweep with `BLINK_CYCLES_PER_SCENE`. The modulo form is decoupled from `TOTAL` — the period is a pure constant, so changes to `TOTAL` (e.g. adding a phrase) don't shift the blink phase. See "Phase 1→N Seam" again for why color comes from typing progress, not from a label.

There is no third "rule" for the inter-phrase hard-cut, because hard-cut means _no animation_ — when `TIMELINE.find` returns the next entry, the next `onUpdate` frame simply writes the new phrase's first character into the same DOM nodes.

## Phase Timing

Phase boundaries are **content-driven** — `TIMELINE[i].endTime` is computed from `(mainLen + accentLen) * charSpeed + hold`, not authored. Every phrase shares one `charSpeed` so the typing rhythm reads as one engine; what varies is total character count and the per-phrase `hold`.

| Phase  | Start ≥                          | Internal duration                                  | Notes                                          |
| ------ | -------------------------------- | -------------------------------------------------- | ---------------------------------------------- |
| 1      | `0`                              | `(main1Len + accent1Len) * charSpeed + HOLD_MID`   | First phrase. `startTime = 0`, no lead-in beat |
| 2..N-1 | `TIMELINE[i-1].endTime` (no gap) | `(mainNLen + accentNLen) * charSpeed + HOLD_MID`   | Hard cut. Zero buffer — see seam               |
| N      | `TIMELINE[N-2].endTime`          | `(mainNLen + accentNLen) * charSpeed + HOLD_FINAL` | Closing beat uses `HOLD_FINAL > HOLD_MID`      |

The most important number in the table is the **zero gap between phrases**. Unlike spring-driven blueprints (brand-reveal, etc.) which need a 0.06–0.3s breath to let `back.out` overshoot decay, this blueprint's only "tween" is a linear clock — there is no spring tail to settle. Adding a gap would just produce a dead frame where `TIMELINE.find` returns `undefined` and the fallback empties the DOM, then on the next frame the new phrase pops in — visually that reads as a "blink to empty, then text appears" stutter. Phase boundaries land exactly on `endTime`, and the next frame's `find` immediately returns the next entry.

`HOLD_MID` is the dwell after the accent finishes typing and before the cut. The eye needs about half a second to lock onto the accent word; less than that and the cut feels rushed, more than ~1.5s and the rhythm stalls. `HOLD_FINAL` extends only on the last phrase — it's the "this is the closing statement" beat, typically 1.5–3s. Ranges live in the [dynamic-content-sequencing](../rules/dynamic-content-sequencing.md) rule's How to Choose Values; the constraint unique to this blueprint is that **`charSpeed` is shared across all phrases** (otherwise the rhythm reads as multiple engines, not one).

## Phase 1→N Seam: Per-Char Typing Inside a Sequencer Entry

This is the core deviation from `dynamic-content-sequencing`. The rule renders each entry as a block content swap on transition (`if (entry.title !== lastTitle) titleEl.textContent = entry.title`). Here the entry transition still happens, but _within_ an entry there is also per-frame character reveal. The math is:

```js
const activeT = t - phrase.startTime; // seconds into this phrase
const charIdx = Math.floor(activeT / charSpeed); // how many chars typed so far
const mainLen = phrase.textMain.length;
const visMain = phrase.textMain.slice(0, Math.min(charIdx, mainLen));
const accentLen = Math.max(0, charIdx - mainLen);
const visAccent = phrase.textAccent.slice(0, accentLen);
```

`Math.floor` is mandatory: `slice` accepts float indices and returns the truncated string with no error, but renders fractional-character widths that flicker frame-to-frame. The `Math.min(charIdx, mainLen)` clamp is what makes the main segment "fill up" before the accent starts — without it, both segments would grow in parallel from `slice(0, charIdx)` and the dual-tone effect collapses.

**The cursor color derives from these two visible lengths, not from a `SEQUENCE` label.** The rule's authored `{segment: "brand", color: "{brandColor}"}` form doesn't fit here because we don't know ahead of time at what `t` value the accent starts — `mainLen * charSpeed` varies per phrase. The derivation is one line:

```js
const inAccent = visMain.length === mainLen && visAccent.length > 0;
cursorEl.style.background = inAccent ? ACCENT_COLOR : MAIN_COLOR;
```

`visMain.length === mainLen` (not `charIdx >= mainLen`) is deliberate — when typing is mid-main, `visMain.length` equals `charIdx`, but once typing crosses into accent, `visMain` caps at `mainLen`. The second condition `visAccent.length > 0` guards the exact boundary frame: when `charIdx` first hits `mainLen`, both `visMain` and `visAccent` are "complete-main, empty-accent" for one frame — the cursor should stay on `MAIN_COLOR` until the first accent character actually appears. Drop that guard and the cursor flashes accent color for one frame on an empty accent segment, which reads as a glitch.

## Phase 1→N Seam: Blink Decoupling

The cursor blink uses `cursorEl.style.opacity = (t % BLINK_CYCLE) < BLINK_CYCLE / 2 ? "1" : "0"` — a pure square wave on `tl.time()`. This is _not_ the rule's sin-sweep form, and the difference matters: the rule's `BLINK_CYCLES_PER_SCENE` ties the blink period to `DURATION`, which is fine when `DURATION` is fixed but fragile here because `TOTAL` is content-derived. Add a phrase and `TOTAL` grows; with the sin-sweep form, `BLINK_CYCLES_PER_SCENE` must be re-tuned to keep the period in the 0.6–1.2s readability window. The modulo form makes `BLINK_CYCLE` an absolute constant — period is invariant under script changes.

The blink runs continuously, including during the pre-first-phrase and post-last-phrase fallback windows where text is empty. This is intentional: a non-blinking cursor reads as "process frozen," a blinking cursor reads as "waiting for input."

## Layout

A centered flex row with three inline spans (`.phrase-main`, `.phrase-accent`, `.phrase-cursor`). No fixed-width container — each phrase fully replaces the previous, so the flex re-centers cleanly at every cut. This is the one place where the layout differs from [context-sensitive-cursor](../rules/context-sensitive-cursor.md)'s `min-width: 1200px` terminal pattern: the cursor rule shows a single growing line where the cursor must stay at a stable x-position, while here every phrase has its own length and re-centering is the desired behavior.

`white-space: pre` is non-negotiable when `textMain` ends with a space (e.g. `"Build video with "`) — collapse the trailing space and the accent visually butts against the lead-in with no gap.

## Key Values to Choose (Not Already in the Rules)

Only listing parameters **unique to this blueprint**; standard parameters (`HOLD_MID`, `HOLD_FINAL`, cursor geometry) live in their respective rules.

- **CHAR_SPEED**: seconds per character, shared across all phrases. 0.04 reads as urgent/mechanical, 0.12 as deliberate. **Must be uniform across the SCRIPT array** — the rule's `SPEED_FACTOR` per-entry override doesn't apply here because the typing-rhythm-as-one-engine effect is the whole point. Convert from frames as `frames / fps`.
- **BLINK_CYCLE**: full on-off period of the cursor blink, 0.6–1.2s. Decoupled from `TOTAL` by design (see "Blink Decoupling" seam). Don't substitute the rule's `BLINK_CYCLES_PER_SCENE` form here.
- **MAIN_COLOR / ACCENT_COLOR**: text + cursor palette. Must have visibly distinct chroma — equal-luminance pairs (two pastels) make the cursor color swap unreadable. ACCENT_COLOR is the source of truth for both `.phrase-accent` text color and the active-segment cursor fill; they must match exactly.
- **SCRIPT length (N)**: 2–5 phrases. The rule's range is 3–6; this blueprint's lower floor is 2 because dual-tone phrases each carry more weight than single-tone sequence items. Above 5 the hard-cut rhythm reads as repetitive.
- **Longest-phrase font sizing**: pick the largest `fontSize` such that `max(mainLen + accentLen) * CHAR_ADVANCE_RATIO * fontSize` fits within `SAFE_WIDTH_RATIO * canvasWidth`. CHAR_ADVANCE_RATIO is ~0.5 for typical sans-serif at weight 700–900; SAFE_WIDTH_RATIO 0.85 leaves comfortable margins. If a deck needs precision, measure with a hidden canvas after `document.fonts.ready` (see [camera-cursor-tracking](../rules/camera-cursor-tracking.md) for the `ctx.measureText` pattern) — but for most messaging scenes the formula plus one hand-tune iteration is enough.

## Critical Constraints (ordered by failure frequency)

- **`Math.floor` on charIdx, and `Math.min(charIdx, mainLen)` on the main slice**: dropping either produces fractional-character flicker or a "both segments grow together" smear that destroys the dual-tone reveal.
- **Cursor color guard uses `visAccent.length > 0`, not `charIdx >= mainLen`**: see Phase 1→N Seam. Without this guard the cursor flashes ACCENT_COLOR for one frame on every main→accent boundary.
- **Zero gap between phrases**: `TIMELINE[i+1].startTime === TIMELINE[i].endTime` exactly. Any positive gap drops the next frame into the empty-state fallback and produces a one-frame stutter.
- **`white-space: pre` on `.phrase-stage`**: required when `textMain` ends with a space. Collapse the space and the lead-in / accent join with no visual gap.
- **`charSpeed` shared across all phrases**: the typing-rhythm-as-one-engine effect requires uniformity. Per-phrase override (the rule's `SPEED_FACTOR` variation) is explicitly _not_ used here.
- **`data-duration ≤ TOTAL`**: equal trims a trailing empty fallback; less is allowed to trim an over-long `HOLD_FINAL` but must fall _inside_ the final phrase's hold window, never mid-accent. `data-duration > TOTAL` leaves the empty-fallback branch firing at the tail — visible as cursor-only on blank for the excess seconds.
- **ACCENT_COLOR is the single source of truth**: `.phrase-accent` CSS color and the active-segment cursor `background` must reference the same value. Defining them in two places lets them drift.
- **DOM write guard**: `if (mainEl.textContent !== visMain) ...` — even though `textContent` is cheap, redundant writes during `hold` windows invalidate layout and cause measurable cost on long compositions.

## Spring → Ease Selection

This blueprint has **no springs**. The clock tween is `ease: "none"`, the blink is a step function via modulo, the cuts are instant. The full spring → ease mapping in [SKILL.md](../SKILL.md) is not relevant here. If you want a soft fade-in instead of hard-cut between phrases, add a 0.1s opacity tween at each `startTime` — but that departs from the source's "statement, then statement" semantic.

## Golden Sample

- [messaging-multi-phrase.html](../examples/messaging-multi-phrase.html) — three-phrase statement scene with concrete colors, font sizing, copy, and per-phrase hold values. Demonstrates the single-paused-timeline + master `onUpdate` engine, the cursor color swap derived from typing progress, the modulo-square-wave blink, and a `data-duration` deliberately set under the computed `TOTAL` to trim the closing hold. Run this first, then change values — much faster than building from scratch.
