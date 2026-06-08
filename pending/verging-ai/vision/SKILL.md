# AI Vision Analysis — verging.ai

Analyze images using GPT-4o Vision through the verging.ai proxy API. Supports both image URL and file upload.

## Authentication

All requests require an API key in the `Authorization` header:

```
Authorization: ApiKey vrg_sk_xxx
```

Replace `vrg_sk_xxx` with your verging.ai API key. You can generate one at https://verging.ai under your account settings.

## Endpoints

### Option A — Image URL (JSON)

```
POST https://verging.ai/api/v1/ai/vision
Content-Type: application/json
```

### Option B — File Upload (multipart)

```
POST https://verging.ai/api/v1/ai/vision/upload
Content-Type: multipart/form-data
```

## Parameters

### JSON (URL mode)

| Parameter  | Type   | Required | Default | Description                              |
|------------|--------|----------|---------|------------------------------------------|
| prompt     | string | Yes      | —       | Analysis instruction / question          |
| image_url  | string | Yes      | —       | URL of the image to analyze              |
| model      | string | No       | gpt-4o  | Vision model                             |
| max_tokens | int    | No       | 1024    | Maximum tokens in the response           |

### Multipart (file upload mode)

| Parameter  | Type   | Required | Default | Description                              |
|------------|--------|----------|---------|------------------------------------------|
| prompt     | string | Yes      | —       | Analysis instruction / question          |
| file       | file   | Yes      | —       | Image file to analyze                    |
| model      | string | No       | gpt-4o  | Vision model                             |
| max_tokens | int    | No       | 1024    | Maximum tokens in the response           |

Requires a minimum balance of **5 credits** before calling (post-deduct billing).

## Examples

### Image URL

```bash
curl -X POST https://verging.ai/api/v1/ai/vision \
  -H "Authorization: ApiKey vrg_sk_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Describe what you see in this image in detail.",
    "image_url": "https://example.com/photo.jpg",
    "max_tokens": 512
  }'
```

### File Upload

```bash
curl -X POST https://verging.ai/api/v1/ai/vision/upload \
  -H "Authorization: ApiKey vrg_sk_xxx" \
  -F "prompt=What objects are in this image?" \
  -F "file=@photo.jpg"
```

## Response

```json
{
  "content": "The image shows a modern office space with several desks...",
  "usage": {
    "prompt_tokens": 1100,
    "completion_tokens": 95,
    "total_tokens": 1195
  },
  "credits_consumed": 2
}
```

- `content` — The analysis result text.
- `usage` — Token usage breakdown.
- `credits_consumed` — Credits deducted for this request.

## Credits

| Component  | Rate                    |
|------------|-------------------------|
| Base fee   | 2 credits               |
| Input tokens  | 1 credit / 10K tokens |
| Output tokens | 3 credits / 10K tokens |

Minimum charge: **2 credits** per request.

## Error Codes

| HTTP Status | Error Code | Description                                      |
|-------------|------------|--------------------------------------------------|
| 402         | 40001      | Insufficient credits (minimum 5 required)        |
| 429         | —          | Rate limit exceeded (check `X-RateLimit-Reset`)  |
| 502         | —          | Upstream provider error                          |
| 503         | —          | Service unavailable or upstream timeout          |

Error response format:

```json
{
  "error_code": 40001,
  "message": "Insufficient credits. Required: 5, available: 2",
  "upstream_error": null
}
```
