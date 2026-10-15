---
name: omniailab-promo-ui-motion-d
description: 「Style D — Music / Audio App」—— UI 动效与产品演示 方向细则：This is a motion language anchor. The brand's colors, typography, phot
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style D — Music / Audio App

**When to anchor here**: the brand IS a music or audio product. The album-art + waveform + playback UI is the product, not a metaphor. This style is wrong for non-audio brands.

This is a **motion language** anchor. The brand's colors, typography, photography mood override everything below.

**Reference video**: see `ui动画/MiniMax H3_视频_Create a 1_539536155260653572.mp4` in the reference pack.

## Motion signature

The album art is the anchor — every other element supports it. The waveform is the only "live" thing on screen; make it the loudest visual element even though it occupies 5% of the frame. Cards behind the main panel are *memory* of what came before, not clutter. The play click is a hard beat.

**Motion verbs for prompts**: `fades in`, `slides in from the right`, `clicks play`, `fills`, `animates`, `pulses`, `color-shifts`, `bounces`.

## Geometry vocabulary

- Main player panel: rounded rectangle (radius 20–28px), glass fill, 1px border
- Album art card: square, same radius, vivid graphic
- Playback bar: thin horizontal line, white with brand-accent progress fill
- Audio waveform: vertical bars, 1–2px wide, varied heights
- Card stacks behind the main panel, slightly offset, blurred (12% white blur)

## Color tokens — FALLBACK ONLY

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0F0A08` | Background, warm near-black |
| `--surface` | `rgba(255,255,255,0.06)` | Card / panel fill |
| `--border` | `rgba(255,255,255,0.10)` | Card border |
| `--accent` | `#FF6B3D` | Orange accent (waveform, active state) |
| `--ink` | `#F4EFE6` | Warm off-white type |
| `--mute` | `rgba(244,239,230,0.55)` | Secondary type |

## Typography — direction only

The brand's typography wins. For an audio brand, a serif on the song title is a strong default — but only if the brand's existing typography is also serif-leaning. If the brand uses geometric sans, use that.

## Motion seed (expand before generation)

```
{brand.background}. A glassmorphic player panel fades in center-screen, empty, with a thin {brand.accent} progress bar at the bottom. An album-art card slides in from the right into the panel: a {brand.accent} square with a {brand.album_graphic_hint} pattern. Track title "01 / <SONG>" appears in {brand.headline_font} to the right of the art. A cursor enters, clicks play; the progress bar fills {brand.accent}, an audio waveform animates (vertical bars growing/shrinking) across the bar. The panel shrinks slightly and a stacked equalizer panel slides in from the right with 5 frequency sliders; the album art color-shifts from {brand.accent} to {brand.accent_lighter}. The video ends on a clean end card: {brand.real_logo} + product name in {brand.headline_font}, tagline below in small caps, {brand.store_badges}. Holds.
```

This block is a style-specific motif seed, not a complete `motion_prompt`. Expand it with `../motion-prompt-writing.md`; for 15s add the full timed causal chain, camera path, depth reactions, and at least three explicit transition bridges.

## Music prompt template

`warm lo-fi hip-hop, vinyl crackle, 78 BPM, no vocals, 15 seconds, soft Rhodes keys, gentle side-chain`

If the brand is more electronic than lo-fi, swap "lo-fi hip-hop, vinyl crackle" for "downtempo electronic, side-chained pad, 90 BPM".

## Director's notes

When the theme color shifts (album art color change, accent fade), every UI element should shift in lockstep, including the text shadow; partial shifts read as a bug. The serif on the song title is doing 80% of the work — don't dilute it with bright color.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
