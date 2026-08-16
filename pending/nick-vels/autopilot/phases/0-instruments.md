# Phase 0 — Raising the instruments

Everything Phase 0 needs to know about the dashboard, and nothing else. **The rest of the instruments — the full `state.js` shape, the stage table, what the dashboard computes — lives in `phases/7-instruments.md` and is read when the tickets are cut.** Reading it now buys nothing and costs the one context that is never refreshed.

Two files, and the split matters:

- **`.autopilot/state.js`** — the truth, and the only thing you ever write. You read it on resume; the user never opens it.
- **`.autopilot/dashboard.html`** — the only human view. Copied from the template once and **never touched again**. No build step, no dependencies, nothing to generate: in a real browser it opens by double-click, and in an in-app pane it needs one static file server and no more (§3).

The page loads `state.js` from beside it and re-loads that file every ten seconds on its own. So there is exactly one place where state lives, one write per update, and nothing that can drift out of sync — because there is no second copy to drift.

## 1. Copy the template

Never regenerate it, never read it into context, never edit it afterwards:

```bash
cp <skill-dir>/phases/dashboard-template.html .autopilot/dashboard.html
```

## 2. Write `.autopilot/state.js`

First line exactly `window.STATE =`, then the state as ordinary indented JSON. Keeping the assignment on its own line is what lets `tail -n +2 .autopilot/state.js | jq .` work, and what makes an edit further down a small edit.

This is the whole file at the moment it is created — copy it and fill in what you know:

```js
window.STATE =
{
  "slug": "telegram-repair-bot",
  "title": "Телеграм-бот для заявок на ремонт",
  "mode": "semi",
  "depth": "normal",
  "polish": null,
  "tier": null,
  "briefFile": "2026-08-07-brief.md",
  "memoryFile": "AGENTS.md",
  "startedAt": "2026-08-07T14:02:06+03:00",
  "updatedAt": "2026-08-07T14:02:06+03:00",
  "finishedAt": null,
  "stages": [
    { "id": "preflight", "status": "active", "startedAt": "2026-08-07T14:02:06+03:00" },
    { "id": "manifest",  "status": "pending" },
    { "id": "briefing",  "status": "pending" },
    { "id": "spec",      "status": "pending" },
    { "id": "plan",      "status": "pending" },
    { "id": "build",     "status": "pending" },
    { "id": "review",    "status": "pending" },
    { "id": "final",     "status": "pending" }
  ],
  "requirements": {
    "total": 0, "done": 0, "inTicket": 0, "inSpec": 0,
    "placeholder": 0, "deferred": 0, "dropped": 0
  },
  "tickets": [],
  "singlePass": null,
  "tests": null,
  "debt": { "placeholders": [], "assumptions": [], "emptyEnv": [] },
  "additions": [],
  "coverage": null,
  "blind": null
}
```

**All eight stages are listed from the first minute**, the seven unreached ones as `pending`. That is what makes the dashboard show the whole road instead of a blank page — the template renders every stage it is given and nothing it is not.

`tier` is `null` until Phase 4 decides it. `polish` stays `null` unless the доводка parameter was requested — see `phases/polish.md`, and do not add the block here on speculation.

**Never put a secret value in here.** `emptyEnv` holds names only — the whole point of the list.

**ISO 8601 with the offset**, always: `2026-08-07T14:02:06+03:00`. A bare `14:50` gives an invalid date and a dead dash on the dashboard. Read the clock with `date -Iseconds` at the moment the thing happens — **seconds are part of the answer**, and a column of times all ending in `:00` is the visible tell that they were written from memory.

## 3. Open it once, by you

The user should not have to be told where a file is and then go find it. **Open the dashboard yourself, immediately after the first write**, before Phase 1 asks anything.

**Wherever it opens, it keeps itself fresh** — you never have to refresh it, re-open it or re-point it. The page re-loads `state.js` every ten seconds, and the reason that works everywhere is worth knowing, because the obvious mechanism does not. In-app panes (Claude Desktop, IDE viewers) **silence navigation**: measured, not assumed — `location.reload()` did nothing, and `<meta http-equiv="refresh">` did nothing either. What those panes do *not* touch is sub-resource loading, so the page appends a fresh `<script src="state.js?t=…">` instead of reloading itself. It costs nothing, keeps scroll position intact, and works identically in a real browser.

**Path A — inside the user's own window (preferred), and it goes over http, not `file://`.** If your harness gives you a way to show a local page in the window the user is already looking at — a preview pane, an in-app browser, a webview — **use it**. The whole point of a dashboard is being glanceable without leaving what you are doing; a separate browser window defeats half of that.

**Handing that pane a `file://` path produces a dashboard that never shows anything.** Measured in the Claude pane on 2026-08-13: the pane does not open the file as a page, it inlines the HTML into `data:text/html;charset=utf-8,…`. From there `location.origin` is `"null"`, `document.baseURI` is the data-URL itself, `<script src="state.js">` resolves to nothing and `window.STATE` stays `undefined`; an absolute `file:///…/state.js` fires `onerror` — an origin of `null` may not touch `file://` sub-resources — and `fetch` is cut by CORS. The user gets the template's «дашборд ещё не прочитал состояние» screen with a perfectly good `state.js` lying beside it, for the whole run. The same file in Chrome works, which is exactly what makes this look like a broken dashboard instead of a pane.

So serve the directory and point the pane at http — measured on the same day, `window.STATE` loads and the ten-second poll keeps repainting the page:

```bash
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory .autopilot >/dev/null 2>&1 &
printf '%s %s\n' "$PORT" "$!" > .autopilot/serve.pid
```

Run it **in the background** — a foreground server blocks the whole build. Then open the pane at `http://localhost:$PORT` and go to `/dashboard.html`. In Claude Code that is `preview_start({url: "http://localhost:PORT"})` followed by a `navigate` to `/dashboard.html`: a bare `navigate` to a localhost port **without** `preview_start` first is refused by pane policy, and `127.0.0.1` in the URL is refused where `localhost` is accepted.

**Path B — the system browser.** No in-app viewer, or no `python3` → hand the file to the OS, no server involved:

```bash
open .autopilot/dashboard.html 2>/dev/null \
  || xdg-open .autopilot/dashboard.html 2>/dev/null \
  || start "" .autopilot\dashboard.html 2>/dev/null \
  || echo "открой вручную: .autopilot/dashboard.html"
```

A real browser opens `file://` as a page and lets it load `state.js` from the same directory, so the poll works there without a server. A background tab may be throttled to about one poll per minute — the data lags by a minute at worst, it does not freeze. An IDE is Path B, not Path A: `code file.html` opens the *source* in an editor tab, and rendering it needs an extension this skill does not install on the user's behalf.

**Rules for both paths:**

- **Opened exactly once.** Both paths keep themselves current. Neither ever opens a second window or tab, and neither is ever re-pointed.
- **Never on resume into a window that is already open.** On a resume, open it again only if the previous session ended (`finishedAt` was set). If `.autopilot/serve.pid` names a live process, reuse that port instead of starting a second server.
- **A failure is not an error.** Headless machine, no default browser, no pane — print the path in one line and carry on. Do not retry, do not install anything, do not try a second launcher.
- **Do not open it in a remote session.** If `$SSH_CONNECTION` or `$CI` is set, skip opening entirely and print the path — a browser window on someone else's machine helps nobody, and neither does a port.
- **One static server, and only for the pane.** `python3 -m http.server` over `.autopilot`, bound to `127.0.0.1` and nothing wider, started once and killed in Phase 8 (`phases/8-final.md`). It serves the run's own directory — briefs, tickets, manifest — so binding it to `0.0.0.0` would publish them to the network. No build step, no bundler, no second file: the dashboard stays one static page that a browser can also open directly.

Say it in one line, once, inside the opening block — Path A names the address, since the user may want it in a real browser too:

> Дашборд открыл — обновляется сам: http://localhost:PORT/dashboard.html

> Дашборд открыл — `.autopilot/dashboard.html`, обновляется сам.

## 4. The update ritual — the same three moves for the rest of the run

This is here rather than in `phases/7-instruments.md` because **you will need it long after that file would have left your context**, and it is the whole of what most updates require:

| When | What |
|---|---|
| entering a phase | that stage → `active` + `startedAt`; the one you left → `done` + `finishedAt` |
| launching a ticket (or a whole wave) | those tickets → `in-progress` + `startedAt` **before** the subagent goes out |
| a ticket returns, review starts | that ticket → `review` |
| a finding goes back for repair | → `repair`, and `repairs` + 1 |
| committed | → `done` + `finishedAt` + tests + commit |

Every one of them: **edit the affected rows** of `state.js` and move `updatedAt`. Not a rewrite of the file — roughly thirty tokens, one tool call, and the screen follows within ten seconds wherever it is open. No mirroring, no second file, no re-opening anything.

- **`startedAt` on a ticket is that ticket's own launch time** — not the run's, not the build stage's. Copying the run's `startedAt` into a ticket is the one mistake that looks harmless and makes every per-ticket duration on the dashboard wrong from the first row.
- **`startedAt` goes in when the thing starts, not when it ends.** An interval with a start and no end is what makes the timer run; filling both in at the end means the user watched a frozen clock while the work was happening.
- **`updatedAt` moves on every write.** The dashboard shows «обновлено N назад» from it and marks it in warning colour after five silent minutes — that is the user's only way to tell «идёт работа» from «агент умер».
- **Never touch `dashboard.html` after copying it**, and never hand-maintain a progress table in prose.

That is all of Phase 0's business with the instruments. When the tickets are cut, read `phases/7-instruments.md` for the ticket shape and the rest of the reasoning.
