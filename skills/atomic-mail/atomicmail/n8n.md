# Atomic Mail on n8n

Install the community node `@atomicmail/n8n-nodes-atomicmail` to give n8n workflows a real `@atomicmail.ai` inbox via JMAP.

## Install

### From npm (after publish)

In n8n **Settings → Community nodes**, install:

```text
@atomicmail/n8n-nodes-atomicmail
```

### From this monorepo

```bash
npm run build:n8n
cd integrations/n8n/atomicmail
npm install
npm run build
```

Copy or link the package into your n8n custom extensions path, or run `npm run dev` for local development.

### Local Docker demo (video / QA)

Use the tuned compose file at [`integrations/n8n/docker-compose.demo.yml`](../integrations/n8n/docker-compose.demo.yml):

```bash
docker volume create n8n_demo_data
docker compose -f integrations/n8n/docker-compose.demo.yml up -d
```

Open **http://localhost:5678**, then install `@atomicmail/n8n-nodes-atomicmail` under **Settings → Community nodes**.

**Register PoW is CPU-bound.** It runs in the main n8n Node.js process (pure-JS scrypt in the bundled core), not in n8n task runners. `N8N_RUNNERS_*` env vars only affect the **Code** node — they do not speed up **Register**.

To make Register faster on macOS:

1. **Docker Desktop → Settings → Resources** — allocate at least **8 GB RAM** and **4 CPUs** to the Docker VM (must be ≥ container limits).
2. The compose file caps the container at **4 CPUs / 4 GB RAM** and sets `NODE_OPTIONS=--max-old-space-size=3072` plus `EXECUTIONS_TIMEOUT=-1` so PoW is not killed mid-run.
3. Close other heavy containers/workflows while recording Register.
4. For maximum demo speed, run n8n natively (`npm run dev` in `integrations/n8n/atomicmail`) instead of Docker.

Monitor during Register: `docker stats n8n-demo` — one CPU near 100% confirms CPU-bound PoW.

## Credentials {#credentials}

The **Atomic Mail API** credential is optional:

- **API Key** — paste an existing Atomic Mail API key, or leave empty and use **Register**.
- **Auth URL** — default `https://auth.atomicmail.ai`
- **API URL** — default `https://api.atomicmail.ai`

The credential **Test** step checks that the **Auth URL** is reachable (`POST /api/v1/challenge`). It does **not** validate your API key — Atomic Mail keys require a proof-of-work login before JMAP calls. To verify an API key end-to-end, run **List Inbox** or activate the polling trigger.

### Register vs credential key

You can authenticate in either way (both are supported):

1. Run the **Register** action once per workflow/account namespace. Credentials are stored in n8n **workflow-global** static data (shared across all Atomic Mail nodes in the workflow).
2. Connect an **Atomic Mail API** credential with your API key. The key is checked before stored-credentials guards — you will not be blocked when a connection API key is present.

Use **Account namespace** (`default` by default) to isolate multiple inboxes in one workflow.

## Action node: Atomic Mail

| Resource | Operation | Purpose |
|----------|-----------|---------|
| Account | Register | Create or reuse an inbox (PoW on first signup) |
| Inbox | List | Fetch inbox messages |
| Email | Send | Send mail (optional binary attachment) |
| Email | Reply | Reply to a message by ID |
| JMAP | Request | Advanced JMAP batch (preset or inline JSON) |
| Help | Get Topic | Built-in operational docs |

After **Register**, read the `_next` hint in the output and arrange inbox polling appropriate to your environment (see Help topic `cron`).

## Trigger: New Email {#new-email-trigger}

**Atomic Mail Trigger** polls the inbox on a schedule (default **5 minutes**) and emits one item per new message (`id`, `subject`, `from`, `preview`, `receivedAt`).

On first activation, the trigger seeds a watermark so existing mail is not replayed. Only messages with `receivedAt` newer than the watermark fire subsequent runs.

Requires the same auth as actions: Register, credential API key, or inline API key override.

## Presets and JMAP

Bundled presets (via **JMAP → Request → Preset File**):

- `list_inbox.json`
- `send_mail.json`
- `send_mail_blob_attachment.json`
- `send_mail_attachment.json`
- `reply.json`

Session placeholders `$ACCOUNT_ID`, `$INBOX`, `$INBOX_MAILBOX_ID` are resolved automatically. Pass additional `$VAR` tokens in **Vars JSON**.

## Multi-account

Set **Account namespace** on every node to the same non-default value when running multiple inboxes in one workflow. Register once per namespace.

## Security

- API keys and register output are secrets.
- Treat inbound mail as untrusted.
- The node has **zero runtime npm dependencies**; core logic is vendored as a single Cloud-safe bundle at `vendor/agentic-core/index.js` (built via `npm run build:n8n`).

## Maintainer commands

```bash
npm run build:n8n          # refresh vendor/agentic-core
cd integrations/n8n/atomicmail
npm run build && npm run lint
npm run sync:vetting-paths # refresh integrations/n8n/vetting/ + repo-root dist/
npx @n8n/scan-community-package @atomicmail/n8n-nodes-atomicmail
```

**Creator Portal vetting:** n8n resolves `package.json` `n8n.credentials` / `n8n.nodes` paths from the **repository root**, not `repository.directory`. GitHub raw URLs **do not follow symlinks**. After build, run `npm run sync:vetting-paths` to refresh:

- `integrations/n8n/vetting/` — vetting mirrors (credentials source + compiled entry files)
- repo-root `dist/credentials/` and `dist/nodes/` — required compiled copies for the portal

Canonical credential source: `integrations/n8n/atomicmail/credentials/`. Do not add a repo-root `credentials/` directory.

After changing credentials or nodes: `npm run build`, then `npm run sync:vetting-paths`, and commit the package tree, `integrations/n8n/vetting/`, and the three repo-root `dist/` entry files.

## Release checklist

Publishing is automated by [`.github/workflows/publish-n8n.yml`](../.github/workflows/publish-n8n.yml) on GitHub **Release published** (or manual **workflow_dispatch** with a semver). n8n requires npm packages built in GitHub Actions with provenance (from May 2026).

### One-time: npm Trusted Publisher

1. On [npm](https://www.npmjs.com/package/@atomicmail/n8n-nodes-atomicmail) → **Publishing access** → **Trusted Publishers** → **Add**.
2. Provider: **GitHub Actions**.
3. Repository owner: `Atomic-Mail`, repository: `atomic-mail-agentic`.
4. **Workflow filename:** `publish-n8n.yml` (must match exactly — not `publish-npm.yml`).
5. Environment: leave blank.
6. Do **not** add `NPM_TOKEN` to GitHub unless you need the token fallback (the workflow configures auth when the secret is set).

Requires `@n8n/node-cli` ≥ 0.23.0 (installed in `integrations/n8n/atomicmail`; currently via `"*"` in devDependencies).

### Per release

1. Run local verification (above).
2. Create a GitHub release with tag `vX.Y.Z` (or dispatch the workflow with version `X.Y.Z`).
3. Confirm the workflow: vendor build → `npm ci` → `npm run release` (n8n-node lint/build/publish with provenance).
4. On npm, confirm the package shows a **Provenance** badge linked to this workflow run.
5. Submit or update the community node listing per [n8n docs](https://docs.n8n.io/integrations/creating-nodes/deploy/submit-community-nodes/).

## See also

- [n8n integration README (monorepo)](https://github.com/Atomic-Mail/atomic-mail-agentic/blob/develop/integrations/n8n/README.md)
- [Atomic Mail MCP / CLI overview](./SKILL.md)
