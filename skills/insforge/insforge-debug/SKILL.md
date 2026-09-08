---
name: insforge-debug
description: >-
  Use when diagnosing problems in an InsForge project — reactive failures (SDK
  error object, HTTP 4xx/5xx, gateway timeout 502/503/504, edge function failure
  or timeout, login/OAuth/auth errors, RLS denial, realtime channel issues,
  slow query on one endpoint, edge function or Vercel deploy failure), proactive
  audits (security/RLS review, performance/index review, system health check,
  pre-launch readiness), or when the user has an error but doesn't know where
  to start.
license: Apache-2.0
---

# InsForge Debug

Diagnose problems in InsForge projects by combining the backend's observability primitives — logs, metrics, db-health, advisor, policies, metadata, error objects, deploy state, and AI assist. This skill provides:

1. A reference per **debug primitive** (one observability surface each — under `references/`)
2. **Symptom Recipes** (below) that name the primitive sequence for known reactive symptoms and proactive audits

**Always use `npx -y @insforge/cli`** — never install the CLI globally.

## Fastest Path: AI-Assisted Triage

When the user gives a concrete description (error message, failing URL, HTTP status), hand it to the InsForge debug agent. Unlike the other primitives, this one returns suggestions, not just observations — verify the diagnosis against the primitives it cites before acting on it.

```bash
npx -y @insforge/cli diagnose --ai "<issue description>"
```

See [references/ai-assisted.md](references/ai-assisted.md) for when to use this first vs when to skip, and how to verify the output.

## Debug Primitives

Each primitive is one independently-queryable observability surface backed by a distinct underlying data source. Real diagnoses are compositions of primitives.

All commands run via `npx -y @insforge/cli ...`. The `(command)` shown next to each primitive is the actual CLI command — primitive names are concept labels, **not** CLI subcommand names (e.g., "DB health" is `diagnose db`, not `diagnose db-health`; "Policies" is `db policies`, not `diagnose policies`).

| Primitive (command) | What you see | Reference |
|---------------------|-------------|-----------|
| **Logs** (`logs <source>`; `diagnose logs` for cross-source aggregate) | Time-stream of events from 5 backend sources (`insforge.logs` / `postgREST.logs` / `postgres.logs` / `function.logs` / `function-deploy.logs`) | [references/logs.md](references/logs.md) |
| **Metrics** (`diagnose metrics`) | EC2 instance time-series (CPU / memory / disk / network) over `1h` / `6h` / `24h` / `7d` | [references/metrics.md](references/metrics.md) |
| **DB health** (`diagnose db`) | Current Postgres state via 7 named checks (`connections` / `slow-queries` / `bloat` / `size` / `index-usage` / `locks` / `cache-hit`) | [references/db-health.md](references/db-health.md) |
| **Advisor** (`diagnose advisor --json`) | Static-scan issues across 3 categories (`security` / `performance` / `health`) with `ruleId` / `affectedObject` / `recommendation` | [references/advisor.md](references/advisor.md) |
| **Policies** (`db policies`) | Active RLS rules from `pg_policies` (USING / WITH CHECK per cmd per role) — returns all policies as a dump | [references/policies.md](references/policies.md) |
| **Metadata** (`metadata --json`) | Declarative backend state dump (auth config / tables / buckets / functions / AI models / realtime channels) | [references/metadata.md](references/metadata.md) |
| **Error objects** (no command — read SDK / HTTP response) | SDK error envelope + HTTP status — the routing table from a client-visible error to the right log source | [references/error-objects.md](references/error-objects.md) |
| **Deploy state** (`deployments list` + `deployments status <id> --json` + `logs function-deploy.logs`) | Frontend (Vercel) deployment history + per-deploy metadata, plus edge function deploy logs | [references/deploy-state.md](references/deploy-state.md) |
| **AI assist** (`diagnose --ai "<description>"`) | LLM agent that combines the other primitives — returns a diagnosis with suggestions | [references/ai-assisted.md](references/ai-assisted.md) |

## Symptom Recipes

Each recipe is a primitive call sequence with one-line "look for X" at each step. Command syntax, flags, and deep interpretation are in the per-primitive references above.

### Recipe: SDK returned `{ data: null, error: { code, message } }`

1. **error-objects** — read code/message/details. If code starts with `PGRST*`, route by prefix using the table in the reference.
2. **logs** (matching source per error-objects routing) — find the error timestamp, get the full backend-side context.
3. **db-health** (`connections`, `locks`, `slow-queries`) — only if the error suggests DB issue (PostgREST timeout, lock conflict).

### Recipe: HTTP 4xx/5xx response on a specific request

1. **error-objects** — use the HTTP status routing table to pick the log source (each status has a distinct path; 429 is special).
2. **logs** (right source for that status) — find the failing request line and error.
3. **metrics** — only for 5xx patterns spanning multiple endpoints, to confirm system-wide load issue.

### Recipe: RLS access issue (403 on write, or empty result on read)

> Same bug, two surfacings. Writes (INSERT / UPDATE / DELETE) fail loudly with **403**. Reads (SELECT) fail silently with an **empty array** — PostgREST filters denied rows out instead of returning 403, so the request looks successful with zero rows. Diagnosis path is the same except step 1 only applies to the 403 variant.

1. **logs** (`postgREST.logs`) — *403 variant only*: find the policy violation event with table and role context. *Empty-result variant*: skip — no error is logged for silently-filtered rows.
2. **policies** — list policies for that table; walk USING / WITH CHECK against the actual request and the JWT claim used.
3. **metadata** — verify auth config (which claim feeds `auth.uid()` / `requesting_user_id()`; for third-party auth like Clerk/Auth0, is the provider registered as a JWT issuer?).
4. **db query** (`db query "<sql>"`) — *empty-result variant only*: confirm rows that *should* be visible actually exist by querying as service role (not as the user): `npx -y @insforge/cli db query "SELECT id, user_id FROM <table>"`. Distinguishes "RLS filtered everything" from "no matching data exists".

### Recipe: Login fails / OAuth callback errors / token expired

1. **logs** (`insforge.logs`) — find auth errors with timestamp and provider context.
2. **metadata** — verify the provider is enabled, redirect URLs match the callback URL exactly (protocol + host + path).

### Recipe: Edge function runtime error / timeout

1. **logs** (`function.logs`) — get the error stack and execution context.
2. **metadata** — confirm the function exists and `status: "active"`.
3. (If needed) `npx -y @insforge/cli functions code <slug>` — inspect the source for obvious issues.

### Recipe: `functions deploy` failed

1. **deploy-state** (`function-deploy.logs`) — find the build/push error.
2. **metadata** — confirm whether the function ended up in the active list (partial-deploy detection).

### Recipe: `deployments deploy` failed (Vercel)

1. **deploy-state** (`deployments list` + `status <id> --json`) — read `status`, `metadata.webhookEventType`, and `envVarKeys`.
2. **Local** `npm run build` — reproduce the same error locally for faster iteration.

### Recipe: Single slow query / one endpoint slow

1. **logs** (`postgres.logs`) — find the query text and timestamp.
2. **db-health** (`slow-queries`, `index-usage`) — `slow-queries` only catches it while still running (>5s snapshot); check `index-usage` for a missing index. Already finished? **advisor** (`--category performance --json`) has the `pg_stat_statements` text + mean time; step 1 has the timestamp.
3. **policies** — if it's an RLS-gated table, verify the policy isn't adding hidden joins.

### Recipe: "Memory is at ~80% but nothing is slow"

1. **Expected — say so first.** A dedicated Postgres instance turns idle RAM into shared buffers
   and page cache; steady high memory with little traffic is its healthy state, not a leak
   ([references/metrics.md](references/metrics.md), "Memory: high is normal").
2. **metrics** (`--range 24h`) — only a *rising* trend or OOM kills/restarts change the answer.
   OOM evidence lives in `postgres.logs` as the crash-recovery aftermath ("terminating connection
   because of crash of another server process" / "automatic recovery in progress").
3. With OOM evidence, the fix is headroom: upgrade to a paid plan and pick a larger instance size
   (dashboard → Project Settings → Compute & Disk). OOM on the smallest instances under real load is common and
   expected — never "restart to free memory".

### Recipe: All responses slow / high CPU/memory (active incident)

1. **metrics** (`--range 1h`) — confirm system-wide pressure (CPU / memory / disk).
2. **db-health** — DB is the most common bottleneck; check `connections`, `locks`, `slow-queries`.
3. **logs** (`diagnose logs` aggregate) — error patterns across sources at the spike timestamp.
4. **advisor** (`--severity critical`) — pre-existing known issues that may explain the degradation.

### Recipe: Realtime channel won't connect / messages missing

1. **logs** (`insforge.logs`) — WebSocket errors and subscription failures.
2. **metadata** — verify the channel pattern matches what the client subscribes to, `enabled: true`.
3. **policies** — RLS on the underlying table (realtime delivers row changes; RLS gates which rows the subscriber sees).

### Recipe: 429 rate limit

1. **error-objects** — confirm 429 status. **No logs are recorded for 429s; no `Retry-After` header is returned.** Don't waste time grepping logs.
2. **metrics** (`--range 1h`) — overall backend load context.
3. **Fix is always client-side**: debounce, batch, exponential backoff, eliminate retry loops.

### Recipe: Gateway timeout (502 / 503 / 504) on a specific URL

Route by URL subsystem before drilling:

| URL pattern | Drill into |
|-------------|-----------|
| `/api/database/records/...` | **logs** (`postgREST.logs` → `postgres.logs`) + **db-health** (`locks`, `slow-queries`) |
| `/functions/<slug>` | **logs** (`function.logs`) — function may be crash-looping |
| `/api/auth/...` | **logs** (`insforge.logs`) |
| Any path during system-wide spike | **metrics** (`--range 1h`) |

**504s across *unrelated* paths on a small instance: suspect OOM first.** Intermittent gateway
timeouts hitting database, auth, and functions alike are the classic out-of-memory signature on
the smallest instance sizes: the kernel kills Postgres, every in-flight request times out at the
gateway while crash recovery runs, and it repeats on the next load spike.

**Fast path: `npx -y @insforge/cli diagnose incident`** (Platform login required). The report is
built entirely on the cloud side — Prometheus scrape history, platform records, an outbound
database probe — so it works **even while the instance is down or wedged**, exactly when
`diagnose logs` stops answering. It returns a verdict (`oom_likely`,
`platform_operation_in_progress`, `paused_or_suspended`, `metrics_stopped`, `down_unknown`,
`no_incident_detected`) with the evidence and the recommended action; `oom_likely` already means
the restart/memory correlation checks below passed on the platform side.

If the command is unavailable (older CLI/backend, `--api-key` link mode), confirm manually in
**logs** (`postgres.logs`) via the crash-recovery aftermath — "terminating connection because of
crash of another server process" / "automatic recovery in progress" — **time-correlated with the
5xx burst**: recovery evidence alone only proves an unclean Postgres restart, so the timestamps
must line up before OOM becomes the leading diagnosis
([references/metrics.md](references/metrics.md)). With that evidence the fix is headroom, not a
retry loop:

1. **Upgrade the instance** — `npx -y @insforge/cli projects upgrade-instance <type>`
   (`nano` → `micro` → `small` → `medium` → `large` → `xl`), or dashboard → Project Settings →
   Compute & Disk. On the free plan, upgrade to a paid plan first, then pick the size. The
   resize changes the bill and the CLI asks for interactive confirmation — get the user's
   go-ahead first, then run unattended with the CLI-level `--yes` (the `-y` in `npx -y` is
   npm's install flag, not the confirm-skip). The resize is async — poll `projects get` until
   `operation_status` clears before declaring the incident resolved.
2. The resize **restarts the project as part of the change**, which also clears any wedged
   state — there is no separate user-facing restart, and a bare restart would only buy minutes
   before the next spike OOMs again. OOM under real load on the smallest sizes is common and
   expected, not a bug.

### Recipe: Pre-launch / proactive audit

> Requires Platform login (`npx -y @insforge/cli login`). **Not available when the project is linked via `--api-key`** — fall back to `db-health` + `policies` + `metadata` for a manual audit in that case.

1. **advisor** — full scan, then `--severity critical` first, then warnings.
2. **advisor** (`--category security`) — focus on security issues; cross-verify with **policies** (RLS coverage) and **metadata** (auth config, public buckets, secret presence).
3. **advisor** (`--category performance`) — cross-verify with **db-health** (`slow-queries`, `index-usage`, `bloat`).
4. **advisor** (`--category health`) — cross-verify with **metrics** (resource trends over `7d`).
5. After fixes, re-run **advisor** and confirm `isResolved: true` for each addressed `ruleId`.

### Recipe: Don't know where to start

1. **ai-assisted** (`diagnose --ai "<error or URL>"`) — get a starting hypothesis.
2. **Verify** by re-checking the primitives the diagnosis names. Trust the primitive observations over the suggestion.

## When the Root Cause Is InsForge Itself

Some diagnoses end at an InsForge-side defect, not a project misconfiguration: a platform bug or regression, an SDK call that misbehaves, docs or a skill that contradict observed behavior, or a missing capability. A debug session is exactly where these get confirmed — report them while the evidence is in hand:

```bash
npx -y @insforge/cli feedback --json \
  --type bug --component backend --area db \
  --title "<one-line summary>" \
  --detail "<what happened vs expected, minimal repro>" \
  --command "<the failing call>" \
  --error "<verbatim error from logs>" \
  --workaround "<what you did instead>"
```

No login required; common PII patterns (emails, credential/key formats, public IPs, home-directory usernames) are redacted locally — pattern-based, so still keep user data out. Use `--component sdk --language <lang>` for SDK defects; `--component docs` or `--component skills` with `--doc` and `--expected` when documentation contradicts reality; `--type feature-request` when the finding is "not supported". Then continue the user's task with the workaround — never block on the report, and never file feedback for problems in the user's own app code or config. Full flag reference: the **insforge-cli** skill's Feedback section.
