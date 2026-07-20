---
name: fish-audio
description: Generate AI text-to-speech audio with Fish Audio and browse public reference voices via AceDataCloud API. Use when creating voiceover/narration audio (TTS), synthesizing multilingual speech, or selecting a Fish reference voice from the model catalog.
license: Apache-2.0
metadata:
  author: acedatacloud
  version: "1.1"
compatibility: Requires ACEDATACLOUD_API_TOKEN in .env file (see _shared/authentication.md).
---

# Fish Audio — Text-to-Speech

Generate narration / voiceover through AceDataCloud's Fish Audio API.

> **Setup:** See [authentication](../_shared/authentication.md) for token setup.

## Quick Start

```bash
curl -X POST https://api.acedata.cloud/fish/tts \
  -H "Authorization: ******ACEDATACLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "model: s2-pro" \
  -d '{"text":"你好，欢迎使用 AceData Cloud。","reference_id":"d7900c21663f485ab63ebdb7e5905036","format":"mp3"}'
```

Synchronous responses return a direct audio URL:

```json
{"audio_url":"https://platform.r2.fish.audio/task/8a72ff9840234006a9f74cb2fa04f978.mp3"}
```

## Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /fish/tts` | Text-to-speech generation |
| `GET /fish/model` | Browse/search public Fish reference voices |
| `POST /fish/tasks` | Poll async TTS jobs when `async: true` |

## Workflows

### 1. Find a reference voice

```bash
curl "https://api.acedata.cloud/fish/model?page_size=10&page_number=1&title=Marcus" \
  -H "Authorization: ******ACEDATACLOUD_API_TOKEN"
```

The response includes `items[]` with public voice metadata such as `_id`, `title`,
`languages`, `tags`, `visibility`, and `state`. Use an item `_id` as
`reference_id` in TTS requests.

### 2. Text-to-Speech

```json
POST /fish/tts
Headers:
  model: s2-pro

{
  "text": "Your narration text.",
  "reference_id": "d7900c21663f485ab63ebdb7e5905036",
  "format": "mp3"
}
```

### 3. Async TTS

```json
POST /fish/tts
Headers:
  model: s1

{
  "text": "Longer narration for background processing.",
  "async": true,
  "callback_url": "https://api.acedata.cloud/health"
}
```

> **Async:** See [async task polling](../_shared/async-tasks.md). Poll via `POST /fish/tasks` with `{"id":"..."}`.

## Parameters — `/fish/tts`

### Header

| Parameter | Values | Description |
|-----------|--------|-------------|
| `model` | `"s1"`, `"s2-pro"` | Fish TTS engine selection |

### JSON body

| Parameter | Type / Values | Description |
|-----------|---------------|-------------|
| `text` | string | Text to synthesize (required) |
| `reference_id` | string | Public/reference voice ID from `GET /fish/model` |
| `format` | `"mp3"`, `"wav"`, `"pcm"`, `"opus"` | Output format |
| `sample_rate` | integer | Optional output sample rate |
| `mp3_bitrate` | `64`, `128`, `192` | MP3 bitrate |
| `opus_bitrate` | integer | Opus bitrate |
| `latency` | `"normal"`, `"balanced"` | TTS latency mode |
| `chunk_length` / `min_chunk_length` | integer | Chunking controls |
| `temperature`, `top_p`, `repetition_penalty` | number | Sampling controls |
| `max_new_tokens` | integer | Maximum generated tokens |
| `normalize` | boolean | Normalize generated audio |
| `prosody` | object | Prosody tuning |
| `references` | array | Additional reference objects |
| `callback_url` | string | Async callback URL |
| `async` | boolean | Run asynchronously and poll `/fish/tasks` |

## Gotchas

- The documented TTS endpoint is `POST /fish/tts` — not `/fish/audios`.
- Choose the Fish engine with the **`model` request header**, not a JSON `model` field.
- Use `reference_id` from `GET /fish/model` — not `voice_id`.
- Synchronous requests return `audio_url` directly; async jobs should be polled via `/fish/tasks`.
- The current OpenAPI spec documents voice browsing via `GET /fish/model`; it does **not** document a voice-cloning write endpoint.
