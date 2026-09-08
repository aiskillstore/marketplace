# Metrics

EC2 instance time-series telemetry: CPU, memory, disk, network. The primary primitive for confirming **system-wide resource pressure** vs an isolated request issue.

## Command

```bash
npx -y @insforge/cli diagnose metrics [--range 1h|6h|24h|7d] [--metrics <list>]
```

Default range: `1h`.

## What you see

| Metric family | Indicates |
|---------------|-----------|
| **CPU** | Compute saturation (sustained >80% = trouble; spike & recover = normal) |
| **Memory** | Memory pressure — but read it with the [high-is-normal rule](#memory-high-is-normal): flat-high = healthy cache; *rising* over time → leak; OOM kills → resize |
| **Disk** | Storage fill rate, IO saturation (read/write throughput, queue depth) |
| **Network** | Inbound/outbound bandwidth, packet rate (sudden spike = traffic surge or attack) |

## Range selection

| Symptom | Range | Why |
|---------|-------|-----|
| Active incident ("everything is slow right now") | `1h` | High-resolution to catch the spike |
| "It was slow ~6 hours ago, what happened?" | `6h` | Cover the window with reasonable resolution |
| "Has performance degraded this week?" | `24h` or `7d` | Trend analysis, not point-in-time |
| Pre-launch baseline | `7d` | Establish normal range before traffic |

## How to read

1. **Start from baseline**: what does the normal range look like for this metric? Always look at the trend, not a single point.
2. **Correlate to events**: spike at a specific timestamp → cross-reference [logs](logs.md) for what was happening then.
3. **Distinguish saturation vs spike**:
   - Sustained high = saturation → scale up or fix the load source
   - Brief spike + recovery = normal burst → not actionable on its own

### Memory: high is normal

A dedicated Postgres instance is *expected* to sit high on memory — often 70–90% — even with zero
traffic: Postgres turns idle RAM into shared buffers and page cache and holds it. "Memory averages
78% with no active queries" describes the healthy steady state, not a leak. **Say that first**,
before proposing any action.

Escalate from "normal" to "needs headroom" only on real pressure evidence:

- **OOM kills / container restarts** — after an OOM kill the concrete signature is the Postgres
  crash-recovery aftermath in `postgres.logs`: "terminating connection because of crash of another
  server process" or "database system was not properly shut down; automatic recovery in progress".
  There is no dedicated OOM log source, so look for that aftermath, not an OOM line.
- **Gateway 502/503/504 bursts across unrelated paths** — while crash recovery runs, every
  in-flight request times out at the gateway regardless of subsystem; on the smallest instance
  sizes this is the most common way an OOM actually surfaces to users (see the gateway-timeout
  recipe in the skill).
- **Rising trend** across `24h`/`7d` (a leak climbs; the buffer cache is ~flat from startup)
- Performance actually degrading alongside it (pair with [db-health](db-health.md))

When that evidence exists, the fix is headroom, and on smaller instances OOM under real load is
common — not a bug: upgrade to a paid plan, then pick a larger instance size (dashboard →
Project Settings → Compute & Disk). Never propose restarting to "free" memory: the cache refills by design and
the restart just costs downtime.

## Boundaries

- **Instance-level only.** Metrics show the EC2 box's resource use, not per-request latency or per-query cost. For request-specific perf, combine with [logs](logs.md) (`postgres.logs` for slow queries) and [db-health](db-health.md).
- **Doesn't explain causes.** Metrics show *symptoms* (CPU high), not *causes* (which query, which function). Pair with [logs](logs.md) or [db-health](db-health.md) for root cause.
- **Edge function execution is separate.** Functions run in their own runtime; their resource use isn't in EC2 metrics.

## Example

User reports: "API has been slow for the last 2 hours."

```bash
# 1. Check resource pressure over the right window
npx -y @insforge/cli diagnose metrics --range 6h

# 2. If CPU/memory spiked at a timestamp, line it up with errors
npx -y @insforge/cli diagnose logs --limit 200

# 3. If DB is the bottleneck (Postgres-heavy CPU patterns)
npx -y @insforge/cli diagnose db
```

## Frequently paired with

- [db-health](db-health.md) — DB is the most common bottleneck behind CPU/memory pressure
- [logs](logs.md) — correlate metric spikes to log events at the same timestamp
- [advisor](advisor.md) — `--severity critical` may already flag the underlying cause (e.g., missing index)
