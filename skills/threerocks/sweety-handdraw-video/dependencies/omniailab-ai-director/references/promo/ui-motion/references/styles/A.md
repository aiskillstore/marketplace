---
name: omniailab-promo-ui-motion-a
description: 「Style A — Abstract Neon (Lumen / youmotion)」—— UI 动效与产品演示 方向细则：This is a motion language anchor. The brand's colors, typography, and 
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style A — Abstract Neon (Lumen / youmotion)

**When to anchor here**: the brand wants an editorial, scroll-stop, abstract feel with no real product UI shown. Best for creative tools, design tools, generative AI products, premium editorial brands. The brand should be OK with words like "minimal", "atmospheric", "abstract" describing the video.

This is a **motion language** anchor. The brand's colors, typography, and photography mood override everything below.

**Reference video**: see `ui动画/1255024316.mp4` and `ui动画/1650245448.mp4` in the original reference pack.

## Motion signature

Slow, breath-like, parallax-driven. Subjects are *made of light*, not lit by it. Each element enters and settles before the next. Heavy spring on UI cards (8–12% overshoot). The first frame is a scroll-stop; the last frame is a wordmark; everything in between is a slow dream in the gap.

**Motion verbs for prompts**: `fades in`, `settles`, `breathes`, `drifts`, `glows`, `pulses`, `blooms`, `dissolves into`.

## Geometry vocabulary

- Rounded-rectangle cards (radius 24–32px) with 1px glowing border
- Filled circle "orbs" with radial-gradient glow
- Cursor arrow as a scene anchor (when no real UI is shown)
- Squiggly spline curves, never straight lines
- A signature glyph (the user provides their own; default is a 4-point sparkle)

## Color tokens — FALLBACK ONLY

Use these ONLY when `brand_profile.colors` is empty or incomplete. The brand's colors always win.

| Token | Value | Use |
|---|---|---|
| `--bg` | `#000000` | Background, never use anything else |
| `--cyan` | `#00E0FF` | Primary accent, glow rings |
| `--magenta` | `#FF2D9C` | Secondary accent, chromatic split |
| `--violet` | `#7A4DFF` | Tertiary, transition glow |
| `--ink` | `#F5F7FA` | Type on black |
| `--mute` | `rgba(255,255,255,0.55)` | Secondary type |

## Typography — direction only

The brand's typography wins. When the brand hasn't provided a font, default to: light geometric sans for display, regular humanist sans for body. Always light-on-dark unless the brand says otherwise.

## Motion seed (expand before generation)

```
{brand.signature_glyph} materializes in dead center of the {brand.background}, a {brand.primary} glow ring expanding outward, soft chromatic-aberration ghost. A rounded-rectangle card slides up from the bottom, thin {brand.primary} border, inside reads "<ONE WORD>" in {brand.headline_font}, a small {brand.accent} dot pulses in its top-right corner. A white cursor of light enters from the right, hovers, drags the card slightly right; a {brand.primary} glow trail follows and the {brand.accent} dot grows into a small constellation of three orbs. The card dissolves into a horizontal spectrum bar in {brand.primary} to {brand.accent}, soft chromatic-aberration halo; {brand.signature_glyph} re-anchors above. The video ends on a clean end card: {brand.real_logo} + "<PRODUCT NAME>" in {brand.headline_font} with a {brand.primary} glow, tagline below in smaller type, and {brand.store_badges} in monochrome outline at the bottom. The frame holds.
```

This block is a style-specific motif seed, not a complete `motion_prompt`. Expand it with `../motion-prompt-writing.md`; for 15s add the full timed causal chain, camera path, depth reactions, and at least three explicit transition bridges.

## Music prompt template

`ambient cinematic pulse, <brand warm/cool descriptor> <rhodes/synth/piano> keys, 70 BPM, no vocals, 15 seconds, gentle sub-bass swell every 4 bars`

Adjust the warm/cool descriptor and instrument based on the brand profile.

## Director's notes

The camera should feel like a **held breath**, not a slideshow. Slow push-ins, gentle parallax, never whip-pans or hard zoom. Negative space is the canvas — crowding the frame kills the feeling. The first frame is a scroll-stop; the last frame is a wordmark; everything in between is a slow dream in the gap. When the brand is warm (cream backgrounds, coral accents), dial back the chromatic aberration — it's a cold-look effect, easy to overdo on a warm brand.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
