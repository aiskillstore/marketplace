---
name: insforge-cli
description: >-
  Use this skill whenever someone needs a backend, or a task touches InsForge backend or cloud infrastructure through the InsForge CLI: projects, SQL, migrations, RLS policies, functions, storage, backups, deployments, compute, secrets, config, schedules, logs, diagnostics, advisor scans and suppressions, import/export, AI/OpenRouter setup and usage overview, Stripe/Razorpay payments, Apify web scraping / data sources, PostHog product analytics, backend branches, organization membership (invite, leave, delete), agent memory (remember/recall project facts and decisions), reporting InsForge-side bugs or doc discrepancies (feedback), or CLI docs. For app code with InsForge or @insforge/sdk, use the insforge app-integration skill instead.
license: Apache-2.0
---

# InsForge CLI

Use this skill whenever someone needs a backend, or when managing InsForge backend and cloud infrastructure with the InsForge CLI. For application code that calls InsForge from a frontend, backend, or edge function, use the `insforge` app-integration skill instead.

## Core Rules

- Always run the CLI through `npx -y @insforge/cli <command>`. Keep npx's `-y`: without it, npx asks "Ok to proceed?" before installing the package and blocks forever in a TTY-attached agent shell. Do not install or call a global `insforge` binary.
- If the project is already linked, use the current linked project. Run login, project creation, link, project discovery, organization listing, or cloud project commands only when connection setup is actually needed.
- When a task needs a backend and no project is linked yet, do connection setup FIRST — before writing any app code: (1) log in (`whoami` to check; in sandboxes use the two-step device login below), (2) `create` a new project or `link` an existing one, (3) then build against the real project URL and keys from the CLI. Never scaffold with placeholder credentials like `your-project.region.insforge.app` — get the real values first.
- Treat InsForge API keys as full-access admin keys. Keep them server-only and out of frontend/public env vars.
- Prefer CLI commands and documented project config over raw backend HTTP calls. If `config apply` reports unsupported/skipped fields, surface that result instead of bypassing the CLI with direct API calls.
- Use `--json` when structured output or non-interactive value collection is needed. Use `--yes` for confirmation prompts when the user has approved the action.
- At the start of a non-trivial task on a linked project, run `npx -y @insforge/cli memory list` (cheap, no AI call) and recall any title relevant to the task before designing or debugging. Record decisions and the gotchas you hit with `memory remember` at the moment they happen. See `references/memory.md`.
- When you hit a hurdle that is InsForge's fault — something that should work but doesn't, a capability you needed but isn't supported, instructions (docs/skill) that reality contradicts, or needless friction — report it with `npx -y @insforge/cli feedback` (see Feedback), then continue the user's task with a workaround. Never file feedback for problems in the user's own app code.

## Global Options

| Flag          | Use                                                                                                                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--json`      | Structured JSON output and skip value-collection prompts such as text/select prompts. Errors if any required value is missing. Combine with `-y` for destructive commands that also ask for Y/N confirmation. |
| `-y`, `--yes` | Auto-accept Y/N confirmation prompts such as delete or overwrite prompts. Does not skip value-collection prompts; use `--json` for that. Separate from npx's own `-y`, so both appear together: `npx -y @insforge/cli link --project-id <id> -y`. |

## Exit Codes

| Code | Meaning                                                 |
| ---- | ------------------------------------------------------- |
| 0    | Success                                                 |
| 1    | General error, including HTTP 400+ from function invoke |
| 2    | Not authenticated                                       |
| 3    | Project not linked                                      |
| 4    | Resource not found                                      |
| 5    | Permission denied                                       |

## Environment Variables

| Variable                | Use                                |
| ----------------------- | ---------------------------------- |
| `INSFORGE_ACCESS_TOKEN` | Override stored access token       |
| `INSFORGE_PROJECT_ID`   | Override linked project ID         |
| `INSFORGE_EMAIL`        | Email for non-interactive login    |
| `INSFORGE_PASSWORD`     | Password for non-interactive login |

## Connection Setup

If a task needs project access and the connection state is unknown, start with `npx -y @insforge/cli current`. Use `npx -y @insforge/cli whoami` when the authenticated identity matters or when `current` reports that the CLI is not authenticated.

If not authenticated, run `npx -y @insforge/cli login` (opens a browser). For headless / agent / CI contexts with no browser, authenticate non-interactively with a user API key: `npx -y @insforge/cli login --user-api-key "$INSFORGE_USER_API_KEY"` (the user creates the key in the dashboard under Profile → API Keys). In sandboxes where the user has a browser but it cannot reach the CLI's local callback (e.g. the ChatGPT app), use device login as two steps: `timeout 15 npx -y @insforge/cli login --device --json 2>&1 || true` to capture the verification link + code, relay them to the user, then rerun `npx -y @insforge/cli login --device --json` to resume the same code and complete once they click Authorize — see `references/login.md`. If the sandbox reports that `api.insforge.dev` is not an allowed network domain, ask the user to add it to the workspace's allowed network domains, then retry. If no project is linked, use `npx -y @insforge/cli link` for an existing project or `npx -y @insforge/cli create` when the user asked for a new backend. In workflows that are already prelinked or preconfigured, such as CI, local test projects, automation, or explicit user-provided project context, use that project context directly. A cloud project is the default throughout; only when the user explicitly asks for a backend running in Docker on their own machine, see `references/local.md` — never as a fallback when login or `create` is inconvenient.

## Command Routing

| Need                                                                                               | CLI area                                        | Reference                                                                                   |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Login, logout, current user                                                                        | `login`, `logout`, `whoami`                     | `references/login.md`                                                                       |
| Create/link/list/current project                                                                   | `create`, `link`, `list`, `current`, `metadata` | `references/create.md`                                                                      |
| Backend in Docker on the user's own machine — only when they explicitly ask     | `local`                                         | `references/local.md`                                                                       |
| Project lifecycle: status, rename, delete, restore, version update, instance resize, transfer       | `projects`                                      | this file                                                                                   |
| Subscription/plan, credits, usage, payment history, billing cycles, plan upgrade, billing portal    | `billing`, `usage`                              | this file                                                                                   |
| Organizations and members (create, update, invite, roles, leave, delete)                           | `orgs`                                          | this file                                                                                   |
| Project backups (list, latest, create, rename, delete, restore — cloud and self-hosted)            | `backups`                                       | this file                                                                                   |
| Advisor scans and suppressing findings (false positives, accepted risks)                           | `advisor`, `diagnose advisor`                   | this file                                                                                   |
| Schema, SQL, RLS, triggers, indexes, imports, exports                                              | `db`                                            | `references/database/*`                                                                     |
| Auth redirects, password policy, SMTP, storage size, realtime/schedule retention, subdomain config | `config`                                        | `references/config.md`                                                                      |
| Storage buckets and objects                                                                        | `storage`                                       | this file                                                                                   |
| Realtime backend setup                                                                             | `db` migrations                                 | `references/realtime.md`                                                                    |
| Edge functions                                                                                     | `functions`                                     | `references/functions-deploy.md`                                                            |
| AI/OpenRouter key setup and Model Gateway usage overview                                           | `ai setup`, `ai overview`                       | this file                                                                                   |
| Agent memory: project facts, decisions, preferences, references across sessions                    | `memory`                                        | `references/memory.md`                                                                      |
| Stripe/Razorpay keys, catalog sync, webhooks                                                       | `payments`                                      | `references/payments/overview.md`                                                           |
| Frontend deployments                                                                               | `deployments`                                   | `references/deployments/deploy.md`                                                          |
| Custom domains, Cloudflare Registrar, DNS sync, SSL verification                                    | `domains`                                       | `references/deployments/domains.md`                                                         |
| Backend containers/services                                                                        | `compute`                                       | `references/compute-deploy.md`                                                              |
| Secrets/env vars                                                                                   | `secrets`, deployment/compute env commands      | this file                                                                                   |
| Scheduled jobs                                                                                     | `schedules`                                     | `references/schedules.md`                                                                   |
| Backend branches                                                                                   | `branch`                                        | `references/branch/overview.md`, `references/branch/merge.md`, `references/branch/reset.md` |
| Logs and health checks                                                                             | `logs`, `diagnose`                              | `references/diagnostics.md`                                                                 |
| Built-in documentation lookup                                                                      | `docs`                                          | this file                                                                                   |
| PostHog setup                                                                                      | `posthog setup`                                 | `references/posthog.md`                                                                     |
| Apify web scraper (connect, auth bridge, scrape, land, schedule)                                   | `webscraper apify`                              | `references/webscraper/apify.md`                                                            |
| Report an InsForge-side bug, doc discrepancy, or design problem                                    | `feedback`                                      | this file                                                                                   |

## Database Workflow

Use database references before writing migrations when the task involves non-trivial database work:

- `references/database/migrations.md` - migration file creation and apply workflow.
- `references/database/query.md` - raw SQL execution and targeted inspection.
- `references/database/access-control.md` - RLS, grants, recursion-safe helper functions, ACLs, protected fields, and public projections.
- `references/database/integrity.md` - constraints, triggers, derived state, lifecycle guards, append-only history, and server-maintained fields.
- `references/database/vector.md` - pgvector extension, vector schema, distance operators, indexes, and vector search SQL/RPC patterns.
- `references/database/export.md` / `references/database/import.md` - schema or data import/export tasks.

Default pattern:

- Prefer `npx -y @insforge/cli db migrations new <name>` plus a migration SQL file for schema, grants, indexes, triggers, functions, and RLS policy changes.
- Apply migrations with `npx -y @insforge/cli db migrations up --all`.
- For new schema work, group related DDL into one migration when practical.
- Use targeted inspection when existing state is unknown or a command fails.
- Use `npx -y @insforge/cli db query <sql>` for targeted inspection and small corrective row/data SQL only when a migration is not appropriate.
- Use `npx -y @insforge/cli db rpc <fn> [--data <json>]` to call database functions through the backend.

Public schema scope:

- For generic application database work, create and modify app-owned objects in the `public` schema.
- Create, alter, drop, grant, revoke, index, trigger, function, view, and policy changes on `public` application objects.
- Do not create custom schemas or write to InsForge-managed/system schemas such as `auth`, `storage`, `realtime`, `payments`, `graphql`, `extensions`, `pg_catalog`, `information_schema`, or `system`, unless you are working on that specific feature module and its docs explicitly allow the operation.
- It is allowed to reference built-in objects such as `auth.users(id)` and `auth.uid()` from public tables or public RLS policies; do not modify those built-in objects.
- Do not create users, seed business rows, or run application CRUD workflows unless the user request explicitly asks for data migration, repair, or test setup.

RLS and access control:

- Use `auth.uid()` or an equivalent authenticated identity expression for user ownership checks.
- Add both SQL privileges and RLS policies. Policies do not replace `GRANT`.
- Runtime roles have broad default DML privileges on `public` tables so RLS can decide row access. If a table needs narrower operation or column access, explicitly `REVOKE` the broad privilege before granting the exact allowed operations or columns.
- Include `WITH CHECK` for INSERT and UPDATE policies so writes cannot create rows the user should not own.
- Prefer helper functions for cross-table RLS checks when direct policy joins can recurse through other RLS policies.
- Helper functions called from RLS policies that query RLS-enabled tables should be `SECURITY DEFINER`.
- Put RLS helper functions in `public` and schema-qualify references such as `public.team_members` and `auth.uid()`.
- For ACLs, protected owner/tenant/role fields, field-level update masks, sanitized public views, or recursion-sensitive policies, read `references/database/access-control.md` before writing migrations.

Integrity:

- For counters, balances, latest pointers, append-only history, state transitions, lifecycle guards, protected deletes, quota guards, leases, or trigger-maintained columns, read `references/database/integrity.md` before writing migrations.

Vector:

- For pgvector, vector search functions, score semantics, ANN indexes, hybrid ranking, RAG chunk retrieval, multi-vector search, or embedding version selection, read `references/database/vector.md` before writing migrations.

## Project and Configuration

Project commands:

- `npx -y @insforge/cli create` - create a new project. Use `--json` with required flags for non-interactive agent runs. See `references/create.md`.
- `npx -y @insforge/cli link` - link the current directory to an existing project.
- `npx -y @insforge/cli link --api-base-url <url> --api-key <admin key>` - link a self-hosted (OSS) backend directly by its URL and admin API key; no platform login required.
- `npx -y @insforge/cli current` - show current linked project.
- `npx -y @insforge/cli metadata --json` - inspect backend metadata when discovery is needed.

Project lifecycle (operates on the linked project unless `--project <id>` is given):

- `npx -y @insforge/cli projects get [--project <id>]` - show a project's current status, in-flight `operation_status`, region, instance type, and version. Use this to poll after an async operation (restore, version update, instance resize) until `operation_status` clears.
- `npx -y @insforge/cli projects update [--name <name>] [--domain <domain>] [--storage-size <gib>] [--project <id>]` - rename or change project settings.
- `npx -y @insforge/cli projects restore [--project <id>]` - bring a paused project back online. Only paused projects can be restored.
- `npx -y @insforge/cli projects update-version [--wait] [--project <id>]` - update the backend to the latest InsForge version (resolved automatically; no-op if already current). Causes a brief restart. Add `--wait` to block until it finishes instead of returning while queued.
- `npx -y @insforge/cli projects upgrade-instance <type> [--project <id>]` - change the instance class. Valid: `nano`, `micro`, `small`, `medium`, `large`, `xl` (`xl` is the ceiling). Restarts the project and changes the bill.
- `npx -y @insforge/cli projects delete --project <id>` - permanently delete a project and all of its resources. `--project` is required (it will not default to the linked project). Irreversible — confirm the exact project id with the user first; this is a guarded, human-in-the-loop operation, so do not auto-bypass the confirmation.
- `npx -y @insforge/cli projects transfer <targetOrgId> --project <id>` - move a project to another organization (billing and access move with it). `--project` is required (it will not default to the linked project). Guarded, human-in-the-loop — confirm the source project and target org first.

Configuration:

- Use `npx -y @insforge/cli config export`, `config plan`, and `config apply` for supported `insforge.toml` knobs.
- TOML is for config values only. SQL belongs in `db migrations`; function code belongs in `functions deploy`; frontend code belongs in `deployments deploy`; compute code/images belong in `compute deploy`.
- If `config apply` returns `skipped[]`, report the skipped items and required backend upgrade. Do not retry with raw HTTP.

## Organizations and Members

Org-scoped commands resolve the organization in this order: `--org-id` flag, `INSFORGE_ORG_ID`, the linked project's org, the configured default org, then a prompt (or single-org auto-select). Pass `--org-id <id>` to act on a specific org.

- `npx -y @insforge/cli orgs list` - list organizations you belong to.
- `npx -y @insforge/cli orgs create <name> [--type personal|team|company]` - create an organization (default type `team`).
- `npx -y @insforge/cli orgs update [--name <name>] [--type <type>] [--org-id <id>]` - rename or change an organization's type.
- `npx -y @insforge/cli orgs members list [--org-id <id>]` - list members and pending invitations.
- `npx -y @insforge/cli orgs members invite <email> [--role administrator|developer] [--org-id <id>]` - invite a member (default role `developer`).
- `npx -y @insforge/cli orgs members role <memberId> <role> [--org-id <id>]` - change a member's role (`administrator` or `developer`).
- `npx -y @insforge/cli orgs members remove <memberId> [--org-id <id>]` - remove a member. Confirm intent first.
- `npx -y @insforge/cli orgs leave --org-id <id>` - leave an organization. `--org-id` is required (it will not default to the linked org). You lose access to all of its projects and must be re-invited to return. The backend refuses if you are the last administrator — transfer the admin role first. Guarded, human-in-the-loop — confirm intent first.
- `npx -y @insforge/cli orgs delete --org-id <id>` - permanently delete an organization. `--org-id` is required (it will not default to the linked org). Owner only. This cascades: every project in the org (databases, storage, all resources) is permanently deleted and the subscription is canceled — the CLI lists the affected projects and warns when the currently linked project is one of them. Irreversible; confirm the exact org id with the user first and do not auto-bypass the confirmation.

## Billing and Usage

Inspect the organization's plan/consumption and manage its subscription. Org resolution matches the Organizations section.

- `npx -y @insforge/cli billing status [--org-id <id>]` - show the current subscription/plan and period.
- `npx -y @insforge/cli billing credits [--org-id <id>]` - show the credit balance and recent credit transactions.
- `npx -y @insforge/cli billing history [--org-id <id>]` - list past payments / invoices.
- `npx -y @insforge/cli billing cycles [--org-id <id>]` - show the current and previous billing-cycle windows.
- `npx -y @insforge/cli usage [--org-id <id>]` - show consumption for the current billing period (summary plus per-project breakdown: database, storage, egress, etc.).
- `npx -y @insforge/cli billing upgrade <plan> [--org-id <id>]` - start a Stripe checkout to change the plan (`free | starter | pro | team | enterprise`). Opens the hosted checkout URL in the browser and also prints it. With `--json` it prints a JSON object (`{ checkoutUrl, sessionId }`) and does not open a browser — use this in headless/CI. No charge happens until the user completes checkout; the backend validates the plan and admin permission.
- `npx -y @insforge/cli billing manage [--org-id <id>]` - open the Stripe customer portal to manage the subscription, payment method, or cancellation. Opens the portal URL in the browser and also prints it. With `--json` it prints a JSON object (`{ portalUrl }`) and does not open a browser — use this in headless/CI.

## Backups

Operates on the linked project unless `--project <id>` is given. Works for both cloud projects and self-hosted projects (linked with `link --api-base-url <url> --api-key <key>`) — the CLI routes to the right backend automatically; an explicit `--project <id>` always targets a cloud project.

- `npx -y @insforge/cli backups list [--project <id>]` - list backups.
- `npx -y @insforge/cli backups latest [--project <id>]` - show the most recent backup. Cloud prints the latest dump file with a presigned download URL; self-hosted prints the newest backup record (no download URL).
- `npx -y @insforge/cli backups create [--name <name>] [--wait] [--project <id>]` - create a backup. `--name` is optional; when provided it must be 1–64 chars. `--wait` blocks until it finishes instead of returning while queued.
- `npx -y @insforge/cli backups rename <backupId> <name> [--project <id>]` - rename a backup (pass `""` to clear the name).
- `npx -y @insforge/cli backups delete <backupId> [--project <id>]` - delete a backup. Confirm intent first.
- `npx -y @insforge/cli backups restore <backupId> [--project <id>]` - restore the project from a backup. Confirm intent first. Cloud: OVERWRITES the project's current database and storage — all data written since the backup is lost. Self-hosted: database-only `pg_restore --clean` — data in backed-up tables is rewound, but tables created after the backup are NOT dropped and storage is untouched.

## Storage

- `npx -y @insforge/cli storage buckets` - list buckets.
- `npx -y @insforge/cli storage create-bucket <name> [--private]` - create a bucket.
- `npx -y @insforge/cli storage delete-bucket <name>` - delete a bucket and all objects. Confirm destructive intent first.
- `npx -y @insforge/cli storage list-objects <bucket> [--prefix] [--search] [--limit] [--sort]` - inspect objects.
- `npx -y @insforge/cli storage upload <file> --bucket <name> [--key <objectKey>]` - upload an object.
- `npx -y @insforge/cli storage download <objectKey> --bucket <name> [--output <path>]` - download an object.
- `npx -y @insforge/cli storage s3-keys list` - list S3-compatible access keys (secret values are never shown).
- `npx -y @insforge/cli storage s3-keys create [--description <text>]` - create an S3 access key. The secret access key is shown ONCE on creation — capture it immediately.
- `npx -y @insforge/cli storage s3-keys delete <id>` - delete an S3 access key. Tools using it stop working. Confirm intent first.

For storage access-control behavior implemented through Postgres policies, use the storage-specific product docs or feature guidance. Do not treat storage internals as generic public-schema database tables unless the referenced storage docs explicitly say to.

## Realtime

Create channel patterns, app-table publish triggers, and channel/message RLS through migrations. See `references/realtime.md`.

## Edge Functions

- `npx -y @insforge/cli functions list` - list deployed functions.
- `npx -y @insforge/cli functions code <slug>` - view function source.
- `npx -y @insforge/cli functions deploy <slug> --file <path>` - deploy or update. See `references/functions-deploy.md`.
- `npx -y @insforge/cli functions invoke <slug> [--data <json>] [--method GET|POST]` - invoke a function.
- `npx -y @insforge/cli functions delete <slug>` - delete a function. Confirm destructive intent first.

## AI Gateway

- `npx -y @insforge/cli ai setup` fetches the linked project's active OpenRouter key and writes `OPENROUTER_API_KEY` to a local server-side env file.
- `npx -y @insforge/cli ai overview` shows Model Gateway key usage: total spend, limit, remaining credit, daily/weekly/monthly spend, and per-model activity when observability is available. Figures are USD credits. Use it to answer "how much AI credit is left / being used".
- Keep `OPENROUTER_API_KEY` server-only. Never expose it as `NEXT_PUBLIC_*`, `VITE_*`, `PUBLIC_*`, or `REACT_APP_*`.

## Memory

Every project has built-in agent memory: durable facts, decisions, preferences, and references that survive across sessions. Use it as a reflex, not an afterthought.

- `npx -y @insforge/cli memory list` - cheap title index (no AI call). Run at the start of a non-trivial task; recall any title relevant to the task.
- `npx -y @insforge/cli memory recall "<query>" [--scope] [--limit] [--threshold]` - semantic + keyword recall.
- `npx -y @insforge/cli memory remember "<content>" [--kind] [--title] [--scope] [--source]` - store one atomic memory. Record decisions and gotchas at the moment they happen, not at session end. `--kind` accepts only `fact`, `decision`, `preference`, or `reference` - store gotchas as `fact` (or `decision` when recording a choice).
- `npx -y @insforge/cli memory remember --file <path>` - extract durable memories from a transcript or notes file.

Storing is idempotent: re-remembering a known fact is a no-op, and a contradicting fact updates the existing memory instead of duplicating it - when the truth changes, just `remember` the new truth. See `references/memory.md` for what to store, kinds, and examples.

## Payments

Use `payments` for Stripe/Razorpay backend setup and catalog sync. See `references/payments/overview.md`.

- Payments are provider-specific: use `payments stripe ...` or `payments razorpay ...` explicitly.
- Configure provider keys with `payments <provider> config set`; setting keys automatically syncs provider state when the key or account changes.
- Check key/account/sync/webhook health with `payments <provider> status`.
- Run `payments <provider> sync` to manually refresh or retry mirrored provider data.
- Stripe uses Products/Prices and supports managed webhook registration; Razorpay uses Items/Plans/Orders and requires manual webhook setup in the Razorpay Dashboard.
- Prefer test mode while building. Use live mode only after explicit user approval.
- If the backend reports payments unavailable, ask the user/admin to enable or upgrade payments. Do not work around it by storing provider keys as generic secrets or embedding payment secret keys in app code.
- Load `references/payments/stripe.md` or `references/payments/razorpay.md` before provider-specific setup.

Runtime checkout, subscriptions, customer portal flows, and app code belong in the `insforge` app-integration skill.

## Deployments

Frontend deployments:

- Build locally first when the app has a build step.
- Ensure frontend runtime env vars are configured with the correct framework prefix before deployment.
- Use `npx -y @insforge/cli deployments deploy <dir>` for frontend source directories. Do not deploy generated output directories unless the deployment reference explicitly calls for it.
- See `references/deployments/deploy.md`.

Custom domains:

- Use `npx -y @insforge/cli domains ...` for custom domains, Cloudflare Registrar, DNS sync, and SSL verification.
- See `references/deployments/domains.md`.

Backend compute services:

- Use `npx -y @insforge/cli compute ...`; do not manage InsForge compute services directly with the user's own `flyctl` account.
- Use source mode for a directory with a Dockerfile, or image mode with `--image <url>` for a pre-built image.
- Use `--env-file` or repeatable env-set/update commands for secrets instead of large inline JSON.
- See `references/compute-deploy.md`.

## Secrets

- `npx -y @insforge/cli secrets list [--all]` - list secret keys without values.
- `npx -y @insforge/cli secrets get <key>` - retrieve a secret value only when necessary.
- `npx -y @insforge/cli secrets add <key> <value> [--reserved] [--expires <ISO date>]` - create a secret.
- `npx -y @insforge/cli secrets update <key> [--value] [--active] [--reserved] [--expires]` - update a secret.
- `npx -y @insforge/cli secrets delete <key>` - soft-delete a secret. Confirm intent first.
- `npx -y @insforge/cli secrets rotate <api-key|anon-key> [--grace-hours <n>]` - rotate the project API key or anon key. The new key is printed ONCE — capture it. The old key keeps working during the grace period (server default if `--grace-hours` is omitted); update all consumers before it expires.

## Schedules

- `npx -y @insforge/cli schedules list/get/create/update/delete/logs`.
- Use standard 5-field cron for wall-clock schedules.
- Use pg_cron interval syntax such as `30 seconds` for sub-minute cadence. Six-field cron with seconds is not supported.
- Headers can reference InsForge secrets with `${{secrets.KEY_NAME}}`.
- See `references/schedules.md` for cron formats, secret header references, examples, common mistakes, and the recommended setup workflow.

## Branching

Use backend branches to test risky schema, RLS, auth, or function changes before applying them to production. See `references/branch/overview.md`.

Common commands:

- `npx -y @insforge/cli branch create <name> [--mode full|schema-only] [--no-switch]`
- `npx -y @insforge/cli branch list`
- `npx -y @insforge/cli branch switch <name>` or `--parent`
- `npx -y @insforge/cli branch merge <name> [--dry-run] [--save-sql <path>]`
- `npx -y @insforge/cli branch reset <name>`
- `npx -y @insforge/cli branch delete <name>`

Branching requires a backend version that supports it. If unavailable, report the backend version limitation instead of inventing a workaround.

## Diagnostics and Logs

- `npx -y @insforge/cli diagnose` - full health report.
- `npx -y @insforge/cli diagnose --ai "<issue description>"` - ask the InsForge debug agent to diagnose a concrete backend issue.
- `npx -y @insforge/cli diagnose metrics [--range 1h|6h|24h|7d]` - EC2 metrics.
- `npx -y @insforge/cli diagnose advisor [--severity critical|warning|info] [--category security|performance|health]` - advisor issues. The Rule column is the id that `advisor suppress` takes.
- `npx -y @insforge/cli diagnose db [--check <checks>]` - database health checks.
- `npx -y @insforge/cli diagnose logs [--source <name>] [--limit <n>]` - aggregate error logs.
- `npx -y @insforge/cli logs <source> [--limit <n>]` - source-specific backend logs.

Typical log sources include `function.logs`, `function-deploy.logs`, `postgres.logs`, `postgrest.logs`, and `insforge.logs`. See `references/diagnostics.md` for common debugging scenarios and source selection.

## Advisor

The backend advisor scans the project for security, performance, and health findings. Read results with `diagnose advisor`; manage scans and false positives with `advisor`:

- `npx -y @insforge/cli advisor scan` - trigger a scan now instead of waiting for the schedule. Use it to re-check immediately after fixing a finding. The scan runs asynchronously (typically well under a minute) — poll `diagnose advisor --json` until `scan.status` is `completed` and `scan.scanId` equals the id that `advisor scan` returned, then read the results.
- `npx -y @insforge/cli advisor suppressions` - list suppressed findings.
- `npx -y @insforge/cli advisor suppress <ruleId> [--object <affectedObject>] --reason <reason> [--note <note>]` - dismiss a finding with a recorded reason. With `--object` (the finding's Affected Object, verbatim) only that instance is suppressed; without it the whole rule is. `--reason` is one of `false_positive | accepted_risk | wont_fix | other`; `--note` is required for `other`. A suppression takes effect from the next scan (run `advisor scan` to see it applied). Only suppress findings the user has judged — never suppress to make a report look clean.
- `npx -y @insforge/cli advisor unsuppress <suppressionId>` - remove a suppression so the finding reappears on the next scan.

## Feedback

When any part of the InsForge toolkit misbehaves — the backend platform, an SDK, the CLI, an agent skill, or the docs — report it to the InsForge team, then continue the task with a workaround. Only report InsForge-side issues, never problems in the user's own app code.

```bash
npx -y @insforge/cli feedback --json \
  --type bug \
  --component backend \
  --title "db policies create returns 500 on uppercase table names" \
  --detail "Creating an RLS policy on table \"Users\" returns 500; lowercase names work. Repro: create table with quoted uppercase name, then run policies create." \
  --area db \
  --command "insforge db policies create --table Users ..." \
  --error "<verbatim error output>" \
  --severity major
```

Required flags:

- `--type`: the kind of hurdle you hit. Map from your situation:
  - "This is not working" (it should, per docs/contract) → `bug`
  - "I was instructed to do X, but reality required an alternative" → also `bug`, with `--doc` (where the instruction lives), `--expected` (what it claimed), and `--workaround` (what worked instead) — you can't know whether the instructions are stale or the product regressed, and those three fields let the team disambiguate
  - "What I want to do is not supported" → `feature-request`
  - "It works, but it was confusing or awkward" (unhelpful error, forced detour) → `friction`
  - anything else → `other`
- `--component`: where in the toolkit it lives — `backend` (platform/hosted services) | `sdk` | `cli` | `skills` (agent skill content) | `docs` | `other`.
- `--title` and `--detail` (or `--file <path>`).

Optional flags:

- `--language`: **required when `--component sdk`** — which SDK, e.g. `js`, `python`, `flutter`, `swift`, `kotlin`, `rest-api`, or `multiple` if it spans SDKs. Also useful with `--component docs` for language-specific doc pages. Omit for other components.
- `--area`: product area — `db` | `auth` | `storage` | `functions` | `deployments` | `billing` | `ai` | `realtime` | `payments`. Orthogonal to `--component`: a broken storage upload in the Python SDK is `--component sdk --language python --area storage`.
- `--workaround`: the alternative you used to get past the hurdle — always include it when you found one; it tells the team how blocking the issue is and often becomes the doc fix.
- `--command` (the CLI/SDK call that surfaced it), `--error` (verbatim output; redacted and truncated automatically), `--expected` (what the docs/skill instructed or you expected) and `--doc "<page or skill section>"` for discrepancies, `--severity blocker|major|minor` (default `minor`).

Keep `--detail` concise and InsForge-focused: what happened, what you expected, minimal repro. Do not paste user app data — the CLI locally redacts common patterns (emails, known credential/key formats, secret assignments, public IPv4 addresses, home-directory usernames) and truncates long fields, but redaction is pattern-based: a safety net, not a license. No login required — works logged out and in OSS setups; project/org context is attached automatically when a cloud project is linked. Returns a feedback id on success (duplicate reports fold into the existing one and return its id).

## Documentation

- `npx -y @insforge/cli docs` - list documentation topics.
- `npx -y @insforge/cli docs instructions` - setup guide.
- `npx -y @insforge/cli docs <feature> <language>` - feature docs for `db`, `storage`, `functions`, `auth`, `ai`, or `realtime` in `typescript`, `swift`, `kotlin`, or `rest-api`.

For application code with InsForge or `@insforge/sdk`, use the `insforge` app-integration skill and use `docs` only as official feature reference.

## PostHog

- `npx -y @insforge/cli posthog setup` ensures the dashboard has a PostHog connection, then prints the official PostHog wizard command plus the connected project's public `phc_` API key and host.
- ⚠️ `posthog setup` alone does NOT instrument the app: no env vars, no SDK, no events until the wizard step happens. The wizard is interactive and may open a browser; ask the user to run it in their real terminal, or instrument manually using the printed `phc_` key/host (PostHog's public client key, safe in frontend env vars).
- Cloud only: self-hosted backends don't expose the integration. Do not substitute a `phc_` key from a separate PostHog account into app env vars — the Analytics page reads from the server-side connection that only `posthog setup` populates; use the key it prints.

## Apify web scraper

- `npx -y @insforge/cli webscraper apify connect` — one-time OAuth connect; stores a refreshable token in InsForge.
- `npx -y @insforge/cli webscraper apify login` — auth bridge: fetches the InsForge-managed token, runs `apify login --token`, and installs Apify's official agent skills. Never run plain `apify login` (browser OAuth). On any Apify `401` / "not logged in", re-run `login`.
- See `references/webscraper/apify.md` for the full scrape → land → schedule workflow and size-based landing strategy.

## Non-Interactive CI/CD

Use env vars and JSON mode for automated contexts:

```bash
INSFORGE_EMAIL=$EMAIL INSFORGE_PASSWORD=$PASSWORD npx -y @insforge/cli login --email -y
npx -y @insforge/cli link --project-id $PROJECT_ID --org-id $ORG_ID -y
npx -y @insforge/cli db query "SELECT 1 AS ok" --json
```

## Project Configuration File

After `create` or `link`, `.insforge/project.json` contains the linked project ID, app key, region, API key, and backend URL.

- Never commit `.insforge/project.json` or share it publicly.
- Do not edit it manually. Use `npx -y @insforge/cli link` or branch commands to switch projects.
