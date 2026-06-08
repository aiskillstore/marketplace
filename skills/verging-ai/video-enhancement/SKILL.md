---
name: video-enhancement
description: AI Video Enhancement - Upscale video resolution, denoise, sharpen. Supports local files and YouTube/Bilibili URLs. HD/4K upscaling with real-time progress.
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

# video-enhancement - AI Video Enhancement

Upscale and enhance video quality using AI via verging.ai.

## Command Format

```
/video-enhancement --video <video file or URL> [options]
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --video | -v | Video file path or URL (YouTube/Bilibili) | Required |
| --start | -s | Start time in seconds | 0 |
| --end | -e | End time in seconds | Video end (max 30s) |
| --hd | | HD upscaling (5 credits/sec) | false (3 credits/sec) |
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
# ⚠️ MUST use -F (multipart form-data)
curl -X POST https://verging.ai/api/v1/upload-video \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "video_file_name=video.mp4" \
  -F "job_type=video-enhance"
```
Response:
```json
{
  "code": 100000,
  "result": {
    "url": "https://...presigned-url...",
    "public_url": "https://img.panpan8.com/video-enhance/..."
  }
}
```

### 3. Upload Video to R2
```bash
curl -X PUT -T /tmp/verging-video-enhancement/trimmed.mp4 \
  -H "Content-Type: video/mp4" \
  "<presigned_url_from_step_2>"
```

### 4. Create Enhancement Job (Form Data)
```bash
# ⚠️ Uses -F (form-data), NOT JSON
curl -X POST https://verging.ai/api/v1/video_enhance/create-job \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "target_video_url=<public_url_from_step_2>" \
  -F "file_name=video.mp4" \
  -F "user_video_duration=30" \
  -F "job_type=video-enhance" \
  -F "is_hd=false"
```
Response: `{"code":10000,"result":{"job_id":"123"},"message":{"en":"Request Success","zh":"提交任务成功"}}`

### 5. Poll Job Status
```bash
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  "https://verging.ai/api/v1/jobs/list-jobs?job_ids=<job_id>"
```
Response: `[{"id":123,"job_type":"video-enhance","status":"COMPLETED","progress":100,"result_url":"https://...","created_at":"...","updated_at":"..."}]`

Status values: `PENDING` → `PROCESSING` → `COMPLETED` (or `FAILED`)

## Execution Flow (Follow Exactly)

1. **Parse args** → extract video path/URL, options
2. **Download remote video** (if URL): `yt-dlp "URL" -o /tmp/verging-video-enhancement/input.mp4`
3. **Get duration** → `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4`
4. **Trim if needed** (--start/--end or duration > 30s):
   ```bash
   ffmpeg -i input.mp4 -ss <start> -to <end> -c:v libx264 -c:a aac /tmp/verging-video-enhancement/trimmed.mp4
   ```
5. **Check credits** → GET /api/v1/auth/me (need duration × 3 normal or ×5 HD)
6. **Upload video** → POST /upload-video (Form Data) → PUT to presigned URL
7. **Create job** → POST /video_enhance/create-job (Form Data)
8. **Poll status** → GET /jobs/list-jobs?job_ids=X every 5 seconds until COMPLETED
9. **Return/download result** → show result_url, optionally curl download

## Critical Notes

- **Use `Authorization: ApiKey <key>` (recommended)** — `Bearer <key>` also works
- **`/upload-video` uses Form Data (`-F`)** — NOT JSON
- **`/video_enhance/create-job` uses Form Data (`-F`)** — NOT JSON, no file upload needed
- **Max video duration: 30 seconds** — trim longer videos first
- **Temp directory:** `/tmp/verging-video-enhancement/`
- If yt-dlp unavailable, ask user to download video manually

## Credit Consumption

| Mode | Cost |
|------|------|
| Normal | 3 credits/second |
| HD | 5 credits/second |

## Privacy & Security

- Set key via env: `export VERGING_API_KEY="your_key"`
- Never expose API key in public repos
- Only process media you have rights to
- Temp files cleaned up after use
