---
name: text-to-sfx
description: Generate a sound effect from a text description using Sonilo — a UI chime, a whoosh, an impact, ambience, a stylized cue — when there is no video to match. Use when the user describes the sound they want in words and gives a duration. For SFX matched to footage, use the video-to-sfx skill; for music, use text-to-music.
license: MIT
compatibility: "Requires Sonilo through either transport — the MCP server connected, or the `sonilo` CLI installed and signed in — plus credentials: a `sonilo login` sign-in, the hosted OAuth plugin, or SONILO_API_KEY. See the setup-api-key skill."
allowed-tools: Bash, Read, Write, mcp__sonilo__*
---

# Sonilo Text-to-SFX

Generate a single sound effect from a text description — no video involved. The
prompt IS the input, so describe the action and materials directly. Generation
runs as an async task on the backend; the tool polls internally and hands back
the saved file.

> **Setup:** See the [setup-api-key](../setup-api-key) skill.

> ⚠️ **Cost:** this tool makes an API call that may incur charges. Only call it when explicitly requested.

> **Matching sound to footage instead?** Use [video-to-sfx](../video-to-sfx) — it reads the cut and can pin sounds to specific moments, which a text prompt cannot do.

## Transport: MCP or CLI

Pick one at the start of the session and stay on it. Do not mix the two inside
a single job, and do not announce the choice.

1. **Sonilo MCP tools visible in this session** (`text_to_sfx` and friends) — use them. This is the preferred path: it needs no shell, and it is the only one that survives a very long generation. If a call fails to authenticate — rather than failing on its inputs — this transport is not usable in this session: go to 2 instead of retrying it.
2. **No usable Sonilo MCP tools, but `sonilo account` exits 0** — use the CLI commands below. Same API, same account, same credential file. Probe with `sonilo account`, not `sonilo whoami`: whoami exits 0 even when signed out, so it cannot tell the two states apart.
3. **Neither** — stop and run the [setup-api-key](../setup-api-key) skill. Do not call `api.sonilo.com` with curl to work around it; both transports handle uploads, polling and retries that a bare request does not.

## Quick Start

### MCP tool call (recommended)

```
text_to_sfx(
    prompt="Thunder rumbling in the distance with light rain",
    duration=6
)
```

### Python (`pip install sonilo`)

```python
from sonilo import Sonilo

client = Sonilo()  # reads SONILO_API_KEY

sfx = client.text_to_sfx.generate(prompt="Thunder rumbling in the distance with light rain", duration=6)
sfx.save("thunder.m4a")
```

### JavaScript / TypeScript (`npm install sonilo`)

```ts
import { SoniloClient } from "sonilo";

const client = new SoniloClient(); // reads SONILO_API_KEY

const sfx = await client.textToSfx.generate({
  prompt: "Thunder rumbling in the distance with light rain",
  duration: 6,
});
```

### CLI (`npm install -g sonilo-cli` or `pip install sonilo-cli`)

```bash
sonilo text-to-sfx --prompt "Thunder rumbling in the distance with light rain" --duration 6
```

Always async under the hood — the CLI submits and polls for you. `--format` accepts `wav|mp3|aac|flac`.

### cURL (raw REST API, no MCP host)

```bash
curl -X POST "https://api.sonilo.com/v1/text-to-sfx" \
  -H "Authorization: Bearer $SONILO_API_KEY" \
  --data-urlencode "prompt=Thunder rumbling in the distance with light rain" \
  --data-urlencode "duration=6"
# -> {"task_id": "..."}  poll GET /v1/tasks/{task_id} until status is succeeded/failed
```

The endpoint returns `{"task_id": ...}` (HTTP 202) and the result is fetched from `GET /v1/tasks/{task_id}` once `status` is terminal. The MCP tool does this polling for you and returns the saved path directly — you only see the `task_id` if the call times out (see [task-recovery](../task-recovery)).

## Tool

| Tool | Description |
|------|-------------|
| `text_to_sfx(prompt, duration, audio_format?, output_directory?)` | Generate one SFX clip from a text description only. |

## Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `prompt` | string | — | Required. 1–2000 chars. |
| `duration` | int | — | Required. 1–180 seconds. There is no source to take the length from, so you must set it. |
| `audio_format` | string | `aac` (`.m4a`) | `wav`, `mp3`, `aac`, or `flac`. |
| `output_directory` | string | `SONILO_MCP_BASE_PATH` | Absolute, or relative to the base path. |

## Prompting

The prompt is the only input — there is no footage to map. Describe the action
and the materials directly, and combine elements: "Heavy rain on a tin roof"
beats "Rain"; "Cinematic braam, horror" or "8-bit retro jump sound" for
stylized cues. The same materials vocabulary and sound-bundle thinking as the
video path applies: [references/sfx-prompting.md](../references/sfx-prompting.md).

Generate once and iterate on the prompt, not on rerolls — failed runs
auto-refund, but your own retry is a new charge.

## Workflow Tips

- **This is for a single clip with no video context** — a UI chime, a whoosh, a foley element you'll layer yourself. If the user has footage, use [video-to-sfx](../video-to-sfx) instead.
- **Duration is required here.** Don't guess it — ask if the user hasn't said.
- **Don't confuse this with music.** For a background score or soundtrack, use [text-to-music](../text-to-music) or [video-to-music](../video-to-music).

## Recovering a Timed-Out Call

Async on the backend already; a long generation can still exceed `TIME_OUT_SECONDS`. If it does, the error carries a `task_id` — the job keeps running (and is already charged). Call `get_sfx_task(task_id)` — `get_generation_task(task_id)` on the hosted server — later to retrieve the result; see [task-recovery](../task-recovery).

## Output Files

Saved in the requested `audio_format` (`.wav`/`.mp3`/`.flac`, or `.m4a` for the `aac` default), named from the prompt (slugified) or `sfx-<first 8 chars of the task id>`.

## Error Handling

Common errors: `401` invalid key, `402` insufficient balance / trial exhausted, `422` invalid parameters (e.g. duration out of range), `429` rate limit. See the [account](../account) skill.
