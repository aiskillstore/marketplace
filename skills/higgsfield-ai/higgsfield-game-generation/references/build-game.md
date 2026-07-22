# Game Assembly & Delivery

> **Scope:** Stage 3+ of the game-generation pipeline, for **every** game route (solo, local
> multiplayer, online multiplayer). Input: the design doc + completed asset jobs. Output: the
> **playable game URL** from the `higgsfield game deploy` response. There is no compile step — the
> platform takes source files as-is and serves them.
>
> **Read order:** this is the **last** reference of the pipeline — open it after
> `game-design-system.md` (always first) and after all asset references, but read it in full
> **before writing any game code**: the app layout and client rules below must shape the code,
> not retro-fit it. Online multiplayer additionally needs the code module from
> `multiplayer.md` (read it before this file when the Players axis is not solo).

---

## 1 — App layout (fixed)

The deliverable is a single source **ZIP** with this layout at its **root** (no wrapper
directory — `logic.js`/`server.js` and `index.html` must sit at the top level of the archive):

```
game.zip
├── logic.js            (turn-based / event-driven games — the rules module)
│     OR
├── server.js           (custom real-time server — tick loops, own protocol)
├── index.html          (the game page — REQUIRED)
└── assets/…            (generated art/audio per the manifest; everything index.html loads)
```

- The zip must contain exactly one code module at its root, and the deploy mode is detected
  from it:
  - `logic.js` — a self-contained pure-function rules module (contract + worked example in
    `logic-reference.md`): exports `meta`, `setup`, `validateAction`, `applyAction`,
    `isGameOver`, `viewFor`; **no imports, no timers**. The platform composes it with a
    trusted room kernel (rooms, WebSockets, seats, reconnects are provided).
  - `server.js` — a custom real-time server: **`export class GameServer extends
    DurableObject`**, imports only from `'cloudflare:workers'`; timers allowed. Use only for
    continuous-movement games (see `multiplayer.md`).
- **Solo / local-multiplayer games need no server logic** — ship this stub `logic.js` (a code
  module is required by the platform):

  ```js
  export const meta = { game: "my-game", minPlayers: 1, maxPlayers: 1 };
  export function setup() { return {}; }
  export function validateAction() { return { ok: true }; }
  export function applyAction(state) { return state; }
  export function isGameOver() { return { over: false }; }
  export function viewFor(state) { return state; }
  ```

- **Online multiplayer** — the code module comes from `multiplayer.md` (+
  `logic-reference.md` / `client-reference.md`); copy the contracts, never invent the
  plumbing.
- **Never scaffold from scratch**: the solo client starts from the skeleton in §3 below; the
  multiplayer client starts from the skeleton in `client-reference.md`.

## 2 — Client rules (non-negotiable, all routes)

- The game runs on `<canvas>` in a plain HTML page. No framework is required or expected —
  a canvas game is a loop, input, and state.
- **All asset and module references are RELATIVE paths** (`./assets/…`, `./game.js`) — the app
  is served under a subpath (`/s/<slug>/`, `/a/<id>/`) and on per-app subdomains; root-relative
  paths break. The WebSocket URL (when used) is built from `location` (see the §3 skeleton /
  `multiplayer.md` client plumbing).
- **Keyboard bound to physical key codes** — `event.code === 'KeyW'`, never `event.key`
  letters: letter bindings break on non-Latin layouts.
- **Touch + keyboard from day one** when mobile is in the delivery context (no hover-only
  interactions); **gamepad via the Gamepad API** when declared — poll in the loop, map onto the
  same command objects.
- **Responsive canvas**: resize and orientation handling, `devicePixelRatio` capped per the
  performance law (`game-design-system.md` §7.5); pause on blur/tab-switch; the mobile viewport
  meta tag set.
- **Fixed-timestep simulation loop** (logic never depends on frame rate) with a seeded RNG —
  the §13.1 determinism rules apply unchanged.
- **Player-visible strings live in one strings module/JSON asset** — zero UI literals in game
  code (`game-design-system.md` §11.3); switching language = swapping the data.
- **Third-party libraries are vendored** into `vendor/` as pinned files copied at
  assembly time. No CDN hotlinks: they drift versions and break offline verification. Adding a
  library is a recorded decision (it must fit the 25 MiB-per-asset bound, §6).
- **Dev overlay** (FPS, frame ms, draw/entity counts where the renderer exposes them) toggled
  by a query flag (e.g. `?dev=1`) — the §7.5 measurements come from it; it ships disabled by
  default.

## 3 — Solo client skeleton

Plumbing complete; replace `update`/`render` and the bindings table with the game:

```html
<!doctype html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Game</title>
<style>html,body{margin:0;height:100%;overflow:hidden;background:#0f1117}canvas{display:block}
#dev{position:fixed;top:4px;left:4px;color:#0f0;font:12px monospace;display:none}</style></head>
<body>
<canvas id="c"></canvas><div id="dev"></div>
<script type="module">
import { STR } from "./strings.js";          // all player-visible text — zero literals below

// --- input: everything becomes a command object; bindings reference event.code ---
const BIND = { KeyW:"up", KeyS:"down", KeyA:"left", KeyD:"right", Space:"action",
               ArrowUp:"up", ArrowDown:"down", ArrowLeft:"left", ArrowRight:"right" };
const PAD  = { 0:"action", 12:"up", 13:"down", 14:"left", 15:"right" }; // standard mapping
const held = new Set();
addEventListener("keydown", e => { const c = BIND[e.code]; if (c) { held.add(c); e.preventDefault(); } });
addEventListener("keyup",   e => { const c = BIND[e.code]; if (c) held.delete(c); });
// touch zones: left half = stick, right half = action (replace with the game's own zones)
const touch = new Set();
addEventListener("touchstart", e => { for (const t of e.changedTouches)
  touch.add(t.clientX < innerWidth/2 ? "left-zone" : "action"); e.preventDefault(); }, {passive:false});
addEventListener("touchend",   e => { touch.clear(); e.preventDefault(); }, {passive:false});
function padCommands() {
  const out = new Set();
  for (const gp of navigator.getGamepads?.() ?? []) if (gp)
    gp.buttons.forEach((b, i) => { if (b.pressed && PAD[i]) out.add(PAD[i]); });
  return out;
}
const commands = () => new Set([...held, ...touch, ...padCommands()]);

// --- canvas: responsive, DPR capped per the §7.5 performance law ---
const canvas = document.getElementById("c"), ctx = canvas.getContext("2d");
const DPR_CAP = 1.5;
function resize() {
  const dpr = Math.min(devicePixelRatio || 1, DPR_CAP);
  canvas.width = innerWidth * dpr; canvas.height = innerHeight * dpr;
  canvas.style.width = innerWidth + "px"; canvas.style.height = innerHeight + "px";
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
addEventListener("resize", resize); addEventListener("orientationchange", resize); resize();

// --- fixed-timestep loop; pause on blur ---
const STEP = 1000 / 60;
let acc = 0, last = performance.now(), paused = false, frames = 0, fpsAt = last, fps = 0;
addEventListener("blur", () => paused = true);
addEventListener("focus", () => { paused = false; last = performance.now(); });

function update(dt, cmds) { /* game simulation — deterministic, seeded RNG */ }
function render(alpha)    { ctx.clearRect(0, 0, innerWidth, innerHeight); /* draw */ }

const dev = new URLSearchParams(location.search).has("dev");
if (dev) document.getElementById("dev").style.display = "block";
function frame(now) {
  requestAnimationFrame(frame);
  if (paused) return;
  acc += now - last; last = now;
  const cmds = commands();
  while (acc >= STEP) { update(STEP, cmds); acc -= STEP; }
  render(acc / STEP);
  if (dev && (frames++, now - fpsAt >= 500)) {
    fps = Math.round(frames * 1000 / (now - fpsAt)); frames = 0; fpsAt = now;
    document.getElementById("dev").textContent = fps + " fps";
  }
}
requestAnimationFrame(frame);
</script>
</body>
</html>
```

`./strings.js` ships alongside: `export const STR = { /* every player-visible string */ };`

## 4 — Wiring the asset manifest

The build consumes assets strictly by manifest `id`/`role` (`design/assets.csv`); missing
assets are a stage-2 failure, not something to silently stub. Files live under
`assets/` and are referenced **relatively** (`./assets/<file>`).

## 5 — Preflight & verify (before publishing)

**Preflight** — the contract artifacts exist and are consumed: `design/plan.md`,
`design/assets.csv` (every row wired), `design/thresholds.md`, the approved STYLE FORMULA.
Any missing artifact is a blocker: go back to the owning stage — do not publish.

Run the client locally (`python3 -m http.server` at the game root — ES modules don't load over
`file://`) and check:

- [ ] core loop playable start → win/lose → restart
- [ ] all manifest assets resolve (no 404s in the console, no placeholder boxes)
- [ ] mode-S gates from `game-design-system.md`: determinism (§13.1), smoke — the reference
      route recorded during planning runs end to end (§13.5)
- [ ] the performance law (§7.5) holds: ≥ 60 fps on the worst-case scene, within the
      `profile.md` budgets, swarms of >50 same-type entities render as one draw call, no
      per-frame allocations — numbers read off the dev overlay
- [ ] mobile in the delivery context → playable **touch-only** at a phone viewport (390×844)
      and keyboard-only on desktop; nothing overflows or sits unreachable
- [ ] keyboard works on a non-Latin layout (`event.code` bindings); gamepad declared →
      playable **gamepad-only**
- [ ] all player-visible strings external; language switch is a data change
- [ ] all references relative — the page works when served under a subpath
- [ ] multiplayer (Players ≠ solo): the `multiplayer.md` §6 netcode gate passes

**Path discipline.** Shell cwd drifts between commands — verify with `pwd` or use absolute
paths; helper scripts you write live under the project folder (e.g. `tools/`), never `/tmp`.
After writing any file, confirm it exists at the expected path before depending on it.

## 6 — Deploy, optionally publish, and deliver

The CLI uploads and confirms the ZIP internally. Do not run a separate upload flow.

1. **Package** from the game root so `logic.js` or `server.js`, `index.html`, and `assets/`
   are at the ZIP root. Keep it lean: no wrapper directory, `node_modules`, repository
   metadata, or build caches.
   ```bash
   zip -r /absolute/path/to/game.zip . -x '*.DS_Store' 'node_modules/*' '.git/*'
   ```
2. **Generate optional share artwork** when the user wants it: a 16:9 cover and 1:1 icon
   through a current image model. Use the returned stable HTTPS URLs as `--thumbnail` and
   `--favicon`.
3. **Deploy** and capture the JSON response:
   ```bash
   higgsfield game deploy /absolute/path/to/game.zip \
     --title "<public title>" \
     --description "<player-facing description>" \
     --thumbnail "<optional https cover URL>" \
     --favicon "<optional https icon URL>" \
     --json
   ```
   The response carries the playable `url` and stable `game_id`.
4. **Publish only on explicit request.** Deployment and marketplace publication are separate:
   ```bash
   higgsfield game publish <game_id> \
     --name "<optional listing name>" \
     --description "<optional listing description>" \
     --cover-url "<optional https 16:9 URL>" \
     --logo-url "<optional https 1:1 URL>" \
     --json
   ```

- The play URL and slug are auto-generated; the response is the only source of truth.
  Never construct links by hand.
- Save `game_id`. For an update, re-package and deploy with `--game-id <game_id>` so the
  existing game keeps its identity and URL. If an update fails, fix and retry with the same
  ID; omitting it would create another game.
- If deployment reports a missing export, forbidden timer in `logic.js`, missing
  `index.html`, or another validation error, fix the source and re-zip. Do not bypass the
  validator.
- Re-verify the returned play URL. For online multiplayer, use two independent sessions.
  Deliver the playable URL, plus the marketplace URL only when publication was requested.

## Other runtimes

Web-only. If the user explicitly asks for another runtime (desktop, mobile app, a specific
engine), say so at the planning stage and offer the web build — don't discover the limitation
after assets are generated.
