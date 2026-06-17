# webpage-av Mode — Complete Guide

Your webpage IS the bot's video feed. Whatever renders on the page is what meeting participants see as the bot's camera square. Audio from the page is also captured into the meeting.

## How It Works

- The page is loaded **once** by FirstCall (meeting infrastructure) in the rendering environment. It does not reload.
- All changes to the page must come via WebSocket events from the agent.
- The agent controls the page. The page is a renderer/display.
- Audio from the page plays into the meeting (captured by FirstCall (meeting infrastructure)).
- Test locally before deploying: what you see in your browser = what participants see.

## Use Cases

### 1. Animated Avatar

```html
<!-- Simple CSS avatar that reacts to voice state -->
<div id="avatar" class="listening"></div>
<script src="../agentcall-audio.js"></script>
<script>
const player = new AgentCallAudio();
const ws = new WebSocket(wsURL);
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.event === 'voice.state') {
    document.getElementById('avatar').className = msg.state;
  }
  player.handleEvent(msg);
};
</script>
```

Participants see the avatar animate — pulsing when speaking, calm when listening.

### 2. Branded Presence

```html
<!-- Static brand card with bot name -->
<div class="brand-card">
  <img src="logo.png" />
  <h1>June AI</h1>
  <p id="status">Listening</p>
</div>
```

Simple, professional. Status text updates via `voice.state` events.

### 3. Agent-Controlled Dynamic UI

The agent serves the page locally and updates content by writing to files
that the page polls via HTTP (every 2 seconds through the tunnel):

```bash
# Agent creates /tmp/screenshare/state.json with current data
echo '{"chart": "revenue", "data": {"revenue": 2.4, "growth": 15}}' > /tmp/screenshare/state.json
```

```javascript
// Page polls state.json and renders
let lastState = '';
setInterval(async () => {
  const r = await fetch('/state.json?t=' + Date.now());
  const text = await r.text();
  if (text !== lastState) {
    lastState = text;
    const state = JSON.parse(text);
    renderChart(state.data);  // update the visual
  }
}, 2000);
```

Agent updates files, page polls and renders. No WebSocket needed for content updates.
For screenshare with slides, see [Webpage AV Screenshare Guide](webpage-av-screenshare.md).

### 4. Standalone Voice Agent (voice-to-voice)

This is powerful — any existing voice agent webpage can join meetings:

```
Meeting audio → FirstCall (meeting infrastructure) → the rendering environment → page's microphone input
                                                    ↓
                                            Voice agent AI processes
                                                    ↓
                                            Page plays response audio
                                                    ↓
                                         FirstCall (meeting infrastructure) captures → meeting
```

The webpage is a complete voice agent:
- Receives meeting audio as browser mic input
- Has its own AI backend (OpenAI Realtime, custom STT+LLM+TTS pipeline)
- Generates and plays response through browser speaker
- FirstCall (meeting infrastructure) captures the browser's audio output into the meeting

Example: An existing customer support voice agent at `https://support.acme.com/agent`
can join any meeting with zero code changes:

```bash
./scripts/run.sh https://meet.google.com/abc-def-ghi \
  --mode webpage-av \
  --webpage-url https://support.acme.com/agent
```

The AgentCall agent in this case is minimal — it just creates the call and monitors
events. The webpage does all the heavy lifting.

## What the Page Receives

| Event | Description |
|---|---|
| `voice.state` | 7 states for visual sync (collaborative only) |
| `tts.webpage_audio` | Audio chunks to play (with sentence metadata) |
| `tts.audio_clear` | Stop audio immediately (interruption) |
| Custom events | Whatever the agent sends via WS |
| Browser mic input | Meeting audio (from the rendering environment) |

## Important Notes

- Page is loaded **once** — no refreshes. Design for long-running operation.
- All state must come from WebSocket events or the page's own logic.
- Keep the page lightweight — it runs in the rendering environment with limited resources.
- Test locally before deploying: what you see in your browser = what participants see.
- Audio: use `AgentCallAudio` for TTS playback, or the page's own audio if it's a standalone voice agent.

## Built-in Templates

Instead of building your own page, use `--template`:

- `orb` — pulsing animated orb, color changes with voice state
- `avatar` — centered image with all 7 voice states + status text
- `dashboard` — participant list + transcript (monitor tool, not camera feed)
- `blank` — bot name on black background
- `voice-agent` — mic-enabled voice agent base with auto-start getUserMedia

## Mic Permissions

FirstCall (meeting infrastructure) automatically grants microphone permission to your webpage. Your page
receives meeting audio as browser microphone input without any user interaction.

Your page MUST auto-start mic recording on load:
```javascript
window.addEventListener('load', async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  // Process meeting audio with your AI
});
```

The rendering environment cannot click buttons or interact with your page.
Everything must start automatically.

## See Also

- [webpage-audio.md](webpage-audio.md) — audio-only webpage mode (no video)
- [interruption-handling.md](interruption-handling.md) — how interruptions work with voice state
- [ui-templates.md](ui-templates.md) — all templates, voice states, mic setup
