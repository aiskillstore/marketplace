# Agnes AI API Reference

Consolidated reference for the Agnes AI image and video generation APIs, used by the VisionCraft PowerShell scripts.

## Authentication

All requests require:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

Base URL: `https://apihub.agnes-ai.com`

> The API key is read from the `AGNES_API_KEY` environment variable. Never hardcode a key in a script or commit it to git.

---

## Image API

### Endpoint
`POST /v1/images/generations`

### Model
`agnes-image-2.1-flash`

### Capabilities
- **Text-to-image** — generate from a prompt.
- **Image-to-image** — transform an existing image (style transfer, scene edit, local edits) while preserving composition.

### Required Parameters
| Param | Type | Description |
|-------|------|-------------|
| model | string | Must be `agnes-image-2.1-flash` |
| prompt | string | Image description |
| size | string | Output dimensions, e.g. `2048x2048` |

### Optional Parameters
| Param | Type | Description |
|-------|------|-------------|
| image | string[] | Input images for image-to-image (URL or Data URI Base64) — placed inside `extra_body` |
| return_base64 | bool | Return Base64 for text-to-image (top level) |
| extra_body.response_format | string | `url` or `b64_json` |

### Critical Rules (these cause 400 errors if violated)
- **NEVER** put `response_format` at the top level — it goes inside `extra_body`.
- **NEVER** send `tags: ["img2img"]` for image-to-image.
- For text-to-image with URL output: `"response_format": "url"` inside `extra_body`.
- For text-to-image with Base64 output: top-level `"return_base64": true`.
- For image-to-image with Base64 output: `"response_format": "b64_json"` inside `extra_body`.
- Input images accept public HTTPS URLs or `data:image/xxx;base64,...` format.

### Supported Sizes
Preset squares: `1024x1024`, `2048x2048`, `3072x3072`, `4096x4096`.
Plus any custom WxH (e.g. `2048x1152`, `1080x1920`).

### Client Timeout
60–360 seconds. Larger images and complex prompts take longer.

### Pricing
$0.003 per image.

### Error Codes
| Code | Meaning |
|------|---------|
| 400 | Bad request — check params (often a misplaced `response_format`) |
| 401 | Invalid API key |
| 500 | Server error |
| 503 | Service busy |

### Response Format

URL output:
```json
{
  "created": 1780000000,
  "data": [{ "url": "https://storage.googleapis.com/agnes-aigc/xxx.png", "b64_json": null }]
}
```
URL is at `data[0].url`.

Base64 output: same structure, with `b64_json` populated and `url` null.

---

## Video API

The video API is **asynchronous**: create a task, then poll.

### Create Task
`POST /v1/videos`

### Query Result (Recommended)
`GET /agnesapi?video_id={VIDEO_ID}` — poll every 5 seconds.

### Query Result (Legacy)
`GET /v1/videos/{TASK_ID}` — still supported.

### Model
`agnes-video-v2.0`

### Capabilities
| Mode | Input | Use case |
|------|-------|----------|
| Text-to-video | none | Generate from a prompt |
| Image-to-video | 1 image (top-level `image` string) | Animate a static photo |
| Multi-image video | 2+ images (`extra_body.image` array) | Multiple reference images guide generation |
| Keyframe animation | 2+ images + `extra_body.mode = "keyframes"` | **Smooth morph between keyframes** |

### Required Parameters
| Param | Type | Description |
|-------|------|-------------|
| model | string | Must be `agnes-video-v2.0` |
| prompt | string | Video description |

### Optional Parameters
| Param | Type | Description |
|-------|------|-------------|
| image | string | Single image URL for image-to-video (top level) |
| extra_body.image | string[] | Multiple images for multi-image/keyframes |
| extra_body.mode | string | `"keyframes"` for keyframe animation |
| width | int | Video width (default 1920) |
| height | int | Video height (default 1080) |
| num_frames | int | Frame count (must be `8n+1`, ≤ 441) |
| frame_rate | int | FPS 1–60 (default 60) |
| negative_prompt | string | What to avoid |
| seed | int | Reproducibility seed |
| num_inference_steps | int | Inference steps |

### Parameter Standardization
The server normalizes `width`/`height`/aspect ratio to the nearest supported tier (`480p` / `720p` / `1080p`). The output may differ from what you send — **trust the `size` field in the response** for the real resolution.

Supported aspect ratios: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`.

### Frame Count Rules
`num_frames` must satisfy `8n + 1` and be `≤ 441`. Duration = `num_frames / frame_rate`.

| Frames | @ 60 fps | @ 30 fps | @ 24 fps |
|--------|----------|----------|----------|
| 81 | ~1.4s | ~2.7s | ~3.4s |
| 121 | ~2.0s | ~4.0s | ~5.0s |
| 161 | ~2.7s | ~5.4s | ~6.7s |
| **241** | **~4.0s (default)** | ~8.0s | ~10.0s |
| 441 | ~7.4s | ~14.7s | ~18.4s |

### Create Task Response
```json
{
  "id": "task_xxx", "task_id": "task_xxx", "video_id": "video_xxx",
  "object": "video", "model": "agnes-video-v2.0",
  "status": "queued", "progress": 0,
  "seconds": "4.0", "size": "1920x1080"
}
```
`video_id` is the recommended ID for polling.

### Completed Response
```json
{
  "video_id": "video_xxx", "status": "completed", "progress": 100,
  "seconds": "4.0", "size": "1920x1080",
  "remixed_from_video_id": "https://storage.googleapis.com/.../video_xxx.mp4",
  "error": null
}
```
> The final video URL is in `remixed_from_video_id` (despite the misleading name). Only populated when `status` is `completed`.

### Task States
| State | Description |
|-------|-------------|
| queued | Waiting in queue |
| in_progress | Generating |
| completed | Done — URL in `remixed_from_video_id` |
| failed | Error — check `error` field |

### Polling
- Every 5 seconds.
- Typical latency 30–90s (longer for 1080p / high frame counts).
- Script polls up to 15 minutes; on timeout it prints `video_id` for manual re-query.

### Pricing
$0.005 / second — **currently promotional: $0** (free).

### Error Codes
| Code | Meaning |
|------|---------|
| 400 | Bad request |
| 401 | Invalid API key |
| 404 | Task or video not found |
| 500 | Server error |
| 503 | Service busy |
