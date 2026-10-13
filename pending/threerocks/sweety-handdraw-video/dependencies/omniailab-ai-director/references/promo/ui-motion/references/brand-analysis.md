---
name: omniailab-promo-ui-motion-brand-analysis
description: 「Brand analysis」—— UI 动效与产品演示 方向细则：The brand profile is the structured output of Phase 2. It's the source
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Brand analysis

The brand profile is the structured output of Phase 2. It's the source of truth for every prompt in the storyboard. Get this right and the rest of the pipeline is mechanical.

## Structure

```json
{
  "version": 1,
  "subject": "Notely — AI note-taking app",
  "brand_name": "Notely",
  "sources": [
    { "type": "image", "path": "brand/notely-logo.png" },
    { "type": "image", "path": "brand/notely-editor.png" },
    { "type": "text", "content": "warm, intellectual, slow, premium" }
  ],
  "colors": {
    "primary": "#FF6B3D",
    "accent": "#1F2A44",
    "neutral": "#F4F1EA",
    "background": "#0F1218",
    "text": "#FAFAFA"
  },
  "color_naming": {
    "primary": "warm coral",
    "accent": "deep navy",
    "background": "near-black with a warm undertone"
  },
  "typography": {
    "headline": {
      "family": "Fraunces",
      "mood": "serif, warm, humanist",
      "weight": "regular",
      "tracking": "slight"
    },
    "body": {
      "family": "Inter",
      "mood": "clean humanist sans",
      "weight": "regular"
    }
  },
  "photography": {
    "mood": "lifestyle, golden hour, soft shadows",
    "subjects": "people working, hands, devices, warm interiors"
  },
  "density": "spacious — lots of negative space, never crowded",
  "motion": {
    "pace": "slow",
    "easing": "smooth with subtle spring",
    "rhythm": "long holds between movements"
  },
  "voice": {
    "tone": "thoughtful, calm, confident",
    "avoid_words": ["exciting", "game-changing", "synergy"]
  }
}
```

## Extraction procedure

### From brand images

For each image the user provided, inspect it. Ask yourself in order and write the answers into the structure:

1. **Background** — light, dark, gradient, photographic? Note the dominant base.
2. **Dominant colors** — list 3–5 with hex. If you can see them but can't name the hex, use a clear color name ("warm coral") and write both into `colors` (hex) and `color_naming` (descriptive).
3. **Typography** — geometric sans, humanist sans, serif, monospace? Light or heavy? Wide or tight? Don't try to identify the font family by name unless it's a brand guideline PDF.
4. **Photography mood** — lifestyle, product-only, abstract, technical, flat-design? If photographic, time of day, setting, subjects?
5. **Visual density** — how full is the frame? Spacious (one element + lots of space), balanced, dense?
6. **Motion hints** — if video/GIF, what does the motion feel like? If static, infer from composition what motion would feel natural (static logo → subtle hover; landscape → parallax).

### From text description

Parse the user's words into the same fields:

- "warm, premium, navy and gold" → colors {primary: gold, accent: navy}; mood: premium (low density, slow motion, serif type)
- "energetic, gaming, neon" → colors {primary: neon green, accent: electric purple}; mood: energetic
- "minimalist, editorial, slow" → density: very spacious; pace: slow

When a word is ambiguous ("modern", "clean", "premium"), err on the side of less — minimalist, slower, more spacious.

### Resolving conflicts

Images win over text descriptions (text is usually aspirational; images are what the brand actually looks like).

If two images conflict (logo monochrome vs marketing banner multicolor), the logo is more authoritative for color identity; the marketing banner is more authoritative for photography mood.

If unresolvable, ask the user once, very specifically: *"Your logo is monochrome but your banner uses warm coral. Which color do you want as the primary — monochrome or coral?"*

## Color descriptions for prompts

Hex codes don't help image generation models. Convert every brand color to a **descriptive name** for use in `first_frame_prompt` and `motion_prompt`:

| Hex | Descriptive name |
|---|---|
| `#FF6B3D` | warm coral |
| `#1F2A44` | deep navy |
| `#F4F1EA` | warm cream |
| `#0F1218` | near-black |
| `#FAFAFA` | off-white |
| `#4FAE6E` | sage green |
| `#E8453D` | bright red |
| `#3D7BE8` | electric blue |

The model renders these more faithfully when described in words. Use descriptive names in prompts; save hex for brand_profile.json.

## Common extraction mistakes

- **Reading the wrong color as primary.** If the brand image is mostly white with a small colored logo, the primary is the logo color, not white.
- **Ignoring the background.** Backgrounds define 60–80% of the visual.
- **Confusing UI density with brand density.** A dense product UI inside a spacious marketing layout means the brand is spacious, the product is dense — different things.
- **Skipping the text description.** Even with great images, the user's own words capture intent (mood, pace, voice) that images can't.

## When the brand profile is empty or incomplete

If the user provided only one tiny image and no text, fill in reasonable defaults and mark them as "default — confirm with user". The chat reply should ask the user to confirm.

Defaults:

- Background: `near-black` (safest for motion design)
- Typography: `clean humanist sans` (Inter-style)
- Density: `balanced`
- Motion: `{pace: medium, easing: smooth, rhythm: even}`
- Photography mood: `abstract`
- Voice: `neutral, professional`

## Validation before storyboard

Before Phase 5, verify:

- [ ] `colors.primary` is set with both hex and descriptive name
- [ ] `colors.background` is set
- [ ] `typography.headline.mood` is set
- [ ] `motion.pace` is set
- [ ] `density` is set

If any are missing, the storyboard will silently fall back to the style anchor's defaults. Catch it now.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
