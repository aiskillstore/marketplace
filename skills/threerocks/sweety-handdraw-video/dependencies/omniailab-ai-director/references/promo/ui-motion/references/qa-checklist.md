---
name: omniailab-promo-ui-motion-qa-checklist
description: 「Pre-delivery QA Checklist」—— UI 动效与产品演示 方向细则：Run through this before sending final.mp4 to the user. Brand consisten
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Pre-delivery QA Checklist

Run through this before sending `final.mp4` to the user. **Brand consistency is the top check** — every other check is secondary if the video doesn't look like the brand.

## Brand consistency (the top check)

- [ ] All colors in the rendered frames come from `brand_profile.colors` (or are derived shades — primary at 50% alpha, etc.). No stray cyan/magenta/violet glows if the brand is warm coral.
- [ ] The end card uses the real brand mark from `brand_assets.end_card` (or the user's uploaded logo), not a generic glyph. The model must NOT fall back to a sparkle ✦, music note, or any signature glyph from a style template.
- [ ] The end card wordmark is in the brand's typography (or a reasonable fallback). Sans brand on a serif brand is a bug.
- [ ] The motion_prompt uses the brand's color *names* ("warm coral", "deep navy") not the style anchor's hardcoded color names. Search the storyboard.json for any leftover "cyan", "magenta", "violet" from Style A — replace with the brand's actual accent names.
- [ ] If the user provided a brand asset, that asset is visibly in the rendered frame. Verify by watching the final video.
- [ ] Music prompt doesn't reference the style's default mood if the brand has its own. A warm brand shouldn't get the "industrial metallic hits" template from Style C.

## Spec

- [ ] Total runtime matches the requested length ±0.15s (e.g. 14.85–15.15s for a 15s ask)
- [ ] Resolution matches the declared aspect ratio: 1080×1920 for 9:16, 1920×1080 for 16:9
- [ ] 30 fps (H.264 + AAC both default to 30 fps)
- [ ] Pixel format `yuv420p` (universal playback, required by most social platforms)

## Duration mode and reference routing

- [ ] A request up to and including 15s has exactly one video generation; a supplied image remains an all-purpose reference, not a first frame
- [ ] A ≤15s storyboard omits generated BGM by default; no music generation was called unless the user explicitly requested an override
- [ ] A >15s storyboard uses contiguous `sequence` values and exactly one segment-1 all-purpose reference input
- [ ] For every segment N>1, the lineage names N-1 and its starting image exactly equals segment N-1's extracted tail frame
- [ ] No later segment reuses the original all-purpose reference as its first frame or repeats the segment-1 opening procedure

## Visual

- [ ] No frame contains literal iOS / Android UI chrome (no system status bar, no app icons, no notification center)
- [ ] On-screen text budget: ≤ 6 words total across the whole video, except the end card which may have product name + tagline + store badges
- [ ] End card text legible at 100% on a phone screen
- [ ] If a continuation first frame exists, it is the untouched previous tail frame; do not add poster text or regenerate it

## Motion prompt quality

- [ ] The prompt covers the full duration with non-overlapping timed beats; 15s has 5–7 beats and never fewer than 1000 Chinese characters or 600 English words of executable direction
- [ ] Every beat states a visible trigger, primary UI response, secondary spatial response, camera response, exact bridge, and readable settle
- [ ] One recurring carrier—cursor, route, line, ring, card edge, waveform, node, or brand glyph—causes or connects the major changes
- [ ] A 15s take has at least three explicit shared-object transitions; “smooth transition” or “UI transforms” without a carrier and landing state does not pass
- [ ] Camera direction is purposeful and varied: entry uses a push-in/push-through or focus move when useful; the relationship reveal uses a pull-back/orbit/overview when useful
- [ ] Foreground, midground, and background reactions create depth without making every layer move simultaneously
- [ ] Every video generation receives its complete local storyboard `motion_prompt` without summarizing or truncating it

## Audio

- [ ] For ≤15s, no extra BGM was generated or muxed by default; preserve the single clip's native audio contract
- [ ] For >15s, the BGM call happened only after all numbered segments and joins passed validation
- [ ] A >15s chain has exactly one BGM pass after all segments and joins succeed; it is instrumental by default and has no lyrics
- [ ] For >15s, BGM peaks below -3 dBFS and has no clipping
- [ ] For >15s, total audio length matches video length ±0.1s
- [ ] Final >15s assembly preserves the requested total length and never stops early because one stream ends first
- [ ] Verify both stream durations after the >15s assembly; the audio must not end before the video

## Numbered continuation chain (>15s only)

- [ ] The join between segment N and segment N+1 has no visible jump. Watch the seam at 0.5x speed.
- [ ] The segment N tail frame was extracted and probed before segment N+1 started; a second opening-generation call does not count as segment N+1
- [ ] If drift is visible, regenerate segment N+1 with a local "from this static frame" continuation prompt
- [ ] Audio is continuous across the join (no gap, no click)

## Platform-specific

- **抖音 / 小红书 (Reels/Shorts)**: poster image should be a clean freeze of the end card
- **YouTube / B站 (16:9)**: end card may include a Subscribe/Follow cue if the user is a creator
- **Twitter / X (in-feed video)**: autoplay is muted, so the first 2 seconds need to be visually punchy without audio

## File

- [ ] Filename ends in `.mp4`
- [ ] File size under 50 MB; if over, use the editor's approved compression preset
- [ ] The exported file opens promptly and keeps the required metadata at the start

## If any check fails

**Brand consistency failure** is the most common and most visible. Don't ship a video that doesn't look like the brand. If the model drifted, regenerate the affected segment with a more explicit prompt that names the brand colors and the real brand mark.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
