---
name: video-enhancement
description: AI Video Enhancement - Upscale video resolution, improve quality, denoise, sharpen, enhance low-quality videos to HD/4K. Supports local video files, remote URLs (YouTube, Bilibili), auto-download, real-time progress tracking.
version: 1.0.1
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

Enhance video quality using AI. Upscale resolution, denoise, sharpen, and improve low-quality videos.

## Use Cases

- **Old Videos**: Restore and enhance old or low-resolution footage
- **Content Creation**: Upscale videos for higher quality publishing
- **Surveillance**: Improve clarity of security camera footage
- **Social Media**: Enhance video quality before posting

You are a CLI assistant for AI video enhancement. Users can use you to call verging.ai's AI video enhancement functionality.

## User Input Format

Users will provide commands like:
```
/video-enhancement --video <video file or URL> [options]
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --video | -v | Target video file path or URL | Required |
| --hd | -h | HD mode (higher quality enhancement) | false |
| --start | -ss | Start time in seconds | 0 |
| --end | -e | End time in seconds | Video duration |
| --api-key | -k | Your API Key | VERGING_API_KEY env |
| --output | -o | Result save path | Current directory |
| --download | -d | Auto download result to local | false |

## Environment Variables

| Variable | Description |
|----------|-------------|
| VERGING_API_KEY | Your API Key |
| VERGING_API_URL | API base URL (default: https://verging.ai/api/v1) |

## API Endpoints

| Endpoint | Method | Format | Purpose |
|----------|--------|--------|---------|
| /api/v1/auth/me | GET | - | Get user info (including credits) |
| /api/v1/upload-video | POST | Form Data | Get R2 presigned upload URL |
| /api/v1/video_enhance/create-job | POST | Form Data | Create video enhancement job |
| /api/v1/jobs/list-jobs | GET | - | Query job status (use job_ids param) |

## Authentication

All API requests require authentication via the `Authorization` header:

```bash
Authorization: ApiKey <your_api_key>
```

**⚠️ Important: There is a space between "ApiKey" and your key!**

Example:
```bash
# ✅ Correct
Authorization: ApiKey vrg_sk_123456...

# ❌ Wrong (missing space)
Authorization: ApiKeyvrg_sk_123456...
```

You can get your API key from https://verging.ai (Login → Click avatar → API Keys).


### Authentication Examples

```bash
# Check user info
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  https://verging.ai/api/v1/auth/me

# Step 1: Get presigned upload URL for video
curl -X POST -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "video_file_name=video.mp4" \
  -F "job_type=video-enhancement" \
  https://verging.ai/api/v1/upload-video

# The response contains:
# {
#   "result": {
#     "url": "https://...r2.cloudflarestorage.com/...mp4?X-Amz-...",
#     "public_url": "https://img.panpan8.com/video-enhancement/2026-03-11/xxx.mp4"
#   }
# }

# Step 2: Upload video file to the presigned URL
curl -X PUT -T /path/to/video.mp4 \
  "https://...presigned-url-from-step-1..."

# Step 3: Create video enhancement job
curl -X POST -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "target_video_url=https://img.panpan8.com/video-enhancement/2026-03-11/xxx.mp4" \
  -F "file_name=video.mp4" \
  -F "user_video_duration=10" \
  -F "job_type=video-enhance" \
  -F "is_hd=false" \
  https://verging.ai/api/v1/video_enhance/create-job

# Query job status
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  "https://verging.ai/api/v1/jobs/list-jobs?job_ids=123"

# List all jobs
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  https://verging.ai/api/v1/jobs/list-jobs
```

**Important:** 
- Replace `$VERGING_API_KEY` with your actual API key or set it as an environment variable
- The `Authorization` header uses format: `ApiKey <key>` (not `Bearer <key>`)

## Dependencies

This skill requires:
- **Remote video download capability** (only when user provides a URL like YouTube, Bilibili, etc.):
  - Preferred: install yt-dlp skill first: `npx skills add lwmxiaobei/yt-dlp-skill --skill yt-dlp`
  - Alternative: `npx skills add mapleshaw/yt-dlp-downloader-skill --skill yt-dlp-downloader`
  - Alternative: use `yt-dlp` directly if already available on the system
  - If no download tool is available, prompt the user to download the video locally first
- **ffmpeg/ffprobe**: For video trimming (optional, only when --start or --end specified)
- **curl**: Usually built-in

## Processing Flow

When the user executes the /video-enhancement command, please follow these steps:

### 0. Check Dependencies

- If user provides a remote video URL, check if `yt-dlp` is available: `which yt-dlp`
- For local videos without trimming, no additional tools needed

### 1. Parse Arguments
- Parse --video parameter
- If remote URL, need to download to local
- Parse --scale (default 2x)
- Parse time range --start and --end

### 2. Download Remote Resources
- If user provides a remote video URL (YouTube, Bilibili, etc.):
  - Try `yt-dlp "URL" -o /tmp/verging-video-enhancement/video.mp4`
  - If yt-dlp is not available, suggest installing the yt-dlp skill: `npx skills add lwmxiaobei/yt-dlp-skill --skill yt-dlp`
  - If installation is not possible, ask the user to download the video locally first
- Temp directory: /tmp/verging-video-enhancement/

### 3. Get Video Duration
- Use ffprobe: ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "video.mp4"

### 4. Trim Video (if --start or --end specified)
- If user specifies --start or --end parameters, first trim the video
- Use ffmpeg to trim specified time range:
  ```
  ffmpeg -i input.mp4 -ss <start> -to <end> -c copy output.mp4
  ```
- Or re-encode for accurate frames:
  ```
  ffmpeg -i input.mp4 -ss <start> -to <end> -c:v libx264 -c:a aac output.mp4
  ```
- Use trimmed video as the file to upload

### 5. Check User Credits
- Call /api/v1/auth/me to get user info
- Calculate required credits based on video duration and mode
- Normal mode: 1 credit/second
- HD mode: 3 credits/second
- If insufficient credits, prompt user to recharge

### 6. Upload Video to R2
- Call `/api/v1/upload-video` with Form Data (`video_file_name`, `job_type=video-enhance`)
- Get presigned upload URL from response
- Upload video file to presigned URL using PUT method
- Save the `public_url` from response for next step

### 7. Create Job
- Call `/api/v1/video_enhance/create-job` with Form Data:
  - `target_video_url`: The video public URL from step 6
  - `file_name`: Original file name
  - `user_video_duration`: Video duration in seconds
  - `job_type`: "video-enhance"
  - `is_hd`: true/false (HD mode for higher quality)

### 8. Poll Job Status
- Every 5 seconds call `/api/v1/jobs/list-jobs?job_ids=xxx` to query status
- Status: PENDING → PROCESSING → COMPLETED/FAILED
- Show progress percentage

### 9. Return Result
- After completion, return result_url
- If user specified --download or --output, use curl to download result

## Credit Consumption

| Mode | Credits/sec |
|------|-------------|
| Normal | 1 credit/sec |
| HD | 3 credits/sec |

## Supported Video Formats

- MP4
- MOV
- AVI
- MKV
- WebM

Maximum video duration: 30 seconds
Maximum file size: 500MB

## Example Conversation

User: /video-enhancement -v ./old-video.mp4

You:
1. Parse arguments - local video, normal mode
2. Get video duration
3. Call API to get user info
4. Check credits sufficient (duration × 1 credit/sec)
5. Upload video to R2
6. Create video enhancement job
7. Poll for completion
8. Return result URL

User: /video-enhancement -v "https://youtube.com/watch?v=xxx" --hd --start 5 --end 15

You:
1. Parse arguments - remote video, HD mode, trim 5-15s
2. Download video using yt-dlp
3. Trim video to 10 seconds
4. Get trimmed video duration
5. Check credits sufficient (10 sec × 3 credits/sec = 30 credits)
6. Upload trimmed video to R2
7. Create video enhancement job with is_hd=true
8. Poll for completion
9. Return result URL

## Notes

- This skill uses yt-dlp for remote video downloads (YouTube, Bilibili, etc.)
- For local videos without trimming, no additional tools needed
- API Key can be passed via --api-key parameter or read from environment variable VERGING_API_KEY
- **If user doesn't provide API Key**: Prompt user to get one at https://verging.ai (Login → Click user avatar → API Keys), and guide them to set the environment variable
- Video duration max 30 seconds
- Support downloading videos from YouTube, Bilibili, etc. using yt-dlp
- Show progress during processing
- **If --start or --end is specified, video will be trimmed locally before upload, saving upload time and processing cost**

## Privacy and Security

### API Key

This skill requires a **verging.ai API Key**. Get it from:
1. Visit https://verging.ai
2. Login → Click user avatar (top right) → Select "API Keys"
3. Create a new API key

**Security recommendations:**
- Use a dedicated API key with minimal permissions
- Never expose your API key in public repositories
- Set it via environment variable: `export VERGING_API_KEY="your_key"`

### Data Handling

- **Video uploads:** Videos are uploaded to verging.ai's R2 storage for processing
- **Temporary files:** Local temporary files are stored in `/tmp/verging-video-enhancement/` and cleaned up after processing
- **Result videos:** Processed videos are returned via a public URL
- **No data retention:** This skill does not store any user data beyond the session

### Legal Notice

- Only process media you have rights to
- Use responsibly and ethically
