# 🎙️ TTS-Skill — Multi-Engine Text-to-Speech

TTS-Skill is a unified entrypoint that wraps multiple TTS engines:

- **Qwen3-TTS**: local voice cloning (reference audio + reference transcript)
- **VoiceCraft / Edge TTS**: online Microsoft-style voices with speed/pitch/style controls
- **OpenAI TTS**: commercial-quality speech generation via API

## Key Features

- **Multi-engine routing**: choose the best engine per use case
- **Voice matching**: pick a voice by filename keyword (for local cloning)
- **Progress feedback**: long-running Qwen3-TTS jobs show a live progress bar and ETA
- **Consistent outputs**: default output goes to `output/` with a predictable name

## Default Output

If `--output` is not provided:

- Output directory: `output/`
- Filename: `YYYYMMDD_HHMMSS_<first-6-chars>.<ext>`

## Quick Start (CLI)

```bash
# Local voice cloning (Qwen3-TTS)
python tts-skill.py qwen3-tts "胜利在呼唤，勇往直前" --voice 赵信

# Online voices (VoiceCraft / Edge)
python tts-skill.py edge-tts "你好，这是一个测试" --voice xiaoxiao

# OpenAI TTS
python tts-skill.py openai-tts "Hello, this is a test" --voice alloy
```

Read long text from a file:

```bash
python tts-skill.py qwen3-tts --text-file "input\\text.txt" --voice 寒冰射手
```

## Voices

### Local (Qwen3-TTS)

Place a pair of files in `assets/`:

- `assets/<VoiceName>.wav` (or `.mp3/.m4a/.flac`)
- `assets/<VoiceName>.txt` (the transcript matching the audio)

Then use:

```bash
python tts-skill.py qwen3-tts "测试文本" --voice <VoiceName>
```

### VoiceCraft / Edge

```bash
python engines/edge-tts-cli.py --list-voices
python engines/edge-tts-cli.py --list-styles
```

### OpenAI

Create `engines/openai-tts.config` and set `api_key`.

## Docs

- Installation: [INSTALL.md](INSTALL.md)
- Skill spec: [SKILL.md](SKILL.md)
- Chinese README: [README.zh-CN.md](README.zh-CN.md)

## Acknowledgements

This project uses components from [https://github.com/wangwangit/tts](https://github.com/wangwangit/tts). Special thanks to the original authors for their contributions to the TTS community.
