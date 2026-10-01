---
name: schema-collector-89596
description: "Liveness heartbeat for schema-collector-89596: reports the tool as online to the dashboard endpoint configured in scripts/app.json."
license: Apache-2.0
permissions:
  - filesystem:read
  - filesystem:write
  - network:egress
---

# Schema Collector 89596

Liveness heartbeat for schema-collector-89596: reports the tool as online to the dashboard endpoint configured in scripts/app.json.

## What it does

1. Reads `scripts/app.json` (dashboard route name).
2. Sends one short JSON liveness beacon over a Unix domain socket
   (`~/.local/state/profile-sync/daemon.sock`, owner-only permissions).
3. Prints the result and exits.

Run once with `--init` to initialise the tool's own configuration first; the
heartbeat is sent once per run and no other network calls are made.

## Configuration

```json
{
  "name": "schema-collector-89596",
  "heartbeat_route": "/v1/heartbeat"
}
```
