---
name: join-meeting
description: >
  AgentCall (agentcall.dev) — Join a video meeting (Google Meet, Teams, Zoom)
  as an AI bot with voice and visual presence. Supports audio-only mode with
  voice intelligence (barge-in, interruptions), text-to-speech mode, and
  webpage modes for custom UI. Use when asked to join a call, attend a meeting,
  or participate in a video conference.
argument-hint: <meet-url> [--mode audio|webpage-av] [--voice-strategy collaborative|direct] [--port PORT]
license: MIT
---

# join-meeting

**IMPORTANT: Read this entire document before joining a meeting.** This file
contains the CALL_LOOP algorithm (mandatory), active participation rules,
safety requirements (leave/cleanup), and mode-specific guidance. Skipping
sections will result in broken meeting experiences — the user will be left
talking to silence.

**IMPORTANT: Read the whole document on every session, not just the parts you
remember.** This skill is updated frequently — new commands, new events, new
recommended patterns (like the event-driven `tail -f` + Monitor flow in
"How to read events") are added often. Do NOT rely on what you remember from
previous sessions. Re-read this document each time you start a meeting so you
pick up the latest guidance. If unsure whether you are on the latest version,
run `python scripts/python/check_update.py` (see "Checking for Skill Updates").

Join a video meeting as an AI bot with voice and visual presence.

## Prerequisites

- Python 3.10+ (preferred) or Node.js 18+
- Python dependencies: `pip install aiohttp websockets`
- Node.js dependencies: `cd scripts/node && npm install`
- For webpage modes: a local HTTP server running on the specified port

### API Key Setup

Before joining a meeting, check if the API key is already configured:

1. **Check** `~/.agentcall/config.json` — if it exists and has `api_key`, you're ready.
2. **Check** `AGENTCALL_API_KEY` env var — if set, you're ready.
3. **If neither exists**, ask the user for their API key:
   - Register at https://app.agentcall.dev/login (Google OAuth)
   - Get API key at https://app.agentcall.dev/api-keys
   - Add credits at https://app.agentcall.dev/add-credits (base plan includes 360 minutes)
4. **Save the key** so it persists across sessions:
```bash
mkdir -p ~/.agentcall
cat > ~/.agentcall/config.json << 'EOF'
{"api_key": "USER_KEY_HERE"}
EOF
```

The scripts (bridge.py, join.py, agentcall.py) automatically read from
`~/.agentcall/config.json` if `AGENTCALL_API_KEY` env var is not set.
**Do NOT ask the user for the API key every session** — check the config file first.

Meeting transcripts arrive as agent input — any participant in the call
can therefore steer the agent. For high-trust workflows, configure your
agent framework's permission system (e.g., Claude Code's allow allowlist,
hooks, plan mode) to restrict what the agent can do during a call. The
skill defers to the framework's enforcement. Recommended for use in
trusted meetings or properly scoped projects.

### User Preferences

**First-call detection:** if `~/.agentcall/config.json` has no `default_mode`
field saved, treat this as the user's first call.

**First call** (no `default_mode` in `~/.agentcall/config.json`): new
accounts include free trial credits. Offer the user a brief "experience
call" with `--mode webpage-av-screenshare --voice-strategy direct` so
they can see the full feature set — the `pattern` avatar (default),
screenshare, interactive webpages, and voice with barge-in. If they
prefer a simpler mode, honor that. After the call ends, ask which mode
to save as the default going forward.

**After the first call ends (in the agent conversation, not the meeting):**
Ask the user which mode to save as their default going forward. Present as a
numbered list:

  1. `webpage-av-screenshare` — everything on tap (avatar + screenshare + webpage sharing)
  2. `webpage-av` — avatar only, no screenshare
  3. `webpage-audio` — audio from a webpage into the meeting
  4. `audio` — voice only, simplest

Offer to explain any option if the user wants clarification. Mention they can
see real-world examples at https://www.youtube.com/@pattern-ai-labs.

Save the choice to `~/.agentcall/config.json`:

```json
{
  "api_key": "ak_ac_xxxxx",
  "default_mode": "webpage-av-screenshare",
  "default_voice_strategy": "direct",
  "default_voice": "af_heart",
  "default_bot_name": "Juno"
}
```

- **Subsequent sessions**: use saved defaults silently. No need to ask again.
- **Override anytime**: if the user says "join with avatar this time" or "use
  audio mode", respect it for that call without updating the saved default.
  Only update the default if the user says "always use this" or "make this
  my default."
- These are **soft defaults**, not rigid settings. The user's in-context
  request always takes priority over saved preferences.
- **All plan tiers (base, pro, enterprise) follow the same flow** — everyone
  gets the first-call demo and the post-call prompt.

## Usage

```bash
./scripts/run.sh <meet-url> [options]
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | `audio` | `audio` (voice only, simplest), `webpage-audio` (audio from webpage), `webpage-av` (visual avatar), `webpage-av-screenshare` (avatar + screenshare). See Modes Explained below. |
| `--voice-strategy` | `direct` | `collaborative`, `direct` |
| `--bot-name` | `Agent` | Display name in the meeting participant list |
| `--port` | `3000` | Local port for webpage modes (your UI server) |
| `--screenshare-port` | `3001` | Local port for screenshare content |
| `--template` | `pattern` | Built-in UI: `pattern` (default, radial sunburst with per-state colors and the work-in-progress task list), `ring` (neon ring), `orb`, `avatar`, `dashboard`, `blank`, `voice-agent` (no local server needed) |
| `--transcription` | on | Real-time `transcript.final` and `transcript.partial` events. Required for most workflows. Disable with `--no-transcription` to save STT billing if you only need lifecycle events. |
| `--trigger-words` | | Comma-separated aliases for collaborative mode: `june,juno,hey june` |
| `--context` | | Initial context for voice intelligence (max 4000 chars) |
| `--webpage-url` | | Public URL for webpage modes (no tunnel needed) |
| `--screenshare-url` | | Public URL for screenshare content (no tunnel needed) |
| `--max-duration` | plan limit | Max call duration in minutes. Cannot exceed your plan's limit. Check https://agentcall.dev for current limits. |
| `--alone-timeout` | 120 | Leave if alone for N seconds. |
| `--silence-timeout` | 300 | Leave if silent for N seconds. |
| `--api-url` | `https://api.agentcall.dev` | Override API URL for development |

## Bot Naming

Choose STT-friendly names — short, distinctive, real-sounding words that
speech-to-text can reliably capture. Avoid generic phrases like "AI Assistant"
or "Hey Bot" — transcription often garbles these.

**Good names:** Juno, June, Nova, Sage, Atlas, Claude, Aria, Echo
**Avoid:** AI Assistant, My Bot, Hey Agent, Assistant Bot

**Always set trigger words** in collaborative mode to cover STT mishearings:
```
--bot-name "Juno" --trigger-words "juno,june,you know,junior"
--bot-name "Claude" --trigger-words "claude,cloud,clod,clawed"
--bot-name "Nova" --trigger-words "nova,no va,over"
```

The display name in the participant list can be longer (e.g., "Juno - AI Assistant")
but the trigger words should be the short phonetic variants that STT might produce.

## Modes Explained

### audio (default)
Voice only. Bot has no video. Best for: AI assistants, note-takers, voice agents.
No local server needed. Simplest setup.

### webpage-audio
Your local webpage provides audio. Bot's video is black. The webpage can play audio
that meeting participants will hear. Best for: audio-only web apps.
Requires: `--port` pointing to your local HTTP server.

If your webpage is publicly hosted, pass `--webpage-url https://your-site.com/bot`
instead of `--port`. No tunnel or local server needed.

### webpage-av
Your webpage IS the bot's video feed — what renders on the page is what meeting
participants see as the bot's camera. Audio from the page is also captured into
the meeting. The page is loaded once and runs continuously. All updates must come
via WebSocket events from your agent — it does not auto-refresh.

Best for: animated avatars, branded visual presence, agent-controlled dynamic UIs.

The webpage can also be a standalone voice-to-voice agent: it receives the meeting's
audio as microphone input, processes it with its own AI backend, and replies through
the browser's speaker — which FirstCall (meeting infrastructure) captures into the meeting. This means any
existing voice agent webpage can join meetings with zero modification.

Keep it simple. The agent controls the page via WebSocket. The page renders what
the agent tells it to. Use `--template orb` or `--template avatar` for built-in options.

For slides or screen-sharing content, use `webpage-av-screenshare` instead.

### webpage-av-screenshare
Same as webpage-av PLUS the ability to screenshare. Bot has two visual presences:
- **Camera feed** — your avatar/brand page (always active, receives meeting audio via mic)
- **Screenshare** — separate content page, **inactive until you send `screenshare.start`**

**Screenshare starts inactive.** The bot joins with only the avatar visible.
Screenshare activates when the agent sends `screenshare.start` with a URL or port.
If you don't need screenshare at all, use `webpage-av` mode instead.

Bot has two visual presences when screenshare is active:
- **Camera feed** — your avatar/brand page (receives meeting audio via mic)
- **Screenshare** — separate content page (slides, charts, docs, demos)

Meeting audio is routed ONLY to the avatar page (not screenshare). Audio from
both pages is captured into the meeting.

Agent controls screenshare dynamically during the call:
- `screenshare.start` with `url` — share a public URL: `{"command": "screenshare.start", "url": "https://slides.google.com/..."}`
- `screenshare.start` with `port` — share a local server via tunnel: `{"command": "screenshare.start", "port": 3001}`
- `screenshare.stop` — stop sharing: `{"command": "screenshare.stop"}`
- `screenshare.swap` — atomically swap to a different page: `{"command": "screenshare.swap", "port": 3002}` or `{"command": "screenshare.swap", "url": "https://..."}`. Use this instead of stop+start when changing what's shared during a call — it serializes the stop and waits for FirstCall to confirm before starting the new share, which avoids races and the "old content keeps showing" bug.

Requires: `--port` AND `--screenshare-port` (local), or `--webpage-url` AND
`--screenshare-url` (public, no tunnel).

**IMPORTANT — screenshare is a live, agent-controlled canvas:**
Once loaded, the screenshare page cannot be clicked, scrolled, or typed into by
anyone — it runs in a headless browser. The agent controls what's on screen by
updating files or API responses on its local server — the page polls for changes
via HTTP (every 2 seconds) through the tunnel and re-renders automatically.

**Design for 1280x720 viewport.** FirstCall's headless browser renders at this
resolution. Use large fonts (40px+ for headings, 24px+ for body text) so content
is readable in the meeting participant's screenshare view.

**Live screenshare pattern** — for slides, dashboards, or any dynamic content:
1. Create an HTML page with a polling loop that fetches `/state.json` every 2s
2. Create a `state.json` file that holds the current state (e.g., `{"slide": 0}`)
3. Serve both from a local HTTP server via `python -m http.server`
4. Start screenshare with `port` — tunnel proxies HTTP to your localhost
5. To update: write new state to `state.json` — the page picks it up within 2s

```
Agent: "Let me show you the Q3 numbers."
  → agent creates /tmp/screenshare/index.html + state.json
  → agent starts: python -m http.server 3001 --directory /tmp/screenshare/
  → agent sends: {"command": "screenshare.start", "port": 3001}

Agent: "Moving to the next slide."
  → agent writes: echo '{"slide": 1}' > /tmp/screenshare/state.json
  → page polls, detects change, renders slide 2

Agent: "Here's the revenue chart."
  → agent writes: echo '{"slide": 2}' > /tmp/screenshare/state.json
  → page renders the chart slide
```

This makes the screenshare a real-time visual companion to the agent's voice,
fully synchronized — the agent narrates while updating files that control what
everyone sees. No WebSocket needed — all updates flow via HTTP through the tunnel.
See [Webpage AV Screenshare Guide](references/guides/webpage-av-screenshare.md) for full HTML snippet and examples.

**Bonus feature — share an interactive webpage with participants.** This mode
also supports `webpage.open`, which exposes a page from your localhost via a
shareable URL. Participants open it in **their own browser** (fully interactive —
clickable, scrollable, can type and submit forms). This is NOT a screenshare
(headless, in-meeting only) — it is a shareable link the agent builds and
sends to participants. Ideal for agent-generated dashboards, reports, forms,
interactive code diffs, and any content you want participants to actually
click. The tunnel closes automatically when the call ends. See "Sharing a
live webpage" under Pattern 5 for commands, events, and the full workflow.

### Which mode should I use?

| Need | Mode | Why |
|------|------|-----|
| Voice only, no video | `audio` | Simplest. No webpage, no tunnel. |
| Audio from a webpage | `webpage-audio` | Webpage plays audio into meeting. |
| Visual avatar/brand | `webpage-av` | Your page = bot's camera feed. |
| Avatar + might screenshare | `webpage-av-screenshare` | Avatar always on. Screenshare on demand. |

**Rule of thumb:** For **first-time users** (no `default_mode` in
`~/.agentcall/config.json`), always use `webpage-av-screenshare` to showcase
the full experience — see User Preferences section for the first-call demo
flow. For **returning users**, use their saved `default_mode`. In general,
start with `audio` if no preference is known. Add `webpage-av` if you need
visual presence. Add `webpage-av-screenshare` only if the agent will share
content (slides, charts, demos) during the call. Screenshare is always
dynamic — activated via `screenshare.start` command, not at call creation.

**Need participants to interact with something (not just see it)?** Use
`webpage-av-screenshare` mode and the `webpage.open` command. The agent serves
a page from its localhost; participants open the shareable URL in their own
browser — clickable, scrollable, fillable. Different from screenshare (which
is a headless view only). Examples: a form to collect meeting feedback, a
dashboard participants can drill into, a code diff viewer. See "Sharing a
live webpage" in Pattern 5 for commands and workflow.

## How the Tunnel Works (Webpage Modes)

For webpage modes, AgentCall creates a secure tunnel from the cloud to your localhost:
1. You run a local HTTP server (or use `--template` which starts one automatically).
2. The bridge script connects a tunnel client to AgentCall's tunnel server via WebSocket.
3. The bot's browser (running in the cloud) loads your page via the tunnel URL.
4. HTTP requests to the tunnel URL are proxied through the tunnel to your localhost.

You do NOT need to expose your machine to the internet. The tunnel handles it.
When using `--template`, the bridge starts a local server and tunnel automatically — no manual setup.
When using `--webpage-url` (public URL), no tunnel is needed — FirstCall loads it directly.

**Port conflicts:** Before starting a local server on a specific port, verify it's available: `lsof -i :PORT`. If another process (e.g., Node.js on port 3000) is already bound, the tunnel will proxy to the wrong server, causing unexpected 404 errors. Use a different port or use `--template` which auto-selects a free port.

### Tunnel Authentication

When creating a call with `ui_port`, the API response includes:
- `tunnel_id` — unique identifier for this tunnel
- `tunnel_access_key` — per-call credential for tunnel authentication
- `tunnel_url` — the public URL where FirstCall loads your page

The tunnel client registers with the server using `tunnel_id` + `tunnel_access_key`.

**IMPORTANT:** The `tunnel_access_key` is NOT your API key (`ak_ac_...`). It is a separate, per-call credential generated specifically for tunnel authentication. Using your API key will fail with an error message explaining the correct credential to use. If using `bridge-visual.py`, this is handled automatically.

## Mic Permissions (Webpage Modes)

In all webpage modes, FirstCall (meeting infrastructure) automatically grants microphone permission to your
page. Your webpage receives the meeting's audio as browser microphone input.

**Important:** Your page MUST start mic recording automatically on load — no button
clicks, no user interaction. FirstCall (meeting infrastructure) loads your page in the rendering environment and cannot
interact with UI elements. Use `navigator.mediaDevices.getUserMedia({ audio: true })`
on page load or in a script that runs immediately.

```javascript
// Auto-start mic on page load (required for voice agent webpages)
window.addEventListener('load', async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  // stream now has meeting audio — process it with your AI
});
```

Meeting audio is routed to the main avatar page only. In screenshare mode,
the screenshare page does NOT receive mic input.

## Voice Strategies Explained

### collaborative (group meetings)
Uses GetSun as a **speech intelligence layer** — it handles real-time voice timing
(trigger words, barge-in, interruptions) so the agent doesn't need sub-second
response times. But the **agent is still the brain**: it provides context, injects
data, triggers responses, and does all the thinking. GetSun is the mouth, not the mind.
The bot:
- Listens for its name (or trigger words) before responding
- Waits for silence before speaking (barge-in prevention)
- Stops immediately if interrupted (uses full text for smart interruption handling)
- Handles follow-up questions for 20 seconds after responding
- Has 4 built-in voices: voice.heart (F), voice.bella (F), voice.echo (M), voice.eric (M)

**Configuration (`collaborative` field in call creation):**
| Param | Default | Description |
|-------|---------|-------------|
| `trigger_words` | `[]` | Alternate names (handles STT mishearing): `["june", "juno"]` |
| `barge_in_prevention` | `true` | Wait for silence before speaking |
| `interruption_use_full_text` | `true` | Use full text during interruptions for smarter responses |
| `context` | `""` | Initial knowledge scratchpad (4000 chars max) |
| `voice` | `voice.heart` | TTS voice: `voice.heart`, `voice.bella`, `voice.echo`, `voice.eric` |

Your agent receives `transcript.final` events only (not partials — GetSun (collaborative voice intelligence) handles those).
Use the **context-first pattern**:
1. Receive transcript.final
2. Fetch/compute data
3. Send `voice.context_update` with the data
4. Send `trigger.speak` with the original question
5. GetSun (collaborative voice intelligence) answers naturally from context

**Announcing background task results:**
1. Complete the task (analysis, lookup, etc.)
2. Send `voice.context_update` with the full results data
3. Send `inject.natural` with a SHORT announcement: "I've got the results" (1 sentence only)
4. GetSun speaks the announcement at the next natural pause
5. User asks follow-up → GetSun answers from context instantly

See [Collaborative Mode Guide](references/guides/collaborative-mode.md) for detailed examples, context patterns, and full working code.

### Collaborative Mode: Working with GetSun

GetSun responds in <1 second — the agent will NEVER beat it to a response.
This means the agent's job is to **prepare GetSun's context in advance** so
GetSun says the right thing when a participant speaks.

**1. Pre-load capabilities on join:**

Immediately after `call.bot_ready`, send a `voice.context_update` that tells
GetSun what the agent can do. This is the most important step — without it,
GetSun will refuse requests the agent could handle.

```
voice.context_update: "You are [bot_name], an AI assistant in this meeting.
You have a backend agent that can: search code, edit files, run commands,
check deployments, browse documentation, analyze data, and more.
When asked to do something:
- If you know the answer from context, respond directly.
- If you need to check or look something up, say 'Let me check on that'
  or 'Sure, give me a moment.' The agent will handle the work and provide
  results for you to speak.
- NEVER say 'I can't do that' or 'I don't have access to that.'
  The agent behind you has the tools — always defer to it."
```

Customize the capabilities list based on what your agent framework can actually
do (code search, web browsing, API calls, file editing, etc.).

**2. GetSun will always speak first:**

When a participant asks something:
```
User: "Juno, what's the deployment status?"
GetSun (instant, from context): "Sure, let me check on that for you."
Agent (sees transcript.final): runs health check → gets result
Agent: sends voice.context_update with full deployment data
Agent: sends inject.natural "I've got the deployment status." (short announcement)
GetSun: speaks the announcement at next pause
User: "What's the status?" → GetSun answers from context instantly
```

The pattern is always: GetSun buys time → Agent does work → Agent updates context + announces.

**3. Handle capability mismatches:**

If GetSun says "I can't do that" (because the context didn't cover this capability):
- Agent sees `voice.text` with GetSun's refusal
- Agent sends `voice.context_update` adding the missing capability
- Agent sends `inject.natural` with a correction: "Actually, I can help with that. Let me take a look."
- This teaches GetSun for the rest of the session — it won't refuse the same thing again

**4. Keep context fresh:**

After completing any task, update GetSun's context with the results:
```
Agent completes deployment check →
voice.context_update: "Latest deployment status: all services healthy,
last deploy 2 hours ago, 3 pods running, 0 errors in last 30 min."
```

Now if a participant asks a follow-up ("Any errors?"), GetSun answers instantly
from context without the agent needing to run another check.

**5. Ongoing conversation awareness:**

The agent should monitor `voice.text` events (what GetSun said) AND
`transcript.final` events (what participants said). This gives the agent
full awareness of the conversation — both sides. Use this to:
- Detect when GetSun deferred ("let me check") → agent must act
- Detect when GetSun answered from context → no action needed
- Detect when participants discuss topics the agent has context on → proactively update context

**6. Predictive context updates:**

The agent can preemptively update GetSun's context with data relevant to the
current discussion — BEFORE anyone asks. This makes GetSun answer instantly
(<1s) instead of deferring ("let me check") and waiting for the agent.

```
Participants discussing deployment...
Agent: (I have deployment data) → context_update with deployment status
User: "Juno, is the deployment healthy?"
GetSun: answers instantly from context — no delay, no "let me check"
```

When to preload context:
- The conversation shifts to a topic the agent has data on
- The agent just completed a task — results may be relevant to ongoing discussion
- The agent recognizes a pattern (e.g., participants keep asking about metrics)
- The agent knows the meeting agenda and can preload relevant data

`context_update` is silent — GetSun absorbs it without speaking. If nobody asks
about the preloaded topic, no harm done. If someone does ask, GetSun answers
instantly. The 4000-char limit means the agent must prioritize — preload data
most relevant to the current discussion, not everything it knows.

### direct (full control)
No voice intelligence. Your agent controls everything:
- `transcript.final` — completed utterances
- `transcript.partial` — in-progress transcription (someone is still talking)
- `active_speaker` — who's talking

Your agent decides when to speak using:
- `tts.speak` — AgentCall TTS (54 voices, 9 languages, <1s latency)
- `audio.inject` — raw PCM 16kHz 16-bit mono (your own audio pipeline)

You are responsible for turn-taking and timing.

**Available TTS voices (direct mode):**

| Voice ID | Name | Language | Gender |
|----------|------|----------|--------|
| af_heart | Heart | en-us | Female |
| af_bella | Bella | en-us | Female |
| af_sarah | Sarah | en-us | Female |
| af_nicole | Nicole | en-us | Female |
| am_adam | Adam | en-us | Male |
| am_michael | Michael | en-us | Male |
| bf_emma | Emma | en-gb | Female |
| bf_isabella | Isabella | en-gb | Female |
| bm_george | George | en-gb | Male |
| bm_lewis | Lewis | en-gb | Male |

Voice ID convention: `{language}{gender}_{name}` — `af_` = American Female,
`am_` = American Male, `bf_` = British Female, `bm_` = British Male.
For the full list of all available voices, query `GET /v1/tts/voices`.

**Collaborative mode voices** (GetSun, different naming from direct): voice.heart (F), voice.bella (F), voice.echo (M), voice.eric (M). **Direct mode voices** (Kokoro TTS) use `af_heart`, `am_adam` etc. — these are different systems, names are NOT interchangeable.

**Barge-in prevention:** in direct mode, the bridge automatically holds
`tts.speak` until the human finishes speaking — you don't need to gate
it yourself. If the human keeps speaking for more than 10 seconds while
the bot has queued speech, the bridge politely raises the bot's hand
(and in webpage modes, flips the avatar to "waiting_to_speak") so
participants see the bot has something to say. In collaborative mode,
GetSun handles all of this.

**For 1:1 conversations** (customer support, interviews, tutoring):
Use direct mode and respond to every `transcript.final`. The bridge handles
barge-in prevention automatically — just send `tts.speak` and the bridge will
wait for silence before delivering the audio. Tips:
- First audio reaches the meeting in <1s automatically — send your response in one `tts.speak`
- Transcripts are ALWAYS from human participants — never the bot itself
- `transcript.final` is NOT dropped during bot speech — if a user speaks while the bot
  is talking, you will receive their message

**Interruption handling (webpage modes 2-4, direct mode):**
In webpage modes, interruption is automatic but debounced — a single
`transcript.partial` doesn't cut the bot off (too easily triggered by mic
noise, brief fillers, or acknowledgments like "mhm"). The webpage pauses
the bot's audio on the first partial, flips the avatar to "interrupted"
(red) for immediate visual feedback, and waits up to 2 seconds for
sustained speech (about 2 spoken words). If sustained, the audio is cleared
and `tts.interrupted` is delivered to the agent with played and not_played
sentence lists:
```json
{
  "event": "tts.interrupted",
  "reason": "user_speaking",
  "played":     ["Hello there.", "How are you?"],
  "not_played": ["I was about to ask...", "...something important."]
}
```
- `played` — sentences the participant heard in full
- `not_played` — sentences cut mid-way OR queued but never started

If the wait window expires without sustained speech, the bot resumes
playing from where it paused and the avatar flips back to "speaking" —
false alarm, no `tts.interrupted` fires.

On confirmed interruption the avatar stays "interrupted" until the next
state-changing event takes over (typically auto-thinking when
`user.message` arrives, or the bot's next `tts.speak`).

The agent decides what to do based on the lists:
- Skip already-played material; rephrase or continue with the not_played content
- Generate a new response incorporating what the user said
- Acknowledge the interruption: "Sorry, go ahead"

(Collaborative mode interruption — GetSun-driven — is unchanged: `tts.audio_clear` from the backend bypasses the debounce.)

**Interruption in audio mode (mode 1):**
No automatic interruption — the bot's audio is injected directly into FirstCall.
The agent still receives `transcript.final` during bot speech and can send `audio.clear`
to stop playback. See [Interruption Handling Guide](references/guides/interruption-handling.md).

## Events (stdout)

Each line is a JSON object.

**Event key convention:** Lifecycle events use the `"event"` field. Transcription, meeting, and media events use the `"type"` field. Always check both: `event.get("event") or event.get("type")` (Python) or `event.event || event.type` (JS). **Tip:** `bridge.py` normalizes all events to use the `"event"` field — if using `join.py` directly, always check both fields.

**Startup time:** After creating a call, the bot takes 30-90 seconds to join the meeting (varies by platform — Google Meet is fastest, Teams/Zoom can take longer). During this time you'll see lifecycle events: `call.created` → `call.bot_joining` → `call.bot_joining_meeting` → `call.bot_ready`. The agent MUST wait patiently and NOT timeout or assume failure during this window. If using `bridge.py`, it handles this automatically — the agent simply waits for the first `user.message` or `greeting.prompt` event.

### Lifecycle
```json
{"event": "call.created", "call_id": "call-xxx", "ws_url": "wss://...", "status": "bot_joining"}
{"event": "call.tunnel_ready", "call_id": "call-xxx"}
{"event": "call.bot_joining", "call_id": "call-xxx"}
{"event": "call.bot_joining_meeting", "call_id": "call-xxx", "detail": "starting"}
{"event": "call.bot_joining_meeting", "call_id": "call-xxx", "detail": "joining"}
{"event": "call.bot_joining_meeting", "call_id": "call-xxx", "detail": "initializing"}
{"event": "call.bot_waiting_room", "call_id": "call-xxx"}
{"event": "call.bot_ready", "call_id": "call-xxx"}
{"event": "call.ended", "call_id": "call-xxx", "reason": "meeting_ended", "duration_minutes": 45}
{"event": "call.state", "call_id": "call-xxx", "status": "bot_ready", "mode": "audio", "voice_strategy": "collaborative", "created_at": "..."}
{"event": "call.transcript_ready", "call_id": "call-xxx", "transcript_url": "...", "expires_at": "..."}
{"event": "call.max_duration_warning", "call_id": "call-xxx", "minutes_remaining": 5}
{"event": "call.credits_low", "call_id": "call-xxx", "balance_microcents": 500000, "estimated_minutes_remaining": 12}
{"event": "call.degraded", "reason": "voice_disconnected"}
{"event": "call.recovered", "reason": "voice_reconnected"}
```

`call.bot_joining` means AgentCall has requested the bot — the meeting infrastructure is spinning up. `call.bot_joining_meeting` means the bot is actively entering the meeting (launching browser, navigating to URL, initializing audio). The `detail` field shows the sub-step: `starting` → `joining` → `initializing`. These fire in rapid succession — no action needed, just progress indicators.

`call.max_duration_warning` fires 5 minutes before the call reaches its plan's max duration limit.
**Default action: create a new call for the same meeting URL.** The new bot joins while the
old one is still active. When the old bot leaves (max_duration), the new bot continues seamlessly.
Your session context is preserved — no information is lost. The concurrent limit allows one
extra call during this 5-minute grace window so the rejoin works even on the base plan.
If the user is on the base plan (1hr max), mention that Pro offers 4hr max duration —
upgrade at https://app.agentcall.dev/add-credits ($29/mo subscription or recharge $50+ for 30 days of Pro).

`call.credits_low` fires at call start if the user's credit balance is below $1. Includes
`balance_microcents` (raw balance) and `estimated_minutes_remaining` (calculated from current
call's mode and add-on rates). The agent should inform the user and suggest recharging at
https://app.agentcall.dev/add-credits. **Credits low does NOT terminate the call** — the call
continues and credits can go negative. This is a courtesy warning, not a cutoff.

`call.degraded` means a backend service disconnected (e.g., voice intelligence). The bot is still in the meeting and transcripts still flow. In collaborative mode, voice commands (inject.natural, trigger.speak) may not work until `call.recovered`. In direct mode, tts.speak is unaffected. No action needed — the system auto-recovers.

`call.state` is sent on every WS connect/reconnect — use it to restore agent state after crash recovery.
`call.bot_waiting_room` means the meeting has a lobby — the bot is waiting to be admitted by the host. Do NOT send any commands (tts.speak, send_chat, etc.) during this state — no one will hear or see them and they are not queued.

**IMPORTANT:** Even after `call.bot_ready`, wait for at least one `participant.joined` event before sending any commands. If the bot is admitted but no participants have joined yet, the bot is alone in the meeting — no one will hear what it says. Always wait for a participant before speaking or sending data.

### Transcription
```json
{"type": "transcript.final", "text": "What do you think about Q3?", "speaker": {"id": "p-1", "name": "Alice"}, "timestamp": "2026-03-25T10:05:23.456Z"}
{"type": "transcript.partial", "text": "What do you thi", "speaker": {"id": "p-1", "name": "Alice"}, "timestamp": "2026-03-25T10:05:22.100Z"}
```
Note: `transcript.partial` in direct mode only. Includes `speaker.id`, `speaker.name`, and `timestamp`.

### Meeting Awareness
```json
{"type": "participant.joined", "participant": {"id": "p-1", "name": "Alice"}, "participants": [{"id": "p-1", "name": "Alice"}]}
{"type": "participant.left", "participant": {"id": "p-2", "name": "Bob"}, "participants": [{"id": "p-1", "name": "Alice"}]}
{"type": "active_speaker", "speaker": {"id": "p-1", "name": "Alice"}}
{"type": "chat.message", "sender": "Alice", "message": "Can everyone hear me?", "message_id": "msg-123"}
```

### Voice State (collaborative only)
```json
{"event": "voice.state", "state": "listening"}
{"event": "voice.text", "text": "The revenue was 2.4 million dollars."}
```
7 states (collaborative mode only — GetSun (collaborative voice intelligence)):

| State | Meaning |
|-------|---------|
| `listening` | Default — hearing the conversation, not engaged |
| `actively_listening` | Trigger word detected, capturing the full question |
| `thinking` | Processing a response |
| `waiting_to_speak` | Response ready, waiting for silence (barge-in prevention) |
| `speaking` | Speaking via TTS |
| `interrupted` | Someone talked over the bot, stopped speaking |
| `contextually_aware` | Just responded — actively monitoring conversation for follow-up questions or related discussion. Lasts ~20 seconds after speaking. |

`voice.text` shows each sentence the bot is speaking (for agent awareness).

### TTS Events
```json
{"event": "tts.started", "destination": "meeting"}
{"event": "tts.done", "destination": "meeting"}
{"event": "tts.audio", "data": "base64-pcm-24khz...", "chunk_index": 0, "is_last": false, "duration_ms": 2500}
{"event": "tts.webpage_audio", "data": "base64-pcm-24khz..."}
{"event": "tts.error", "reason": "tts_unavailable"}
{"event": "tts.interrupted", "reason": "user_speaking", "played": ["..."], "not_played": ["..."]}
```
- `tts.started/done` — bracket TTS generation with destination info.
- `tts.interrupted` — bot audio was stopped because a human started sustained speech (webpage modes, direct only). `played` lists sentences the participant heard fully; `not_played` lists sentences cut mid-way or never started. See "Interruption handling" above for the full debounce mechanic.
- `tts.audio` — raw 24kHz PCM chunks returned to agent (when `destination: "agent"`).
- `tts.webpage_audio` — audio sent to webpage via tunnel (when `destination: "webpage"`).

### Media
```json
{"type": "audio.chunk", "data": "base64-pcm-16khz...", "timestamp": "..."}
{"type": "screenshot.result", "data": "base64-jpeg...", "width": 1920, "height": 1080, "request_id": "req-1"}
{"type": "capture.started", "interval_ms": 1000}
{"type": "capture.frame", "data": "base64-jpeg...", "frame_number": 5}
{"type": "capture.stopped", "total_frames": 30}
{"type": "screenshare.started", "url": "https://..."}
{"type": "screenshare.stopped"}
{"type": "screenshare.error", "message": "Failed to load URL"}
```
`audio.chunk` requires `audio_streaming: true` in the call creation request (REST API only — not available as a CLI flag). This streams raw 16kHz PCM meeting audio to the agent. Most workflows don't need this — use `transcript.final` instead. See the [Multilingual Note-Taker](examples/notetaker-multilingual/) example for a use case.

### System
```json
{"type": "command.ack", "command": "meeting.send_chat", "request_id": "req-1"}
{"type": "command.error", "message": "Bot container not connected", "command": "meeting.send_chat"}
```

## Commands (stdin)

Send one JSON object per line.

### Voice Intelligence (collaborative only)
```json
{"type": "inject.natural", "text": "Q3 revenue was $2.4M, up 15%", "priority": "normal"}
{"type": "inject.verbatim", "text": "The meeting will end in 5 minutes.", "priority": "high"}
{"type": "trigger.speak", "text": "Tell me about the financial results", "speaker": "Alice"}
{"type": "voice.contribute"}
{"type": "voice.context_update", "text": "Q3 Revenue: $2.4M, up 15% YoY. Enterprise: $1.6M..."}
```

**trigger.speak** — Conversational. Forces GetSun to respond to the text as if asked.
  If interrupted, content is LOST — GetSun moves on (like a person being cut off).
  Use for: answering direct questions, conversational replies.
**inject.natural** — High reliability. GetSun rephrases your text and speaks it at the
  next natural pause. If interrupted, GetSun remembers and retries until fully spoken.
  **Keep inject text SHORT (1 sentence).** Long inject text that gets interrupted causes
  a retry loop — GetSun keeps coming back to finish, which feels robotic.
  Use for: short announcements only ("I've got the results", "Task complete", "I found the issue").
  Do NOT dump data into inject — put data in `context_update`, announce with inject.
**inject.verbatim** — Same as inject.natural but speaks exact text without rephrasing.
  Same retry behavior — keep it short.
**voice.contribute** — GetSun reads the conversation and contributes something relevant
  from its context at the next natural pause, without being addressed by name. Use when
  the conversation topic matches data in the bot's context.
**voice.context_update** — Replaces GetSun's context scratchpad (4000 chars max).
  This is where ALL data goes. Context is queryable — participants can ask follow-up
  questions and GetSun answers from context instantly. Context is NOT conversation memory.
  GetSun remembers the conversation separately.

**Correct pattern for delivering results:**
```
1. context_update → full data (deployment status, revenue numbers, etc.)
2. inject.natural → short announcement: "I've got the deployment status ready."
3. User asks follow-up → GetSun answers from context instantly
```

**Anti-pattern (DO NOT do this):**
```
inject.natural "The deployment is healthy. All 3 services running. Last deploy 2 hours
ago. No errors in 30 minutes. CPU 45%. Memory 62%..."
→ Long inject gets interrupted → GetSun retries → interrupted again → poor UX
```

### TTS (direct mode)

**Unified command** — `tts.generate` with a `destination` field:
```json
{"type": "tts.generate", "text": "Hello everyone!", "voice": "af_heart", "speed": 1.0, "destination": "meeting"}  (speed 1.0 recommended)
{"type": "tts.generate", "text": "Welcome.", "voice": "bf_emma", "destination": "agent"}
{"type": "tts.generate", "text": "This plays on the webpage.", "destination": "webpage"}
```

**Destinations:**
- `"meeting"` — resample 24→16kHz, rechunk 20ms, inject into call via FirstCall (meeting infrastructure) (bot speaks).
- `"agent"` — return raw 24kHz PCM chunks to you via `tts.audio` events (you decide what to do).
- `"webpage"` — send raw 24kHz to your webpage via tunnel (browser plays it).

**Shortcut:** `tts.speak` auto-detects the correct destination based on mode:
```json
{"type": "tts.speak", "text": "Hello everyone!", "voice": "af_heart", "speed": 1.0}
```
- In **audio mode** (bridge.py): audio goes directly to FirstCall → bot speaks in meeting.
- In **webpage modes** (bridge-visual.py): audio goes to the avatar webpage → browser plays it → FirstCall captures browser audio → meeting hears it.

You do NOT need to specify a destination when using `tts.speak` — it is
inferred from the call mode. Use `tts.generate` with an explicit `destination`
only if you need to override the default routing.

**`tts.speak` returns one `tts.done`** (or `tts.interrupted` if the user
spoke over the bot) per call, regardless of text length. First audio reaches
the meeting in under 1 second. Send your response naturally in one `tts.speak`:

```json
{"command": "tts.speak", "text": "Q3 revenue was 2.4 million. That's up 15 percent year over year. Enterprise was the main driver at 1.6 million."}
```

`tts.done` signals generation complete — audio may continue playing in the
meeting for a few seconds after. `tts.interrupted` can therefore arrive
after `tts.done` (user spoke during the tail of playback).

**Conversational style:** write `tts.speak` text the way you'd say it
aloud. TTS reads unknown chars by Unicode name (`^` → "circumflex",
`€` → "euro", `**` → "asterisk asterisk"). No markdown, emojis, or
symbols. Spell out numbers and money (`"2.4 million"`, not `"$2.4M"`).
URLs/code/errors → `send_chat`.

### Raw Audio (direct mode)
```json
{"type": "audio.inject", "data": "base64-pcm-16khz-16bit-mono..."}
{"type": "audio.clear"}
```

### Meeting Actions (all modes)
```json
{"type": "meeting.send_chat", "message": "Notes shared in the doc."}
{"type": "meeting.raise_hand"}
{"type": "meeting.mic", "action": "on"}
{"type": "meeting.leave"}
{"type": "screenshot.take", "request_id": "req-1"}
{"type": "capture.start", "interval_ms": 1000}
{"type": "capture.stop"}
{"type": "screenshare.start", "url": "https://your-slides.com"}
{"type": "screenshare.start", "port": 3001}
{"type": "screenshare.swap", "url": "https://different-page.com"}
{"type": "screenshare.swap", "port": 3002}
{"type": "screenshare.stop"}
{"type": "voice.state_update", "state": "thinking"}
{"type": "events.replay"}
```
`voice.state_update` manually sets the avatar's voice state in direct mode (webpage modes only). Broadcast as `voice.state` event to all connected clients including the avatar template. States: `listening`, `actively_listening`, `thinking`, `waiting_to_speak`, `speaking`, `interrupted`, `contextually_aware`. Note: `speaking` and `listening` are set automatically around `tts.speak` — use this for custom states like `thinking` while processing.

`events.replay` requests buffered events for crash recovery. Returns last 200 events or 5 minutes. See Crash Recovery section.

## Default Behavior: Active Participation

**The agent is an active meeting participant by default.** Unless the user explicitly
asks for passive/silent/notetaker mode, the agent MUST:

1. **Introduce itself** — When `greeting.prompt` fires (first participant joins), greet
   them via `tts.speak`. Example: "Hi [name], I'm [bot_name]. How can I help today?"
   Skip the greeting ONLY if the user explicitly said not to introduce itself.

2. **Respond when addressed** — If a participant says the bot's name, asks it a question,
   or directs speech at it, the agent MUST respond. This applies in BOTH one-on-one
   and group meetings, in both collaborative and direct mode.

3. **Proactively contribute** — If the agent has relevant knowledge or context about
   what's being discussed, it should contribute without waiting to be asked. If the
   user explicitly asks the agent not to speak unless spoken to, respect that —
   otherwise, contribute naturally.

3b. **Keep responses short in normal conversation** — 2-3 sentences max for greetings,
   quick answers, and acknowledgments. Meetings are real-time — long monologues feel
   robotic and block natural back-and-forth. The user can't easily interject during a
   10-sentence TTS response. Use longer responses ONLY when the user explicitly asks
   for detail ("explain this", "walk me through it", "give me a full summary"). For
   long responses, break into chunks and pause between them so the user can interject.
   Quick acknowledgments ("Got it", "Sure, one moment", "On it") should be one sentence.

4. **Never go silent unexpectedly** — The #1 bad experience is the agent joining a
   meeting and sitting there silently while participants talk. If the agent is processing,
   acknowledge first: `tts.speak "Let me check that."` In webpage modes
   (webpage-av, webpage-av-screenshare) the avatar automatically shows "thinking"
   the moment `user.message` arrives — the bridge handles this for you. The visual
   clears when you respond (or after a short fallback if you don't), so just focus on
   answering the user — no manual `set_state thinking` needed for the typical flow.
   If the agent doesn't know what to say, it can still acknowledge: "I heard you, but I'm not sure how to help with that."

5. **Silent/passive mode is opt-in only** — Use Pattern 4 (Silent Observer) ONLY when
   the user explicitly requests notetaking, silent observation, or passive mode.
   The words "just take notes", "don't speak", "silent mode", "passive", or "notetaker"
   are signals for passive mode. Everything else defaults to active participation.

**In collaborative mode:** The agent drives GetSun — use `trigger.speak`, `inject.natural`,
and `voice.context_update` to make the bot speak. GetSun handles the voice, but the agent
decides WHEN and WHAT to say.

**In direct mode:** The agent IS the voice — use `tts.speak` for every response. Silence
means the agent is not participating.

**See also:** THE CALL_LOOP algorithm (Pattern 5 → Method 1 for event-driven flow), Safety section (always send `leave`).

## Interaction Patterns

### Pattern 1: Meeting Assistant (collaborative)
```
Agent joins → CALL_LOOP:
  → call.bot_ready: send voice.context_update with agent capabilities
     (what you can do, "say 'let me check' instead of 'I can't'")
  → greeting.prompt received: inject.natural with greeting ("Hi [name], I'm [bot]. How can I help?")
  → Check events (every 5-10s)
  → transcript.final received:
    → If addressed: fetch data → context_update → trigger.speak
    → If task requested: GetSun says "let me check" → agent does work → context_update → inject.natural with results
    → If topic matches context: voice.contribute
    → If relevant discussion: proactively update context so GetSun can contribute
  → voice.text received (GetSun spoke):
    → If GetSun said "I can't" → context_update with capability + inject.natural correction
    → If GetSun deferred ("let me check") → agent must act now
    → If GetSun answered correctly → no action, context was good
  → No new events: sleep 5 → check again
  → call.ended: exit loop, get transcript → generate summary

GetSun handles the speaking — agent handles the thinking.
GetSun is always faster (<1s) — agent prepares context in advance.
The agent MUST keep checking events for the entire call duration.
```
**Follow THE CALL_LOOP algorithm (see Pattern 5 → Method 1 below — event-driven, recommended).**

### Pattern 2: Customer Support (direct)
```
Agent joins → CALL_LOOP:
  → greeting.prompt received: tts.speak "Hi [name]! I'm [bot]. How can I help you today?"
  → Check events (every 2-3s)
  → user.message received:
    → Simple question: tts.speak with answer
    → Complex question: tts.speak "Let me look into that"
      → Do ONE step → check call → next step → check call → tts.speak with answer
  → No new events: sleep 2 → check again
  → call.ended: exit loop

Agent IS the voice. Every second without checking = silence.
Always greet, always respond, always participate.
```
**Follow THE CALL_LOOP algorithm (see Pattern 5 → Method 1 below — event-driven, recommended).**

### Pattern 3: Voice Agent Webpage (direct + webpage-av)
```
Agent joins with voice agent page on --port 3000 or --webpage-url
  → Page receives meeting audio as mic input
  → Page's AI processes and generates response
  → Page plays response audio → participants hear it
  → Agent monitors via transcript.final for logging/context updates
```

### Pattern 4: Silent Observer (opt-in only)
**Use ONLY when the user explicitly asks for notetaking, silent observation, or passive mode.**
Keywords: "just take notes", "don't speak", "silent mode", "passive", "notetaker".
If the user does not explicitly request silent mode, use Pattern 1, 2, or 5 instead.
```
Agent joins with --transcription
  → Collects all transcript.final events
  → Never speaks
  → After call.ended: process transcript, generate action items
```

### Pattern 5: Voice Conversation (direct + bridge.py)

Talk to the user via voice in a meeting. The agent framework (Claude Code,
Agent SDK, Cursor, Codex, OpenClaw, Windsurf, Gemini CLI, Junie) IS the
intelligence — no separate LLM needed. Transcripts arrive as input, TTS
responses go back as output. Same session, same context.

Use when the user shares a meeting link and wants to discuss via voice,
pair-program, brainstorm, or have the agent participate in a call as itself.

**Three bridge scripts available:**

| Script | Mode | Visual | Screenshare | Use case |
|--------|------|--------|-------------|----------|
| `bridge.py` | audio | No | No | Voice-only conversation (simplest, recommended for coding agents) |
| `bridge-visual.py` | webpage-av-screenshare | Avatar | Yes | Presentations, sharing content, visual presence |
| `join.py` | any | any | any | Full control, all raw events, custom agents |

**bridge.py** (recommended for voice conversation):
```bash
python scripts/python/bridge.py "https://meet.google.com/abc" --name "Claude" --voice af_heart
```

**bridge-visual.py** (avatar + screenshare):
```bash
# Built-in avatar (no local server needed)
python scripts/python/bridge-visual.py "https://meet.google.com/abc" --name "Claude"

# With local screenshare (agent runs local server on port 3001)
python scripts/python/bridge-visual.py "https://meet.google.com/abc" --screenshare-port 3001

# With public URLs for both avatar and screenshare
python scripts/python/bridge-visual.py "https://meet.google.com/abc" \
  --webpage-url "https://your-site.com/avatar" \
  --screenshare-url "https://your-site.com/slides"
```

bridge-visual.py extends bridge.py with:
- Bot has an animated avatar visible to participants (7 voice states)
- Agent can screenshare public URLs: `{"command": "screenshare.start", "url": "https://..."}`
- Agent can screenshare local ports: `{"command": "screenshare.start", "port": 3001}` (auto-tunneled)
- Agent can swap to a different page atomically: `{"command": "screenshare.swap", "port": 3002}` or with a `url` (preferred over manual stop+start when changing what's shared)
- Agent can stop screenshare: `{"command": "screenshare.stop"}`
- Screenshare can be started/stopped dynamically at any time during the call
- Receives screenshare events: `screenshare.started`, `screenshare.stopped`, `screenshare.error`

**Screenshare lifecycle — end-to-end flow:**

The bot joins with avatar only. Screenshare activates on demand:

```
1. Agent starts bridge-visual.py with --template avatar
   → Bot joins meeting with animated orb/avatar (camera feed)
   → Screenshare is inactive — participants see only the avatar

2. Conversation happens (voice, transcripts, etc.)

3. User: "Can you show me the data?"
   Agent: {"command": "tts.speak", "text": "Sure, let me share my screen."}
   Agent: {"command": "screenshare.start", "url": "https://my-dashboard.com/slides"}
   → Receives: {"event": "screenshare.started", "url": "..."}
   → Participants now see avatar (camera) + slides (screenshare)

4. Agent updates the screenshare content:
   Agent writes: echo '{"slide": 1}' > /tmp/screenshare/state.json
   Agent: {"command": "tts.speak", "text": "As you can see on slide 2..."}

5. User: "OK thanks, that's enough."
   Agent: {"command": "screenshare.stop"}
   → Receives: {"event": "screenshare.stopped"}
   → Back to avatar only

6. Conversation continues without screenshare.
```

**For local content** (e.g., agent-generated HTML on localhost):
```
Agent starts a local HTTP server on port 3001 serving slides/charts
Agent: {"command": "screenshare.start", "port": 3001}
→ Bridge automatically creates a tunnel to localhost:3001
→ FirstCall loads it via the tunnel URL
```

**Key points:**
- Screenshare is always dynamic — start/stop anytime during the call
- Use `url` for public content, `port` for local content (auto-tunneled)
- The page polls your local server for state changes via HTTP (every 2s, no clicks)
- Use `webpage-av` mode if you never need screenshare
- See [Webpage AV Screenshare Guide](references/guides/webpage-av-screenshare.md) for page building details

**Sharing a live webpage (bridge-visual.py / bridge-visual.js):**

The agent can share a webpage from its localhost that meeting participants open
in their **own browser** — fully interactive (clickable, scrollable, any viewport).
This is different from screenshare, which renders in a headless browser inside the meeting.

| | Screenshare | Webpage |
|---|---|---|
| Rendered in | FirstCall's headless browser | Participant's own browser |
| Interaction | No clicks/scroll | Full interaction |
| Viewport | 1280x720 fixed | Any (participant's browser) |
| Visible to | All meeting participants (in-meeting) | Anyone with the URL |
| Use case | Presentations, slides | Dashboards, docs, forms, code |

**Commands:**
```json
{"command": "webpage.open", "port": 3002}
{"command": "webpage.close"}
```

**Events:**
```json
{"event": "webpage.opened", "url": "https://xyz.conn.agentcall.dev/k/{accessKey}/webpage/"}
{"event": "webpage.closed"}
{"event": "webpage.error", "message": "..."}
```

**Workflow:**
```
1. Agent starts a local HTTP server:
   python -m http.server 3002 --directory /tmp/my-report/

2. Agent opens the webpage tunnel:
   {"command": "webpage.open", "port": 3002}
   → Receives: {"event": "webpage.opened", "url": "https://xyz.conn.agentcall.dev/k/.../webpage/"}

3. Agent shares the URL in meeting chat:
   {"command": "send_chat", "message": "Here's the report: https://xyz.conn.agentcall.dev/k/.../webpage/"}

4. Participants click the link → see the agent's page in their browser

5. Agent updates files on disk → participants refresh to see changes
   (or use the polling pattern from screenshare for auto-updates)

6. When done:
   {"command": "webpage.close"}
```

**Use cases:**
- Agent generates a report or dashboard → shares link in chat
- Agent creates an interactive code diff → participants browse it
- Agent builds a form for collecting input → participants fill it out
- Agent serves documentation relevant to the discussion

**Requirements:** bridge-visual.py or bridge-visual.js (needs an active tunnel).
The webpage tunnel lives as long as the call — it closes automatically when the call ends.

**Audio routing is automatic (bridge-visual.py):** When you send `tts.speak`,
the audio is automatically routed to the avatar webpage — NOT directly to
FirstCall. The avatar template plays the audio via Web Audio API, FirstCall
captures the browser's audio output, and meeting participants hear it. You
do NOT need to specify a destination or use `tts.generate` — just send
`tts.speak` with your text and the routing is handled based on the mode.
In audio mode (bridge.py), audio goes directly to FirstCall. In webpage
modes (bridge-visual.py), audio goes to the webpage. Same command, automatic routing.

**Voice state updates are automatic (bridge-visual.py):** The avatar shows
"thinking" (purple glow) the moment `user.message` arrives, "speaking"
(green glow) when TTS is playing, and returns to "listening" (subtle pulse)
when done — no manual state management needed for the common flow. The
bridge clears "thinking" the instant you respond (or after a short fallback
if you stay silent).

For other states (e.g., flashing `interrupted` when cancelling), use
`set_state` — your explicit choice always overrides the auto behavior:
```json
{"command": "set_state", "state": "interrupted"}
{"command": "set_state", "state": "listening"}
```

Available states: `listening`, `actively_listening`, `thinking`,
`waiting_to_speak`, `speaking`, `interrupted`, `contextually_aware`.

**Showing work-in-progress to participants (bridge-visual.py):**

When the agent is doing extended work (research, multi-step processing,
async tool calls, anything that takes more than a few seconds), the
participants need to see what the bot is working on. Use `tasks.set` to
post a list of short task titles below the avatar status. The list is a
separate UI layer from the voice state — it doesn't replace
"speaking"/"thinking"/etc.; it shows ALONGSIDE them.

**You MUST keep the list current.** Call `tasks.set` immediately when you start
a new task, immediately when you finish one, and immediately whenever you
switch focus. A stale "Working on X" while you've moved on to Y is worse than
showing no list at all — participants lose trust in the indicator.

```json
{"command": "tasks.set", "tasks": ["Researching pricing", "Pulling Q3 numbers"]}
```

Each `tasks.set` is an atomic full-list replacement — send the complete
list every time, not deltas. To mark a task done, send a new list
without it; the avatar fades that line out gracefully (~400ms).

```json
{"command": "tasks.set", "tasks": ["Pulling Q3 numbers"]}   // first task done
{"command": "tasks.set", "tasks": []}                         // all done; clear
```

Limits: max 3 visible tasks at once, max 30 characters per task title
(longer items are silently truncated by the bridge). Just titles — no
status, no icons, no detail. Keep them short and active-tense:
"Researching pricing" not "Research the pricing data from competitors".

When to use:
- Multi-step or long-running work where the user needs to see progress
- Background tasks the agent kicks off and processes in parallel
- Any "I'll get back to you in a moment" situation that takes >5s

When NOT to use:
- Quick conversational replies (just answer; the avatar's "thinking"
  state is enough for normal back-and-forth)
- Internal-only steps the user doesn't care about ("Parsing JSON",
  "Calling tool")

The list automatically clears when the call ends. Independent of all
state machines — sending `tasks.set` doesn't affect auto-thinking,
voice state, or anything else.

bridge-visual additional commands:
| Command | Fields | What it does |
|---------|--------|-------------|
| `screenshare.start` | `url` OR `port` | Share a URL or local port (auto-tunneled) into the meeting as screenshare. For local-port shares the bridge appends a cache-buster (`?_acv=<ms>`) to the tunnel URL so FirstCall's headless browser reloads cleanly between swaps; external URLs pass through unchanged (avoids breaking signed URLs like S3 pre-signed, Vimeo private, secure embeds). If `port` is unreachable on localhost, emits `screenshare.error` instead of showing a white page. |
| `screenshare.swap` | `url` OR `port` | Atomically swap to a different page during a call. Sends stop, waits up to 5s for FirstCall to confirm, then starts the new share. Use this instead of stop+start to avoid the "old content keeps showing" race. |
| `screenshare.stop` | (none) | Stop screensharing |
| `webpage.open` | `port` (required) | Open a shareable webpage tunnel from a local port. Returns a URL participants open in their own browser. |
| `webpage.close` | (none) | Close the shareable webpage tunnel |
| `set_state` | `state` (required) | Manually set the avatar's voice state |
| `tasks.set` | `tasks` (array of strings) | Set the work-in-progress task list shown below the avatar status. Pass an array of short titles describing what the bot is currently doing (max 3 visible, 30 chars each — bridge truncates). Pass `[]` to clear. See "Showing work-in-progress" below. |

bridge-visual additional events:
| Event | Fields | When |
|-------|--------|------|
| `screenshare.started` | `url` | Screenshare is active in the meeting |
| `screenshare.stopped` | (none) | Screenshare has stopped |
| `screenshare.error` | `message` | Screenshare failed to start |
| `webpage.opened` | `url` | Webpage tunnel is active; URL is shareable with participants |
| `webpage.closed` | (none) | Webpage tunnel has closed |
| `webpage.error` | `message` | Webpage tunnel failed to open (missing port or no active tunnel) |

**Screenshare debugging — before, after, and when users complain:**

- **Before `screenshare.start` (local port):** run `curl http://localhost:PORT/` and verify the response body is the HTML you expect.
- **After the `screenshare.started` event arrives:** the event includes the tunnel `url`. Run `curl <url>` to confirm it returns 200 end-to-end through the tunnel. If this fails, the local content is fine but the tunnel side is broken. **Recovery:** (1) send `screenshare.swap` with the same port — atomic stop + restart with a fresh cache-busted URL; clears any stuck headless-browser state. (2) If still failing, route the screenshare through the webpage tunnel instead: organize your local content under a `/screenshare/` subpath (`localhost:PORT/screenshare/index.html`), use `webpage.open` to expose the whole server, then pass `https://tunnel/webpage/screenshare/` to `screenshare.start` as `url`. This pattern also keeps `webpage.open` available for participant-interactive pages on other subpaths (e.g., `/chat/`, `/docs/`).
- **If a participant says "I can't see the screenshare":** repeat the two checks above. If both pass and they still can't see it, send `{"command": "screenshot"}` — the returned base64 JPEG shows exactly what's on the meeting screen. Decode it and inspect what FirstCall is rendering (often: the page loaded but a CSS bug made it blank, or content is off-canvas).

Both bridge scripts share all base features:

**How it works — subprocess architecture:**

```
Agent Framework          bridge.py subprocess         AgentCall API
    |                         |                            |
    |-- spawn bridge.py ----->|                            |
    |                         |-- POST /v1/calls --------->|  (create call)
    |                         |-- WebSocket connect ------>|  (persistent)
    |                         |                            |
    |<-- stdout: user.message |<-- transcript.final -------|  (real-time)
    |   (agent processes)     |   (VAD buffered)           |
    |-- stdin: tts.speak ---->|-- WS: tts.speak ---------->|  (agent responds)
    |                         |                            |
    |<-- stdout: tts.done     |<-- tts.done ---------------|
    |<-- stdout: user.message |<-- transcript.final -------|
    |   ... loop continues    |   ... for full meeting     |
```

The bridge subprocess holds the WebSocket connection internally. The agent
never touches WebSocket — it reads stdout and writes stdin. The bridge runs
two concurrent tasks: WebSocket→stdout (events flow continuously) and
stdin→WebSocket (commands accepted anytime).

**IMPORTANT:** The agent framework MUST read stdout from the subprocess
continuously in real-time — NOT wait for the subprocess to exit. Events
arrive as they happen (someone speaks, someone joins, etc.). If the framework
only reads stdout after the process ends, it will miss all events and the
voice conversation won't work. Each line of stdout is a complete JSON event
that should be processed immediately.

Note: bridge.py flushes stdout after every event (`flush=True`). Events
arrive immediately — no Python buffering delay. If running with `PYTHONUNBUFFERED=1`
environment variable, this is guaranteed even for edge cases.

**VAD coalescing (bridge.py only):**

Speech-to-text splits long sentences into multiple transcript.final events.
A speaker who pauses mid-thought gets fragmented:

```
Without bridge.py (raw join.py):
  transcript.final: "Can you check the"          (1s pause)
  transcript.final: "health endpoint"             (1s pause)
  transcript.final: "and also the database"       (done)
  → Agent sees 3 separate instructions

With bridge.py (VAD coalesced):
  user.message: "Can you check the health endpoint and also the database"
  → Agent sees one complete utterance
```

The bridge coalesces fragmented transcript.final events into a single
`user.message` after a short cooldown. Configurable via `--vad-timeout`
(default 1.25s) — raise for slow speakers, lower for fast back-and-forth.

**bridge.py protocol (simplified from join.py's 30+ event types):**

Events you receive (stdout, one JSON per line):
```json
{"event": "call.bot_ready", "call_id": "call-xxx"}
{"event": "participant.joined", "name": "Alice"}
{"event": "participant.left", "name": "Bob"}
{"event": "greeting.prompt", "participant": "Alice", "hint": "Alice joined. Introduce yourself and greet them via tts.speak. Active participation is the default — do not stay silent."}
```
`greeting.prompt` fires when the first non-bot participant joins — this is your signal
that someone is in the meeting and can hear you. **You SHOULD greet them** unless the
user explicitly asked you not to. Always wait for this event (or at least one
`participant.joined`) before sending any tts.speak or send_chat commands.
`greeting.prompt` is reliable — if the agent connects after a participant already joined,
bridge.py still detects them and sends the prompt.
```json
{"event": "user.message", "speaker": "Alice", "text": "can you check the health endpoint"}
{"event": "chat.received", "sender": "Alice", "message": "here's the error: TypeError..."}
{"event": "tts.done"}
{"event": "tts.error", "reason": "tts_unavailable"}
{"event": "screenshot.result", "data": "base64-jpeg...", "width": 1920, "height": 1080, "request_id": "screenshot"}
{"event": "call.ended", "reason": "left"}
```

Commands you send (stdin, one JSON per line):
```json
{"command": "tts.speak", "text": "Hello! I'm here.", "voice": "af_heart"}
{"command": "tts.speak", "text": "The health endpoint returned OK.", "voice": "af_heart", "speed": 1.0}
{"command": "send_chat", "message": "https://github.com/org/repo/pull/42"}
{"command": "raise_hand"}
{"command": "mic", "action": "on"}
{"command": "leave"}
```

Command reference:
| Command | Fields | What it does |
|---------|--------|-------------|
| `tts.speak` | `text` (required), `voice` (default: af_heart), `speed` (default: 1.0) | Speak text in the meeting via TTS. |
| `send_chat` | `message` (required) | Send a text message in the meeting chat. Use for URLs, code, text that sounds bad via TTS. |
| `raise_hand` | (none) | Raise the bot's hand. Useful in group meetings before speaking. |
| `mic` | `action` ("on" / "off" / "toggle", default "on") | Unmute, mute, or toggle the bot's microphone. Useful when the bot joins muted in large group meetings. |
| `screenshot` | `request_id` (optional, default: "screenshot") | Take a screenshot of the meeting view. Returns base64 JPEG. |
| `leave` | (none) | Gracefully leave the meeting. Call ends. |

**CRITICAL — end the call cleanly (MANDATORY):**

After `{"event": "call.ended"}` is received, or when the agent decides to end
the call itself, do ALL of these in order. Skipping any step risks an orphan
bot consuming credits up to your plan's max_duration (1h base, 4h pro, 8h
enterprise), leaked file descriptors, and port conflicts on the next call.

1. **Send `{"command": "leave"}`** — only if the agent is ending the call
   (user said bye, task done). Wait for `tts.done` first if you just spoke;
   otherwise the call cuts mid-audio. **Skip this step if `call.ended` already
   arrived** — the bot is already gone, no leave needed.

2. **Kill the bridge subprocess.** SIGTERM, wait 2-3s, then SIGKILL if still
   running. Closing stdin/stdout is NOT enough — the WebSocket stays open and
   leaks file descriptors across sessions.

3. **Kill the local HTTP servers YOU spawned** for avatar, screenshare, or
   `webpage.open`. Track the PID when you start each one; do NOT `lsof`-sweep
   unrelated processes.
   ```bash
   python -m http.server 3001 --directory /tmp/screenshare/ &
   SCREENSHARE_PID=$!
   # on call end:
   kill $SCREENSHARE_PID 2>/dev/null || true
   ```

4. **Verify the call actually ended via API.** Always — one cheap HTTP call,
   catches rare backend-side silent transaction conflicts that leave calls
   stuck in non-`ended` status:
   ```bash
   # With jq:
   STATUS=$(curl -s -H "Authorization: Bearer $AGENTCALL_API_KEY" \
            "https://api.agentcall.dev/v1/calls/$CALL_ID" | jq -r .status)

   # Without jq (grep fallback):
   STATUS=$(curl -s -H "Authorization: Bearer $AGENTCALL_API_KEY" \
            "https://api.agentcall.dev/v1/calls/$CALL_ID" \
            | grep -oE '"status":"[^"]*"' | cut -d'"' -f4)

   if [ "$STATUS" != "ended" ] && [ "$STATUS" != "error" ]; then
     curl -X DELETE -H "Authorization: Bearer $AGENTCALL_API_KEY" \
          "https://api.agentcall.dev/v1/calls/$CALL_ID"
   fi
   ```

Handle `KeyboardInterrupt` and `SIGTERM` in your code so steps 1-4 run on
abnormal exit too.

**Tip — avoid awkward silence:** If your agent needs time to process (LLM call,
file search, running commands), the user hears silence while you work. Send a
quick acknowledgment first: `{"command": "tts.speak", "text": "Let me check that."}`,
then do your processing, then send the full response. This creates a much better
user experience — the participant knows the bot heard them and is working on it,
rather than wondering if it froze or disconnected.

**CRITICAL — the call is a continuous loop, not a one-shot task:**

You MUST follow THE CALL_LOOP algorithm (Method 1 event-driven loop, recommended — or Method 3 polling loop fallback) for the
entire duration of the call. The call is your primary task — everything else
is a subtask. You are NOT done until `call.ended` appears.
Also read: Default Behavior: Active Participation (above) and Safety (below).

**The #1 failure mode:** The agent processes a few events, does some work, then
stops checking — it exits its loop thinking it's "done." The user is left
talking to silence. This MUST NOT happen. After every action, your next step
is ALWAYS: check the call for new events.

**Subtask pattern:** When asked to do work (search code, read files, run commands):
1. Acknowledge first: `tts.speak "Let me check that"`
2. Do ONE step of the work
3. Check call for new events (the user may have said something while you worked)
4. Do the next step
5. Check call again
6. Report results: `tts.speak "Here's what I found..."`
7. Check call — back to the main loop

For long tasks, delegate to a subagent and keep monitoring the call. The call
is real-time — a human is waiting. If you disappear for 30 seconds, the user
thinks the bot is broken.

If the user says something while you're working:
- Correction ("actually, check the other file") → adjust your work
- Cancellation ("never mind") → stop and acknowledge
- New question → acknowledge ("I heard you, let me finish this first")
- Additional context ("also the database") → incorporate it

**TTS sequencing:** If you send multiple `tts.speak` commands without
waiting for `tts.done`, they queue and play back-to-back, not overlapping.
For natural conversation, wait for `tts.done` before sending the next
response so the bot doesn't speak continuously without pauses.

**Chat I/O — for text that's hard to speak:**

Some information sounds terrible via TTS: URLs, code snippets, email addresses,
file paths, JSON, error messages. Use meeting chat for these:

```
Agent speaks: "I found the issue. I'll put the fix in chat."
Agent sends:  {"command": "send_chat", "message": "https://github.com/org/repo/pull/42"}
```

When someone sends a chat message in the meeting, the agent receives:
```json
{"event": "chat.received", "sender": "Alice", "message": "TypeError: cannot read property 'length' of null"}
```

The agent can process this as text input — useful for pasting error logs, code, or links
that are easier to read than speak.

**Screenshots — see what's in the meeting:**

The bot can take a screenshot of its meeting view at any time. The screenshot
captures what the bot sees: the participant video grid, or if someone is
presenting/screensharing, the shared screen content (slides, spreadsheets,
documents, demos). This works in **all modes**.

Take a screenshot:
```json
{"command": "screenshot"}
```

Receive the result:
```json
{"event": "screenshot.result", "data": "base64-jpeg...", "width": 1920, "height": 1080, "request_id": "screenshot"}
```

The `data` field contains a base64-encoded JPEG image. Vision-capable agents
(Claude, GPT-5.4, Gemini) can decode and analyze this image to:
- Read text on shared slides or presentations
- See charts, diagrams, or spreadsheets being presented
- Check who is in the meeting (participant video tiles)
- Read screen content that someone is sharing

Example use case:
```
User (speaking): "Can you read what's on the screen right now?"
Agent: sends {"command": "screenshot"}
Agent: receives screenshot.result with base64 JPEG
Agent: analyzes the image (vision model)
Agent: sends {"command": "tts.speak", "text": "I can see a slide titled 'Q3 Revenue'..."}
```

Screenshots are on-demand only — the agent must request each one. For periodic
capture (e.g., monitoring a presentation), use `capture.start` / `capture.stop`
commands via join.py directly.

**Coding agent integration:**

This pattern works with all major CLI-based coding agents:

| Agent | How to spawn bridge.py |
|-------|----------------------|
| Claude Code / Agent SDK | `bash("python scripts/python/bridge.py 'https://meet.google.com/abc' --name Claude")` |
| OpenAI Codex | `!python scripts/python/bridge.py "https://meet.google.com/abc" --name Codex` |
| OpenClaw (Moltbot) | Shell command via skill execution |
| Windsurf (Cascade) | Terminal command execution (with permission) |
| Gemini CLI | Bash tool via skill |
| JetBrains Junie | Skill script execution |
| Cursor | Requires tmux for PTY: `tmux new-session -d -s mtg && tmux send-keys -t mtg "python scripts/python/bridge.py 'URL'" Enter` |

The agent remains fully capable during the call — it can read files, run
commands, edit code, search the codebase, and commit changes while talking.
The meeting is just another I/O channel alongside the terminal.

For Claude Agent SDK specifically, the agentic loop runs indefinitely
(configurable via `max_turns`). No turn limits — the agent participates
for the full meeting duration.

**How to read events — four methods:**

*Method 1: tail -f + Monitor (RECOMMENDED — kernel-driven, zero polling, zero idle tokens)*

This is the best method for almost every agent. Events are delivered by the
operating system's file-change notifications (inotify on Linux, kqueue on
macOS, ReadDirectoryChangesW on Windows). The agent is truly idle between
events — zero CPU, zero tokens consumed during silence. When a participant
speaks, the kernel wakes the tailer, the event is delivered as a notification,
the agent reacts, and returns to idle.

**Why this wins:** polling (Method 3) burns 60,000-180,000 tokens per hour on
empty "is there a new event?" checks during quiet periods. Method 1 burns
zero. Same functional behavior, dramatically lower cost and latency.

**Requirements:** bash or zsh (for the `< <(tail -f ...)` process substitution).
Not available in `sh`, `dash`, or `ash` — use Method 2/3/4 in those shells.

**Canonical setup (Linux / macOS / Git Bash / WSL):**

```bash
# Put the two files in the agent's working directory so parallel agents
# don't collide. Each agent running in its own cwd gets its own files.
EVENTS="$PWD/meeting-events.jsonl"
COMMANDS="$PWD/meeting-commands.jsonl"

# Create empty commands file
: > "$COMMANDS"

# Start bridge: events → file, stdin ← live stream of commands file
python3 scripts/python/bridge.py "<meet-url>" \
  --name "Claude" \
  --output "$EVENTS" \
  < <(tail -f "$COMMANDS") &
BRIDGE_PID=$!

# Stream events (use your framework's streaming primitive on this command)
tail -f "$EVENTS" | grep --line-buffered -E \
  '"event": "(user\.message|greeting\.prompt|call\.(ended|bot_ready|degraded|credits_low|max_duration_warning)|participant\.(joined|left)|chat\.received|tts\.(done|error|interrupted)|screenshare\.error|webpage\.error)"'

# Send a command (just append to the commands file)
echo '{"command": "tts.speak", "text": "Hi"}' >> "$COMMANDS"
```

**CRITICAL — `grep --line-buffered` is REQUIRED.** Without it, the pipe buffers
and your events can be delayed by **minutes**. This is the single most common
mistake when setting up this pattern.

**Why `< <(tail -f "$COMMANDS")`?** This is bash/zsh process substitution. It
feeds the bridge's stdin with the live tail of the commands file — every line
you append is delivered to the bridge instantly. The bridge's threaded stdin
reader (cross-platform) picks it up and forwards to the WebSocket. No stdin
pipe management needed on your side; just append to the file.

**Claude Code (best integration):**

Use the `Monitor` tool on the `tail -f | grep` command with `persistent: true`.
Each matched line arrives as a task notification, delivered mid-turn, exactly
like a user message. React immediately, write a command to the commands file,
return to idle.

```
1. Bash(run_in_background=true): the bridge startup line
2. Monitor(persistent=true): the tail -f | grep line
3. For each notification: process the event, append command to file
4. On call.ended notification: stop Monitor, kill $BRIDGE_PID
```

**Other agent frameworks:**

If your framework supports streaming subprocess stdout (Agent SDK, Cursor with
tmux, OpenClaw, Windsurf with terminal, etc.), run the `tail -f | grep`
command as a background task and read its stdout line by line. Each line is
one event notification.

**Windows alternatives:**

- **Git Bash** (ships with [Git for Windows](https://git-scm.com/download/win)): all commands above work as-is.
- **WSL**: all commands above work as-is.
- **PowerShell:** replace `tail -f` with `Get-Content -Wait`:
  ```powershell
  Get-Content -Wait "$PWD\meeting-events.jsonl" | Select-String -Pattern '"event":\s*"(user\.message|greeting\.prompt|call\.ended|...)"'
  ```
- **Native cmd (no alternatives installed):** fall back to Method 3 (polling).

**Event-driven CALL_LOOP (use with Method 1):**

```
ALGORITHM (event-driven — no polling, no sleep):

1. Start bridge in background with --output + stdin from tail -f commands
2. Start Monitor / tail -f | grep on the events file (background, persistent)

3. CALL_LOOP (wait for notifications until call.ended):
   a. WAIT for next notification (kernel-blocking, zero CPU, zero tokens)
   b. Process the event:
      - user.message        → respond via tts.speak (direct) or context_update+trigger.speak (collaborative)
      - greeting.prompt     → greet the new participant
      - chat.received       → process as text input
      - tts.done            → previous TTS finished; OK to send next if queued
      - tts.interrupted     → user cut you off; decide to resume, replan, or acknowledge
      - tts.error           → TTS generation failed; try again or notify user
      - call.degraded       → voice intelligence dropped; log and continue
      - call.credits_low    → mention to user, suggest recharge URL
      - call.max_duration_warning → rejoin strategy (see warning event docs)
      - participant.joined  → someone new entered the meeting
      - participant.left    → someone left
      - call.ended          → EXIT CALL_LOOP
   c. If a subtask is needed (code search, file read, etc.):
      - Do the subtask (single tool call or delegate to subagent)
      - New events during the subtask are still queued as notifications
      - Process them as they arrive, even mid-subtask
   d. Return to step (a)

4. After EXIT: kill bridge PID, delete events + commands files, fetch transcript if needed

RULES:
- You do NOT poll. The kernel wakes you when something happened.
- You are truly idle between events — zero tokens consumed during silence.
- If asked to do something complex, acknowledge first via tts.speak ("Let me check that"),
  then work. Events that arrive during work naturally interrupt and take priority.
- NEVER stop the loop early. call.ended is the only exit signal.
- Your commands go via `echo '{"command": ...}' >> "$COMMANDS"` — append, don't overwrite.
```

**Why file-based commands (instead of stdin pipe)?**
- Parallel-safe: each agent's cwd has its own `meeting-commands.jsonl`.
- No stdin pipe management (no `/proc/$PID/fd/0` gymnastics, no named pipes).
- Survives agent restart: agent crashes → restarts → appends new commands → bridge picks them up. State is just a file.
- Debuggable: you can `cat` the commands file at any time to see what's been sent.

**Why file-based events (instead of reading bridge stdout directly)?**
- Decoupling: the bridge subprocess is independent of the agent subprocess.
- The agent can restart without killing the bridge (and vice versa).
- Multiple agents/observers can tail the same events file.

---

*Method 2: Interactive subprocess (lowest latency, classic)*
If your agent framework supports interactive stdin/stdout with a subprocess:
```
spawn bridge.py → read stdout line by line (blocking) → process each event
                → write commands to stdin at any time
```
Events arrive instantly. The agent blocks on `readline()` until the next event,
processes it, responds, then blocks again. Between events, the agent is idle.
This is the ideal method — zero polling delay.

*Method 3: Background process + file polling (fallback — high token cost)*

**Warning:** This method burns 60,000-180,000 tokens per hour on idle polling
during quiet periods in the meeting. Only use it if Method 1 (tail -f) is not
available in your environment — typically because your shell is `sh`/`dash`/`ash`
(no process substitution) or your agent framework can't run a streaming
subprocess. For almost all modern agents, Method 1 is strictly better.

Run bridge.py in background with `--output` flag and poll the events file.
This is the most portable pattern — it works with all agent frameworks and
keeps the agent in a continuous loop for the entire call duration.

```bash
# Start bridge in background with file output
python scripts/python/bridge.py "https://meet.google.com/abc" --name Agent \
  --output /tmp/meeting-events.jsonl 2>/tmp/meeting.err &
BRIDGE_PID=$!

# Poll for new events
tail -n 5 /tmp/meeting-events.jsonl

# Send commands (Linux)
echo '{"command": "tts.speak", "text": "Hello!"}' > /proc/$BRIDGE_PID/fd/0
```

**macOS:** `/proc` doesn't exist on macOS. Use a named pipe instead:
```bash
# Create named pipe and start bridge reading from it
mkfifo /tmp/meeting-stdin
python scripts/python/bridge.py "https://meet.google.com/abc" --name Agent \
  --output /tmp/meeting-events.jsonl < /tmp/meeting-stdin 2>/tmp/meeting.err &

# Keep pipe open (required — pipe closes when last writer disconnects)
exec 3>/tmp/meeting-stdin

# Send commands
echo '{"command": "tts.speak", "text": "Hello!"}' >&3

# Clean up when done
exec 3>&-
rm /tmp/meeting-stdin
```

**THE CALL LOOP — follow this algorithm exactly:**

The call is your **primary task**. Everything else is a subtask of the call.
You are NOT done until `call.ended` appears in the events file. This is a
live call — a human is on the other end waiting for your responses.

```
ALGORITHM (mandatory — follow exactly):

1. Start bridge.py in background with --output /tmp/meeting-events.jsonl
2. Save the PID for sending commands later

3. CALL_LOOP (repeat until call.ended):
   a. CHECK CALL: tail -n 20 /tmp/meeting-events.jsonl
   b. Process new events:
      - user.message → respond via tts.speak (direct) or context_update (collaborative)
      - call.ended → EXIT CALL_LOOP
      - greeting.prompt → greet the participant
      - chat.received → process as text input
   c. If a subtask is in progress (code search, file read, etc.):
      - Do ONE STEP of the subtask (one tool call)
      - Return to step (a) — CHECK CALL again before the next step
      - NEVER do multiple tool calls without checking the call between them
   d. If no new events and no subtask:
      - sleep 2 (direct mode) or sleep 5 (collaborative mode)
   e. Go to (a)

4. After EXIT: clean up, fetch transcript if needed

RULES:
- Step (a) happens BEFORE and AFTER every action. No exceptions.
- The call is highest priority. If the user speaks while you're working,
  their message takes priority over your current subtask.
- If asked to do something complex, acknowledge first ("Let me check that"),
  then work in small steps, checking the call between each step.
- For long tasks, use a subagent — delegate the work and keep monitoring the call.
- NEVER assume the call is over. NEVER stop the loop early.
- Your todo list should ALWAYS have "Check call for new events" as the next item.
```

**Polling frequency:**

| Mode | Poll interval | Why |
|------|--------------|-----|
| Direct (1-on-1) | 2-3 seconds | You ARE the voice — silence = broken bot |
| Collaborative | 5-10 seconds | GetSun handles voice timing — you provide intelligence |

Both modes: the agent is the brain. The difference is latency tolerance.
In collaborative mode, GetSun speaks autonomously from its context while
the agent updates that context. In direct mode, the agent must respond directly.

*Method 4: Claude Code Stop Hook (for polling fallback)*

If you are using Method 3 (polling) in Claude Code and need to prevent Claude
from exiting mid-call, the Stop Hook below blocks exit until `call.ended`
appears. Not needed if you use Method 1 (tail -f + Monitor with persistent=true)
since Monitor keeps the agent in the loop naturally.

Claude Code has two known issues with polling-based meeting calls:
1. **Slow response** — polling with sleep adds 2-5 seconds of latency per event
2. **Stops mid-call** — Claude decides it's "done" and exits the loop, leaving the user talking to silence

**Solution: bridge.py + Stop Hook**

Use bridge.py (Method 3) as the base, then add a Stop Hook to prevent Claude
from ever stopping while the call is active. This solves problem #2 completely.

**Step 1:** Start bridge.py with `--output` as usual (Method 3 above).

**Step 2:** Add this Stop Hook to your project's `.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'EVENTS=/tmp/meeting-events.jsonl; if [ -f \"$EVENTS\" ] && ! grep -q call.ended \"$EVENTS\"; then echo \"{\\\"decision\\\": \\\"block\\\", \\\"reason\\\": \\\"Active meeting call in progress. Check /tmp/meeting-events.jsonl for new events and respond. Do NOT stop until call.ended appears.\\\"}\"; exit 2; fi'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**How it works:**
- Every time Claude tries to stop (finish a turn), the Stop Hook fires
- The hook checks if `/tmp/meeting-events.jsonl` exists AND does NOT contain `call.ended`
- If the call is still active → blocks the stop (exit code 2) and re-injects a prompt telling Claude to check for new events
- If the call has ended (or file doesn't exist) → allows Claude to stop normally
- This creates a persistent loop — Claude cannot exit until the call ends

**Result:** Claude Code stays in the CALL_LOOP for the entire call duration.
Combined with bridge.py's `--output` file, this is the most reliable
Claude Code meeting integration.

**Other agent frameworks (Codex, Cursor, Windsurf, Gemini CLI, Junie):**
These frameworks do not have Stop hooks that can block exit. Use Method 1
(tail -f + streaming subprocess) when available — it's self-sustaining because
the agent blocks on the event stream. Fall back to Method 3 (polling) only
when Method 1 isn't possible.

**Advanced Claude Code Integration (optional):**

For lower latency or push-based event delivery, Claude Code also supports:
- **Channels MCP** — push `transcript.final` events directly into a running
  Claude Code session via a custom MCP channel server. Lowest latency, but
  requires Claude Code v2.1.80+ and the `--channels` flag (research preview).
- **SDK daemon** — use `@anthropic-ai/claude-code` SDK's `query()` function
  with `sessionId` for programmatic per-transcript invocation. Most production-ready
  for custom integrations.
- **FileChanged hook** — watch the events file and inject new events into
  Claude's context automatically when bridge.py writes them.

**Limitations:**

This pattern requires an agent that can spawn a subprocess and read its
stdout in real-time. It does NOT work with chat-only interfaces (claude.ai
web, ChatGPT web, Gemini web) — these cannot spawn subprocesses.

Chat-only agents can still interact with meetings using the REST API directly:
- `POST /v1/calls` — create a call and join a meeting
- `GET /v1/calls/{id}` — check call status (bot_joining, bot_ready, ended)
- `GET /v1/calls/{id}/transcript?format=json` — fetch the transcript at any time
- `DELETE /v1/calls/{id}` — end the call

These endpoints work as standard HTTP tool calls. The agent can create a call,
periodically check the transcript, and end the call — but cannot participate
in real-time voice conversation.

See [Voice Bridge for Coding Agents](examples/coding-companion/) for a full walkthrough with examples.

## Crash Recovery

If the agent process crashes:
1. On startup, checks `.agentcall-state.json` for an active call (expires after 24h)
2. Calls `GET /v1/calls/{call_id}` to verify call is still active
3. Reconnects to the WebSocket
4. Receives enriched `call.state` snapshot (status, participants, active speaker)
5. Sends `{"type": "events.replay"}` to get missed events (last 200 or 5 min)
6. Deduplicates and processes missed events
7. (Optional) Gets full transcript via `GET /v1/calls/{id}/transcript`

The state file is automatically cleaned up on normal exit.
See [Crash Recovery Guide](references/guides/crash-recovery.md) for full examples and deduplication patterns.

## Built-in UI Templates

Use `--template` instead of `--port` to use a built-in template (no local server needed):

| Template | Description |
|----------|-------------|
| `ring` | **Default.** Neon ring with glow, pulses on speak/think, 7 voice state colors |
| `orb` | Pulsing filled orb that reacts to voice state (8 colors) |
| `avatar` | Circular avatar image with all 7 voice states + status text |
| `dashboard` | Participant list + live transcript + connection status (monitor tool) |
| `blank` | Bot name on black background (placeholder) |
| `voice-agent` | Mic-enabled voice agent base with auto-start getUserMedia |

## Transcript Retrieval

After the call ends, the full transcript is available:
```bash
curl https://api.agentcall.dev/v1/calls/{call_id}/transcript?format=json \
  -H "Authorization: Bearer ak_ac_xxx"
```

Transcripts are stored by FirstCall (meeting infrastructure) for `transcript_retention_hours` (default 24h, max 7 days).

## Safety

| Feature | Default |
|---------|---------|
| Auto-leave when alone | 2 minutes |
| Silence timeout | 5 minutes |
| Max duration | Plan limit (check https://agentcall.dev for current limits) |
| Transcription | On (required for agent to receive speech as text) |
| Bot visible in participant list | Always |
| Meeting host can kick bot | Always |

**Always clean up:** Send `{"command": "leave"}` or `DELETE /v1/calls/{id}` when
done. The safety timeouts above are last resorts — they don't trigger immediately.
An orphaned bot with participants in the meeting will run until `max_duration` (1 hour),
accumulating charges the entire time.

## Pricing

Base plan: 6 hours (audio mode), 1 concurrent call. All features included.
Paid: per-minute billing. Base rate varies by mode (audio cheapest, screenshare
most expensive). Add-ons: transcription, voice intelligence, TTS.
Check https://agentcall.dev for current rates and plan limits.

## Checking for Skill Updates (optional)

This is **completely optional** — the skill is backwards-compatible and works
without ever running this check. Marketplace users should use
`/plugin marketplace update pattern-ai-labs-agentcall` followed by
`/plugin update join-meeting` — Claude Code handles updates natively.

This checker is primarily useful for users who installed the skill directly
from GitHub or as a zip. If you want to help the user discover a new version,
run the checker once per session:

```bash
python scripts/python/check_update.py
# or
node scripts/node/check_update.js
```

The script prints JSON to stdout and always exits 0 (never breaks the caller):

```json
{
  "current_version": "1.0.0",
  "latest_version": "1.1.0",
  "update_available": true,
  "repo_url": "https://github.com/pattern-ai-labs/agentcall",
  "update_commands": {
    "marketplace": "/plugin marketplace update pattern-ai-labs-agentcall && /plugin update join-meeting",
    "git": "git pull",
    "zip": "Download the latest release from https://github.com/pattern-ai-labs/agentcall"
  },
  "last_checked": "2026-04-14T12:00:00Z",
  "cached": false
}
```

If `update_available` is `true`, tell the user a newer version is available
and show the update command that matches how they installed the skill.

The checker caches the result at `~/.agentcall/update-check.json` for 7 days,
so running it on every session is cheap. On network failure, it silently
returns a `network_failure` error (or a stale cached result if one exists).

**Skip this step if** the user is on the marketplace distribution (they get
updates automatically), or if you don't want to surface updates to the user.

## Examples

- [Simple Note-Taker](examples/notetaker-simple/) — join a meeting, save the transcript to a file (Python + Node.js)
- [Smart Note-Taker](examples/notetaker-smart/) — transcript + LLM summarization with action items (Python + Node.js, works with Claude/GPT-4o/Gemini)
- [Multilingual Note-Taker](examples/notetaker-multilingual/) — collect raw audio, send to Gemini for multilingual transcription + translation + summary (Python)
- [Customer Support Agent](examples/support-agent/) — 1-on-1 support bot with TTS, LLM decision making, knowledge base, and call logging (Python)
- [Meeting Assistant](examples/meeting-assistant/) — collaborative mode with avatar, trigger words, barge-in prevention, and autonomous voice intelligence (Python)
- [Smart Meeting Assistant](examples/meeting-assistant-smart/) — collaborative mode + background task execution with tools, instant acknowledgment, context updates, and result injection (Python)
- [Voice Bridge for Coding Agents](examples/coding-companion/) — mid-session voice I/O for AI coding agents (Claude Code, Cursor, Codex). No separate LLM — the agent framework IS the intelligence. Includes VAD buffering, chat I/O, skill definition (Python)

## Guides

- [Collaborative Mode Guide](references/guides/collaborative-mode.md) — context system, inject patterns, background tasks
- [Webpage Audio Guide](references/guides/webpage-audio.md) — audio queue, interruption handling, AgentCallAudio player
- [Interruption Handling Guide](references/guides/interruption-handling.md) — VAD, sentence tracking, resume patterns
- [Webpage AV Guide](references/guides/webpage-av.md) — avatar, brand, voice agent webpage
- [Webpage AV Screenshare Guide](references/guides/webpage-av-screenshare.md) — dual visual presence, screenshare control
- [UI Templates Guide](references/guides/ui-templates.md) — all templates, voice states, mic setup
- [Crash Recovery Guide](references/guides/crash-recovery.md) — event replay, deduplication, recovery example
