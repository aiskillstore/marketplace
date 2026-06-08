# stt - AI Speech-to-Text Transcription

Transcribe audio files to text using OpenAI Whisper via the verging.ai API. Supports MP3, WAV, M4A, and more.

## Install

```bash
npx skills add verging-ai/agent-skills --skill stt
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
# Transcribe an audio file
curl -X POST https://verging.ai/api/v1/ai/stt \
  -H "Authorization: ApiKey $VERGING_API_KEY" \
  -F "file=@recording.mp3" \
  -F "language=en"
```

## Supported Audio Formats

MP3, MP4, MPEG, MPGA, M4A, WAV, WebM (max 25MB)

## Features

- Powered by OpenAI Whisper model
- Automatic language detection
- Customizable output format and temperature
- Low cost: 1 credit per minute of audio

## Credits

| Rate | Minimum |
|------|---------|
| 1 credit / minute | 1 credit |

## Links

- Website: https://verging.ai
- API Docs: https://verging.ai/docs/api
