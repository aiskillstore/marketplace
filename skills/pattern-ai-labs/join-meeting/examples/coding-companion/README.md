# Voice Bridge for AI Coding Agents

Talk to your AI coding agent via a meeting call instead of typing. The agent joins a Google Meet, Zoom, or Teams call, hears you via transcript, and speaks back via TTS — all within the same coding session.

## The Core Idea

You're working with an AI coding agent (Claude Code, Cursor, Codex, Gemini CLI). You've been chatting via text. Now you want to switch to voice — maybe you're brainstorming, away from the keyboard, or just find it faster to talk.

You share a meeting link. The agent joins the call. **From this point, your voice is the input and TTS is the output — but everything else stays the same.** The agent still has your full project context, can still read files, edit code, run commands. The meeting is just another I/O channel.

```
Before:  [You type]  →  Agent processes  →  [Agent types back]
After:   [You speak] →  Agent processes  →  [Agent speaks back]
                         ↕ same session, same context, same tools
```

## How It Works

### Phase 1: Normal text coding session

```
You (typing): "check if the health endpoint is responding"
Agent: runs curl https://api.agentcall.dev/health
Agent: "Health endpoint returned status OK."
```

### Phase 2: Switch to voice

```
You (typing): "join this meeting: https://meet.google.com/abc-def-ghi"
Agent: spawns bridge.py as subprocess
Agent: receives {"event": "call.bot_ready"} on stdout
Agent: writes {"command": "tts.speak", "text": "Hey, I'm here."} to stdin
```

### Phase 3: Voice conversation

The bridge script translates between the meeting and the agent:

```
Meeting                    bridge.py                  Agent Framework
  |                            |                            |
  | User speaks:               |                            |
  | "check the endpoint"       |                            |
  |                            |                            |
  | transcript.final --------->|                            |
  | transcript.final --------->| (VAD buffer: wait 2s)     |
  |                            |                            |
  |                 (silence)  |                            |
  |                            |-- stdout: user.message --->|
  |                            |   "check the endpoint"     |
  |                            |                            |
  |                            |   Agent: runs curl...      |
  |                            |                            |
  |                            |<-- stdin: tts.speak -------|
  |                            |   "Status OK"              |
  |<-- TTS audio --------------|                            |
  | User hears: "Status OK"   |                            |
```

```
You (speaking): "can you read the webhook handler and tell me if there are any issues?"

Agent (same session — already knows the codebase):
  → reads server/internal/api/payment_handlers.go
  → analyzes the code
  → speaks: "The webhook handler looks solid. HMAC signature verification is in place,
     idempotency check on order ID, and proper error handling. One thing I'd suggest
     is adding rate limiting — currently anyone who knows the endpoint URL could
     flood it with requests."

You (speaking): "good point, add rate limiting to it"

Agent:
  → edits the file (normal tool use, same as text)
  → speaks: "Done. I added a rate limiter to the webhook endpoint — 
     10 requests per second per IP."
```

### Phase 4: End the call

The agent can end the call itself, or you can end it from the meeting:

```
You (speaking): "that's all for now, thanks"

Agent:
  → speaks: "Sounds good. I made two changes during our call — rate limiting on
     the webhook handler and a typo fix in the README. Want me to commit them?"
  → sends: {"command": "leave"}

Call ends. Agent continues in text mode.
```

Or if you end the call from the meeting side:

```
← stdout: {"event": "call.ended", "reason": "meeting_ended"}

Agent: "The call ended. Here's a summary of what we discussed:
  1. Verified health endpoint is responding
  2. Added rate limiting to webhook handler
  3. Discussed next steps for Kokoro TTS deployment
  Want me to commit the changes?"
```

## Files

| File | Purpose |
|------|---------|
| `../../scripts/python/bridge.py` | The bridge script — spawned as subprocess by the agent framework. Located in `scripts/python/` alongside `join.py`. |
| `SKILL-FRAGMENT.md` | Skill definition — tells agent frameworks how to discover and use this |
| `README.md` | This file — detailed walkthrough and explanation |

**Note:** `bridge.py` lives in `scripts/python/` (not in this example folder) because it is a core script, not just an example. It is the recommended script for coding agents joining calls.

## Setup

### Prerequisites

```bash
pip install aiohttp websockets
export AGENTCALL_API_KEY="ak_ac_your_key"
```

### For Agent Framework Developers

1. Copy `SKILL-FRAGMENT.md` to your skills directory as `SKILL.md`:
   ```bash
   # For Claude Code:
   cp SKILL-FRAGMENT.md ~/.claude/skills/voice-meeting/SKILL.md
   cp bridge.py ~/.claude/skills/voice-meeting/scripts/bridge.py

   # For GitHub Copilot:
   cp SKILL-FRAGMENT.md .github/skills/voice-meeting/SKILL.md

   # For Cursor / Windsurf / others:
   cp SKILL-FRAGMENT.md .agents/skills/voice-meeting/SKILL.md
   ```

2. The agent discovers the skill from the `description` field in the frontmatter
3. When the user shares a meeting URL, the agent spawns `bridge.py` as a subprocess
4. Events arrive on stdout, commands go via stdin

### For Testing Manually

```bash
# In one terminal, run the bridge:
python bridge.py "https://meet.google.com/abc-def-ghi" --name "Claude"

# In another terminal, simulate the agent:
echo '{"command": "tts.speak", "text": "Hello!"}' > /proc/<PID>/fd/0

# Or pipe commands:
echo '{"command": "tts.speak", "text": "Hello!"}' | python bridge.py "https://meet.google.com/abc"
```

## VAD Gap Buffering

### The Problem

Speech-to-text splits long utterances into multiple `transcript.final` events:

```
User says: "Can you check the health endpoint and also the database connection"

STT produces:
  transcript.final: "Can you check the health endpoint"     (1s pause)
  transcript.final: "and also the database connection"       (silence)
```

Without buffering, the agent sees two separate instructions instead of one.

### The Solution

The bridge buffers `transcript.final` events and waits for a silence gap:

```
transcript.final arrives → start 2s timer
  ↓
transcript.partial arrives within 2s?
  YES → user still speaking, reset timer, keep buffering
  NO  → 2s of silence, user is done speaking
        → combine all buffered finals into one user.message
        → emit to agent
```

### Configuration

```bash
# Default: 2 seconds (good for most speakers)
python bridge.py "https://meet.google.com/abc"

# Slow speakers or complex instructions: increase to 3-4s
python bridge.py "https://meet.google.com/abc" --vad-timeout 3.5

# Fast back-and-forth conversation: decrease to 1-1.5s
python bridge.py "https://meet.google.com/abc" --vad-timeout 1.0
```

## Chat Messages

### Why Chat?

Some information is hard to speak aloud:
- URLs: "https://api.agentcall.dev/v1/payments/webhook" sounds terrible via TTS
- Code: `func (s *Session) broadcastEvent(data json.RawMessage)` is unreadable
- Emails, file paths, JSON, error messages

### Receiving Chat

When the user sends a message in the meeting chat, the bridge emits:

```json
{"event": "chat.received", "sender": "John", "message": "here's the error: TypeError: cannot read property 'length' of null"}
```

The agent can process this as text input — great for pasting error messages, logs, or code.

### Sending Chat

The agent can send text to the meeting chat:

```json
{"command": "send_chat", "message": "Here's the deployment URL: https://agentcall.dev"}
```

Combine with voice: the agent speaks "I'll put the URL in chat" and sends the actual URL via chat.

## Raise Hand

In group meetings (more than 2 people), the agent can raise the bot's hand before speaking:

```json
{"command": "raise_hand"}
```

This signals to the group that the bot has something to say. In 1-on-1 calls this isn't needed.

## Available TTS Voices

| Voice ID | Name | Gender | Language |
|----------|------|--------|----------|
| `af_heart` | Heart | Female | en-us |
| `af_bella` | Bella | Female | en-us |
| `af_sarah` | Sarah | Female | en-us |
| `am_adam` | Adam | Male | en-us |
| `am_michael` | Michael | Male | en-us |
| `bf_emma` | Emma | Female | en-gb |
| `bm_george` | George | Male | en-gb |

Full list of 54 voices across 9 languages: `GET /v1/tts/voices`

## Billing

| Component | Charged? | Notes |
|-----------|----------|-------|
| Meeting bot (base) | Yes | Per minute of call |
| Speech-to-text | Yes | Per minute (needed to hear the user) |
| Voice intelligence | **No** | Direct mode — no GetSun needed |
| Text-to-speech | Yes | Per minute of generated audio |
| External LLM | **No** | The agent framework IS the LLM |

This is cheaper than collaborative mode because there's no voice intelligence charge. The agent framework handles all the intelligence.

## Why This Pattern Matters

### No separate LLM
Every other example in this repo uses a separate LLM call (Claude API, GPT-4o, Gemini). This example uses **none**. The agent framework that spawns the bridge IS the LLM — with full project context already loaded.

### No context loading
The agent doesn't need to read memory files, git logs, or project structure. It already has all that context from the current coding session. The meeting transcript is just another input.

### Same capabilities
During the voice call, the agent can:
- Read and explain code ("walk me through session.go")
- Edit files ("add error handling to the webhook")
- Run commands ("check if the server is running")
- Search the codebase ("find where we handle payments")
- Check git status, create commits, push to remote
- Everything it could do via text, now via voice

### Seamless switching
The developer can switch between text and voice mid-session. Start typing, switch to voice for brainstorming, switch back to text for precise code changes. Same session throughout.

## Extending

### Add screen sharing
Use `webpage-av` mode instead of `audio` to give the bot a visual presence. The bot could show its current activity (file being edited, terminal output) as its video feed.

### Add recording
Set `audio_streaming: true` in the call creation to also capture raw audio. Save the meeting audio alongside the transcript for records.

### Multi-agent meetings
Multiple AI agents could join the same meeting, each with different specialties. One handles code, one handles documentation, one handles deployment. Each is a separate bridge instance connected to a different agent framework.

### Voice commands
Add special voice commands that trigger specific actions:
- "Screenshot the meeting" → `screenshot.take`
- "Share my screen" → `screenshare.start`
- "Mute yourself" → `leave` (no mute command, but leave works)
