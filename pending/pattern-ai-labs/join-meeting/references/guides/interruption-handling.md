# Interruption Handling Guide

How to handle interruptions in AgentCall so the bot stops talking when someone speaks.

## Why Interruption Handling Matters

- Without it, the bot talks over people — terrible UX in meetings
- Different modes have different interruption mechanisms
- **Collaborative mode**: GetSun (collaborative voice intelligence) handles it automatically via `text.partial`
- **Direct mode**: the agent must handle it (or use VAD on the webpage)

---

## Interruption in Collaborative Mode (Automatic)

In collaborative mode, GetSun (collaborative voice intelligence) detects and handles interruptions for you:

```
Person starts talking -> FirstCall (meeting infrastructure) sends transcript.partial
  -> AgentCall forwards to GetSun (collaborative voice intelligence) as text.partial
  -> GetSun (collaborative voice intelligence) detects interruption -> sends audio.interrupted
  -> Server sends:
       audio mode: audio.clear to FirstCall (meeting infrastructure)
       webpage mode: tts.audio_clear to webpage
  -> Bot stops talking
  -> GetSun (collaborative voice intelligence) evaluates what was said -> decides: respond or listen
```

The agent receives `voice.state: "interrupted"`. No action needed — GetSun (collaborative voice intelligence) handles everything.

---

## Interruption in Direct Mode

**Important:** FirstCall does NOT transcribe bot audio. All `transcript.partial` and
`transcript.final` events are always from human participants. This means any transcript
event during bot speech is a real interruption signal — not echo.

### Approach 0: Automatic (webpage modes 2-4) — RECOMMENDED

In webpage modes, `agentcall-audio.js` handles interruption automatically:
- When `transcript.partial` arrives while audio is playing → audio is cleared immediately
- The `tts.interrupted` event is sent back through WebSocket with sentence tracking info
- The bridge script forwards it to the agent as:
  `{"event": "tts.interrupted", "reason": "user_speaking", "sentence_index": 1, "elapsed_ms": 800}`
- The agent knows which sentence was interrupted and can decide how to respond

**No code needed** — this works out of the box with all built-in templates (orb, avatar,
dashboard, blank, voice-agent). If you build a custom webpage, include `agentcall-audio.js`
and wire the `onInterrupted` callback to send `tts.interrupted` back through the WebSocket.

### Approach 1: Simple — Check transcript.partial Before Speaking (audio mode)

```python
# Before sending tts.speak, check if someone is talking
if recent_transcript_partial and time.time() - last_partial_time < 2:
    # Someone is talking, don't speak yet
    return
await client.send_command({"type": "tts.speak", "text": response})
```

### Approach 2: Sentence Tracking — Know What Was Interrupted

Each `tts.webpage_audio` event includes metadata:
```json
{
  "event": "tts.webpage_audio",
  "data": "base64...",
  "sentence_index": 0,
  "sentence_text": "Q3 revenue was 2.4 million.",
  "duration_ms": 2100
}
```

When interrupted (via VAD or `tts.audio_clear`), the page can report:
```json
{
  "type": "tts.interrupted",
  "sentence_index": 1,
  "elapsed_ms": 800
}
```

The agent knows: sentence 0 completed, sentence 1 was cut at 800ms, sentences 2+ never played.

### Approach 3: VAD on Webpage (Best Accuracy)

Use Silero VAD in the browser to detect when someone is talking:
- Monitors audio input from the meeting
- When speech detected, clear audio queue and notify the agent
- Works in all webpage modes

---

## Silero VAD Integration (Detailed)

### What is Silero VAD?

Voice Activity Detection model (~1.5MB ONNX). Runs in the browser via ONNX Runtime Web. Detects whether audio contains speech. Used to know when a meeting participant is talking.

### Why Use It?

- More accurate than checking `transcript.partial` (detects speech before STT processes it)
- Works even when STT is disabled
- Sub-100ms detection latency
- Runs locally in the browser — no external API calls

### When to Use

- Direct mode with webpage (no GetSun (collaborative voice intelligence) for interruption)
- When low-latency interruption is important (customer support, real-time conversations)
- When you need to detect speech even without transcription enabled

### When NOT Needed

- Collaborative mode (GetSun (collaborative voice intelligence) handles it)
- Audio mode (no webpage — use `transcript.partial` for basic detection)
- Silent observer mode (bot never speaks)

### Implementation

**Step 1: Add ONNX Runtime Web + Silero VAD model**

```html
<script src="https://cdn.jsdelivr.net/npm/onnxruntime-web@1.17.0/dist/ort.min.js"></script>
```

Download `silero_vad.onnx` (~1.5MB) from https://github.com/snakers4/silero-vad

**Step 2: Set up audio capture + VAD**

```javascript
// Capture audio from the browser (meeting audio from FirstCall (meeting infrastructure))
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const audioCtx = new AudioContext({ sampleRate: 16000 });
const source = audioCtx.createMediaStreamSource(stream);
const processor = audioCtx.createScriptProcessor(512, 1, 1);

// Load Silero VAD model
const session = await ort.InferenceSession.create('silero_vad.onnx');
let h = new Float32Array(64).fill(0);
let c = new Float32Array(64).fill(0);

processor.onaudioprocess = async (e) => {
  const input = e.inputBuffer.getChannelData(0);
  
  // Run VAD inference
  const inputTensor = new ort.Tensor('float32', input, [1, input.length]);
  const hTensor = new ort.Tensor('float32', h, [2, 1, 64]);
  const cTensor = new ort.Tensor('float32', c, [2, 1, 64]);
  const srTensor = new ort.Tensor('int64', BigInt64Array.from([16000n]), []);
  
  const result = await session.run({
    input: inputTensor, h: hTensor, c: cTensor, sr: srTensor
  });
  
  h = result.hn.data;
  c = result.cn.data;
  const speechProb = result.output.data[0];
  
  if (speechProb > 0.5) {
    onSpeechDetected();
  }
};

source.connect(processor);
processor.connect(audioCtx.destination);

function onSpeechDetected() {
  // Someone is talking in the meeting — stop bot audio
  audioPlayer.clear();
  
  // Optionally notify agent
  ws.send(JSON.stringify({
    type: 'tts.interrupted',
    sentence_index: audioPlayer.currentSentenceIndex || 0,
    reason: 'vad_speech_detected'
  }));
}
```

**Step 3: Connect to AgentCallAudio**

```javascript
const audioPlayer = new AgentCallAudio({
  onStateChange: (playing) => {
    // Only run VAD when bot is playing audio (save CPU)
    if (playing) startVAD();
    else stopVAD();
  }
});
```

### Important Notes

- VAD detects ALL speech, including the bot's own TTS output. To avoid false positives, only run VAD when the bot is playing audio AND the detected speech is from a different source. One approach: compare the energy of the detected speech against expected TTS energy.
- Alternative: use the `active_speaker` event from FirstCall (meeting infrastructure) instead of raw VAD. If `active_speaker` is not the bot, someone else is talking.
- The simplest reliable approach: combine `transcript.partial` (someone started talking) + `active_speaker` (someone is talking) as interruption signals, and use VAD only as a faster first-pass detector.

---

## Resume vs New Response (Agent Decision)

When the agent is notified of an interruption, it has full context:
- Which sentence was playing (`sentence_index`)
- How far into that sentence (`elapsed_ms`)
- What the interruptor said (`transcript.final` arrives shortly after)

### Pattern 1: Resume From Where Stopped

```python
async def handle_interruption(interrupted_event, transcript_event):
    interrupted_idx = interrupted_event["sentence_index"]
    interruptor_text = transcript_event["text"]
    
    # Check if it's a brief interruption ("uh huh", "right", "ok")
    if is_backchannel(interruptor_text):
        # Brief acknowledgment — resume from interrupted sentence
        remaining = original_sentences[interrupted_idx:]
        for sentence in remaining:
            await client.send_command({
                "type": "tts.speak", "text": sentence
            })
        return
    
    # It was a real interruption — generate new response
    handle_new_question(interruptor_text)
```

### Pattern 2: Always Generate Fresh Response

```python
async def handle_interruption(interrupted_event, transcript_event):
    # Don't resume — always respond to what was said
    response = await generate_response(transcript_event["text"])
    await client.send_command({"type": "tts.speak", "text": response})
```

### Pattern 3: Smart Routing

```python
async def handle_interruption(interrupted_event, transcript_event):
    text = transcript_event["text"]
    
    if is_follow_up(text, current_topic):
        # Related to what bot was saying — answer the follow-up
        context = f"I was saying: {get_completed_text(interrupted_idx)}. They asked: {text}"
        response = await generate_response(context)
    elif is_correction(text):
        # "No, I meant Q2 not Q3" — correct and re-answer
        response = await generate_corrected_response(text)
    elif is_new_topic(text):
        # Completely different topic — switch
        response = await generate_response(text)
    else:
        # Brief interruption — resume
        remaining = original_sentences[interrupted_idx:]
        for s in remaining:
            await client.send_command({"type": "tts.speak", "text": s})
        return
    
    await client.send_command({"type": "tts.speak", "text": response})
```
