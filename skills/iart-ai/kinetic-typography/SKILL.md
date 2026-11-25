---
name: kinetic-typography
description: This skill should be used when the user asks to "animate a headline", "make a kinetic typography video", "do a split-text reveal", "stagger text by character/word/line", "make a lyric or caption video", "animate a variable font weight", "put text on a path", or "create an animated title card". Covers reveal techniques in CSS, GSAP SplitText, Framer Motion, and Remotion.
version: 0.1.0
---

# Typography in Motion

Animate text expressively: splitting copy into lines/words/characters, staggering reveals, masking, blurring, morphing weight, and running text along a path. Produces runnable code for the web (CSS, GSAP, Framer Motion) and video (Remotion), plus an After Effects expression approach.

## When to use

- Headline / tagline entrances and animated title cards.
- Lyric videos, caption/subtitle reveals, kinetic-typography pieces.
- Variable-font animation (weight, width, slant, optical size).
- Text-on-path, text stroke draw-on, and per-character morph effects.

## Core workflow

### 1. Get static typography right first

Motion cannot rescue bad type. Before animating, lock line-height (1.1-1.2 for display headlines, 1.4-1.6 for body), tracking (tighten display by -1% to -3%, e.g. `letter-spacing: -0.02em`), alignment, and weight. Then split and animate.

### 2. Choose split granularity

- **By line** — calmest, most premium; best for multi-line paragraphs and elegant headlines.
- **By word** — energetic, good for taglines and lyric hits.
- **By character** — most kinetic/playful; risk of feeling busy on long copy. Reserve for short strings.

Tools: `SplitType` or GSAP `SplitText` on the web; `.split('')` / `.split(' ')` plus `interpolate` in Remotion; `motion` staggered children in Framer Motion.

Critical accessibility note: splitting into per-character spans destroys the text for screen readers and breaks copy-paste. Always set `aria-label` on the container with the full string and `aria-hidden="true"` on the split fragments.

### 3. Apply a reveal technique

The four workhorse reveals:

- **Mask / clip reveal (most robust)** — wrap each line in `overflow: hidden`; animate the child from `translateY(100%)` to `0`. The text wipes up from a hidden baseline. No blur artifacts, GPU-cheap, the industry-standard headline reveal.
- **Blur-in** — animate `filter: blur(12px) -> blur(0)` with `opacity 0 -> 1`. Soft, premium, "focus-pull" feel. Costlier to render; keep blur radius modest and prefer short durations.
- **Clip-path wipe** — animate `clip-path: inset(0 100% 0 0)` to `inset(0 0 0 0)` for a directional reveal without moving the glyphs.
- **Character stagger** — split to chars, fade/translate each with a 20-40ms offset.

### 4. Apply principle-correct timing

Inline essentials (so this skill stands alone):
- Enter with ease-out: `cubic-bezier(0.16, 1, 0.3, 1)` (easeOutExpo) feels premium.
- Per-fragment duration 400-600ms.
- Stagger: lines 60-100ms, words 40-70ms, characters 20-40ms apart.
- Cap total reveal near ~800ms; for long strings, reduce per-char offset or switch to word/line granularity.

### 5. Mask-reveal, copy-paste (vanilla CSS + JS line split)

```html
<h1 class="reveal" aria-label="Designed for motion">Designed for motion</h1>
```

```css
.reveal .line { overflow: hidden; }
.reveal .line > span {
  display: inline-block;
  transform: translateY(110%);
  animation: rise 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.reveal .line:nth-child(2) > span { animation-delay: 0.08s; }
.reveal .line:nth-child(3) > span { animation-delay: 0.16s; }
@keyframes rise { to { transform: translateY(0); } }
```

### 6. Variable-font weight animation

```css
@keyframes thicken {
  from { font-variation-settings: "wght" 200; }
  to   { font-variation-settings: "wght" 800; }
}
.headline {
  font-family: "Inter var", sans-serif;
  animation: thicken 0.8s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}
```

Animate `font-variation-settings` (covers any axis: `wght`, `wdth`, `slnt`, `opsz`, plus custom axes), not `font-weight`, to hit non-standard values and to interpolate smoothly. Confirm the loaded font is actually a variable font and the axis range (e.g. wght 100-900) before animating, or the value clamps silently.

## Deliver & verify (standalone HTML)

> **Packaged helper** (`scripts/`): `scripts/seek-shot.sh anim.html 0 1.5 3` freezes the `?t=N` harness and screenshots each moment; `scripts/contact-sheet.sh sheet.png frame-*.png` tiles them for one-glance review. See `scripts/README.md`.

For a web text reveal / kinetic-title deliverable, ship **one `.html` file that opens directly in a browser** — no build step. One file is the right tier for a headline, title card, or single reveal.

**Output contract:**
- One `.html` file: markup with `aria-label` on the container, the reveal in inline `<style>` (or one inline GSAP `<script>` from CDN).
- One animation driver — a CSS `@keyframes` reveal, or a single GSAP timeline; not both.
- Include the freeze harness below so any moment can be screenshotted deterministically.
- Split AFTER `document.fonts.ready` so line breaks are correct in the frozen frame.

**Freeze harness — pin a frame for screenshots.**

```html
<script>
  const t = new URLSearchParams(location.search).get("t");
  if (t !== null) {
    // CSS @keyframes reveal:
    document.querySelectorAll(".reveal *").forEach(el => {
      el.style.animationDelay = (-parseFloat(t)) + "s";
      el.style.animationPlayState = "paused";
    });
    // GSAP timeline instead? → tl.pause(); tl.seek(parseFloat(t));
  }
  window.__ready = true;                                          // ready signal for headless wait
</script>
```

**Verify loop — render → freeze → screenshot → check:**
1. Open the file frozen at start / mid / end: `…/type.html?t=0`, `?t=<dur/2>`, `?t=<dur>`.
2. Screenshot each frozen frame.
3. Check **fidelity** (matches the brief) and **artifacts** — clipped glyphs/descenders, masks that don't fully hide the baseline, FOUC or wrong line breaks before fonts load, blur fringing.

```bash
npx playwright screenshot --wait-for-timeout=500 "file://$PWD/type.html?t=0.4" frame-mid.png
```

**Before you finish:**
1. Opens standalone in a browser — no console errors, no missing CDN/font.
2. One reveal driver; `?t=N` freezes the exact frame correctly.
3. Screenshotted at start / mid / end — no clipped glyphs, no FOUC, line breaks correct.
4. `prefers-reduced-motion` honored (text shown in final state, no motion).
5. `aria-label` on the container; split fragments `aria-hidden` — copy and screen-reader text intact.

## Quick reference

| Effect | Core CSS / approach |
|---|---|
| Mask up reveal | parent `overflow:hidden`; child `translateY(110%)->0` |
| Blur in | `filter: blur(12px)->0` + opacity |
| Directional wipe | `clip-path: inset(0 100% 0 0)->inset(0)` |
| Char stagger | split chars, 20-40ms offset, fade+rise |
| Variable weight | animate `font-variation-settings:"wght" a->b` |
| Text on path | SVG `<textPath href="#curve">` |
| Stroke draw-on | SVG text as path, animate `stroke-dashoffset` |

## Text on a path (SVG)

```html
<svg viewBox="0 0 600 200">
  <path id="curve" d="M20,150 Q300,20 580,150" fill="none" />
  <text font-size="42" fill="#fff">
    <textPath href="#curve" startOffset="0%">Follow the curve</textPath>
  </text>
</svg>
```

Animate the `startOffset` attribute (`0%` -> `100%`) to scroll text along the path, or animate the path `d` to make text flow on a morphing curve.

## Reference files

- `references/reveal-recipes.md` — copy-paste reveal cookbook: mask/blur/clip/char-stagger in CSS, GSAP SplitText timelines, Framer Motion staggered variants, Remotion per-character interpolation, variable-font keyframes, and a screen-reader-safe split helper.
