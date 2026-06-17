# Simple Note-Taker Bot

Joins a meeting, records who said what, and saves the transcript to a markdown file.

## What It Does

1. Creates a call in **audio mode** (voice-only, cheapest)
2. Connects via WebSocket to receive real-time transcript events
3. Prints each utterance as it happens: `[Alice] Let's discuss Q3 numbers`
4. When the meeting ends, fetches the full transcript from the API
5. Saves everything to `meeting-notes-YYYY-MM-DD-HHMM.md`

## Billing

Only two components are charged (no voice intelligence or TTS):
- **Meeting bot** — per minute of call
- **Speech-to-text** — per minute of call

## Setup

### Python

```bash
pip install requests websockets
export AGENTCALL_API_KEY="ak_ac_your_key"
python notetaker.py "https://meet.google.com/abc-def-ghi"
```

### Node.js

```bash
npm install ws
export AGENTCALL_API_KEY="ak_ac_your_key"
node notetaker.js "https://meet.google.com/abc-def-ghi"
```

### Options

```bash
# Custom bot name (default: "Notetaker")
python notetaker.py "https://meet.google.com/abc-def-ghi" --name "Scribe"
node notetaker.js "https://meet.google.com/abc-def-ghi" --name "Scribe"
```

## Output

```markdown
# Meeting Notes — 2026-04-03 14:30

## Participants
- Alice, Bob

## Transcript
[14:30:12] Alice: Let's discuss the Q3 roadmap
[14:30:45] Bob: I think we should focus on mobile first
[14:31:02] Alice: Agreed. What about the API timeline?
...

## Meeting Info
- Call ID: call-550e8400...
- Duration: 32 minutes
- End reason: left
- Total utterances: 47
```

## How It Works

```
Your script                    AgentCall API
    |                               |
    |-- POST /v1/calls ------------>|  audio mode, transcription: true
    |<-- {call_id, ws_url} ---------|
    |                               |
    |-- WS connect ---------------->|
    |<-- transcript.final ----------|  real-time transcripts
    |<-- transcript.final ----------|
    |<-- call.ended ----------------|
    |                               |
    |-- GET /v1/calls/{id}/transcript  fetch full transcript
    |<-- {entries, duration} -------|
    |                               |
    |-- Save to .md file            |
```
