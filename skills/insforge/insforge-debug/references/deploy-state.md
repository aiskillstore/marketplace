# Deploy state

History and per-deploy metadata for both frontend deployments (Vercel) and edge function deploys. The primary primitive for debugging **what happened during a deploy** — separate from runtime logs because deploy failures often never leave a runtime trace.

## Commands

```bash
# Frontend (Vercel)
npx -y @insforge/cli deployments list
npx -y @insforge/cli deployments status <id> [--sync] [--json]

# Edge function deploys
npx -y @insforge/cli logs function-deploy.logs [--limit <n>]
npx -y @insforge/cli functions list
```

## Frontend deployments

`deployments list` returns recent deploys with status. `deployments status <id> --json` returns per-deploy metadata:

| Field | Meaning |
|-------|---------|
| `status` | `pending` / `building` / `ready` / `error` / `canceled` |
| `metadata.target` | Vercel deploy target (production / preview) |
| `metadata.fileCount` | Number of files uploaded |
| `metadata.projectId` | Vercel project ID |
| `metadata.startedAt` | Build start time |
| `metadata.envVarKeys` | Env var keys baked into the build (values redacted) |
| `metadata.webhookEventType` | e.g., `deployment.succeeded`, `deployment.error` |

`--sync` re-fetches from Vercel (use when the local cached status looks stale).

## Edge function deploys

`function-deploy.logs` captures backend deploy events (compile errors, push failures, registration errors). `functions list` confirms the final state — if the function isn't there or `status != active`, the deploy didn't fully take.

## How to read

For "frontend deploy failed":

1. `deployments list` — find the failing deploy id
2. `deployments status <id> --json` — read `status` and the `metadata` block; `webhookEventType` usually names the failure stage
3. Reproduce locally: `npm run build` — server deploys often surface the same error that local build would (faster to debug locally)
4. Verify `envVarKeys` matches what the app needs at runtime

For "function deploy failed":

1. `npx -y @insforge/cli logs function-deploy.logs --limit 50` — find the build/push error
2. `npx -y @insforge/cli functions list` — confirm the function did or didn't make it into the active list
3. Re-run `npx -y @insforge/cli functions deploy <slug>` if needed and capture stdout for the explicit error

## Boundaries

- **Doesn't surface Vercel build logs inline.** Detailed Vercel build output lives in the Vercel dashboard or via `vercel logs`; this primitive surfaces the deploy *event metadata*.
- **Doesn't include compute service (Fly) deploy errors.** For compute services use `npx -y @insforge/cli compute events <id>` (machine lifecycle); container stdout/stderr is not yet exposed.
- **Distinct from runtime errors.** A function with a successful deploy can still error at invoke time — that's [logs](logs.md) `function.logs`, not this primitive.

## Example

User reports: "I ran `deployments deploy` and got an error."

```bash
# 1. Get the most recent deploy id and status
npx -y @insforge/cli deployments list

# 2. Full metadata on the failed one
npx -y @insforge/cli deployments status <id> --json

# 3. Reproduce locally to see the actual build error
npm run build
```

User reports: "`functions deploy my-handler` failed."

```bash
# 1. Re-run to capture the explicit error
npx -y @insforge/cli functions deploy my-handler

# 2. Backend-side deploy log
npx -y @insforge/cli logs function-deploy.logs --limit 50

# 3. Confirm the function isn't half-deployed
npx -y @insforge/cli functions list
```

## Frequently paired with

- [logs](logs.md) — `function-deploy.logs` is the source; `function.logs` is separate (runtime, not deploy)
- [metadata](metadata.md) — verify the function ended up `active` after deploy
