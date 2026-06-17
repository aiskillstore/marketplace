# Crash Recovery Guide

## What Happens When Your Agent Crashes

When an agent process crashes mid-call:
1. The meeting bot keeps running (FirstCall (meeting infrastructure) manages it independently)
2. GetSun (collaborative voice intelligence) keeps running (if collaborative)
3. The tunnel stays open (if webpage mode)
4. Events continue but nobody receives them (agent is disconnected)
5. The call ends only when FirstCall (meeting infrastructure) timeouts trigger (alone_timeout, silence_timeout)

## Recovery Flow

```
Agent crashes
    |
    v
Agent restarts
    |
    +-- 1. Check .agentcall-state.json (has call_id + timestamp)
    |      -> If expired (>24h), skip recovery
    |
    +-- 2. GET /v1/calls/{call_id} -> verify call still active
    |      -> If ended/error, clean up state file
    |
    +-- 3. Reconnect WebSocket: wss://api.agentcall.dev/v1/calls/{call_id}/ws
    |
    +-- 4. Receive call.state snapshot (enriched):
    |      {call_id, status, mode, bot_name, voice_strategy,
    |       created_at, participants, active_speaker}
    |
    +-- 5. Send {"type": "events.replay"} to request missed events
    |      -> Receive {"event": "events.replay", "count": N, "events": [...]}
    |      -> Contains last 200 events or 5 minutes (whichever is less)
    |      -> Only state-changing events (transcript.final, participant.joined/left,
    |        voice.state, chat.message, etc.)
    |      -> NOT transient events (transcript.partial, audio.chunk, tts.webpage_audio)
    |
    +-- 6. (Optional) GET /v1/calls/{call_id}/transcript
    |      -> Full transcript for complete history
    |
    +-- 7. Resume normal operation
```

## Event Replay

After reconnecting, the agent can request missed events:

```python
# After WebSocket reconnects and call.state is received:
await client.send_command({"type": "events.replay"})

# Server responds with buffered events:
# {"event": "events.replay", "count": 12, "events": [
#   {"type": "participant.joined", "participant": {"name": "Alice"}, ...},
#   {"type": "transcript.final", "text": "Let's start", "speaker": {"name": "Alice"}, ...},
#   {"type": "transcript.final", "text": "June, pull up the Q3 data", ...},
#   {"event": "voice.state", "state": "thinking"},
#   ...
# ]}
```

**What's included in replay:**
- transcript.final (completed utterances)
- participant.joined / participant.left
- voice.state / voice.text (collaborative mode)
- chat.message
- call.bot_ready / call.ended / call.transcript_ready
- call.tunnel_ready / call.bot_joining / call.bot_waiting_room
- call.credits_low / call.degraded / call.recovered

**What's NOT included (transient/streaming events):**
- transcript.partial (stale partials are meaningless)
- audio.chunk (too large, already played)
- tts.webpage_audio (already played)
- tts.audio_clear (transient signal)
- active_speaker (only latest matters — included in call.state)
- command.ack / command.error (agent-specific)

## Deduplication

The replay buffer may contain events the agent already received before crashing. The agent should deduplicate:

**By timestamp:**
```python
last_event_time = None  # track the last event timestamp before crash

async def handle_replay(replay_msg):
    events = replay_msg.get("events", [])
    for event in events:
        # Skip events we already processed before crash
        event_time = event.get("timestamp")
        if event_time and last_event_time and event_time <= last_event_time:
            continue
        
        # Process the missed event
        await process_event(event)
```

**By event content (simpler):**
```python
seen_events = set()  # store hashes of recent events

async def handle_replay(replay_msg):
    events = replay_msg.get("events", [])
    for event in events:
        # Simple dedup: hash the event JSON
        event_hash = hash(json.dumps(event, sort_keys=True))
        if event_hash in seen_events:
            continue
        seen_events.add(event_hash)
        await process_event(event)
```

**Simplest approach (recommended):**
```python
# Just process all replay events. Most agents are idempotent for
# transcript.final (adding to a list) and participant events.
# Duplicate processing is harmless.

async def handle_replay(replay_msg):
    for event in replay_msg.get("events", []):
        await process_event(event)  # same handler as live events
```

For most agents, duplicates are harmless — adding the same transcript entry twice to a list, or re-processing a participant.joined for someone already tracked. The simplest approach is to just process everything.

## State File

The state file `.agentcall-state.json` is saved in the working directory:

```json
{
  "call_id": "call-abc123",
  "meet_url": "https://meet.google.com/xyz",
  "mode": "audio",
  "created_at": "2026-04-01T12:00:00.000Z"
}
```

- Created when a new call starts
- Checked on agent startup for recovery
- **Expires after 24 hours** — stale state is ignored
- Deleted on normal exit (SIGINT/SIGTERM)
- If agent crashes (SIGKILL), file persists for recovery

## Full Recovery Example (Python)

```python
import asyncio
import json
from agentcall import AgentCallClient

async def main():
    client = AgentCallClient(api_key="ak_ac_xxx")
    
    # Step 1: Check for existing state
    state = load_state()  # reads .agentcall-state.json
    
    if state and not is_expired(state):
        # Step 2: Verify call is still active
        try:
            call = await client.get_call(state["call_id"])
            if call["status"] in ("ended", "error"):
                cleanup_state()
                state = None
        except:
            cleanup_state()
            state = None
    
    if state:
        call_id = state["call_id"]
        print(f"Recovering call {call_id}")
    else:
        # Create new call
        call = await client.create_call(
            meet_url="https://meet.google.com/abc",
            mode="audio",
            voice_strategy="collaborative",
            # ...
        )
        call_id = call["call_id"]
        save_state(call_id)
    
    # Step 3: Connect WebSocket
    recovering = state is not None
    
    async for event in client.connect_ws(call_id):
        event_type = event.get("event") or event.get("type", "")
        
        # Step 4: On connect, receive call.state automatically
        if event_type == "call.state":
            print(f"Status: {event['status']}")
            print(f"Participants: {event.get('participants', [])}")
            print(f"Active speaker: {event.get('active_speaker')}")
            
            # Step 5: Request replay if recovering
            if recovering:
                await client.send_command({"type": "events.replay"})
                recovering = False
            continue
        
        # Step 5b: Handle replay response
        if event_type == "events.replay":
            count = event.get("count", 0)
            print(f"Replaying {count} missed events")
            for missed in event.get("events", []):
                await process_event(missed)
            continue
        
        # Normal event processing
        await process_event(event)
        
        if event_type == "call.ended":
            break


async def process_event(event):
    event_type = event.get("event") or event.get("type", "")
    
    if event_type == "transcript.final":
        print(f"[{event['speaker']['name']}] {event['text']}")
    elif event_type == "participant.joined":
        print(f"+ {event['participant']['name']} joined")
    elif event_type == "participant.left":
        print(f"- {event['participant']['name']} left")
    # ... handle other events


asyncio.run(main())
```

## Limitations

- **Server restart**: If the AgentCall server restarts, sessions are lost. The agent gets HTTP 410 on WS reconnect. The meeting bot continues but cannot be controlled until the call ends naturally.
- **Replay window**: Only last 200 events or 5 minutes. If agent was down longer, use the transcript API for full history.
- **No streaming data replay**: Audio chunks, partial transcripts, and TTS audio are NOT replayed (too large, stale).
- **Single machine**: State file is local. If agent moves to a different machine, recovery won't find the state file.
