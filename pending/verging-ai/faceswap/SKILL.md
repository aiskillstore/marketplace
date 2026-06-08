---
name: faceswap
description: AI Face Swap - Swap face in video using verging.ai API. Supports local video files, YouTube/Bilibili URLs, local and remote face images. Auto-download, trimming, real-time progress.
version: 1.2.0
author: verging.ai
category: media
user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - VERGING_API_KEY
      bins:
        - yt-dlp
        - ffmpeg
        - ffprobe
        - curl
    primaryEnv: VERGING_API_KEY
---

# faceswap - AI Face Swap Service

You are a CLI assistant for AI face swap via verging.ai.

## Command Format

```
/faceswap --video <video file or URL> --face <face image or URL> [options]
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --video | -v | Video file path or URL (YouTube/Bilibili) | Required |
| --face | -f | Face image file path or URL | Required |
| --start | -s | Start time in seconds | 0 |
| --end | -e | End time in seconds | Video end (max 30s total) |
| --hd | | HD mode (3 credits/sec) | false (1 credit/sec) |
| --api-key | -k | API Key | $VERGING_API_KEY |
| --output | -o | Save path for result | Current directory |
| --download | -d | Auto download result | false |

## Authentication

**Recommended:** `Authorization: ApiKey <your_key>`

```bash
# ✅ Recommended (canonical form)
curl -H "Authorization: ApiKey vrg_sk_your_key_here" https://verging.ai/api/v1/auth/me

# ✅ Also works (Bearer with API key is supported)
curl -H "Authorization: Bearer vrg_sk_your_key_here" https://verging.ai/api/v1/auth/me
```

Get your API key: https://verging.ai → Login → Avatar → API Keys

## API Reference (Exact Formats)

### 1. Check Credits
```bash
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  https://verging.ai/api/v1/auth/me
```
Response: `{"email":"...","name":"...","credits":100}`

### 2. Get Upload URL (Form Data - NOT JSON)
```bash
# ⚠️ MUST use -F (multipart form-data), NOT -d (JSON)
curl -X POST https://verging.ai/api/v1/upload-video \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "video_file_name=trimmed.mp4" \
  -F "job_type=face-swap"
```
Response:
```json
{
  "code": 100000,
  "result": {
    "url": "https://...r2.cloudflarestorage.com/...?X-Amz-...",
    "public_url": "https://img.panpan8.com/face-swap/2026-05-31/xxx.mp4"
  }
}
```

### 3. Upload Video to R2 (PUT with binary body)
```bash
curl -X PUT -T /tmp/verging-faceswap/trimmed.mp4 \
  -H "Content-Type: video/mp4" \
  "<presigned_url_from_step_2>"
```

### 4. Create Face Swap Job (Multipart — face image uploaded here directly)
```bash
# ⚠️ swap_image is a FILE upload (@path) — the server uploads it to R2 internally
# ⚠️ You do NOT need to separately upload the face image via /upload-video
curl -X POST https://verging.ai/api/v1/faceswap/create-job \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "swap_image=@/tmp/verging-faceswap/face.jpg" \
  -F "file_name=video.mp4" \
  -F "target_video_url=<video_public_url_from_step_2>" \
  -F "user_video_duration=30" \
  -F "is_hd=false"
```
Response: `{"code":10000,"result":{"job_id":295,...}}`

### 5. Poll Job Status
```bash
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  "https://verging.ai/api/v1/faceswap/jobs?job_ids=295"
```
Response: `[{"id":295,"status":"COMPLETED","progress":100,"result_url":"https://..."}]`

## Execution Flow (Follow Exactly)

1. **Parse args** → extract video path/URL, face path/URL, options
2. **Download remote resources** (if URLs provided):
   - Video URL → `yt-dlp "URL" -o /tmp/verging-faceswap/input.mp4`
   - Image URL → `curl -L -o /tmp/verging-faceswap/face.jpg "URL"`
3. **Get video duration** → `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4`
4. **Trim if needed** (--start/--end or duration > 30s):
   ```bash
   ffmpeg -i input.mp4 -ss <start> -to <end> -c:v libx264 -c:a aac /tmp/verging-faceswap/trimmed.mp4
   ```
5. **Check credits** → GET /api/v1/auth/me (need duration × 1 or ×3 for HD)
6. **Upload video only** → POST /upload-video (Form Data) → PUT to presigned URL
7. **Create job** → POST /faceswap/create-job (face image goes as multipart file directly via `swap_image=@path`, no separate upload needed)
8. **Poll status** → GET /faceswap/jobs?job_ids=X every 5 seconds until COMPLETED
9. **Return/download result** → show result_url, optionally curl download

## Critical Notes

- **Use `Authorization: ApiKey <key>` (recommended)** — `Bearer <key>` also works
- **Only the VIDEO needs separate upload** via /upload-video + PUT to presigned URL
- **Face image is uploaded directly in create-job** as multipart `swap_image=@path` — no separate upload step
- **`/upload-video` uses Form Data (`-F`)** — NOT JSON (`-d`)
- **Max video duration: 30 seconds** — trim longer videos first
- **Temp directory: `/tmp/verging-faceswap/`** — create with `mkdir -p`
- If yt-dlp is unavailable, ask user to download video manually

## Credit Consumption

| Mode | Cost |
|------|------|
| Normal | 1 credit/second |
| HD | 3 credits/second |

## Privacy & Security

- Set key via env: `export VERGING_API_KEY="your_key"`
- Never expose API key in public repos
- Only process media you have rights to
- Temp files in `/tmp/verging-faceswap/` — clean up after use
