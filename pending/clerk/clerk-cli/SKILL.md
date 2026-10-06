---
name: clerk-cli
description: >-
  Operate the Clerk CLI (`clerk` binary) for authentication, user/org/session
  management, impersonation, local webhook testing, deploy verification,
  instance config, env keys, feature toggles, and any Clerk Backend, Platform,
  or Frontend API call. Use when the user mentions Clerk management tasks,
  "list clerk users", "impersonate a user", "test webhooks locally",
  "enable orgs", "enable billing",
  "clerk env pull", "clerk doctor", "clerk deploy", "clerk api", or any ad-hoc
  Clerk API request. Prefer the CLI over raw HTTP: it handles auth, key
  resolution, app/instance targeting, and formatting automatically.
license: MIT
---

# Clerk CLI

The `clerk` binary is a pre-authenticated gateway to Clerk's Backend API and Platform API, plus project-level tooling (auth, linking, env pulls, instance config). When the user asks anything that touches a Clerk resource, reach for `clerk` first instead of hand-rolling `curl`.

For setup or `init` requests, use the [`clerk-setup`](../clerk-setup/SKILL.md) skill as the source of truth. Its package-runner, accountless, migration, and init-first guidance takes precedence over the general operational prerequisites below.

> This skill targets clerk `latest`. If `clerk --version` disagrees with the latest available CLI, refresh it with `clerk update`, or invoke the latest through a package runner such as `bunx clerk@latest`. The binary is always the source of truth, so run `clerk <command> --help` to verify anything this skill claims.

## Execution environment (prefer the host, understand the sandbox warning)

Most AI coding agents default to running shell commands in a sandbox where the
user's home directory, OS keychain, browser launch, localhost callback
binding, or network access may be blocked. The Clerk CLI depends on all of
those host capabilities:

- **OS credential store**: `clerk auth login` stores the OAuth token in the
  system keychain. A sandbox without keychain access reports "not logged in"
  even when the host is authenticated.
- **Home-directory Clerk state**: saved config, cached metadata, and fallback
  credentials live under the user's Clerk config/data directories.
- **Linked project metadata**: resolved from the repo's git remote plus Clerk
  config. Sandboxes with stripped repo state or blocked home-dir reads can
  misreport "not linked".
- **Local `.env*` files**: publishable and secret keys materialized by
  `clerk env pull`.
- **Outbound network access to Clerk**: every Backend and Platform API call.
- **Browser + localhost OAuth callback**: `clerk auth login` needs both.

In agent mode, the CLI now does a **best-effort warn-once check** at the
host-sensitive library boundaries. When it detects that host-only Clerk state
or system capabilities are unavailable, it emits:

```text
Host-only Clerk state or system capabilities may be unavailable in agent mode. This may be a sandboxed run.
Re-run this command on the host shell before trusting auth, link, env, or API failures.
```

Treat that warning as authoritative. The command may continue, but any auth,
link, env, config, API, browser, or OAuth callback failure from that
invocation is untrusted until you rerun the same command on the host.

**Prefer these commands on the user's host shell, not in a sandbox:**

`clerk doctor`, `clerk whoami`, `clerk auth login`, `clerk link`, `clerk env pull`,
`clerk apps ...`, `clerk config ...`, `clerk api ...`.

If a command was accidentally run in a sandbox and it reports `Not logged in`,
`auth_required`, `not linked`, missing env, keychain/file permission errors,
or network failures, **do not treat the result as authoritative**. Rerun it on
the host before acting on it or reporting it to the user.

## Invoking the CLI

Before running any `clerk` command, figure out which binary to invoke and bind that choice for the rest of the session:

```sh
# 1. Prefer a globally installed binary when it matches the skill's target version.
command -v clerk >/dev/null 2>&1 && clerk --version
```

If that prints `latest` or any version you trust, use bare `clerk` for the rest of the session.

Otherwise fall back to a package runner, in this order (matches the CLI's own `preferredRunner` logic, which prefers the runner that matches the project's lockfile):

| Project package manager   | Invocation                       |
| ------------------------- | -------------------------------- |
| bun (`bun.lock*`)         | `bunx clerk@latest`     |
| npm (`package-lock.json`) | `npx -y clerk@latest`   |
| pnpm (`pnpm-lock.yaml`)   | `pnpm dlx clerk@latest` |
| yarn >= 2 (`yarn.lock`)   | `yarn dlx clerk@latest` |

Yarn Classic (v1) has no `dlx`; treat those projects as "no preferred runner" and fall back to the first runner from the list above that's on PATH.

The published npm package is **`clerk`**, not `@clerk/cli`. Never teach `npm install -g clerk` as the primary path. If the global CLI is stale or behaves differently from this skill, either upgrade the global install or fall back to the `latest` runner form above.

## Prerequisites (run at session start for non-setup operations)

Except when following `clerk-setup`, verify the CLI is authenticated, linked, and healthy before running other Clerk commands in a session:

```sh
clerk --version               # confirm the binary is on PATH
clerk doctor --json           # structured health check; exit 1 if anything failed
```

**Always run `clerk doctor --json` first.** It catches the common setup failures (not logged in, project not linked, missing keys, stale CLI version) up front, so later commands don't fail with confusing errors. In agent mode it also includes a `Host execution` check that warns when Clerk's host-side config / credential directories are not writable, which is the canonical signal that the current invocation is likely sandboxed.

Each result has `name`, `status` (`pass`/`warn`/`fail`), `message`, optional `detail`, optional `remedy` (how to fix it), and optional `fix` (label for auto-fixable issues). Parse that and act on it, or surface it to the user. If `Host execution` warns, rerun the command on the host before trusting any auth/link/env/API failures from the same sandboxed run. Rerun `clerk doctor --json` whenever a later command starts misbehaving.

If `clerk --version` reports a newer CLI than this skill covers, trust `clerk <command> --help` first and refresh this skill bundle from its source. The reverse also applies: `--accountless` and the `accountless` JSON keys ship in CLI 3.3+ — on an older CLI, use the `--keyless` alias or upgrade.

## Accountless setup

`clerk init` does **not** require `clerk auth login`: on a framework with accountless support, an unauthenticated bootstrap with no `--app`, or an unauthenticated agent run with no `--app` or existing project link, mints an unclaimed accountless app with temporary development keys — no account, no browser, no flag. (A signed-out human re-running it in an *existing* project gets the login flow instead — `--accountless` forces the temporary-keys path.) Most instance commands then work on that key alone.

Two things to know before you use it: the accountless path follows whatever `sk_` key is local — `sk_live_` included, claimed or not — so pass `--app <id>` when you mean a real app; and `clerk open` returns a credential-equivalent claim URL, never safe to paste into a log or PR.

Which commands need an account, and the full rules: [auth.md](references/auth.md#accountless-operating-without-an-account).

## The mental model

| Layer                           | What it does                                                                                 | Commands                                                       |
| ------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **Session / project**           | Auth, link a repo to a Clerk app, pull env keys                                              | `auth login`, `link`, `unlink`, `whoami`, `env pull`, `doctor` |
| **Instance config**             | Manage the configuration (social providers, session lifetimes, etc.) for a specific instance | `config pull`, `config schema`, `config patch`, `config put`   |
| **Backend API (default)**       | Runtime data: users, orgs, sessions, invitations, JWT templates, webhooks                    | `clerk api <path>`                                             |
| **Platform API (`--platform`)** | Account-level: applications, instances, billing                                              | `clerk api --platform <path>`                                  |
| **Frontend API (`--fapi`)**     | The instance's public client-facing API (what clerk-js calls)                                | `clerk api --fapi <path>`                                      |

A project is "linked" to an application via `clerk link`. Once linked, most commands auto-resolve the target app and dev instance from the repo's git remote. To target something else, pass `--app <id>` and/or `--instance dev|prod|<instance_id>`. See [references/auth.md](references/auth.md) for the full resolution order.

## Discover endpoints - don't memorize them

The CLI ships with the Clerk OpenAPI catalog. Always discover endpoints dynamically instead of guessing paths:

```sh
clerk api ls                  # list every Backend API endpoint
clerk api ls users            # filter by keyword (matches path, summary, tag, operationId)
clerk api ls --platform apps  # list Platform API endpoints
```

Use this before `clerk api <path>`. If you don't see the endpoint you expected, it probably isn't exposed.

## The `clerk api` command (the workhorse)

`clerk api` makes authenticated HTTP calls. It auto-resolves keys, auto-detects method from body presence, supports stdin, and can preview mutations with `--dry-run`.

```sh
# GET requests
clerk api /users                                  # list users
clerk api /users/user_abc123                      # fetch one
clerk api /users?limit=5&order_by=-created_at     # query params work inline

# Mutating requests
clerk api /users -d '{"email_address":["a@b.co"]}'          # POST (auto-detected from body)
clerk api /users/user_abc123 -X PATCH -d '{"first_name":"A"}'
clerk api /users/user_abc123 -X DELETE

# Body from file or stdin
clerk api /users --file payload.json
cat payload.json | clerk api /users

# Always preview mutations first
clerk api /users/user_abc123 -X DELETE --dry-run
clerk api /users/user_abc123 -X DELETE --yes      # skip confirmation once you've verified

# Target a specific app/instance
clerk api /users --app app_abc123 --instance prod

# Include response headers when debugging
clerk api /users --include

# Platform API (account-level, not tenant data)
clerk api /v1/platform/applications --platform

# Frontend API (the instance's public client-facing API — what clerk-js calls.
# Unauthenticated; --fapi and --platform cannot be combined, --secret-key is ignored)
clerk api --fapi /environment
```

In human mode, `clerk api` with no arguments opens an interactive request builder; in agent mode it prints usage guidance and exits `0` — always pass an endpoint (or `ls`) explicitly from scripts.

For instance config, prefer the dedicated `clerk config ...` commands over raw Platform API `/config` paths. They handle dry-run, diffing, and confirmation more cleanly than the raw endpoint form.

**Always `--dry-run` a mutation before running it for real.** Then re-run without `--dry-run` (add `--yes` if you're sure). In agent mode, interactive confirmation is bypassed, so `--dry-run` is the only safety net for destructive calls.

**JSON bodies must be valid JSON.** The CLI validates and rejects malformed payloads.

**Endpoint paths may be given with or without `/v1/` prefix** - both work for Backend API calls. The CLI normalizes.

See [references/recipes.md](references/recipes.md) for concrete patterns: listing/filtering users, creating orgs, impersonation sessions, etc.

## Inspecting large outputs (do not flood your context)

`users list`, `apps list`, `config pull`, and most `clerk api` GETs return payloads that can be many kilobytes or megabytes. Production tenants commonly have thousands of users; an instance config can be hundreds of fields deep. Reading those responses into the conversation costs context window for no benefit. Save the response to a file first, then query just what you need with `jq`:

```sh
# 1. Persist the response. Use --limit 250 to maximize page size for users list.
clerk users list --json --limit 250 > /tmp/users.json
clerk apps list --json                > /tmp/apps.json
clerk api /users/user_abc123          > /tmp/user.json

# 2. Inspect only what you need.
jq '.data | length'                       /tmp/users.json   # current page size
jq '.hasMore'                             /tmp/users.json   # are more pages available?
jq '.data[0] | keys'                      /tmp/users.json   # discover the user shape once
jq '.data[] | {id, email_addresses}'      /tmp/users.json   # project to a few fields
jq '[.data[] | select(.banned)] | length' /tmp/users.json   # aggregate without reading rows
```

**If `jq` is not available**, fall back to Python or Node - both can stream the file without printing it whole:

```sh
python3 -c 'import json; d=json.load(open("/tmp/users.json")); print(len(d["data"]), d["hasMore"])'
node -e 'const d=require("/tmp/users.json"); console.log(d.data.length, d.hasMore)'
```

`cat` / `head` the file only when you genuinely need to see the raw structure for one-off debugging. When walking pages, write each page to its own file (e.g. `page-${offset}.json`) so individual pages stay independently inspectable.

## Core commands at a glance

| Command                       | Purpose                                                                                                                                                                                                                                                                                                             | Key flags                                                                                                                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `clerk init`                  | Scaffold Clerk into a project. An unauthenticated bootstrap with no `--app`, or an unauthenticated agent run with no `--app` or existing link, writes temporary development keys by default — no login required (see [Accountless setup](#accountless-setup)). `--starter` only supports bootstrap for Next.js, React Router, Astro, Nuxt, TanStack Start, React, Vue, and JavaScript. `--accountless` with `--app`/`--login`, and `--template`/`--fresh` with `--login`, are usage errors before anything is scaffolded. `--template`/`--fresh` on a run that *resolves* to a real app (including while merely signed in) errors only after strategy resolution — so a starter run leaves the scaffolded project behind. | `--framework`, `--pm`, `--name` (with `--starter`), `--app`, `--starter`, `--accountless`, `--login`, `--template`, `--fresh`, `-y`, `--no-skills`                                   |
| `clerk auth login`            | OAuth browser login (stores token). Not required for bootstrap or accountless instance config. Agent mode: no-op if already logged in. With no stored session it still opens a browser and binds a localhost callback, so it is not unattended; prefer `CLERK_PLATFORM_API_KEY` for headless flows. Aliases: `signup`, `signin`, `sign-in`. Top-level shortcut: `clerk login`. | -                                                                                                                                                                                |
| `clerk auth logout`           | Clear stored credentials. Aliases: `signout`, `sign-out`. Top-level shortcut: `clerk logout`.                                                                                                                                                                                                                       | -                                                                                                                                                                                |
| `clerk whoami`                | Print the logged-in email.                                                                                                                                                                                                                                                                                          | -                                                                                                                                                                                |
| `clerk link` / `clerk unlink` | Link this repo to a Clerk app, or remove the link. `unlink` requires `--yes` in agent mode.                                                                                                                                                                                                                         | (see `--help`)                                                                                                                                                                   |
| `clerk env pull`              | Write publishable + secret keys to the framework's env file (merge, not clobber). Resolves `.env.development.local` → framework-preferred file → `.env.local`; override with `--file`.                                                                                                                              | (see `--help`)                                                                                                                                                                   |
| `clerk config {pull,schema}`  | Fetch instance config JSON, or its JSON Schema.                                                                                                                                                                                                                                                                     | (see `--help`)                                                                                                                                                                   |
| `clerk config patch`          | Partial update (PATCH) of instance config. Pass `--destructive` to actually delete sub-resources touched by the patch rather than resetting them to defaults.                                                                                                                                                       | `--app`, `--instance`, `--file`, `--json`, `--dry-run`, `--yes`, `--destructive`                                                                                                 |
| `clerk config put`            | Full replacement (PUT) of instance config. Pass `--destructive` to actually delete removed sub-resources rather than resetting them to defaults.                                                                                                                                                                    | `--app`, `--instance`, `--file`, `--json`, `--dry-run`, `--yes`, `--destructive`                                                                                                 |
| `clerk apps {list,create}`    | List or create Clerk applications. Defaults to JSON in agent mode.                                                                                                                                                                                                                                                  | (see `--help`)                                                                                                                                                                   |
| `clerk users` (no subcommand) | Interactive picker for `users` actions in human mode; in agent mode prints the action list and exits `2`. Always pass an explicit subcommand from agents.                                                                                                                                                           | `--app`, `--instance`, `--secret-key`                                                                                                                                            |
| `clerk users list`            | List users via curated BAPI flags. JSON output (default when piped or in agent mode) is `{data, hasMore}` so callers can paginate without `/users/count`. `--limit` defaults to 100 (max 250).                                                                                                                      | `--limit`, `--offset`, `--query`, `--email-address`, `--phone-number`, `--username`, `--user-id`, `--external-id`, `--order-by`, `--json`, `--app`, `--instance`, `--secret-key` |
| `clerk users create`          | Create a user from curated flags or a raw BAPI body. **No confirmation prompt in any mode** - it writes immediately. `--yes` is accepted but has no effect. `--dry-run` is the only safety net; preview with it first.                                                                                                                                                                                                                            | `--email`, `--phone`, `--username`, `--password`, `--first-name`, `--last-name`, `--external-id`, `-d, --data`, `--file`, `--dry-run`, `--yes`, `--json`                         |
| `clerk users open [user-id]`  | Open a user's dashboard page. Agent mode requires `user-id` and prints a JSON descriptor instead of launching a browser.                                                                                                                                                                                            | (see `--help`)                                                                                                                                                                   |
| `clerk impersonate [user]`    | Sign in as a user for debugging: creates a short-lived actor token and prints the sign-in URL. Alias: `clerk imp`. Requires `clerk auth login` (no `--secret-key`-only bypass) — every token is stamped `cli:<email>` for auditability. `[user]` accepts a `user_...` ID, exact email, or fuzzy search term. On production it bypasses the user's MFA and may count against the impersonation quota — confirm with the user first. | `--print`, `--open`, `--yes`, `--expires-in <seconds>` (default 3600), `--actor <context>`, `--app`, `--instance`                                                                |
| `clerk impersonate revoke <actor-token-id>` | Revoke a pending actor token. The token `id` is printed only at creation (the Backend API has no actor-token list endpoint), so capture it then.                                                                                                                                                      | `--app`, `--instance`                                                                                                                                                            |
| `clerk open [subpath]`        | Open the linked app's dashboard in a browser. Agent mode: prints a JSON descriptor instead of opening.                                                                                                                                                                                                              | (see `--help`)                                                                                                                                                                   |
| `clerk deploy`                | Human-mode production deploy wizard. Agent mode: emits a read-only JSON handoff and tells the agent whether to ask the human to run the wizard, wait for provisioning, finish OAuth, or do nothing.                                                                                                                 | `--mode agent`, `--mode human`, `--verbose`                                                                                                                                      |
| `clerk deploy status`         | Read-only deploy verification. Triggers a DNS check, reports aggregate domain and OAuth readiness, and exits `0` only when complete. Agent mode does one quick check by default; pass `--wait` to keep waiting.                                                                                                     | `--mode agent`, `--wait`, `--verbose`                                                                                                                                            |
| `clerk webhooks listen`       | First-party local webhook tunnel (like `stripe listen`): opens a Svix relay inbox URL and forwards each delivery to your local handler. No auth, no linked project, no Clerk API. Full flow in [references/recipes.md](references/recipes.md#webhooks-local-testing).                                                 | `--forward-to <url>` (required), `--token <c_token>`, `-H, --header <k:v>` (repeatable), `--json` (NDJSON)                                                                       |
| `clerk webhooks token`        | Mint a relay token (`c_` + 10 base62 chars) to pin a stable `listen` inbox URL across machines: `clerk webhooks listen --token "$(clerk webhooks token)" --forward-to ...`.                                                                                                                                          | `--json`                                                                                                                                                                         |
| `clerk webhooks verify`       | Verify a webhook signature offline (pure local HMAC, no auth): from a saved `listen` event line (`--delivery @event.json`) or from the four raw values.                                                                                                                                                             | `--secret <whsec>` (required), `--delivery @file`, `--payload @file`, `--id`, `--timestamp`, `--signature`, `--json`                                                             |
| `clerk enable orgs` / `clerk disable orgs` | Toggle Organizations on the instance. For org features, components, and API usage, see the `clerk-orgs` skill.                                                                                                                                                                                         | `--force-selection`, `--auto-create`, `--max-members <n>`, `--domains`, `--dry-run`, `--yes`, `--app`, `--instance`                                                              |
| `clerk enable billing` / `clerk disable billing` | Toggle billing for users and/or orgs (defaults to both). For plans, pricing components, and entitlements, see the `clerk-billing` skill.                                                                                                                                                         | `--for <orgs\|users>`, `--dry-run`, `--yes`, `--no-skills` (enable only), `--app`, `--instance`                                                                                  |
| `clerk doctor`                | Health check (CLI version, login, link, env, config, completion; plus host-execution probe in agent mode).                                                                                                                                                                                                          | `--json`, `--spotlight`, `--verbose`, `--fix`                                                                                                                                    |
| `clerk api [path]`            | Authenticated HTTP to Backend/Platform API.                                                                                                                                                                                                                                                                         | `-X`, `-d`, `--file`, `--dry-run`, `--yes`, `--include`, `--app`, `--secret-key`, `--instance`, `--platform`                                                                     |
| `clerk api ls [filter]`       | Discover endpoints from the bundled OpenAPI catalog.                                                                                                                                                                                                                                                                | (see `--help`)                                                                                                                                                                   |
| `clerk completion [shell]`    | Print a shell completion script (`bash`, `zsh`, `fish`, `powershell`).                                                                                                                                                                                                                                              | -                                                                                                                                                                                |
| `clerk update`                | Update the CLI to the latest version.                                                                                                                                                                                                                                                                               | `--channel`, `-y`, `--all`                                                                                                                                                       |

**`clerk <command> --help` is the source of truth for flags.** This table is a hint, not a spec. Before running an unfamiliar command or flag combination, run `clerk <command> --help` once per session. Every command also defines `setExamples([...])` in source, which `--help` renders as a copy-pasteable Examples block, so you rarely need to guess syntax.

## Agent-mode behavior (important)

The CLI auto-detects agent mode when stdout is not a TTY, or when `--mode agent` / `CLERK_MODE=agent` is set. In agent mode:

- **Interactive prompts are disabled.** Commands that would normally show pickers (`link` without `--app`, `unlink` without `--yes`, `users` without a subcommand) either auto-resolve or exit with a usage error. `clerk api` with no args prints usage guidance and exits 0; pass an endpoint (or `ls`) explicitly. Always pass explicit flags (`--app`, `--yes`) in scripted calls.
- **Host-sensitive operations emit a sandbox warning once per invocation.** Home-directory Clerk state, keychain access, networked Clerk calls, browser launch, and localhost OAuth callback setup can trigger the warning shown above. If it appears, rerun the same command on the host before trusting the result.
- **If your harness does not clearly present as agent mode, force it.** Use `--mode agent` or `CLERK_MODE=agent` when you want the CLI's non-interactive behavior and sandbox warning path to apply deterministically.
- **`link` supports deterministic agent flows.** In agent mode, `clerk link --app <id>` links directly. Without `--app`, the CLI will try silent key-based autolink first; if it cannot determine the app unambiguously, it exits and tells you to pass `--app`.
- **For `init`, follow `clerk-setup`.** It owns framework-support, accountless, app-linking, migration, and login-order guidance so setup instructions have one source of truth.
- **`--fresh` is destructive.** It replaces the temporary app and overwrites the env keys and `.clerk/keyless.json` breadcrumb with no prompt, orphaning the previous app and its users. Never pass it just to re-run `init`.
- **`unlink` requires `--yes` in agent mode.** It gates on `isAgent() && !options.yes` and exits with a usage error without it. This is the exception, not the pattern - see the next bullet.
- **Only `unlink` actually requires `--yes`.** Every other confirmation gate is written as `isHuman() && !options.yes`, so agent mode skips it outright: the mutation executes with no prompt and no error. Passing `--yes` is harmless but changes nothing. Do not treat it as a safety gate - `--dry-run` is the real one.
- **`impersonate` requires the `[user]` positional in agent mode.** If a search term matches multiple users, it exits `2` listing candidate user IDs — retry with a specific `user_...` ID. Output is a JSON object (`{url, id, userId, actor, ...}`); surface `url` to the user and capture `id` — it is the only chance to record the revoke handle.
- **`webhooks listen` is long-running.** Run it in the background. In agent mode (or with `--json`) it emits NDJSON: one `ready` line (`{type:"ready", relay_url, forward_to}`), then one `event` line per delivery — each event line can be fed back to `clerk webhooks verify --delivery`.
- **`doctor --fix` is ignored.** Parse `doctor --json` output's `remedy` field and act on it yourself.
- **`apps list` and `apps create` default to JSON** when piped.
- **`users` defaults to JSON when piped, like `apps`.** `clerk users list` and `clerk users create` emit JSON in agent mode. Bare `clerk users` (no subcommand) is a usage error in agent mode - pass `list`, `create`, or `open` explicitly. `clerk users open` requires the `user-id` positional in agent mode and prints a JSON descriptor instead of launching a browser.
- **`deploy` has an agent handoff plus a verification gate.** In agent mode, bare `clerk deploy` is read-only and emits a JSON handoff. It never drives the interactive wizard. Do not tell Claude or another agent to run `! clerk deploy`, because the wizard needs interactive stdin prompts. Ask the human to run `clerk deploy` in a new terminal window when needed, then run `clerk deploy status --mode agent` to verify completion. See [references/agent-mode.md](references/agent-mode.md#deploy-handoff-and-verification).
- **`--input-json <json|@file|->`** expands JSON into flags on any command (e.g. `clerk init --input-json '{"framework":"next","yes":true}'`). Stdin needs the explicit `-` marker (`echo '{"yes":true}' | clerk init --input-json -`); bare piped stdin is **not** auto-detected, so shell loops and self-reading commands (`cat body.json | clerk api …`) are untouched. Place `--input-json` after the leaf subcommand. Full rules in [references/agent-mode.md](references/agent-mode.md#passing-options-as-json---input-json).

Full matrix and sandbox details in [references/agent-mode.md](references/agent-mode.md).

## Output format and errors

- **JSON output:** `--json` on `apps list` and `doctor`. For `clerk api`, the response body is the raw API JSON, so pipe into `jq` freely.
- **Exit codes:** `0` success, `1` runtime error, `2` usage/validation error. `doctor` returns `1` if any check failed.
- **Error format:** User-facing errors print a single line to stderr and set a non-zero exit code. Use `--verbose` for stack traces when debugging.

## Safety rules for autonomous use

1. **Discover before acting:** `clerk api ls <keyword>` before `clerk api <path>`.
2. **Preview mutations:** `--dry-run` on every `config patch`, `config put`, `api -X POST/PATCH/PUT/DELETE`.
3. **Target explicitly in production:** pass `--instance prod` rather than relying on defaults, and confirm with the user before any production mutation.
4. **Never commit secrets:** `env pull` writes to `.env.local` (which should be gitignored). Don't paste secret keys into code or chat.
5. **Use `doctor --json`** to diagnose before assuming the CLI is broken.

## References

- [references/auth.md](references/auth.md) - auth flow, key resolution order, host-vs-sandbox behavior, `--app`/`--instance` targeting, Backend vs Platform API.
- [references/recipes.md](references/recipes.md) - copy-pasteable recipes for common Clerk tasks.
- [references/agent-mode.md](references/agent-mode.md) - agent-mode behavior matrix, sandbox warning semantics, exit codes, error format.
