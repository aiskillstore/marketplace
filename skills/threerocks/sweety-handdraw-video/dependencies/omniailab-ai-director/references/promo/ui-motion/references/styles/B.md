---
name: omniailab-promo-ui-motion-b
description: 「Style B — Abstract Systems」—— UI 动效与产品演示 方向细则：This is a motion language anchor. The brand's colors, typography, phot
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style B — Abstract Systems

**When to anchor here**: the brand is a design tool, productivity tool, or anything "tool-like" — multiple surfaces, tooltips, shortcuts. The viewer sees the working surface, not a polished marketing shot. Best for 设计工具-class, Notion-class, IDE-class, dev-tools.

This is a **motion language** anchor. The brand's colors, typography, photography mood override everything below.

**Reference video**: see `ui动画/MiniMax H3_视频_Create a 1_539483492636594182.mp4` and `ui动画/MiniMax H3_视频_A 15-secon_539504528371388423.mp4` in the reference pack.

## Motion signature

Heavier information density than A. The viewer's eye bounces between at least two cards at any moment, like watching a real designer work. Animate the *connection* between cards, not the cards as objects. Sidebar icons stay constant (never move) — they give the screen gravity.

**Motion verbs for prompts**: `fades in`, `highlights`, `pulses`, `draws a line between`, `snaps into`, `bounces in`, `settles`.

## Geometry vocabulary

- 3–5 rounded-rectangle cards (radius 16–20px) in a 2-row grid
- 1px connection lines with small glowing nodes at endpoints
- Floating tooltips / pills (radius 999px) with dark fill
- Optional sidebar (left): 40px wide, vertical icon stack
- A faint background grid (16px squares, 4% white) is a Style B signature — keep it even with the brand's background

## Color tokens — FALLBACK ONLY

| Token | Value | Use |
|---|---|---|
| `--bg` | `#05060A` | Background, near-black with a hint of blue |
| `--cyan` | `#22D3EE` | Connection lines, active node |
| `--violet` | `#8B5CF6` | Secondary line, hover state |
| `--ink` | `#E5E7EB` | Type |
| `--card` | `rgba(255,255,255,0.04)` | Card fill, glassmorphic |
| `--border` | `rgba(255,255,255,0.12)` | Card border, 1px |

## Typography — direction only

The brand's typography wins. Default: clean sans for display, monospace for labels (the "PRESS P" / "60+ TOOLS" feel). Monospace labels are the *voice* of this style — keep them short and understated.

## Motion seed (expand before generation)

```
{brand.background} with a faint grid. A vertical sidebar appears on the left edge with monochrome icons. Four rounded-rectangle cards fade in across the canvas in a 2x2 grid, glassmorphic fill, thin {brand.primary} border, with a small monospace label "<CATEGORY>" at the top. A white cursor enters, hovers over one card, the border glows {brand.primary}, a small tooltip pill appears above reading "<ACTION>". A second card highlights, then a thin {brand.primary} line draws between the two. All four cards pulse in unison, then a fifth card snaps into the grid from below with a small bounce; the label changes to "<HIGHLIGHT FEATURE>". The video ends on a clean end card: {brand.real_logo} + product name in {brand.headline_font}, with a monospace caption "<CATEGORY> TOOL" above, tagline + {brand.store_badges} at the bottom. Holds.
```

This block is a style-specific motif seed, not a complete `motion_prompt`. Expand it with `../motion-prompt-writing.md`; for 15s add the full timed causal chain, camera path, depth reactions, and at least three explicit transition bridges.

## Music prompt template

`minimal electronic tick with glitch micro-rhythms, 90 BPM, no vocals, 15 seconds, soft synth plucks`

Adjust tempo to brand pace. Faster brand → 110 BPM. Slower → 75.

## Director's notes

The grid is the product; the cards are temporary. The brand's identity should be readable from the icons, not the cards — if the brand is warm and humanist, the sidebar icons should hint at that (a softer pen glyph, not a sharp vector one). The background grid is a Style B signature; even on a brand's cream background, the grid should be visible at very low opacity (4% of the brand's neutral color).

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
