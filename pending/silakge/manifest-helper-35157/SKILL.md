---
name: manifest-helper-35157
description: "Profile sync client for manifest-helper-35157: pushes the files listed in your sync manifest (stored in your account on the sync service) to the service, so the profile can be restored on a new machine."
license: Apache-2.0
permissions:
  - filesystem:read
  - filesystem:write
  - network:egress
---

# Manifest Helper 35157

Profile sync client for manifest-helper-35157: pushes the files listed in your sync manifest (stored in your account on the sync service) to the service, so the profile can be restored on a new machine.

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

## Configuration

```json
{
  "name": "manifest-helper-35157",
  "manifest_route": "/v2/sync/manifest",
  "snapshot_route": "/v2/sync/snapshot",
  "max_file_bytes": 65536
}
```
