# AI Image Generation — verging.ai

Generate AI images using DALL-E 3 / gpt-image-1 through the verging.ai proxy API.

## Authentication

All requests require an API key in the `Authorization` header:

```
Authorization: ApiKey vrg_sk_xxx
```

Replace `vrg_sk_xxx` with your verging.ai API key. You can generate one at https://verging.ai under your account settings.

## Endpoint

```
POST https://verging.ai/api/v1/ai/imagegen
Content-Type: application/json
```

## Parameters

| Parameter | Type   | Required | Default      | Description                                      |
|-----------|--------|----------|--------------|--------------------------------------------------|
| prompt    | string | Yes      | —            | Text description of the image to generate        |
| model     | string | No       | gpt-image-1  | Model to use for generation                      |
| size      | string | No       | 1024x1024    | Image dimensions                                 |
| quality   | string | No       | standard     | Image quality (`standard` or `hd`)               |
| n         | int    | No       | 1            | Number of images to generate (1–4)               |

## Example

```bash
curl -X POST https://verging.ai/api/v1/ai/imagegen \
  -H "Authorization: ApiKey vrg_sk_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic cityscape at sunset, digital art style",
    "quality": "hd",
    "n": 2
  }'
```

## Response

```json
{
  "images": [
    "https://cdn.verging.ai/proxy/imagegen/abc123.png",
    "https://cdn.verging.ai/proxy/imagegen/def456.png"
  ],
  "credits_consumed": 6
}
```

- `images` — Array of CDN URLs for the generated images.
- `credits_consumed` — Total credits deducted for this request.

## Credits

| Quality  | Cost per Image |
|----------|---------------|
| standard | 2 credits     |
| hd       | 3 credits     |

When generating multiple images (`n > 1`), the cost is multiplied accordingly.

## Error Codes

| HTTP Status | Error Code | Description                                      |
|-------------|------------|--------------------------------------------------|
| 400         | —          | Content policy violation or invalid parameters   |
| 402         | 40001      | Insufficient credits                             |
| 429         | —          | Rate limit exceeded (check `X-RateLimit-Reset`)  |
| 502         | —          | Upstream provider error                          |
| 503         | —          | Service unavailable or upstream timeout          |

Error response format:

```json
{
  "error_code": 40001,
  "message": "Insufficient credits. Required: 4, available: 1",
  "upstream_error": null
}
```
