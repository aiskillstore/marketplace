# Online Multiplayer — rules module, client protocol, deploy

> **Scope:** Mandatory whenever the Players axis is not solo (co-op, versus, party). Local
> same-screen multiplayer is a client-only game — it needs none of this; use the solo path in
> `build-game.md`. This file covers ONLINE multiplayer: what you write, the two engine tiers,
> and the netcode correctness rules. The app layout, packaging, and publishing live in
> `build-game.md` (§1, §6) for every route.

The platform provides rooms, WebSockets, seating, reconnects, authoritative state, and
broadcasting — **you never write that plumbing**. You produce exactly two artifacts:

- **`logic.js`** — the game rules: a self-contained, pure-function ES module.
- **`index.html`** — the game page: a dumb renderer speaking the room protocol.

Before writing code, load both contracts and follow them exactly:

- `get_game_creation_bundle_file` → `references/logic-reference.md` — the six required
  exports, a worked example, the hidden-information pattern, the pitfalls.
- `get_game_creation_bundle_file` → `references/client-reference.md` — the exact WebSocket
  protocol and a known-good page skeleton (reuse its plumbing; replace only `render()` and
  input wiring).

When something behaves unexpectedly (who receives which message, seat/spectator rules, what
survives a restart) also load `references/kernel-reference.md` — the exact trusted code your
logic runs inside.

---

## 1 — Principles

- **The server is the referee.** All rules live in `logic.js` and run server-side. The client
  sends inputs and draws the latest state. Never enforce a rule only in the UI.
- **Secrets are masked server-side.** Anything one player must not see (hidden hands,
  unrevealed choices, fog of war) is stripped in `viewFor` — not hidden with CSS. Assume
  every player reads their WebSocket frames in devtools.
- **Pick the right tier** (§2). Turn-based and simultaneous-reveal games are the standard
  path and cost ~nothing while idle. Real-time games are possible but heavier.
- **Ship, then offer variants.** Deploy the straightforward version first and hand over the
  link; offer rule tweaks as a follow-up (updates keep the same URL — `build-game.md` §6).

## 2 — Two tiers: rules module vs custom server

| | **`logic.js` — game rules (DEFAULT)** | **`server.js` — custom server** |
|---|---|---|
| Fits | turn-based, simultaneous-reveal: boards, cards, words, quizzes, party games | continuous movement, tick loops, FPS/.io-style, custom protocols |
| You write | six pure functions over JSON state | a full `GameServer` class with its own protocol |
| Plumbing | platform kernel: rooms, seats, join/action/reset protocol, reconnects, persistence | you own the protocol; platform provides sockets + sharding |
| Idle cost | ~nothing (rooms hibernate between actions) | always-on while occupied |
| Timers | forbidden (statically rejected) | allowed — start lazily, stop when empty |

Rule of thumb: **if nothing happens while players think, use `logic.js`.** If the world moves
on its own, use `server.js`.

The zip layout for both is in `build-game.md` §1 — the code module sits at the archive root
next to `index.html`. The deploy mode is detected from the file automatically.

## 3 — Tier 1: the rules module (`logic.js`)

The full contract, a worked tic-tac-toe example, and the hidden-information pattern are in
`logic-reference.md`. The deploy validator enforces statically (the deploy fails otherwise):

- Self-contained ES module, **no imports**.
- Must export all six: `meta`, `setup`, `validateAction`, `applyAction`, `isGameOver`,
  `viewFor`.
- **No timers** (`setTimeout`/`setInterval`) — the contract is event-driven: state changes
  only when a player acts.

State must survive `JSON.parse(JSON.stringify(s))`: plain objects/arrays/primitives only.
`Math.random` is fine (it runs server-side). Set `minPlayers == maxPlayers` for fixed-seat
games (almost all of them) — the engine seats players in join order, starts the game when
`minPlayers` have joined, and later visitors become spectators.

Before moving on, simulate one full game in your head against your own
`validateAction`/`applyAction`/`isGameOver`: opening move, an illegal move, a winning line, a
draw. Fix what breaks.

## 4 — Tier 1: the game page (`index.html`)

Follow `client-reference.md` — it contains the exact protocol and a known-good skeleton with
the connection plumbing already written. Non-negotiables:

- Connect to `ws(s)://<host><page-path-without-trailing-slash>/ws/<roomId>`; join with a
  `playerId` kept in **sessionStorage** (so two tabs = two players — also how you test).
- Put the room id in `?room=<id>` and show the invite link prominently while waiting.
- Render **only** from the latest `state` message — every message carries the complete
  picture (`status`, `seats`, `you`, `view`, `result`).
- Show three phases clearly: waiting (invite link), playing (whose turn / what to do), over
  (who won + a "play again" button sending `{"type":"reset"}`).
- Disable inputs when it's not the player's turn or they're spectating; show server `error`
  messages instead of swallowing them.
- Reconnect automatically on socket close.

One page, inline CSS/JS, relative asset paths, big touch-friendly controls.

## 5 — Tier 2: the custom server (`server.js`)

Only for real-time games. The module must satisfy the deploy validator:

- **`export class GameServer extends DurableObject`** — the engine instantiates it per shard
  and forwards every request, including WebSocket upgrades, to its `fetch()`.
- Imports **only** from `'cloudflare:workers'`.

Inside `fetch()` handle the upgrade with `WebSocketPair` + `ws.accept()`. One instance runs
per shard (`<base>/ws/<shard>` — use shards as rooms, or manage rooms internally on
`<base>/ws`). Timers are allowed (start lazily, stop when the room empties); binary frames
pass through; state is in-memory and resets on restart, so clients must auto-reconnect and
rejoin. The first upgrade can take ~1s cold — queue `ws.send` calls until the `open` event.
The sandbox has no network egress and no storage bindings — pure compute.

## 6 — Netcode correctness gate (before deploy)

- [ ] every action is validated server-side; the client merely disables illegal inputs
- [ ] hidden information never appears in another player's `view` (check the frames in
      devtools, not the UI)
- [ ] a second browser tab can join via the invite link and play a full game
- [ ] refresh mid-game reconnects and restores the correct view for that player
- [ ] the game over → reset loop works without re-creating the room
- [ ] spectator (a third tab) sees the game without gaining a seat or inputs

Then package and deploy per `build-game.md` §6; `higgsfield game deploy` uploads the ZIP
internally. Save the returned `game_id` for in-place updates.
