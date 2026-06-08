# vision - AI Image Analysis

Analyze images using GPT-4o Vision via the verging.ai API. Supports both image URL and file upload modes.

## Install

```bash
npx skills add verging-ai/agent-skills --skill vision
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
# Analyze an image by URL
curl -X POST https://verging.ai/api/v1/ai/vision \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Describe what you see in this image.",
    "image_url": "https://example.com/photo.jpg"
  }'

# Analyze a local image file
curl -X POST https://verging.ai/api/v1/ai/vision/upload \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "prompt=What objects are in this image?" \
  -F "file=@photo.jpg"
```

## Features

- Powered by GPT-4o Vision
- Two modes: image URL (JSON) or file upload (multipart)
- Detailed scene description, object detection, text extraction
- Configurable max_tokens for response length

## Credits

| Component | Rate |
|-----------|------|
| Base fee | 2 credits |
| Input tokens | 1 credit / 10K tokens |
| Output tokens | 3 credits / 10K tokens |

Minimum charge: 2 credits per request. Requires 5 credits minimum balance.

## Links

- Website: https://verging.ai
- API Docs: https://verging.ai/docs/api
