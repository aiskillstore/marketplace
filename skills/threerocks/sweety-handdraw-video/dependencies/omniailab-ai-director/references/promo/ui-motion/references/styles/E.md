---
name: omniailab-promo-ui-motion-e
description: 「Style E — Warm Smart Home / Lifestyle」—— UI 动效与产品演示 方向细则：This is a motion language anchor. The brand's colors, typography, phot
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style E — Warm Smart Home / Lifestyle

**When to anchor here**: the brand is lifestyle / wellness / IoT / home / family / sleep / morning. Cream backgrounds, warm accents, organic. NOT for clinical or technical brands. The brand should be selling a feeling, not a feature.

This is a **motion language** anchor. The brand's colors, typography, photography mood override everything below.

**Reference video**: see `ui动画/MiniMax H3_视频_生成 15 秒、16_539490649989877769.mp4` in the reference pack.

## Motion signature

Warmth is the entire point. If the frame ever looks "cool" or "clinical", the design has failed. Soft, slow, organic motion. Rounded corners, soft shadows, lived-in photography. The home glyph / brand mark appears in *every* beat, even subtly.

**Motion verbs for prompts**: `fades in`, `glows softly`, `settles`, `drifts`, `warms`, `dims`, `rises gently`.

## Geometry vocabulary

- UI cards: rounded corners (radius 24–32px), white fill, soft warm shadow
- A signature glyph (the user provides their own; default is a rounded square with a home/product icon)
- A "scene" / "view" selector pattern: vertical stack of pills or horizontal segmented control
- Background: always the brand's warm background with a soft off-frame light source + organic shadow

## Color tokens — FALLBACK ONLY

| Token | Value | Use |
|---|---|---|
| `--bg` | `#F5E9DA` | Warm cream background |
| `--surface` | `#FFFFFF` | Card fill, white |
| `--shadow` | `rgba(120,80,40,0.10)` | Soft warm shadow |
| `--orange` | `#F08A2C` | Primary accent, warm scenes |
| `--green` | `#4FAE6E` | Secondary accent, sleep/calm scenes |
| `--ink` | `#2A2622` | Warm near-black type |
| `--mute` | `rgba(42,38,34,0.55)` | Secondary type |

## Typography — direction only

The brand's typography wins. Default: serif or rounded sans for headlines, clean rounded sans for body. But if the brand uses geometric sans, lean into that — warmth comes from color and shadow, not just from typography.

## Motion seed (expand before generation)

```
{brand.warm_background} with a soft window-light gradient and a faint organic shadow. A small rounded {brand.primary}-tinted square containing the {brand.signature_glyph} fades in center-screen. The square expands into a small icon, then a room-card grid fades in: "Living Room / Bedroom / Kitchen / Bathroom", each card with a small icon and a tiny status dot. The "Bedroom" card highlights in {brand.primary}. The view switches into a room card; a scene selector appears on the right: "Home / Away / Good Night / Morning". A "Good Night" pill highlights in {brand.primary}; three control cards appear (Light, AC, Curtain) with values. The user taps a scene; the background shifts color, the values change, and the control cards' border turns {brand.accent} to confirm "applied". The video ends on a clean end card: {brand.real_logo} + product name in {brand.headline_font}, tagline "{brand.tagline}" below, {brand.store_badges}. Holds.
```

This block is a style-specific motif seed, not a complete `motion_prompt`. Expand it with `../motion-prompt-writing.md`; for 15s add the full timed causal chain, camera path, depth reactions, and at least three explicit transition bridges.

## Music prompt template

`gentle acoustic morning, soft nylon guitar, fingerpicking, 70 BPM, no vocals, 15 seconds, warm and optimistic`

If the brand is more clinical than warm, drop the "acoustic morning" and substitute "ambient electronic, soft piano, 75 BPM".

## Director's notes

Warmth is the entire point. If the frame ever looks "cool" or "clinical", the design has failed — go back and add the warm color or soften the shadow. Real photography in the corner cards is essential; illustrated or stocky photos kill the lived-in feel. Avoid corporate-looking icons; round everything by 4px more than feels necessary.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
