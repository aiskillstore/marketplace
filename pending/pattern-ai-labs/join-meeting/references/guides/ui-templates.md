# UI Templates Guide

Pre-built HTML pages for giving your bot a visual presence in meetings, with zero setup.

## What Templates Are

- Pre-built HTML pages hosted by AgentCall at `/templates/{name}/`
- Used with `--template orb` (starts a local server + tunnel automatically)
- FirstCall (meeting infrastructure) loads the page in the rendering environment and renders it as the bot's video feed
- Templates connect to AgentCall's WebSocket for real-time events and audio

When you pass `--template`, the bridge script starts a local HTTP server and tunnel automatically. The backend appends `?ws=` and `&name=` query parameters to the URL when sending it to FirstCall, so templates can connect to the WebSocket without any manual configuration.

---

## Template Reference

### 1. orb — Animated Pulsing Orb

Canvas-based animated orb that changes color for all 7 voice states.

**Visual behavior:**
- Blue (listening) -> light blue (actively listening) -> purple (thinking) -> yellow (waiting) -> green (speaking) -> red (interrupted) -> teal (follow-up)
- Audio level reactive: pulses faster when the bot is speaking

**Best for:** Simple visual presence, minimal branding.

**Query params:** `?ws=<url>`

---

### 2. avatar — Circular Avatar with Voice States

Displays a circular image with the bot name below. Status text shows a human-readable state label ("Listening", "Thinking...", "Speaking", etc.).

**7 distinct visual states with unique colors, glows, and animations:**

| State | Border/Glow Color | Animation |
|---|---|---|
| `listening` | Muted gray (#555) | Subtle pulse |
| `actively_listening` | Bright blue (#60a5fa) | Alert pulse |
| `thinking` | Purple (#a855f7) | Breathing animation |
| `waiting_to_speak` | Yellow (#eab308) | Eager pulse |
| `speaking` | Green (#22c55e) | Active pulse |
| `interrupted` | Red (#ef4444) | Shrinks slightly |
| `contextually_aware` | Teal (#14b8a6) | Slow pulse |

**Best for:** Branded bot presence, professional look.

**Query params:** `?ws=<url>&avatar=<image_url>&name=<bot_name>`

---

### 3. dashboard — Meeting Monitor

Two-column layout: participants (left) and live transcript (right).

**Features:**
- Connection status indicator (connecting/connected/disconnected)
- Active speaker highlighted with green dot
- Auto-scrolling transcript

**Important:** NOT intended as the bot's camera feed. Use as a debug/monitor tool or for transparency into what the bot sees and hears.

**Best for:** Meeting observers, debugging, recording what happened.

**Query params:** `?ws=<url>`

---

### 4. blank — Minimal Placeholder

Bot name centered on a black background. No visual feedback for voice states. Plays audio via AgentCallAudio.

**Best for:** When you just need a placeholder video feed.

**Query params:** `?ws=<url>&name=<bot_name>`

---

### 5. voice-agent — Mic-Enabled Voice Agent Base

Auto-starts microphone on page load (`getUserMedia`). Shows mic status (listening/speaking/error). Includes basic energy-based interruption detection.

Demonstrates the complete pattern for voice agent webpages: receiving meeting audio as mic input, processing it, and playing responses back through the browser.

**Best for:** Starting point for custom voice agents.

**Query params:** `?ws=<url>&name=<bot_name>`

---

## Voice State Visual Reference

All 7 states used by the collaborative voice strategy:

| State | Meaning | Typical Duration | Color |
|---|---|---|---|
| `listening` | Idle, waiting to be addressed | Until name detected | Gray/Blue |
| `actively_listening` | Detected name in speech, processing | Brief (~1-2s) | Light blue |
| `thinking` | Preparing response from context | 1-5s typically | Purple |
| `waiting_to_speak` | Response ready, waiting for silence | Until silence | Yellow |
| `speaking` | Outputting audio | Until done or interrupted | Green |
| `interrupted` | Stopped mid-speech | Until evaluation done | Red |
| `contextually_aware` | Follow-up window (no name needed) | 20 seconds | Teal |

Templates that visualize voice states (`orb`, `avatar`) listen for `voice.state` WebSocket events and update their appearance accordingly.

---

## Mic Permission for Voice Agent Webpages

When your webpage is a voice agent (it receives meeting audio, processes it, and responds):

### Why Mic Is Needed

- Meeting audio is delivered to the page as browser microphone input
- The rendering environment captures your page's video and audio output
- For the page to "hear" what meeting participants say, it needs mic access

### Why Auto-Start Is Required

- FirstCall (meeting infrastructure) loads your page in the rendering environment (no human present)
- The rendering environment cannot click buttons or interact with UI elements
- Your page MUST call `getUserMedia` in a script that runs on page load
- FirstCall (meeting infrastructure) automatically grants mic permission -- no dialog appears

### How to Add Mic to Your Custom Page

```javascript
// Add this at the TOP of your page's script (runs on load)
let micStream = null;

async function startMic() {
  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    // micStream is now live — meeting audio available

    // Process with your AI:
    const ctx = new AudioContext({ sampleRate: 16000 });
    const source = ctx.createMediaStreamSource(micStream);
    const processor = ctx.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (e) => {
      const samples = e.inputBuffer.getChannelData(0);
      // Feed samples to your STT engine, OpenAI Realtime, etc.
    };

    source.connect(processor);
    processor.connect(ctx.destination);

  } catch (err) {
    console.error('Mic failed:', err);
  }
}

// Auto-start on load — no button clicks!
startMic();
```

### When You Do NOT Need Mic

- Templates that only show visuals (`orb`, `avatar`, `blank`) -- audio comes from AgentCall's TTS pipeline
- Pages that only play audio, not listen
- `dashboard` template (observer only)

---

## When to Use Each Template

| Want to... | Use template |
|---|---|
| Simple visual presence | `orb` |
| Branded avatar with name | `avatar` |
| Monitor meeting (debug) | `dashboard` |
| Just need placeholder video | `blank` |
| Build a voice agent | `voice-agent` (as starting point) |
| Custom UI with full control | Build your own page, use `--port` or `--webpage-url` |

---

## Building Your Own Template

If the built-in templates do not fit your needs, create your own page:

1. Include `<script src="agentcall-audio.js"></script>` for audio playback
2. Read the `?ws=` query param and connect to the WebSocket — the backend appends this automatically when loading your page
3. Handle events: `voice.state`, `tts.webpage_audio`, `tts.audio_clear`
4. If building a voice agent: call `getUserMedia` on page load (see above)
5. Host locally (`--ui-port 3000`) or publicly (`--webpage-url`)

See the [Webpage Audio Guide](webpage-audio.md) for details on the `AgentCallAudio` player and audio event handling.
