---
name: ai-avatar-video
description: "Create AI avatar and talking head videos via inference.sh CLI. Recommended: P-Video-Avatar (fastest, cheapest, built-in TTS). Also: OmniHuman, Fabric, PixVerse. Capabilities: audio-driven avatars, text-to-avatar, lipsync videos, talking head generation, virtual presenters. Use for: AI presenters, explainer videos, virtual influencers, dubbing, marketing videos. Triggers: ai avatar, talking head, lipsync, avatar video, virtual presenter, ai spokesperson, audio driven video, heygen alternative, synthesia alternative, talking avatar, lip sync, video avatar, ai presenter, digital human"
allowed-tools: Bash(belt *)
---

# AI Avatar & Talking Head Videos

Create AI avatars and talking head videos via [inference.sh](https://inference.sh) CLI.

![AI Avatar & Talking Head Videos](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg0tszs96s0n8z5gy8y5mbg7.jpeg)

## Quick Start

> Requires inference.sh CLI (`belt`). [Install instructions](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# Recommended: P-Video-Avatar (fastest, cheapest, built-in TTS)
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "Hello, welcome to our product demo!",
  "voice": "Zephyr (Female)"
}'
```

## Available Models

**Start with P-Video-Avatar** — it's 18x faster and 6x cheaper than alternatives, with built-in TTS, dynamic backgrounds, and 1080p support.

| Model | App ID | Best For | Built-in TTS |
|-------|--------|----------|-------------|
| **P-Video-Avatar** | `pruna/p-video-avatar` | **Best overall: speed, cost, quality, control** | **Yes (30 voices, 10 languages)** |
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | Multi-character, audio-driven | No |
| Fabric 1.0 | `falai/fabric-1-0` | Image talks with lipsync | Yes |
| PixVerse Lipsync | `falai/pixverse-lipsync` | Highly realistic lipsync | No |

### Cost & Speed Comparison

| Model | Speed (per sec of video) | Cost per second |
|-------|-------------------------|----------------|
| **P-Video-Avatar** | **~1.83s/s** | **$0.025** |
| OmniHuman 1.5 | ~28s/s (15x slower) | $0.16 (6.4x more) |
| Fabric 1.0 | ~34s/s (18x slower) | $0.14 (5.6x more) |

## Examples

### P-Video-Avatar (Recommended)

Generate avatar from portrait + text script with built-in TTS:

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "Welcome to our product walkthrough. Today I will show you three key features.",
  "voice": "Puck (Male)",
  "voice_language": "English (US)",
  "resolution": "720p"
}'
```

With custom style control:

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "This is exciting news!",
  "voice": "Aoede (Female)",
  "voice_prompt": "Enthusiastic and energetic tone",
  "video_prompt": "The person is presenting on stage with dramatic lighting",
  "resolution": "1080p"
}'
```

With audio file instead of TTS:

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "audio": "https://speech.mp3"
}'
```

### Full Workflow: Generate Portrait + Avatar

Use Pruna P-Image to generate the portrait, then create the avatar:

```bash
# 1. Generate a portrait image
belt app run pruna/p-image --input '{
  "prompt": "professional headshot portrait of a young woman, neutral background, looking at camera, studio lighting, photorealistic",
  "aspect_ratio": "9:16"
}'

# 2. Create avatar video with built-in TTS
belt app run pruna/p-video-avatar --input '{
  "image": "<image-url-from-step-1>",
  "voice_script": "Hi there! Let me walk you through our latest features.",
  "voice": "Zephyr (Female)"
}'
```

### OmniHuman 1.5 (Multi-Character)

```bash
belt app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

Supports specifying which character to drive in multi-person images.

### Fabric 1.0 (Image Talks)

```bash
belt app run falai/fabric-1-0 --input '{
  "image_url": "https://face.jpg",
  "audio_url": "https://audio.mp3"
}'
```

### PixVerse Lipsync

```bash
belt app run falai/pixverse-lipsync --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

## Full Workflow: TTS + Avatar (Non-TTS Models)

For models without built-in TTS, generate speech first:

```bash
# 1. Generate speech from text
belt app run infsh/kokoro-tts --input '{
  "prompt": "Welcome to our product demo. Today I will show you..."
}' > speech.json

# 2. Create avatar video with the speech
belt app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://presenter-photo.jpg",
  "audio_url": "<audio-url-from-step-1>"
}'
```

## Full Workflow: Dub Video in Another Language

```bash
# 1. Transcribe original video
belt app run infsh/fast-whisper-large-v3 --input '{"audio_url": "https://video.mp4"}' > transcript.json

# 2. Translate text (manually or with an LLM)

# 3. Generate speech in new language
belt app run infsh/kokoro-tts --input '{"text": "<translated-text>"}' > new_speech.json

# 4. Lipsync the original video with new audio
belt app run infsh/latentsync-1-6 --input '{
  "video_url": "https://original-video.mp4",
  "audio_url": "<new-audio-url>"
}'
```

## Use Cases

- **Marketing**: Product demos with AI presenter
- **Education**: Course videos, explainers
- **Localization**: Dub content in multiple languages
- **Social Media**: Consistent virtual influencer
- **Corporate**: Training videos, announcements
- **Gaming**: Character avatars, NPC dialogue

## Tips

- Use high-quality portrait photos (front-facing, good lighting)
- Audio should be clear with minimal background noise
- P-Video-Avatar supports built-in TTS — no need for a separate speech generation step
- P-Video-Avatar output aspect ratio matches the input image
- Generate portraits with `pruna/p-image` using `9:16` aspect ratio for vertical videos
- OmniHuman 1.5 supports multiple people in one image
- LatentSync is best for syncing existing videos to new audio

## Related Skills

```bash
# Dedicated P-Video-Avatar skill
npx skills add inference-sh/skills@p-video-avatar

# Full platform skill (all 250+ apps)
npx skills add inference-sh/skills@infsh-cli

# Text-to-speech (generate audio for non-TTS avatar models)
npx skills add inference-sh/skills@text-to-speech

# Speech-to-text (transcribe for dubbing)
npx skills add inference-sh/skills@speech-to-text

# Video generation
npx skills add inference-sh/skills@ai-video-generation

# Image generation (create avatar images)
npx skills add inference-sh/skills@ai-image-generation
```

Browse all video apps: `belt app list --category video`

## Documentation

- [Running Apps](https://inference.sh/docs/apps/running) - How to run apps via CLI
- [Content Pipeline Example](https://inference.sh/docs/examples/content-pipeline) - Building media workflows
- [Streaming Results](https://inference.sh/docs/api/sdk/streaming) - Real-time progress updates
