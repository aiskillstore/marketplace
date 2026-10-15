---
name: omniailab-promo-ui-motion-f
description: 「Style F — Spatial Audio Visualization」—— UI 动效与产品演示 方向细则：This is a motion language anchor. The brand's colors, typography, phot
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style F — Spatial Audio Visualization

**When to anchor here**: the brand sells audio spatiality — AirPods-class, immersive audio, music production tool with spatial mix. The 4-orb + fabric surface is iconic and only makes sense for spatial audio. Wrong for anything else.

This is a **motion language** anchor. The brand's colors, typography, photography mood override everything below.

**Reference video**: see `ui动画/MiniMax H3_视频_生成一支15秒、16_539458496606408704.mp4` in the reference pack.

## Motion signature

Spatial audio is about *distance* and *presence*, not volume. The mode change (e.g. INTIMATE → IMMERSIVE) is the entire narrative — the fabric waves should grow dramatically. The orbs are *instruments*, not buttons; treat them like they're being listened to, not clicked. The "LISTENER" anchor is the only constant; everything else moves around it.

**Motion verbs for prompts**: `fades in`, `slides in`, `drags forward`, `scales up`, `pulses outward`, `rises into waves`, `settles`.

## Geometry vocabulary

- 4 colored glass orbs (radius 60–80px) in a horizontal row, slight z-stagger
- Each orb: gradient fill (light center → dark edge) + soft outer glow
- "Fabric" surface: a soft undulating mesh in the lower half, picks up the orb colors
- Top mode selector: 3 words in a row, active word gets an underline
- White arrow cursor used as the interaction agent
- Small "LISTENER" dot at the bottom-center anchor

## Color tokens — FALLBACK ONLY

| Token | Value | Use |
|---|---|---|
| `--bg` | `#000000` | Background |
| `--percussion` | `#E8453D` | Red orb, drums |
| `--vocal` | `#3D7BE8` | Blue orb, lead vocal |
| `--ambience` | `#3DCC8E` | Green orb, atmosphere |
| `--bass` | `#E8A93D` | Amber orb, bass |
| `--ink` | `#FFFFFF` | Type, cursor |
| `--mute` | `rgba(255,255,255,0.45)` | Inactive labels |

## Typography — direction only

The brand's typography wins. Default: monospace for the channel labels and status text. The labels and the mode selector are the *voice* of this style — keep them short, all-caps, restrained.

## Motion seed (expand before generation)

```
{brand.background}. A {brand.primary}-tinted glass orb (the lead) fades in center-screen with a thin white label below it. A small white "LISTENER" dot appears below the orb. Three more orbs slide in from the sides — each tinted with one of {brand.accent_set}. Each gets a label and a soft glow ring. A white cursor enters, clicks and drags the lead orb forward; the lead orb scales up slightly and a series of concentric rings pulse outward from it. A mode selector fades in at the top, with the middle option underlined. The cursor clicks the rightmost mode option; the fabric surface below the orbs rises into tall colored waves, picking up each orb's color. The orb spacing increases; a status line appears in monospace. The video ends on a clean end card: {brand.real_logo} + product name in {brand.headline_font}, tagline below, {brand.store_badges}. Holds.
```

This block is a style-specific motif seed, not a complete `motion_prompt`. Expand it with `../motion-prompt-writing.md`; for 15s add the full timed causal chain, camera path, depth reactions, and at least three explicit transition bridges.

## Music prompt template

`ambient electronic, granular synth textures, 60 BPM, no vocals, 15 seconds, slow build, immersive pad`

If the brand is warmer, swap "granular synth" for "warm pad swells" and bump to 70 BPM.

## Director's notes

The orbs are *instruments*, not buttons. Treat them like they're being listened to, not clicked. Cursor is a *gaze*, not a pointer — it moves slowly and pauses before selecting. Avoid ever showing the orbs perfectly equal-spaced or perfectly aligned — asymmetry reads as "live", symmetry reads as "demo".

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
