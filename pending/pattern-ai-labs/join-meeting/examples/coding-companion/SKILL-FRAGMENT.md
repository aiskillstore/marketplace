---
name: voice-meeting
description: >
  Join a Google Meet, Zoom, or Teams meeting to talk with the user via voice
  instead of text. Use when the user shares a meeting URL and wants to discuss
  via voice call. Transcripts arrive as user.message events on stdout. Respond
  by writing tts.speak commands to stdin. You can also send and read chat
  messages, raise hand, and leave the call. Your existing session context is
  used — no separate LLM or context loading needed.
argument-hint: <meeting-url> [--name <bot-name>] [--voice af_heart] [--vad-timeout 2.0]
user-invocable: true
---

# Voice Meeting — Talk to the user via a meeting call

Join a meeting as an AI bot with voice. The user speaks, you hear transcripts.
You speak back via TTS. Same session, same context — voice is just another I/O channel.

## When to Use

Use this skill when:
- The user shares a meeting link and asks you to join
- The user says "let's discuss this on a call" or "join the meeting"
- The user wants to switch from text to voice conversation
- The user wants to pair-program or brainstorm via voice

## Quick Start

```bash
# Spawn the bridge as a subprocess (bridge.py is in scripts/python/)
python scripts/python/bridge.py "https://meet.google.com/abc-def-ghi" --name "Claude" --voice af_heart
```

Requires: `pip install aiohttp websockets` and an AgentCall API key.
The key is read from `~/.agentcall/config.json` (persists across sessions) or
`AGENTCALL_API_KEY` env var. If neither exists, ask the user for their key
(get one at https://app.agentcall.dev/api-keys) and save it:
```bash
mkdir -p ~/.agentcall && echo '{"api_key": "KEY_HERE"}' > ~/.agentcall/config.json
```

## Protocol

Communication is via stdin/stdout, one JSON object per line.

### Events you receive (stdout)

| Event | Fields | When |
|-------|--------|------|
| `call.created` | `call_id`, `status` | Call created, bot joining meeting |
| `call.bot_ready` | `call_id` | Bot is in the meeting, ready |
| `participant.joined` | `name` | A person joined the meeting |
| `participant.left` | `name` | A person left the meeting |
| `greeting.prompt` | `participant`, `hint` | First person joined — greet them and introduce yourself |
| `user.message` | `speaker`, `text` | User finished speaking (VAD-buffered, complete utterance) |
| `chat.received` | `sender`, `message` | User sent a text message in meeting chat |
| `tts.done` | | Your TTS finished playing — you can speak again |
| `tts.error` | `reason` | TTS failed |
| `call.ended` | `reason` | Call is over |
| `error` | `message` | Something went wrong |

### Commands you send (stdin)

| Command | Fields | What it does |
|---------|--------|-------------|
| `tts.speak` | `text`, `voice` (optional), `speed` (optional) | Speak text in the meeting via TTS |
| `send_chat` | `message` | Send a text message in the meeting chat |
| `raise_hand` | | Raise the bot's hand in the meeting |
| `leave` | | Gracefully leave the meeting |

### Example stdin/stdout exchange

```
← stdout: {"event": "call.bot_ready", "call_id": "call-abc123"}
← stdout: {"event": "participant.joined", "name": "John"}
← stdout: {"event": "greeting.prompt", "participant": "John", "hint": "John joined. Introduce yourself and greet them via tts.speak. Active participation is the default — do not stay silent."}

→ stdin:  {"command": "tts.speak", "text": "Hey John! I'm here. What would you like to work on?"}

← stdout: {"event": "tts.done"}
← stdout: {"event": "user.message", "speaker": "John", "text": "Can you check if the health endpoint is responding?"}

(You run: curl https://api.agentcall.dev/health → {"status":"ok"})

→ stdin:  {"command": "tts.speak", "text": "Health endpoint returned status OK. Everything is running."}

← stdout: {"event": "tts.done"}
← stdout: {"event": "user.message", "speaker": "John", "text": "Great. Can you send me the deployment URL in chat?"}

→ stdin:  {"command": "send_chat", "message": "https://agentcall.dev"}
→ stdin:  {"command": "tts.speak", "text": "I've sent the URL in the chat."}

← stdout: {"event": "tts.done"}
← stdout: {"event": "user.message", "speaker": "John", "text": "Thanks, let's end the call"}

→ stdin:  {"command": "tts.speak", "text": "Sounds good. Talk to you later!"}
→ stdin:  {"command": "leave"}

← stdout: {"event": "call.ended", "reason": "left"}
```

## Important Notes

### user.message is VAD-buffered
The bridge waits for a silence gap (default 2 seconds) after the last transcript.final
before emitting a user.message. This means you receive complete utterances, not fragments.
If the user speaks slowly with pauses, all their words are combined into one message.
Adjust with `--vad-timeout` (higher for slow speakers, lower for fast speakers).

### Wait for tts.done before speaking again
After sending tts.speak, wait for the tts.done event before sending another tts.speak.
If you send multiple tts.speak commands without waiting, they will queue up and play
in sequence, which may sound unnatural.

### Bot's own speech is filtered
The bridge filters out transcripts from the bot itself (by matching the bot name).
You will not receive your own TTS output as a user.message. You also won't receive
transcripts while the bot is actively speaking (is_speaking flag).

### Chat for text that's hard to speak
Use send_chat for: URLs, code snippets, email addresses, file paths, JSON, or any
text that would sound wrong spoken aloud. You can tell the user "I'll put that in chat"
and send it via send_chat.

### The call can end in two ways
1. You send `{"command": "leave"}` — you chose to end the call
2. You receive `{"event": "call.ended", "reason": "..."}` — the user or meeting ended it

Reasons include: `left` (user left), `meeting_ended`, `alone_timeout` (bot was alone too long),
`silence_timeout`, `max_duration`, `error`.

### MANDATORY post-call cleanup (4 steps, in order)
After `call.ended`, or when you chose to end the call, do ALL of these:
1. **Send `{"command": "leave"}`** — only if YOU are ending (user said bye).
   Skip if `call.ended` already arrived. Wait for `tts.done` first if you just spoke.
2. **Kill the bridge subprocess** (SIGTERM, wait 2-3s, SIGKILL if needed).
   Closing stdin/stdout is NOT enough — the WS stays open.
3. **Kill agent-spawned HTTP servers** (screenshare, webpage.open, custom avatar).
   Track the PID when you spawn; `kill $PID`. Don't lsof-sweep.
4. **Verify via API** — `GET /v1/calls/{id}`; if status isn't `ended` or `error`,
   `DELETE /v1/calls/{id}`. Catches rare silent backend transaction conflicts.

Skipping risks orphan bots consuming credits (up to your plan's max_duration).
See the main `SKILL.md` Pattern 5 for the full snippet with jq/grep examples.

### Raise hand in group meetings
If multiple people are in the meeting, use raise_hand before speaking to signal you
have something to say. This is optional in 1-on-1 calls.

### Active participation is the default
You are an active meeting participant. When `greeting.prompt` fires, introduce yourself
and greet the participant. Respond to questions, contribute to discussions, and
acknowledge when you're working on something. Do NOT stay silent — silence is the
worst user experience. Only use passive/notetaker mode if the user explicitly asks
for it (e.g., "just take notes", "don't speak", "silent mode").

### Claude Code: Stop Hook (recommended)
If you are Claude Code, add this Stop Hook to `.claude/settings.json` to prevent
exiting mid-call. This ensures you stay in the CALL_LOOP until `call.ended`:
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
