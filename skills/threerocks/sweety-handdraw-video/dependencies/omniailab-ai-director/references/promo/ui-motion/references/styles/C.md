---
name: omniailab-promo-ui-motion-c
description: 「Style C — Futuristic 3D Product」—— UI 动效与产品演示 方向细则：This is a motion language anchor. The brand's colors, typography, phot
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style C — Futuristic 3D Product

**When to anchor here**: the brand sells a physical product — hardware, EV, aerospace, audio gear, anything with a tangible object to "explode" or X-ray. The product itself is the star; the UI is the chrome around it.

This is a **motion language** anchor. The brand's colors, typography, photography mood override everything below.

**Reference video**: see `ui动画/MiniMax H3_视频_Create a 1_539471132777680903.mp4` in the reference pack.

## Motion signature

The chrome is the hero, not the background. The X-ray overlay and exploded view are *the* "wow" — treat the explosion as a held beat. Camera does a slow orbital move, not a push-in. The product should feel like it was always there and the camera is just now finding it.

**Motion verbs for prompts**: `slides in`, `rotates to a 3/4 view`, `catches a highlight`, `explodes outward`, `collapses back`, `scan-line sweeps`.

## Geometry vocabulary

- The product itself: a chrome cylinder / sphere / device, occupying center
- 1px wireframe lines tracing the same surface
- HUD-style annotations: 4 corner marks (L-shaped, 16px arms), floating labels connected by 1px dotted lines
- Coordinate readouts ("x: 4.21  y: 0.18  z: -0.95") in tiny monospace
- A faint horizon line / floor reflection for grounding

## Color tokens — FALLBACK ONLY

| Token | Value | Use |
|---|---|---|
| `--bg` | `#000000` | Background |
| `--chrome-light` | `#E8ECF1` | Specular highlight on metal |
| `--chrome-dark` | `#3A3F47` | Shadow on metal |
| `--xray` | `#2E7BFF` | Wireframe / X-ray glow |
| `--hud-red` | `#FF3B3B` | Corner marks, alert dots |
| `--ink` | `#FFFFFF` | Primary type |
| `--mute` | `rgba(255,255,255,0.45)` | Secondary HUD labels |

When the brand has a primary color, the X-ray glow uses the brand's primary at high saturation. HUD "red" markers become the brand's accent. Chrome stays neutral.

## Typography — direction only

The brand's typography wins. Default for the title: 700 weight, all-caps, wide tracking, white. HUD labels always monospace, 10–11px, 45% white.

## Motion seed (expand before generation)

```
{brand.background}. A {brand.product_name} device slides in from the left, half off-screen, with {brand.accent} corner marks and a coordinate readout in the top-right. The device rotates to a 3/4 view, catching a strong top-down highlight. A {brand.primary}-tinted wireframe overlay appears on its left third, showing internal structure. A label "SECTION A-A" floats in a dotted line. The device explodes horizontally — top half lifts, internal parts fan out, {brand.primary} wireframe lines connect all parts; tiny {brand.accent} dots pulse at the connection points. The parts collapse back into the device, the wireframe glows brighter, then a final {brand.primary} scan-line sweeps left-to-right. A label "<SPEC KEY>" appears in big white type: "3000 W · 0.3 ms". The video ends on a clean end card: {brand.real_logo} + product name in heavy all-caps, small monospace tagline underneath, a thin horizontal chrome bar at the bottom. Holds.
```

This block is a style-specific motif seed, not a complete `motion_prompt`. Expand it with `../motion-prompt-writing.md`; for 15s add the full timed causal chain, camera path, depth reactions, and at least three explicit transition bridges.

## Music prompt template

`industrial cinematic tension with deep metallic hits, 80 BPM, no vocals, 15 seconds, low brass swells, mechanical precision`

If the brand is warm, drop "metallic hits" for "warm pad swells" — keep the precision, lose the cold.

## Director's notes

The product is the star. Don't let the UI chrome compete with it. When the brand is warm, dial back the chrome and lean more on the wireframe glow — chrome reads cold. HUD annotations should *under*-explain: a coordinate readout, one label, a dotted line. Anything more breaks the credibility.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
