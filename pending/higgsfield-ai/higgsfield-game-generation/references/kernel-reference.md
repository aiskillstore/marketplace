# Kernel reference — what wraps your rules module

When you deploy game rules with `higgsfield game deploy`, the platform composes your logic
module with this trusted **game kernel** and uploads the pair as one app.
Reading it tells you exactly when each of your functions runs, what the
client receives, and what is (and isn't) your responsibility.

## The runtime around the kernel

The hosting engine owns the WebSockets (hibernation API — rooms cost ~zero
while players think) and runs the kernel as a pure message handler:

- one **room = one shard** (`<base>/ws/<roomId>`), each room an isolated
  instance with its own storage;
- every socket event becomes one kernel call; the kernel returns a list of
  `{to: connId, data}` messages and the host fans them out;
- the kernel (and your logic) is sandboxed: no network, no timers, no
  storage other than its own.

## Consequences for the logic module you write

- **State must be JSON.** It is persisted via storage on every action and
  survives restarts/hibernation. Don't put functions, Maps, or class
  instances in it.
- **`viewFor` runs once per connected player on every broadcast** — every
  state change re-renders everyone's view. Keep it cheap, and do ALL
  secret-masking there: each client only ever receives its own view.
- **Your validation is the only gate.** The kernel calls
  `validateAction` → `applyAction` → `isGameOver` in that order, only for
  seated players, only while `status === "playing"`. Errors you return go
  verbatim to the acting player.
- **Seats are kernel-owned.** Join order fills seats up to
  `meta.maxPlayers`; the game starts when `meta.minPlayers` have joined;
  later connections are spectators (they receive views but cannot act).
  Your `setup(players)` gets the seat list and must not depend on anything
  else (randomness is fine — it runs server-side).
- **No timers exist in v1.** Nothing happens between actions: no turn
  clocks, no scheduled events. Design rules accordingly (e.g. no
  "auto-pass after 30s").
- **Reconnects are identity-based.** A player rejoining with the same
  `playerId` keeps their seat; the conn→player map is persisted, so even a
  server restart preserves the game.

## The kernel source (v1)

```js
// Shipped by tools/multiplayer_game.py: composed with the generated logic.js
// at publish time and uploaded to the apps-engine as a pump-mode app. The
// engine never sees game semantics — this kernel IS the game layer.
// Source of truth alongside the engine POC: games-poc/kernel/game-kernel-v1.js.
// game-kernel v1 — turn-based multiplayer game semantics as a PUMP-mode app
// for the thin apps-engine. This module is composed with a generated
// `logic.js` by the PUBLISHER (the hermes game tool); the engine never sees
// game concepts.
//
// Implements the existing tier-1 wire protocol, so clients built for the old
// game engine work unchanged:
//   in:  {type:"join", playerId} | {type:"action", action} | {type:"reset"}
//   out: {type:"state", status, seats, you, connected, view, result, meta}
//        {type:"error", error}
//
// One Host shard = one room. State lives in the facet's own storage, so it
// survives restarts and hibernation; the conn→player map is persisted too
// (the host's sockets outlive this facet's memory).
//
// logic.js contract (pure functions over JSON state):
//   meta {game, minPlayers, maxPlayers} · setup(players) · validateAction
//   (state, playerId, action) · applyAction(state, playerId, action) ·
//   isGameOver(state) · viewFor(state, playerId)

import { DurableObject } from "cloudflare:workers";
import * as logic from "./logic.js";

export class App extends DurableObject {
  async _load() {
    return {
      game:
        (await this.ctx.storage.get("game")) ?? {
          status: "waiting", // waiting | playing | over
          seats: [], // playerIds in join order
          state: null,
          result: null,
        },
      conns: (await this.ctx.storage.get("conns")) ?? {}, // connId -> playerId
    };
  }

  async _save(game, conns) {
    await this.ctx.storage.put("game", game);
    await this.ctx.storage.put("conns", conns);
  }

  _broadcast(game, conns) {
    return Object.entries(conns).map(([connId, playerId]) => ({
      to: connId,
      data: {
        type: "state",
        status: game.status,
        seats: game.seats,
        you: playerId,
        connected: Object.keys(conns).length,
        view: game.state ? logic.viewFor(game.state, playerId) : null,
        result: game.result,
        meta: logic.meta,
      },
    }));
  }

  _error(connId, error) {
    return [{ to: connId, data: { type: "error", error } }];
  }

  async onConnect(_connId, _meta) {
    return []; // clients introduce themselves with a join message
  }

  async onMessage(connId, raw) {
    if (typeof raw !== "string") return [];
    let msg;
    try {
      msg = JSON.parse(raw);
    } catch {
      return this._error(connId, "invalid json");
    }

    const { game, conns } = await this._load();

    if (msg.type === "join") {
      const playerId = String(msg.playerId || "").slice(0, 64);
      if (!playerId) return this._error(connId, "playerId required");
      conns[connId] = playerId;
      if (!game.seats.includes(playerId) && game.seats.length < logic.meta.maxPlayers) {
        game.seats.push(playerId);
      }
      if (game.status === "waiting" && game.seats.length >= logic.meta.minPlayers) {
        game.state = logic.setup(game.seats);
        game.status = "playing";
      }
      await this._save(game, conns);
      return this._broadcast(game, conns);
    }

    const playerId = conns[connId];
    if (!playerId) return this._error(connId, "join first");

    if (msg.type === "action") {
      if (game.status !== "playing") return this._error(connId, "game is not in progress");
      if (!game.seats.includes(playerId)) return this._error(connId, "spectators cannot act");
      const verdict = logic.validateAction(game.state, playerId, msg.action);
      if (!verdict.ok) return this._error(connId, verdict.error);
      game.state = logic.applyAction(game.state, playerId, msg.action);
      const end = logic.isGameOver(game.state);
      if (end.over) {
        game.status = "over";
        game.result = end;
      }
      await this._save(game, conns);
      return this._broadcast(game, conns);
    }

    if (msg.type === "reset") {
      if (!game.seats.includes(playerId)) return this._error(connId, "spectators cannot reset");
      game.state = game.seats.length >= logic.meta.minPlayers ? logic.setup(game.seats) : null;
      game.status = game.state ? "playing" : "waiting";
      game.result = null;
      await this._save(game, conns);
      return this._broadcast(game, conns);
    }

    return this._error(connId, `unknown message type: ${msg.type}`);
  }

  async onClose(connId) {
    const { game, conns } = await this._load();
    if (connId && conns[connId] !== undefined) {
      delete conns[connId];
      await this._save(game, conns);
    }
    return this._broadcast(game, conns);
  }

  async onWake() {
    return []; // turn-based kernel schedules no timers (v1)
  }
}

export default {
  fetch() {
    return new Response("game kernel module", { status: 200 });
  },
};
```
