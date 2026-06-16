# Discovering Apps

## Your Apps

```bash
belt app list
belt app list --search "flux"
belt app search "flux"
belt app list -l  # detailed
```

## Browse the Public Store

```bash
belt app store
```

## Pagination

```bash
belt app store --page 2
```

## Filter by Category

```bash
belt app store --category image
belt app store --category video
belt app store --category audio
belt app store --category text
belt app store --category other
```

## Search the Store

```bash
belt app store search "flux"
belt app store search "video generation"
belt app store search "tts" -l
belt app store search "image" --category image
```

## Featured Apps

```bash
belt app store --featured
```

## Newest First

```bash
belt app store --new
```

## Detailed View

```bash
belt app store -l
```

Shows table with app name, category, description, and featured status.

## Save to File

```bash
belt app store --save apps.json
```

## Get App Details

```bash
belt app get falai/flux-dev-lora
belt app get falai/flux-dev-lora --json
```

Shows full app info including input/output schema.

## Popular Apps by Category

### Image Generation
- `falai/flux-dev-lora` - FLUX.2 Dev (high quality)
- `falai/flux-2-klein-lora` - FLUX.2 Klein (fastest)
- `infsh/sdxl` - Stable Diffusion XL
- `google/gemini-3-pro-image-preview` - Gemini 3 Pro
- `xai/grok-imagine-image` - Grok image generation

### Video Generation
- `google/veo-3-1-fast` - Veo 3.1 Fast
- `google/veo-3` - Veo 3
- `bytedance/seedance-2-0` - Seedance 2.0
- `bytedance/seedance-2-0-fast` - Seedance 2.0 Fast
- `infsh/ltx-video-2` - LTX Video 2 (with audio)
- `bytedance/omnihuman-1-5` - OmniHuman avatar

### Audio
- `infsh/dia-tts` - Conversational TTS
- `infsh/kokoro-tts` - Kokoro TTS
- `infsh/fast-whisper-large-v3` - Fast transcription
- `infsh/diffrythm` - Music generation

## Documentation

- [Browsing the Grid](https://inference.sh/docs/apps/browsing-grid) - Visual app browsing
- [Apps Overview](https://inference.sh/docs/apps/overview) - Understanding apps
- [Running Apps](https://inference.sh/docs/apps/running) - How to run apps
