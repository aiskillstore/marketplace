# video-enhancement - AI Video Enhancement

Upscale and enhance video quality using AI. Supports local files and YouTube/Bilibili URLs.

## Install

```bash
npx skills add verging-ai/agent-skills --skill video-enhancement
```

## Setup

1. Visit [verging.ai](https://verging.ai)
2. Login → Click avatar (top right) → API Keys
3. Create a key, then set it:

```bash
export VERGING_API_KEY="vrg_sk_your_key_here"
```

## Requirements

- `yt-dlp` (for downloading YouTube/Bilibili videos)
- `ffmpeg` / `ffprobe` (for trimming)
- `curl`

## Usage

```bash
# Enhance a local video
/video-enhancement -v ./video.mp4

# Enhance a YouTube video
/video-enhancement -v "https://youtube.com/watch?v=xxx"

# HD upscaling, trim to first 20 seconds, auto-download
/video-enhancement -v ./video.mp4 --end 20 --hd --download
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --video | -v | Video file or URL | Required |
| --start | -s | Start time (seconds) | 0 |
| --end | -e | End time (seconds) | Video end |
| --hd | | HD upscaling (4K) | false |
| --download | -d | Auto-download result | false |
| --output | -o | Output path | Current dir |

## Credits

| Mode | Cost |
|------|------|
| Normal | 3 credits/second |
| HD | 5 credits/second |

Max video duration: 30 seconds (longer videos are auto-trimmed).

## Links

- Website: https://verging.ai
- API Docs: https://verging.ai/docs/api
