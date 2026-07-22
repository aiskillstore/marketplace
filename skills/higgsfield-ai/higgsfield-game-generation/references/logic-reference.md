# Rules module reference (`logic.js`)

The engine loads this module into a sandboxed isolate and calls your
functions around every player action. State lives in server-side storage
between calls; your functions are the only thing that ever changes it.

## The contract (all six exports required)

```js
export const meta = { game: "<display-name>", minPlayers: 2, maxPlayers: 2 };

// Called once when minPlayers have joined. `players` = playerIds in seat
// order (players[0] joined first). Return the complete initial state.
export function setup(players) { ... }

// May this player do this action right now? Return {ok: true} or
// {ok: false, error: "<shown to that player verbatim>"}.
// NEVER throw; never mutate state here.
export function validateAction(state, playerId, action) { ... }

// Apply a VALIDATED action. Return the NEW state (the engine stores your
// return value). Treat `state` as immutable — copy, don't mutate.
export function applyAction(state, playerId, action) { ... }

// Checked after every applyAction.
// {over: false} | {over: true, winner: "<playerId>"} | {over: true, draw: true}
// (you may add extra fields, e.g. winning line — the client sees them in `result`)
export function isGameOver(state) { ... }

// What THIS player is allowed to see. The client only ever receives
// viewFor's return value, never the raw state.
export function viewFor(state, playerId) { ... }
```

Environment: standard JS built-ins only (`Math.random` is fine — it runs
server-side, so clients can't predict it). No imports and no timers — the
deploy tool rejects those statically. Network/`eval` simply fail at runtime:
the sandbox has no bindings and no egress. State must survive `JSON.parse(JSON.stringify(s))`:
plain objects, arrays, numbers, strings, booleans, null. No `Map`/`Set`/
`Date`/class instances.

## Worked example — tic-tac-toe (turn-based, no secrets)

```js
export const meta = { game: "tic-tac-toe", minPlayers: 2, maxPlayers: 2 };

const LINES = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6],
];

export function setup(players) {
  return {
    board: Array(9).fill(null),
    marks: { [players[0]]: "X", [players[1]]: "O" },
    turn: players[0],                    // a playerId, not an index
  };
}

export function validateAction(state, playerId, action) {
  if (!action || !Number.isInteger(action.cell)) {
    return { ok: false, error: "action.cell (0-8) required" };
  }
  if (state.turn !== playerId) return { ok: false, error: "not your turn" };
  if (action.cell < 0 || action.cell > 8) return { ok: false, error: "cell out of range" };
  if (state.board[action.cell] !== null) return { ok: false, error: "cell already taken" };
  return { ok: true };
}

export function applyAction(state, playerId, action) {
  const board = [...state.board];
  board[action.cell] = state.marks[playerId];
  const next = Object.keys(state.marks).find((id) => id !== playerId);
  return { ...state, board, turn: next };
}

export function isGameOver(state) {
  for (const [a, b, c] of LINES) {
    if (state.board[a] && state.board[a] === state.board[b] && state.board[b] === state.board[c]) {
      const winner = Object.entries(state.marks).find(([, m]) => m === state.board[a])[0];
      return { over: true, winner, line: [a, b, c] };
    }
  }
  if (state.board.every((cell) => cell !== null)) return { over: true, draw: true };
  return { over: false };
}

export function viewFor(state, _playerId) {
  return state; // nothing is secret in tic-tac-toe
}
```

## The hidden-information pattern (simultaneous reveal, secret hands)

For games where players act secretly — rock-paper-scissors, liar's dice,
hidden hands, sealed bids — keep the secret in state and **mask it in
`viewFor`**:

```js
// State: pending secret choices accumulate, then resolve together.
export function applyAction(state, playerId, action) {
  const choices = { ...state.choices, [playerId]: action.choice };
  const [p1, p2] = state.players;
  if (!choices[p1] || !choices[p2]) {
    return { ...state, choices };               // wait for the other player
  }
  const scores = resolveRound(choices, state);  // both in — resolve
  return { ...state, choices: {}, scores, lastRound: { choices } };
}

// Each player sees their own pending choice; the opponent's shows as "?".
export function viewFor(state, playerId) {
  const choices = {};
  for (const [pid, c] of Object.entries(state.choices)) {
    choices[pid] = pid === playerId ? c : "?";
  }
  return { ...state, choices };   // lastRound stays revealed — it's resolved
}
```

The rule of thumb: if leaking a field would let a player cheat, `viewFor`
must remove or replace it. Masking in the client is not masking.

## Pitfalls (each one is a real bug)

- **Mutating `state` in place** and returning it can make changes invisible
  or non-atomic. Always build a new object (`{...state, field: next}`).
- **Turn by index** breaks when you reorder anything. Store the playerId
  whose turn it is.
- **Forgetting the draw check** leaves a full board in "playing" forever.
- **Throwing in `validateAction`** kills the action silently. Return
  `{ok: false, error}` — the string is shown to the player, write it for
  them ("a ship is already there"), not for a debugger.
- **Validating in the client only.** The server must reject every illegal
  action, because the client is editable by anyone.
- **Unbounded state growth** (e.g. appending every move forever for no
  reason). Keep state minimal; it's serialized on every action.
- **Asymmetric `setup`** that depends on anything besides `players`. It must
  be a pure function of the seat list (randomness is fine).
