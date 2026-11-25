---
name: nano-banana-video-visuals
description: >-
  当用户需要为短视频制作 AI 图片提示词时使用，尤其是 Nano Banana / Gemini 文生图工作流：短视频封面、分镜关键帧、首尾帧图、角色一致性素材、表情表、动作表、贴纸、道具、透明抠图、视觉连贯素材包。也用于把脚本、IP 角色、Obsidian 视频笔记或零散想法，整理成可复用的视觉提示词包。常见触发词：生成短视频封面、做分镜图、角色一致性、表情包贴纸、透明背景素材、AI 图片提示词参考。
---

# Nano Banana Video Visuals

This skill turns a video idea into a production-ready visual prompt pack. It is inspired by the public `PicoTrex/Awesome-Nano-Banana-images` gallery, but should not copy long prompts from it. Use the gallery as pattern evidence and generate fresh prompts for the user's project.

## Source And Scope

Primary source:

https://github.com/PicoTrex/Awesome-Nano-Banana-images

The source is a curated image/prompt gallery, not a Codex skill. This skill distills reusable workflow patterns from it for the user's video work.

## When To Use

Use this skill for:

- Short-video cover image prompts
- Storyboard keyframes from a script
- First-frame and last-frame image prompts for image-to-video tools
- Character consistency across multiple images
- Character turnarounds, pose sheets, expression sheets, emoji packs, and stickers
- Props, scene cards, product-like displays, toy/plush-style assets, and transparent cutouts
- Children's, parenting, cute IP, vegetable-character, or Q-style visual assets
- Converting a loose video concept into a repeatable visual system

Do not use it for:

- General article writing without visual assets
- Photo retouching where the user wants direct image editing
- UI layout implementation
- Installing Nano Banana, Gemini, or any external model
- Copying the source repository wholesale into the answer

## Core Rule

Output prompts as a usable production pack, not a single pretty prompt.

For each visual, specify:

- Purpose: cover, keyframe, cutout, expression, pose, prop, scene, transition, ending card
- Aspect ratio and platform fit
- Subject identity locks
- Scene and action
- Emotion and story beat
- Camera/framing
- Style and lighting
- Text policy: whether to leave blank space for text or render no text
- Negative constraints: what must not change

## Workflow

1. Identify the production mode:
   - `cover`: one high-click cover or poster
   - `storyboard`: 3-8 linked keyframes
   - `character-pack`: consistent character assets
   - `material-pack`: props, backgrounds, transparent cutouts
   - `repair-extend`: image cleanup, outpainting, background swap, pose/expression change

2. Extract anchors:
   - Character or subject
   - Target viewer
   - Video emotion
   - Platform and ratio
   - Visual style
   - Required continuity

3. Build identity locks before variation:
   - Fixed character traits
   - Fixed colors
   - Fixed clothing or accessories
   - Fixed face/body proportions
   - Fixed rendering style

4. Generate the pack:
   - Give a short use note first.
   - Then provide numbered prompts.
   - For storyboards, include one continuity sentence shared by all frames.
   - For character packs, include the identity lock block once, then variations.

5. Add a quick QA checklist:
   - Same character?
   - Same palette?
   - Scene readable at phone size?
   - Enough blank area for title?
   - No unwanted text?
   - No style drift?

## Prompt Shape

Use Chinese by default for the user-facing explanation. Prompts can be Chinese, English, or bilingual depending on the target image tool. If the user does not specify, output Chinese plus concise English prompt text for better image-model transfer.

Prefer this compact structure:

```text
用途：
比例：
中文提示词：
English prompt:
一致性锁定：
避免：
```

## Video-Specific Defaults

If the user does not specify:

- Short-video cover: `9:16`, strong subject, readable empty title area, high contrast, no rendered text unless requested
- Storyboard: 5 keyframes, beginning/conflict/turning point/result/ending
- Character pack: front view, side view, back view, 6 expressions, 6 actions, transparent cutout
- Cute IP or child-facing content: bright, warm, clean, rounded shapes, soft contrast

## Reference Routing

For concrete prompt patterns, read `references/video-visual-patterns.md`.

## Boundaries

- Do not claim Nano Banana can guarantee perfect consistency; design prompts to improve consistency and tell the user when reference images are needed.
- Do not generate copyrighted character replicas unless the user owns the character or asks for a broad non-infringing inspiration.
- Do not include hidden or invisible watermark removal instructions.
- For children or parenting visuals, keep the tone warm and non-exploitative; avoid fear-heavy or medicalized visuals unless the user explicitly asks and it is appropriate.
