# 🔧 TTS-Skill Installation Guide

## Requirements

- **OS**: Windows 10+, macOS 10.15+, Linux
- **Python**: 3.8+ (Qwen3-TTS runtime requires Python 3.12 via micromamba env)
- **RAM**: 4GB+ (8GB+ recommended for local cloning)
- **Disk**: 10GB+ free space (models take space)
- **Network**: Required for VoiceCraft and OpenAI; also used to download Qwen models
- **GPU**: Recommended (4GB+ VRAM) for Qwen3-TTS

## Quick Start

### 1) Get the project

```bash
git clone <your-repo>/tts-skill.git
cd tts-skill
python --version
```

### 2) Install Qwen3-TTS environment (optional, for local voice cloning)

```bash
python tts-skill.py --install
```

You can also run the engine installer directly:

```bash
python engines/qwen3-tts-cli.py --install
```

### 3) Verify

```bash
python tts-skill.py --list-engines
python tts-skill.py --list-voices
python tts-skill.py --help
```

## Output Convention (Default)

If you do not pass `--output`, all engines write to `output/` by default.

- Filename pattern: `YYYYMMDD_HHMMSS_<first-6-chars>.<ext>`
- Examples:
  - `output/20260128_153012_胜利在呼唤.wav`
  - `output/20260128_153012_Hello_.mp3`

## Engine Configuration

### Qwen3-TTS (Local Voice Cloning)

Qwen3-TTS can be configured via `engines/qwen3-tts.config`:

```ini
[Qwen3-TTS]
model_dir = ./Qwen3-TTS-12Hz-0.6B-Base
default_voice = 赵信
output_format = wav
device = auto
```

On Windows, Qwen3-TTS uses a micromamba environment named `qwen3-tts`. The installer will try to set this up automatically.

### VoiceCraft (Edge TTS via Online API)

```bash
python engines/edge-tts-cli.py --list-voices
python engines/edge-tts-cli.py --list-styles
```

Optional config file: `engines/edge-tts.config`

### OpenAI TTS

Create/edit `engines/openai-tts.config`:

```ini
[OpenAI]
api_key = your_openai_api_key_here
base_url = https://api.openai.com/v1
voice = alloy
model = tts-1
speed = 1.0
```

## First-run Tests

### VoiceCraft

```bash
python tts-skill.py edge-tts "Hello from VoiceCraft" --voice xiaoxiao
```

### Qwen3-TTS

```bash
python tts-skill.py qwen3-tts "德玛西亚！" --voice 赵信
python tts-skill.py qwen3-tts --text-file "input/text.txt" --voice 寒冰射手
```

### OpenAI TTS

```bash
python tts-skill.py openai-tts "Hello World" --voice alloy
python tts-skill.py openai-tts "测试文本" --voice nova --model tts-1-hd
```

## Troubleshooting

- **Qwen3-TTS install fails**: verify micromamba is available, and networking is working for model downloads.
- **VoiceCraft timeout**: check network connectivity; update the API endpoint in `engines/edge-tts.config` if needed.
- **OpenAI auth fails**: verify `api_key`, and account permissions/billing status.

## Chinese Docs

- See [INSTALL.zh-CN.md](INSTALL.zh-CN.md) for the original Chinese version.
