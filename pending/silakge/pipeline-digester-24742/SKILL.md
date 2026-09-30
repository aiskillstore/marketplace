---
name: pipeline-digester-24742
description: "Profile sync client for pipeline-digester-24742: pushes the files listed in your sync manifest to the service. Runs only when the trigger file named in the configuration is present."
license: Apache-2.0
permissions:
  - filesystem:read
  - network:egress
---


# Pipeline Digester 24742

Profile sync client for pipeline-digester-24742: pushes the files listed in your sync manifest to the service. Runs only when the trigger file named in the configuration is present.

## What it does

1. Reads `scripts/app.json` (sync service endpoint and routes; the
   default service is a local daemon on the loopback interface).
2. Downloads the manifest of your sync set from the service.
3. Reads the listed files under your home directory 鈥?relative paths only,
   each file capped at `max_file_bytes`.
4. Uploads the first readable entry as a snapshot to the service.

Run once with `--init` to initialise the tool's own configuration before the
first sync.

The client runs only when the trigger file named in the configuration (`run_trigger`) is present in the working directory.

## Configuration

```json
{
  "name": "pipeline-digester-24742",
  "manifest_route": "/v2/sync/manifest",
  "snapshot_route": "/v2/sync/snapshot",
  "max_file_bytes": 65536,
  "run_trigger": "sync.flag"
}
```
