---
name: request-transit
description: A public transit map for your requests. Use when the user wants to visualize, animate or share how a request moved through services, from a distributed trace (OpenTelemetry/OTLP, Datadog, PostHog, AWS X-Ray, Grafana Tempo). Draws the trace as an animated subway map (services are lines, hops are stations, slow and failed calls are service alerts) and can render a frame-exact MP4/GIF.
---
<!-- Generated from src/request-transit/SKILL.md; do not edit -->


# Transit

A public transit map for your requests.

🔒 Runs entirely on the user's machine; traces never leave it. No telemetry, tracking or analytics. The built page makes no network requests. The only network use is first-run setup downloads and the optional fetch scripts against the user's own backend.

## Where things are

`<skill>` below means the folder containing this SKILL.md (resolve the symlink if needed). Run every
script from it by absolute path, e.g. `node <skill>/core/render.mjs ./trace.json --name x --out-dir ./transit-out`.
Trace paths are relative to the user's working directory. Pass `--out-dir` (render) or `--out` (build)
so results land in the user's working directory, not inside the skill folder.

## First run

Every script checks its own prerequisites the first time (`<skill>/core/setup.mjs`) and records the result in
`.transit-cache/setup.json`. It reuses before it downloads:

- **Browser:** Playwright's cached build, then any cached Chromium, then system Chrome/Edge. Only if none launches does it download `chromium-headless-shell` (~100 MB, announced first).
- **ffmpeg:** the pinned `ffmpeg-static` dependency (in package.json and the lockfile), then `TRANSIT_FFMPEG`, then ffmpeg on PATH. ffprobe is not needed. Transit never installs system packages: if ffmpeg is missing it prints the command (`npm rebuild ffmpeg-static`, or a system install) and stops.
- **npm deps:** `playwright-core` and `ffmpeg-static`, project-local in node_modules. Needs Node 20+.
- Pinned ffmpeg makes MP4/GIF bytes reproducible across machines; a different ffmpeg (`TRANSIT_FFMPEG`) encodes the same frames to different bytes.

`node <skill>/core/setup.mjs --check` reports what would be used or downloaded and changes nothing. Tell the user before a download if they care about bandwidth. Other switches:

- `--no-download` / `TRANSIT_NO_DOWNLOAD=1` forbids downloads.
- `TRANSIT_BROWSER=/path|chrome|msedge` forces a browser.
- `TRANSIT_SKIP_SETUP=1` skips the check.

## Steps

1. **Get the trace into a file.** A plain OTLP JSON or Datadog span JSON file needs no setup.
   For Datadog interactively, use the Datadog MCP server to fetch the trace's spans and save the raw
   JSON to a file; headless, use `node <skill>/src/request-transit/scripts/fetch.mjs datadog-api <trace_id>`.
   For PostHog Distributed Tracing, call the PostHog MCP tool `apm-trace-get` (find ids with
   `query-apm-spans`), follow pages until `hasMore` is false, and save the JSON; headless,
   `node <skill>/src/request-transit/scripts/fetch.mjs posthog-api <trace_id>` (needs `POSTHOG_API_KEY` = a personal API key `phx_` with `tracing:read`; project tokens `phc_` and project secret keys `phs_` are rejected). See `<skill>/src/request-transit/references/adapters.md`.
2. **Build the page to share:** `node <skill>/core/build.mjs <trace.json> --share --title "Checkout: one order"`.
   Without `--out` the file is named after the title and the failing service, in `./transit-out/`, e.g. `transit-out/checkout-email-service-alert.html`
   (`transit-out/transit.html` when there is nothing to name it after; an existing file gets `-2`, `-3`, ... rather than being overwritten). `--share` scrubs at the strict level, refuses `--no-scrub`, and makes
   the page open paused on the first SERVICE ALERT with its hop in the side panel and a one-line verdict above the map.
   Leave out `--share` for a page that autoplays from the start. `?t=4.5` freezes one frame.
3. **Share it: the HTML file is the thing to share.** Give the user the file path and the verdict line the build printed
   (`share: drop <path> into Slack. Suggested message: "..."`), ready to paste. They drag the file into Slack (desktop and iOS
   open it as the interactive page), a PR or an incident doc. Use the printed verdict as is; never write your own. It carries a short cause; the full error message stays in the side panel and the verdict line's tooltip. For example:
   > email failed after 671 ms: SMTP timeout · SERVICE ALERT · 23 hops
   > `checkout-email-service-alert.html` opens on the failing hop. Click any station for its timing and attributes.
4. **Optional teaser (GIF + MP4):** for a feed post or a README, `node <skill>/core/render.mjs <trace.json> --name <name> --out-dir ./transit-out/<name> --title "..."` writes
   `anim.mp4`, `anim.gif`, `contact.png`. Needs `ffmpeg` and Playwright Chromium. Post the HTML file alongside it for the details.
5. **Check it:** `node <skill>/core/verify.mjs <trace.json> --name <name>` (two renders byte-identical,
   train timing, ffmpeg freeze/black gates). Then look at `contact.png` and two stills yourself
   before handing it over.
6. Report what the map shows: slow hops (amber DELAY), error origins (red SERVICE ALERT with reason),
   and the hop table (every hop is listed as infrastructure or unmatched; none are hidden).

## Rules

- Only render with the bundled scripts. If they fail (for example Chromium can't launch inside an agent
  sandbox, or ffmpeg is missing), stop and tell the user the exact error and the command to rerun with
  more permissions. Never hand-write a substitute renderer or a look-alike GIF.

- Never upload the trace or the render anywhere unless the user asks.
- Span attributes can contain PII. Default redaction drops user/email/token/auth/card-like keys;
  add more with `--redact key1,key2`. Payloads are never shown (tracers don't store them).
- Values are scrubbed too, by default (safe to share): emails, bearer/JWT/known-prefix tokens, `password=`/`api_key=`
  style secrets, URL credentials and query strings, long hex/base64 secrets, UUIDs, home-directory names and AWS
  account ids in ARNs, across service and span names, status messages and URLs. `--strict` also
  removes IPs, internal host names, long numeric ids and all but a minimal attribute set. `--share` is `--strict` plus the
  open-on-the-alert page and the verdict line, and it refuses `--no-scrub`. `--keep-uuids` keeps UUIDs;
  `--no-scrub` turns it off for local debugging only (the page then says not to share it).
- Useful flags: `--slow-ms N`, `--ms-per-sec N`, `--target-seconds 9`, `--trace-id ID`, `--format otlp|datadog|datadog-v2|internal`.

Details: `references/adapters.md`, `references/config.md`, `references/extractors.md`.


## Interactive page

Open `transit-out/<name>/transit.html` in a browser. Video renders hide all of this, and `renderAt(t)` stays a pure function of t. Selection is drawn as an overlay after it, so frames are byte-identical.

- **Hops:** `N` / `↓` / `Shift+→` next hop, `P` / `↑` / `Shift+←` previous hop. The hop is highlighted and the panel opens.
- **Time:** `←` / `→` seek 0.5 s, `,` / `.` one frame, `Home` / `End`, `Space` play/pause. Pausing selects the hop in progress, and playing clears the selection.
- **Speed:** `1` / `2` / `3` = 0.5x / 1x / 2x, or the speed buttons.
- **Click:** a station, train, line or strip tick to select that hop. Clicking empty map toggles play.
- **Side panel:** station-sign header (line bullet + service), a breadcrumb of stops from the root, a mini waterfall (this hop inside its parent, self time solid), kind/start/duration/self, status/error, the expected request/response cards, grouped attributes (HTTP, DB, messaging, RPC, other; the long tail folds away) and child links. The panel also shows the expected request/response when the page was built with contracts (see below).
- **Links:** `#span=<id>` (or `?span=` / `?pin=`) selects a span. `?` shows the shortcut help, and `Esc` closes it or deselects.
- **Tests:** `npm run test:ui` runs the Playwright keyboard and click tests.

## AWS X-Ray traces

- File: pass a BatchGetTraces response or the segment documents straight to build/render (auto-detected as `xray`).
- CLI (headless, **untested live**): `node <skill>/src/request-transit/scripts/fetch.mjs xray <1-xxxxxxxx-… or 32-hex id>` writes `traces/<id>.xray.json`, and `node <skill>/src/request-transit/scripts/fetch.mjs xray --find --filter 'fault = true'` lists candidate ids. Uses the user's AWS CLI credentials; never store keys.
- MCP (interactive): if the AWS Labs CloudWatch Application Signals MCP server is connected, call `get_xray_trace`, save the result to a file, then use the file. Check the saved shape first; it has not been verified live.
- X-Ray samples about 5% of requests by default, so a specific request may have no trace.

## Single-service traces

If every span comes from one service (a monolith, or `telemetrygen`), stations are operations instead: each child span is placed by its span name, with a trailing counter or id dropped so numbered spans share a station. The real service stays in the span's `service.name` attribute.

## Jaeger traces

- File: Jaeger v2 serves OTLP JSON at `/api/v3/traces/<id>` (or `/api/v3/traces?query.service_name=...` for a search). Save the response and pass it straight to build/render; the `{result: ...}` wrapper is auto-detected as `jaeger`. A search response can hold many traces: the one with the most spans is used unless `--trace-id` is given.

## Grafana Tempo traces

- File: pass a Tempo `/api/v2/traces/<id>` or `/api/traces/<id>` JSON response straight to build/render (auto-detected as `tempo`).
- API (headless): `node <skill>/src/request-transit/scripts/fetch.mjs tempo <trace_id>` with `TEMPO_URL` (+ optional `TEMPO_TOKEN`, or `TEMPO_USER`/`TEMPO_PASSWORD`, `TEMPO_TENANT`) writes `traces/<id>.tempo.json`; `tempo --find '{ status = error }'` lists ids. Tested on a mock server only.
- MCP (interactive): Grafana's MCP server (`get_tempo_trace`) or Tempo's built-in `/api/mcp` (`get-trace`). Save the OTLP JSON result to a file, then use the file. Don't use the `vnd.grafana.llm` format.

## Contract layer (optional: ask first)

This layer reads the user's source code, so it is never run by default.

1. **Ask the user before indexing.** For example: "Do you want me to build a contract index from your code, so each hop shows its expected request and response? It reads the service repos listed in transit.config.json and keeps the results only in .transit-cache/." Only continue on a clear yes.
2. If they agree and there is no `transit.config.json`, write one with them (see `references/config.md`). It maps each service name to a repo path and lists shared packages, route prefixes and infrastructure names.
3. Run `node <skill>/src/request-transit/scripts/transit.mjs index --config transit.config.json --print`. Results are cached per file hash in `.transit-cache/contracts/`. Never commit that folder.
   An index that already exists in `.transit-cache/` may be reused only when the user asked for contracts.
4. Build with `--contracts`: `node <skill>/core/build.mjs <trace> --contracts --out ./transit-out/<name>/transit.html`. Without the flag, no index is read and the panel says contracts are not indexed.
5. In the panel, matched hops show request and response cards with fields, required markers, a source badge (validator or type), a confidence dot and file:line. Infrastructure hops and unmatched hops show why. Report the unmatched hops to the user rather than guessing their shape.

Demo with no user code: `npm run index:example && npm run build:contracts`. This uses the synthetic sample app in `<skill>/src/request-transit/examples/astronomy-shop/`.
