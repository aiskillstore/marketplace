---
name: video-to-music
description: Score a video with original music using Sonilo — the model watches the cut and matches pacing, motion, and emotion, returning either the audio or a new video with the score muxed in. Use when the user has a finished video that needs a soundtrack. Every track is licensed and cleared for commercial use. For music with no video, use the text-to-music skill.
license: MIT
compatibility: "Requires Sonilo through either transport — the MCP server connected, or the `sonilo` CLI installed and signed in — plus credentials: a `sonilo login` sign-in, the hosted OAuth plugin, or SONILO_API_KEY. See the setup-api-key skill."
allowed-tools: Bash, Read, Write, mcp__sonilo__*
---

# Sonilo Video-to-Music

Hand Sonilo a finished video and it composes an original score to the cut —
pacing, motion, and emotion matched, with transitions and beat drops aligned to
the edit, at exactly the video's length. This is Sonilo's flagship capability.
Every track is licensed (music licensed via Shutterstock) and cleared for
commercial use on social, brand content, and advertising.

> **Setup:** See the [setup-api-key](../setup-api-key) skill to connect the Sonilo MCP server and authenticate — `sonilo login` (no key) or `SONILO_API_KEY`.

> ⚠️ **Cost:** every tool below makes an API call that may incur charges. Only call it when the user has actually asked for a generation. Check `get_account_services` (see the [account](../account) skill) if you're unsure whether free-trial runs remain.

## Transport: MCP or CLI

Pick one at the start of the session and stay on it. Do not mix the two inside
a single job, and do not announce the choice.

1. **Sonilo MCP tools visible in this session** (`video_to_music` and friends) — use them. This is the preferred path: it needs no shell, and it is the only one that survives a very long generation. If a call fails to authenticate — rather than failing on its inputs — this transport is not usable in this session: go to 2 instead of retrying it.
2. **No usable Sonilo MCP tools, but `sonilo account` exits 0** — use the CLI commands below. Same API, same account, same credential file. Probe with `sonilo account`, not `sonilo whoami`: whoami exits 0 even when signed out, so it cannot tell the two states apart.
3. **Neither** — stop and run the [setup-api-key](../setup-api-key) skill. Do not call `api.sonilo.com` with curl to work around it; both transports handle uploads, polling and retries that a bare request does not.

## Quick Start

### MCP tool call (recommended)

```
video_to_music(
    video_path="~/Desktop/trailer.mp4",
    prompt="Build suspense, then resolve with a warm cinematic finish"
)
```

Saves the generated file(s) to `SONILO_MCP_BASE_PATH` (`~/Desktop` by default) and returns the saved path(s) as text.

### Python (`pip install sonilo`)

```python
from sonilo import Sonilo

client = Sonilo()  # reads SONILO_API_KEY

score = client.video_to_music.generate(video="trailer.mp4", prompt="Build suspense, then resolve with a warm cinematic finish")
score.save("score.m4a")

# video_to_video_music: get the video back with the music muxed in
video = client.video_to_video_music.generate(video="trailer.mp4", prompt="cinematic, uplifting")
video.save("scored.mp4")
```

`preserve_speech=True` on `video_to_music` requires the async path — use `generate_async()` instead of `generate()` to get the extra `vocals`/`mux`/`ducked` outputs; see [sonilo-python's README](https://github.com/sonilo-ai/sonilo-python#preserve-speech-async) for the full pattern.

### JavaScript / TypeScript (`npm install sonilo`)

```ts
import { SoniloClient } from "sonilo";

const client = new SoniloClient(); // reads SONILO_API_KEY

const score = await client.videoToMusic.generate({
  video: "./trailer.mp4",
  prompt: "Build suspense, then resolve with a warm cinematic finish",
});

// video_to_video_music: get the video back with the music muxed in
const video = await client.videoToVideoMusic.generate({
  video: "./trailer.mp4",
  prompt: "cinematic, uplifting",
});
```

`preserveSpeech: true` on `videoToMusic` requires the async path — use `.submit()` + `client.tasks.wait()` instead of `.generate()`; see [sonilo-js's README](https://github.com/sonilo-ai/sonilo-js/tree/main/packages/sonilo#preserve-speech-async) for the full pattern.

### CLI (`npm install -g sonilo-cli` or `pip install sonilo-cli`)

```bash
sonilo video-to-music --video trailer.mp4 --prompt "Build suspense, then resolve with a warm cinematic finish" --output score.m4a
```

`--format wav`, `--preserve-speech`, and `--isolate-vocals` each switch `video-to-music` to the async submit-and-poll path.

```bash
# the muxed video, from the CLI
sonilo video-to-video-music --video trailer.mp4 --prompt "cinematic, uplifting" --output scored.mp4
```

### cURL (raw REST API, no MCP host)

```bash
curl -X POST "https://api.sonilo.com/v1/video-to-music" \
  -H "Authorization: Bearer $SONILO_API_KEY" \
  -F "video=@trailer.mp4" \
  -F "prompt=Build suspense, then resolve with a warm cinematic finish" \
  --output score.m4a
```

`video_to_music` also accepts a `video_url` form field instead of an uploaded file — pass one or the other, never both.

## Tools

| Tool | Description |
|------|-------------|
| `video_to_music(video_path? \| video_url?, prompt?, preserve_speech?, output_format?, ducking?, variants_num?, prompt_influence?, stems?, output_directory?)` | Score a video: matches pacing/motion/emotion, matches the video's duration exactly. Returns audio only (the video itself is not muxed). |
| `video_to_video_music(video_path? \| video_url?, prompt?, segments?, keep_original_sound?, ducking?, preserve_speech?, variants_num?, prompt_influence?, output_directory?)` | Same scoring, but returns a **new `.mp4`** with the music already muxed in. **By default the source's own audio is dropped** — see `keep_original_sound`. |

## Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `prompt` | string | — | Optional style hint. Omit to let the footage lead entirely. |
| `video_path` | string | — | Absolute path, or relative to `SONILO_MCP_BASE_PATH`. `.mp4/.mov/.avi/.wmv/.webm/.mkv`. Max **360s (6 min)**, subject to the account's upload-size cap (typically 300 MB). |
| `video_url` | string | — | HTTPS URL to a video file. Exactly one of `video_path`/`video_url`. |
| `preserve_speech` | bool | `false` | Keeps the source speech audible. On `video_to_music`, also returns a `vocals` speech stem and a ready-to-use `mux` (speech+music mixed) — this makes the call run asynchronously (submit + poll) instead of streaming, so it takes a bit longer but the tool still waits for completion. |
| `ducking` | bool \| null | server default ON for `video_to_music`, `false` for `video_to_video_music` | Dips the generated music under the source voice. Free, best-effort. On `video_to_video_music` it only does anything alongside `keep_original_sound` or `preserve_speech` — with neither, there is no source voice left in the output to duck under. |
| `keep_original_sound` | bool | `false` | `video_to_video_music` only. **This is the parameter to reach for when the result sounds wrong.** By default the returned `.mp4` carries the generated music *alone* — the source's dialogue, room tone, and effects are gone. Set `true` to keep the whole source track with the music mixed under it, and add `ducking=true` to dip the music under the voice rather than mixing it flat. `keep_original_sound` supersedes `preserve_speech`. |
| `variants_num` | int | `1` | 1–10. Generates that many distinct creative directions in one request — different takes, not re-renders of one. **Cost scales linearly with the count, and any value above 1 is never covered by the free trial**, so confirm the number with the user first. Above 1 writes one file per variant and forces the backend's async mode. |
| `prompt_influence` | float \| null | API default `0.5` | 0–1: how strictly the music follows your prompt versus what the video itself suggests. Lower lets the footage lead, higher enforces the brief. **Free**, and it does not change the mode or the number of files — omit it unless the user asks for stricter or looser adherence. |
| `stems` | bool | `false` | `video_to_music` only — `video_to_video_music` has no such param. **Free.** Additionally splits each **generated** track into four separated instrument tracks — `drums`, `bass`, `vocals`, `other` — returned alongside the untouched full mix. It never touches the video's own audio. Async-only on REST (`stems=true` without `mode=async` is a `400`). See [Stems](#stems). |
| `output_format` | string | `m4a` | `video_to_music` only — `video_to_video_music` has no such param and always outputs a muxed `.mp4`. `m4a` or `wav`. `wav` (and `preserve_speech`/`ducking`) triggers the backend's async mode internally. |
| `output_directory` | string | `SONILO_MCP_BASE_PATH` | Absolute, or relative to the base path. |

## Stems

`stems=true` on `video_to_music` additionally returns each generated track
split into four separated instrument tracks — `drums`, `bass`, `vocals`,
`other` — **free of charge**. The full mix is untouched; the stems arrive
alongside it in the task result as a `stems` array next to `audio`:

```json
"stems": [
  {
    "stream_index": 0,
    "drums":  { "url": "…", "content_type": "audio/mp4", "file_size": 2913044 },
    "bass":   { "url": "…", "content_type": "audio/mp4", "file_size": 2870211 },
    "vocals": { "url": "…", "content_type": "audio/mp4", "file_size": 2794560 },
    "other":  { "url": "…", "content_type": "audio/mp4", "file_size": 3011830 }
  }
]
```

What matters when you use it:

- **It splits the GENERATED music, never the video's own audio.** The `vocals` stem is whatever singing the generated score contains — usually near-silent, since scores are mostly instrumental, and that is correct behavior, not a bug. To get the *source* speech isolated, use `preserve_speech` (a different feature) instead.
- **Async only on REST.** `stems=true` requires `mode=async` (a `400` otherwise): you get a `202` + `task_id` and poll `/v1/tasks/{task_id}`. The MCP tools are always async, so on the hosted server the param just works.
- **Available on every surface** (verified 2026-08-17): REST, the hosted MCP server, the local `sonilo-mcp` package (>= 0.18.0), the SDKs (`sonilo` npm >= 0.16.0, PyPI >= 0.15.0), and the CLIs (`--stems`, npm `sonilo-cli` >= 0.15.0, PyPI `sonilo-cli` >= 0.14.0).
- **Match stems to tracks by `stream_index`, never by array position.** A stream whose separation failed is simply absent, so `stems` can be shorter than `audio`.
- **`stems_error` is not a failed generation.** When separation failed wholly or partly, or was skipped, the task carries a `stems_error` string — possibly *alongside* a partial `stems` array. The generation itself succeeded and every `audio` URL is valid: treat missing stems as a missing extra, never as a reason to retry or refund.
- **Timing:** separation runs after generation finishes — typically another 2–6 min, giving up after 30 min (then `stems_error`).
- **The four stem names are fixed** (htdemucs separation): melodic instruments — piano, synths, guitar, strings — land in `other`.
- **Formats:** stems normally follow `output_format`; trust each stem's `content_type` for what was actually delivered.

## Prompting

No prompt is required — the model reads the cut. A short structured brief adds
what the video can't carry: your intent — genre, the moment that must hit, the
sounds that must not appear.

Before a paid call: probe the exact duration and existing audio, respect the
**360 s** cap (over = 422 reject, never truncated), and get sign-off — failed
runs auto-refund, but your own retry is a new charge. Write the brief first,
generate once, iterate on the prompt, not on rerolls.

- Full pre-flight (inspect the video, caps, credits, verification): [references/preflight.md](../references/preflight.md)
- Style-prompt craft (audio brief, genre/energy wording, `preserve_speech`, segmented music): [references/music-prompting.md](../references/music-prompting.md)

## Workflow Tips

- **Prompting:** a style hint (e.g. "cinematic, uplifting") steers the result, but the prompt is optional — Sonilo already reads the footage.
- **`preserve_speech` for talking-head or narrated video:** if the source has dialogue/voiceover the user wants kept, set `preserve_speech=true`. Behavior differs by tool: on `video_to_music` you get the music, the isolated speech stem, *and* a ready-mixed combined file (the mux) — use the mux directly rather than re-mixing yourself. On `video_to_video_music` there's no separate stem or mux file; it just keeps the source speech audible in the single muxed output video.
- **Want the video back with the score baked in?** Use `video_to_video_music` instead of `video_to_music` — same inputs, but the output is a new `.mp4`, not just audio. **Warn the user that the source audio is dropped by default**: if their video has dialogue, narration, or effects they expect to hear, pass `keep_original_sound=true` (add `ducking=true` to keep the voice on top), or `preserve_speech=true` for the isolated speech only. A "the music is there but my voiceover vanished" report is always this.
- **Several takes in one go:** `variants_num=3` returns three distinct directions for one request instead of three re-rolls. It costs 3×, and it is never free-trial covered — say the price before calling.
- **User wants the score's instruments as separate files** (to remix, re-balance, or drop one)? `stems=true` on `video_to_music` — it's free, but async-only and not on every surface yet, and it splits the generated music, never the source audio; see [Stems](#stems).
- **Duration:** always matched to the source video automatically — don't ask for it.
- **Need SFX too?** To generate music **and** sound effects for the same video in one balanced, single-charge call, use [video-to-sound](../video-to-sound) rather than calling this and [video-to-sfx](../video-to-sfx) separately.
- **Don't know what it should sound like?** Run [video-analysis](../video-analysis) first: one call returns a section plan plus ready-to-use generation prompts read off the footage, which beats guessing a prompt and rerolling. It is a paid call that generates nothing, so use it when the brief is genuinely unclear — not when the user already told you what they want.
- **Content restriction:** prompts cannot reference specific artists, bands, or copyrighted lyrics.

## Recovering a Timed-Out Call

`video_to_music` (without any of `preserve_speech`/`ducking`/`stems`/`output_format="wav"`) streams its result in one call. Any variant that triggers the backend's async mode — and `video_to_video_music`, which is always async — can time out on a very long `TIME_OUT_SECONDS`. If it does, the error message includes a `task_id`; the generation keeps running (and is already charged) on the backend. Call `get_sfx_task(task_id)` — `get_generation_task(task_id)` on the hosted server — to retrieve the result once ready; see the [task-recovery](../task-recovery) skill.

## Output Files

- `video_to_music`: `.m4a` by default (`.wav` if requested), named from the prompt (slugified) or `sonilo-<timestamp>.m4a`. Multiple parallel streams get a `-<index>` suffix.
- `video_to_music(preserve_speech=true)`: also saves `<base>-vocals.<ext>` (isolated speech) and `<base>-mux.<ext>` (speech+music combined — the one to actually use).
- `video_to_video_music`: a single `.mp4` with the score muxed in.

## Error Handling

Common errors: `401` invalid key, `402` insufficient balance / trial exhausted, `413` file too large, `422` invalid parameters (e.g. video over the 360 s cap), `429` rate limit. See the [account](../account) skill to check trial/usage before a call, and the sonilo-mcp README's error table for exact recovery steps.
