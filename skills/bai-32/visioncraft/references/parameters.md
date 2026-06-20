# VisionCraft — Script Parameters Reference

Every parameter accepted by the two scripts in `scripts/`, with examples and defaults.

---

## `gen_image.ps1`

Calls `POST /v1/images/generations` with model `agnes-image-2.1-flash`.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `-Prompt` | string | ✅ yes | — | Image description (text-to-image) or transformation instruction (image-to-image). |
| `-Size` | string | no | `2048x2048` | Output dimensions, e.g. `2048x2048`, `2048x1152`. Any custom WxH works. |
| `-Ratio` | string | no | none | Aspect-ratio shortcut. Overrides `-Size`. One of `1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 21:9`. |
| `-ImageUrl` | string | no | none | Public HTTPS URL or `data:image/...;base64,...`. Provide to switch to image-to-image. |
| `-ReturnBase64` | switch | no | off | Return Base64 data instead of a hosted URL. |

### Examples

```powershell
# Text-to-image with defaults (2048x2048)
.\scripts\gen_image.ps1 -Prompt "..."

# 16:9 marketing poster
.\scripts\gen_image.ps1 -Prompt "..." -Ratio 16:9

# Image-to-image (auto-detected when -ImageUrl is provided)
.\scripts\gen_image.ps1 -Prompt "..." -ImageUrl "https://..."

# Custom non-standard size
.\scripts\gen_image.ps1 -Prompt "..." -Size "1536x1024"
```

### Output

On success the script prints a `MEDIA:<url>` line you can pipe to other tools. Base64 output prints the length of the returned string.

---

## `gen_video.ps1`

Asynchronous: `POST /v1/videos` to create a task, then `GET /agnesapi?video_id=...` every 5 seconds until completion.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `-Prompt` | string | ✅ yes | — | Video description. |
| `-Image` | string[] | no | none | One or more image URLs. **1 image** → image-to-video; **2+** → multi-image (default) or keyframes (with `-Mode keyframes`). |
| `-Mode` | string | no | `multi-image` | Only meaningful with 2+ images: `multi-image` or `keyframes`. |
| `-Ratio` | string | no | none | Aspect-ratio shortcut. Overrides `-Width`/`-Height`. One of `16:9, 9:16, 1:1, 4:3, 3:4`. |
| `-Seconds` | double | no | none | Duration shortcut. Auto-calculates `NumFrames` (rounded up to satisfy `8n+1`, capped at 441) using the current `FrameRate`. |
| `-Width` | int | no | `1920` | Video width (used when `-Ratio` not set). |
| `-Height` | int | no | `1080` | Video height (used when `-Ratio` not set). |
| `-NumFrames` | int | no | `241` | Frame count. Must satisfy `8n+1` and be `≤ 441`. Valid: `9, 17, 25, ..., 81, 121, 161, 241, ..., 441`. |
| `-FrameRate` | int (1–60) | no | `60` | FPS. |
| `-Seed` | int | no | none | Random seed for reproducibility. |
| `-NegativePrompt` | string | no | none | What to avoid in the video (e.g. `"blurry, watermark"`). |

### Frame count cheat-sheet

`duration = num_frames / frame_rate`

| Frames | @ 60fps | @ 30fps | @ 24fps |
|--------|---------|---------|---------|
| 81 | ~1.4s | ~2.7s | ~3.4s |
| 121 | ~2.0s | ~4.0s | ~5.0s |
| 161 | ~2.7s | ~5.4s | ~6.7s |
| **241 (default)** | **~4.0s** | ~8.0s | ~10.0s |
| 441 (max) | ~7.4s | ~14.7s | ~18.4s |

### Examples

```powershell
# Defaults: 1920x1080 @ 60fps, 241 frames (~4.0s)
.\scripts\gen_video.ps1 -Prompt "..."

# Vertical short with duration shortcut
.\scripts\gen_video.ps1 -Prompt "..." -Ratio 9:16 -Seconds 8

# Image-to-video
.\scripts\gen_video.ps1 -Prompt "..." -Image "https://example.com/photo.png"

# Multi-image (no -Mode flag = treated as multi-image references)
.\scripts\gen_video.ps1 -Prompt "..." -Image "https://a.png","https://b.png"

# Keyframe animation (smooth A → B morph)
.\scripts\gen_video.ps1 -Prompt "..." -Image "https://a.png","https://b.png" -Mode keyframes

# Cinematic 18s max-length video
.\scripts\gen_video.ps1 -Prompt "..." -NumFrames 441 -FrameRate 24

# Reproducible result
.\scripts\gen_video.ps1 -Prompt "..." -Seed 42

# Avoid common artifacts
.\scripts\gen_video.ps1 -Prompt "..." -NegativePrompt "blurry, distorted faces, watermark, text"
```

### Output

On success the script prints a `MEDIA:<url>` line plus the actual server-reported resolution and duration. On a 15-minute polling timeout it prints the `video_id` and a manual re-query command — the task is **not** abandoned, just slower than the polling window.

### Server-side normalization

The API normalizes `width`/`height` to standard tiers (480p / 720p / 1080p) and the supported aspect ratios. The actual returned resolution may differ slightly from what you sent — the script prints both the requested and the reported size.

---

## Common patterns

| Goal | Flags |
|------|-------|
| 16:9 hero image | `-Ratio 16:9` |
| Social square | `-Ratio 1:1` |
| TikTok / Reels vertical | `-Ratio 9:16 -Seconds 8` |
| Cinematic 10s clip | `-Ratio 16:9 -Seconds 10 -FrameRate 24` |
| Smooth slow-mo (default) | (no flags — defaults are tuned for this) |
| Reproducible iterations | `-Seed 42` (reuse same seed) |
