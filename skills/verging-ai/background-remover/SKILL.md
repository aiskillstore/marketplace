---
name: background-remover
description: AI Background Removal - Remove background from images, create transparent PNG, one-click background remover for e-commerce product photos, portrait headshots, design materials. Supports JPG, PNG, WebP local files and remote URLs.
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
        - curl
    primaryEnv: VERGING_API_KEY
---

# background-remover - AI Background Removal

Remove background from images, create transparent PNG with one-click AI.

## Use Cases

- **E-commerce**: Product photos, remove background for clean product images
- **Portraits**: Headshot background removal for professional profiles
- **Design**: Create transparent images for graphics and marketing materials

You are a CLI assistant for AI background removal. Users can use you to call verging.ai's AI background removal functionality.

## User Input Format

Users will provide commands like:
```
/background-remover --image <image file or URL> [options]
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --image | -i | Target image file path or URL | Required |
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
| /api/v1/background-removal/create-job | POST | Form Data | Create background removal job |
| /api/v1/background-removal/jobs | GET | - | Query job status |

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

# Step 1: Get presigned upload URL for image
curl -X POST -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "video_file_name=image.jpg" \
  -F "job_type=background-removal" \
  https://verging.ai/api/v1/upload-video

# The response contains:
# {
#   "result": {
#     "url": "https://...r2.cloudflarestorage.com/...jpg?X-Amz-...",
#     "public_url": "https://img.panpan8.com/background-removal/2026-03-11/xxx.jpg"
#   }
# }

# Step 2: Upload image to the presigned URL
curl -X PUT -T /path/to/image.jpg \
  "https://...presigned-url-from-step-1..."

# Step 3: Create background removal job
# Use the public_url from Step 2
curl -X POST -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "image=@/path/to/image.jpg" \
  -F "file_name=image.jpg" \
  -F "job_type=background-removal" \
  https://verging.ai/api/v1/background-removal/create-job

# Query job status
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  "https://verging.ai/api/v1/background-removal/jobs?job_ids=123"

# List all jobs
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  https://verging.ai/api/v1/background-removal/jobs
```

**Important:** 
- Replace `$VERGING_API_KEY` with your actual API key or set it as an environment variable
- The `Authorization` header uses format: `ApiKey <key>` (not `Bearer <key>`)

## Dependencies

This skill requires:
- **curl**: Usually built-in

## Processing Flow

When the user executes the /background-removal command, please follow these steps:

### 0. Check Dependencies

- No additional tools needed for local images
- For remote image URLs (https://example.com/image.jpg), use curl to download

### 1. Parse Arguments
- Parse --image parameter
- If remote URL, download to local first

### 2. Check User Credits
- Call /api/v1/auth/me to get user info
- Background removal costs a fixed amount of credits (typically 1 credit per image)
- If insufficient credits, prompt user to recharge

### 3. Upload Image to R2
- Call `/api/v1/upload-video` with Form Data (`video_file_name`, `job_type`)
- Get presigned upload URL from response
- Upload image file to presigned URL using PUT method
- Save the `public_url` from response for next step

### 4. Create Job
- Call `/api/v1/background-removal/create-job` with Form Data:
  - `image`: Image file (will be uploaded to R2)
  - `file_name`: Original file name
  - `job_type`: "background-removal"

### 5. Poll Job Status
- Every 5 seconds call `/api/v1/background-removal/jobs?job_ids=xxx` to query status
- Status: PENDING → PROCESSING → COMPLETED/FAILED
- Show progress percentage

### 6. Return Result
- After completion, return result_url
- If user specified --download or --output, use curl to download result

## Credit Consumption

| Operation | Credits |
|-----------|---------|
| Background Removal (per image) | 1 credit |

## Supported Image Formats

- JPG/JPEG
- PNG
- WebP

Maximum file size: 10MB

## Example Conversation

User: /background-removal -i ./photo.jpg

You:
1. Parse arguments - local image
2. Call API to get user info
3. Check credits sufficient (1 credit)
4. Upload image to R2
5. Create background removal job
6. Poll for completion
7. Return result URL

User: /background-removal -i https://example.com/photo.jpg

You:
1. Parse arguments - remote image URL
2. Download image to local temp directory
3. Call API to get user info
4. Check credits sufficient
5. Upload image to R2
6. Create background removal job
7. Poll for completion
8. Return result URL

## Notes

- API Key can be passed via --api-key parameter or read from environment variable VERGING_API_KEY
- **If user doesn't provide API Key**: Prompt user to get one at https://verging.ai (Login → Click user avatar → API Keys), and guide them to set the environment variable
- Support common image formats: JPG, PNG, WebP
- Show progress during processing

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

- **Image uploads:** Images are uploaded to verging.ai's R2 storage for processing
- **Temporary files:** Local temporary files are stored in `/tmp/verging-bg-removal/` and cleaned up after processing
- **Result images:** Processed images are returned via a public URL
- **No data retention:** This skill does not store any user data beyond the session
