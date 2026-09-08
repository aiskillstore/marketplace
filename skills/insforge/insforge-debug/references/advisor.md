# Advisor

Static-scan engine that audits the project against a rule catalog and returns issue rows. The primary primitive for **proactive audits** — security misconfigurations, performance regressions, and system health concerns surfaced **without a specific failing request**.

## Command

```bash
npx -y @insforge/cli diagnose advisor [--severity critical|warning|info] [--category security|performance|health] [--limit <n>] [--json]
```

Default limit: 50. Requires Platform login — **not available on backends linked via `--api-key`**.

**Add `--json` when you need the full issue payload.** Human-readable output is a 4-column table (severity / category / affectedObject / title). Fields like `ruleId`, `description`, `recommendation`, `isResolved` are only emitted by `--json` — without the flag, you can't read or act on the recommendation programmatically.

## What you see

Each scan returns:

**Scan summary** — `scanId`, `scannedAt`, status, and counts by severity (critical / warning / info).

**Issue rows** — each issue has:

| Field | Meaning |
|-------|---------|
| `ruleId` | Stable identifier of the rule that fired (e.g., `security.rls.missing-policy`) |
| `severity` | `critical` / `warning` / `info` |
| `category` | `security` / `performance` / `health` |
| `affectedObject` | The specific schema object (table, function, policy, secret name) the issue applies to |
| `title` | Short human label |
| `description` | What the rule detected |
| `recommendation` | Suggested fix, often a concrete SQL/CLI step |
| `isResolved` | `true` after a re-scan confirms the fix |

## Categories

| Category | Typical rules | Fix in |
|----------|--------------|--------|
| `security` | RLS missing/permissive on a table, expired/exposed secrets, weak JWT config, public bucket on sensitive data | `db migrations` (RLS), `secrets` (key rotation), `metadata` (auth/bucket config) |
| `performance` | Missing index on heavy filter column, bloat over threshold, sequential scans on large tables, slow recurring query | `db migrations` (indexes), query rewrite, vacuum tuning |
| `health` | Connection pool near limit, EC2 disk filling, deprecated feature in use, version drift | Infra resize, code change, version upgrade |

## How to read

1. **Start with severity**: `--severity critical` first; critical issues block launch.
2. **Group by category** to keep the fix mode coherent (don't context-switch between RLS edits and index migrations).
3. **`affectedObject` tells you where to fix** — it names the concrete schema object.
4. **`recommendation` is usually actionable as-is**. Verify it makes sense (the recommendation may be generic), then apply via the appropriate primitive's tooling.

## Iteration workflow

```text
1. Scan:    diagnose advisor --severity critical --json
2. Triage:  pick one issue, read affectedObject + recommendation
3. Verify:  inspect the affected object (db query / db policies / metadata)
4. Fix:     apply the change (migration / RLS edit / secret rotation / config update)
5. Re-scan: diagnose advisor --json — confirm isResolved=true for that ruleId
6. Repeat with next critical, then warnings, then info
```

## Boundaries

- **Scans are not real-time.** A new scan triggers when the platform schedules it; recommendations lag behind very recent changes. Force a fresh scan if needed.
- **Recommendations are static suggestions, not auto-fixes.** Always validate against current schema state before applying.
- **`affectedObject` is a string, not a typed reference.** It names the object but doesn't link to it — combine with [metadata](metadata.md) / [policies](policies.md) to inspect.
- **Not available when linked via `--api-key`.** Requires `insforge login` (Platform auth).

## Example

Pre-launch audit:

```bash
# Full scan, critical only first
npx -y @insforge/cli diagnose advisor --severity critical

# Security focus
npx -y @insforge/cli diagnose advisor --category security

# Performance focus (often pairs with db-health to verify)
npx -y @insforge/cli diagnose advisor --category performance
npx -y @insforge/cli diagnose db --check slow-queries,index-usage

# Re-scan after fixes
npx -y @insforge/cli diagnose advisor --severity critical
```

## Frequently paired with

- [policies](policies.md) — security category issues often name a table with missing/broken RLS policy
- [metadata](metadata.md) — security/health issues often name a configured object (bucket, secret, auth provider) whose state needs inspecting
- [db-health](db-health.md) — performance category overlaps with `slow-queries` / `index-usage` / `bloat`; cross-verify
- [metrics](metrics.md) — health category issues (pool exhaustion, disk fill) line up with metric trends
