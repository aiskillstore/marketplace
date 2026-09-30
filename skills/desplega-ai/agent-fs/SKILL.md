---
name: agent-fs
description: >-
  Use when the user wants to store, retrieve, search, or manage files in agent-fs —
  an agent-first filesystem backed by S3. Triggers on: "save this to agent-fs",
  "find that file", "store this document", "search agent-fs", "list my files",
  "show version history", "revert file", "set up agent-fs", "get a signed url",
  "share this file", "manage members", "invite user", "list members", "remove member",
  "update role", "reset api key", "rotate api key", "lost my api key", file
  persistence for agents, shared agent filesystem, or any
  mention of the agent-fs CLI. Also use when the user needs to manage drives,
  manage org/drive members, generate presigned URLs, check recent activity, or use
  semantic search across stored files. Also use when the user wants to run SQL
  over stored data files ("query this csv", "sql over my files", "duckdb",
  "aggregate the parquet file", "query the sqlite db", "join these spreadsheets").
  Also use when the user wants to mount or
  unmount agent-fs as a Linux FUSE filesystem ("mount agent-fs", "fuse mount",
  "fuse", "remote mount", "sandbox mount", "expose drives as files",
  "use cat/grep/mv on my agent-fs files", "umount the drive", "mount a remote
  drive", "mount from sprite", "mount from e2b", "mount from hetzner"). Also use
  when the user wants to use agent-fs as a just-bash filesystem. Also use when the
  user wants to set up agent-fs without Docker or S3 ("local filesystem backend",
  "filesystem storage", "no docker", "onboard --filesystem", "store files on disk").
  If the user
  mentions agent-fs in any context, always consult this skill.
---

# agent-fs CLI

agent-fs is an agent-first filesystem with full versioning, full-text search (FTS5), and semantic search. It provides a CLI that outputs JSON, making it ideal for agent workflows. Files are organized in drives within orgs.

## Storage Backends

agent-fs stores file bytes in a pluggable storage backend. The durable value — version history, comments, and search — lives in SQLite and works identically on every backend.

| Backend | Setup | Versioning tier | `signed-url` |
|---------|-------|-----------------|--------------|
| **S3 / MinIO** (default) | `agent-fs onboard -y` (local MinIO, needs Docker) or `--s3-*` flags for AWS/R2/etc. | Full — `revert` + historical `diff` via S3 object versioning | Real presigned URL (public, time-limited) |
| **Local filesystem** | `agent-fs onboard --filesystem` (no Docker, no S3) | Full — `revert` + historical `diff` via content-addressed blobs on disk | Falls back to an authenticated in-app link (requires sign-in; does not expire) |

Both backends are **full-tier**: every op — including `revert` and historical `diff` — works. Future backends may be **basic-tier** (no object versioning): on those, `revert` and historical `diff` are unavailable and fail cleanly with an `UNSUPPORTED_OPERATION` error (HTTP 422) rather than a raw storage error — current content, listing, comments, and search keep working. Check a backend's capabilities before relying on versioning if you're unsure which backend a drive uses.

## Quick Start

```bash
# 1. Set up (local MinIO — requires Docker)
agent-fs onboard -y

#    ...or with no Docker/S3 at all — store bytes on the local filesystem:
agent-fs onboard --filesystem            # uses ~/.agent-fs/storage
agent-fs onboard --filesystem --storage-root /data/agent-fs   # custom dir

# 2. Optionally start the daemon (CLI auto-detects and works without it)
agent-fs daemon start

# 3. Start using it
echo "hello world" | agent-fs write docs/readme.txt -m "initial version"
agent-fs cat docs/readme.txt
```

For custom S3 (AWS, R2, etc.), use flags: `agent-fs onboard --s3-endpoint <url> --s3-bucket <name> --s3-access-key <key> --s3-secret-key <key>`.

The local-filesystem backend (`--filesystem`, equivalently `--storage local`) needs no Docker and no S3 — bytes are stored under `--storage-root` (default `~/.agent-fs/storage`), with every version content-addressed so `revert` and historical `diff` work the same as on S3.

## just-bash Adapter

Use `@desplega.ai/agent-fs-just-bash` when a `just-bash` environment needs to
read and write through agent-fs as its `fs` implementation.

```ts
import { Bash } from "just-bash";
import { AgentFsFileSystem } from "@desplega.ai/agent-fs-just-bash";

const fs = new AgentFsFileSystem({
  baseUrl: process.env.AGENT_FS_API_URL,
  apiKey: process.env.AGENT_FS_API_KEY,
  orgId: "org_...",
  driveId: "drive_...",
});

const bash = new Bash({ fs, cwd: "/" });
```

The adapter uses `/raw` for byte-safe reads/writes and `/ops` for listing and
metadata. Empty directories are represented by a hidden `.agent-fs-dir` marker;
symlinks are unsupported and throw `EPERM`.

## Essential Patterns

1. **Use JSON for machine output** — pass `--json` when parsing CLI output (except `download` without `-o`, which writes raw bytes to stdout; `daemon status` and `auth register` print human-readable text).

2. **Auto-detection** — the CLI automatically detects whether the daemon is running. If it is, commands go via HTTP; otherwise, they use embedded mode directly. No user action needed.

3. **Default org/drive resolution** — with no `--org`/`--drive` flag, the CLI resolves in order: the flag itself, then local config (`org switch <id>` / `drive switch <id>`, sticky per machine), then the `AGENT_FS_DEFAULT_ORG_ID` / `AGENT_FS_DEFAULT_DRIVE_ID` env vars (a deployment-level hint, e.g. the shared org an agent-swarm worker container is provisioned to write to), then the account's own default org/drive from `GET /me` (the auto-created personal org, unless changed). Check `agent-fs org current` / `agent-fs drive current` (`source` field) if a write lands somewhere unexpected — a write with no flags always lands on the personal org/drive unless one of the earlier tiers is set.

4. **Stdin and file upload** — `write` accepts raw bytes from stdin or `--file`, and text from `--content`; `append` accepts text via stdin or `--content`:
   ```bash
   # Preferred for multi-line text
   echo "content here" | agent-fs write path/to/file.txt

   # Inline for short content
   agent-fs write path/to/file.txt --content "short text"

   # Binary-safe upload
   agent-fs write assets/screenshot.png --file ./screenshot.png
   ```

5. **Paths** — forward-slash separated, no leading slash required. Example: `docs/notes/meeting.md`

6. **Version messages** — optional but recommended for auditability:
   ```bash
   agent-fs write docs/spec.md --content "..." -m "added API section"
   ```

7. **Optimistic concurrency** — use `--expected-version` on `write` to prevent conflicts:
   ```bash
   agent-fs write config.json --content '{}' --expected-version 3
   # Fails if file is not at version 3
   ```

## Command Quick Reference

### File Operations

| Command | Usage | Description |
|---------|-------|-------------|
| `write` | `agent-fs write <path> [--content <text>] [--file <local-path>] [-m <msg>] [--expected-version <n>]` | Write text or binary bytes |
| `cat` | `agent-fs cat <path> [--offset <n>] [--limit <n>] [--raw]` | Read text file content |
| `edit` | `agent-fs edit <path> --old <text> --new <text> [-m <msg>]` | Find-and-replace in file |
| `append` | `agent-fs append <path> [--content <text>] [-m <msg>]` | Append to file (stdin or --content) |
| `tail` | `agent-fs tail <path> [--lines <n>]` | Last N lines (default: 20) |
| `ls` | `agent-fs ls [path]` | List directory contents (defaults to /) |
| `stat` | `agent-fs stat <path>` | Show file metadata (size, version, timestamps) |
| `tree` | `agent-fs tree [path] [--depth <n>]` | Recursive directory listing |
| `glob` | `agent-fs glob <pattern> [--path <prefix>]` | Find files by pattern (`*.md`, `**/*.md`) across all storage pages |
| `rm` | `agent-fs rm <path>` | Delete a file |
| `mv` | `agent-fs mv <from> <to> [-m <msg>]` | Move or rename a file |
| `cp` | `agent-fs cp <from> <to>` | Copy a file |
| `signed-url` | `agent-fs signed-url <path> [--expires-in <seconds>] [--inline]` | Generate a download URL. On S3/MinIO: a presigned URL (default 24h, max 7 days, `kind: "presigned"`). On local-FS: an authenticated in-app link (`kind: "app"`, requires sign-in, non-expiring). By default the URL forces a download; `--inline` makes the browser render the file instead (PDF, image). |
| `download` | `agent-fs download <path> [-o <local-path>]` | Download raw bytes |

`cat` is a paginated viewer, not a raw file reader: without `--limit`, it defaults to the first 200 lines at a TTY, but returns the **whole file** when stdout is piped or redirected (a pipe/redirect almost always means "give me everything"). Any time `cat` returns fewer lines than requested, a `truncated: showing N of M lines (use --limit)` note goes to **stderr** — never stdout, so it never corrupts piped/redirected output. The default (non-`--raw`, TTY) view also prefixes each line with a line number for readability; that prefix is **not** part of the stored bytes. For a complete, byte-exact read — required before parsing as CSV/JSON, or any time line numbers or a partial read would corrupt the data — use `agent-fs cat <path> --raw` or, better, `agent-fs download <path> -o <file>`.

### Versioning

| Command | Usage | Description |
|---------|-------|-------------|
| `log` | `agent-fs log <path> [--limit <n>]` | Show version history |
| `diff` | `agent-fs diff <path> --v1 <n> --v2 <n>` | Diff between versions |
| `revert` | `agent-fs revert <path> --version <n>` | Revert to a previous version |

`log` works on every backend (version metadata is in SQLite). `revert` and historical `diff` (comparing two stored versions) need a **full-tier** backend — S3/MinIO and local-filesystem both qualify. On a basic-tier backend without object versioning, `revert` and historical `diff` fail cleanly with `UNSUPPORTED_OPERATION` (HTTP 422); `diff` then degrades to the stored summary instead of full content.

### Search & Discovery

| Command | Usage | Description |
|---------|-------|-------------|
| `grep` | `agent-fs grep <pattern> <path>` | Regex search in file content |
| `fts` | `agent-fs fts <pattern> [--path <prefix>]` | Full-text search with FTS5 query syntax in the active drive |
| `search` | `agent-fs search <query> [--limit <n>]` | Hybrid search (semantic + keyword, best for general queries) |
| `vec-search` | `agent-fs vec-search <query> [--limit <n>]` | Semantic search over distinct files in the active drive |
| `recent` | `agent-fs recent [path] [--since <duration>] [--limit <n>]` | Recent activity (e.g., `--since 24h`) |
| `reindex` | `agent-fs reindex [path]` | Re-index files with failed/missing embeddings |

**When to use which:**
- `grep` — you know the exact pattern and path (regex)
- `fts` — keyword search across all files (fast, FTS5-based)
- `search` — general-purpose search combining keywords and meaning (recommended default)
- `vec-search` — pure semantic search when you want conceptual matches only

Search uses the active organization and drive. Check `org current` and `drive current`, or pass explicit `--org` and `--drive` flags.
`glob`, `ls`, and `tree` read every S3 listing page. A drive with more than 1,000 objects remains searchable.
`search` and `vec-search` select semantic candidates within the active drive and count distinct files toward the limit.
Semantic results require embeddings. `vec-search` returns a hint when no provider exists, and `search` identifies keyword-only results.

`fts` accepts raw FTS5 syntax. Quote punctuation-bearing terms with FTS double quotes inside shell single quotes:

```bash
agent-fs glob '**/*ai-tinkerers*'
agent-fs glob '**/*ai-tinkerers*' --path thoughts/research
agent-fs fts '"ai-tinkerers"'
agent-fs fts 'ai AND tinkerers'
```

Double an embedded quote inside an FTS quoted term. Backslash escaping does not escape an FTS quote.
Filename patterns are case-sensitive. Full-text matches indexed tokens, so neither mode corrects spelling errors.

### SQL Queries (DuckDB)

| Command | Usage | Description |
|---------|-------|-------------|
| `sql` | `agent-fs sql <query> [-t name=path[:format]]... [--max-rows <n>]` | Run DuckDB SQL over stored documents |

Supported formats: csv, tsv, parquet, xlsx, json, ndjson/jsonl (each also `.gz` except parquet/xlsx), sqlite (`.db`/`.sqlite`/`.sqlite3`), and `.duckdb`. Reference file-format documents directly by quoted drive path inside the query, or bind any document to a table name with `-t`. SQLite/DuckDB databases require a `-t` binding and expose their tables as `<name>.<table>`. Append `:format` to a binding to query documents with non-standard extensions (e.g. `-t logs=/raw/data.txt:csv`). Queries are sandboxed — no host filesystem or network access. Results cap at `--max-rows` (default 1000, max 10000); `truncated: true` in JSON output signals more rows exist.

### Comments

| Command | Usage | Description |
|---------|-------|-------------|
| `comment add` | `agent-fs comment add <path> --body <text> [--line-start <n>] [--line-end <n>]` | Add a comment to a file |
| `comment reply` | `agent-fs comment reply <comment-id> --body <text>` | Reply to a comment |
| `comment list` | `agent-fs comment list [path]` | List comments (with inline replies) |
| `comment get` | `agent-fs comment get <id>` | Get a comment with its replies |
| `comment update` | `agent-fs comment update <id> --body <text>` | Update a comment (author only) |
| `comment delete` | `agent-fs comment delete <id>` | Soft-delete a comment (author only) |
| `comment resolve` | `agent-fs comment resolve <id>` | Resolve a comment |
| `comment notifications` | `agent-fs comment notifications [--unread] [--limit <n>]` | List comment notifications for the current user in the active drive |
| `comment read` | `agent-fs comment read [ids...] [--all]` | Mark selected notification event IDs, or all active-drive notifications, as read |

### Setup & Auth

| Command | Usage | Description |
|---------|-------|-------------|
| `onboard` | `agent-fs onboard [--local] [--filesystem] [--storage <minio\|local>] [--storage-root <dir>] [-y] [--embeddings <provider>]` | Set up agent-fs (storage backend + database + user). `--filesystem` (or `--storage local`) uses an on-disk backend — no Docker/S3; `--storage-root <dir>` sets its directory. |
| `init` | `agent-fs init [--local] [-y]` | Alias for `onboard` |
| `auth register` | `agent-fs auth register <email>` | Register a new user |
| `auth whoami` | `agent-fs auth whoami` | Show current user info |
| `auth reset-key` | `agent-fs auth reset-key` | Reset your own API key. The old key stops working immediately. |

### Member Management

| Command | Usage | Description |
|---------|-------|-------------|
| `member list` | `agent-fs member list` | List org members (use `--drive <id>` for drive members) |
| `member invite` | `agent-fs member invite <email> --role <role>` | Invite user to org (viewer/editor/admin) |
| `member update-role` | `agent-fs member update-role <email> --role <role>` | Update org role (use `--drive <id>` for drive role) |
| `member remove` | `agent-fs member remove <email>` | Remove from org (use `--drive <id>` for drive only) |
| `member reset-key` | `agent-fs member reset-key <email>` | Reset a member's API key (org admin only). The old key stops working immediately. |

The `--drive` flag is a global option — place it before the subcommand: `agent-fs --drive <id> member list`.

Member commands are admin-gated: org-scoped commands require org `admin`; drive-scoped commands (`--drive <id>`) require drive `admin` or admin of the owning org, and the drive must belong to the current org. Non-admins get a permission error; org/drive IDs outside your memberships return "not found".

### Drive Management

| Command | Usage | Description |
|---------|-------|-------------|
| `drive list` | `agent-fs drive list` | List drives in current org |
| `drive create` | `agent-fs drive create <name>` | Create a new drive (requires org admin) |
| `drive current` | `agent-fs drive current` | Show current drive context |
| `drive invite` | `agent-fs drive invite <email> --role <role>` | Invite user (viewer/editor/admin) |

Drive membership is explicit: `drive list` shows only drives you're a member of. Creating a drive automatically grants you admin membership on it; other users must be invited per drive (or via org invite, which grants access to the default drive).

### Config & Daemon

| Command | Usage | Description |
|---------|-------|-------------|
| `config get` | `agent-fs config get <key>` | Get config value (dot notation: `s3.bucket`) |
| `config set` | `agent-fs config set <key> <value>` | Set config value |
| `config list` | `agent-fs config list` | Show all configuration |
| `config validate` | `agent-fs config validate` | Check S3, database, auth, embeddings health |
| `daemon start` | `agent-fs daemon start` | Start the background daemon |
| `daemon stop` | `agent-fs daemon stop` | Stop the daemon |
| `daemon status` | `agent-fs daemon status` | Check if daemon is running |

### FUSE Mount (Linux only)

Expose all org drives as a Linux FUSE filesystem so agents can use plain shell verbs (`cat`, `grep`, `mv`, `rm`) against agent-fs content. Requires `/dev/fuse` and `SYS_ADMIN` cap; not available on macOS or in gVisor-based sandboxes.

Two topologies are supported:
- **Local mode** (default): helper talks to a local daemon over a Unix socket. Daemon must be running and have an S3 backend configured.
- **Remote mode** (`--remote`): helper talks directly to a remote agent-fs HTTP API. No local daemon required — ideal for sandboxes (sprite, E2B, Hetzner VMs, GitHub Actions runners) that can reach a hosted agent-fs but can't run the full daemon stack.

FUSE writes require the `editor` role or better on the drive — on drives where you're a `viewer`, the mount is read-only for file writes (writes fail with `EACCES`; check `<mount>/.agent-fs/errors.ndjson` for the `PERMISSION_DENIED` record).

| Command | Usage | Description |
|---------|-------|-------------|
| `mount` | `agent-fs mount <path> [--allow-other] [--foreground]` | Mount drives at `<path>` via local daemon (e.g. `/mnt/agent-fs/<drive>/`). |
| `mount --remote` | `agent-fs mount <path> --remote [--api-url <url>] [--api-key <key>]` | Mount against a remote agent-fs HTTP API. Reads `apiUrl`/`apiKey` from `~/.agent-fs/config.json` or `AGENT_FS_API_URL`/`AGENT_FS_API_KEY` env if flags omitted. Prefer env over `--api-key` (the latter exposes the key in `ps`). |
| `umount` | `agent-fs umount <path>` | Unmount the FUSE mountpoint. |
| `mount status` | `agent-fs mount status` | Show whether a mount is active and where. |

## Common Workflows

### Store and retrieve a document

```bash
# Write a document (multi-line via stdin)
cat <<'EOF' | agent-fs write reports/q1-summary.md -m "Q1 summary draft"
# Q1 Summary
Revenue grew 15% quarter over quarter.
EOF

# Read it back
agent-fs cat reports/q1-summary.md

# Check metadata
agent-fs stat reports/q1-summary.md
```

### Search across files

```bash
# Regex search within a specific path
agent-fs grep "revenue|growth" reports/

# Full-text search across all files (FTS5 — fast keyword matching)
agent-fs fts "quarterly revenue"

# Hybrid search (combines keyword + semantic matching — recommended default)
agent-fs search "financial performance metrics" --limit 5

# Vector-only semantic search (conceptual matches only)
agent-fs vec-search "financial performance metrics" --limit 5
```

### Query data files with SQL

```bash
# Query a CSV directly by path
agent-fs sql "SELECT category, sum(amount) AS total FROM '/finance/2026.csv' GROUP BY category" --json

# Join documents of different formats
agent-fs sql "SELECT s.name, t.tag FROM sales s JOIN tags t ON s.id = t.id" \
  -t sales=/data/sales.csv -t tags=/data/tags.parquet

# Query a stored SQLite database (tables exposed as app.<table>)
agent-fs sql "SELECT count(*) FROM app.users" -t app=/backups/app.db

# Pipe a query via stdin
echo "SELECT count(*) FROM '/data/events.ndjson'" | agent-fs sql
```

### Review and revert changes

```bash
# View version history
agent-fs log docs/spec.md --limit 10

# Compare two versions
agent-fs diff docs/spec.md --v1 2 --v2 5

# Revert to version 2
agent-fs revert docs/spec.md --version 2
```

### Comments and collaboration

```bash
# Add a comment to a file
agent-fs comment add docs/spec.md --body "Needs more detail on auth"

# Reply to a comment
agent-fs comment reply <comment-id> --body "Added in v3"

# List comments
agent-fs comment list docs/spec.md

# Check unread notifications (the returned IDs are notification event IDs)
agent-fs comment notifications --unread --limit 20

# Mark selected notifications as read
agent-fs comment read <notification-id> [<notification-id>...]

# Or acknowledge every notification in the active drive
agent-fs comment read --all

# Resolve a comment
agent-fs comment resolve <comment-id>
```

### Set up a new drive and invite users

```bash
# Create a shared drive
agent-fs drive create "team-docs"

# Invite a teammate
agent-fs drive invite alice@company.com --role editor

# Check current drive context
agent-fs drive current
```

### Manage members

```bash
# List org members
agent-fs member list

# List drive members
agent-fs --drive <driveId> member list

# Invite a user
agent-fs member invite alice@company.com --role editor

# Change role
agent-fs member update-role alice@company.com --role admin

# Remove from org (cascades to all drives)
agent-fs member remove alice@company.com

# Remove from a specific drive only (keeps org membership)
agent-fs --drive <driveId> member remove alice@company.com
```

### Check recent activity

```bash
# What changed in the last hour?
agent-fs recent --since 1h

# Recent changes under a specific path
agent-fs recent docs/ --since 24h --limit 20
```

### Generate a shareable download link

```bash
# Default expiry (24 hours)
agent-fs signed-url docs/report.pdf

# Custom expiry (1 hour)
agent-fs signed-url docs/report.pdf --expires-in 3600

# Render in the browser instead of downloading (PDF viewer, image tab)
agent-fs signed-url docs/report.pdf --inline

# JSON output (useful for agents)
agent-fs signed-url docs/report.pdf --json
# → { "url": "https://...", "path": "/docs/report.pdf", "expiresIn": 86400, "expiresAt": "2026-03-20T..." }
```

On an S3/MinIO backend (`kind: "presigned"`) the URL requires no authentication — anyone with the link can download the file until it expires. Access is RBAC-checked only at generation time (viewer-or-better on the drive); after that the URL is a bearer secret. Don't log it or paste it anywhere you wouldn't paste a credential, and prefer the shortest workable `--expires-in`. Signed URLs serve the correct `Content-Type` header based on file extension (e.g., `application/pdf` for `.pdf`, `image/png` for `.png`). By default they also carry `Content-Disposition: attachment`, so opening the link saves the file under its real name. Pass `--inline` (API: `"disposition": "inline"`) when the link will be embedded or opened for viewing, such as a PDF in an `<iframe>`; `<img>` tags ignore the disposition either way.

On a backend without presigned URLs (the local-filesystem backend), `signed-url` does **not** fail — it falls back to an authenticated in-app link (`kind: "app"`, `expiresIn: 0`) of the form `<appUrl>/file/~/<org>/<drive>/<path>`. Unlike a presigned URL this link is **not** a public bearer secret: the daemon's `/raw` route and the web viewer require sign-in, so the recipient must be an authenticated member of the drive. Set `AGENT_FS_APP_URL` (or `appUrl` in config) so the link points at your deployment.

**MIME types on upload:** `write`, `edit`, `append`, and `revert` automatically detect and set the correct `Content-Type` on S3 objects based on file extension. The content type is also stored in the database and visible in `stat` output via the `contentType` field. Raw stdin and `--file` uploads preserve bytes exactly; text search/indexing is applied only when the payload is valid, indexable UTF-8 text.

### App URL in responses

When `AGENT_FS_APP_URL` is set (e.g., `https://live.agent-fs.dev`), file-related ops automatically include an `appUrl` field pointing to the file in the live web app:

```bash
AGENT_FS_APP_URL=https://live.agent-fs.dev agent-fs stat docs/report.pdf --json
# → { ..., "appUrl": "https://live.agent-fs.dev/file/~/org-id/drive-id/docs/report.pdf" }
```

This applies to any op that returns a `path` or `to` field (write, stat, edit, append, rm, cp, mv, signed-url, etc.).

### Validate your setup

```bash
agent-fs config validate
```

### Mount a remote drive from a sandbox

Use `--remote` when the agent is running in a Linux sandbox (sprite, E2B, Hetzner VM, GitHub Actions runner, etc.) that can reach a hosted agent-fs HTTP API but cannot run the full daemon + S3 stack locally.

```bash
# Linux prereqs (run once per sandbox)
sudo apt-get install -y fuse3
sudo chmod 666 /dev/fuse
sudo ln -sf /proc/mounts /etc/mtab
echo user_allow_other | sudo tee -a /etc/fuse.conf

# Auth — either env vars or ~/.agent-fs/config.json
export AGENT_FS_API_URL=https://agent-fs.example.com
export AGENT_FS_API_KEY=<key>

# Mount — no local daemon needed
mkdir -p ~/mnt
agent-fs mount ~/mnt --remote

# Use plain shell verbs against remote content
ls ~/mnt
cat ~/mnt/current/docs/spec.md
echo "edit from sandbox $(date)" > ~/mnt/current/notes.txt

# Unmount
fusermount3 -u ~/mnt
```

See `docs/mounting/` for per-environment guides (sprite, E2B, Hetzner).

### Upload limit configuration

Raw HTTP uploads default to 50 MiB. Set `AGENT_FS_MAX_UPLOAD_BYTES` on the server
(e.g. `104857600` for 100 MiB) and restart the daemon to change the limit. Invalid
values fall back to 50 MiB. The web UI discovers the limit from `/health`.
JSON/MCP `write` stays at 10 MiB. FUSE retains a 64 MiB encoded IPC frame ceiling
including protocol overhead; use HTTP raw uploads for larger files.

## Own profile

`agent-fs profile get` reads your profile. `agent-fs profile set --name "Taras"`
sets your display name. Names are trimmed, 1–100 characters, and shown to anyone
who can read your comments. Only your authenticated profile can be edited.
HTTP: `GET /auth/profile`, `PATCH /auth/profile` with `{ "displayName": "Taras" }`
(or `null` to clear). MCP: `profile-get`, `profile-set` with `displayName`.
The web account menu has **Edit profile**. Comment responses include
`authorDisplayName` when set; emails and member roles remain admin-only.
