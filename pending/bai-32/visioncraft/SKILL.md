---
name: visioncraft
description: |
  Generate images and videos via Agnes AI. Triggers on any request to create, draw, render, design, edit, restyle, or animate visual content — pictures, posters, illustrations, product visuals, photos, or video clips. Handles text-to-image, image-to-image, text-to-video, image-to-video, multi-image video, and keyframe animation.
---

# VisionCraft

Generate images and videos via Agnes AI APIs. Calls PowerShell scripts in `scripts/`. API key is read from environment variable `AGNES_API_KEY`.

> **First time?** See [Prerequisites](#prerequisites). For prompt-writing tips and parameter details, see [`references/`](references/).

## Quick Reference

| Task | Command |
|------|---------|
| Text-to-Image | `scripts/gen_image.ps1 -Prompt "..."` |
| Image-to-Image | `scripts/gen_image.ps1 -Prompt "..." -ImageUrl "https://..."` |
| Text-to-Video | `scripts/gen_video.ps1 -Prompt "..."` |
| Image-to-Video | `scripts/gen_video.ps1 -Prompt "..." -Image "https://..."` |
| Multi-image Video | `scripts/gen_video.ps1 -Prompt "..." -Image "https://a.png","https://b.png"` |
| Keyframes Animation | `scripts/gen_video.ps1 -Prompt "..." -Image "https://a.png","https://b.png" -Mode keyframes` |

**Defaults:** Images `2048x2048`. Videos `1920x1080 @ 60fps, 241 frames` (~4s).

## Prerequisites

Set the API key once (persists across sessions):

```powershell
[System.Environment]::SetEnvironmentVariable("AGNES_API_KEY", "sk-your-key-here", "User")
```

Or for the current session only:

```powershell
$env:AGNES_API_KEY = "sk-your-key-here"
```

Verify with `echo $env:AGNES_API_KEY`.

## How to Use This Skill

### 1. Identify the request

| User says | Mode |
|-----------|------|
| "make/draw/generate a picture of..." | Text-to-Image |
| "edit/transform/restyle this image..." (URL provided) | Image-to-Image |
| "make a video / animate / generate a clip of..." | Text-to-Video |
| "animate this photo / make this image move" (1 image) | Image-to-Video |
| "blend these images into a video" (multiple images) | Multi-image Video |
| "smooth transition / morph from A to B" (2+ images) | Keyframes Animation |

### 2. Refine the prompt if needed

If the request is vague, briefly suggest a richer prompt before running. For prompt structure and best practices see [`references/prompt-guide.md`](references/prompt-guide.md).

### 3. Run the script

Pass aspect ratio with `-Ratio` and duration with `-Seconds` for the simplest control. See [`references/parameters.md`](references/parameters.md) for all parameters.

```powershell
# Examples:
scripts/gen_image.ps1 -Prompt "..." -Ratio 16:9
scripts/gen_video.ps1 -Prompt "..." -Ratio 9:16 -Seconds 8
```

### 4. Surface the result

The scripts print a `MEDIA:<url>` line on success. **Always echo the URL on its own line** — never bury it in a paragraph. If the platform supports inline media rendering, embed it; otherwise the URL alone is enough.

**Never download the result to local disk** unless the user explicitly asks.

## Output Format

Image:
```
✅ Image generated.

MEDIA:https://platform-outputs.agnes-ai.space/images/...
```

Video:
```
🎬 Video generated (4.0s, 1920x1080).

MEDIA:https://platform-outputs.agnes-ai.space/videos/...
```

## Errors & Troubleshooting

| Error | Fix |
|-------|-----|
| `AGNES_API_KEY not set` | Set it (see Prerequisites). Restart terminal if needed. |
| 401 Unauthorized | API key invalid or expired. |
| 400 Bad Request | Check prompt, size format, frame count rule (8n+1, ≤441). |
| 503 Service Unavailable | Service busy. Wait 30s, retry. |
| Video timeout (15 min) | Script prints the `video_id` — re-query later, the task is not abandoned. |

For full API behavior see [`references/api_docs.md`](references/api_docs.md).

## Reference Files

- [`references/api_docs.md`](references/api_docs.md) — full Agnes API specification
- [`references/prompt-guide.md`](references/prompt-guide.md) — prompt structure for both image and video
- [`references/parameters.md`](references/parameters.md) — every script parameter, with examples
