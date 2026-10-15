---
name: omniailab-promo-ui-motion-style-matching
description: 「Style matching」—— UI 动效与产品演示 方向细则：Phase 4 of the skill. The 8 style files are inspiration anchors, not t
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Style matching

Phase 4 of the skill. The 8 style files are inspiration anchors, not templates. This document explains when to anchor to one, when to go custom, and how to anchor without imposing the style's colors on the brand.

## Mental model

The 8 styles contribute 3 things:

1. **Motion language** — pacing, easing, transition vocabulary, rhythm
2. **Geometry vocabulary** — rounded vs sharp, dense vs spacious, glossy vs matte
3. **Music mood template** — a baseline instrumental prompt for music generation with the Skill's default `official/music-3.0` route

They do NOT contribute:

- Colors
- Typography
- Photography mood
- Brand voice

Anchor to Style A and the brand is warm coral + cream + serif → the video has Style A's slow breathing motion + chromatic-aberration transitions + Lumen-style sparkle vocabulary — but rendered in warm coral on cream, with a serif wordmark, and warm Rhodes BGM. The style's color tokens are fallback only.

## Quick reference — when each style fits

| Style | Brand motion language matches when… |
|---|---|
| **A — Abstract Neon** | Editorial / scroll-stop, no real product UI. Creative tools, design tools, generative AI. |
| **B — Abstract Systems** | Design tool, productivity tool, anything "tool-like". Lots of UI elements, labels, callouts. |
| **C — Futuristic 3D** | Physical product — hardware, EV, aerospace, audio gear. |
| **D — Music/Audio App** | Brand IS a music or audio product. The waveform UI is the product. |
| **E — Warm Smart Home** | Lifestyle / wellness / IoT / home / sleep / morning. Cream backgrounds, warm accents. |
| **F — Spatial Audio** | Audio spatiality — AirPods-class, immersive audio, spatial mix. |
| **G — Vision Pro / Spatial** | AR / VR / spatial computing. Needs concrete gallery / glass panels / hand gestures. |
| **H — Dossier** | Investigative / institutional / spy / cinematic-narrative. B&W + red, monospace, file stamps. |

If the brand fits none, the answer is **custom** — see `custom-style.md`.

## Matching rubric

| Brand signal | Style hint |
|---|---|
| Brand sells software (not hardware, not audio) | A, B, E (in that order) |
| Brand is editorial / creative / generative | A |
| Brand is productivity / professional / B2B | B |
| Brand sells a physical object or device | C |
| Brand is music / audio / has audio as core | D or F |
| Brand is lifestyle / wellness / IoT | E |
| Brand is AR/VR/spatial | G |
| Brand is investigative / institutional / cinematic | H |

Tiebreaker: brand's `motion.pace` (slow/medium/fast):

- Slow → A, E, G, H
- Medium → B, C, D
- Fast → B, F (rare; only gaming/energetic)

70% threshold: if the top match scores above 70%, anchor to it. Otherwise go custom.

## Custom path

When the brand is its own thing (warm coral wellness, editorial newsletter, fintech wanting clinical + humanist + gold), no style fits cleanly. Use the custom path:

- Motion language from `brand_profile.motion`
- Geometry from `brand_profile.density` + `brand_profile.typography`
- Music from `brand_profile.voice.tone` + `brand_profile.motion.pace`
- Storyboard built from scratch

See `custom-style.md` for the full recipe.

## What "anchoring" actually means

When you anchor to a style:

- **Steal** the motion signature, easing curves, transition vocabulary, and music prompt template
- **Do NOT steal** the color tokens, typography mood, photography mood — those come from the brand profile
- **In every prompt**, replace the style's hardcoded color words with the brand's color names
- **Replace** the style's signature glyph (sparkle, music note, hand cursor) with the brand's signature element (logo, product icon, or generic placeholder)

If the style's signature glyph is iconic and the brand doesn't have an equivalent, keep the glyph as a brand-neutral anchor — but only if it doesn't conflict with the brand's identity.

## When the user says "use Style X"

If the user says "I want the Lumen style" or names a style letter:

1. Anchor to that style as a **motion language**
2. Still override colors, typography, photography mood with the brand profile
3. Mention in the chat reply: *"You asked for Style A's motion language; I applied it to your brand's coral/cream/serif palette. If you wanted Style A's Lumen cyan/magenta look too, let me know and I'll override your brand."*
4. Give a one-line "if you want the pure Lumen look" option

"Style A" is a motion language, not a visual identity. The user might not have realized that — flag it.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
