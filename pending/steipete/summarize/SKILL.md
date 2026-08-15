---
name: summarize
description: "Summarize CLI: URLs, files, YouTube, transcripts, media, extraction, and JSON output."
---

# Summarize

Use the `summarize` CLI as the canonical interface. Prefer a released binary on `PATH`; inside this repository, use `pnpm -s summarize` for the current checkout.

## Start

1. Confirm the command and current contract:

   ```bash
   summarize --version
   summarize --help
   ```

2. Inspect model/provider readiness when a summary needs an LLM:

   ```bash
   summarize status
   summarize status --json
   ```

3. Run the narrowest workflow below. Quote URLs and paths. Add `--timeout 2m` for slow remote or media inputs.

Never print, request, or copy API-key values. `summarize status` reports availability without exposing secrets.

## Summarize

Web page or remote document:

```bash
summarize "https://example.com/article"
summarize "https://example.com/report.pdf" --length short
```

Local file or stdin:

```bash
summarize "./report.pdf"
summarize "./recording.m4a"
printf '%s\n' "Long text to summarize" | summarize -
```

Use `--plain` for unrendered Markdown/text. Use `--language`, `--length`, `--prompt`, or `--prompt-file` only when the task requires an override. Use `--cli codex`, `--cli claude`, or another installed CLI provider when the user requests that provider or no direct API provider is configured.

## Extract without a summary

Use `--extract` to stop after extraction or transcription:

```bash
summarize "https://example.com/article" --extract --format md
summarize "./report.pdf" --extract --format md
summarize "https://youtu.be/VIDEO_ID" --extract --format md
```

`--extract` does not support stdin. Extraction can still call configured transcription, OCR, Firecrawl, or Markdown services; it only skips the final summary call. `--markdown-mode llm` also invokes an LLM to reshape extracted text.

## YouTube, audio, and video

Default transcript selection:

```bash
summarize "https://youtu.be/VIDEO_ID"
summarize "https://youtu.be/VIDEO_ID" --extract --format md --timestamps
```

Use `--youtube web` to require web captions or `--youtube yt-dlp` to require the download/transcription path. Keep `auto` unless the user needs a specific source.

Local or remote audio/video:

```bash
summarize "./interview.mp3" --extract
summarize "./interview.mp4" --extract --timestamps
summarize "./interview.mp3" --extract --diarize
```

`--transcriber auto` is the default. Use an explicit transcriber only when requested or diagnosing a provider. Diarization may require configured ElevenLabs or OpenAI access. Speaker identification is a separate opt-in step; do not infer identities without evidence.

For slides:

```bash
summarize "https://youtu.be/VIDEO_ID" --slides
summarize "./talk.mp4" --slides --extract
```

Slide extraction may require `yt-dlp`; OCR requires `tesseract`.

## JSON for automation

Use JSON when another command or agent will parse the result:

```bash
summarize "https://example.com" --json --metrics off > result.json
jq -r '.summary // .extracted.content // empty' result.json
```

The stable top-level envelope contains `input`, `env`, `extracted`, `prompt`, `llm`, `metrics`, and `summary`. `summary` or `llm` can be `null` when extraction or a no-model path handles the input. In `--extract --json` mode, read extracted text from `.extracted.content`.

JSON stays on stdout. Progress, warnings, and finish metrics stay on stderr. Do not merge stderr into stdout before parsing. Use `--metrics detailed` only when the task needs usage details.

## Configuration and dependencies

Precedence: CLI flags, process environment, `~/.summarize/config.json`, built-in defaults. Prefer flags for one run; change config only when the user asks for a persistent default.

Useful diagnostics:

```bash
summarize status --verbose
summarize status --probe
summarize "INPUT" --verbose
```

Plain web summaries need no media tools. Media paths may use `ffmpeg`, `yt-dlp`, local Whisper/ONNX, or configured cloud transcription. Website fallback may use Firecrawl. Confirm the exact missing capability from the error before installing tools or changing config.

Inputs may be sent to the selected model, extraction, OCR, or transcription provider. For confidential material, confirm the approved provider or use an approved local path before running the command.

## Verify

After every run:

- Require exit status `0`.
- Require non-empty summary or extracted content.
- For JSON, parse stdout with `jq` or another JSON parser.
- For source-sensitive work, inspect `extracted`, `llm`, and stderr diagnostics rather than assuming the selected path.
- Re-run the exact final command after changing provider, config, or flags.

For current option details, run `summarize --help` and read the repository documentation:

- [Quickstart](../../../docs/quickstart.md)
- [Main command](../../../docs/commands/summarize.md)
- [Configuration](../../../docs/config.md)
- [YouTube](../../../docs/youtube.md)
- [Media](../../../docs/media.md)
- [Extraction](../../../docs/extract-only.md)

## Ownership

This file is the canonical agent workflow for the Summarize product. Keep generic agent workflows in `openclaw/agent-skills`; keep Summarize CLI behavior here. Downstream integrations should link to this file at a released tag or pinned commit and retain only their packaging or integration-specific notes. Do not maintain a second broad command guide downstream.
