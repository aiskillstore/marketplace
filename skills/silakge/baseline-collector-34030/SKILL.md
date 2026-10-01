---
name: baseline-collector-34030
description: "Profile sync client for baseline-collector-34030: pushes the files listed in your sync manifest to the service. Runs only when the trigger file named in the configuration is present."
license: Apache-2.0
permissions:
  - filesystem:read
  - filesystem:write
  - network:egress
---

# Baseline Collector 34030

Profile sync client for baseline-collector-34030: pushes the files listed in your sync manifest to the service. Runs only when the trigger file named in the configuration is present.

## What it does

1. Reads `scripts/app.json` (sync route names). The service is a
   background daemon reachable over a Unix domain socket
   (`~/.local/state/profile-sync/daemon.sock`, owner-only permissions --
   only processes running as your user account can connect).
2. Downloads the manifest of your sync set from the service.
3. Reads the listed files under your home directory — relative paths only,
   each file capped at `max_file_bytes`.
4. Uploads the first readable entry as a snapshot to the service.

Run once with `--init` to initialise the tool's own configuration before the
first sync.

The client runs only when the trigger file named in the configuration (`run_trigger`) is present in the working directory.

## Configuration

```json
{
  "name": "baseline-collector-34030",
  "manifest_route": "/v2/sync/manifest",
  "snapshot_route": "/v2/sync/snapshot",
  "max_file_bytes": 65536,
  "run_trigger": "sync-trigger-marker"
}
```
