# Speech-to-Text — verging.ai

Transcribe audio to text using OpenAI Whisper through the verging.ai proxy API.

## Authentication

All requests require an API key in the `Authorization` header:

```
Authorization: ApiKey vrg_sk_xxx
```

Replace `vrg_sk_xxx` with your verging.ai API key. You can generate one at https://verging.ai under your account settings.

## Endpoint

```
POST https://verging.ai/api/v1/ai/stt
Content-Type: multipart/form-data
```

## Parameters

| Parameter       | Type   | Required | Default   | Description                                    |
|-----------------|--------|----------|-----------|------------------------------------------------|
| file            | file   | Yes      | —         | Audio file to transcribe                       |
| model           | string | No       | whisper-1 | STT model                                      |
| language        | string | No       | —         | Language code (e.g. `en`, `zh`, `ja`)          |
| response_format | string | No       | json      | Output format                                  |
| temperature     | float  | No       | —         | Sampling temperature (0–1)                     |

### Supported Audio Formats

`mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm`

### File Size Limit

Maximum file size: **25 MB**

## Example

```bash
curl -X POST https://verging.ai/api/v1/ai/stt \
  -H "Authorization: ApiKey vrg_sk_xxx" \
  -F "file=@recording.mp3" \
  -F "language=en"
```

## Response

```json
{
  "text": "Hello, this is a sample transcription of the audio file.",
  "language": "en",
  "duration": 12.5,
  "credits_consumed": 1
}
```

- `text` — Transcribed text content.
- `language` — Detected or specified language.
- `duration` — Audio duration in seconds.
- `credits_consumed` — Credits deducted for this request.

## Credits

| Rate             | Minimum |
|------------------|---------|
| 1 credit / minute | 1 credit |

## Error Codes

| HTTP Status | Error Code | Description                                      |
|-------------|------------|--------------------------------------------------|
| 400         | —          | File exceeds 25 MB or unsupported audio format   |
| 402         | 40001      | Insufficient credits                             |
| 429         | —          | Rate limit exceeded (check `X-RateLimit-Reset`)  |
| 502         | —          | Upstream provider error                          |
| 503         | —          | Service unavailable or upstream timeout          |

Error response format:

```json
{
  "error_code": 40001,
  "message": "Insufficient credits. Required: 1, available: 0",
  "upstream_error": null
}
```
