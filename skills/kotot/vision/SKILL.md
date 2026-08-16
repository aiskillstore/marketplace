---
name: vision
description: >-
  See and understand images when you (the current model) have no native vision.
  Use this WHENEVER you need to look at, read, describe, OCR, or reason about
  the contents of an image, screenshot, photo, diagram, chart, UI mockup, or
  scanned page — including when the user references a local image file or an
  image URL and you cannot view it yourself. Also triggers on: 看图 / 识图 / 截图 /
  图片内容 / OCR 文字识别 / 这张图是什么. Delegates the actual seeing to a configurable
  OpenAI-compatible vision model via a small script.
---

# Vision (delegated image understanding)

You do not have native vision, but you can still "see" an image by running the
bundled script, which sends the image to a configurable OpenAI-compatible vision
model and returns a text answer.

## When to use

Use this skill whenever a task requires understanding image content and you
cannot view it directly, for example:

- The user uploads or points to an image / screenshot / photo and asks what's in it.
- You need to read text inside an image (OCR).
- You need to diagnose an error from a screenshot.
- You need to understand a UI mockup, diagram, chart, or scanned document.
- You need to compare what an image shows against code or expected output.

## How to use

Run the script with the Bash tool. Pass the image (local path or http(s) URL)
and a clear, specific instruction describing what you need to know:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/see.py" <image_path_or_url> "your question"
```

If `$CLAUDE_SKILL_DIR` is not set in your environment, use the relative path to
this skill folder, e.g. `python3 scripts/see.py ...` from the skill directory,
or the absolute path where the skill is installed.

Examples:

```bash
# Describe an image
python3 scripts/see.py ./photo.jpg "Describe this image in detail"

# OCR — extract text
python3 scripts/see.py ./receipt.png "Transcribe all text exactly, preserving layout"

# Diagnose an error screenshot
python3 scripts/see.py ./error.png "What error is shown and what is the likely cause?"

# Read a chart into structured data
python3 scripts/see.py ./chart.png "Extract every series, label, and value as a markdown table"

# Remote image
python3 scripts/see.py "https://example.com/diagram.png" "Explain this architecture diagram"
```

The script prints the model's answer to stdout. Read that answer and use it to
continue the task. Ask a focused question rather than a generic "describe" when
you need something specific (a value, a status, an error message) — you get
better results and spend fewer tokens.

## Configuration (required, set once)

The script reads its config from environment variables **or** a
`.claude/settings.json` `env` block (same variable names as the
vision-mcp-server MCP, so config carries over). Resolution order: an explicit
environment variable wins; otherwise the script reads `.claude/settings.json`,
searching from the current directory upward and then `~/.claude/`.

| Variable | Required | Example |
| --- | --- | --- |
| `VISION_BASE_URL` | yes | `http://localhost:1234/v1/chat/completions` |
| `VISION_MODEL` | yes | `Qwen3-VL-32B`, `gpt-4o`, `glm-4v`, ... |
| `VISION_API_KEY` | no* | your API key (*optional for local servers) |
| `VISION_MAX_TOKENS` | no | `4096` |
| `VISION_TEMPERATURE` | no | `0.2` |
| `VISION_DETAIL` | no | `auto` \| `low` \| `high` |
| `VISION_TIMEOUT` | no | `120` |

> `VISION_BASE_URL` must be the **full** chat-completions endpoint
> (`.../v1/chat/completions`), not just the base URL.

Set them in your shell profile, or in the MCP/agent `env` block, or inline:

```bash
export VISION_BASE_URL=http://localhost:1234/v1/chat/completions
export VISION_MODEL=Qwen3-VL-32B
export VISION_API_KEY=sk-...        # optional for local
```

Or put them in `.claude/settings.json` (project-level, or global `~/.claude/`):

```jsonc
{
  "env": {
    "VISION_BASE_URL": "http://localhost:1234/v1/chat/completions",
    "VISION_MODEL": "Qwen3-VL-32B",
    "VISION_API_KEY": "sk-..."
  }
}
```

## Notes

- Pure Python standard library — no `pip install` needed.
- Local files are auto-converted to a base64 data URL; http(s) URLs are passed through.
- If the script reports a missing variable or an unreachable endpoint, fix the
  config above and retry. Add `--dry-run` to inspect the request without sending it:
  `python3 scripts/see.py --dry-run img.png "test"`.
