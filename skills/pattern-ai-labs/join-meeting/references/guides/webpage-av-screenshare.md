# webpage-av-screenshare Mode — Complete Guide

Two visual presences in the meeting: camera + screenshare.

- **Avatar page** = bot's camera feed (identity, brand, animated avatar)
- **Screenshare page** = shared content (slides, charts, demos, docs)
- Agent orchestrates both via WebSocket

## Audio Routing

```
Meeting participants speak
    -> FirstCall (meeting infrastructure) captures
    -> Routes to avatar page as mic input
    -> Avatar page can process (voice agent AI)
    -> Avatar page plays response -> meeting hears it

Screenshare page
    -> NO mic input (doesn't receive meeting audio)
    -> BUT audio output IS captured (e.g., video with sound)
    -> Meeting hears any audio the screenshare page plays
```

Summary:
- Meeting audio goes to the **avatar page only** (not screenshare)
- Audio output from **both pages** is captured into the meeting
- The screenshare page is for visual content — it cannot listen

## Setup Examples

```bash
# Both local (tunneled)
./scripts/run.sh https://meet.google.com/abc \
  --mode webpage-av-screenshare \
  --port 3000 \
  --screenshare-port 3001

# Avatar public, screenshare local
./scripts/run.sh https://meet.google.com/abc \
  --mode webpage-av-screenshare \
  --webpage-url https://brand.com/avatar \
  --screenshare-port 3001

# Both public (no tunnels)
./scripts/run.sh https://meet.google.com/abc \
  --mode webpage-av-screenshare \
  --webpage-url https://brand.com/avatar \
  --screenshare-url https://slides.com/deck
```

## Controlling Screenshare

```python
# Start sharing (via bridge-visual.py stdin)
{"command": "screenshare.start", "port": 3001}

# Stop sharing
{"command": "screenshare.stop"}

# To change content: update state.json on your local server
echo '{"slide": 1}' > /tmp/screenshare/state.json
# The page polls /state.json every 2 seconds and re-renders
```

## Use Cases

1. **Presenter Bot** — avatar as camera, slides as screenshare. Agent narrates slides with TTS, controls slide transitions via custom WS events.

2. **Support Bot with Docs** — avatar handles voice conversation, screenshare shows relevant documentation or troubleshooting steps based on what's being discussed.

3. **Demo Bot** — branded avatar as camera, live product demo as screenshare. Agent walks through the demo, responding to questions.

4. **Training Bot** — avatar as instructor presence, screenshare shows training materials, diagrams, or interactive exercises.

5. **Interactive content** — for content participants need to click, scroll, or type in (dashboards, docs, forms, code diffs), use `webpage.open` instead of screenshare. It opens in the participant's own browser with full interaction. See "Sharing a Live Webpage" in SKILL.md.

## Building the Screenshare Page

The screenshare page is a regular webpage that:
- Renders content (slides, charts, docs)
- Polls the local server for state changes via HTTP (every 2 seconds)
- Updates DOM when state changes
- Does NOT receive mic input
- Any audio it plays IS captured into the meeting

**Design for 1280x720 viewport.** Use large fonts (40px+ headings, 24px+ body).

The agent creates two files in a local directory (e.g., `/tmp/screenshare/`):

**`state.json`** — the agent updates this to control the page:
```json
{"slide": 0}
```

**`index.html`** — polls `state.json` and renders the current slide:
```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin:0; background:#0d0d0d; color:#fff; font-family:system-ui;
         display:flex; align-items:center; justify-content:center;
         width:1280px; height:720px; overflow:hidden; }
  .slide { text-align:center; max-width:1100px; padding:40px; }
  h1 { font-size:56px; margin-bottom:20px; }
  p { font-size:28px; color:#aaa; line-height:1.5; }
</style>
</head>
<body>
<div class="slide" id="content"></div>
<script>
const slides = [
  '<h1>Q3 Revenue Report</h1>',
  '<h1>Revenue: $2.4M</h1><p>Up 15% YoY</p>',
  '<h1>Enterprise: $1.6M</h1><p>67% of total</p>',
  '<h1>Questions?</h1>'
];
let current = -1;
async function poll() {
  try {
    const r = await fetch('/state.json?t=' + Date.now());
    const state = await r.json();
    if (state.slide !== current) {
      current = state.slide;
      document.getElementById('content').innerHTML = slides[current] || '';
    }
  } catch(e) {}
}
setInterval(poll, 2000);
poll();
</script>
</body>
</html>
```

Serve with: `python -m http.server 3001 --directory /tmp/screenshare/`

To change slides, the agent writes to `state.json`:
```bash
echo '{"slide": 1}' > /tmp/screenshare/state.json
```
The page detects the change within 2 seconds and renders the next slide.

## Agent-Side Orchestration (bridge-visual.py)

The agent controls the full screenshare lifecycle via bridge-visual.py commands:

### Starting screenshare

```json
// Share a public URL
{"command": "screenshare.start", "url": "https://your-slides.com/deck"}

// Share local content via tunnel (auto-tunneled)
{"command": "screenshare.start", "port": 3001}
```

The bridge handles tunneling automatically for local ports. The page loads in
FirstCall's browser and connects to the WebSocket via the `?ws=` parameter
(appended automatically by the backend).

### Controlling the page

Update `state.json` on your local server — the page polls it every 2 seconds:

```bash
# Next slide
echo '{"slide": 1}' > /tmp/screenshare/state.json

# Go to specific slide
echo '{"slide": 3}' > /tmp/screenshare/state.json

# You can extend the state with any fields your page understands:
echo '{"slide": 2, "highlight": "revenue"}' > /tmp/screenshare/state.json
```

The page picks up the change on the next poll cycle (within 2 seconds).
Meeting participants see the update in real-time.

### Stopping screenshare

```json
{"command": "screenshare.stop"}
```

### Swapping to a different page

Use `screenshare.swap` (preferred) when you want to change what's shared during a call:

```json
{"command": "screenshare.swap", "port": 3002}
{"command": "screenshare.swap", "url": "https://different-page.com"}
```

The bridge sends `screenshare.stop`, waits up to 5 seconds for FirstCall to confirm the previous share has stopped, then issues `screenshare.start`. For local-port swaps it cache-busts the tunnel URL; external URLs pass through unchanged. This eliminates two failure modes:

1. **"Old content keeps showing"** — for local-port swaps the tunnel URL is byte-identical (`https://tunnel/screenshare/`), so FirstCall's headless browser would otherwise see "same URL — don't reload." The cache-buster (`?_acv=<ms>`) forces a fresh page load. External URLs aren't cache-busted because (a) two different external URLs already trigger a fresh load, and (b) appending `_acv` would break signed URLs (S3 pre-signed, Vimeo private, Power BI secure embeds, etc. — the signature is computed over the query string).
2. **Race conditions** — manually doing `stop` then `start` in quick succession can cause FirstCall to receive `start` before `stop` has been processed, leaving the new screenshare in a broken state.

If you must do it manually with `stop` + `start`, wait for the `screenshare.stopped` event before sending `start`.

If the new local port has no server listening, the bridge emits `screenshare.error` immediately rather than producing a white page in the meeting:
```json
{"event": "screenshare.error", "message": "localhost:3002 is not reachable. Is your local server running?"}
```

### Full example — presenter bot flow

```
# Setup: agent creates /tmp/screenshare/index.html + state.json, starts HTTP server

Agent: tts.speak "Good morning everyone. Let me walk you through Q3 results."
Agent: screenshare.start {"port": 3001}
  → event: screenshare.started

Agent: tts.speak "Starting with revenue. As you can see, we hit 2.4 million."
Agent: echo '{"slide": 1}' > /tmp/screenshare/state.json

Agent: tts.speak "Enterprise was the main driver at 1.6 million."
Agent: echo '{"slide": 2}' > /tmp/screenshare/state.json

User: "Can you go back to the revenue slide?"
Agent: tts.speak "Sure."
Agent: echo '{"slide": 1}' > /tmp/screenshare/state.json

User: "Thanks, we're good."
Agent: tts.speak "Ending the presentation."
Agent: screenshare.stop
  → event: screenshare.stopped
  → Participants see only the avatar now
```

### Local screenshare with tunnel

For agent-generated content (dynamically created HTML, charts, code):

```bash
# Agent starts a local HTTP server
python -m http.server 3001 --directory /tmp/my-slides/

# Then via bridge-visual.py stdin:
{"command": "screenshare.start", "port": 3001}
```

The bridge automatically creates a tunnel from `localhost:3001` through AgentCall's
tunnel server. FirstCall loads the page via the tunnel URL. The page polls
`/state.json` on the same server — requests go through the tunnel back to localhost.
When the agent updates `state.json`, the page detects the change and re-renders.

## Important Notes

- **Screenshare is inactive at start** — the bot joins with avatar only. Send `screenshare.start` when ready.
- If you don't need screenshare, use `webpage-av` mode instead of `webpage-av-screenshare`.
- The page polls your local server every 2 seconds for state changes via HTTP through the tunnel.
- To swap to a completely different page: prefer `screenshare.swap` (atomic). If using stop+start manually, wait for `screenshare.stopped` event before sending `start`.
- Design for **1280x720 viewport** — use large fonts (40px+ headings, 24px+ body).
- Keep screenshare pages lightweight for performance.
- The screenshare page runs in a headless browser — no clicks, scrolling, or typing possible.
- Test locally: what you see in your browser at 1280x720 = what participants see.
- Add `?t=Date.now()` to fetch URLs to prevent cached responses through the tunnel.

## See Also

- [webpage-av.md](webpage-av.md) — single-page AV mode (no screenshare)
- [webpage-audio.md](webpage-audio.md) — audio-only webpage mode
- [interruption-handling.md](interruption-handling.md) — how interruptions work with voice state
