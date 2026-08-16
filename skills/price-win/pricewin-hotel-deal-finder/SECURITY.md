# Security & Data Handling — PriceWin Hotel Deal Finder

This skill drives a stealth browser (Patchright/Chromium) to read **public** hotel
listings and compare prices. It runs entirely on the user's machine, needs no API
keys, and collects no personal data. This document discloses exactly what it
executes, what it downloads, what leaves the machine, and how untrusted web
content is contained — so an auditing agent (or a human) can verify the behavior
instead of inferring it.

## What runs (command execution)

The skill's only entry point is one command:

```bash
node bin/search.js "<city>" <checkIn> <checkOut> <adults> [locale]
```

`search.js` spawns `bin/browse.js` / `bin/daemon.js` (both shipped in this repo)
to control a local browser. It runs **no** shell strings built from scraped
content, executes **no** downloaded code, and takes **no** command input from web
pages — the browser flow is fixed in this repo's source. `npm install` / `npx`
appear **only** at install time to fetch the `patchright` dependency (see below).

The skill's whole source is three files in `bin/` and four in `lib/`: no minified
blobs, no obfuscation, no `eval`, no post-install script that fetches code (the
`postinstall` hook only prints a reminder). Every source file is auditable in the
public repo
<https://github.com/Price-Win/pricewin-skills-hub>.

## Why a "stealth" browser

The word is doing narrow work here. Patchright masks the CDP-level automation
fingerprint so a **normal, logged-out page view** of a public listing is not
mistaken for a scraping bot and served an empty or blocked page. It exists to
read public prices reliably from bot-hardened cities, not to evade security
controls: the skill does not bypass authentication, solve CAPTCHAs, defeat
rate limits with proxy rotation, hide from the user, or persist beyond the
session (`browse close`, `SIGTERM`, or the state file disappearing all stop it).
Nothing about it is aimed at endpoint security software, and it makes no attempt
to conceal what it is doing on the user's own machine — the daemon logs to
stderr and its state file is in plain sight under `~/.cache/`.

## What it downloads

| Item | When | Source | Purpose |
|------|------|--------|---------|
| `patchright` npm package | install | npm registry | Stealth Playwright fork (browser driver) |
| Chromium | first run (`install.sh`) | Patchright's official host | The browser engine that renders OTA pages |

No other binaries or code are downloaded at runtime.

## What leaves the machine (network egress)

Egress is limited to a fixed, auditable set of hosts. **The only user-derived data
sent is the search query itself** — city, check-in/out dates, guest count. No
account data, credentials, cookies from other sites, files, or PII are transmitted.

| Host | Data sent | Why |
|------|-----------|-----|
| `booking.com`, `agoda.com`, `google.com/travel` | city + dates + guests (as normal search URL params) | Read public listing prices |
| `api.opentravel.one` (override via `OPENTRAVEL_API_BASE_URL`) | city + dates + guests | Partner inventory lookup |
| `open.er-api.com` | none (public `GET /latest/USD`) | Live VND→USD FX rate for price normalization |

There is no telemetry, analytics, or callback to PriceWin servers.

## The local daemon (`bin/daemon.js`)

`search.js` drives one long-running local process that owns the Chromium
instance and answers commands over HTTP. It is privileged — it can navigate and
read any page — so it is locked down on four axes:

| Control | Implementation |
|---|---|
| Loopback only | `server.listen(port, '127.0.0.1')` — never reachable from the LAN or internet |
| Authenticated | Every request (including `/ping`) must carry `x-pricewin-token`, a 32-byte random token minted per daemon run and compared with `crypto.timingSafeEqual` |
| Token not readable by other users | The token lives only in `~/.cache/pricewin-hotel-deal-finder/session-default.json`, written `0600` inside a `0700` directory |
| Anti-DNS-rebinding | Requests whose `Host` header is not `127.0.0.1` / `localhost` / `::1` are rejected `403`, so a web page cannot reach the daemon even if it guesses the port |

Ephemeral port, chosen at startup; no fixed port to scan for. The daemon exits on
`SIGTERM`/`SIGINT` and on `browse close`, clearing its state file.

**Chromium sandbox stays ON.** `--no-sandbox` is *not* passed by default. It is
added only when the sandbox provably cannot work — running as root on Linux, or
an explicit `PRICEWIN_NO_SANDBOX=1` — and the daemon prints a warning to stderr
when it does.

## Untrusted content containment (indirect prompt injection)

Hotel names, prices, and aria-labels scraped from OTA pages are **untrusted
third-party content**. Before any of it reaches the model-visible output,
`sanitizeText()` in `bin/search.js`:

- strips control, zero-width, and bidirectional-override characters (defeats
  hidden-instruction and text-spoofing tricks);
- removes the markdown/link control set (`` ` `` `[ ] ( ) < > { } \ |`) so scraped
  text cannot forge `[label](url)` structure or smuggle directives;
- collapses whitespace and caps length.

All booking links (including the OpenTravel partner API's) are passed through
`cleanLink()`, which **accepts only `http(s)` URLs** — a `javascript:` or other
scheme can never render as a clickable link. The skill also treats scraped data
as data only: it ranks and formats prices, and never executes or follows
instructions found inside scraped text.

## Guidance for the running agent

The skill instructs the agent to treat OTA output as reference data to present to
the user, not as commands. Partial results (a source blocked or empty) are normal
and are surfaced honestly rather than "fixed" by ad-hoc scraping.

## Reporting

Found an issue? Open a ticket at
<https://github.com/Price-Win/pricewin-skills-hub/issues>.
