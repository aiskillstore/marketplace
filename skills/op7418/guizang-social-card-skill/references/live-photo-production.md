# Live Photo Production Workflow

This note records the workflow for making Xiaohongshu / Rednote and WeChat Official Account style `3:4` Live Photo assets from supplied videos, screen recordings, or rendered social-card videos.

## Contents

- When To Use Live Photo
- Key Finding
- Recommended Output
- Visual Format
- Live Photo Information Budget
- Triple Live Photo Collage
- Material-First Puzzle Layouts
- Long Video Intake
- Intake Decision Tree
- Video As Image-Well Replacement
- Preview-First Workflow
- Contact-Sheet Inspection Algorithm
- Validation
- iPhone Test
- Platform Notes
- Troubleshooting

## When To Use Live Photo

Use Live Photo when the user explicitly asks for `Live Photo` / `实况照片`, or when they ask to make a social card from video素材 and the motion is the proof.

The normal production path uses user-supplied videos, screen recordings, or product demos. Web-sourced free videos are only for making our own demo/promo cases, or when the user explicitly asks for sourced example material.

Core principle: Live Photo does not tell a complete long story. It proves one moment, one small process, one before/after change, or a compact set of parallel results.

Audience-facing copy should name the real scene in the video. Do not put internal production labels in the H1 or main copy: `3s`, `5s`, `Live Photo`, `triple collage`, `long-video intake`, `information budget`, `speed-up`, `highlight detection`, and `one action point` belong in planning notes, filenames, QA summaries, or delivery text. The visible card should read like the user posted it for their audience, not like the agent is explaining how it was made.

User problems this feature solves:

- **Compress motion into a carousel card**: a user can publish code generation, UI interaction, game demo, before/after state, or scroll reveal inside a normal image carousel instead of switching to a pure video post.
- **Preserve the Skill's layout quality**: the poster still follows the existing 3:4 visual system; only the image well becomes a video well.
- **Preview before spending render/model budget**: the agent can extract the video first frame, place it as a still image, and confirm the layout before producing a MOV or `.pvt`.
- **Handle overlong clips**: the agent can decide whether to trim, speed up, or combine both, instead of forcing the user to pre-edit every source.
- **Make evidence readable**: the agent crops video like it crops images, enlarging the important UI/counter/result area instead of dropping in a tiny full-screen recording.
- **Avoid platform gotchas**: the agent outputs `.pvt` for iPhone/AirDrop and respects platform duration limits.
- **Explain the publish path**: users learn that `.pvt` must be transferred to iPhone and published from the mobile app path, not from desktop/web upload.
- **Provide graceful fallbacks**: if WeChat web upload is required, the same source can become GIF/short video while the static card remains usable.

## Key Finding

Do not AirDrop a plain `JPG + MOV` pair as separate files and expect iPhone Photos to merge them automatically.

Even when both files contain matching Apple Live Photo metadata, the normal multi-file AirDrop path can import them as separate assets. For reliable testing and transfer, package the pair as a single `.pvt` bundle.

## Recommended Output

For each Live Photo, generate these deliverables:

```text
local-tests/<slug>/output/
  IMG_<slug>_LIVE.JPG       # 1080 x 1440 key photo / cover frame
  IMG_<slug>_LIVE.MOV       # platform-duration paired video
  IMG_<slug>_LIVE.pvt/      # AirDrop-friendly Live Photo package
    IMG_<slug>_LIVE.JPG
    IMG_<slug>_LIVE.MOV
    metadata.plist
```

Use the `.pvt` package for AirDrop tests. Use the `JPG + MOV` pair as source/debug artifacts.

If both Xiaohongshu and WeChat are requested, export separate platform files so the user knows what to upload:

```text
IMG_<slug>_XHS_5S_LIVE.*
IMG_<slug>_WECHAT_3S_LIVE.*
```

## Visual Format

Default Xiaohongshu Live Photo card:

- Canvas: `1080 x 1440`
- Ratio: `3:4`
- Duration: `5s`
- FPS: `24-30` for screen recordings; `12-15` is acceptable for simple animated graphics.
- Codec: H.264 MOV
- First frame: a valid static social card state with no excessive crop.
- Key photo: a readable representative frame from the confirmed layout. It may be the first frame or a later stronger result frame, but it must use the same crop and composition.

Default WeChat Official Account Live Photo card:

- Canvas: `1080 x 1440`
- Ratio: `3:4`
- Duration: `3s`
- Upload path: iPhone only; web upload should use GIF/short-video fallback.

For a "triple test" card:

- Top: title and short thesis.
- Middle: three horizontal result strips.
- Each strip should show one generated result, not only code.
- Add compact labels such as `01 / 3D SPACE GAME`, `02 / AI INFERENCE WEBSITE`, `03 / SPACE TRAVEL WEBSITE`.
- The static key photo must be useful even when motion is not supported.

## Live Photo Information Budget

Judge how much source material can fit before designing the layout.

| Format | Time budget | Best for | Avoid |
| --- | --- | --- | --- |
| WeChat single Live Photo | `3s` | one action point, one tap result, one before/after reveal | multi-step tutorials, long scrolls, three unrelated clips |
| Xiaohongshu single Live Photo | `5s` | one small process, short product interaction, key game move, generation-to-result proof | full story arcs, dense narration, long setup before the result |
| Triple Live Photo collage | `3-5s` per exported asset, three wells inside one card | three parallel results, three viewpoints, three examples, wrong/fix/result | a sequential process that needs the viewer to read all three wells in order |
| Material-first puzzle | `3-5s` | high-quality footage where the image is the content: single video, two-grid, three-grid, or four-grid motion cards | forcing explanatory text, labels, or diagrams onto beautiful footage |
| Long source video | source is much longer than target | diagnosis, trim, speed-up, split, or user-specified range | blindly compressing the entire clip into `3s` or `5s` |

Use this motion-role vocabulary when planning:

- **Operation proof**: show the exact action and resulting state.
- **Process compression**: show a small transformation from start to result.
- **Before/after**: make the difference credible by showing the transition.
- **Parallel evidence**: show multiple outcomes side by side.
- **Atmosphere supplement**: static card carries the information; motion adds place, texture, or realism.

If the source video carries more than one of these roles, pick the strongest one or split it. Do not overfill a single Live Photo.

## Triple Live Photo Collage

Use a triple collage when the user has three short videos, three generated results, three product states, three gameplay clips, or three viewpoints that are stronger together than as separate pages.

Recommended structures:

1. **Pure three-column / three-strip video collage**: almost no text; use when the clips themselves are the content.
2. **Title + three videos**: one hook at top, three labeled wells below; good for Rednote first-card use.
3. **Editorial mixed collage**: asymmetric wells plus labels, short conclusions, or numbered captions; good for tutorials, guides, and product updates.

Judge the relationship between the three clips before choosing geometry:

- **Parallel comparison**: A / B / C.
- **Process stages**: before / during / after.
- **Result showcase**: three generated or tested outputs.
- **Correction flow**: wrong / fix / result.
- **Multi-view**: overview / detail / result.

Keep labels short: `01 / SETUP`, `02 / ACTION`, `03 / RESULT`. Do not turn the collage into three tiny full-screen recordings. Crop each well around the evidence area.

## Material-First Puzzle Layouts

Use this when the user supplies good footage and wants the Live Photo to behave like a moving photo layout, not a text card. The key choice is geometry, not copywriting.

Supported shapes:

- **Single video**: crop one clip to `3:4` full canvas. Add at most one short headline, placed in a confirmed quiet zone away from faces, bodies, hands, products, or key motion. If text is added, it must follow the M16 Image-Led Cover / text-on-image typography: Editorial serif/Songti, regular-medium weight, paper-cream color, restrained tracking, and no default full-canvas mask. Do not invent extra kicker, meta, hairlines, labels, or badges just to make the overlay feel designed. If only one headline is available, make the typography carry the layout: phrase-aware line break, restrained size, tracking, alignment, and placement.
- **Two-grid**: stack two clips vertically. Use no added text unless the user asks.
- **Three-grid**: stack three clips vertically. Use no added text; the rhythm comes from the footage.
- **Four-grid**: use a `2 x 2` grid of four `3:4` wells (`540 x 720` each inside a `1080 x 1440` card). Crop each source as a real `3:4` material, not as a tiny landscape thumbnail.

Rules:

- Do not add template filler: no labels, numeric tags, rulers, badges, subtitles, or explanatory production copy.
- Source-embedded text is part of the footage. Do not add new text on top of it unless requested.
- Keep gutters at `0-12px`; choose no gutter when the user asks for pure 拼图 or the source already has strong edges.
- Generate source contact sheets first, then choose crop positions. For people, protect faces and upper body; for objects, protect the focal feature.
- For single-video text, follow `image-overlay.md`: subject map first, no full-canvas mask, title in one quiet zone, and thumbnail readability check.
- Do not render single-video text as generic subtitles. It should look like an Editorial image-led cover title, not video captioning.
- Do not confuse "minimal copy" with permission to invent copy. Minimal copy still needs typography and a deliberate relation to the subject, but the agent must not add new visible words unless the user asks.
- If a crop cannot preserve the subject, prefer a different puzzle geometry over forcing a bad crop.

## Long Video Intake

For long user videos, do not promise precise automatic highlight detection. Use a low-cost diagnosis first, then make a recommendation.

Low-cost diagnosis:

1. Probe duration, resolution, frame rate, and audio presence with `ffprobe`.
2. Generate a sparse contact sheet:
   - `8-12` frames for an initial long-source scan.
   - `12-15` frames for a candidate 5-second window.
   - `8-12` frames for a candidate 3-second window.
3. Inspect only the contact sheet unless the user asks for deeper analysis.
4. Identify obvious structure only: black/blank intro, static stretches, large section changes, visible result frame, or multiple separate moments.

Recommendation types:

- **Trim**: use one stable time window at normal speed.
- **Speed-up + trim**: preserve a short process when readability is still acceptable.
- **Split / triple collage**: use multiple parallel moments instead of compressing a long story.
- **Ask for range**: when the contact sheet cannot reveal the intended highlight.
- **Reject Live Photo**: when the material needs narration, audio, or a long sequence; suggest short video/GIF instead.

Useful response pattern:

```text
我先粗看了这个视频的信息量。它不适合整段压进 5 秒。
建议有两种：
A. 裁 00:04-00:09，保留关键操作和结果
B. 拆成三连 Live Photo：准备 / 操作 / 结果
你想走哪一种？
```

## Tooling

Primary tool:

- [`RhetTbull/makelive`](https://github.com/RhetTbull/makelive)

Why this tool:

- It writes the Apple Live Photo content identifier metadata into both photo and video resources.
- It can create a `.pvt` package via `save_live_photo_pair_as_pvt`.
- The `.pvt` package is specifically useful for AirDrop and other transfer paths that may not preserve a loose photo/video association.

Install or run with `uv`:

```bash
uvx --from 'makelive==0.7.0' makelive IMG_TEST_LIVE.JPG IMG_TEST_LIVE.MOV
```

Pin the version (`0.7.0` as of 2026-07) to avoid breakage from API changes in this small-audience package.

For `.pvt`, use the Python API:

```bash
uvx --from makelive python -c "from makelive import save_live_photo_pair_as_pvt; asset_id, pvt_path = save_live_photo_pair_as_pvt('IMG_TEST_LIVE.JPG', 'IMG_TEST_LIVE.MOV'); print(asset_id); print(pvt_path)"
```

If running inside a restricted sandbox, set writable cache/tool directories:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache \
UV_TOOL_DIR=/private/tmp/uv-tools \
uvx --from makelive python -c "from makelive import save_live_photo_pair_as_pvt; asset_id, pvt_path = save_live_photo_pair_as_pvt('IMG_TEST_LIVE.JPG', 'IMG_TEST_LIVE.MOV'); print(asset_id); print(pvt_path)"
```

This repo also includes a generic wrapper:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache \
UV_TOOL_DIR=/private/tmp/uv-tools \
uvx --from makelive python scripts/package-live-photo.py IMG_TEST_LIVE.JPG IMG_TEST_LIVE.MOV
```

Use this wrapper when available so every run prints the asset id and `.pvt` path consistently.

### Swift Metadata Helpers

When `makelive` is unavailable or you need to add Apple Live Photo metadata manually, the repo includes two Swift scripts. They require macOS with the system Swift toolchain (Xcode or Command Line Tools) and AVFoundation.

Write the MakerNote asset identifier into a JPEG:

```bash
swift scripts/add-livephoto-maker-note.swift input.jpg output.jpg <asset-id>
```

Write the QuickTime content identifier and still-image-time metadata into a MOV:

```bash
swift scripts/add-livephoto-mov-metadata.swift input.mov output.mov <asset-id>
```

Both scripts must receive the same `<asset-id>` (a UUID string) so iPhone Photos pairs the JPG and MOV as one Live Photo. Normally `makelive` handles this automatically; the Swift scripts are a fallback for environments where Python/uvx is blocked.

## Intake Decision Tree

When the user provides video assets:

1. Identify target platform:
   - Xiaohongshu / Rednote → `5s`
   - WeChat Official Account → `3s`
2. Classify the likely format:
   - single Live Photo
   - triple Live Photo collage
   - long-video intake
3. Probe each source:
   - duration
   - width / height
   - frame rate
   - whether the clip contains multiple sections, transitions, or scroll boundaries
4. If the source is long or ambiguous, generate a sparse contact sheet first. Do not inspect dense frame sequences unless the user explicitly needs precision.
5. If the source is longer than the platform duration, give a recommendation and ask one concise question unless the intended moment is obvious:

   ```text
   这个视频比平台 Live Photo 时长长。粗看更适合：
   A. 裁一段，保持原速
   B. 加速 + 裁切，保留更多过程
   C. 拆成三连 Live Photo
   ```

6. If the source is shorter than the platform duration, do not silently pad and call it dynamic. Choose one:
   - ask for a longer source
   - use the shorter platform-safe duration
   - hold the final frame and state that it is a hold
7. If the source has a visible section transition or page scroll boundary, choose a stable time window or slow the segment slightly. Do not let two sections occupy a shallow crop at once.
8. If the important visual focus is ambiguous, do not guess. Ask whether the user wants readability-focused enlargement, full-context preservation, or a balanced crop.

Useful short-source prompt:

```text
这个素材短于目标 Live Photo 时长。你想：
A. 换一个更长素材
B. 直接做成较短的 Live Photo
C. 允许末帧停住 / 轻微慢放，并在交付时说明
```

Useful focus/crop prompt:

```text
这个视频可以有两种处理：
A. 放大关键区域，数字 / UI 更清楚，但会少一点全局上下文
B. 保留完整画面，信息更全，但手机上细节会小一些
你更想突出哪一个？
```

## Video As Image-Well Replacement

Treat video wells like image wells:

- Keep the original card layout, margins, labels, typography, and style mode.
- Apply the same crop logic to video that you would apply to a still image.
- The video first frame must look like a finished static card image. Before rendering the MOV, extract the first frame, place it in the card, and verify:
  - no important UI/text/product/detail is over-cropped
  - the crop follows the original image-well rule and safe area
  - the surrounding title/body/layout still match the chosen recipe
  - the card works as a still image if motion is unavailable
- Use `object-fit: cover` equivalent behavior with ffmpeg: crop first, then scale to the image well.
- Use `object-fit: contain` equivalent behavior when dense UI text must remain readable: scale with letterboxing or enlarge the well rather than cutting important UI.
- Choose a representative key frame after the video crop is final; the still image must be useful even if motion playback fails.
- Treat "可图性提升" as an option, not an automatic fix. If the source would benefit from zooming in, sharpening, slowing, or making a video well larger, suggest it and wait for the user when the focal priority is not obvious.

## Preview-First Workflow

Always confirm the static version before producing the Live Photo package. This saves tokens and render time because the expensive motion path runs only after the layout/crop is accepted.

1. Extract the first frame from each video source or chosen time window:

   ```bash
   ffmpeg -y -ss <start_seconds> -i source.mp4 \
     -frames:v 1 -q:v 2 assets/source-first-frame.jpg
   ```

2. Use that frame exactly like a supplied image inside the normal `3:4` card template. Apply the same crop, object position, title spacing, safe area, and density rules as static cards.
3. Render a static PNG preview of the card. Inspect it and, when working interactively, show it to the user before rendering video.
4. Only after the user accepts the preview, render the platform-duration MOV using the same crop coordinates and layout geometry.
5. Extract the key JPG from the rendered MOV. Prefer a frame that is readable and strong as a static card while remaining faithful to the confirmed crop.

Do not use a separate "video layout" that differs from the static preview. The preview is the contract.

## Contact-Sheet Inspection Algorithm

Use contact sheets to inspect motion cheaply. Generate the tiled frame strip with command-line tools, then inspect only the final composite image. This avoids loading many individual frames into the model context and makes visual QA much faster.

Algorithm:

1. Probe the output duration with `ffprobe`.
2. Choose the inspection window:
   - final MOV → full platform duration
   - source clip with suspected issue → the candidate trim window
3. Choose `N` frames. Use `8-12` for a 3-second asset and `12-15` for a 5-second asset.
4. Compute sample rate as `N / window_duration`.
5. Use ffmpeg to sample, scale each frame to a fixed thumbnail width, and tile into `cols x rows`.
6. Inspect the resulting JPG/PNG for:
   - over-cropped first frame
   - section-boundary overlap
   - unreadable counters or UI text
   - frozen areas caused by padding short clips
   - unexpected black bars or aspect-ratio changes

Generic command:

```bash
ffmpeg -y -ss <start_seconds> -t <window_seconds> -i input.mov \
  -vf "fps=<frame_count>/<window_seconds>,scale=320:-1:flags=lanczos,tile=<cols>x<rows>:padding=12:margin=12:color=white" \
  -frames:v 1 contact-sheet.jpg
```

Examples:

```bash
# 3-second WeChat Live Photo, 9 frames
ffmpeg -y -t 3 -i IMG_LIVE.MOV \
  -vf "fps=9/3,scale=320:-1:flags=lanczos,tile=3x3:padding=12:margin=12:color=white" \
  -frames:v 1 contact-wechat.jpg

# 5-second Xiaohongshu Live Photo, 15 frames
ffmpeg -y -t 5 -i IMG_LIVE.MOV \
  -vf "fps=15/5,scale=320:-1:flags=lanczos,tile=5x3:padding=12:margin=12:color=white" \
  -frames:v 1 contact-xhs.jpg
```

This repo includes a wrapper with the same logic:

```bash
python scripts/make-video-contact-sheet.py IMG_LIVE.MOV contact-xhs.jpg --frames 15 --cols 5 --duration 5
```

## Example: Render A 3:4 MOV

This example combines three existing landscape screen recordings into one vertical `3:4` Live Photo source movie.

```bash
ffmpeg -y \
  -ss 145 -t 3 -i "Area测试 01.mp4" \
  -ss 49 -t 3 -i "Area 测试 2.mp4" \
  -ss 154 -t 3 -i "Area 测试 3.mp4" \
  -i overlay.png \
  -filter_complex "color=c=0x030611:s=1080x1440:d=3:r=15[bg];[0:v]fps=15,crop=1580:980:344:60,scale=1000:330:force_original_aspect_ratio=increase,crop=1000:330,setsar=1[g];[1:v]fps=15,scale=1000:330:force_original_aspect_ratio=increase,crop=1000:330,setsar=1[a];[2:v]fps=15,scale=1000:330:force_original_aspect_ratio=increase,crop=1000:330,setsar=1[s];[bg][g]overlay=40:190[p1];[p1][a]overlay=40:590[p2];[p2][s]overlay=40:990[p3];[p3][3:v]overlay=0:0" \
  -t 3 -r 15 -an -c:v libx264 -pix_fmt yuv420p -movflags +faststart \
  IMG_TEST_LIVE_RAW.mov
```

If `ffmpeg` lacks `drawtext`, create text and border overlays as a transparent PNG with ImageMagick, then overlay that PNG in the video render.

## Extract The Key Photo

Pick the final readable frame as the still image:

```bash
ffmpeg -y \
  -ss 2.7 -i IMG_TEST_LIVE_RAW.mov \
  -frames:v 1 -q:v 2 \
  IMG_TEST_LIVE.JPG
```

Copy or rename the raw MOV:

```bash
cp IMG_TEST_LIVE_RAW.mov IMG_TEST_LIVE.MOV
```

Then create the `.pvt` package:

```bash
uvx --from makelive python -c "from makelive import save_live_photo_pair_as_pvt; asset_id, pvt_path = save_live_photo_pair_as_pvt('IMG_TEST_LIVE.JPG', 'IMG_TEST_LIVE.MOV'); print(asset_id); print(pvt_path)"
```

## Validation

Check dimensions and duration:

```bash
ffprobe -v error \
  -show_entries stream=width,height,r_frame_rate \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 \
  IMG_TEST_LIVE.MOV
```

Expected:

```text
width=1080
height=1440
r_frame_rate=<chosen fps>
duration=<platform duration>
```

Inspect the `.pvt` package:

```bash
find IMG_TEST_LIVE.pvt -maxdepth 2 -type f -print
plutil -p IMG_TEST_LIVE.pvt/metadata.plist
```

Expected package shape:

```text
IMG_TEST_LIVE.pvt/IMG_TEST_LIVE.JPG
IMG_TEST_LIVE.pvt/IMG_TEST_LIVE.MOV
IMG_TEST_LIVE.pvt/metadata.plist
```

Then create a contact sheet from the final MOV and inspect that one image:

```bash
python scripts/make-video-contact-sheet.py IMG_TEST_LIVE.MOV contact-final.jpg --frames 15 --cols 5 --duration 5
```

For WeChat `3s`, use fewer frames:

```bash
python scripts/make-video-contact-sheet.py IMG_TEST_LIVE.MOV contact-final.jpg --frames 9 --cols 3 --duration 3
```

The first tile should satisfy the static card rules. The later tiles should show motion without section-boundary overlap, unintended freezes, or unreadable focal content.

## iPhone Test

Use AirDrop with the package:

1. In Finder, select `IMG_TEST_LIVE.pvt` as one item.
2. AirDrop it to the iPhone.
3. Open Photos and verify that it imports as one Live Photo asset.
4. Press and hold to confirm motion playback.
5. Publish from the iPhone app path: Xiaohongshu app for Rednote, or the iPhone Official Account article editing path for WeChat.

Avoid selecting these together for the transfer:

```text
IMG_TEST_LIVE.JPG
IMG_TEST_LIVE.MOV
IMG_TEST_LIVE_RAW.mov
```

That path may produce three separate iPhone Photos assets.

Do not promise desktop publishing for `.pvt`. Current practical path:

```text
Mac Finder -> AirDrop .pvt as one item -> iPhone Photos -> publish from mobile app
```

Computer-side upload paths generally treat `.pvt` as an unknown package or separate source files, so they cannot be used as the primary Live Photo publishing workflow.

## Platform Notes

### Xiaohongshu / Rednote

Use Live Photo as the first card when the motion itself is the hook.

Duration:

- Use `5s` unless the user asks for a shorter asset.
- If a source is longer, prefer trim-only for readable demos; use speed-up + trim when the user wants to preserve more process.
- If a source is shorter, ask for more source or clearly document any hold frame.

Good first-card structure:

- Static cover is clear at thumbnail size.
- Motion reveals code speed first, then runnable results.
- The final frame is the strongest result state.

For a mixed post:

1. Static `3:4` cover.
2. Text + image explanation card.
3. Triple-result Live Photo.
4. Individual result cards.
5. Speed / evaluation matrix.

### WeChat Official Account

WeChat Official Account Live Photo support is upload-path dependent.

Observed behavior:

- iPhone upload can preserve Live Photo.
- Web upload does not expose the same Live Photo path.
- Keep Live Photo duration at or below `3s`.

Recommended fallback:

- Keep static `3:4` images for article body cards.
- Use GIF or short video when a desktop/web publishing path is required.
- Use Live Photo from iPhone when the motion card is important.

## Optional Local Scripts

This repo includes two small Swift helpers created during testing:

- `scripts/add-livephoto-maker-note.swift`
- `scripts/add-livephoto-mov-metadata.swift`

They can write Apple-style identifiers and timed metadata manually, but the recommended production path is still `makelive`, because it also creates the `.pvt` package needed for AirDrop-style transfer tests.

Use the Swift helpers only when debugging metadata or when `makelive` is unavailable.

## Troubleshooting

If iPhone Photos shows separate JPG and MOV assets:

- You probably AirDropped loose files, not the `.pvt` package.
- Recreate the `.pvt` using `save_live_photo_pair_as_pvt`.
- AirDrop only the `.pvt` item.

If the Live Photo imports but does not animate:

- Keep duration within the target platform limit: `5s` for Xiaohongshu, `3s` for WeChat Official Account.
- Use H.264 MOV and `yuv420p`; use `24-30fps` for screen recordings and `12-15fps` for simple graphics.
- Make sure the key photo and MOV came from the same canvas ratio and dimensions.
- Rebuild with `makelive` so identifiers are consistent.

If `uvx` fails inside a sandbox:

- Use writable `UV_CACHE_DIR` and `UV_TOOL_DIR`.
- If the failure is network or macOS system-configuration related, run it outside the sandbox with user approval.

If the result/demo region looks like two videos overlap:

- First inspect the source clip contact sheet. If the source scrolls between webpage sections, a shallow crop can show the end of one section and start of the next at the same time.
- Do not fix this by adding masks or more overlays.
- Choose a better time window, make the result well taller, or slow a shorter stable segment into the target duration.
- For webpage demos, keep Hero visible briefly, then allow controlled scroll. Avoid spending the whole Live Photo on Hero unless the Hero itself is the result.

## Case Study: MIMO UltraSpeed Card Lessons

This section records the issues found while producing the MIMO UltraSpeed Xiaohongshu / WeChat Live Photo card. Keep it as the reusable checklist for future screen-recording based Live Photos.

### Final Working Layout

The accepted card used a Swiss International treatment:

- Canvas: `1080 x 1440`, `3:4`
- FPS: `30`
- Codec: H.264 MOV, `yuv420p`
- Background: off-white `#fafaf8`
- Accent: IKB blue `#002FA7`
- Structure:
  - Top: short title and one-line context.
  - Middle-small: process / token speed strip.
  - Bottom-large: result demo strip.
  - Footer: compact factual stats.

The accepted geometry was:

```text
token strip:  x=64, y=360, w=956, h=327
result strip: x=64, y=744, w=956, h=595
```

The important editorial decision: **the result demo should be the larger evidence block**. The token strip only needs to prove speed and motion; it should not dominate the page.

### Do Not Add Synthetic Metrics

For speed tests, do not invent a large extra number beside the source recording.

Bad:

- Add a separate animated counter.
- Re-type `tokens/s` as a designed KPI block while the real platform counter is already visible.

Good:

- Crop the real platform speed panel from the source video.
- If clarity is poor, enlarge the crop and sharpen it lightly.
- Keep the source UI as evidence; do not replace it with a decorative metric.

### Static Preview Before Live Photo

For video cards, first generate a static preview frame and confirm the crop. Do not jump straight to `.pvt`.

Recommended preview process:

```bash
mkdir -p /private/tmp/mimo-check

ffmpeg -y -i "process.mp4" \
  -vf "fps=1,scale=481:-1,tile=6x1" \
  -frames:v 1 /private/tmp/mimo-check/process_contact.jpg

ffmpeg -y -i "result.mp4" \
  -vf "fps=1,scale=481:-1,tile=6x1" \
  -frames:v 1 /private/tmp/mimo-check/result_contact.jpg
```

Inspect these contact sheets before choosing crop coordinates. For this MIMO case, skipping this step caused several rounds of wrong crops.

### Token Strip Crop

Problem observed:

- The first token strip crop preserved too much browser whitespace.
- The actual `tokens/s` number was tiny and blurry.
- A later crop preserved only the number, but lost the sense that code was being generated.

Accepted compromise:

- Crop the bottom of the code pane plus the real `tokens/s` panel.
- Keep a little generated text above the speed number.
- Avoid the later part of the recording if it switches into the right-side preview pane.

Final crop used for the `1924 x 1080` process recording:

```text
crop=760:260:690:715
scale=956:327
unsharp=5:5:0.45
```

Example filter:

```bash
ffmpeg -y -t 5 -i "5 秒-过程.mp4" \
  -vf "fps=30,trim=0:5,setpts=PTS-STARTPTS,crop=760:260:690:715,scale=956:327:flags=lanczos,unsharp=5:5:0.45,setsar=1" \
  token-preview.mov
```

Notes:

- If the source recording is low bitrate, enlarging helps composition but cannot restore true detail.
- Prefer a fresh high-bitrate screen recording over over-sharpening.
- If the target duration is longer than the usable process segment, ask for a longer source or explicitly document any hold frame. Do not silently pad still frames and describe it as fully dynamic.

### Result Demo Crop

Problem observed:

- Cropping the result demo into a short horizontal strip made webpage section transitions look like overlapping videos.
- The source webpage scroll can naturally show two sections at once near boundaries. A very shallow crop exaggerates this and makes it look broken.
- Scaling with `force_original_aspect_ratio=increase` plus a tight vertical crop can change the apparent scroll rhythm.

Accepted approach:

- Give the result demo a larger region.
- Preserve the full vertical structure of the source as much as possible.
- For `16:10` style recordings, use full-frame scaling when possible.
- If the source width changes, center-crop only the horizontal edges, not the vertical content.
- Time-window selection matters as much as crop. If a 5-second source contains Hero → scroll → data section, choose a window that shows the intended story without crossing section boundaries too abruptly.

For the newer `1924 x 1080` 5-second result source, the accepted crop was:

```text
crop=1736:1080:88:0
scale=956:595
```

This center-crops the wider screen recording to match the previous 16:10-ish view before scaling into the card.

For already-cropped `1736 x 1080` result sources, do not apply the `x=88` center crop again. Use:

```text
crop=1736:1080:0:0
scale=956:595
```

Observed fixes from the MIMO tests:

- Test 1 had a title/start screen before the game. Fix: skip the first `0.35s` so the Live Photo starts on the real game result.
- Test 2 had a long Hero plus scroll. A full `0-5s` window made section boundaries look overlapped; a pure `0-2.8s` window removed the scroll. Fix: take `1.0-5.2s` and lightly stretch it to `5s`, preserving Hero briefly and then scrolling.
- Test 3 was stable because its first seconds stayed mostly on the Hero/result state.

Example timing filters:

```text
# Trim only, normal speed
trim=start=0:end=5,setpts=PTS-STARTPTS

# Skip an intro frame before a game/demo starts
trim=start=0.35:end=5.35,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.5

# Preserve a later webpage scroll while fitting 4.2s into a 5s Live Photo
trim=start=1.0:end=5.2,setpts=(5/4.2)*(PTS-STARTPTS)
```

### Duration Rule

Always verify source duration before promising a Live Photo duration:

```bash
ffprobe -v error \
  -show_entries format=filename,duration,size \
  -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,duration \
  -of json "source.mp4"
```

For a 5-second Live Photo, both visual tracks should ideally be at least 5 seconds.

Acceptable alternatives only if stated clearly:

- Top process video holds the final frame after its usable segment.
- Top process video continues into preview mode.
- Use a shorter Live Photo duration.

Do not call a file "true 5 seconds" if one track is mostly padded. Validate the output with frame counting:

```bash
ffprobe -v error -count_frames -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,duration,nb_read_frames \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 \
  IMG_MIMO_AD_V3_5S_LIVE.MOV
```

Expected for 5 seconds at 30fps:

```text
width=1080
height=1440
r_frame_rate=30/1
duration=5.000000
nb_read_frames=150
```

### Final 5-Second MIMO Command Pattern

This pattern combines a 5-second process recording and a 5-second result recording into the accepted card layout.

```bash
ffmpeg -y \
  -t 5 -i "5 秒-过程.mp4" \
  -t 5 -i "5 秒-结果.mp4" \
  -i overlay.png \
  -filter_complex "color=c=0xfafaf8:s=1080x1440:d=5:r=30[bg];[0:v]fps=30,trim=0:5,setpts=PTS-STARTPTS,crop=760:260:690:715,scale=956:327:flags=lanczos,unsharp=5:5:0.45,setsar=1[token];[1:v]fps=30,trim=0:5,setpts=PTS-STARTPTS,crop=1736:1080:88:0,scale=956:595:flags=lanczos,setsar=1[result];[bg][token]overlay=64:360[p1];[p1][result]overlay=64:744[p2];[p2][2:v]overlay=0:0" \
  -t 5 -r 30 -an -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart \
  IMG_MIMO_AD_V3_5S_LIVE.MOV
```

Then extract the key image and create `.pvt`:

```bash
ffmpeg -y -ss 0.8 -i IMG_MIMO_AD_V3_5S_LIVE.MOV \
  -frames:v 1 -q:v 2 IMG_MIMO_AD_V3_5S_LIVE.JPG

UV_CACHE_DIR=/private/tmp/uv-cache \
UV_TOOL_DIR=/private/tmp/uv-tools \
uvx --from makelive python -c "from makelive import save_live_photo_pair_as_pvt; asset_id, pvt_path = save_live_photo_pair_as_pvt('IMG_MIMO_AD_V3_5S_LIVE.JPG', 'IMG_MIMO_AD_V3_5S_LIVE.MOV'); print(asset_id); print(pvt_path)"
```

### Failure Modes And Fixes

| Failure | Likely cause | Fix |
| --- | --- | --- |
| Result demo appears to overlap | Crop is too shallow; source page is crossing section boundaries | Make result area taller; preserve full vertical source; inspect contact sheet |
| Result demo feels frozen | A short source window was stretched too much | Use a later/larger time window, or trim only |
| Token number is unreadable | Crop contains too much empty browser space or source is low bitrate | Crop closer around the real platform counter; request higher-bitrate source if needed |
| Token strip loses "generation" feeling | Crop only shows the numeric panel | Include the bottom of the generated code pane above the speed number |
| 5-second output plays but one area freezes | One source clip is shorter than target duration or was padded with `tpad` | Use true 5-second source clips or explicitly label the hold |
| iPhone imports separate files | Loose JPG/MOV were AirDropped | AirDrop only the `.pvt` package |
| Style feels off-brand | The card ignores this skill's Swiss rules | Use off-white, black, one IKB accent, straight modules, no shadow/glass/rounded cards |

### Reusable Rule Of Thumb

For social-card Live Photos built from screen recordings:

1. Inspect source duration, resolution, and bitrate first.
2. Create contact sheets before choosing crops.
3. Produce a static preview before `.pvt`.
4. Make the result/demo area the main visual evidence.
5. Keep the process/token area small but legible.
6. Preserve real UI counters instead of designing fake ones.
7. Validate frame count after rendering.
8. Package with `.pvt` for AirDrop tests.
