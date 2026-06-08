# AI Chat / Text Generation — verging.ai

Generate AI chat completions using GPT-4o through the verging.ai proxy API. Supports both streaming (SSE) and non-streaming responses.

## Authentication

All requests require an API key in the `Authorization` header:

```
Authorization: ApiKey vrg_sk_xxx
```

Replace `vrg_sk_xxx` with your verging.ai API key. You can generate one at https://verging.ai under your account settings.

## Endpoint

```
POST https://verging.ai/api/v1/ai/chat
Content-Type: application/json
```

## Parameters

| Parameter   | Type    | Required | Default | Description                                         |
|-------------|---------|----------|---------|-----------------------------------------------------|
| messages    | array   | Yes      | —       | Array of message objects `{role, content}`           |
| model       | string  | No       | gpt-4o  | Model to use                                        |
| temperature | float   | No       | —       | Sampling temperature (0–2)                          |
| max_tokens  | int     | No       | —       | Maximum tokens in the response                      |
| stream      | boolean | No       | false   | Enable Server-Sent Events streaming                 |

Each message object:

| Field   | Type   | Description                              |
|---------|--------|------------------------------------------|
| role    | string | `system`, `user`, or `assistant`         |
| content | string | The message content                      |

Requires a minimum balance of **5 credits** before calling (post-deduct billing).

## Examples

### Non-streaming

```bash
curl -X POST https://verging.ai/api/v1/ai/chat \
  -H "Authorization: ApiKey vrg_sk_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing in one paragraph."}
    ],
    "temperature": 0.7,
    "max_tokens": 256
  }'
```

### Streaming (SSE)

```bash
curl -N -X POST https://verging.ai/api/v1/ai/chat \
  -H "Authorization: ApiKey vrg_sk_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Write a haiku about coding."}
    ],
    "stream": true
  }'
```

## Response

### Non-streaming

```json
{
  "content": "Quantum computing leverages quantum mechanical phenomena...",
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 85,
    "total_tokens": 109
  },
  "credits_consumed": 1
}
```

### Streaming (SSE)

The response is a stream of Server-Sent Events. Each content chunk:

```
data: {"content": "Quantum "}

data: {"content": "computing "}
```

The final chunk includes usage and credits information:

```
data: {"usage": {"prompt_tokens": 24, "completion_tokens": 85, "total_tokens": 109}, "credits_consumed": 1}

data: [DONE]
```

## Credits

| Token Type | Rate                |
|------------|---------------------|
| Input      | 1 credit / 10K tokens |
| Output     | 3 credits / 10K tokens |

Minimum charge: **1 credit** per request.

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
