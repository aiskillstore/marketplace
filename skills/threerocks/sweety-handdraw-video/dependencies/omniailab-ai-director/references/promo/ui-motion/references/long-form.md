---
name: omniailab-promo-ui-motion-long-form
description: 「Long-form (>15s) continuation chains」—— UI 动效与产品演示 方向细则：The base skill has two explicit duration modes. A request up to and in
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Long-form (>15s) continuation chains

The base skill has two explicit duration modes. A request up to and including 15s is one video generation with the user's image as an all-purpose reference and no extra BGM by default. Anything longer uses a **numbered continuation chain**: generate segment 1 through that route, extract and probe its real tail frame, then generate segment 2 from that file. Repeat the tail-frame handoff for every later segment. A later segment is never produced by running the opening procedure again.

The brand-first architecture makes long-form easier: the brand profile + style anchor stay the same. Only the storyboard structure changes (from `narrative` to the `takes` array of numbered segments).

## 30s structure (2 segments × 15s)

```
Segment 1 (15s)
┌────────────────────────────────────┐
│ cold open + reveal + interaction   │  ← beats 1-3
│ + first half of wow beat           │
│ [last frame: a static moment]      │  ← chosen for minimal drift
└────────────────────────────────────┘
                ↓ extract last frame
Segment 2 (15s)
┌────────────────────────────────────┐
│ continuation + end card reveal     │  ← beats 4-5
│ [last frame: end card holding]     │
└────────────────────────────────────┘
                ↓
        ordered concat (sequence 1 → 2)
        generate one BGM after both succeed
        mix with one BGM after both segments succeed, preserving the requested length
```

The seam is invisible when segment 1 ends on a **static moment** (held pose, ribbon fully spread, glyph at rest). The video model continues from that exact frame with minimal drift.

## 60s structure (4 segments × 15s)

For 60s, use 4 segments of 15s with 3 seams. Apply the static-end rule at every seam. The `motion_prompt` for each segment covers only that segment's local story; it must not pretend that a new opening is being generated.

For 30s stories that work:

- **Tutorial**: show 3 features sequentially, each with a real product asset
- **Comparison**: split-screen "before / after" using two half-frame panels, both in the brand colors
- **Documentary**: layer a narrator voice over the visuals (see Voice-over below)

## Voice-over

If the user wants narration, record the chosen voice direction, exact text, and resulting `audio/vo.mp3` alongside the storyboard. The final assembly keeps narration clearly above BGM and preserves the requested timing.

## Music length and timing

For any output longer than 15s, wait for every numbered segment to succeed and for every join to pass the tail-frame check. Then make exactly one instrumental BGM from the brand profile and full-film energy timeline, record the returned actual duration, and use another supported model only when the user explicitly requests it.

For outputs up to and including 15s, do not call the music generation by default. The absence of `music` in the storyboard is intentional, not a missing step.

The music prompt should still be derived from the brand profile. A longer piece has more time to develop—the same brand mood, but with longer phrasing, more harmonic movement, section-level energy changes, and an explicit ending.

## Brand profile stability across long-form

The brand profile is the *constant* across a 30s or 60s video. You don't re-extract the brand profile per segment — the same `brand_profile.json` drives all of them. The brand's color names, typography, photography mood are stable inputs.

## Avoiding drift at the seams

Four rules keep the numbered continuation seamless:

1. **End segment N on a static moment** — held pose, fully-spread ribbon, glyph at rest. The model has nothing stable to continue if the frame is dynamic, so it invents motion that doesn't match.
2. **Persist the lineage before generating segment N+1** — set the next sequence number, name its predecessor, and point its starting image at segment N's extracted, probed tail frame.
3. **Keep the motion_prompt for segment N+1 focused on the local beat** — "from this static frame, fade to background and reveal the end card" — not a recap or a new opening.
4. **If drift appears, regenerate segment N+1 only** — segment N is fine. Do not re-roll the whole chain or substitute the original reference image.

## Structure extension

The base `storyboard.json` already supports the long-form case via the optional `takes` array. The version stays at `4`. Keep the brand fields unchanged and retain enough lineage information to identify each segment, its predecessor, its input tail frame, its output clip, and its extracted tail frame.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
