---
name: omniailab-promo-ui-motion-custom-style
description: 「Custom style」—— UI 动效与产品演示 方向细则：When no template fits, derive the style entirely from the brand profil
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Custom style

When no template fits, derive the style entirely from the brand profile. This is the most common case for a brand-first workflow — the brand should look like itself, not like a stock reel.

## When to use this

- The brand profile is complete and the user didn't name a style
- The 8 templates score below 70% on the matching rubric
- The user explicitly said "no template, just use my brand"

## How to derive the style

### 1. Motion signature

Read `brand_profile.motion` (pace, easing, rhythm) and write a 1-line description:

- pace=slow + easing=smooth + rhythm=long-holds → "slow, deliberate, breath-like motion; each element enters and settles before the next"
- pace=medium + easing=spring + rhythm=even → "responsive, slightly bouncy; cards have personality"
- pace=fast + easing=snap + rhythm=punchy → "snappy, confident; each beat lands hard"
- pace=medium + easing=smooth + rhythm=even → "professional, controlled, no surprises"

Default to medium/smooth/even if missing.

### 2. Easing vocabulary

Map brand tone to a specific easing profile:

| Brand tone | Easing | Implementation |
|---|---|---|
| premium, slow, calm | ease-out-quart, no overshoot | `cubic-bezier(0.25, 1, 0.5, 1)` |
| playful, friendly, warm | spring with 8–12% overshoot | springy bounce |
| technical, B2B | ease-in-out, no overshoot | `cubic-bezier(0.4, 0, 0.2, 1)` |
| energetic, gaming | ease-in-back, hard overshoot | `cubic-bezier(0.68, -0.55, 0.27, 1.55)` |
| editorial, sophisticated | ease-in-out, longer duration | `cubic-bezier(0.4, 0, 0.2, 1)` over 0.6s |

### 3. Transition vocabulary

Single-take videos avoid hard cuts, but the prompt must choreograph how one state physically becomes the next. Choose 2–4 transition families from `motion-prompt-writing.md` and bind them to a recurring carrier such as a route, card edge, ring, line, cursor, or brand glyph.

- slow pace → shared-element expansion, material propagation, gentle occlusion; verbs such as "unfolds", "flows into", "settles"
- fast pace → path continuation, magnetic reassembly, foreground wipe; verbs such as "pulls", "snaps into", "whips past and reveals"
- medium → shape morph, orientation change, depth pass-through; verbs such as "stretches into", "tilts toward", "passes through"

Pair the transitions with a small camera vocabulary: push-in or focus move for entry, path-following or orbit for depth, and pull-back for the system reveal. Name the target and landing state instead of writing “dynamic camera”.

### 4. Geometry vocabulary

Read `brand_profile.density` and `brand_profile.typography.headline.mood`:

- spacious + serif → soft rounded rectangles (radius 16–24px), generous padding
- spacious + geometric-sans → softer rounded rectangles, more whitespace
- balanced + serif → medium rounded rectangles (radius 12–16px)
- dense + monospace → sharp rectangles (radius 4–6px), dashboard feel
- dense + geometric-sans → medium rectangles, product feature focus

### 5. Music signature

`<rhythm> <instrumentation>, <tempo> BPM, no vocals, 15 seconds, <emotional qualifier>`

Examples:

- "ambient cinematic pulse with warm Rhodes keys, 70 BPM, no vocals, 15 seconds, gentle sub-bass swell every 4 bars" (warm, slow, premium)
- "minimal electronic tick with glitch micro-rhythms, 90 BPM, no vocals, 15 seconds, soft synth plucks" (cool, medium, professional)
- "dark ambient thriller with sub-bass drone and sparse metallic hits, 55 BPM, no vocals, 15 seconds, tense and minimal" (cool, slow, institutional)

## Storyboard construction

With the custom style spec, build the single `motion_prompt` through `motion-prompt-writing.md`: 5–7 timed beats for 15s, one recurring motion cause, exact interaction-to-camera causality, and at least three explicit transition bridges. Use the brand colors and typography. Do not include any of the 8 templates' signature elements (sparkle, music note, glass panel) unless the brand has an equivalent in its own visual identity.

## Saving the custom spec

```json
{
  "anchor": "custom",
  "custom_spec": {
    "motion_signature": "slow, deliberate, breath-like motion; each element enters and settles before the next",
    "easing": "ease-out-quart, no overshoot",
    "geometry": "soft rounded rectangles (radius 20px), generous padding, single element per beat",
    "music_prompt": "ambient cinematic pulse with warm Rhodes keys, 70 BPM, no vocals, 15 seconds"
  }
}
```

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
