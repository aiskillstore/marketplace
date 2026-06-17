# Webpage Audio — How Audio Works in Webpage Modes

In webpage modes (`webpage-audio`, `webpage-av`, `webpage-av-screenshare`), the bot's audio doesn't go directly to the meeting. Instead, audio is routed to your webpage, which plays it through the browser — and FirstCall (meeting infrastructure) captures the browser's audio output into the meeting.

This guide explains why this matters, how to handle it, and what happens during interruptions.

## Why Audio Routing Differs by Mode

### Audio Mode (simple)
```
AgentCall TTS/GetSun (collaborative voice intelligence) generates audio (24kHz)
    → Server resamples to 16kHz
    → Server sends audio.send to FirstCall (meeting infrastructure)
    → FirstCall (meeting infrastructure) plays it in the meeting
```
The server handles everything. Your agent doesn't touch audio.

### Webpage Modes (your page plays audio)
```
AgentCall TTS/GetSun (collaborative voice intelligence) generates audio (24kHz)
    → Server sends tts.webpage_audio event to your webpage
    → Your webpage decodes + plays via Web Audio API
    → FirstCall (meeting infrastructure) captures browser audio output
    → Meeting participants hear it
```
**Your webpage is responsible for playing the audio.** If your page doesn't play it, nobody hears anything.

### Why This Architecture?

In webpage modes, FirstCall (meeting infrastructure) loads your webpage in the rendering environment. It captures:
- **Video**: whatever renders on the page (canvas, HTML, video elements)
- **Audio**: whatever the page plays (Web Audio API, `<audio>` tags, etc.)

This means your page controls both what participants see AND hear. This is powerful — you can:
- Synchronize audio with visual animations (lip-sync avatars)
- Apply audio effects (reverb, pitch shift)
- Mix multiple audio sources (TTS + background music)
- Control volume levels programmatically

But it also means your page must actively play the audio chunks it receives.

---

## The Audio Events

### `tts.webpage_audio` — Play This Audio

Sent when GetSun (collaborative voice intelligence) or AgentCall TTS generates audio for your webpage to play.

```json
{
  "event": "tts.webpage_audio",
  "data": "SGVsbG8gd29ybGQ..."
}
```

- `data`: base64-encoded raw PCM audio (24kHz, 16-bit, mono)
- Arrives in small chunks (each chunk is a fraction of a sentence)
- Multiple chunks arrive rapidly — they must be queued for gapless playback

### `tts.audio_clear` — Stop Playing Immediately

Sent when the bot is interrupted mid-speech. Clear all queued audio.

```json
{
  "event": "tts.audio_clear"
}
```

**When this fires:**
1. Bot is speaking (audio chunks streaming to your page)
2. A meeting participant starts talking (interruption detected)
3. GetSun (collaborative voice intelligence) sends `audio.interrupted` to the server
4. Server sends `tts.audio_clear` to your webpage
5. Your page must stop current playback and flush the queue

**If you don't handle this:** The bot keeps "talking" through queued audio even though it was interrupted — it talks over the person who interrupted it. This is the most important event to handle correctly.

---

## Why You Need an Audio Queue

Audio arrives as small chunks, not one big file. Each chunk is a fraction of a sentence:

```
Chunk 1: "Hello every" (200ms of audio)
Chunk 2: "one, today we're"  (300ms)
Chunk 3: " going to discuss" (250ms)
Chunk 4: " Q3 results."     (280ms)
```

**Without a queue (wrong):**
```javascript
// BAD — gaps between chunks
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.event === 'tts.webpage_audio') {
    const buffer = decodeAudio(msg.data);
    playImmediately(buffer);  // starts now, but previous chunk might still be playing
                               // OR there's a gap between chunks
  }
};
```

**With a queue (correct):**
```javascript
// GOOD — each chunk scheduled to start exactly when previous ends
// Uses AgentCallAudio which handles all of this
const player = new AgentCallAudio();
ws.onmessage = (e) => {
  player.handleEvent(JSON.parse(e.data));
};
```

The queue ensures:
- **No gaps**: each chunk starts exactly when the previous one ends
- **No overlaps**: chunks never play simultaneously
- **Instant clear**: when interrupted, all pending chunks are discarded

---

## Using AgentCallAudio (Recommended)

We provide a drop-in audio player that handles queuing, playback, and clearing. Include it in your webpage:

```html
<script src="../agentcall-audio.js"></script>
<script>
  const player = new AgentCallAudio();
  
  const ws = new WebSocket(wsURL);
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    player.handleEvent(msg);  // handles tts.webpage_audio + tts.audio_clear
  };
</script>
```

That's it. `handleEvent` automatically:
- Decodes base64 PCM → AudioBuffer
- Queues for gapless sequential playback
- Clears queue on `tts.audio_clear`

### With State Callback

```html
<script src="../agentcall-audio.js"></script>
<script>
  const player = new AgentCallAudio({
    onStateChange: (playing) => {
      // Update visual based on whether audio is playing
      document.getElementById('avatar').classList.toggle('speaking', playing);
    }
  });
  
  const ws = new WebSocket(wsURL);
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    player.handleEvent(msg);
    
    // Also handle voice state for other visual updates
    if (msg.event === 'voice.state') {
      updateStatusIndicator(msg.state);
    }
  };
</script>
```

### Manual Control

```javascript
const player = new AgentCallAudio();

// Queue a chunk manually (if not using handleEvent)
player.playChunk(base64Data);

// Clear all audio (if not using handleEvent)
player.clear();

// Check if playing
if (player.isPlaying()) {
  console.log('Bot is speaking');
}
```

---

## Building Your Own Audio Player (Advanced)

If you need custom audio handling (effects, mixing, etc.), here's how to build your own:

```javascript
class CustomAudioPlayer {
  constructor() {
    this.ctx = null;
    this.queue = [];
    this.nextTime = 0;
  }
  
  play(base64Data) {
    // Create AudioContext on first play (browser autoplay policy).
    if (!this.ctx) {
      this.ctx = new AudioContext({ sampleRate: 24000 });
    }
    
    // Decode base64 → PCM bytes → Float32 samples.
    const bytes = Uint8Array.from(atob(base64Data), c => c.charCodeAt(0));
    const samples = new Float32Array(bytes.length / 2);
    const view = new DataView(bytes.buffer);
    for (let i = 0; i < samples.length; i++) {
      samples[i] = view.getInt16(i * 2, true) / 32768.0;  // signed 16-bit LE → float
    }
    
    // Create AudioBuffer (24kHz, mono).
    const buffer = this.ctx.createBuffer(1, samples.length, 24000);
    buffer.getChannelData(0).set(samples);
    
    // Schedule playback after last chunk.
    const source = this.ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(this.ctx.destination);
    
    const now = this.ctx.currentTime;
    if (this.nextTime < now) this.nextTime = now;
    source.start(this.nextTime);
    this.nextTime += buffer.duration;
    
    // Track for clearing.
    this.queue.push(source);
    source.onended = () => {
      const idx = this.queue.indexOf(source);
      if (idx !== -1) this.queue.splice(idx, 1);
    };
  }
  
  clear() {
    // Stop ALL queued audio immediately.
    for (const source of this.queue) {
      try { source.stop(); } catch (e) {}
    }
    this.queue = [];
    this.nextTime = 0;
  }
}
```

### Adding Audio Effects

```javascript
// Example: Add reverb to the bot's voice
const convolver = this.ctx.createConvolver();
convolver.buffer = reverbImpulseResponse;  // load your IR
convolver.connect(this.ctx.destination);

// Connect source through reverb instead of direct
source.connect(convolver);  // instead of source.connect(this.ctx.destination)
```

### Mixing Background Music

```javascript
// Play background music at low volume while bot speaks
const music = this.ctx.createBufferSource();
music.buffer = backgroundMusicBuffer;
const gainNode = this.ctx.createGain();
gainNode.gain.value = 0.1;  // 10% volume
music.connect(gainNode);
gainNode.connect(this.ctx.destination);
music.start();

// TTS audio plays at full volume alongside
source.connect(this.ctx.destination);
```

---

## Complete Example: Animated Avatar with Audio

A webpage that shows an animated avatar that:
- Pulses when speaking
- Reacts to voice state changes
- Plays audio correctly with queue + clear

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { background: #000; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  #avatar {
    width: 200px; height: 200px;
    border-radius: 50%;
    background: url('avatar.png') center/cover;
    border: 3px solid #333;
    transition: all 0.3s ease;
  }
  #avatar.speaking {
    border-color: #22c55e;
    box-shadow: 0 0 30px rgba(34, 197, 94, 0.4);
    transform: scale(1.05);
  }
  #avatar.thinking {
    border-color: #a855f7;
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
  }
  #avatar.interrupted {
    border-color: #ef4444;
    transform: scale(0.98);
  }
  #status {
    position: absolute; bottom: 30px;
    color: #666; font-family: system-ui; font-size: 14px;
  }
</style>
</head>
<body>

<div id="avatar"></div>
<div id="status">listening</div>

<script src="../agentcall-audio.js"></script>
<script>
const avatar = document.getElementById('avatar');
const statusEl = document.getElementById('status');

// Audio player with visual feedback.
const audioPlayer = new AgentCallAudio({
  onStateChange: (playing) => {
    // Audio started/stopped — update avatar visual.
    // Note: voice.state also sends 'speaking', but this is more precise
    // because it tracks actual audio output, not GetSun (collaborative voice intelligence)'s intent.
  }
});

// Connect to AgentCall WebSocket.
const params = new URLSearchParams(window.location.search);
const wsURL = params.get('ws');

if (wsURL) {
  const ws = new WebSocket(wsURL);
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    const eventType = msg.event || msg.type;

    // Voice state → update avatar visual.
    if (eventType === 'voice.state') {
      const state = msg.state;
      statusEl.textContent = state.replace(/_/g, ' ');
      
      // Remove all state classes.
      avatar.className = '';
      
      // Add current state class.
      if (state === 'speaking') avatar.classList.add('speaking');
      if (state === 'thinking' || state === 'waiting_to_speak') avatar.classList.add('thinking');
      if (state === 'interrupted') avatar.classList.add('interrupted');
    }

    // Audio playback + clear — handled by AgentCallAudio.
    audioPlayer.handleEvent(msg);
  };
}
</script>
</body>
</html>
```

---

## Interruption Flow — What Happens

```
1. Bot is speaking (state: speaking)
   └── tts.webpage_audio chunks arriving → queued → playing

2. Meeting participant starts talking
   └── FirstCall (meeting infrastructure) detects → transcript.partial sent to GetSun (collaborative voice intelligence)

3. GetSun (collaborative voice intelligence) detects interruption
   ├── state → "interrupted" (sent to agent + webpage)
   └── audio.interrupted (sent to server)

4. Server handles audio.interrupted
   ├── Audio mode: sends audio.clear to FirstCall (meeting infrastructure)
   └── Webpage modes: sends tts.audio_clear to webpage

5. Webpage receives tts.audio_clear
   └── AgentCallAudio.clear() → stops all playback, flushes queue
   └── Silence. Bot stops "talking".

6. GetSun (collaborative voice intelligence) evaluates the interruption
   ├── If follow-up question → state: thinking → prepares new response
   └── If unrelated → state: listening → goes back to idle
```

**Without proper clear handling:**
```
Steps 1-4 same...
5. Webpage does NOT handle tts.audio_clear
   └── Queued audio keeps playing
   └── Bot talks over the person who interrupted
   └── Awkward conversation, bot seems rude
```

---

## Audio Format Reference

| Property | Value |
|---|---|
| Sample rate | 24,000 Hz |
| Bit depth | 16-bit signed integer |
| Channels | Mono (1 channel) |
| Byte order | Little-endian |
| Encoding | Raw PCM (no headers, no compression) |
| Transport | Base64-encoded in JSON WebSocket messages |

**Conversion:**
```
base64 string → atob() → Uint8Array → DataView.getInt16(LE) → Float32 (-1.0 to 1.0)
```

**Duration calculation:**
```
duration_seconds = base64_decoded_bytes / (24000 * 2)
                                          ↑ sample_rate × bytes_per_sample
```

---

## Troubleshooting

**No audio playing:**
- Check browser console for AudioContext errors
- Browser autoplay policy may block audio until user interaction
- Fix: add a "Click to start" button that creates the AudioContext

**Gaps between chunks:**
- Use AgentCallAudio or implement proper queue scheduling
- Don't play each chunk with `source.start(0)` — use `source.start(nextTime)`

**Audio continues after interruption:**
- Ensure you handle `tts.audio_clear` events
- Call `player.clear()` or stop all AudioBufferSourceNodes

**Echo/feedback:**
- The browser's audio output is captured by FirstCall (meeting infrastructure)
- If your page also captures microphone input, you'll get feedback
- Solution: don't capture microphone in your webpage — FirstCall (meeting infrastructure) handles meeting audio separately
