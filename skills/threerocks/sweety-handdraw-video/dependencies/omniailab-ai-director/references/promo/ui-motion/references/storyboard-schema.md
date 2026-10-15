---
name: omniailab-promo-ui-motion-storyboard-schema
description: 「Storyboard structure」—— UI 动效与产品演示 方向细则：This reference describes the planning structure for storyboard.json. K
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Storyboard structure

This reference describes the planning structure for `storyboard.json`. Keep it as a human-readable record of the brand, style, references, timing, motion direction, and assembly lineage.

## Single segment (up to 15 seconds)

Record one subject, the requested aspect ratio and resolution, the total duration, the paths to `brand_profile.json` and `style_anchor.json`, and the approved reference images. The narrative has two parts:

- a short reference description that explains what the supplied image contributes and explicitly says it is not the opening frame;
- a complete chronological motion treatment from `motion-prompt-writing.md`, with visible triggers, UI responses, camera movement, transition bridges, readable settles, and a stable end card.

The user's image remains an all-purpose reference throughout this route. Do not invent an opening still, add a second subject, or add BGM by default.

## Continuation chain (over 15 seconds)

Store a numbered list of segments. Segment 1 uses the approved all-purpose reference. Every later segment starts from the verified tail frame of the immediately preceding segment and has its own local motion treatment. Keep each segment's duration, input path, output clip path, extracted tail-frame path, and a plain-language lineage note. The first segment has no predecessor; every later segment names the preceding sequence.

Generate all segments before creating one instrumental BGM. Concatenate clips in sequence order, mix the BGM only after the chain is complete, and report the actual summed duration. Never repeat the opening procedure for a later segment, silently replace a missing tail frame, or use a second music pass.

## Shared fields

- `subject`: one-line product or concept description.
- `aspect_ratio`, `resolution`, and `total_duration_sec`: the confirmed delivery constraints.
- `brand_profile_ref` and `style_anchor_ref`: workspace-relative paths to the shared planning artifacts.
- `brand_assets`: optional descriptors for reference images and the real end-card mark, including each asset's path and contribution.
- `narrative`: required for a single segment; keep the reference description and full motion treatment together.
- `takes`: required for a continuation chain; entries are contiguous, strictly ordered segments.

## Segment checks

1. The total duration equals the sum of all segment durations.
2. A later segment can start only from the inspected tail frame of the previous segment; the original reference image is never silently reused as a continuation frame.
3. Every motion treatment is complete for its local duration and follows `motion-prompt-writing.md`; do not send abbreviated notes as a finished prompt.
4. Colors and typography come from the brand profile, while motion rhythm and transition vocabulary come from the selected style anchor.
5. The end card uses the real brand mark and holds long enough for text and spacing to remain legible.

## Failure recovery

- If a reference image cannot be used, stop and ask for a replacement or an explicit text description; do not fall back to a stock brand.
- If a continuation tail frame is missing, stop the chain, identify the missing segment, and regenerate only that segment after its predecessor is stable.
- If a join drifts, preserve the approved brand profile and local motion treatment, then regenerate the affected continuation rather than relabeling a new opening.
- If assembly is unavailable, deliver the ordered clips, planning artifacts, and a clear note that final concatenation and mixing remain.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
