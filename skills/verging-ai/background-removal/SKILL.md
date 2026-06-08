---
name: background-removal
description: AI Background Removal - Remove background from images, create transparent PNG. Supports JPG, PNG, WebP local files and remote URLs. One credit per image.
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
        - curl
    primaryEnv: VERGING_API_KEY
---

# background-removal - AI Background Removal

Remove image backgrounds with AI via verging.ai. Returns transparent PNG.

## Command Format

```
/background-removal --image <image file or URL> [options]
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --image | -i | Image file path or URL | Required |
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

### 2. Create Background Removal Job (Multipart with file — direct upload)
```bash
# ⚠️ image is a FILE upload (@path) — server handles R2 upload internally
# ⚠️ You do NOT need to use /upload-video separately for background removal
curl -X POST https://verging.ai/api/v1/background-removal/create-job \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "image=@/tmp/verging-bg-removal/photo.jpg" \
  -F "file_name=photo.jpg" \
  -F "job_type=background-removal"
```
Response: `{"code":10000,"result":{"job_id":"456"},"message":{"en":"Request Success","zh":"提交任务成功"}}`

### 3. Poll Job Status
```bash
curl -H "Authorization: ApiKey $VERGING_API_KEY" \
  "https://verging.ai/api/v1/background-removal/jobs?job_ids=456"
```
Response: `[{"id":456,"status":"COMPLETED","progress":100,"result_url":"https://...","image_url":"https://...","created_at":"...","updated_at":"..."}]`

Status values: `PENDING` → `PROCESSING` → `COMPLETED` (or `FAILED`)

## Execution Flow (Follow Exactly)

1. **Parse args** → extract image path/URL
2. **Download remote image** (if URL): `curl -L -o /tmp/verging-bg-removal/photo.jpg "URL"`
3. **Validate** → check file exists, format is JPG/PNG/WebP, size < 10MB
4. **Check credits** → GET /api/v1/auth/me (needs 1 credit)
5. **Create job** → POST /background-removal/create-job (Multipart with `image=@path` — server uploads to R2 internally, no separate upload step needed)
6. **Poll status** → GET /background-removal/jobs?job_ids=X every 5 seconds until COMPLETED
7. **Return/download result** → show result_url, optionally curl download

## Critical Notes

- **Use `Authorization: ApiKey <key>` (recommended)** — `Bearer <key>` also works
- **No separate upload step needed** — create-job handles R2 upload internally when you provide `image=@path`
- **`image` must be a file upload (`@path`)** — NOT a URL string
- **Cost: 1 credit per image (fixed)**
- **Supported formats:** JPG, PNG, WebP (max 10MB)
- **Temp directory:** `/tmp/verging-bg-removal/`

## Privacy & Security

- Set key via env: `export VERGING_API_KEY="your_key"`
- Never expose API key in public repos
- Temp files cleaned up after use
