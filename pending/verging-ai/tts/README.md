# tts - AI Text-to-Speech Generation

Convert text to natural-sounding speech audio using OpenAI TTS-1-HD via the verging.ai API. Six voices, adjustable speed.

## Install

```bash
npx skills add verging-ai/agent-skills --skill tts
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
# Generate speech from text
curl -X POST https://verging.ai/api/v1/ai/tts \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello! Welcome to verging.ai.",
    "voice": "nova",
    "speed": 1.0
  }'
```

## Available Voices

| Voice | Style |
|-------|-------|
| alloy | Neutral, balanced |
| echo | Warm, rounded |
| fable | Expressive, British |
| onyx | Deep, authoritative |
| nova | Friendly, upbeat |
| shimmer | Soft, gentle |

## Features

- Powered by OpenAI TTS-1-HD model
- 6 distinct voice options
- Adjustable playback speed (0.25x–4.0x)
- MP3 output with CDN delivery
- Max input: 4096 characters

## Credits

| Rate | Minimum |
|------|---------|
| 1 credit / 1K characters | 1 credit |

## Links

- Website: https://verging.ai
- API Docs: https://verging.ai/docs/api
