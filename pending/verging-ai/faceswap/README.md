# faceswap - AI Face Swap

Swap faces in videos using AI, right from the command line. Supports local files, YouTube/Bilibili URLs, and remote images.

## Demo

[![Face Swap Demo](https://img.youtube.com/vi/xvlZe4uqvY4/maxresdefault.jpg)](https://youtu.be/xvlZe4uqvY4)

▶️ Click to watch demo video

## Install

```bash
npx skills add verging-ai/agent-skills --skill faceswap
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
# Local video + local face image
/faceswap -v ./video.mp4 -f ./face.jpg

# YouTube URL + remote face image
/faceswap -v "https://youtube.com/watch?v=xxx" -f "https://example.com/face.jpg"

# Trim to 10-25 seconds, HD mode, auto-download result
/faceswap -v ./video.mp4 -f ./face.jpg --start 10 --end 25 --hd --download
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --video | -v | Video file or URL | Required |
| --face | -f | Face image file or URL | Required |
| --start | -s | Start time (seconds) | 0 |
| --end | -e | End time (seconds) | Video end |
| --hd | | HD quality | false |
| --download | -d | Auto-download result | false |
| --output | -o | Output path | Current dir |

## Credits

| Mode | Cost |
|------|------|
| Normal | 1 credit/second |
| HD | 3 credits/second |

Max video duration: 30 seconds (longer videos are auto-trimmed).

## Links

- Website: https://verging.ai
- API Docs: https://verging.ai/docs/api
