# imagegen - AI Image Generation

Generate images from text prompts using DALL-E 3 / GPT-Image-1 via the verging.ai API. Standard and HD quality.

## Install

```bash
npx skills add verging-ai/agent-skills --skill imagegen
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
# Generate an image
curl -X POST https://verging.ai/api/v1/ai/imagegen \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic cityscape at sunset, digital art",
    "quality": "hd",
    "n": 1
  }'
```

## Features

- Powered by DALL-E 3 / GPT-Image-1
- Standard and HD quality modes
- Generate 1–4 images per request
- 1024x1024 default resolution
- CDN-delivered output URLs

## Credits

| Quality | Cost per Image |
|---------|---------------|
| Standard | 2 credits |
| HD | 3 credits |

Multiple images (`n > 1`) multiply the cost accordingly.

## Links

- Website: https://verging.ai
- API Docs: https://verging.ai/docs/api
