# InsForge CLI Local Instances

`npx -y @insforge/cli local` runs an InsForge backend in Docker on the user's own
machine — Postgres, PostgREST, the backend, and the edge-functions runtime.

## When to use this

Only when the user explicitly asks for a backend on their own machine: "run
InsForge locally", "I want it in Docker", "run it in a container here".

"No account" on its own is a constraint, not a request for Docker — ask what they
want rather than starting containers on it.

Not for offline work on its own. The first start in a directory fetches the setup
script and pulls images, so it needs network; only later starts of an instance
that already exists run offline.

A cloud project is the default for everything else.

## Commands

- `npx -y @insforge/cli local start` - start the stack, wait for health, link this
  directory, seed `.env.local`. Flags: `--storage <local|minio|rustfs>`, `--pull`,
  `--port-app <n>` (and `--port-auth`, `--port-deno`, `--port-postgres`,
  `--port-postgrest`).
- `npx -y @insforge/cli local status [--show-keys] [--json]` - health, ports,
  backend version, per-container state. Keys are masked unless `--show-keys`.
- `npx -y @insforge/cli local stop [--delete-data] [--unlink]` - stop the stack.

`--json` is a global option, not one of these commands' flags — it works on all
three.

After `local start` the directory is linked, so project-scoped commands — `db`,
`storage`, `functions`, `secrets`, `schedules`, `logs`, `metadata` — target the
local backend with no login.

Platform commands still reach InsForge Cloud and still need an account:
`whoami`, `list`, `orgs`, `billing`, `usage`, `create`. A linked local instance
does not change what those talk to.

## Credentials

`.env.local` gets the API URL and the **anon** key only — safe to hand to browser
code, and what the app should read.

`local start --json` is different: it returns the API key, the admin password, and
a `databaseUrl` carrying the Postgres password. Live credentials for a running
backend. Read them into variables when scripting; do not echo the payload into CI
output, logs, or a file under version control. `local status --json` withholds all
of it unless `--show-keys` is passed, so that one is safe to paste.

## Destructive

`local stop --delete-data` removes the volumes — database, storage objects, and
logs — and is classified `critical` by the human-in-the-loop guard. Confirm intent
before running it. A plain `local stop` keeps the data and never prompts.

## What it runs

The first start fetches `deploy/setup.sh` from the InsForge repository and runs it
into `.insforge/checkout/`, then runs the compose file that script wrote — the
same one self-hosting uses. The CLI adds one overlay: the telemetry stamp, and
loopback binding for the published ports.

`.insforge/checkout/.env` holds the generated secrets. `local start` writes
`.insforge/.gitignore` covering `checkout/`, so `git add -A` cannot commit them —
but nothing stops a command from printing the file, so do not cat it into output
you keep. If it goes missing while
volumes still exist, `local start` refuses instead of generating new ones —
Postgres reads its password only at cluster creation, so fresh secrets would leave
the database unreachable. Restore the file, or `local stop --delete-data`.

## One instance per directory

The compose project name carries a hash of the directory path, so two folders get
separate containers, volumes, and databases — including two that share a name.

The first instance on a machine gets ports 7130 / 7131 / 7133 / 5432 / 5430. When
those are taken the whole block shifts by ten, and `start` prints what moved. A
port passed with `--port-*`, or one the directory already used, never moves.

## Requirements

Docker with Compose 2.24.4 or newer, and roughly 1.5 GB available to the daemon.
Any Docker-compatible runtime works. Without Docker, `create` gives the user a
hosted project instead — offer it, but do not switch to it on your own.

## Common Mistakes

**Using `local` as a fallback when authentication is inconvenient.** A local
instance is a different backend with different data, so starting one to work
around a login problem silently moves the user off the project they meant to use.
When `login` fails or no browser is available, use `login --user-api-key` or
`login --device`. Not `create` — it calls the platform API and needs the same
authentication that just failed.

**Pointing a server deployment at `local start`.** See below.

**Assuming a fresh start works offline.** The first start fetches the setup script
and pulls images.

## Self-hosting is not this

`local start` is a development backend: loopback ports, `:latest` images, one
instance per directory. Deploying InsForge to a server is `deploy/setup.sh`
directly — see the InsForge repository's deployment docs. Do not point a user
setting up a server at `local start`.
