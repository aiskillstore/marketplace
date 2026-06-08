---
name: verging-ai-tts
description: Convert text to speech audio using OpenAI TTS-1-HD through the verging.ai proxy API. Supports multiple voices, playback speed control, and various audio output formats.
---

# Text-to-Speech — verging.ai

Convert text to speech audio using OpenAI TTS-1-HD through the verging.ai proxy API.

## Authentication

All requests require an API key in the `Authorization` header:

```
Authorization: ApiKey vrg_sk_xxx
```

Replace `vrg_sk_xxx` with your verging.ai API key. You can generate one at https://verging.ai under your account settings.

## Endpoint

```
POST https://verging.ai/api/v1/ai/tts
Content-Type: application/json
```

## Parameters

| Parameter       | Type   | Required | Default  | Description                                          |
|-----------------|--------|----------|----------|------------------------------------------------------|
| input           | string | Yes      | —        | Text to convert to speech (max 4096 characters)      |
| voice           | string | No       | alloy    | Voice to use (see options below)                     |
| model           | string | No       | tts-1-hd | TTS model                                           |
| response_format | string | No       | mp3      | Audio output format                                  |
| speed           | float  | No       | 1.0      | Playback speed (0.25–4.0)                            |

### Available Voices

| Voice   | Description       |
|---------|-------------------|
| alloy   | Neutral, balanced |
| echo    | Warm, rounded     |
| fable   | Expressive, British |
| onyx    | Deep, authoritative |
| nova    | Friendly, upbeat  |
| shimmer | Soft, gentle      |

## Example

```bash
curl -X POST https://verging.ai/api/v1/ai/tts \
  -H "Authorization: ApiKey vrg_sk_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello! Welcome to verging.ai, your AI services platform.",
    "voice": "nova",
    "speed": 1.1
  }'
```

## Response

```json
{
  "audio_url": "https://cdn.verging.ai/proxy/tts/abc123.mp3",
  "credits_consumed": 1
}
```

- `audio_url` — CDN URL of the generated audio file.
- `credits_consumed` — Credits deducted for this request.

## Credits

| Rate              | Minimum |
|-------------------|---------|
| 1 credit / 1K characters | 1 credit |

## Error Codes

| HTTP Status | Error Code | Description                                      |
|-------------|------------|--------------------------------------------------|
| 400         | —          | Input exceeds 4096 characters or invalid params  |
| 402         | 40001      | Insufficient credits                             |
| 429         | —          | Rate limit exceeded (check `X-RateLimit-Reset`)  |
| 502         | —          | Upstream provider error                          |
| 503         | —          | Service unavailable or upstream timeout          |

Error response format:

```json
{
  "error_code": 40001,
  "message": "Insufficient credits. Required: 2, available: 0",
  "upstream_error": null
}
```
