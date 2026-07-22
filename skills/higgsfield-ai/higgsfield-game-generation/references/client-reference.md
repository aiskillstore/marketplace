# Game page reference (`index.html`)

One complete HTML page, inline CSS/JS, no external resources. The engine
serves it at the game's URL; the same page is opened by every player.

## The WebSocket protocol (exact, do not improvise)

**Connect** to the room socket under the page's own path:

```js
const base = location.pathname.replace(/\/+$/, "");   // strip trailing slash
const wsUrl = (location.protocol === "https:" ? "wss://" : "ws://")
            + location.host + base + "/ws/" + roomId;
```

**You send** (JSON, one object per message):

| Message | When |
|---|---|
| `{"type":"join","playerId":"<id>"}` | immediately on socket open (also after reconnect) |
| `{"type":"action","action":{...}}` | a move; `action` is whatever your logic's `validateAction` expects |
| `{"type":"reset"}` | restart after the game is over |

**You receive:**

| Message | Meaning |
|---|---|
| `{"type":"state", status, seats, you, connected, view, result, meta}` | the full picture; re-render everything from it |
| `{"type":"error","error":"..."}` | your last message was rejected; show the text |

`state` fields: `status` is `"waiting" | "playing" | "over"`; `seats` is the
playerIds in seat order; `you` is this client's playerId; `view` is what your
logic's `viewFor` returned for this player (null while waiting); `result` is
the `isGameOver` object once status is `"over"`. Every broadcast is complete
— never accumulate state client-side.

## Known-good skeleton

The plumbing below (room id, identity, connect, reconnect, dispatch) is
correct — reuse it as-is and replace only the marked sections.

```html
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><!-- GAME NAME --></title>
<style>
  /* Clean dark theme; big, touch-friendly controls. Style your game here. */
  body { font-family: system-ui, sans-serif; background: #0f1117; color: #e8e8e8;
         display: flex; flex-direction: column; align-items: center; padding-top: 40px; }
  #status { color: #9aa4b2; min-height: 1.4em; margin: 12px 0 20px; }
  #err { color: #e06c75; min-height: 1.2em; margin-top: 10px; font-size: 14px; }
  #reset { display: none; margin-top: 16px; padding: 8px 20px; }
  #share { margin-top: 24px; font-size: 13px; color: #9aa4b2; }
  #share input { width: 320px; }
</style>
</head>
<body>
<h1><!-- GAME NAME --></h1>
<div id="status">connecting…</div>
<!-- ============ YOUR GAME UI HERE (board, hand, buttons…) ============ -->
<div id="err"></div>
<button id="reset">play again</button>
<div id="share">invite link: <input readonly id="link"></div>
<script>
  // --- room id: from ?room= or generate one and put it in the URL --------
  const params = new URLSearchParams(location.search);
  let room = params.get("room");
  if (!room) {
    room = Math.random().toString(36).slice(2, 8);
    params.set("room", room);
    history.replaceState(null, "", location.pathname + "?" + params);
  }
  document.getElementById("link").value = location.href;

  // --- identity: sessionStorage, so two tabs = two players ---------------
  let playerId = sessionStorage.getItem("mp-player-id");
  if (!playerId) {
    playerId = "p-" + Math.random().toString(36).slice(2, 10);
    sessionStorage.setItem("mp-player-id", playerId);
  }

  // --- connection with auto-reconnect ------------------------------------
  const base = location.pathname.replace(/\/+$/, "");
  const wsUrl = (location.protocol === "https:" ? "wss://" : "ws://")
              + location.host + base + "/ws/" + room;
  const statusEl = document.getElementById("status");
  const errEl = document.getElementById("err");
  const resetEl = document.getElementById("reset");
  resetEl.onclick = () => send({ type: "reset" });

  let ws;
  function send(obj) { if (ws && ws.readyState === 1) ws.send(JSON.stringify(obj)); }
  function connect() {
    ws = new WebSocket(wsUrl);
    ws.onopen = () => { errEl.textContent = ""; send({ type: "join", playerId }); };
    ws.onclose = () => { statusEl.textContent = "disconnected — retrying…"; setTimeout(connect, 1500); };
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "error") { errEl.textContent = msg.error; return; }
      if (msg.type !== "state") return;
      errEl.textContent = "";
      render(msg);
    };
  }

  // --- render: the ONLY place the UI changes ------------------------------
  function render(s) {
    resetEl.style.display = s.status === "over" ? "block" : "none";
    if (s.status === "waiting") {
      statusEl.textContent = "waiting for opponent — send the invite link below";
      // disable your inputs here
      return;
    }
    const v = s.view;                 // your viewFor output for THIS player
    const seated = s.seats.includes(s.you);
    // ====================================================================
    // YOUR GAME RENDERING HERE, driven entirely by `s`:
    //  - draw the board/hand from `v`
    //  - enable inputs only if (s.status === "playing" && seated && it is
    //    this player's turn per `v`)
    //  - on input: send({ type: "action", action: { ... } })
    // ====================================================================
    if (s.status === "over") {
      statusEl.textContent = s.result.draw ? "draw!"
        : s.result.winner === s.you ? "you win! 🎉" : "you lose";
    } else if (!seated) {
      statusEl.textContent = "spectating";
    } else {
      statusEl.textContent = /* whose turn / what to do, from `v` */ "";
    }
  }

  connect();
</script>
</body>
</html>
```

## UX requirements

- **Waiting phase sells the game**: show the invite link prominently and say
  what's happening ("waiting for opponent"). This is the first thing the
  user sees.
- **Always show whose turn it is** (or "waiting for opponent's choice" in
  simultaneous games) and clearly mark which player the viewer is
  ("you are X").
- **Disable what can't be clicked** — occupied cells, out-of-turn input,
  spectator input — and surface server `error` strings near the board.
- **Game over is a moment**: name the winner from the viewer's perspective
  ("you win!" / "you lose" / "draw"), highlight the winning line/cards if
  the result includes one, and show the play-again button.
- Keep everything in one page; no external fonts, scripts, or images. Emoji
  make fine game pieces (✊ ✋ ✌️ ♟ 🚢 💣).

## Pitfalls

- **Deriving the WS URL wrong.** It must be built from `location.pathname`
  (the game lives under a subpath), never hardcoded or root-absolute.
- **Sending before the socket opens.** The server upgrade can take ~1s on a
  cold start (vs. instant on localhost), so a fast UI click can hit a socket
  still in CONNECTING state and throw `InvalidStateError`. The skeleton's
  `send()` + join-on-open pattern is safe; if you add UI that sends before
  joining, queue messages until the `open` event.
- **localStorage for identity** makes two tabs the same player — the user
  literally cannot test the game. Use sessionStorage.
- **Accumulating state client-side** (appending moves as they happen)
  desyncs on reconnect. Re-render everything from each `state` message.
- **Forgetting the spectator case**: `s.you` may not be in `s.seats`; inputs
  must be disabled, not broken.
- **Swallowing `error` messages** leaves the player clicking a dead board
  with no feedback.
