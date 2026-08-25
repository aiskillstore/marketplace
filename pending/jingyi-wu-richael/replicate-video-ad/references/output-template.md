# Output Template

Use this structure for `视频复刻提示词.md`. Keep it concise enough to use, but complete enough to produce.

## 1. Source Summary

- Duration and aspect ratio
- Sampling density and transcript source
- Visual format and camera grammar
- Story mechanism in one sentence
- Product assumption and unresolved facts

## 2. Shot Timeline

| 时间 | 画面与动作 | 对白/字幕 | 剧情功能 | 商品露出 |
|---|---|---|---|---|
| 0:00-0:03 | ... | ... | Hook | ... |

Use ranges rather than listing every sampled frame. Every range must be grounded in inspected frames.

## 3. Adaptation Logic

State what remains faithful and what changes for the target product. List each product claim as `verified`, `observed`, or `placeholder`.

## 4. Copy-Ready Master Prompt

Write one prompt in a fenced `text` block. Include, in this order:

1. format, duration, realism, and overall visual grammar;
2. location, camera placement, lens feel, lighting, and production texture;
3. stable character, wardrobe, prop, and product definitions;
4. timestamped actions, reactions, and supported dialogue;
5. native product bridge and observable proof;
6. sound design and music arc;
7. post-production text plan;
8. negative constraints.

Use `【字段】` placeholders consistently. Never silently convert a placeholder into a factual claim.

## 5. Post-Production Copy

Provide:

- first-frame headline;
- dialogue subtitle styling;
- 2-4 proof labels;
- closing emotional line;
- brand/product lockup;
- offer and CTA placeholders.

Do not ask the video model to render exact Chinese text.

## 6. Segmented Generation Plan

For each segment, provide the time range, start state, key action, end state, and continuity anchors. Recommend using the same character, room, wardrobe, and product reference images across segments.

## 7. Handoff Note

State:

- sampled frame count and interval;
- whether audio was transcribed;
- any unclear dialogue or product claims;
- delivered artifact names.
