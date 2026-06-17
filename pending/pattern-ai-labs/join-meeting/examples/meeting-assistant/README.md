# Simple Meeting Assistant (Collaborative Mode)

An AI meeting assistant that joins with an animated avatar, listens to the conversation, and answers when someone says its name. No LLM needed — GetSun (collaborative voice intelligence) handles everything autonomously using the meeting transcript as memory.

## What It Does

1. Joins meeting in **webpage-av** mode with the **avatar** UI template
2. GetSun (collaborative voice intelligence) listens to all transcripts automatically
3. When someone says a trigger word ("Juno", "Zuno", "Assistant"), GetSun responds
4. GetSun answers from what it has heard in the meeting so far
5. Avatar shows voice states: listening, thinking, speaking, interrupted
6. Agent just logs events and saves a meeting log when done

## What the Agent Does vs What's Automatic

### Automatic (agent does nothing)
- Transcripts forwarded to GetSun (collaborative voice intelligence) → it hears everything
- Trigger word detection → GetSun knows when it's being addressed
- Barge-in prevention → GetSun waits for silence before speaking
- Interruption handling → GetSun stops immediately if someone talks over it
- TTS audio → routed to the avatar webpage → plays through meeting
- Avatar visual states → updates automatically on voice.state events

### Agent's job
- Create the call with collaborative config
- Stay connected via WebSocket (keeps the session alive)
- Log events (optional — for post-meeting notes)

## Setup

```bash
pip install requests websockets
export AGENTCALL_API_KEY="ak_ac_your_key"
python assistant.py "https://meet.google.com/abc-def-ghi"
```

## Usage

```bash
# Default: "Juno" responds to "juno", "zuno", "assistant"
python assistant.py "https://meet.google.com/abc-def-ghi"

# Custom name and trigger words
python assistant.py "https://meet.google.com/abc" --name "Aria" --triggers "aria,hey aria"

# Custom voice (GetSun voices: voice.heart, voice.bella, voice.echo, voice.eric)
python assistant.py "https://meet.google.com/abc" --voice voice.bella

# Custom persona
python assistant.py "https://meet.google.com/abc" --context "You are a financial analyst. Answer with data and numbers."

# Custom output file
python assistant.py "https://meet.google.com/abc" --output standup-log.md
```

## Example Session

```
Creating meeting assistant:
  Bot name: Juno
  Trigger words: ['juno', 'zuno', 'assistant']
  Voice: voice.heart
  Mode: webpage-av (avatar visible)
  Strategy: collaborative (autonomous voice intelligence)

Call created: call-550e8400...
Bot is in the meeting with avatar visible.
Say the trigger word to ask a question.

  + Alice joined
  + Bob joined
  👂 Voice state: listening
  [Alice] Let's review the Q3 numbers. Revenue was 2.4 million.
  [Bob] And enterprise was the biggest segment at 1.6 million.
  [Alice] Hey Juno, what was the total revenue we just discussed?
  🎯 Voice state: actively_listening
  🧠 Voice state: thinking
  ⏳ Voice state: waiting_to_speak
  🗣️ Voice state: speaking
  💬 Bot says: "Based on what was discussed, total Q3 revenue was 2.4 million, with enterprise contributing 1.6 million."
  🔊 TTS started
  🔇 TTS done
  👂 Voice state: listening
  [Bob] What about the--
  🛑 Voice state: interrupted
  [Bob] What about the growth rate?
  🎯 Voice state: actively_listening
  🧠 Voice state: thinking
  🗣️ Voice state: speaking
  💬 Bot says: "I haven't heard a specific growth rate mentioned in this meeting yet."
  👂 Voice state: listening

Call ended: left
Meeting log saved to: meeting-log-2026-04-03-1430.md
```

## Avatar Voice States

The avatar template shows these visual states automatically:

| State | Visual | Meaning |
|-------|--------|---------|
| listening | Subtle gray pulse | Default — hearing the conversation |
| actively_listening | Blue glow | Trigger word detected, capturing the question |
| thinking | Purple spin | Processing a response |
| waiting_to_speak | Gold pulse | Response ready, waiting for silence |
| speaking | Green glow + wave | Speaking via TTS |
| interrupted | Red flash | Someone talked over the bot, stopped |
| contextually_aware | Teal glow | Background context update |

## Billing

| Component | Charged? | Notes |
|-----------|----------|-------|
| Meeting bot (base) | Yes | Per minute of call |
| Speech-to-text | Yes | Per minute (transcripts needed) |
| Voice intelligence | Yes | Collaborative mode uses GetSun |
| Text-to-speech | Yes | Per minute of audio generated |
| External LLM | **No** | Not needed — GetSun uses meeting memory |

## Collaborative Config

```json
{
  "trigger_words": ["juno", "zuno", "assistant"],
  "barge_in_prevention": true,
  "interruption_use_full_text": true,
  "context": "You are Juno, a helpful meeting assistant...",
  "voice": "voice.heart"
}
```

| Field | Purpose |
|-------|---------|
| `trigger_words` | Words that activate the bot (case-insensitive) |
| `barge_in_prevention` | Wait for silence before speaking (prevents talking over people) |
| `interruption_use_full_text` | Use the full interrupted sentence for smarter recovery |
| `context` | Persona and instructions for how the bot should behave |
| `voice` | GetSun voice: `voice.heart`, `voice.bella`, `voice.echo`, `voice.eric` |

## Extending This Example

This is the simplest collaborative assistant — GetSun answers from meeting memory alone. To make it smarter:

### Add external knowledge (voice.context_update)
```python
# When you detect a question about external data:
await ws.send(json.dumps({
    "command": "voice.context_update",
    "text": "Q3 revenue breakdown: Enterprise $1.6M, SMB $600K, Consumer $200K"
}))
# Then force a response with the new context:
await ws.send(json.dumps({
    "command": "trigger.speak",
    "text": original_question,
    "speaker": speaker_name
}))
```

### Proactively inject information (voice.inject)
```python
# Agent can inject data without waiting for a question:
await ws.send(json.dumps({
    "command": "inject.natural",
    "text": "Meeting is at the 45 minute mark. 3 action items captured so far.",
    "priority": "normal"
}))
```

### Add LLM for smarter context
Instead of relying only on meeting memory, use an LLM to:
- Detect when external data is needed
- Query databases/APIs
- Format context for GetSun (collaborative voice intelligence)
- Decide when to proactively contribute

See the [Customer Support Agent](../support-agent/) example for LLM integration patterns.
