# AgentCall API Reference — Skill Quick Reference

Complete event and command reference for agents using the AgentCall skill.

## Authentication

API keys are prefixed `ak_ac_` and passed as `Authorization: Bearer ak_ac_xxx`.

To get an API key:
```bash
# 1. Register
curl -X POST https://api.agentcall.dev/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "your-password"}'
# Response: {"id": "usr-xxx", "email": "you@example.com"}

# 2. Login (get JWT)
curl -X POST https://api.agentcall.dev/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "your-password"}'
# Response: {"token": "eyJ..."}

# 3. Create API key (using JWT)
curl -X POST https://api.agentcall.dev/v1/auth/api-keys \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent"}'
# Response: {"key": "ak_ac_xxx...", "id": "key-xxx", "key_prefix": "ak_ac_xxxx", "name": "my-agent"}
# Save the key — it is shown only once.

# Check credit balance
curl https://api.agentcall.dev/v1/auth/credits \
  -H "Authorization: Bearer eyJ..."
# Response: {"credits": 21600000000}
```

Set `AGENTCALL_API_KEY=ak_ac_xxx...` in your environment.

---

## REST Endpoints

### POST /v1/calls — Create a Call

```json
{
  "meet_url": "https://meet.google.com/abc-def-ghi",
  "bot_name": "June",
  "mode": "audio",
  "voice_strategy": "collaborative",
  "transcription": true,
  "collaborative": {
    "trigger_words": ["june", "juno", "hey june"],
    "barge_in_prevention": true,
    "interruption_use_full_text": true,
    "context": "You are June. You help with financial data and code analysis.",
    "voice": "voice.heart"
  },
  "webhook_url": "https://my-server.com/webhooks",
  "event_filter": ["transcript.final", "participant.joined"],
  "alone_timeout": 120000,
  "silence_timeout": 300000,
  "max_duration": 3600000,
  "transcript_retention_hours": 24,
  "disclosure": {
    "enabled": true,
    "message": "This meeting is being transcribed by June.",
    "delay_seconds": 60
  },
  "webpage_url": "https://your-site.com/bot",
  "screenshare_url": "https://your-site.com/screenshare"
}
```

**Response (201):**
```json
{
  "call_id": "call-550e8400-e29b-41d4-a716-446655440000",
  "status": "bot_joining",
  "ws_url": "wss://api.agentcall.dev/v1/calls/call-550e.../ws",
  "tunnel_url": "https://x8f2k.conn.agentcall.dev/k/a7b2c.../ui",
  "tunnel_id": "tun-a7b2c...",
  "tunnel_access_key": "tak_...",
  "call_token": "ct_...",
  "created_at": "2026-03-25T10:00:00.000Z"
}
```
- `tunnel_id` + `tunnel_access_key` — for tunnel client auth (webpage modes only, NOT the API key)
- `call_token` — call-scoped token for UI page WebSocket auth (`/v1/calls/{id}/ws/ui?call_token=ct_xxx`)

### GET /v1/calls — List Active Calls

```json
// Response (200):
[
  {
    "call_id": "call-550e8400-e29b-41d4-a716-446655440000",
    "status": "bot_ready",
    "meet_url": "https://meet.google.com/abc-def-ghi",
    "bot_name": "June",
    "mode": "audio",
    "voice_strategy": "collaborative",
    "ws_url": "wss://api.agentcall.dev/v1/calls/call-550e.../ws",
    "created_at": "2026-03-25T10:00:00.000Z"
  }
]
```

### GET /v1/calls/:id — Get Call Details

```json
// Response (200):
{
  "call_id": "call-550e8400...",
  "status": "bot_ready",
  "meet_url": "https://meet.google.com/abc-def-ghi",
  "bot_name": "June",
  "mode": "audio",
  "voice_strategy": "collaborative",
  "bot_id": "bot-abc123",
  "ws_url": "wss://...",
  "tunnel_url": "",
  "created_at": "2026-03-25T10:00:00.000Z",
  "ended_at": null,
  "cost": null
}
```

### DELETE /v1/calls/:id — End Call

Bot leaves meeting. Cost calculated using plan-based rates and credits deducted.

```json
// Response (200):
{"status": "ended"}

// If already ended (409):
{"error": "call already ended"}
```

### GET /v1/calls/:id/transcript — Get Transcript

Query param: `format=json` (default) or `format=text`.
Available during and after the call for `transcript_retention_hours`.

```json
// Response (200, format=json):
{
  "bot_id": "bot-abc123",
  "entries": [
    {"speaker": {"id": "p-1", "name": "Alice"}, "text": "Let's start.", "timestamp": "2026-03-25T10:01:00.000Z"},
    {"speaker": {"id": "p-2", "name": "Bob"}, "text": "Good morning.", "timestamp": "2026-03-25T10:01:05.000Z"}
  ],
  "duration_minutes": 45,
  "entry_count": 247
}
```

### POST /v1/tts/generate — Standalone TTS

```json
// Request:
{"text": "Hello world", "voice": "af_heart", "speed": 1.0, "format": "pcm_16khz"}

// Response (200, streaming JSON lines):
{"type": "audio.chunk", "data": "base64-pcm-data...", "chunk_index": 0, "is_last": false}
{"type": "audio.chunk", "data": "base64-pcm-data...", "chunk_index": 1, "is_last": true}
```

### GET /v1/tts/voices — List TTS Voices

```json
// Response (200):
{"voices": [
  {"id": "af_heart", "name": "Heart", "language": "en-us", "gender": "female"},
  {"id": "af_bella", "name": "Bella", "language": "en-us", "gender": "female"},
  {"id": "am_adam", "name": "Adam", "language": "en-us", "gender": "male"},
  {"id": "bf_emma", "name": "Emma", "language": "en-gb", "gender": "female"}
]}
```

---

## WebSocket Connection

```
wss://api.agentcall.dev/v1/calls/{call_id}/ws?api_key=ak_ac_xxx
```

On connect, receives `call.state` snapshot with current status.

---

## Events Reference (Agent Receives)

### Lifecycle Events

| Event | When | Fields |
|-------|------|--------|
| `call.created` | Call registered | `call_id` |
| `call.tunnel_ready` | Tunnel client connected (webpage modes) | `call_id` |
| `call.bot_joining` | Bot entering meeting | `call_id` |
| `call.bot_joining_meeting` | Bot actively joining (sub-steps) | `call_id`, `detail`: `starting`/`joining`/`initializing` |
| `call.bot_waiting_room` | Bot in waiting room | `call_id` |
| `call.bot_ready` | Bot active in meeting | `call_id` |
| `call.ended` | Call finished | `call_id`, `reason`, `duration_minutes`, `cost`, `transcript_url`, `participants_summary` |
| `call.state` | State snapshot (on WS connect/reconnect) | `call_id`, `status`, `mode`, `bot_name`, `voice_strategy`, `created_at` |
| `call.transcript_ready` | Transcript available for download | `call_id`, `entries`, `transcript_url`, `expires_at` |
| `call.credits_low` | Credits approaching zero | `call_id` |
| `call.degraded` | Internal connection lost | `reason`: `voice_disconnected` |
| `call.recovered` | Internal connection restored | `reason`: `voice_reconnected` |

### Transcription Events

| Event | Strategies | Fields |
|-------|-----------|--------|
| `transcript.final` | all | `text`, `speaker.name`, `speaker.id`, `timestamp` |
| `transcript.partial` | direct | `text`, `speaker.name`, `timestamp` |

### Meeting Events

| Event | Fields |
|-------|--------|
| `participant.joined` | `participant.id`, `participant.name`, `participants[]` |
| `participant.left` | `participant.id`, `participant.name`, `participants[]` |
| `active_speaker` | `speaker.id`, `speaker.name` (`null` when nobody speaking) |
| `chat.message` | `sender`, `message`, `message_id`, `timestamp` |

### Voice Events (collaborative only)

| Event | Fields |
|-------|--------|
| `voice.state` | `state`: one of 7 values (see below) |
| `voice.text` | `text`: sentence the bot is speaking |

**voice.state values:**
- `listening` — idle, waiting to be addressed
- `actively_listening` — detected name, processing incoming speech
- `thinking` — preparing a response
- `waiting_to_speak` — response ready, waiting for silence
- `speaking` — outputting audio
- `interrupted` — stopped mid-speech, evaluating
- `contextually_aware` — follow-up window (20s after speaking)

### TTS Events

| Event | Fields | When |
|-------|--------|------|
| `tts.started` | `destination` | TTS generation began |
| `tts.done` | `destination` | Audio finished playing |
| `tts.error` | `reason` | `tts_unavailable` or `tts_interrupted` |
| `tts.webpage_audio` | `data` (base64 PCM 24kHz), `sentence_index`, `sentence_text`, `duration_ms` | Audio chunk for webpage to play (webpage modes only). `sentence_index`, `sentence_text`, and `duration_ms` are optional fields, present when sent via `tts.speak`. |
| `tts.interrupted` | `sentence_index`, `elapsed_ms`, `reason` | Sent by webpage when interruption detected |
| `tts.audio_clear` | (none) | Stop all audio playback immediately (interruption in webpage modes) |

**`tts.webpage_audio`** — In webpage modes, audio from GetSun (collaborative voice intelligence)/AgentCall TTS arrives as base64 PCM chunks. Your webpage must decode and play them. Use `AgentCallAudio` for automatic queuing.

**`tts.audio_clear`** — When the bot is interrupted mid-speech, this event tells the webpage to flush its audio queue and stop playback immediately. Without handling this, the bot talks over the person who interrupted it.

See [Webpage Audio Guide](guides/webpage-audio.md) for details, examples, and the `AgentCallAudio` player.

### Media Events

| Event | Fields |
|-------|--------|
| `audio.chunk` | `data` (base64 PCM 16kHz), mode 1 + `audio_streaming` only |
| `screenshot.result` | `data` (base64 JPEG), `width`, `height`, `request_id` |
| `capture.started` | `interval_ms` |
| `capture.frame` | `data` (base64 JPEG), `frame_number` |
| `capture.stopped` | `total_frames` |
| `screenshare.started` | `url` |
| `screenshare.stopped` | |
| `screenshare.error` | `message` |

### System Events

| Event | Fields |
|-------|--------|
| `command.ack` | `command`, `request_id` |
| `command.error` | `message`, `command` |
| `events.replay` | `count`, `events[]` | Response to events.replay command with buffered events |

---

## Commands Reference (Agent Sends)

### Voice Intelligence (collaborative only)

| Command | Fields | Description |
|---------|--------|-------------|
| `inject.natural` | `text`, `priority` (`normal`/`high`) | GetSun (collaborative voice intelligence) rephrases and speaks naturally |
| `inject.verbatim` | `text`, `priority` | GetSun (collaborative voice intelligence) speaks exact text |
| `trigger.speak` | `text`, `speaker` | Force response (always responds) |
| `voice.contribute` | (none) | GetSun (collaborative voice intelligence) contributes based on recent transcript |
| `voice.context_update` | `text` (max 4000 chars) | Replace GetSun (collaborative voice intelligence)'s context scratchpad |

**Context vs Conversation:**
- **Context** = your swappable knowledge layer (replaced each time)
- **Conversation** = everything said in the session (automatic, never cleared)
- GetSun (collaborative voice intelligence) remembers the conversation even after you swap context

### TTS (direct mode)

| Command | Fields | Description |
|---------|--------|-------------|
| `tts.generate` | `text`, `voice`, `speed`, `destination` | Unified TTS — routes audio based on destination |
| `tts.speak` | `text`, `voice`, `speed` | Shortcut for `tts.generate` with `destination: "meeting"` |

**Destinations:**
- `"meeting"` — resample 24→16kHz, rechunk 20ms, inject into call (bot speaks in meeting)
- `"agent"` (default) — return raw 24kHz PCM chunks via `tts.audio` events
- `"webpage"` — send raw 24kHz to tunnel for browser playback

**Best practice:** Send text sentence by sentence for lowest latency (<1s to first audio):
```json
{"type": "tts.generate", "text": "First sentence.", "voice": "af_heart", "destination": "meeting"}
{"type": "tts.generate", "text": "Second sentence.", "voice": "af_heart", "destination": "meeting"}
```

**TTS Events received:**
- `tts.started` — generation began (includes `destination`)
- `tts.audio` — audio chunk (only for `destination: "agent"`, includes `data`, `chunk_index`, `is_last`, `duration_ms`)
- `tts.webpage_audio` — audio sent to webpage (only for `destination: "webpage"`)
- `tts.done` — generation complete (includes `destination`)
- `tts.error` — failure (includes `reason`)

**Available voices:** 54 voices across 9 languages. Default: `af_heart`.
Use `GET /v1/tts/voices` for the full list.

### Raw Audio (direct mode)

| Command | Fields | Description |
|---------|--------|-------------|
| `audio.inject` | `data` (base64 PCM 16kHz 16-bit mono) | Inject raw audio into meeting |
| `audio.clear` | (none) | Stop current audio playback |

### Meeting Actions (all modes)

| Command | Fields | Description |
|---------|--------|-------------|
| `meeting.send_chat` | `message` | Send chat message |
| `meeting.raise_hand` | (none) | Raise bot's hand |
| `meeting.leave` | (none) | Leave meeting gracefully |

### Screenshots & Capture (all modes)

| Command | Fields | Description |
|---------|--------|-------------|
| `screenshot.take` | `request_id` | Take single screenshot |
| `capture.start` | `interval_ms` (min 500, multiple of 250) | Start periodic capture |
| `capture.stop` | (none) | Stop periodic capture |

### Screenshare (webpage-av-screenshare only)

| Command | Fields | Description |
|---------|--------|-------------|
| `screenshare.start` | `url` | Start screensharing a URL |
| `screenshare.stop` | (none) | Stop screensharing |

### System Commands

| Command | Description |
|---------|-------------|
| `events.replay` | Request replay of missed events (crash recovery). Returns last 200 events or 5 minutes. |

---

## Call Lifecycle

```
call.created
    │
    ▼
call.tunnel_ready      (webpage modes only — tunnel client connected)
    │
    ▼
call.bot_joining       (FirstCall (meeting infrastructure) bot entering meeting)
    │
    ▼
call.bot_joining_meeting (detail: starting → joining → initializing)
    │
    ▼
call.bot_waiting_room  (if meeting has waiting room)
    │
    ▼
call.bot_ready         (bot is in the meeting, events flowing)
    │
    ▼
call.ended             (reason + duration + cost + transcript_url)
    │
    ▼
call.transcript_ready  (if transcription was enabled)
```

## End Reasons

| Reason | Description |
|--------|-------------|
| `left` | Agent called DELETE or meeting.leave |
| `ended` | Meeting ended on its own |
| `rejected` | Host rejected the bot |
| `blocked` | Bot was kicked |
| `error` | Internal error |
| `max_duration` | Hit the max_duration limit |
| `timeout_silence` | No audio for silence_timeout |
| `timeout_alone` | Bot alone for alone_timeout |

---

## Mode & Strategy Restrictions

Sending a command that doesn't match the current mode/strategy is silently ignored or returns `command.error`:

| Command | Requires |
|---------|----------|
| `inject.verbatim`, `inject.natural`, `trigger.speak`, `voice.contribute`, `voice.context_update` | collaborative strategy only |
| `tts.speak`, `tts.generate` | direct strategy (with AgentCall TTS) |
| `audio.inject` | direct strategy + agent audio |
| `screenshare.start`, `screenshare.stop` | webpage-av-screenshare mode |
| `audio.chunk` events | audio mode + `audio_streaming: true` |
| `transcript.partial` events | direct strategy |

---

## Error Codes

| HTTP | Meaning |
|------|---------|
| 400 | Bad request (validation error) |
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |
| 404 | Call not found |
| 429 | Rate limit or concurrent call limit |
| 501 | Feature not yet implemented |
| 503 | Service unavailable (TTS down) |

---

## Rate Limits

| Resource | Limit |
|----------|-------|
| API requests | 100/second per API key |
| WebSocket commands | 100/second per connection |
| Register | 5/IP/hour |
| Login | 10/IP/minute |

## Billing

| Component | Free | Pro | Enterprise |
|-----------|------|-----|------------|
| Base (meeting bot) | $0.35/hr | $0.30/hr | $0.25/hr |
| Transcription | $0.12/hr | $0.10/hr | $0.08/hr |
| Voice intelligence (GetSun (collaborative voice intelligence)) | $1.00/hr | $0.80/hr | $0.50/hr |
| TTS generation (AgentCall TTS) | $8.00/hr | $6.00/hr | $5.00/hr |

Base plan: 6 hours, 1 concurrent call, all features.

---

## Guides

- [Collaborative Mode Guide](guides/collaborative-mode.md) — context system, inject patterns, background tasks, full examples
- [Webpage Audio Guide](guides/webpage-audio.md) — audio queue, interruption handling, AgentCallAudio player, custom audio effects
- [Interruption Handling Guide](guides/interruption-handling.md) — VAD, sentence tracking, resume patterns
- [UI Templates Guide](guides/ui-templates.md) — all templates, voice states, mic setup, building custom pages
- [Crash Recovery Guide](guides/crash-recovery.md) — event replay, deduplication, full recovery example
