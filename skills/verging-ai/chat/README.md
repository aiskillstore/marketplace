# chat - AI Chat & Text Generation

Generate AI chat completions using GPT-4o via the verging.ai API. Supports streaming (SSE) and non-streaming responses.

## Install

```bash
npx skills add verging-ai/agent-skills --skill chat
```

## Setup

1. Visit [verging.ai](https://verging.ai)
2. Login → Click avatar (top right) → API Keys
3. Create a key, then set it:

```bash
export VERGING_API_KEY="vrg_sk_your_key_here"
```

## Usage

```bash
# Non-streaming chat completion
curl -X POST https://verging.ai/api/v1/ai/chat \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain quantum computing briefly."}
    ]
  }'

# Streaming (SSE)
curl -N -X POST https://verging.ai/api/v1/ai/chat \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Write a haiku."}],
    "stream": true
  }'
```

## Features

- Powered by GPT-4o
- Streaming (Server-Sent Events) and non-streaming modes
- System/user/assistant message roles
- Configurable temperature and max_tokens
- Token usage reporting per request

## Credits

| Token Type | Rate |
|------------|------|
| Input | 1 credit / 10K tokens |
| Output | 3 credits / 10K tokens |

Minimum charge: 1 credit per request. Requires 5 credits minimum balance.

## Links

- Website: https://verging.ai
- API Docs: https://verging.ai/docs/api
