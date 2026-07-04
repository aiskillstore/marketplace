---
name: tilt
description: Use when checking deployment health, investigating errors, reading logs, or working with Tiltfiles. Queries Tilt resource status, logs, and manages dev environments.
---

# Tilt

## First Action: Check for Errors

Before investigating issues or verifying deployments, check resource health. Run **errors first**, separately from pending/in-progress — otherwise real failures get buried in 20+ pending lines:

```bash
# 1. Errors only — surface the buildHistory[0].error so you see WHY, not just THAT
tilt get uiresources -o json | jq -r '.items[] | select(.status.runtimeStatus == "error" or .status.updateStatus == "error") | "\(.metadata.name): runtime=\(.status.runtimeStatus) update=\(.status.updateStatus)\n  reason: \((.status.buildHistory[0].error // "(no buildHistory error; check tilt logs)") | gsub("\n"; " ") | .[0:240])"'

# 2. In-progress and pending — informational; an in-progress build may flip to error any moment
tilt get uiresources -o json | jq -r '.items[] | select(.status.updateStatus == "in_progress" or .status.updateStatus == "pending" or .status.runtimeStatus == "pending") | "\(.metadata.name): runtime=\(.status.runtimeStatus) update=\(.status.updateStatus)"'

# 3. Docker-compose container health — MISSED by the error filter above.
#    An `Up (unhealthy)` compose container keeps runtimeStatus=ok/update=ok, so
#    queries 1-2 never flag it; the red UI badge comes from healthStatus here.
tilt get uiresources -o json | jq -r '.items[] | select(.status.composeResourceInfo.healthStatus == "unhealthy") | "\(.metadata.name): compose healthStatus=unhealthy (HEALTHCHECK failing — service may still be up)"'

# 4. Quick status overview
tilt get uiresources -o json | jq '[.items[].status.updateStatus] | group_by(.) | map({status: .[0], count: length})'
```

If a resource is `in_progress` when you check, **re-poll** before declaring it healthy — it can transition straight to `error` with a populated `buildHistory[0].error`. The `updateStatus` field reflects only the *current* build attempt; the last error always lives in `buildHistory[0].error` even when `updateStatus` is `none` or `not_applicable`.

**Docker-compose resources are a blind spot.** Their `runtimeStatus`/`updateStatus` reflect only build/up state, NOT the container's docker `HEALTHCHECK` — so a probe-failing container (`docker ps` → `Up (unhealthy)`) reads `runtimeStatus=ok` and slips past queries 1-2, while the Tilt UI still reddens it. The authoritative signal is `.status.composeResourceInfo.healthStatus` (`healthy` / `unhealthy` / absent when the service has no healthcheck), which query 3 catches. These resources also have `k8sResourceInfo: null` (`spec.type == "docker-compose"`); to find *why* a probe fails, drop to docker: `docker inspect <compose-project>-<svc> --format '{{json .State.Health}}'` reads the probe's last exit code + output. A common cause is the healthcheck script invoking a CLI the image doesn't ship (e.g. `curl`/`grpcurl` removed in slimmed images) — the service is fine, the probe is broken.

## Non-Default Ports

When Tilt runs on a non-default port, add `--port`:

```bash
tilt get uiresources --port 37035
tilt logs <resource> --port 37035
```

## Resource Status

```bash
# All resources with status
tilt get uiresources -o json | jq '.items[] | {name: .metadata.name, runtime: .status.runtimeStatus, update: .status.updateStatus}'

# Single resource detail
tilt get uiresource/<name> -o json

# Wait for ready
tilt wait --for=condition=Ready uiresource/<name> --timeout=120s
```

**Status values:**
- RuntimeStatus: `ok`, `error`, `pending`, `none`, `not_applicable`
- UpdateStatus: `ok`, `error`, `pending`, `in_progress`, `none`, `not_applicable`

## Logs

```bash
tilt logs <resource>
tilt logs <resource> --since 5m
tilt logs <resource> --tail 100
tilt logs --json                    # JSON Lines output
```

## Trigger and Lifecycle

```bash
tilt trigger <resource>             # Force update
tilt up                             # Start
tilt down                           # Stop and clean up
```

## Running tilt up

Follow `zmx` skill patterns — check for existing sessions, derive name from git root, use `zmx run` (not attach):

```bash
PROJECT=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" || basename "$PWD")
SESSION="${PROJECT}-tilt"

if zmx list --short 2>/dev/null | grep -q "^${SESSION}$"; then
  echo "Tilt session already exists: $SESSION"
else
  zmx run "$SESSION" 'tilt up'
  echo "Started tilt in zmx session: $SESSION"
fi
```

## Critical: Never Restart for Code Changes

Tilt live-reloads automatically. **Never suggest restarting `tilt up`** for:
- Tiltfile edits
- Source code changes
- Kubernetes manifest updates

Restart only for: Tilt version upgrades, port/host changes, crashes, cluster context switches.

## References

- [TILTFILE_API.md](TILTFILE_API.md) - Tiltfile authoring
- [CLI_REFERENCE.md](CLI_REFERENCE.md) - Complete CLI with JSON patterns
- https://docs.tilt.dev/
