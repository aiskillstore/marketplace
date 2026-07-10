---
name: wonda-cli
description: Using the Wonda CLI to generate images, videos, music, and audio from the terminal — plus LinkedIn, Reddit, and X/Twitter research and automation
---

# Wonda CLI

Wonda CLI is a content creation toolkit for terminal-based agents. Use it to generate images, videos, music, and audio; edit and compose media; publish to social platforms; and research/automate across LinkedIn, Reddit, and X/Twitter.

## Install

If `wonda` is not found on PATH, install it first:

```bash
# npm
npm i -g @degausai/wonda

# Homebrew
brew tap degausai/tap && brew install wonda
```

## Setup

- **Auth**: `wonda auth login` (opens browser, recommended) or set `WONDA_API_KEY` env var
- **Verify**: `wonda auth check`

### OAuth connector auth

Claude web and Cowork connectors use Wonda's OAuth 2.1 flow instead of a CLI
API key field. The connector signs in through Wonda in the browser, grants the
requested account access, and receives OAuth tokens bound to the Wonda API
resource. The server swaps those tokens to the account's internal API key only
inside Wonda, so agents and connector hosts never see the `sk_...` key. For the
CLI and local stdio MCP path, keep using `wonda auth login` or
`WONDA_API_KEY`.

### Claude Cowork local relay

Claude Cowork (the desktop app) runs local MCP servers on the host, so it can
load the `.mcpb` bundle or a local stdio `wonda-mcp` config directly, WAB
writes included (verified 2026-07-07). Claude web cannot. The Wonda local
relay is the alternative path: it lets the REMOTE connector (web or Cowork)
run actions on the user's own Mac and residential IP without any local MCP
config:

1. Open `https://wonda.sh/download` while signed in and install the notarized
   Mac package.
2. Pair the relay with `wonda relay pair` or the first-run browser handoff. This
   uses the existing `cli-auth` flow with a relay-scoped `wrelay_...`
   credential stored in the macOS Keychain. Do not ask the user to paste an API
   key or device code.
3. Open `https://wonda.sh/setup`, connect LinkedIn, X, and Reddit through the
   headful local WAB, then approve the Wonda connector once in Claude.

The engine policy is `auto | my_machine | cloud`. `auto` uses the local relay
when it is online and cloud otherwise. `my_machine` must not silently fall back:
if the relay is offline, ask whether to switch to cloud.

### Organizations & spend context

Wondercat orgs are shared wallets with their own seats and billing.
Members can spend from the org wallet (instead of their personal credits)
by switching context:

- `wonda organizations list` (aliases: `wonda orgs list`, `wonda org list`) — see every org you belong to with your role and seat plan in each.
- `wonda use --org <slug>` — sticky org context for this machine. Sets
  `X-Wonda-Org` on every request; holds, charges, and `wonda balance`
  route through the org wallet.
- `wonda use --personal` — back to personal.
- `wonda usage` — spend-only usage summary (total + per-model + per-project
  breakdown) for a period (`--month 2026-05`, or `--from`/`--to`; defaults
  to the current month, UTC). `--project <name>` restricts the report to one
  project. In org context it reports org-wide usage including a per-member
  breakdown — admin/owner role required. Admins can also download a full
  Excel report from the org page on the web.

### Projects (spend tagging)

Projects attribute spend to a named workstream for monitoring. Agents
should check the active project at task start (`wonda use` prints it) and
set one per task when the operator monitors spend by project:

- `wonda use --project <name>` — sticky: every subsequent charge carries
  the project (in `wonda usage`, the API, and the org Excel report).
  `wonda use --no-project` stops tagging; switching org/personal context
  clears the project automatically (projects are per-scope).
- `--project <name>` on any command — one-off override for that invocation.
- `wonda project list|create|delete` — manage the registry in the active
  scope. Org projects are created by org admins/owners only; personal
  projects are self-service. Tagging against a name that doesn't exist
  fails with `unknown_project` (no silent new buckets, so typos can't
  split the monitoring data).

`wonda topup` always tops up your **personal** wallet, regardless of
context. Topping up the org wallet (and configuring auto top-up) is
admin-only and happens on the web at `/organizations/<slug>`. If a
member runs out of org credits, the error tells them to ask an admin or
switch back to personal — they cannot top up the org wallet from CLI.

Roles inside an org are separate from the seat plan:

- **Owner**: the original creator. Cannot be demoted or kicked. Can transfer ownership to another member from the org page (rare).
- **Admin**: can invite (single or bulk via paste), kick, change roles, change seats, top up, configure auto top-up, change monthly limits.
- **User**: can only spend within the org wallet (subject to a per-member monthly limit if the admin set one).

A paid org seat (`WONDA` / `WONDA_PREMIUM`) grants the same paid feature access (skills, etc.) as a personal paid plan, but only while in org context. `wonda use --personal` falls back to the user's personal account plan.

### Access tiers

Wonda is paid-only: every product surface (generation, media, publishing, scraping, analysis, skills, cloud twin) requires a paid plan. New accounts get no credits and no product access until they subscribe.

| Tier                                            | Access                                                                                                                                                                                                                                                                                                                      |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Anonymous** (temporary account, no login)     | No product access. The CLI mints a temporary account on first run, but it reaches only the local commands below plus the auth/billing endpoints. Run `wonda auth login`, then subscribe.                                                                                                                                    |
| **Free** (logged in, no paid plan)              | No product access. Subscribe at https://wonda.sh/account to use the product.                                                                                                                                                                                                                                                |
| **WONDA** (`$19.99/mo`, "Pro")                  | Everything except cloud twin: generation (`image/generate`, `video/generate`, ...), media upload/download, publishing, scraping, analytics, video analysis, skills (`wonda skill install/list/get`), transitions, clipping, email, reddit/linkedin account creation, styles, brand.                                         |
| **WONDA_PREMIUM** (`$49.99/mo`, "Premium")      | Everything in WONDA, plus **cloud twin** (`wonda twin`: provisioning, scheduled runs, streamed login) with antidetect / shadowban protection, no caps, and US account creation.                                                                                                                                             |
| **Flagged** (per-account PostHog kill-switches) | Included in the paid plan but still gateable by a per-account flag: `wonda reddit signup` (redditAccountCreationEnabled), `wonda email` (emailServerApiEnabled), public LinkedIn profile enrichment (linkedinProfileEnrichmentEnabled).                                                                                     |
| **Local** (no API call, no credits, no plan)    | Run entirely on your machine, so they work without a plan: `wonda brand extract <url>` (no `--save`), `wonda compose motion`/`wonda compose text`, `wonda wab record <url>`, `wonda edit ...` ffmpeg primitive transforms on local files, and `wonda doctor`. The Chromium-backed ones need a one-time `wonda wab install`. |

If a command returns a `403` (`paid_plan_required`), subscribe at https://wonda.sh/account.

### Voice cloning

Clone a voice from a 10s+ audio clip and use it in TTS. Hard limit: 20 cloned voices per account. Cost: $1.50 per clone.

```bash
# Clone from a local file (auto-uploads to media library first)
wonda voice create "Andu" --file ./sample.mp3 --description "My voice"

# Clone from existing wonda media
wonda voice create "Brand" --media-id <uuid>

# Optional source-audio preprocessing
wonda voice create "Clean" --file ./raw.wav --noise-reduction --normalize-volume

# List cloned voices (each row reports isExpired and expiresInDays)
wonda voice list

# One voice
wonda voice get <voice-id>

# Rename / re-describe (local only, no provider call)
wonda voice update <voice-id> --name "New Name" --description "..."

# Delete
wonda voice delete <voice-id>
```

**Use a cloned voice in TTS** by passing the `providerVoiceId` from `voice get` as `voiceId` to `/audio/speech`:

```bash
wonda audio speech "Hello world" \
  --model minimax-speech-2-8-hd \
  --params '{"voiceId":"<providerVoiceId>"}'
```

**7-day expiry**: cloned voices that haven't been used in TTS within 7 days are automatically expired. Running TTS with a cloned voice automatically refreshes its expiry. Idle voices that lapse must be re-cloned ($1.50 again).

### Credentials vault

Persist logins created on external platforms (Instagram, TikTok, Twitter, etc.) so they can be reused on the next run. Passwords are AES-256-GCM encrypted with a server-side key and only decrypted on `get`.

```bash
# Create
wonda credentials create --website instagram.com --username myhandle \
  --email me@example.com --password-stdin <<< "hunter2" \
  --metadata '{"signup_source":"wonda-email"}'

# List (passwords omitted)
wonda credentials list --website instagram.com

# Get full record including decrypted password
wonda credentials get <id>

# Update any field (use --password-stdin to rotate; --username "" to clear)
wonda credentials update <id> --username newhandle

# Delete
wonda credentials delete <id>

# Fetch + record why you're using it in one call — POST, not GET, because
# it writes a 'used' event with the reason. Prefer this over `get` whenever
# you can articulate the reason.
wonda credentials use <id> --reason "instagram signup flow"

# See recent events (created / used / rotated / updated) for audit
wonda credentials events <id>
```

Fields: `website` (required — typed input like `insta` is canonicalized to `instagram.com`), `username`, `email`, `password` (required), `metadata` (arbitrary JSON). At least one of `username` / `email` must be present. Multiple records per `(website, username)` are allowed — dedupe on your side if you need to.

**Event log**: every `credentials get`/`use`, `create`, password rotate, and other updates are recorded as events on the credential (actor: `cli` | `web` | `system`). Use `credentials events <id>` or the web UI's history icon to audit. The event log is append-only and cascades on credential delete.

### Global output flags

All commands support these output control flags:

- `--json` — Force JSON output (auto-enabled when stdout is piped)
- `--quiet` — Only output the primary identifier (job ID, media ID, etc.) — ideal for scripting
- `-o <path>` — Download output to file (implies `--wait`)
- `--fields status,outputs` — Select specific JSON fields
- `--jq '.outputs[0].media.url'` — Filter JSON output with a jq expression

### CLI announcements & deprecation warnings

On every command the CLI polls `GET /api/v1/updates` (anonymous, 1h cache in `~/.wonda/state.json`) for active announcements: deprecation notices, incident heads-ups, upgrade prompts. Messages are printed to stderr only, so stdout/JSON stays clean for piping.

Per-request deprecation hints arrive as the standard `Warning: 299 - "<message>"` HTTP header and are surfaced to stderr by the CLI's HTTP client as `[deprecated METHOD /path] <message>`.

Silence both channels with `WONDA_QUIET=1` (env var) or `--quiet` (flag). Disable just the network checks with `WONDA_NO_UPDATE_CHECK=1`.

### WAB / Wonda Automation Browser (`wonda wab`)

The Wonda Automation Browser (WAB) is a premium stealth antidetect browser, hardened so platforms cannot fingerprint it as automation. `wonda wab` is the one command for the antidetect Chromium stack (an undetected Playwright fork). It has two faces:

- **Authenticated sessions.** One persistent headful Chromium per persona that holds signed-in sessions for LinkedIn, X, Reddit, and friends. The CLI spawns it on demand, lets it idle out, and routes platform reads/writes through it whenever a command runs `--via wab`. Cookies live in the persona's Chromium profile, not in `~/.wonda/config.json`.
- **Anonymous capture.** `wonda wab record <url>` (and `wonda brand extract`) drive an ephemeral Chromium with a fresh fingerprint, no persona, no cookies. See the `record` block below.

The mental model: you have **accounts** (one identity per platform). Each platform command routes to that account's cookies via either the flat JSON store (`--via cookies`, fast, no Chromium) or the account's **persona** (`--via wab`, live antidetect Chromium). A persona is the Chromium envelope that can hold multiple accounts under one fingerprint. In almost every case the persona is auto-created on first `--via wab` use, named after the account, so you never type a persona name.

The local `wonda.mcpb` Desktop Extension uses this same local WAB path from Claude Desktop or Claude Code: platform cookies stay on-device, reads use local cookies, and writes use the local WAB. Claude web and Cowork need the remote MCP connector instead.

**Native login is the default for a new persona.** `wonda wab login <persona> <platform>` opens a headful WAB window and you log in there. The session is minted INSIDE the WAB, so it is independent (logging out of the same account in an unrelated Chrome cannot revoke it) and the cookies are born under the WAB's own fingerprint, so session and browser identity stay coherent. A brand-new persona auto-created on first `--via wab` use chains straight into this flow on a TTY. Pasting cookies from another browser (`wonda linkedin auth set`, `wonda x auth set`, ...) still works and is the explicit fallback, but a hand-pasted `li_at` on a novel WAB fingerprint is the highest-risk shape.

```bash
wonda wab install                             # one-time: npm install + stealth-browser Chromium (shared by sessions, record, brand extract)
wonda wab start [account]                     # spawn (offscreen by default; --visible to show)
wonda wab stop [account]                      # graceful shutdown
wonda wab show [account]                       # peek a background WAB on-screen to watch it (suspends the macOS focus guard); starts it offscreen first if needed
wonda wab hide [account]                       # send a surfaced WAB back offscreen, resume silent background operation
wonda wab screenshot [account]                 # capture the persona's current page as a PNG without surfacing the window; --json returns inline base64, --output writes a file, --tab/--full-page optional
wonda wab menubar                              # macOS menu-bar control (🐱): click to Show/Hide running WABs; --stop to remove
# macOS Dock menu: right-click a running WAB's Dock tile (the 🐱) for "Show on screen" / "Send to background" (same as wab show/hide). Each running persona has its own Dock tile and its menu controls only that persona. Opt out with WAB_DOCK_MENU=0.
# macOS: a background WAB no longer steals focus or flashes the menu bar / Dock when it opens a new tab; the Dock tile stays, it just never comes to the foreground until you `wab show` it.
wonda wab status                              # list personas + last activity
wonda wab login <account> <linkedin|x|reddit|instagram> # RECOMMENDED for a new persona: open headful window, user logs in, session minted in-WAB (independent + fingerprint-coherent)
wonda wab check <account> <linkedin|x|reddit|instagram> # non-interactive session-alive probe
wonda wab bind <persona> --x <acct> --reddit <acct> --linkedin <acct>  # multi-account power-user path: bind N accounts to ONE persona
wonda wab record <url>                        # anonymous one-shot capture (no account, no cookies), see below
wonda wab sync-cookies [account]              # force wab → disk cookie sync now (don't wait for the 10-min timer)
wonda wab logs [account] --tail 100           # tail driver.log (--audit for structured per-command log)
wonda wab errors --tail 20 --since 24h        # tail the cross-persona action-failure log
wonda wab top-failures --since 7d             # rank local WAB failures by platform/action/reason, joined with DOM recovery stats
wonda wab top-failures --platform x --json    # machine-readable local failure ranking
wonda wab bundle-failures list                # recent action failure bundles (one per failed run: screenshot, dom, visible-elements, cookies-summary REDACTED)
wonda wab bundle-failures show <id>           # print manifest + file tree for a bundle (id = unix-ms-ts prefix)
wonda wab bundle-failures ship <id>           # zip to ~/Downloads/wonda-failure-<id>.zip for sharing
wonda wab bundle-failures prune               # remove bundles older than 30d (or --max-per-persona, --all)
# Telemetry: on every wab action failure we report (action, platform, reason, error-string, has_bundle, cli_version) as a wab_action_failed PostHog event so maintainers can spot platform rotations across users. NO bundle contents, NO cookies, NO DOM, NO screenshots leave the user's machine. Opt out: WONDA_TELEMETRY_DISABLED=1. For server-side breakdowns, group `wab_action_failed` by `platform`, `action`, `reason`, and `has_bundle` in PostHog. Locally, `wonda wab top-failures` reads only `~/.wonda/wab/errors.jsonl` and persona-local `dom-recoveries.jsonl`, then shows count, last seen, recovered rate, bundle count, and a sample bundle id.
wonda wab migrate-legacy                      # copy a legacy WAB-driver profile into a persona slot
wonda wab restore <persona> [timestamp]       # restore from an hourly snapshot (--list to enumerate)
wonda wab backup disable                      # opt out of auto-push (on by default; existing cloud backups untouched)
wonda wab backup enable                       # opt back in (auto-push synced cookie JSON to wondercat after every disk sync)
wonda wab backup status                       # show config + remote inventory
wonda wab backup push [account]               # one-shot manual push for all platform bindings
wonda wab backup pull [account]               # guarded restore to ~/.wonda/<platform>-cookies/<account>.json; refuses non-empty local unless --force
wonda wab backup pull [account] --dry-run     # preview restores without writing
wonda wab backup list                         # inventory of cloud backups, including device/provenance metadata when available
wonda wab backup delete <plat> <persona> [acct] # remove one backup
wonda wab cookies list                        # explicit cookie backup inventory, metadata only
wonda wab cookies status [account]            # local cookie files plus cloud backup rows
wonda wab cookies port <plat> <persona> [acct] --from-device <id|label> # safely port one selected cloud row to this machine
wonda wab config set <persona> <key> <value>  # persist per-persona spawn defaults (idle-timeout, locale, visible, interactive, proxy_url, timezone, geo_lat/lon)
wonda wab config get <persona>                # print a persona's persisted config
```

**Local browser proxy (`proxy_url`).** By default the local WAB dials direct (your own IP). Set `wonda wab config set <persona> proxy_url managed` to route the LOCAL browser through your account's minted twin proxy, so it shares the same egress as the cloud twin (useful for IP continuity or a VPN/office/CGNAT network). A literal `socks5://…`/`https://…` value is a manual override instead; unset clears it back to direct. The proxy is optional: if minting is disabled for the environment or unavailable, the browser falls back to a direct dial.

Lifecycle commands take an `--account` (e.g. `wonda wab login <account> linkedin`); the persona is auto-derived from the account name. `wonda wab bind` is the one place a persona is named explicitly: use it when one Chromium must host accounts that have different names per platform.

**Anonymous capture (`record`).** `wonda wab record <url>` records a URL to webm in an ephemeral Chromium (fresh fingerprint each call, no persona, no cookies). Use it for cookie-banner-gated pages (Notion public shares, pdf.js renders, any site where bare Playwright trips a bot check) and marketing demo capture.

```bash
wonda wab record https://example.notion.site/page \
  --output recording.webm \
  --duration 5 \
  --viewport 960x1080 \
  --inject-js scripts/page-script.mjs   # optional: runs after load, before timer starts

# Transcode webm to mp4 at 30 fps (the stealth browser records webm/VP8)
ffmpeg -y -i recording.webm -t 5 -r 30 -an \
  -c:v libx264 -pix_fmt yuv420p -crf 18 recording.mp4
```

The `--inject-js` file is wrapped in an async IIFE so top-level `await` works. It runs AFTER `domcontentloaded` + `networkidle` + 400 ms paint settle, BEFORE the duration timer starts. Any `await` inside counts against the recording window. Use it for dark-theme injection, cookie-banner removal, scroll animations, anything that needs to happen in page context.

Node.js requirement: wonda needs Node >= v20 on PATH. Brew users get it via the `node` dependency; npm users have it by definition; install.sh users may need `brew install node` (or any Node distribution). If Node is missing, `wonda wab install` fetches a private copy into `~/.wonda/node/`.

**Cookie cloud backup.** On by default (opt out per machine with `wonda wab backup disable`). The WAB driver pushes the synced cookie JSON for each bound platform to the wondercat backend after every wab → disk sync and graceful shutdown; auto-push no-ops when no api_key is configured. Encrypted at rest server-side (AES-256-GCM) when `SOCIAL_COOKIES_KEY` is set, else plaintext jsonb; the wire payload is always plaintext because the server holds the key. Cookie values are never printed by list/status/port commands.

Recovery is guarded. `wonda wab backup pull <account>` and `wonda wab cookies port <platform> <persona> [account]` refuse to overwrite a non-empty or newer local cookie file unless `--force` is passed. Forced writes create a hidden `.before-pull-*` backup first. Use `--dry-run` to inspect planned writes. When the backend exposes multiple device rows for the same platform/persona/account, use `wonda wab cookies port ... --from-device <id|label>` so the source row is explicit.

Current backend compatibility: legacy servers still expose one last-write-wins row per `(account, platform, persona, account_label)`. Newer servers may include `device_id`, `device_label`, `source`, `status`, `generation`, and `provenance`; the CLI displays those fields when present and shows legacy rows as device `legacy`.

Source lives at `cli/wondercat/wab/`. The driver is `launch.mjs` and per-platform action scripts under `actions/<platform>/`.

**Per-command transport (`--via`).** `linkedin`, `x`, and `reddit` commands take:

- `--via cookies|wab`: `cookies` reads the flat per-account JSON store (fast, no Chromium); `wab` routes through the account's persona Chromium (cookies + TLS fingerprint inherit from a real browser session). An unsupported value errors loudly rather than silently downgrading.
- `--via public`: paid public-data API where a command explicitly supports it. For LinkedIn this avoids logged-in cookies and WAB profile reads, and uses the public scrape task route for `wonda linkedin profile` and `wonda linkedin enrich`.
- `--account <name>`: which on-disk identity to use (cookie filename / persona). Persona resolution is implicit: the first `--via wab` use auto-creates a persona named after the account and (on a TTY) chains straight into login.

**Defaults differ for reads vs writes.** Read commands (profile, posts, search, timeline, etc.) default to `cookies` (direct API), because that path is fast and detection-safe. Write / engagement commands (post, comment, like, follow, connect, message, mute, repost, delete) default to `wab`, because the cookie-API path triggers anti-abuse heuristics on LinkedIn / X / Reddit at any meaningful volume. Pass `--via cookies` to a write command if you explicitly want the legacy API path (where the command supports it).

**Commands that require `--via wab`.** A few commands have no cookie path and only run through the Wonda Automation Browser: `wonda linkedin comment`, `wonda linkedin reply-comment`, `wonda linkedin mute`, `wonda linkedin follow`, `wonda linkedin edit-post`, `wonda linkedin edit-comment`, `wonda linkedin delete-comment`, `wonda linkedin post --media`, `wonda x delete`, `wonda x reply --attach`, `wonda x dm send`, `wonda x dm accept`, and `wonda x dm start`. On these, the default already resolves to wab (one stderr line noting it); passing `--via cookies` explicitly errors. Reddit's writes (`vote`, `comment`, `subscribe`, `save`, `unsave`, `delete`, and subreddit `submit`) are likewise wab-only.

**Where it runs (`--engine`).** `--via` picks the transport (browser vs. cookies); `--engine` picks the location, and the two are orthogonal. Values: `local` (this machine's WAB), `cloud` (the account's cloud twin, reached through the twin-action API with the control-session warm-up hidden behind a blocking wait), or `auto` (the default). `auto` resolves to `local` when the identity lives on this machine and `cloud` when it only exists as a cloud twin (a persona with no local footprint, or one cached as `home=cloud` from `wonda twin provision`). So `wonda linkedin like <url> --account <twin> --engine cloud` runs the like on the cloud twin with the same grammar as the local command. `--via` works the same on both engines: writes default to `wab`, and `--via cookies` is honored on the verbs that support it locally (`connect`, `like`/`unlike`, `send-message`); the wab-only cases (`comment`, comment reactions, and `--dry-run` sends) reject `--via cookies` on cloud exactly as they do locally. Wired for LinkedIn (`connect`, `like`/`unlike`, `comment`, `reply-comment`, `edit-comment`, `send-message`, `follow`, `mute`, `delete-post`, `edit-post`), X (`like`/`unlike`, `bookmark`, `retweet`/`unretweet`, `follow`/`unfollow`, `delete`), Reddit (`vote`, `subscribe`, `save`/`unsave`, `delete`), and Instagram (`comment`); other verbs run local only. `--engine` is accepted at the platform level (so both `linkedin --engine cloud connect` and `linkedin connect --engine cloud` work) but honored only on the wired verbs; passing it to a read or an unwired write is a clear error, not a silent no-op. **`wonda twin run-action` is deprecated in favor of `<platform> <verb> --engine cloud`** (it still works so running agents are not broken). On cloud, `like` supports plain likes and reactions (`--reaction`, routed to the `react` action); only comment reactions (`--comment`) stay local for now. `auto` resolves to local when a persona has no local footprint and no cloud twin (so first-use auto-create still works), and to cloud when a cloud twin exists for it. An explicit `--engine cloud` always runs on the cloud twin and never falls back to a live local relay. Note the cloud `--via` override takes effect once the twin-runner image is redeployed.

**Per-account credentials.** Cookies live in per-account JSON files on disk:

- `~/.wonda/x-cookies/<account>.json`
- `~/.wonda/reddit-cookies/<account>.json`
- `~/.wonda/linkedin-cookies/<account>.json` (auto-migrated from the legacy single-file format)

Pass `--account <name>` to `auth set` to keep multiple logins side-by-side. The binding is recorded against the account's persona in `account-bindings.json` and, if the persona's Chromium is running, the rotated cookies get pushed into the live context. The driver also syncs cookies back to disk every 10 minutes (and on graceful shutdown), so rotated cookies (ct0 cycles, token_v2 server-side refresh, etc.) flow back to the cookies path without manual re-paste.

### Action rate limits

Every platform command (`linkedin`, `x`, `reddit`, `instagram`), reads AND writes, runs through a per-profile rate-limit guard so a burst doesn't trip a platform's shadow-ban / anti-abuse heuristics. Accounting is per `(platform, account)` in a rolling 24h window, logged per profile under `~/.wonda/wab/personas/<persona>/` (so a cloud twin's caps persist across runs).

- **Reads** are _paced_, never blocked: spacing is jittered to keep a profile under `read_per_min` (75/min default), holding across separate invocations.
- **Writes** are checked against per-bucket daily caps. The LinkedIn defaults (other platforms track + count toward the total/day but have no per-type write cap by default):

  | bucket                   | commands                              | safe        | max |
  | ------------------------ | ------------------------------------- | ----------- | --- |
  | outreach                 | `connect` + `send-message` + `inmail` | 20          | 40  |
  | post                     | `post`                                | 3           | 5   |
  | comment                  | `comment`, `reply-comment`            | 10          | 20  |
  | react                    | `like`                                | 25          | 50  |
  | visit                    | `visit`                               | 15          | 30  |
  | search                   | `search`, `search-posts`              | 25          | 50  |
  | **total** (all non-read) | any of the above                      | warn at 90% | 100 |

`salesnav search` (Sales Navigator) is exempt: it carries no Commercial Use Limit, so it paces as an uncapped read instead of counting toward the `search` cap or the total/day.

Caps are **SOFT by default**: an over-safe / over-max action prints a shadow-ban-risk warning to stderr and **proceeds**. Pass `--hard` (or set `mode: hard` in config) to make over-cap writes **abort** (exit 1) instead.

`wonda actions` is a JSON data query (not a dashboard) for reading a profile's rolling-24h usage vs caps on demand; the caps/pacing/warnings run silently in the live hook regardless.

```bash
wonda actions                        # rolling-24h usage per profile vs caps, as JSON
wonda actions --persona <persona>        # one profile
wonda actions --platform linkedin    # filter to one platform
wonda actions sync                   # flush local action/health events to your Wonda account
wonda actions sync --persona <persona>   # flush one profile's ledgers
wonda linkedin post "…" --hard       # enforce caps as hard limits for this command
```

When an API key is configured, the local ledgers (actions log, WAB audit/error logs, cookie provenance) also sync to your Wonda account-health record automatically in the background on every command: best-effort, batched, and idempotent (a stable client event id per record means retries never double count), so offline use keeps working and sync catches up later. `wonda actions sync` forces a full flush and prints the server's insert/dedup counts; without an API key it is a silent no-op. Only event metadata travels, never cookie values or failure bundles. `WONDA_TELEMETRY_DISABLED=1` turns the background sync off.

Override / disable / hard-mode via `~/.wonda/config.json` under `action_limits` (caps are clamped to safety floors/ceilings so an override can loosen but not silently disable the guard):

```json
{
  "action_limits": {
    "mode": "hard",
    "read_per_min": 75,
    "total_per_day": 100,
    "buckets": { "linkedin": { "outreach": { "safe": 15, "max": 30 } } }
  }
}
```

### Config keys

`wonda config get|set|list` keys:

- `api-key`: your wondercat API key.
- `base-url`: API base (defaults to prod, set to `https://staging.api.wondercat.ai` for staging).
- `default-account`: account used when a platform command doesn't pass `--account`.
- `wab-backup-enabled`: `true`/`false` for cookie cloud backup (same as `wonda wab backup enable`/`disable`). On by default; only an explicit `false` disables it.

Transport is NOT a config key. Each command picks it per kind (reads default to `cookies`, writes / engagement default to `wab`), identically on every platform. Override it per command with `--via cookies|wab` (where the platform supports it).

## How to think about content creation

You are a marketing director with access to a full production toolkit. Before touching any tool, think:

1. **What product category?** (beauty, food, tech, fashion, fitness, etc.)
2. **What format performs for this category?** (UGC memes for everyday products, cinematic for luxury, before/after for transformations, testimonial for services)
3. **What's the hook?** (relatable scenario, surprising twist, aspirational lifestyle, social proof)
4. **What specific scene?** (not "product on table" but "person discovering the product in a funny situation")

## Decision flow

When asked to create content, follow this order:

### Step 1: Gather context

```bash
wonda brand                                                    # Active brand: identity, colors, fonts, logos, products
wonda brand list                                               # All brands owned by this account/org
wonda brand show <brand-id>                                    # Specific brand
wonda brand extract https://stripe.com                         # Local-only: writes ./output/stripe.com/{DESIGN.md, tokens.json, assets/}
wonda brand extract https://stripe.com --save --make-active    # Local + persist + activate (the common path)
wonda brand extract https://stripe.com --save --name "Stripe"  # Persist with a custom name
wonda brand extract https://stripe.com --no-output --save      # Don't write to disk, persist only
wonda brand save                                               # Persist the most recent ./output/<domain>/ dir to the server
wonda brand save --from ./output/stripe.com --make-active
wonda brand pull <brand-id>                                    # Download a saved brand back to ./output/<domain>/
wonda brand activate <brand-id>                                # Set as the active brand
wonda brand upload-logo <brand-id> https://acme.com/logo.svg   # Attach a logo by URL (--variant wordmark|icon|dark|light)
wonda brand upload-font <brand-id> https://acme.com/Geist.woff2 --weight 700
wonda brand delete <brand-id>
wonda analytics instagram                                      # What content performs well
wonda scrape social --handle @competitor --platform instagram --wait  # Competitive research (if relevant)

# Cross-platform research (if relevant)
wonda x search "topic OR keyword"                              # Find conversations on X/Twitter
wonda x user-tweets @competitor                                # Competitor's recent tweets
wonda reddit search "topic" --sort top --time week             # Reddit discussions
wonda reddit feed marketing --sort hot                         # Subreddit trends
wonda linkedin search "topic" --type COMPANIES                 # LinkedIn company/people research
wonda linkedin profile competitor-vanity-name                  # LinkedIn profile intel
```

### Step 2: Check content skills

Content skills are step-by-step guides for common content types. Each skill tells you exactly which models, prompts, and editing operations to use — and in what order. ALWAYS check skills before building from scratch.

Skills are **server-hosted, per-account, and editable** (the same model as `wonda brand save`) — you don't download a folder of `.md` files you own. Wonda ships a canonical set of **default** skills, served read-only as the fallback. Pull them live for a task; fork a default into your own copy when you want to tweak it; Wonda keeps full version history. `skill list` shows your effective skills (defaults overlaid with your own edits), and flags any fork whose default has since changed.

```bash
wonda skill list                                # Browse your effective skills (defaults + your own); forks with a changed default are flagged
wonda skill get <slug>                          # Pull a skill's full step-by-step guide live to stdout
```

<!-- SKILLS_TABLE_START -->

**Default skill catalog** (live source: `wonda skill list`, which also shows your own forks/edits and flags drift):

**video**

| Slug                | What it does                                                                                                                                                                                                                |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| product-demo-video  | Premium ~15s multi-beat product demo, a dev hits a pain point, runs your tool, it does something real on screen, the payoff lands, then a branded CTA, built as one HTML composite captured per-frame and muxed with ffmpeg |
| product-video       | Product/scene video from an image or from scratch                                                                                                                                                                           |
| split-screen-demo   | 5-second 16:9 LinkedIn loop, source doc to designed slides comparison ending on a CTA that crosses out the competitors                                                                                                      |
| tiktok-ugc-pipeline | Reverse-engineer a viral reel, generate 5 variations, auto-post                                                                                                                                                             |
| ugc-dance-motion    | Dance and motion transfer video from image + reference                                                                                                                                                                      |
| ugc-hook-brainstorm | 25 graded scroll-stopping UGC hooks, hot casting, iPhone 16 aesthetic, psychological levers                                                                                                                                 |
| ugc-reaction-batch  | Batch produce TikTok-native UGC reaction videos                                                                                                                                                                             |
| ugc-talking         | Talking-head UGC ad, single clip, two-angle PIP, or long-form 20s+                                                                                                                                                          |

**image**

| Slug                              | What it does                                                                                                                                                                                                                                                                                         |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| creative-static-ads               | High-converting single-frame static ads, 6 conversion pillars, 8 format archetypes, 8 psychological hooks                                                                                                                                                                                            |
| linkedin-media-premium-generation | Render a single stop-the-scroll LinkedIn hero card (1920x1080) using a layered visual vocabulary: italic-serif headline, real product screenshot, paper grain, floating social-proof cards. Six layout patterns sharing the same DNA. Wonda CLI sourcing for real quotes from X / LinkedIn / Reddit. |
| premium-static-ads                | Pixel-perfect HTML+Playwright static ads with brand extraction (`wonda brand extract`). Real fonts, exact tokens, reproducible templates                                                                                                                                                             |
| tiktok-slideshow-carousel         | 3-5 slide TikTok carousel that looks organic but promotes your product, hook, bridge, reveal                                                                                                                                                                                                         |

**social-research**

| Slug                      | What it does                                                                                                                          |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| analyze-reel              | Analyze a viral reel or TikTok, viral breakdown + 5 adapted content ideas                                                             |
| linkedin-engager-intel    | Pull every commenter + reactor on a LinkedIn post with profile URLs for warm outreach                                                 |
| linkedin-icp-qualify      | Enrich LinkedIn engagers with their current employer (industry, headcount, HQ, description) so you can filter for ICP fit             |
| linkedin-social-listening | Paste any keyword, pull every recent post that mentions it, then enrich each post's engagers into an ICP-qualified outreach shortlist |
| reddit-subreddit-intel    | Scrape top posts, analyze virality patterns, generate post ideas                                                                      |
| twitter-influencer-search | Find micro-influencers and amplifiers for product launches                                                                            |

**strategy**

| Slug                 | What it does                                                                                                                                                                                                                                                         |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| linkedin-post-system | Turn a raw idea into a LinkedIn post that matches proven formats and the user's exact voice. Bootstraps the user's voice corpus via wonda linkedin profile/posts, maps the idea to one of 28 proven content formats, drafts 2 variants with anti-AI-slop guardrails. |
| marketing-brain      | Strategy brain for hooks, visuals, ads, and competitive analysis                                                                                                                                                                                                     |

**utility**

| Slug                   | What it does                                                                                                                                                                                               |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| extract-apply-style    | Extract a visual style from any image, then generate new subjects in that style                                                                                                                            |
| ffmpeg                 | Local deterministic media transforms, trim, replace audio, burn captions, social formatting, scene splitting, silence cut, frame extraction, analysis artifacts                                            |
| image-edit             | Edit existing images, img2img, background removal, crop, text overlay, vectorize                                                                                                                           |
| slide-generation       | Generate branded slide decks from any content source, codebase, Notion notes, or Google Docs                                                                                                               |
| software-ui-mockups    | Render real software UIs, terminal/CLI TUIs, the Chrome browser window, the macOS desktop, pixel-accurately in HTML for demo videos, slides, screenshots and docs, from the program's real source of truth |
| tiktok-caption-presets | TikTok-style textOverlay and animatedCaptions presets applied via wonda edit --preset                                                                                                                      |

<!-- SKILLS_TABLE_END -->

**Editing skills (optional).** When a default doesn't quite fit, fork and edit it instead of working around it. Editing a default forks it into your account automatically:

```bash
wonda skill create my-ugc --from ugc-talking    # Fork a default into your own editable copy
wonda skill edit my-ugc --editor                # Record a new version (opens $EDITOR; or --file <md> / stdin)
wonda skill diff <slug>                          # See what changed in the default since you forked it (drift)
wonda skill refactor <slug> --editor             # Re-base your fork onto the updated default, clears the drift hint
```

**If a skill matches** → `wonda skill get <slug>`, read it, adapt to context, execute each step.

**If no skill matches** → build from scratch (Step 3).

### Step 2.5: Decide whether finishing should be local

Not every media task should go back through Wonda editing. Use this routing rule:

- Use `wonda` for AI generation, AI transcription/alignment, scraping, publishing, hosted transitions, and workflows that need media IDs or remote jobs.
- Use local `ffmpeg` for deterministic transforms on files you already have or can download: trim, crop/scale/pad, concat (merging multiple clips), replace audio, extract audio/frame, reverse, normalize for delivery, burn captions, split scenes, cut silence, and build analysis artifacts. **Always merge clips locally** — server-side merge can hang for 30+ minutes once any input exceeds ~7MB.

When a task starts from a Wonda media ID but the actual edit is deterministic, move it to local files first:

```bash
wonda media download <mediaId> -o ./input.mp4
```

Before any local ffmpeg work:

```bash
which ffmpeg
which ffprobe
ffmpeg -version
ffprobe -v error -show_format -show_streams -of json ./input.mp4
```

Font rule for local caption/text work:

- Prefer an explicit font file path over a family name.
- Never assume a font exists. Check first with `fc-match`, `fc-list`, `/System/Library/Fonts`, `/Library/Fonts`, `~/Library/Fonts`, or `/usr/share/fonts`.
- If the task is mainly local finishing/captions/formatting/splitting/artifact extraction, check the `ffmpeg` skill before inventing commands.
- `wonda edit video` runs a **local ffmpeg** for every editor op: `trim`, `crop`, `volume`, `speed`, `reverseVideo`, `extractFrame`, `extractAudio`, `editAudio`, `imageCrop`, `imageToVideo`, `merge`, `overlay`, `splitScreen`, `splitScenes`, `skipSilence`. The render runs on your machine via ffmpeg: no server-side `editor_job` and no credit hold for the render itself (inputs are downloaded and the result uploaded around it). `textOverlay` and `animatedCaptions` also run locally, via the bundled hyperframes (Chromium) renderer. ffmpeg must be on PATH (`wonda doctor` verifies). The public API `/video/edit`, `/image/edit`, `/audio/edit` are no longer used for these and return 410 Gone.
- **Always merge clips locally.** Server-side merge can hang for 30+ minutes once any input exceeds ~7MB, and `wonda edit video --operation merge` now runs in local ffmpeg by default for the same reason.
- **Never mix per-clip audio then concat.** Concat the video tracks first, then layer the full voiceover or music track once over the joined timeline. Per-clip audio bakes create cut-line collisions and silent gaps.

Default local export target unless the user asked otherwise:

```bash
-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k
```

Always pass `-y` as the first flag so the command auto-overwrites the output. `ffmpeg` prompts interactively when the output path exists and agent shells hang on that prompt until timeout.

### Step 2.6: Pick the right local tool

Editing maps to one of four tools. Pick the first row that matches.

| Need                                                         | Tool                                                                   | Why                                                                                              |
| ------------------------------------------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Primitive transform (trim, crop, speed, merge, overlay, ...) | `wonda edit video --operation <op>`                                    | Wraps local ffmpeg. Free, deterministic, renders on your machine (no server render, no credits). |
| Motion graphics, animated text, lower thirds, intro/outro    | `wonda compose <kind>` (hyperframes HTML compositions, local render)   | One-shot, no Lambda, no Node bundled into wonda. Requires Node >= 22 + ffmpeg.                   |
| Kinetic captions, branded effects pipelines, scene FX        | `wonda transitions run --preset <name>` (miruna's transitions service) | Hosted; richer effect library (SAM3 masking, scene transitions, caption presets).                |
| One-off raw transform not covered by a primitive             | Raw `ffmpeg` via Bash (see the `ffmpeg` skill)                         | Faster than picking a wrong primitive; matches "deterministic transform on local files".         |
| Complex multi-step pipeline                                  | Chain the above (`wonda edit ...` → raw ffmpeg → `wonda compose ...`)  | Each step writes a local mp4; pass it as `--input` / `--media` to the next.                      |

Run `wonda doctor` once on a new machine to confirm ffmpeg, node, and hyperframes are all available. Pass `--warm-chrome` to pre-fetch hyperframes' bundled Chromium (~150 MB) so the first clipping render doesn't pause to download it.

**Examples:**

Primitive trim and merge (wonda edit, local ffmpeg):

```bash
wonda edit video --operation trim --media $VID \
  --params '{"trimStartMs":3000,"trimEndMs":10000}' \
  --wait -o ./trimmed.mp4

wonda edit video --operation merge --media $A,$B,$C \
  --wait -o ./merged.mp4
```

Motion graphics intro (wonda compose, hyperframes):

```bash
wonda compose motion --template fade-in \
  --text "Q4 Recap" --subtitle "Wondercat" \
  --duration 4 --resolution portrait -o intro.mp4

wonda compose text --input ./clip.mp4 --text "NEW DROP" \
  --position bottom-center -o overlay.mp4
```

Kinetic captions on a finished clip (transitions service):

```bash
wonda transitions run --media $VID --preset caption_word_pop --wait -o final.mp4
```

Raw ffmpeg for an op no primitive covers (e.g. concat with audio fade out):

```bash
ffmpeg -y -f concat -safe 0 -i list.txt \
  -af "afade=out:st=29:d=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k out.mp4
```

Multi-step pipeline (compose intro → wonda merge with main → transitions captions):

```bash
wonda compose motion --template scale-pop --text "Hello" --duration 3 -o intro.mp4
wonda edit video --operation merge --media $(wonda media upload intro.mp4 --quiet),$MAIN_VID \
  --wait -o merged.mp4
MERGED_ID=$(wonda media upload merged.mp4 --quiet)
wonda transitions run --media $MERGED_ID --preset caption_word_pop --wait -o final.mp4
```

### Step 3: Build from scratch (chain endpoints)

When no skill matches, chain individual CLI commands. Each step produces an output that feeds into the next.

**Single asset:**

```bash
wonda generate image --model gpt-image-2 --prompt "..." --aspect-ratio 9:16 --wait -o out.png
# --params '{"quality":"high"}' — auto/low/medium/high (default auto)
# --negative-prompt "..."       — override what to exclude (model-dependent)
# --seed <number>               — pin the seed for reproducible results (model-dependent)
wonda generate video --model seedance-2 --prompt "..." --duration 5 --params '{"quality":"high"}' --wait -o out.mp4
wonda generate text --model <model> --prompt "..." --wait
wonda generate music --model suno-music --prompt "upbeat lo-fi" --wait -o music.mp3
```

**Audio (speech, transcription, dialogue):**

```bash
# List available voices (TTS + dialogue use the same set)
wonda audio voices

# Text-to-speech
wonda audio speech --model elevenlabs-tts --prompt "Your script here" \
  --params '{"voiceId":"hpp4J3VqNfWAUOO0d1Us"}' --wait -o speech.mp3
# elevenlabs-tts always requires a voiceId — pick one from `wonda audio voices`

# Transcribe audio/video to text
wonda audio transcribe --model elevenlabs-stt --attach $MEDIA --wait

# Multi-speaker dialogue (each speaker needs a voiceId from `wonda audio voices`)
wonda audio dialogue --model elevenlabs-dialogue \
  --prompt 'ALICE: Hi! BOB: Hello!' \
  --params '{"speakers":[{"label":"ALICE","voiceId":"hpp4J3VqNfWAUOO0d1Us"},{"label":"BOB","voiceId":"IKne3meq5aSn9XLyUdCD"}]}' \
  --wait -o dialogue.mp3
```

**Audio AI operations (direct-inference, NOT editor ops):**

```bash
# Denoise / dereverberate speech
wonda audio enhance --model replicate-resemble-enhance --attach $MEDIA \
  --params '{"denoise":true,"chunkSeconds":10}' --wait -o enhanced.wav

# Split a track into voice and instrumental stems
wonda audio extract-voice --model replicate-demucs --attach $MEDIA \
  --wait -o vocals.wav
```

**Add animated captions to a video:**

The `animatedCaptions` operation handles everything in one step — it extracts audio, transcribes for word-level timing, and renders animated word-by-word captions onto the video.

```bash
# Generate a video with speech audio
VID_JOB=$(wonda generate video --model seedance-2 --prompt "..." --duration 5 --aspect-ratio 9:16 --params '{"quality":"high"}' --wait --quiet)
VID_MEDIA=$(wonda jobs get inference $VID_JOB --jq '.outputs[0].media.mediaId')

# Add animated captions (single step)
wonda edit video --operation animatedCaptions --media $VID_MEDIA \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"bottom-center","sizePercent":80,"strokeWidth":2.5,"fontSizeScale":0.8,"highlightColor":"rgb(252, 61, 61)"}' \
  --wait -o final.mp4
```

The video's original audio is preserved. Do NOT replace the audio with TTS — Sora already generated the speech.

**Transitions (effects pipelines on a single video):**

```bash
wonda transitions presets                            # List built-in presets (JSON)
wonda transitions operations                         # Grouped by category (analysis/effect/...)
wonda transitions operations --json                  # Full per-param metadata
wonda transitions llms                               # Full reference (presets + ops + dependencies)
wonda transitions run --media $VID --preset flash_glow --wait -o out.mp4
# Or send an agent-generated timeline of clips (inline JSON):
wonda transitions run --media $VID \
  --clips '[{"layer_type":"video","start_frame":0,"end_frame":60}]' --wait -o out.mp4
# Or from a file (handy for long agent timelines):
wonda transitions run --media $VID --clips ./timeline.json --wait -o out.mp4
# To attach scene_transitions: pass an envelope (clips + scene_transitions)
# instead of a bare clip array — same file, both fields forwarded.
wonda transitions run --media $VID --clips ./timeline_with_transitions.json --wait -o out.mp4
# where timeline_with_transitions.json is:
#   { "clips": [...],
#     "scene_transitions": [{"name":"crossfade","params":{"duration":8},"boundaries":[60]}] }
wonda transitions job <jobId>                        # Poll a transition job
```

Use exactly one of `--preset` or `--clips`. Requires a full (logged-in) account. **Always read `wonda transitions llms` first when composing a clips timeline.** It documents the detect/segment/effect dependencies, which ops need masks, and the full clip-spec shape (layer types, tracks, effects, transforms).

**Preset variables (`variables` block).** Each preset declares the template variables it accepts under `variables` in `wonda transitions presets`. Each entry has `name`, `description`, and `required`. Required variables MUST be supplied or the job is rejected with a 400 — no more silent skipping. Pass them with `--var name=value` (repeatable) or, for the common `prompt` case, the `--prompt` shortcut:

```bash
# flash_glow_prompted requires { prompt }
wonda transitions run --media $VID --preset flash_glow_prompted \
  --prompt "woman in white dress" --wait -o out.mp4

# text_behind_person requires { prompt, text }
wonda transitions run --media $VID --preset text_behind_person \
  --var prompt="the person" --var text="HELLO WORLD" --wait -o out.mp4

# Numeric-typed vars: bare digits are decoded as numbers, "true"/"false" as
# bools, everything else stays a string. Presets that compare frame indices
# numerically (border_frame, marquee_text, quick_motion_text, bg_remove_scale)
# need this — quoting an int turns it back into a string.
wonda transitions run --media $VID --preset border_frame \
  --var exit_start_frame=200 --var exit_end_frame=251 --wait -o out.mp4
```

The `prompt` variable is a **detection text query** describing which subject to mask, fed to SAM3 to produce per-frame segmentation masks. Not a content-generation prompt.

Building a custom `--clips` timeline that needs detection masks? Add a clip with `layer_type: "video"` and a `mask: {layer_type: "mask", analysis_steps: [{name: segment, params: {prompt: "..."}}]}`. SAM3 handles both detection and segmentation in one step from the prompt, so no separate `detect` step is needed.

### Pre-warming masks before render (recommended)

For presets with `mask:<label>` variables, run `wonda transitions ensure-masks` first so the render starts with masks already prepared. The first call for a (media, label) pair takes 1-3 minutes; subsequent calls are near-instant.

```bash
# 1. Ensure masks are prepared for the labels you'll use, blocking until ready.
wonda transitions ensure-masks --media $VID --labels person,phone --wait

# 2. Run the render. Masks are already prepared.
wonda transitions run --media $VID --preset slide_reflect_background \
  --var "masks=mask:person+phone" --wait -o out.mp4
```

`ensure-masks` flags:

- `--media MEDIA_ID` — required, the video the masks are for
- `--label NAME` — repeatable, one label per call (`--label person --label phone`)
- `--labels NAME,NAME` — comma-separated alternative (`--labels person,phone`)
- `--wait` — block until every label is prepared
- `--timeout DUR` — cap wait time when `--wait` is set (default 10m)

Multi-prompt syntax: `mask:woman+phone` in `--var` is split into separate masks (`woman`, `phone`) and unioned per-frame. Pass each sub-label separately to `ensure-masks` so all of them are pre-warmed.

When to skip `ensure-masks`:

- Non-mask presets (no `mask:<label>` variables) — nothing to prepare
- A previous render already used these (media, labels) — already prepared

When `ensure-masks` matters most:

- First render of a new media with mask-based presets
- Iterating params on a render — pre-warm once, then run as many times as you want without re-preparing

**Multi-scene presets (`requiresMultiScene: true`).** Some presets use scene-aware logic and expect a video with multiple cuts/scenes. Check `requiresMultiScene` in `wonda transitions presets`. If true, feeding a single continuous shot will produce only one scene and the effect may look underwhelming. Combine clips first or use a video with natural cuts.

**Tweaking preset params.** Every preset is clip-shape. Pull a single preset with `wonda transitions preset <name> --json`, read its `clips:` (single-track) or `tracks:` (multi-track) field, edit any clip param, and submit as `--clips`. For multi-track presets, flatten by giving each clip a `track` index drawn from the track it came from. If the preset declares `sceneTransitions:`, pass that array through unchanged on the request.

```bash
# Single-track preset (e.g. flash_glow_montage): copy clips: directly
wonda transitions preset flash_glow_montage --json | jq '.preset.clips' > clips.json
# edit clips.json
wonda transitions run --media $VID --clips "$(cat clips.json)" --wait -o out.mp4
```

**Auto-repair safety net (`--auto-repair`, `--face-bbox`).** For `--clips` renders the worker runs a deterministic repair pass on the submitted JSON before rendering, default on. Repairs: width-fit font clamp, descender clamp against canvas bottom, stack-spacing snap (`ROW1_py` from cap-height formula), keyframe-bound clamp to `[0, source_duration]`, same-y-row caption overlap trim, mask full-duration extension, stroke-width zeroing, letter-spacing target snap per font, mask-cutout duration extension, negative-start clamp, and (with `--face-bbox`) face-overlap caption shift. Pass `--auto-repair=false` for strict validation; out-of-spec values then surface as render errors.

```bash
# Push body captions off the speaker's face. bbox is x1,y1,x2,y2 in canvas pixels (top-left origin).
wonda transitions run --media $VID --clips ./timeline.json \
  --face-bbox 200,160,520,520 --wait -o out.mp4

# Strict mode — disable auto-repair to see exactly which clips fail validation.
wonda transitions run --media $VID --clips ./timeline.json \
  --auto-repair=false --wait -o out.mp4
```

`--face-bbox` only shifts body captions. Decorative text you want behind the speaker still routes through an explicit `mask_cutout {prompt: "person"}` clip.

**Output URL paths differ by job type:**

- Inference jobs (generate, audio): `.outputs[0].media.url` and `.outputs[0].media.mediaId`
- Editor jobs (edit): `.outputs[0].url` and `.outputs[0].mediaId`

## Model waterfall

### Image

Default: `gpt-image-2`. OpenAI's flagship — strongest prompt adherence, best text-in-image, high-fidelity edits via reference images. Handles 1-4 reference images. Quality tiers: `auto` (default), `low`, `medium`, `high` — pass via `--params '{"quality":"high"}'`. Caps at 1536px output.

For img2img editing specifically (change, add/remove, restyle, bg-remove, crop, text overlay, vectorize), use `wonda skill get image-edit` — it has the full edit-specific decision tree.

Pick something else only when one of these applies:

- User explicitly requests another model
- **More than 4 reference images** → `nano-banana-2` (gpt-image-2 caps at 4 refs; nano-banana-2 accepts up to 14). For 1-4 refs, stay on `gpt-image-2`.
- Need vector output → `runware-vectorize`
- Need background removal → `birefnet-bg-removal`
- Cheapest possible / fastest drafts → `z-image`
- Need >1536px / true 4K output → `nano-banana-pro` (1K/2K/4K) or `nano-banana-2` (1K/2K/4K). gpt-image-2 caps at 1536px.
- gpt-image-2 unavailable / OpenAI down → `nano-banana-2` or `seedream-4-5` or `grok-imagine-pro`

### Video

Default: `seedance-2` (duration 5/10/15s, default 5s, quality: high). Escalation:

- Quality complaint or different style → `sora2` or `sora2pro`
- Max single-clip duration is **15s** for Seedance 2, **20s** for Sora → for longer content, stitch multiple clips via merge
- Veo (`veo3_1`, `veo3_1-fast`) is available but NOT in the default waterfall. Only pick Veo when the user explicitly asks for Veo by name.
- Gemini Omni (`gemini-omni-video`) is available but NOT in the default waterfall. Only pick it when the user asks for Gemini by name, or specifically needs multi-image reference T2V/I2V (up to 7 reference images) or 4K output.

**Image-to-video routing (MANDATORY when attaching a reference image):**

- Person/face visible in the **reference image** → MUST use `kling_3_pro` (preserves identity better for faces)
- No person in reference image → use `seedance-2`
- **Text-to-video (no reference image):** Seedance 2 generates people fine. This rule ONLY applies when you `--attach` an image.

**Kling model family:**

- `kling_3_pro` — Text-to-video and image-to-video, supports start/end images, custom elements (@Element1, @Element2), 3-15s duration, 16:9/9:16/1:1
- `kling_2_6_pro` — General purpose, 5-10s, 16:9/9:16/1:1, text-to-video and image-to-video
- `kling_2_6_motion_control` — Motion transfer: requires both a reference image AND a reference video, recreates the video's motion with the image's appearance
- `kling2_5-pro` — Budget Kling option, 5-10s, supports first/last frame images

**Kling prompt rules (important):** Kling's prompt field caps at **2,500 characters** and Kling responds poorly to Sora-style structured briefs (`SCENE:` / `SUBJECT:` / `MOTION:` / `BANNED LOOK:` section headers). In that format Kling latches onto atmosphere nouns and silently drops the central subject (verified empirically: the same 2,842-char Sora-style prompt that rendered correctly on Sora 2 Pro and Seedance 2 produced no phone at all on Kling — even when trimmed to 2,250 chars). When escalating Seedance → Kling, or targeting Kling directly, **rewrite the prompt as short natural-language prose (~1,000–1,500 chars)** and **lead with the hero subject in the opening sentence** rather than burying it inside a `SUBJECT:` block. Do NOT pass a Sora-formatted prompt through to Kling unchanged.

**Other video models:**

- `grok-imagine-video` — xAI video generation, 5-15s, supports 7 aspect ratios including 4:3 and 3:2
- `gemini-omni-video`: Google Gemini Omni. Text-to-video and image-to-video with up to 7 reference images (slots `reference_image_1` through `reference_image_7`). Durations 4/6/8/10s, aspect ratios 9:16 and 16:9, resolutions 720p / 1080p / 4K. Pricing: $0.15 base + $0.075/s at 720p/1080p, $0.75 base + $0.075/s at 4K. No native audio (pair with a separate audio model if speech is needed).
- `topaz-video-upscale` — Upscale video resolution (1-4x factor, supports fps conversion)
- `sync-lipsync-v2-pro` — Legacy lipsync for user-supplied video + audio pairs. Inferior to native-audio generation and almost never the right choice for new content. See the "Lip sync" section for rules.

Seedance family (DEFAULT video model, watermarks automatically removed):

- `seedance-2` — Base Seedance 2.0 (T2V/I2V, 5-15s, high=standard/basic=fast)
- `seedance-2-omni` — Multi-reference generation (images, audio refs)
- `seedance-2-video-edit` — Edit existing video via text prompt

**Video durations:** Accepted `--duration` values vary by model. Check with `wonda capabilities` or `wonda models info <slug>`.

### Audio

- Music: `suno-music` (set `--params '{"instrumental":true}'` for no vocals)
- Text-to-speech: `elevenlabs-tts` — only for explicit narrator/voice-over asks over silent footage. Do NOT use to "make a UGC character talk" — Sora / Sora 2 Pro / Veo 3.1 / Kling 3 / Seedance 2 generate native synced speech in any language, which looks and sounds far better. Always set voiceId in params. Default female voice: `--params '{"voiceId":"21m00Tcm4TlvDq8ikWAM"}'` (Rachel).
- Transcription: `elevenlabs-stt`
- Multi-speaker dialogue: `elevenlabs-dialogue`
- Enhance audio (clean up noisy speech): `replicate-resemble-enhance` via `wonda audio enhance` — denoise + dereverberate. Use when a voice recording sounds muffled, echoey, or has background noise. NOT a general "sounds better" button; if the source is already clean this can soften it.
- Extract voice (isolate vocals / split stems): `replicate-demucs` via `wonda audio extract-voice` — splits into voice and instrumental tracks. Use to pull a speaker or singer off a track, or to isolate the music behind a vocal.

**Native synced speech (preferred over TTS + lipsync):** Sora, Sora 2 Pro, Veo 3.1, Kling 3, and Seedance 2 all generate dialogue in any language directly inside the video, with mouth movements baked in. Put the line (and language) in the video model's `--prompt`. Never chain `elevenlabs-tts` → `sync-lipsync-v2-pro` to fake speech over a silent generation.

## Characters

Characters are reusable saved combos (image + optional voice audio) you can mention in prompts with `@name`. The server auto-injects the image, optional face video, and audio into the right slots for the selected model. Works on Kling 3 Pro (`start_image` + `element_1` + `voice_audio`) and Seedance 2 Omni (`ref_image_1` + `ref_video_1` + `ref_audio_1`). Name rules: must start with a letter, 1–31 chars, alphanumeric + `_`/`-`.

**Provider gotchas (Seedance 2 Omni):** when a character is mentioned, the API routes Seedance to MuAPI automatically. Replicate enforces a 15s `ref_audio_1` cap and rejects famous-celebrity refs with `E005 — input flagged as sensitive`. MuAPI is the reliable path for character-driven jobs. Even on MuAPI, top-tier celebrity refs (think Sydney Sweeney, Leonardo DiCaprio) are blocked with `"Face detected in uploaded image. Please use an image without real people."` Non-celebrity faces and lesser-known public figures pass cleanly. If you see that error on a real-person ref, use Kling 3 Pro instead (its character pipeline runs voice cloning server-side, so the raw face audio never touches a moderation classifier).

**From a Kling clip** — extract a frame + voice from a generation you like:

```bash
VID=$(wonda generate video --model kling_3_pro --prompt "young man, grey tshirt, talking to camera" --wait --quiet)
VID_MEDIA=$(wonda jobs get inference $VID --jq '.outputs[0].media.mediaId')
wonda character from-media alex --source $VID_MEDIA --frame-ms 2500
wonda generate video --model kling_3_pro --prompt "@alex welcomes viewers to the channel" --wait -o alex-welcome.mp4
```

**From scratch** — generate a portrait and a TTS sample, then bind them:

```bash
IMG=$(wonda generate image --model nano-banana-2 --prompt "young woman, studio portrait" --wait --quiet)
IMG_MEDIA=$(wonda jobs get inference $IMG --jq '.outputs[0].media.mediaId')
AUD=$(wonda audio speech --model elevenlabs-tts --prompt "Hi, this is me" --params '{"voiceId":"21m00Tcm4TlvDq8ikWAM"}' --wait --quiet)
AUD_MEDIA=$(wonda jobs get inference $AUD --jq '.outputs[0].media.mediaId')
wonda character create maya --image $IMG_MEDIA --audio $AUD_MEDIA
```

List / inspect / update / delete: `wonda character list`, `wonda character get <name>`, `wonda character update <name> --audio $NEW`, `wonda character delete <name>`. Only one character with audio can be referenced per generation.

## Prompt writing rules

Follow this waterfall top-to-bottom. Use the FIRST matching rule and stop.

1. **PASSTHROUGH** — If the user says "use my exact prompt" / "verbatim" / "no enhancements" → copy their words exactly. Zero modifications.

2. **IMAGE-TO-VIDEO** — When a source image feeds into a video model, describe MOTION ONLY. The model can see the image. Do NOT describe the image content.
   - Good: `"gentle breathing motion, camera slowly pushes in, atmospheric lighting shifts"`
   - Bad: `"Two cats on a lavender background breathing softly"` (describes the image)

3. **EMPTY PROMPT (from scratch)** — Use the user's exact request as the prompt. Do NOT add style descriptors, lighting, composition, or mood.
   - User says "create an image of a cat with sunglasses" → prompt: `"create an image of a cat with sunglasses"`
   - Do NOT enhance to `"A playful orange tabby wearing oversized reflective sunglasses, studio lighting, shallow depth of field"`

4. **NON-EMPTY PROMPT (adapting a template)** — Keep the structure and style, only swap content to match the user's request. Keep prompts literal and constraint-heavy.

## Aspect ratio rules

Three cases, no exceptions:

1. User specifies a ratio → use it: `--aspect-ratio 16:9`
2. User doesn't mention ratio → explicitly set `--aspect-ratio 9:16` for social content (UGC, TikTok, Reels, Stories). Portrait is the default for any social/marketing video.
3. Editing existing media → use `--aspect-ratio auto` to preserve source dimensions

**UGC and social content is ALWAYS portrait (9:16).** If someone asks for a TikTok, Reel, Story, or UGC video, always use `--aspect-ratio 9:16`. Landscape is only for YouTube, presentations, or when explicitly requested.

**Square (1:1)** is supported by all Kling models and some image models — use for Instagram feed posts when requested.

## Common chaining patterns

These patterns show how to compose multi-step pipelines by chaining CLI commands. Each step's output feeds into the next.

> **No need to download and re-upload between steps.** Every generation and edit
> produces a media ID in its output. Pass that ID directly to the next command
> via `--media` or `--audio-media`. Use `--jq '.outputs[0].media.mediaId'`
> for inference jobs and `--jq '.outputs[0].mediaId'` for editor jobs.
> Only use `-o <file>` on the FINAL step to download the finished output.

### Animate an image to video

```bash
MEDIA=$(wonda media upload ./product.jpg --quiet)
# No person in image → Seedance 2
wonda generate video --model seedance-2 --prompt "camera slowly pushes in, product rotates" \
  --attach $MEDIA --duration 5 --params '{"quality":"high"}' --wait -o animated.mp4
# Person in image → Kling (ONLY when attaching a reference image with a person)
wonda generate video --model kling_3_pro --prompt "the person turns and smiles" \
  --attach $MEDIA --duration 5 --wait -o person.mp4
```

### Replace audio on a video (TTS voiceover or music)

```bash
# Generate TTS
TTS_JOB=$(wonda audio speech --model elevenlabs-tts --prompt "The script" \
  --params '{"voiceId":"21m00Tcm4TlvDq8ikWAM"}' --wait --quiet)
TTS_MEDIA=$(wonda jobs get inference $TTS_JOB --jq '.outputs[0].media.mediaId')
# Mix onto video (mute original, full voiceover)
wonda edit video --operation editAudio --media $VID_MEDIA --audio-media $TTS_MEDIA \
  --params '{"videoVolume":0,"audioVolume":100}' --wait -o with-voice.mp4
```

Only use this when you need to REPLACE the video's audio. Sora, Sora 2 Pro, Veo 3.1, Kling 3, and Seedance 2 all generate native synced speech in any language — don't replace it with TTS unless the user explicitly asks for a different voiceover. Never reach for this step to "add speech" to a UGC/talking-head clip; put the dialogue in the video model's prompt instead.

### Add static text overlay

Static overlays (meme text, "chat did i cook", etc.) use smaller font sizes than captions. They're ambient, not meant to dominate the frame.

```bash
wonda edit video --operation textOverlay --media $VID_MEDIA \
  --prompt-text "chat, did i cook" \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"top-center","sizePercent":66,"fontSizeScale":0.5,"strokeWidth":4.5,"paddingTop":10}' \
  --wait -o with-text.mp4
```

**Featured textOverlay + animatedCaptions presets.** `wonda edit {video,image,audio}` accepts `--preset <name>` (scoped to `--operation`). `--params` fields override preset values on key collisions.

`textOverlay` (static, top-centered):

- `TikTok White Highlight` — black text on a slightly rounded white box.
- `TikTok Black Highlight` — white text on a slightly rounded black box.
- `TikTok Red Highlight` — white text on a slightly rounded red (`#E14135`) box.

`animatedCaptions` (STT-driven, bottom-centered):

- `TikTok White Captions` — black text, white highlight on the active word.
- `TikTok Black Captions` — white text, black highlight on the active word.
- `TikTok Red Captions` — white text, red (`#E14135`) highlight on the active word.

```bash
wonda edit video --operation textOverlay \
  --preset "TikTok Red Highlight" --media <id> \
  --params '{"text":"YOUR HEADLINE"}' --wait -o ./out.mp4
```

`textOverlay` renders locally via the bundled hyperframes (Chromium) renderer. There is no server-side image `textOverlay` anymore.

**Font sizing guide:**

- Static overlays: `sizePercent: 66`, `fontSizeScale: 0.5`, `strokeWidth: 4.5`
- Animated captions: `sizePercent: 80`, `fontSizeScale: 0.8`, `strokeWidth: 2.5`, `highlightColor: rgb(252, 61, 61)`
- Font: `TikTok Sans SemiCondensed` for both

### Add animated captions (word-by-word with timing)

The `animatedCaptions` operation extracts audio, transcribes, and renders animated word-by-word captions — all in one step.

```bash
wonda edit video --operation animatedCaptions --media $VIDEO_MEDIA \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"bottom-center","sizePercent":80,"strokeWidth":2.5,"fontSizeScale":0.8,"highlightColor":"rgb(252, 61, 61)"}' \
  --wait -o with-captions.mp4
```

For quick static captions (no timing, just text on screen), use `textOverlay` with `--prompt-text`:

```bash
wonda edit video --operation textOverlay --media $VIDEO_MEDIA \
  --prompt-text "Summer Sale - 50% Off" \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"bottom-center","sizePercent":80}' \
  --wait -o captioned.mp4
```

### Add background music

```bash
MUSIC_JOB=$(wonda generate music --model suno-music \
  --prompt "upbeat lo-fi hip hop, warm vinyl crackle" --wait --quiet)
MUSIC_MEDIA=$(wonda jobs get inference $MUSIC_JOB --jq '.outputs[0].media.mediaId')
wonda edit video --operation editAudio --media $VID_MEDIA --audio-media $MUSIC_MEDIA \
  --params '{"videoVolume":100,"audioVolume":30}' --wait -o with-music.mp4
```

### Editor output chaining

When chaining multiple editor operations (e.g., editAudio → animatedCaptions → textOverlay), extract the media ID from each editor job output and pass it to the next step. Note the jq path differs from inference jobs:

```bash
# Inference jobs: .outputs[0].media.mediaId
# Editor jobs:    .outputs[0].mediaId

EDIT_JOB=$(wonda edit video --operation editAudio --media $VID --audio-media $AUDIO \
  --params '{"videoVolume":0,"audioVolume":100}' --wait --quiet)
STEP1_MEDIA=$(wonda jobs get editor $EDIT_JOB --jq '.outputs[0].mediaId')

CAP_JOB=$(wonda edit video --operation animatedCaptions --media $STEP1_MEDIA \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"bottom-center","sizePercent":80,"strokeWidth":2.5,"fontSizeScale":0.8,"highlightColor":"rgb(252, 61, 61)"}' --wait --quiet)
STEP2_MEDIA=$(wonda jobs get editor $CAP_JOB --jq '.outputs[0].mediaId')

wonda edit video --operation textOverlay --media $STEP2_MEDIA \
  --prompt-text "Hook text" --params '{"position":"top-center","fontFamily":"TikTok Sans SemiCondensed","sizePercent":66,"fontSizeScale":0.5,"strokeWidth":4.5}' --wait -o final.mp4
```

### Merge multiple clips

**Always merge locally with ffmpeg.** Server-side merge (`wonda edit video --operation merge`) can hang for 30+ minutes once any input exceeds ~7MB.

Download every Wonda media ID, then concat. Stream-copy is fast but requires matching codec/profile/resolution; fall back to re-encode if it errors:

```bash
wonda media download $CLIP1 -o /tmp/clip-1.mp4
wonda media download $CLIP2 -o /tmp/clip-2.mp4
wonda media download $CLIP3 -o /tmp/clip-3.mp4
cat > /tmp/concat.txt <<EOF
file '/tmp/clip-1.mp4'
file '/tmp/clip-2.mp4'
file '/tmp/clip-3.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt -c copy /tmp/merged.mp4
# If stream-copy fails, re-encode:
# ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt \
#   -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart \
#   -c:a aac -b:a 192k /tmp/merged.mp4

# Re-upload only if a downstream wonda step needs the mediaId.
MERGED_MEDIA=$(wonda media upload /tmp/merged.mp4 --quiet)
```

File order in `concat.txt` = playback order. See the `ffmpeg` skill for the full concat reference.

### Split scenes / keep a specific scene

Two modes, pick by intent:

```bash
# Split mode (default) — returns EVERY detected scene as its own media.
# JSON output lists each scene under scenes[] ({mediaId,index,startS,endS}).
wonda edit video --operation splitScenes --media $VID_MEDIA \
  --params '{"mode":"split","threshold":0.5,"minClipDuration":2}' --json
# With -o, each scene downloads to a numbered file (out-1.mp4, out-2.mp4, ...);
# a single detected scene writes the path verbatim.
wonda edit video --operation splitScenes --media $VID_MEDIA \
  --params '{"mode":"split","threshold":0.5,"minClipDuration":2}' -o scenes.mp4

# Remove a scene (omit mode) — removes one scene, merges the rest into one file.
wonda edit video --operation splitScenes --media $VID_MEDIA \
  --params '{"mode":"omit","threshold":0.5,"minClipDuration":2,"outputSelection":"first"}' \
  --wait -o without-first.mp4
# outputSelection (omit mode only): "first", "last", or a 1-indexed number = which scene to REMOVE
```

Use omit mode for "remove frozen first frame" (common with Sora videos). Use split mode to get all scenes as separate clips.

### Image editing

Any image edit — img2img, background removal, crop, text overlay, vectorize — has its own skill with the full decision tree, aspect-ratio rules, and model waterfall for edits:

```bash
wonda skill get image-edit
```

One gotcha worth keeping here: image and video background removal use **different** models (`birefnet-bg-removal` vs `bria-video-background-removal`). Never swap them.

### Lip sync (last-resort fallback — prefer native-audio video models)

Sora, Sora 2 Pro, Veo 3.1, Kling 3, and Seedance 2 all generate speech in any language with correctly synced mouth movements as part of the video itself. That path produces dramatically better results than `sync-lipsync-v2-pro`: better lip physics, better lighting, better costs, and no second inference round-trip. For any talking UGC, ad, or spokesperson video, put the dialogue directly in the video model's prompt — do not chain TTS + lipsync.

Only reach for `sync-lipsync-v2-pro` when the user EXPLICITLY supplies both a pre-existing video and a pre-existing audio clip and asks you to align the mouth to that audio. If a user asks for lipsync as the default method of making a character speak, push back: the native-audio video models are the better tool and work in any language.

```bash
wonda generate video --model sync-lipsync-v2-pro --attach $VIDEO_MEDIA,$AUDIO_MEDIA --wait -o synced.mp4
```

### Video upscale

```bash
wonda generate video --model topaz-video-upscale --attach $VIDEO_MEDIA \
  --params '{"upscaleFactor":2}' --wait -o upscaled.mp4
```

### Clipping (longform → vertical shorts)

`wonda clipping` takes a long video (podcast, interview, talking-head)
and produces short vertical clips. Selection is LLM-driven and supports
a natural-language `--brief` so you can ask for specific moments instead
of generic virality.

V1 renders 9:16 with **face-tracked reframe** (LR-ASD active-speaker
detection + One-Euro stabilizer, default) and the existing
`animatedCaptions` op + a top-third hook overlay per clip. Pass
`--reframe blur-fill` to keep the full landscape source inside a
vertical canvas with a blurred background instead.

**Translated captions:** pass `--caption-language <code>` (ISO-639-1,
e.g. `en`) to render captions in another language while keeping the
original audio. Each clip's transcript is translated per sentence and the
spoken timing is preserved, so captions stay in sync. Omit the flag to
caption in the spoken language. On `--restyle`, the language is inherited
from the parent job unless overridden, so you can cheaply spin out an
English-captioned version of an already-clipped job (reuses the
transcript, no re-transcription).

Async: `POST /api/v1/clipping` returns a `clippingJobId`; the CLI polls
`GET /api/v1/clipping/jobs/{id}` under `--wait`. Pass `--output <dir>`
and the CLI downloads each rendered clip + a `plan.json`.

Auth: included in the paid plan.

**Source: `--url` accepts YouTube and direct mp4 URLs.**

```bash
wonda clipping --url "<youtube-url>" --brief "the most controversial moments" --wait
```

YouTube links work; a long video can take several minutes to ingest before
transcription starts. If a YouTube ingest fails, download the file locally
and upload it first, then clip with `--media`:

```bash
yt-dlp -o /tmp/source.mp4 \
  -f "bv*[ext=mp4][height<=720]+ba[ext=m4a]/b[ext=mp4][height<=720]" \
  --merge-output-format mp4 "<youtube-url>"
MEDIA=$(wonda media upload /tmp/source.mp4 --no-transcode --quiet)
```

`--no-transcode` skips the server-side normalize so longform sources are
usable in seconds instead of minutes (a 1 h upload otherwise transcodes for
~19 min before clipping can start). Clipping handles incompatible formats
(AV1, rotated phone video) per selected clip automatically. Omit the flag
for uploads you plan to publish or edit directly without clipping.

```bash
# Plan only — fast, no render
wonda clipping --media $MEDIA --brief "the most controversial moments" --dry-run --wait

# Full pipeline: select + render + download
wonda clipping --media $MEDIA \
  --brief "the most controversial moments" \
  --caption-preset "TikTok Red Captions" \
  --hook auto \
  --wait --output ./clips/

# Translate captions to English (original audio kept)
wonda clipping --media $MEDIA --caption-language en --wait --output ./clips/

# Re-caption an existing job into English (reuses STT + clip picks, ~$0)
wonda clipping --restyle <jobId> --caption-language en --wait --output ./clips/

# Filter by speaker (uses ElevenLabs diarization labels)
wonda clipping --media $MEDIA --speaker SPEAKER_00 --wait --output ./clips/

# Speaker rename for readable rationales
wonda clipping --media $MEDIA --speaker Joe \
  --speaker-map '{"SPEAKER_00":"Joe","SPEAKER_01":"Guest"}' --wait --output ./clips/

# Tune count and durations — pick a target length with a tolerance
wonda clipping --media $MEDIA --brief "punchy one-liners" \
  --count 5 --duration 20 --tolerance 5 --wait --output ./clips/

# Or specify an explicit min/max range instead (mutually exclusive
# with --duration/--tolerance)
wonda clipping --media $MEDIA --brief "punchy one-liners" \
  --count 5 --min-duration 8 --max-duration 30 --wait --output ./clips/

# Auto-pick FX preset per clip from a catalog
wonda clipping --media $MEDIA --auto-preset \
  --preset-catalog '[{"slug":"flash_glow","description":"glow + scene flash"},{"slug":"text_glow","description":"per-word text glow"}]' \
  --wait --output ./clips/
```

Job-status shape (returned by GET `/api/v1/clipping/jobs/{id}`):

```json
{
  "clippingJobId": "...",
  "status": "succeeded",
  "stage": "succeeded",
  "progress": 1,
  "plan": {
    "sourceDurationSec": 1800.5,
    "speakers": ["SPEAKER_00", "SPEAKER_01"],
    "clips": [
      {
        "start": 12.4,
        "end": 38.7,
        "title": "Why he quit the agency",
        "hookText": "He admits…",
        "rationale": "Concedes \"the agency model is dead\" then explains why...",
        "score": 87,
        "dominantSpeaker": "SPEAKER_00",
        "reframeMode": "blur-fill",
        "preset": null,
        "mediaId": "uuid-of-rendered-clip",
        "url": "https://storage.googleapis.com/.../clip.mp4"
      }
    ]
  },
  "error": null
}
```

## Editor operations reference

| Operation          | Inputs                      | Key Params                                                                                                 |
| ------------------ | --------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `animatedCaptions` | video_0                     | fontFamily, position, sizePercent, fontSizeScale, strokeWidth, highlightColor                              |
| `textOverlay`      | video_0 + prompt            | fontFamily, position, sizePercent, fontSizeScale, strokeWidth                                              |
| `editAudio`        | video_0 + audio_0           | videoVolume (0-100), audioVolume (0-100)                                                                   |
| `merge`            | video_0..video_4            | Handle order = playback order                                                                              |
| `overlay`          | video_0 (bg) + video_1 (fg) | position, resizePercent                                                                                    |
| `splitScreen`      | video_0 + video_1           | targetAspectRatio (16:9 or 9:16)                                                                           |
| `trim`             | video_0                     | trimStartMs, trimEndMs (milliseconds)                                                                      |
| `crop`             | video_0                     | aspectRatio (16:9/9:16/1:1/4:5/21:9/custom) OR cropPercent+cropAxis. Ratio/percent based, NOT pixel coords |
| `volume`           | video_0                     | volume (0-100) or muted                                                                                    |
| `speed`            | video_0                     | speed (multiplier: 2 = 2x faster)                                                                          |
| `extractFrame`     | video_0                     | timestampMs or timestampPercent (outputs an image)                                                         |
| `extractAudio`     | video_0                     | Extracts audio track (outputs mp3)                                                                         |
| `reverseVideo`     | video_0                     | Plays backwards                                                                                            |
| `splitScenes`      | video_0                     | mode (split returns all scenes / omit returns one merged file), threshold, outputSelection (omit only)     |
| `skipSilence`      | video_0                     | maxSilenceDuration (default 0.03)                                                                          |
| `audioTrim`        | audio_0                     | trimStartMs, trimEndMs (milliseconds)                                                                      |
| `imageCrop`        | image_0                     | cropPixelX, cropPixelY, cropPixelWidth, cropPixelHeight (exact pixel rectangle)                            |
| `textOverlay`      | video_0 (image)             | Same as video textOverlay — works on images, outputs image (png/jpg)                                       |

> **`crop` vs `imageCrop`:** video `crop` is **ratio/percent** based (`aspectRatio` or `cropPercent`+`cropAxis`); it does NOT take pixel coordinates and rejects `cropPixelX/Y/Width/Height` with an error. For an **exact pixel rectangle**, use `imageCrop`. Run `wonda operations info <operation>` for the full param list, defaults, and ranges of any op.

Valid textOverlay fonts: Inter, Montserrat, Bebas Neue, Oswald, TikTok Sans, TikTok Sans Condensed, TikTok Sans SemiCondensed, TikTok Sans SemiExpanded, TikTok Sans Expanded, TikTok Sans ExtraExpanded, Nohemi, Poppins, Raleway, Anton, Comic Cat, Gavency
Valid positions: top-left, top-center, top-right, center-left, center, center-right, bottom-left, bottom-center, bottom-right

## Marketing & distribution

```bash
# Connected social accounts
wonda accounts instagram
wonda accounts tiktok

# Analytics
wonda analytics instagram
wonda analytics tiktok
wonda analytics meta-ads

# Organic owned-post analytics use platform-specific read commands:
# wonda x analytics, wonda linkedin analytics, wonda reddit analytics.
# The global analytics group above is for connected marketing APIs.

# Scrape competitors
wonda scrape social --handle @nike --platform instagram --wait
wonda scrape social-status <taskId>                   # Get results of a social scrape
wonda scrape cancel <taskId>                          # Cancel any public scrape task
wonda scrape ads --query "sneakers" --country US --wait
wonda scrape ads --query "sneakers" --country US --search-type keyword \
  --active-status active --sort-by impressions_desc --period last30d \
  --media-type video --max-results 50 --wait
wonda scrape ads-status <taskId>                      # Get results of an ads search

# Download a single reel or TikTok video
SCRAPE=$(wonda scrape video --url "https://www.instagram.com/reel/ABC123/" --wait --quiet)
# → returns scrape result with mediaId in the media array

# Publish
wonda publish instagram --media <id> --account <accountId> --caption "New drop"
wonda publish instagram --media <id> --account <accountId> --caption "..." --alt-text "..." --product IMAGE --share-to-feed
wonda publish instagram-carousel --media <id1>,<id2>,<id3> --account <accountId> --caption "..."
wonda tiktok creator-info --account <accountId>      # Live privacy options + comment/duet/stitch defaults
wonda publish tiktok --media <id> --account <accountId> --caption "New drop" --privacy PUBLIC_TO_EVERYONE
wonda publish tiktok --media <id> --account <accountId> --caption "..." --privacy PUBLIC_TO_EVERYONE \
  --disable-comment --commercial-disclose --brand-organic
wonda publish tiktok-carousel --media <id1>,<id2> --account <accountId> --caption "..." \
  --privacy PUBLIC_TO_EVERYONE --cover-index 0

# History
wonda publish history instagram --limit 10
wonda publish history tiktok --limit 10

# Browse media library
wonda media list --kind image --limit 20
wonda media info <mediaId>
```

### X/Twitter

Supports reads, writes, and social graph.

> ⚠️ **Anti-fraud caution: don't probe freshly-pasted cookies.** When you've just received cookies (yours or a user's), the FIRST request on them should be the operation the user actually wants, not `wonda x auth check`, not `wonda x home`, not anything that fires a probe. Burst activity on a new IP / device / process is the textbook signal X (and Reddit / LinkedIn / IG) flag as credential theft, and the cookies get shadow-banned or hard-killed. If you must verify, use `wonda x auth check --account <name> --via wab` (that routes through the account's existing logged-in browser session: same IP, same fingerprint, same browsing history) instead of firing a raw API request from a fresh process.

```bash
# Auth setup (run `wonda x auth --help` for details)
wonda x auth set --auth-token <token> --ct0 <ct0>
wonda x auth set --account <name> --auth-token <...> --ct0 <...>  # multi-account
wonda x auth check                                              # raw probe, see warning above
wonda x auth check --account <name> --via wab               # safe: routes via account's WAB session

# Read
wonda x search "sneakers" -n 20                     # Search tweets (sort: latest, current, top; time: day, week, month, year, all)
wonda x search "sneakers" --sort top --time week -n 20  # Top tweets from the last week
wonda x user @nike                                   # User profile
wonda x user-tweets @nike -n 20                      # User's recent tweets
wonda x read <tweet-id-or-url>                       # Single tweet
wonda x analytics <tweet-id-or-url>                  # Tweet metrics: viewCount, likeCount, retweetCount, replyCount
wonda x insights <tweet-id-or-url>                   # Alias for x analytics
wonda x replies <tweet-id-or-url>                    # Replies to a tweet
wonda x thread <tweet-id-or-url>                     # Full thread (author's self-replies)
wonda x home                                         # Home timeline (--following for Following tab)
wonda x bookmarks                                    # Your bookmarks
wonda x likes                                        # Your liked tweets
wonda x following @handle                            # Who a user follows
wonda x followers @handle                            # A user's followers
wonda x lists @handle                                # User's lists (--member-of for memberships)
wonda x list-timeline <list-id-or-url>               # Tweets from a list
wonda x news --tab trending                          # Trending topics (tabs: for_you, trending, news, sports, entertainment)
wonda x mentions -n 20                               # Recent replies and @mentions directed at your account
wonda x dm inbox -n 20                               # X DM conversations, default cookie path
wonda x dm requests -n 20                            # X DM message requests, default cookie path
wonda x dm read <conversation-id> -n 50              # Messages in one conversation
wonda x dm read <conversation-id> --via wab          # Same read routed through the WAB browser session

# Write (tweet/reply/engagement defaults to --via wab; X DM sends are wab-only)
wonda x tweet "Hello world"                          # Post a tweet
wonda x tweet "Hello world" --account <name> --via wab  # Full stealth via real browser
wonda x tweet "Hello world" --attach ~/clip.mp4      # Attach image/gif/video (up to 4)
wonda x reply <tweet-id-or-url> "Great point"        # Reply
wonda x like <tweet-id-or-url>                       # Like
wonda x unlike <tweet-id-or-url>                     # Unlike
wonda x retweet <tweet-id-or-url>                    # Retweet
wonda x unretweet <tweet-id-or-url>                  # Unretweet
wonda x follow @handle                               # Follow
wonda x unfollow @handle                             # Unfollow
wonda x feed-engage --authors "a,b" --duration 5m    # Scroll the feed and like posts from these authors (wab-only)
wonda x feed-engage --keywords "wonda alternative" --reply --max-reply 3  # Monitor search results, gate relevance, reply via WAB
wonda x dm send <conversation-id> "Hey, quick note"  # Send in an existing DM thread, wab-only
wonda x dm send <conversation-id> "Hey" --dry-run    # Type only, do not click Send
wonda x dm accept <conversation-id> --dry-run        # Open a message request without accepting it
wonda x dm accept <conversation-id>                  # Accept an incoming DM request, wab-only
wonda x dm start @handle --text "Hey, quick note"    # Start or reuse a DM by handle, wab-only
wonda x dm passcode set --account <name>             # Save encrypted XChat passcode for that account
wonda x dm passcode status --account <name>          # Show whether a passcode is configured

# Maintenance
wonda x refresh-ids                                  # Refresh cached GraphQL query IDs from X's JS bundles
```

All paginated commands support: `-n <count>`, `--cursor`, `--all`, `--max-pages`, `--delay <ms>`.

`wonda x user` includes additive `emails` and `links` fields when the member has published explicit contact details in their public bio or X exposes expanded URL entities for that profile. These fields are read-only and equivalent to manually reading the profile. No inferred emails, enrichment data, storage, or DOM scraping is involved.

**Tweet modes:** The `tweet` command has two transports:

- **`--via cookies` (internal API):** X's internal GraphQL (`CreateTweet` for ≤280 chars, `CreateNoteTweet` for long-form Premium). Fast (<1s), supports `--attach` for media. Occasionally fails with error 226 when X rotates query IDs or feature flags. When that happens, recapture via `twitter-tone-research/_artifacts/scripts/capture-ct-bw.mjs` and bump the three knobs in `xclient/`.
- **`--via wab` (default for writes):** Routes through the account's WAB Chromium (auto-spawned on first `--via wab` use), opens x.com compose, types with human-style jitter, clicks Post. Supports `--attach` (image/gif/video, up to 4); files are driven through the hidden compose input via Playwright's `setInputFiles`, no native picker dialog opens; the script waits for X's upload pipeline to finalize (up to 5 min for video) before submitting. Zero fingerprinting risk. Slower (~10s text, ~30-90s with video) but fully drift-proof: no queryIds, feature flags, or request shape to maintain. The stealth browser + Chromium install once via `wonda wab install` (~315 MB, one-time, idempotent). Cookies live in `~/.wonda/x-cookies/<account>.json`, bound to the account's persona via `account-bindings.json`. `wonda x reply --attach` is wab-only (no cookie path).

### Inbound engagement

Received engagement means inbound activity on the twin's own content: replies, mentions, comments, and DMs. This is the reverse direction of outbound posting, liking, and following.

It is not keyword monitor, not sent-invite/outreach acceptance tracking, and not the outbound action ledger. Use platform search commands for keyword monitoring. Use `wonda actions` for outbound action accounting.

```bash
wonda inbound                                      # New inbound items for every local persona
wonda inbound --persona brubakerwise              # One persona
wonda inbound --platform x -n 20                  # Only X mentions/replies
wonda inbound --platform linkedin                 # LinkedIn notifications
wonda inbound --platform reddit                   # Reddit classic inbox
wonda inbound --all                               # Dump fetched items without high-water diff or state write
```

`wonda inbound` fans out direct read clients only: X mentions/replies, LinkedIn notifications, and Reddit classic inbox. Output is always normalized JSON:

```json
{
  "new_count": 1,
  "items": [
    {
      "persona": "brubakerwise",
      "platform": "x",
      "account": "brubakerwise",
      "kind": "reply",
      "author": "someone",
      "text": "Useful point",
      "target_id": "2069000000000000000",
      "item_id": "2069000000000000001",
      "timestamp": "2026-06-22T12:00:00Z",
      "url": "https://x.com/someone/status/2069000000000000001"
    }
  ]
}
```

By default it persists a high-water mark per persona/platform/account at `~/.wonda/wab/personas/<persona>/inbound-state.json` and only emits items newer than the last run. Corrupt or missing state is treated as a first run. `--all` bypasses state reads and writes and returns the full fetched set.

**X DMs:** `wonda x dm inbox`, `wonda x dm requests`, and `wonda x dm read` read through the cookie-backed `xclient` path by default and can use `--via wab` for browser-session transport parity. `requests` returns the untrusted/message-request inbox so recipient-side acceptance can be handled explicitly. `wonda x dm send`, `wonda x dm start`, and `wonda x dm accept` are WAB-only DOM writes: sends open the real X messages UI, type into `[data-testid="dmComposerTextInput"]`, and click the composer send button; accept opens the request thread through Chat and clicks the visible Accept/Allow control. `start` verifies that the selected suggestion's screen name equals the requested handle before sending, and WAB DM writes verify the active X browser account when `--account` or persona bindings provide one. If `x dm send` or `x dm start` fails with `recipient_cannot_receive_dm`, X refused the DM before send. Check that the recipient can receive DMs from the sender: mutual follow/connect may be required, and the recipient may need to accept any pending message request before retrying. If X shows an encrypted XChat passcode gate, store the passcode with `wonda x dm passcode set --account <name>`; it is encrypted locally using the same local-secret pattern as cookie-adjacent storage and is never printed or included in failure bundles. Deeper XChat/Juicebox message decrypt/encrypt support remains unsupported until X exposes a thread that needs it.

### LinkedIn

Supports search, profiles, companies, messaging, and engagement.

> ⚠️ **Same anti-fraud caution as X: don't probe freshly-pasted cookies.** First request on new cookies = the actual operation, never a check. LinkedIn's anti-fraud is the most aggressive of all the platforms (force-logout, password reset, account flag). If you must verify, use `wonda linkedin auth check --account <name> --via wab` to route through the account's existing WAB session.

```bash
# Auth setup (run `wonda linkedin auth --help` for details)
wonda linkedin auth set --li-at-value <v> --jsessionid-value <v>
wonda linkedin auth set --account brand-A --li-at-value <...> --jsessionid-value <...>  # multi-account
wonda linkedin auth check                                              # raw probe, see warning above
wonda linkedin auth check --account <name> --via wab               # safe: routes via account's WAB session
wonda linkedin auth status --account <name>                        # local-only: cookie provenance (login vs paste) + 429-risk, never probes

# Read
wonda linkedin me                                    # Your identity
wonda linkedin search "data engineer" --type PEOPLE  # Search (types: PEOPLE, COMPANIES, ALL)
wonda linkedin profile johndoe                       # View profile (vanity name or URL)
wonda linkedin profile johndoe --via public          # View public profile data through the paid scrape API
wonda linkedin profile johndoe --via public --force-refresh --idempotency-key run-123
wonda linkedin enrich johndoe janedoe                # Batch profile enrichment through cookies, max 25 inputs
wonda linkedin enrich johndoe janedoe --via public   # Paid public enrichment task, default waits for completion
wonda linkedin enrich johndoe --via public --no-wait # Create task only, then poll GET /scrape/linkedin-profiles/{taskId}
wonda linkedin company google                        # View company page
wonda linkedin conversations                         # List message threads
wonda linkedin messages <conversation-urn>           # Read messages in a thread
wonda linkedin notifications -n 20                   # Recent notifications
wonda linkedin connections                           # Your own connections (recently-added order, each with connectedAt)
wonda linkedin connections johndoe                   # A member's connections visible to you (connectionOf search; relevance order, no dates; --degree 1|2|3 filters by your distance; --all enumerates)
wonda linkedin sent-invitations                      # Pending sent invites + audit reconciliation; cookies default, --via wab supported
wonda linkedin invitations                           # Incoming connection requests with notes and sharedSecret (cookie-only read)
wonda linkedin connection-status johndoe janedoe     # Per-member: connected / pending (in|out) / not_connected (cookie-only)
wonda linkedin saves                                 # Your saved posts (My Items → Saved posts; --all, --enrich for likes/comments)
wonda linkedin analytics <activity-id>               # Owned post analytics: impressions, uniqueViewers, engagements, profileViews when exposed
wonda linkedin analytics --profile                   # Profile-view analytics when LinkedIn exposes it for the account
wonda linkedin reactions <activity-id>               # Reactions with reactor profiles + type
wonda linkedin comment-reactors <comment-url-or-activityId:commentId> # Reactions on a specific comment with reactor profiles + type
wonda linkedin browser-bootstrap                     # Inject stored cookies into the WAB profile (one-time + on rotation)
wonda linkedin comments <activity-id> --account <name> --via wab  # Commenters with profile + vanity (auto-spawns WAB)
wonda linkedin activity johndoe                      # A member's recent-activity feed. --type all (their posts + reshares, default) | comments (posts they commented on, with their own comment text) | reactions (posts they reacted to, with reaction type). Each item carries the referenced post's author (name + profile URL), text, and URL; --count N (default 20)
wonda linkedin search-posts "<keyword>" --date-range past-week --account <name>  # Keyword to recent posts + author profile (Voyager content API over cookies by default, returns the activity id + exact post time; --via wab for the DOM-scrape fallback; for social listening run `wonda skill get linkedin-social-listening`)

# Sales Navigator (seat-gated: the LinkedIn account needs an SN seat; cookie reads, each verb also runs as a cloud twin action)
wonda linkedin salesnav search "VP marketing" --seniority 210 --region 100506914  # Faceted lead search; also --industry/--company/--function/--connection-of; '~' prefix excludes a value; --csv exports
wonda linkedin salesnav search --school 235785 --past-company 1009 --past-title 3 --years-of-experience 4  # Background facets: school/university, past employer, past job title, years-of-experience buckets (1 <1y, 2 1-2y, 3 3-5y, 4 6-10y, 5 10+y); --title filters current job title
wonda linkedin salesnav facets SCHOOL "HEC Paris"    # Resolve a facet value name to the id the search flags take (no args lists the filter types; YEARS_OF_EXPERIENCE has no typeahead, pass the bucket ids directly)
wonda linkedin salesnav --help                       # More seat-gated reads: saved-searches, lists, profile, typeahead, recommended leads|companies, alerts, recent, personas, notifications, warm-intro, insights
wonda linkedin salesnav profile "urn:li:fs_salesProfile:(ACwAA...,NAME_SEARCH,eQ3R)"  # Resolve one or more SN leads by fs_salesProfile urn (name + picture); add --enrich for each lead's education (school/degree/field/years), full experience history, and years-of-experience (opt-in; ~2 extra Voyager reads per lead, capped at 25)

# WAB lifecycle (see `wonda wab --help` for the full surface: start/stop/status/install/bind/sync-cookies/logs)
wonda linkedin enrich-engagers --activity-id <id>    # Scrape engagers + enrich each with profile + current employer (joined JSON; --company-detail=false skips company page lookups)
wonda linkedin enrich-engagers --activity-id <id> --profile-source public  # Keep engager collection logged-in, use paid public profile detail

# Write
wonda linkedin visit <vanity-name> --account <name>  # Visit a real profile page in the WAB, dwell, and optionally notify the target
wonda linkedin connect <vanity-name> --message "Hey!" # Send connection request with note
wonda linkedin connect <vanity-name> -m "Hey!" --account <name> --via wab  # Full stealth via the account's persona
wonda linkedin follow <vanity-name-or-url> --account <name> # Follow a member or company (wab-only; primary button or under "More"; idempotent)
wonda linkedin comment <activity-id> --account <name> # Add a comment (wab-only: needs SDUI render state)
wonda linkedin reply-comment <activity-id> <comment-id> "Good point." --account <name> # Reply under a specific comment (wab-only)
wonda linkedin mute <vanity-name-or-url> --account <name> # Mute a member's posts in the actor's feed (wab-only; keeps the connection)
wonda linkedin edit-post <activity-id-or-url> "Updated body" # Edit your own post (wab-only: menu -> Edit post -> Save -> verify)
wonda linkedin edit-comment <activity-id-or-url> <comment-id> "Updated comment" # Edit your own comment (wab-only: comment menu -> Edit -> Save -> verify)
wonda linkedin like <activity-urn>                   # Like a post
wonda linkedin like <activity-urn> --comment <commentId>        # Like a specific comment (wab-only)
wonda linkedin like <activity-urn> --comment <commentId> --reaction love  # React to a specific comment
wonda linkedin unlike <activity-urn>                 # Remove a like
wonda linkedin unlike <activity-urn> --comment <commentId>      # Remove your reaction from a specific comment (wab-only)
wonda linkedin send-message <conversation-urn> "Hi!" # Send a message
wonda linkedin inmail <vanity-name> --message "Hi!" --subject "Quick question" # Native LinkedIn InMail (wab-only)
wonda linkedin post "Excited to announce..."         # Create a post
wonda linkedin post "A quick visual note" --media ./image.png --via wab # Create a post with media
wonda linkedin delete-post <activity-id>             # Delete a post
wonda linkedin delete-comment <comment-url-or-activityId:commentId> # Delete your own comment (WAB: comment menu -> Delete -> confirm -> verify)
wonda linkedin feed-engage --authors "a,b" --duration 5m  # Scroll the feed and like posts from these authors (wab-only)
wonda linkedin feed-engage --keywords "short form video" --reply --max-reply 3  # Monitor content search, gate relevance, comment via WAB
wonda linkedin feed-engage --authors "a,b" --engage-comments --max-comment-engage 2  # Also react to matching comments on engaged posts
wonda linkedin engage-commenters --post <activity-id-or-url> --actions like,reply,connect --reply-text "Good point." --connect-note "I liked your perspective here." --max-commenters 25 --duration 3m  # Read a post's commenters, then like, reply, or connect (paid, WAB writes)

# Account creation (wab-only, flagged: linkedinAccountCreationEnabled)
wonda linkedin signup --persona <name> --random                                     # Create a brand-new account end-to-end
wonda linkedin signup --persona <name> --email <addr> --first-name Ada --last-name Lovelace --password <pw>
wonda linkedin signup --persona <name> --job-title "Engineer" --company "Acme"       # Profile stage with employment (default: student path)
wonda linkedin signup --persona <name> --resume code --email <addr>                  # Resume after a manual step
```

Paginated commands support: `-n <count>`, `--start`, `--all`, `--max-pages`, `--delay <ms>`.

`wonda linkedin profile` includes additive `emails`, `websites`, `phone`, and `twitter` fields when the member exposes them in LinkedIn's Contact info. The contact-info read uses the same logged-in Voyager cookie and CSRF path as profile reads, is best-effort when hidden or rate-limited, and is equivalent to manually opening the Contact info overlay. It does not infer, enrich, persist, or batch-harvest contacts.

`wonda linkedin profile` also returns `education` (a list of `{school, degree, fieldOfStudy, startYear, endYear}`, `endYear` 0 meaning ongoing), `yearsOfExperience` (career span in years, computed from the earliest dated experience; 0 if none), and the full `experiences` work history (each `{title, companyName, companyUrn, companyUniversalName, startYear, startMonth, endYear, location}`, `endYear` 0 meaning current) plus `currentCompany` in the same shape for the present role. These read over the same logged-in Voyager cookie/CSRF path as the rest of the profile and are best-effort when hidden or rate-limited.

**LinkedIn profile visit warm-up:** `wonda linkedin visit <vanity-or-url> --account <name>` is WAB-only and intentionally separate from `wonda linkedin profile`. `profile` is a stealth data read and does not fire viewed-your-profile. `visit` opens the real `/in/<vanity>/` page in the persona browser, dwells for roughly 6-20s by default, makes a light scroll pass unless `--no-scroll` is set, and returns `{ ok, status, profile, dwellMs, scrolled }`. Private or anonymous LinkedIn profile-viewing settings can suppress the target notification.

**LinkedIn account creation:** `wonda linkedin signup` provisions a brand-new LinkedIn account: it mints a throwaway mailbox (or uses `--email`), drives the join flow (email plus password, name, emailed verification code, profile) in a headful WAB window, fetches the verification PIN from the inbox, then binds the persona and syncs cookies so LinkedIn reads and writes route through the new account. Gated by the `linkedinAccountCreationEnabled` flag (server-evaluated preflight: `GET /linkedin/signup/enabled`). Bind a mobile or residential proxy to the persona first (`wonda wab config set <persona> proxy_url socks5://...`): LinkedIn shadowbans accounts born on datacenter IPs even harder than Reddit. LinkedIn frequently inserts a captcha or "security verification" puzzle the flow cannot pass automatically; when a field cannot be located the flow pauses and leaves the window on that screen, so finish by hand then re-run with `--resume <step>` (`account|name|code|profile|persist`). On success it prints `{name, email, password, persona, account}` plus a ready-to-paste `op item create` block for the "LinkedIn logins" vault.

**Connection request modes:** The `connect` command has two transports:

- **`--via cookies` (API):** Voyager REST API with fingerprint mitigations (profile visit, drawer warm-up, connect). Fast (~3s), supports notes via `customMessage`.
- **`--via wab`:** Routes through the account's persona Chromium (auto-spawned) for full stealth via DOM dispatch. Zero fingerprinting risk. Slower (~10s) but fully safe. Use when you need extra protection. The stealth browser + Chromium install once via `wonda wab install` (~315 MB, idempotent). The persona reuses its persistent profile under `~/.wonda/wab/personas/<persona>/profile`. Cookies live in `~/.wonda/linkedin-cookies/<account>.json`, bound to the persona via `account-bindings.json`; rotating via `wonda linkedin auth set --account <name>` pushes the new cookies into the live Chromium if it's running.

**LinkedIn InMail:** `wonda linkedin inmail <vanity-or-url> --message <body> [--subject <subject>] [--yes-consume-credit] [--dry-run]` drives LinkedIn's native InMail composer in WAB only. It is not `connect` and not `send-message`; first-degree recipients are refused with a pointer to `wonda linkedin send-message`. Open Profile / free InMail can send without credit confirmation. If LinkedIn indicates one InMail credit will be consumed, the command stops with `sent:false` and exits 0 unless `--yes-consume-credit` is provided. `--dry-run` fills the composer and stops before Send.

**LinkedIn public profile enrichment:** `wonda linkedin enrich <profile-url-or-vanity...>` defaults to `--via cookies`, uses the local logged-in profile read path one profile at a time, reuses `_artifacts/linkedin-cache`, adds jitter between misses, aborts on 429-style rate-limit signals, and rejects more than 25 inputs. Use `--via public` for paid public enrichment through `POST /api/v1/scrape/linkedin-profiles`, polling `GET /api/v1/scrape/linkedin-profiles/{taskId}` until completion unless `--no-wait` is set. Cancel a running paid scrape with `wonda scrape cancel <taskId>`. Public mode supports `--force-refresh`, `--timeout 10m`, `--idempotency-key`, and `--output json|table`. The single-profile `wonda linkedin profile --via public` path uses the same paid route and also supports `--force-refresh`, `--timeout`, and `--idempotency-key`.

**LinkedIn sent invitation tracking:** `wonda linkedin sent-invitations` is read-only and defaults to `--via cookies`. It lists live pending outgoing invites and, by default, reconciles them with the local WAB connect audit to label audited targets as `accepted`, `pending`, or `withdrawn`; pass `--reconcile=false` for the raw paginated pending list or `--no-connection-check` to skip per-target connection-status reads. `--via wab` routes the same reads through the account persona. LinkedIn's sent-list Voyager endpoints currently churn, so the command falls back to the read-only sent-invitations manager page payload when Voyager rejects the sent list. `--via public` and `--via api` are not supported.

**Engager enrichment:** `wonda linkedin enrich-engagers --activity-id <id>` scrapes reactors (and optionally commenters via `--comments`), then fetches each engager's profile + current employer + company page, and emits a single joined JSON document keyed by vanity with `profile` and `currentEmployer` (industry, headcount, HQ, description, employee count) blocks per engager. Use `--company-detail=false` to skip company page lookups and keep only inlined employer identity (`name`, `urn`, `universalName`). Use `--max-profiles N` to cap the batch (default 250, hard ceiling 250 unless `--override-max-profiles` is set) and `--out file.json` to write to disk. `--profile-source cookies|public` controls only per-profile detail enrichment; engager collection still uses logged-in LinkedIn access.

For ICP qualification of post engagers, run `wonda skill get linkedin-icp-qualify`.

### Instagram

A first-class platform with three transports selected by `--via`, the same legitimacy gradient as the others:

- `--via api` — official Graph API via your connected OAuth account (`--connection`). ToS-safe, used for publishing.
- `--via cookies` — private mobile API via the local cookie `--account`. Used for reads (saved posts, comments).
- `--via wab` — browser DOM via the account's Wonda Automation Browser persona. Used for the `comment` write (drives the reel's inline comment composer with a real-browser fingerprint, the same stealth path X reply / LinkedIn comment use).

Transports are per-operation capabilities: `saved` and `comments` are cookies-only (no Graph endpoint for them), `post`/`carousel` are api-only, and `comment` is wab-only. The two identities are distinct: `--account`/`--sessionid` = the local cookie identity; `--connection` = the OAuth `instagram_account` UUID. For `--via wab` the persona is auto-derived from `--account` (or pass `--persona` directly); the WAB injects the bound account's `sessionid` (+ `ds_user_id`) into the Chromium cookie jar at spawn.

> ⚠️ **Same anti-fraud caution as the others: don't probe freshly-pasted cookies.** The first request on a new `sessionid` should be the operation you wanted. Instagram flags burst activity from a new IP/process on a freshly-handed session.

```bash
# Auth setup — local cookie identity (run `wonda instagram auth --help` for details)
wonda instagram auth set --sessionid <value>                # Just the sessionid cookie (simplest)
wonda instagram auth set --cookies "$(pbpaste)"             # Full DevTools cookie: header (also captures ds_user_id)
wonda instagram auth set --account <name> --sessionid <v>   # Multi-account
wonda instagram auth set --account <name> --sessionid <v> --persona <persona>  # Also bind to a WAB persona

# Read (cookies)
wonda instagram saved                                       # Your saved posts (--all to walk all pages)
wonda instagram saved --jq '.posts[] | {authorHandle, url}' # Project fields out of the result
wonda instagram comments https://instagram.com/reel/<code>/ # A post/reel's comments (--all to walk all pages)
wonda instagram comments <code> --jq '.comments[] | {authorHandle, text}'  # Bare shortcode also works

# Publish (--via api, default — the official Graph API via your connected account)
wonda instagram post --media <media-id> --caption "Hello"   # Single image/reel
wonda instagram post --media <id> --connection <ig-uuid>    # Pick the connected account explicitly
wonda instagram carousel --media <id1> --media <id2>        # 2-10 image carousel

# Comment on a reel (--via wab only — drives the inline composer in the WAB)
wonda instagram comment https://instagram.com/reel/<code>/ "Great reel!" --persona my-account
wonda instagram comment <code> "Love this" --persona my-account   # Bare shortcode also works

# Feed-engage (--via wab only: scroll the home feed and like target authors' posts)
wonda instagram feed-engage --authors "a,b" --duration 5m --persona my-account  # Scroll the feed and like posts from these authors (wab-only)
```

`--account` selects the cookie file under `~/.wonda/instagram-cookies/<account>.json`. For `saved`, carousels contribute every child's media URL (videos win over images for the per-item URL); pagination uses the `max_id` cursor (`--cursor`, `--all`, `--max-pages`, `--delay <ms>`). `comments` takes a `/p/<code>/` or `/reel/<code>/` URL (or a bare shortcode), decodes it to the numeric media id locally, then pages the same `max_id` cursor; the result carries each comment's `id`, `text`, `authorHandle`, `authorName`, `createdAt`, `likeCount`, `replyCount` plus the parent media's total `commentCount`. For posting, `wonda instagram post --via api` and `wonda publish instagram` share the same Graph-API path. `comment` (write) takes a `/reel/<code>/` or `/p/<code>/` URL (or bare shortcode) plus the text, and is wab-only: it auto-spawns the persona's WAB if needed, types into the inline composer, submits, and writes a `comment` audit row to `~/.wonda/wab/audit.jsonl` (failures fire `wab_action_failed` telemetry and drop a failure bundle).

### Reddit

Reddit's transport is fixed per command kind, so `--via` is mostly not yours to choose here:

- **Reads** (search, subreddit, feed, user, user-posts, user-comments, post, trending, home, saved) run direct via a Chrome-fingerprinted Go HTTP client (fast, ~700ms p50). Cookies only. `--via wab` is not available for reads and errors.
- **Writes** (vote, comment, subscribe, save, unsave, delete, and subreddit `submit`) dispatch through the account's Wonda Automation Browser so the shreddit GraphQL mutations carry a real-browser signal. WAB only. `--via cookies` errors on these.
- **Submit to a profile self-post** (`u_<handle>` / `u/<handle>`) **or a link post** goes via the tls-client (cookies) only. `--via wab` is not available for those (no DOM submit URL), so `--dry-run` (DOM-only) does not apply to them either.

`--account` selects the cookie file under `~/.wonda/reddit-cookies/` (and, for writes, the account's auto-derived persona). You don't pass a persona here.

> ⚠️ **Anti-fraud caution on freshly-pasted cookies.** `wonda reddit auth check` is safe (it only decodes the JWT exp locally), but the FIRST read or write you fire on new cookies hits Reddit's API from your IP / process. If those cookies were last used elsewhere (different machine, different country), Reddit's anti-fraud trips the session-theft heuristic and may force-logout the cookies. Pattern: paste cookies, go straight to the operation the user wanted. Never do a "let me just check this works" round-trip first.

```bash
# Auth setup (run `wonda reddit auth --help` for details)
wonda reddit auth set --cookies "$(pbpaste)"                         # Paste full DevTools cookie: header
wonda reddit auth set --account <name>-1 --cookies "$(pbpaste)"      # Multi-account
wonda reddit auth set --account <name>-1 --from-keychain             # Opt-in: read from browser Keychain
wonda reddit auth check

# Read (direct tls-client, --account picks the session for logged-in views)
wonda reddit search "AI video" --sort top --time week   # Search posts (sort: relevance, hot, top, new, comments)
wonda reddit subreddit marketing                        # Subreddit info
wonda reddit rules marketing                            # Subreddit posting rules (+ site-wide rules)
wonda reddit feed marketing --sort hot                  # Subreddit posts (sort: hot, new, top, rising)
wonda reddit comments marketing                         # Newest comments across a subreddit (find reply opportunities)
wonda reddit user spez                                  # User profile
wonda reddit user-posts spez --sort top                 # User's posts
wonda reddit user-comments spez                         # User's comments
wonda reddit post <id-or-url> -n 50                     # Post with comments
wonda reddit analytics <id-or-url>                      # Owner viewCount plus public score, upvoteRatio, commentCount
wonda reddit trending --sort hot                        # Popular/trending posts
wonda reddit home --sort best                           # Your home feed (requires auth)
wonda reddit saved                                      # Your saved posts + comments (requires auth; --all to walk all pages)
wonda reddit whoami                                     # Your own account identity: username + id + karma (requires auth; alias: me)
wonda reddit inbox                                      # Classic notifications: replies to your posts/comments, mentions, old PMs (requires auth)
wonda reddit inbox --unread                             # Only unread; --type mentions for mentions only

# Write (wab-only via the account's persona; --account selects the identity)
wonda reddit submit marketing --title "Great tool" --text "Check this..." --account <name>-1   # Subreddit text post (DOM)
wonda reddit submit marketing --title "..." --text "..." --flair "Discussion" --account <name>-1 # Subreddit text post with flair
wonda reddit submit u_<your-handle> --title "..." --text "..." --account <name>-1               # Profile self-post (tls-client / cookies only)
wonda reddit submit marketing --title "..." --url "https://..." --account <name>-1              # Link post (tls-client / cookies only)
wonda reddit comment t3_<post-id> --text "Nice post!" --account <name>-1
wonda reddit comment t1_<comment-id> --text "..." --post-id t3_<post-id> --account <name>-1 # Nested reply (needs parent post-id)
wonda reddit vote <fullname> --up --account <name>-1     # Upvote (--down, --unvote)
wonda reddit vote t1_<comment-id> --up --post-id t3_<post-id> --account <name>-1
wonda reddit subscribe marketing --account <name>-1      # Subscribe (--unsub to unsubscribe)
wonda reddit save <fullname> --account <name>-1          # Save a post or comment (--post-id for t1_*)
wonda reddit unsave <fullname> --account <name>-1
wonda reddit delete <fullname> --account <name>-1        # Delete your own post or comment
wonda reddit feed-engage --authors "a,b" --duration 5m   # Scroll the feed and upvote posts from these authors (wab-only)
wonda reddit feed-engage --keywords "ai video,ugc ads" --subreddits SaaS,marketing --reply --max-reply 3  # Monitor scoped searches, gate relevance, comment via WAB

# Account creation (wab-only, flagged: redditAccountCreationEnabled)
wonda reddit signup --persona <name> --random                                       # Create a brand-new account end-to-end
wonda reddit signup --persona <name> --email <addr> --username <handle> --password <pw>
wonda reddit signup --persona <name> --resume credentials                           # Resume after a manual step
```

`wonda reddit user` includes additive `emails` and `links` fields when the user has published explicit contact details in their public About text. These fields are read-only and equivalent to manually reading the profile. No inferred emails, enrichment data, storage, or DOM scraping is involved.

Add `--dry-run` on a subreddit `comment` or `submit` to type into the composer but not click Post (useful for review). It is DOM-only, so it does not apply to profile self-posts or link posts. For subreddit submits, pass `--flair "<label>"` to select post flair in the composer. Flair labels match case-insensitively with normalized whitespace, first by exact label and then by contains fallback. If a subreddit requires flair and it is omitted, or if the requested flair does not exist, the command fails with the available flair labels. `--flair` is not supported with profile self-posts or `--url` link posts.

`wonda reddit signup` provisions a brand-new Reddit account: it mints a throwaway mailbox (or uses `--email`), drives the 5-stage register form (email, emailed code, username plus password, age, interests) in a headful WAB window, fetches the verification code from the inbox subject line, then binds the persona and syncs cookies so reddit reads and writes route through the new account. Gated by the `redditAccountCreationEnabled` flag (server-evaluated preflight: `GET /reddit/signup/enabled`). Bind a mobile or residential proxy to the persona first (`wonda wab config set <persona> proxy_url socks5://...`): Reddit shadowbans accounts born on datacenter IPs. If a field cannot be located the flow pauses and leaves the window on that screen; finish by hand, then re-run with `--resume <step>`. On success it prints `{username, email, password, persona}` plus a ready-to-paste `op item create` block for the "Reddit logins" vault.

Paginated commands support: `-n <count>`, `--after <cursor>`, `--all`, `--max-pages`, `--delay <ms>`.

**Feed-engage author mode** (`wonda {linkedin,x,reddit,instagram} feed-engage`): scroll the home feed like a human and engage only the posts that scroll past from your target authors. On reddit that engagement is an upvote, on the others a like. It is WAB-only (it drives a live browser scroll + click through the account's persona, so there is no cookie path) and opportunistic: it never opens profiles or searches, it just rides the feed and acts when a target's post appears. Pass the targets with `--authors "alice,bob"` (comma-separated handles/vanities/usernames, leading `@` and `u/` are stripped) or `--authors-file <path>` (one author per line, local use only). `--duration` caps the wall-clock browse time (e.g. `5m`, `90s`, default `2m`) and `--max-engage` caps the number of successful likes/upvotes (default `8`); whichever limit hits first stops the run. Pacing is human (eased scrolling, randomized dwell, jittered cursor motion), so let it run for the full duration rather than expecting an instant result.

LinkedIn author mode can also opt into comment reactions with `--engage-comments`: by default it reacts only to comments from `--authors`, `--engage-comments-from any` includes all visible comments, and `--max-comment-engage` caps comment reactions per engaged post (default `3`).

**LinkedIn engage-commenters** (`wonda linkedin engage-commenters`): read commenters on one LinkedIn post, then run the selected per-commenter actions in order: `like`, `reply`, `connect`. Pass the post with `--post <activity-id|urn|url>`. `--actions` accepts `like,reply,connect` and defaults to `like`; `--reply-text` is required when `reply` is selected; `--connect-note` is optional; `--max-commenters` defaults to `25`; `--duration` defaults to `3m`; `--dry-run` resolves targets and opens controls/composers without submitting writes. Access tier: paid/WAB. Transport: commenter reads use the established LinkedIn DOM comments path; every write uses WAB DOM primitives.

**Feed-engage monitor mode** (`wonda {linkedin,x,reddit} feed-engage --keywords ...`): run one bounded keyword/intent monitor pass, score unseen candidates with `/text/generate`, and optionally generate persona replies with `/text/generate`. `--keywords` enables monitor mode and is mutually exclusive with `--authors` and `--authors-file`. Reddit supports `--subreddits SaaS,marketing` to scope search. Without `--reply`, monitor mode is read-only and prints candidates plus relevance verdicts. With `--reply --dry-run`, it generates reply text but posts nothing and leaves the ledger unchanged. With `--reply`, it posts through DOM/WAB writers only: Reddit comment composer, X reply composer, and LinkedIn comment composer. Reads use cookies/tls-client where available: Reddit search and X search use the platform clients; LinkedIn content search uses the existing WAB DOM `search-posts` flow because LinkedIn content search is not reliable through the cookie API. Safety controls: `--max-scan` (default 50), `--relevance-threshold` (default 0.7), `--max-reply` (default 3), `--per-day-cap` (default 8), and a persistent dedupe ledger under `~/.wonda/reply-ledger/`. Generated public replies are post-processed to remove em dashes. Monitor mode is not supported for Instagram.

### Cross-platform DM coverage

| Platform | Read inbox | Read conversation | Send existing thread | Start or cold-DM                   |
| -------- | ---------- | ----------------- | -------------------- | ---------------------------------- |
| LinkedIn | Yes        | Yes               | Yes                  | Yes, via profile/message flow      |
| Reddit   | Yes        | Yes               | Yes                  | Yes, via `wonda reddit chat start` |
| X        | Yes        | Yes               | Yes                  | Yes, via `wonda x dm start`        |

### Reddit chat / DMs

Direct messaging through the WAB. Chat uses the logged-in Reddit browser session
and is available as first-class twin actions with `--via wab`. There is no
separate chat token.

```bash
# Read
wonda reddit chat inbox                                  # List DM conversations with latest messages
wonda reddit chat messages <room-id> -n 50               # Fetch messages from a room

# Write
wonda reddit chat start <username> --text "Hey!"         # Start (or reuse) a DM with a user by username (no room-id needed)
wonda reddit chat send <room-id> --text "Hey!"           # Send a DM into an existing room (mimics browser typing behavior)

# Management
wonda reddit chat accept-all                             # Accept all pending chat requests
```

**Important**: Rate limit DM sends to 15-20/day with varied text to avoid detection. The `send` command drives the browser composer and verifies the rendered message.

### Cloud digital twins (`wonda twin`)

Manage cloud-hosted social personas that run behind mobile proxies. Sessions are server-side; schedules drive recurring tasks (saved-content sync, engagement, agent runs) on a cron.

The MCP twin surface tags read tools as Always allow and write tools as Needs approval. Use `run_campaign` and `schedule_loop` for one-approval autopilot loops; use the per-verb platform tools for supervised actions.

Claude web and Cowork users can connect the cloud twin as a custom remote MCP connector from https://wonda.sh/docs/connect-claude.

```bash
# Sessions
wonda twin list                                          # List twin sessions
wonda twin show <persona>                                # Show one session
wonda twin provision <persona> --region GB               # Provision (flags: --provenance, --spend-cap <microdollars>, --allow <cmd> (repeatable))
                                                         # --max-writes-per-hour <N>: max platform writes/hour before the soft cap logs+meters (0/unset = unlimited)
                                                         # --alert-webhook-url <url> + --alert-webhook-secret <secret>: HMAC-signed owner alert on needs_auth / consecutive failures (secret is write-only)
wonda twin update <persona> --spend-cap <microdollars>   # Change caps + alert webhook post-provision without re-provisioning (flags: --max-writes-per-hour <N>, --alert-webhook-url <url>, --alert-webhook-secret <secret>)
wonda twin pause <persona>                               # Pause a session
wonda twin resume <persona>                              # Resume a paused session
wonda twin needs-auth <persona>                          # Flag a session as needing re-auth
wonda twin needs-auth-view <persona> --platform x        # Flag needs_auth and mint a hosted login session. Returns a browser-openable `viewerUrl` (the raw `wsUrl` is included for custom viewers). A human opens viewerUrl to sign in; login is human-gated (you cannot type credentials for them). Token ~20 min TTL; one twin viewable at a time (open sequentially).
wonda twin recover <persona>                             # Clear an ACTIVE critical safety signal (captcha / unusual-activity / account-restricted) AFTER you have resolved it in-browser. Those criticals do NOT change the twin status, so the safety gate hard-blocks the persona with NO auto-resume until you clear it; this appends a 'recovered' marker the gate reads to stop treating the critical as active. A security checkpoint / needs_auth is cleared by re-login (wonda twin login) instead, not this. -> { recovered, clearedSignalType, persona }
wonda twin login <persona> --platform instagram          # Open a born-in-cloud streamed login in a DEDICATED tab inside your local WAB (the cloud login looks like our antidetect browser, just on the cloud; an existing WAB session in your other tabs is left untouched). Spawns the persona's WAB visibly and opens the viewer at <web-base>/twin-login.html (token in the URL fragment); prints the viewer URL too so you can open it in any browser. On sign-in the stream stops and a Wonda "you are signed in" confirmation replaces it (the platform feed is hidden as you sign in). Unmetered. (--platform <x|linkedin|reddit|instagram>, --web-base default https://wonda.sh)
wonda twin seed-from-cookies <persona> --platform x      # Start a cloud seed job from browser cookies previously stored with /social-tokens. The run output carries per-platform login-status results.
wonda twin login-automated <persona> --platform x        # Attempt credential-vault onboarding; returns { status: needs_human, viewerUrl } when the route cannot finish safely without a human. Open viewerUrl in a browser to complete the sign-in, then re-check with login-status.
wonda twin login-status <persona> --platform x           # Read-only advisory signed-in check from a warm control session.
wonda twin sync-profile <persona> --cookies-only         # Promote local WAB / local cookie jars to the cloud twin profile. Forces local WAB cookie sync first when that persona is running. Use --platform <x|linkedin|reddit|instagram> to limit scope, --dry-run to inspect, --include-storage to upload Chromium storage too.
wonda twin export-cookies <persona> --platform linkedin  # Import sanitized .seeded-cookies from the current cloud twin generation into local ~/.wonda/<platform>-cookies/<account>.json. Refuses newer local jars unless --force; --dry-run shows planned writes; --account-label overrides the local label; --inject-running explicitly pushes imported cookies into already-running bound WAB personas.

# Schedules
wonda twin schedule list --persona <persona>             # List schedules (--persona optional)
wonda twin schedule add <persona> --cron "0 9 * * *" --kind saved_sync --name saved-posts-scrape   # Add (--kind: saved_sync|engage|agent; --command, --prompt, --mode deterministic|agent)
                                                         # --name <label>: human-readable schedule label (e.g. saved-posts-scrape) for listings/audit; optional
                                                         # --command is tokenized quote-aware on the server, so a free-text write body (a post, comment, DM, or InMail) survives as one argument. Quote any body that has spaces.
                                                         # Posting/comment/DM schedules should use --kind engage so they count toward the write-velocity envelope.
                                                         # --jitter-window-seconds N: fire once/day at a random-looking minute within N seconds AFTER the cron time (the cron marks the window start); 0/omitted = fire exactly at the cron minute
                                                         # --output-webhook <url>: deliver each run's captured command stdout to your HTTPS webhook (payload carries a short-TTL signed download URL); --output-webhook-secret <s>: HMAC-SHA256 key signing the body via the X-Wonda-Signature header
wonda twin schedule add <persona> --kind engage --cron "0 10,14,17 * * 1-5" --jitter-window-seconds 1200 --commands "linkedin feed-engage --authors 'alice,bob' --duration 5m"   # Recurring feed-engage on the cloud twin
wonda twin schedule add <persona> --kind engage --cron "0 9 * * 1-5" --command "x tweet 'gm builders' --via wab --account <persona>"   # Scheduled posting with free-text argv preserved
                                                         # NOTE: pass targets inline with --authors (comma-separated, no spaces). --authors-file is local-only; the cloud runner has no filesystem for the file.
                                                         # Platform verbs in schedules are validated against the twin action registry; unknown LinkedIn/Reddit/X/Instagram verbs are rejected even when the twin allowlist is empty.
wonda twin schedule enable <id>                          # Enable a schedule
wonda twin schedule disable <id>                         # Disable a schedule
wonda twin schedule rm <id>                              # Delete a schedule

# Runs
wonda twin runs --persona <persona> --limit 20           # Recent runs
wonda twin run-now <persona> --command <cmd>             # Trigger a run immediately (a WRITE command over the per-identity action limit returns a structured throttled 429). --command is tokenized quote-aware, so quote a free-text body that has spaces: --command "linkedin send-message alice 'hi there :)' --via wab --account alice"
                                                         # Platform verbs are validated against the twin action registry; non-platform commands still pass through the normal allowlist behavior.
                                                         # Media write verbs accept Wonda media ids or signed URLs on the twin: reddit submit --media <media-id>, x tweet/reply/quote --attach <media-id>, linkedin post --media <media-id>. The runner fetches bytes to /tmp and passes a local file path to the platform CLI.
wonda twin run-action --persona <p> <platform> <action> --field key=value   # [DEPRECATED: prefer `<platform> <verb> --engine cloud`] Run one registry-validated action through the warm hosted control session. Still works so running agents are not broken. If cold, returns { status: "warming", retryAfterMs }. Use --payload @file.json for structured payloads. Requires the Premium plan (cloud twin).
wonda twin output <runId>                                # Fetch a run's captured command output (--url prints just the short-TTL signed download URL)

# SENSE layer (read-only "ask before you act" probes; reuse the EXACT decision + caps the write gate enforces)
wonda twin can-act --persona <p> [--action connect]      # Would this twin run this verb (or any write, no --action) right now? -> { canAct, reason, code, deferUntil, actionsRemaining }. Reads/generation always pass.
wonda twin actions --persona <p>                          # Per-action remaining limit + consumed-today + rolling-7d, plus the resolved cap `mode` (global aggregate floor + connect/message/like/comment/visit). `limit` is null when uncapped (unlimited mode).
wonda twin health --persona <p>                           # Liveness (active|paused|needs_auth) + signalCooldown (the derived graded cooldown: strongest unresolved platform signal) + recentSignals (the append-only health-record tail: 429s, captchas, checkpoints). When an unresolved critical (captcha / unusual-activity / account-restricted) is active it prints a `run: wonda twin recover <persona> after resolving in-browser` hint to stderr (stdout JSON is untouched).

# Action caps (per-twin MODE + custom overrides the safety gate enforces)
wonda twin limits get <persona>                           # Show the twin's cap mode (warmup|conservative_steady|moderate_max|unlimited) + custom overrides
wonda twin limits set <persona> --mode moderate_max       # Set the cap mode. unlimited = NO caps at all (no global, no per-action, no weekly)
wonda twin limits set <persona> --connect 30 --message 60 # Set CUSTOM daily caps per action (UNCLAMPED, own risk): --connect/--message/--like/--comment/--visit, --global <N> (daily aggregate), --*-weekly <N> (rolling-7d). Passing override flags MERGES into the stored overrides (other custom caps are kept); --clear-overrides drops them all back to the mode.
```

### Local WAB relay (`wonda relay`)

Run registered twin actions on this machine's local WAB while callers still use the cloud broker and the same `/twin/sessions/{persona}/actions/{platform}/{action}` API.

```bash
wonda relay pair                                        # Pair this machine with your Wonda account using the existing browser login flow
wonda relay run --persona <p>                           # Reverse-connect to the cloud broker and serve actions for a persona
wonda relay status --persona <p>                        # Show local relay configuration
wonda relay stop --persona <p>                          # Clear cloud relay presence for a persona
wonda relay install [--persona <p>]                     # macOS: install the relay as a LaunchAgent (auto-start at login, restarts on crash, logs to ~/Library/Logs/wonda-relay.log). Re-run to restart onto a new binary
wonda relay uninstall                                   # macOS: stop the relay LaunchAgent and remove its plist
```

The relay runs on your real device and IP. Platform cookies stay local. It only serves actions while the machine and `wonda relay run` are up. If no live relay is present, the broker routes the same twin action call to the cloud twin instead.

**Safety is intrinsic to running anything on a twin.** Account safety is NOT a feature of the outreach sequencer: it is a property of "run a command on a twin." The SAME per-identity safety gate guards an ad-hoc agent (`wonda linkedin connect --account <name>`), the autopilot, a `twin schedule`, and the deterministic outreach sequencer, through ONE enforcement path against ONE shared per-identity counter. So a heavy ad-hoc day on a persona tightens the headroom on that persona automatically (one set of ceilings per identity, no double-charge). The caps are a per-twin MODE (warmup / conservative_steady (default) / moderate_max / unlimited; set via `wonda twin limits set`) selecting the per-action daily ceilings, the per-action rolling-7d weekly ceilings, AND a global daily aggregate cap; `unlimited` turns every cap off, and a custom override is UNCLAMPED. The gate classifies each command from its argv: WRITE / social-action commands (connect, send-message, like, comment, visit, ...) are capped; reads (connection-status, conversations, profile, search), generation (image/video/text), and unknown commands pass freely ungated. This is why the SENSE verbs exist: an agent asks `can-act` / `actions` / `health` BEFORE firing, then branches on the typed result instead of attempting a write and catching a deny.

**Uniform error taxonomy (branch on `code`, never on the message).** Every twin/outreach surface returns the existing `{ error: { code, message } }` envelope, and on a quota deny it also carries `deferUntil` (the ISO time the quota resets) + `reason` (the granular gate signal). Agents branch on the typed `code`:

| `code`                | Meaning                                                                                                                                                                                                                                                                                | What the agent should do                                                                                                                      |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `throttled`           | A WRITE was blocked by the per-identity safety gate (umbrella, HTTP 429). The granular cause is in `reason` (`limit_hit` / `weekly_limit_hit` / `warmup_frozen`).                                                                                                                      | Retry after `deferUntil`; or pick another sender.                                                                                             |
| `limit_reached`       | A per-action DAILY cap (connect / message / like / comment / visit, per the twin's cap mode) is spent for the UTC day.                                                                                                                                                                 | Wait for `deferUntil` (next UTC midnight) or use a different action / sender.                                                                 |
| `limit_exhausted`     | The GLOBAL daily aggregate cap (the `_all` floor) OR a per-action rolling-7d weekly ceiling is spent.                                                                                                                                                                                  | Back off this identity until `deferUntil`; rotate to another twin, or raise the cap mode via `wonda twin limits set`.                         |
| `needs_auth`          | The twin's session needs re-authentication (cookie expiry / checkpoint).                                                                                                                                                                                                               | Run `wonda twin login <persona>`; do not retry the write.                                                                                     |
| `sender_blocked`      | The identity is silent-throttled / watchdog-paused (a connect 200'd with no invitationUrn, the twin is paused / warmup frozen, OR an unresolved critical platform signal — captcha / unusual-activity / account-restricted, or a chronic-429 storm). A health stop, not a clean limit. | Stop driving this identity; check `wonda twin health`. For an active critical, resolve it in-browser then run `wonda twin recover <persona>`. |
| `command_not_allowed` | The command is not on the twin's permission allowlist, or it names an unregistered LinkedIn / Reddit / X / Instagram verb.                                                                                                                                                             | Re-provision with `--allow <cmd>` for allowlist denials; drop unregistered platform verbs.                                                    |
| `unsupported_channel` | The argv targets a platform / verb the twin or CLI can't run.                                                                                                                                                                                                                          | There is no such wonda command for this twin; drop it.                                                                                        |
| `invalid_payload`     | A live stream action payload is malformed, including a bad media ref that is not a Wonda media id or `https://` URL.                                                                                                                                                                   | Fix the payload before retrying.                                                                                                              |
| `media_not_found`     | A Wonda media id in a twin media action does not belong to the caller or has no stored object.                                                                                                                                                                                         | Use a media id owned by the account running the twin.                                                                                         |
| `media_fetch_failed`  | The runner could not download a resolved media URL into its per-action scratch directory.                                                                                                                                                                                              | Retry with a fresh signed URL or a reachable Wonda media id.                                                                                  |
| `not_found`           | The twin / campaign / resource does not exist.                                                                                                                                                                                                                                         | Provision / create it first.                                                                                                                  |
| `deferred`            | A structured, non-error deferral: in a BATCH, the gate dropped one over-limit command and ran the rest.                                                                                                                                                                                | Re-enqueue the deferred command after `deferUntil`.                                                                                           |

`wonda twin can-act` returns the SAME `code` + `reason` for a deny that a later write would, so an agent that reads `code: "needs_auth"` from `can-act` and then sees `needs_auth` on a write branches on the one code.

## Workflow & discovery

### Brand extraction (`brand extract`)

Extract a website's design system (colors, typography, radii, shadows, spacing, fonts, logo, hero decor, CSS pattern backgrounds, dashed/dotted border treatments, `:root` custom properties, headline emphasis pattern, film-grain/noise overlay) into a `DESIGN.md` + `tokens.json` + `assets/`. Runs locally via the bundled stealth browser + Chromium driver (the same `wonda wab install` as `wonda wab record` and the authenticated session flows).

Requires a one-time `wonda wab install` to download the stealth browser + Chromium (~300 MB, shared across `wonda wab record`, the authenticated session flows, and `brand extract`).

This is the in-house replacement for the previous `npx`-based brand-extraction CLI used in the `slide-generation` / `creative-static-ads` / `premium-static-ads` skills.

```bash
# Local-only — no auth, no credits, no API call
wonda brand extract https://linear.app                       # Writes ./output/linear.app/{DESIGN.md, tokens.json, assets/}
wonda brand extract https://stripe.com --output ./refs       # Writes ./refs/stripe.com/...
wonda brand extract https://vercel.com --screenshot          # Also writes page.png
wonda brand extract https://stripe.com --viewport 1440x900   # Override default 1920x1080

# Persist to the server (uploads assets via media presign + POSTs /brand/save)
wonda brand extract https://stripe.com --save                # Local + persist
wonda brand extract https://stripe.com --save --make-active  # Local + persist + activate (the common path)
wonda brand extract https://stripe.com --no-output --save    # Don't write to disk, persist only

# Move a persisted brand around
wonda brand save --from ./output/stripe.com --make-active    # Persist a previously-extracted dir
wonda brand pull <brand-id>                                  # Download a saved brand back to ./output/<domain>/
```

Flags:

- `--save`: upload `assets/` via the media presign flow and POST `{tokens, mediaIds}` to `/api/v1/brand/save`. Requires auth.
- `--make-active`: implies `--save`. Sets the new brand as active.
- `--output <dir>`: override the local output dir. Default is `./output/<domain>/`. Mutually exclusive with `--no-output`.
- `--no-output`: don't write to disk (in-memory extract for piping). Mutually exclusive with `--output`.
- `--name "Brand Name"`: override the brand name when persisting. Defaults to the domain stem capitalized.
- `--screenshot`: also save `page.png` alongside DESIGN.md.
- `--viewport WxH`: viewport size for the headless browser. Default `1920x1080`.

Outputs (when `--no-output` is not set, always to `<output-dir>/<domain>/`):

- `DESIGN.md`: Markdown summary of tokens, typography, hero decor, logo, CSS patterns, dashed borders, and root CSS variables. Read this in the slide / static-ad skills before composing HTML.
- `tokens.json`: raw structured JSON of the extraction.
- `page.png`: only when `--screenshot` is passed.
- `assets/`: raw hero decor files plus `assets/fonts/` for any non-Google `@font-face` URLs. Always written when not `--no-output`.

Prints written file paths to stdout. With `--save`, also prints the API response (`brandId`, `sourceDomain`, `warnings`). Non-zero exit on failure (network error, navigation timeout, browser crash, save failure).

### Video analysis

Analyze a video to extract a composite frame grid (visual) and audio transcript (text). Useful for understanding video content before creating variations. Requires a **full account** (not anonymous) and costs credits based on video duration (ElevenLabs STT pricing).

If the video was just uploaded and is still normalizing, the CLI auto-retries until the media is ready.

```bash
# Analyze a video — returns composite grid image + transcript
ANALYSIS_JOB=$(wonda analyze video --media $VIDEO_MEDIA --wait --quiet)

# The job output contains:
# - compositeGrid: image showing 24 evenly-spaced frames
# - transcript: full text of any speech
# - wordTimestamps: word-level timing [{word, start, end}]
# - videoMetadata: {width, height, durationMs, fps, aspectRatio}

# Download the composite grid for visual inspection
wonda analyze video --media $VIDEO_MEDIA --wait -o /tmp/grid.jpg

# Get just the transcript
wonda analyze video --media $VIDEO_MEDIA --wait --jq '.outputs[] | select(.outputKey=="transcript") | .outputValue'
```

**Error handling**: 402 = insufficient credits, 409 = media still processing (CLI auto-retries).

### Email

Manage throwaway email accounts and read mailbox messages. These commands require the `emailServerApiEnabled` flag.

```bash
wonda email account create [email]                    # Create an email account
wonda email account create --random --domain <domain> # Create an email with a random username
wonda email account create --username <name> --domain <domain> # Create an email with a chosen username
wonda email account get <email>                       # Get email account details
wonda email account delete <email>                    # Delete an email account

wonda email inbox list <email>                        # List inbox messages
wonda email inbox read <email> <id>                   # Read a specific email with verification codes
wonda email inbox wait <email> --timeout 60           # Wait for a new email to arrive
wonda email inbox wait <email> --since "$SINCE"       # Only messages after an RFC 3339 timestamp
wonda email inbox wait <email> --since-id "$MAX_ID"   # Only messages with id greater than this
```

For signup flows, capture `--since` before triggering the verification email, or snapshot the current max message id with `wonda email inbox list <email> --jq '[.[].id] | max // 0'` and pass it to `--since-id`.

### Jobs

```bash
wonda jobs get inference <id>                         # Inference job status
wonda jobs get editor <id>                            # Editor job status
wonda jobs get publish <id>                           # Publish job status
wonda jobs wait inference <id> --timeout 20m          # Wait for completion
```

### Discovery

```bash
wonda models list                                     # All available models
wonda models info <slug>                              # Model details and params
wonda operations list                                 # All editor operations
wonda operations info <operation>                     # Operation details
wonda capabilities                                    # Full platform capabilities
wonda pricing list                                    # Pricing for all models
wonda pricing estimate --model seedance-2 --prompt "..." # Cost estimate
wonda style list                                      # Available visual styles
wonda balance                                         # Current credit balance (org wallet in org context)
wonda usage                                           # Spend summary for the current month (per model/project)
wonda usage --month 2026-05                           # ...for a calendar month
wonda usage --from 2026-04-01 --to 2026-06-30         # ...for a custom range
wonda usage --project acme-launch                     # ...restricted to one project
wonda project list                                    # Spend-tagging projects in the active scope
wonda project create acme-launch                      # Create one (org scope: admin/owner only)
wonda use --project acme-launch                       # Tag subsequent spend with it (sticky)
wonda topup                                            # Top up credits (opens Stripe checkout)
```

### Editing audio & images

```bash
# Edit audio
wonda edit audio --operation <op> --media <id> --wait -o out.mp3
```

For any image edit (crop, text overlay, img2img, background removal, vectorize) pull the dedicated skill: `wonda skill get image-edit`.

### Alignment (timestamp extraction)

```bash
wonda alignment extract-timestamps --model <model> --attach <mediaId> --wait
```

## Quality tiers

| Tier     | Image Model                                    | Resolution                              | Video Model              | When                                                                                                                                               |
| -------- | ---------------------------------------------- | --------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Standard | `gpt-image-2` (auto) — alt: `nano-banana-2` 1K | 1024×1024 / 1024×1536 (gpt) / 1K (nano) | `seedance-2` (high, 5s)  | Default. gpt-image-2 for strongest prompt adherence + text-in-image; nano-banana-2 for faster Gemini iteration with multi-reference support.       |
| High     | `gpt-image-2` (high) — alt: `nano-banana-2` 2K | 1024×1024 / 1024×1536 (gpt) / 2K (nano) | `seedance-2` (high, 15s) | Crisp output. Use `--params '{"quality":"high"}'` on gpt-image-2 or bump `--params '{"resolution":"2K"}'` on nano-banana-2. Also offer `sora2pro`. |
| Max      | `nano-banana-pro` 4K — alt: `nano-banana-2` 4K | 4K                                      | `seedance-2` (high, 15s) | True 4K (gpt-image-2 caps at 1536px). Use `--params '{"resolution":"4K"}'`. Also offer `sora2pro` (1080p) for video.                               |

## Troubleshooting

| Symptom                          | Likely Cause                                  | Fix                                                    |
| -------------------------------- | --------------------------------------------- | ------------------------------------------------------ |
| Sora rejected image              | Person in image                               | Switch to `kling_3_pro`                                |
| Video adds objects not in source | Motion prompt describes elements not in image | Simplify to camera movement and atmosphere only        |
| Text unreadable in video         | AI tried to render text in generation         | Remove text from video prompt, use textOverlay instead |
| Hands look wrong                 | Complex hand actions in prompt                | Simplify to passive positions or frame to exclude      |
| Style inconsistent across series | No shared anchor                              | Use same reference image via `--attach`                |
| Changes to step A not in step B  | Stale render                                  | Re-run all downstream steps                            |

## Timing expectations

- Image: 30s - 2min
- Video (Sora): 2 - 5min
- Video (Sora Pro): 5 - 10min
- Video (Veo 3.1): 1 - 3min
- Video (Kling): 3 - 8min
- Video (Grok): 2 - 5min
- Music (Suno): 1 - 3min
- TTS: 10 - 30s
- Editor operations: 30s - 2min
- Lip sync: 1 - 3min
- Video upscale: 2 - 5min

## Error recovery

- **Unknown model**: `wonda models list`
- **No API key**: `wonda auth login` or set `WONDA_API_KEY` env var
- **Job failed**: `wonda jobs get inference <id>` for error details
- **Bad params**: `wonda models info <slug>` for valid params
- **Timeout**: `wonda jobs wait inference <id> --timeout 20m`
- **Insufficient credits (402)**: `wonda topup` to add credits
