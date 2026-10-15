---
name: omniailab-promo-ui-motion-h
description: 「Style H — Dossier / Classified」—— UI 动效与产品演示 方向细则：This is a motion language anchor. The brand's colors, typography, phot
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style H — Dossier / Classified

**When to anchor here**: the brand is investigative / institutional / spy-themed / cinematic-narrative / documentary. Black-white-red, monospace, file stamps. NOT for friendly consumer brands. The brand should be selling secrecy, gravity, or analysis.

This is a **motion language** anchor. The brand's colors, typography, photography mood override everything below — but the dossier layout (portrait + stamp + network graph + text panels) is iconic enough to keep even if the brand's colors are different.

**Reference video**: see `ui动画/备选03.mp4` in the reference pack.

## Motion signature

The fake text is the product. Every monospace string on screen has to look like it could be a real file ID or coordinate — never "Lorem ipsum", never "Click here". The B&W portrait is the emotional anchor; the network graph is the analytical anchor. Show one, then the other, never both at the same size. Slight film grain everywhere — never a clean vector look.

**Motion verbs for prompts**: `fades in`, `slides in from the left`, `rises from the bottom`, `pulse`, `rotate`, `scale down`, `slide off-frame`.

## Geometry vocabulary

- Document panels: rounded corners (radius 4–8px, slightly sharper than other styles), thin white border
- Network graph: small circular nodes (radius 4–8px) connected by 1px lines, with one yellow "focus" node
- Portrait: B&W, square, framed with a thin red outline
- A signature numeric stamp: oversized, slightly rotated, with a thin black slash
- Always at least one horizontal rule (1px) cutting the frame — color comes from the brand
- Small annotation readouts in the corners, monospace

## Color tokens — FALLBACK ONLY

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0A0A0A` | Background, near-black with grain |
| `--paper` | `#1A1A1A` | Document / panel fill |
| `--red` | `#D72638` | Classification stamp, connection lines |
| `--yellow` | `#F2E863` | Numeric stamp, accent (the "08") |
| `--ink` | `#E8E0D0` | Cream-white type |
| `--mute` | `rgba(232,224,208,0.45)` | Secondary type, annotations |

## Typography — direction only

The brand's typography wins. Default: monospace for body, all-caps for stamps, light sans for the title. Even if the brand's main typography is humanist, the dossier layout benefits from monospace for the *body text inside the panels* — it sells the "document" feel.

## Motion seed (expand before generation)

```
{brand.background} with a slight grain. A large {brand.accent} numeric stamp "<BRAND_INITIALS>" fades in slightly rotated, with a thin black diagonal slash. A {brand.primary} horizontal line draws from the right edge to under the stamp. A B&W portrait panel slides in from the left: a moody mid-shot, framed in a thin {brand.primary} outline. A monospace text block slides in from the right reading "<BRAND_STAMP_TEXT>" and 3–4 lines of fake-but-plausible identification text. A network-graph panel rises from the bottom: 12 circular nodes connected by {brand.primary} lines, the central node glowing {brand.accent}. One by one, three nodes pulse {brand.primary}. A second document panel slides in from the right, slightly behind the portrait panel — translucent, showing more monospace text. The portrait panel scales down and the network graph rotates 15 degrees. The video ends on a clean end card: all panels slide off-frame left, {brand.background} remains with the grain; a small {brand.primary} circle + product name in {brand.headline_font} all-caps, with a {brand.primary} horizontal rule above and below, tagline in monospace below, {brand.store_badges}. Holds.
```

This block is a style-specific motif seed, not a complete `motion_prompt`. Expand it with `../motion-prompt-writing.md`; for 15s add the full timed causal chain, camera path, depth reactions, and at least three explicit transition bridges.

## Music prompt template

`dark ambient thriller, sub-bass drone, sparse metallic hits, 55 BPM, no vocals, 15 seconds, tense and minimal`

If the brand is institutional but not thriller (e.g. a financial regulator), drop the "metallic hits" and substitute "soft piano, 60 BPM".

## Director's notes

The signature numeric stamp (the "08" in the reference) should appear at least 3 times across the video (different sizes, different opacities) so it reads as a recurring motif, not a one-shot. Red rules (horizontal lines) are the *grammar* of the piece — use them as section dividers. The fake text strings should look like real file IDs: "REC. 4782", "OP-0931-A", "SECTOR 4.21", never "Click here".

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
