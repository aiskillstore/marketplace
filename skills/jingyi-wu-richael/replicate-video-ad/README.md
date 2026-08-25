# Replicate Video Ad

English | [简体中文](README.zh-CN.md)

A Codex skill for turning a reference video into an evidence-based shot analysis and a production-ready ecommerce story-ad replication prompt.

It preserves the source video's pacing, framing, narrative mechanics, product reveal, proof sequence, and conversion logic while replacing identities, branding, unsupported claims, and platform chrome.

## What It Produces

- High-density frame sampling at up to 2 fps, with contact sheets and a storyboard
- A timestamped shot timeline covering action, dialogue or subtitles, story function, and product exposure
- A breakdown of the hook, escalation, reversal, product bridge, proof, payoff, and CTA
- A copy-ready master prompt for adapting the structure to another product
- Dialogue and voice direction, post-production copy, negative constraints, and a segmented generation plan
- Explicit separation between observed facts, adaptation decisions, and claims that still need confirmation

## Requirements

- Codex or another agent runtime that supports folder-based skills
- Python 3.10+
- `ffmpeg` and `ffprobe`
- Optional: `yt-dlp` for direct URL input
- Optional: the `watch` skill for transcript and frame acquisition before deterministic extraction

The bundled extractor uses only the Python standard library. It calls the external binaries above when needed.

## Installation

Clone the repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Jingyi-Wu-Richael/replicate-video-ad.git \
  ~/.codex/skills/replicate-video-ad
```

Restart Codex or start a new task so the skill can be discovered.

## Usage

Invoke the skill explicitly and attach a local video:

```text
Use $replicate-video-ad to analyze this reference video and adapt its story structure for my skincare product.
```

You can also provide a public video URL:

```text
Use $replicate-video-ad to break down this video and create a 30-second Douyin ecommerce story-ad prompt for 【产品名】: 【URL】
```

When product facts are incomplete, the skill keeps placeholders such as `【品牌】`, `【产品名】`, and `【核心卖点】` instead of inventing claims.

## Bundled Extractor

Run the deterministic extractor directly when you already have a local video:

```bash
python3 scripts/extract_video.py "/path/to/reference.mp4" \
  --out-dir "/path/to/new-output-directory" \
  --fps 2 --max-frames 120 --width 768
```

Add `--extract-audio` to create a mono 16 kHz MP3 for an available transcription workflow.

The output directory must be new or empty. Typical extractor artifacts include:

```text
storyboard.jpg
frames.zip
frame_manifest.json
frame_manifest.csv
contact_sheets/
frames/
audio.mp3             # only with --extract-audio
```

## Repository Structure

```text
replicate-video-ad/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── ad-framework.md
│   └── output-template.md
└── scripts/
    └── extract_video.py
```

## Responsible Replication

This skill is designed to reproduce structure and conversion mechanics, not identity. It avoids copying identifiable faces, voices, watermarks, account names, platform UI, and unsupported product claims. Dialogue is included only when supported by captions, a permitted transcript, or visible burned-in subtitles.

The default review is high-density frame sampling, not literal extraction of every encoded frame.
