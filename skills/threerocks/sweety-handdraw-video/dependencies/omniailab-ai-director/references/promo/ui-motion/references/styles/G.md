---
name: omniailab-promo-ui-motion-g
description: 「Style G — Vision Pro / Spatial UI」—— UI 动效与产品演示 方向细则：This is a motion language anchor. The brand's colors, typography, phot
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style G — Vision Pro / Spatial UI

**When to anchor here**: the brand sells AR / VR / spatial computing / Vision Pro-class product. Needs the concrete gallery / glass panel / hand-gesture setting. Wrong for non-spatial brands.

This is a **motion language** anchor. The brand's colors, typography, photography mood override everything below.

**Reference video**: see `ui动画/MiniMax H3_视频_生成一支15秒、16_539472603317440521.mp4` in the reference pack.

## Motion signature

The person is the *anchor* — the panels orbit around them. Camera never cuts away from the person; if a panel is important, the person moves *to* it, not the other way around. Hand gestures are the only interaction vocabulary — no cursor, no click, no keyboard. The "glass" effect on the panels is the entire style.

**Motion verbs for prompts**: `walks in`, `reaches toward`, `taps and holds`, `drags slowly`, `scales up`, `steps back`, `camera pushes in`, `walks off-frame`.

## Geometry vocabulary

- Floating glass panels: rounded corners (radius 20–28px), thin white border, slight inner glow
- The person: a real human (silhouette / mid-distance shot), 30–50% of frame height
- A pedestal sculpture in the background to anchor the space (use the brand's product as the "sculpture" if appropriate)
- A "wall of panels" effect when many panels stack vertically on the right
- Hand gestures are the interaction — no cursor
- Depth: panels in foreground are larger and brighter, background panels dimmer

## Color tokens — FALLBACK ONLY

| Token | Value | Use |
|---|---|---|
| `--bg` | `#A8A39A` | Concrete gallery wall (real photo) |
| `--floor` | `#C7B89B` | Light wood floor |
| `--glass` | `rgba(255,255,255,0.10)` | Panel fill, glassmorphic |
| `--border` | `rgba(255,255,255,0.55)` | Panel border, 1.5px |
| `--accent-1` | `#FF6A3D` | Default accent (orange) |
| `--accent-2` | `#7A4DFF` | Drag-state accent (violet) |
| `--accent-3` | `#3DC8E8` | Save-state accent (cyan) |
| `--ink` | `#FFFFFF` | Type |

## Typography — direction only

The brand's typography wins. Default for panel titles: 600 weight, all-caps, wide tracking. If the brand is warm and humanist, soften this — the gallery setting can host a serif as long as it's still clean.

## Motion seed (expand before generation)

```
{brand.gallery_wall} interior, soft daylight from a skylight. A glass panel labelled "{brand.feature_label}" floats center-screen; a person in dark clothes walks in from the right, mid-distance. The person reaches toward the panel; a second panel labelled "{brand.detail_label}" appears, slightly larger, with content inside. The first panel shrinks to the left as a thumbnail. The person's hand taps and holds the panel — its border pulses {brand.accent_1}. They drag it slowly to the right; the panel scales up as it moves, casting a soft shadow on the wall. Three more panels appear in a stack: "{brand.action_label_1}" (border {brand.accent_2}), "{brand.action_label_2}" (border {brand.accent_3}), "{brand.action_label_3}" (border {brand.accent_1}). The person steps back; the camera pushes in slightly. The person walks off-frame left. The panels float in place, then the scene fades to {brand.background}. The video ends on a clean end card: a small glass panel containing {brand.real_logo} + product name in {brand.headline_font}, tagline below, {brand.store_badges}. Holds.
```

This block is a style-specific motif seed, not a complete `motion_prompt`. Expand it with `../motion-prompt-writing.md`; for 15s add the full timed causal chain, camera path, depth reactions, and at least three explicit transition bridges.

## Music prompt template

`cinematic ambient piano, sparse single notes, 65 BPM, no vocals, 15 seconds, gentle reverb, contemplative`

If the brand is more energetic, swap "sparse single notes" for "warm Rhodes keys, 75 BPM".

## Director's notes

The accent color (single bold color per scene) signals which panel is "active"; never have two panels in different accent colors at the same time, it reads as a bug. Real-world depth (panel casts shadow on wall, person occludes panel slightly) is the most expensive thing to fake — when in doubt, simplify the scene instead of overloading it.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
