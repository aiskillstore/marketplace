# Device-Mode REST API Behavior

Lab-tested reference for `/system/device-mode` REST endpoints on CHR 7.22.1 (x86_64). Supplements `device-mode.md` (which covers modes and feature matrix) with REST-specific behavior, blocking semantics, and the quickchr automation pattern.

## GET /rest/system/device-mode

Returns a **flat JSON object** (not an array). All values are strings — booleans are `"true"`/`"false"`, numbers are `"0"`, `"1"`, etc.

```json
{
  "mode": "advanced",
  "allowed-versions": "",
  "flagged": "false",
  "flagging-enabled": "true",
  "attempt-count": "0",
  "scheduler": "true",
  "socks": "true",
  "fetch": "true",
  "pptp": "true",
  "l2tp": "true",
  "bandwidth-test": "true",
  "traffic-gen": "false",
  "sniffer": "true",
  "ipsec": "true",
  "romon": "true",
  "proxy": "true",
  "hotspot": "true",
  "smb": "true",
  "email": "true",
  "zerotier": "true",
  "container": "false",
  "install-any-version": "false",
  "partitions": "false",
  "routerboard": "false"
}
```

24 attributes total. Default CHR mode is `"advanced"` with most features `"true"`.

### .proplist

Supports field selection:

```
GET /rest/system/device-mode?.proplist=mode,container
→ {"mode":"advanced","container":"false"}
```

### /print Does Not Work

`/rest/system/device-mode/print` returns **HTTP 500**. This is a singleton resource — it has no `/print` action via REST. Use plain GET instead.

## POST /rest/system/device-mode/update — Blocking Endpoint

**This endpoint ALWAYS blocks the HTTP response.** It does not return until either:

1. A power-cycle confirms the change, or
2. The `activation-timeout` expires (default: 5 minutes)

This is the critical fact for automation: even a no-op update (same values, empty `{}` body) blocks. While the update is pending, **all REST endpoints become unresponsive** — the entire HTTP server stalls.

### activation-timeout

Controls how long RouterOS waits for the power-cycle confirmation.

- Range: `10s` to `1d` (RouterOS duration string format)
- Default: `5m`
- Examples: `"30s"`, `"5m"`, `"1d"`

Always send a short timeout for automation:

```json
POST /rest/system/device-mode/update
{"container":"true","activation-timeout":"30s"}
```

## quickchr Automation Pattern

The recommended flow used in `src/lib/device-mode.ts`:

```
1. POST /rest/system/device-mode/update
   - Include desired changes + activation-timeout=30s
   - Fire and forget (don't await — it blocks)
   - Use a 300s safety timeout on the HTTP request

2. Sleep 2s
   - Let RouterOS register the pending change

3. Hard power-cycle via QEMU monitor
   - Send `system_reset` to the QEMU monitor socket
   - This is the "physical confirmation" RouterOS requires
   - The pending HTTP request dies with ECONNRESET (suppress it)

4. Wait for boot
   - Poll GET / until RouterOS responds

5. Verify the change
   - GET /rest/system/device-mode
   - Check that the requested fields match
   - attempt-count should be "0" (resets on successful power-cycle)
```

**Key implementation detail:** `startDeviceModeUpdate()` returns a promise but callers race it against a sleep — if the POST hasn't resolved in 2s, RouterOS entered blocking state and needs a power-cycle. The ECONNRESET from killing the connection must be caught and suppressed.

## Timeout Expiry (No Power-Cycle)

If `activation-timeout` expires without a power-cycle, RouterOS returns:

```json
HTTP 400
{"detail":"update canceled","error":400,"message":"Bad Request"}
```

RouterOS resumes normal operation after this. The `attempt-count` increments by 1.

## attempt-count Behavior

- Increments by 1 on every failed/canceled attempt
- Resets to `"0"` only on successful power-cycle confirmation
- Lab tested up to count=12 with no REST-visible limit
- The docs mention "only three times" — this appears to be a CLI-only restriction or approximation; REST continues to accept and block on update requests regardless of count

## flagged vs attempt-count

These are **independent mechanisms**:

- `flagged` — set by RouterOS at boot when it detects suspicious configuration (scripts, fetch, etc.). Not related to update attempts.
- `attempt-count` — tracks pending-change failures. Not related to flagging.

To clear `flagged`:

```json
POST /rest/system/device-mode/update
{"flagged":"no","activation-timeout":"30s"}
```

Then power-cycle to confirm.

## Error Responses (Immediate — No Blocking)

These errors return immediately without blocking:

| Condition | Response |
|---|---|
| Invalid mode value | `{"detail":"input does not match any value of mode","error":400}` |
| Unknown parameter | `{"detail":"unknown parameter nonexistent","error":400}` |
| Bad timeout value | `{"detail":"value of activation-timeout is out of range (00:00:10 .. 1d00:00:00)","error":400}` |

All are HTTP 400. The endpoint only blocks when the request is valid and accepted.

## Via /rest/execute

Update commands block the same way:

```json
POST /rest/execute
{"script":"/system/device-mode/update container=yes activation-timeout=30s","as-string":""}
```

Print works normally (no blocking):

```json
POST /rest/execute
{"script":"/system/device-mode/print","as-string":""}
→ {"ret":"          mode: advanced\n  ...key: value text..."}
```

## Via SSH

SSH commands have the same blocking behavior for updates:

```bash
ssh -o BatchMode=yes -p 9102 admin@127.0.0.1 "/system/device-mode/print"
# Returns immediately with key:value text

ssh -o BatchMode=yes -p 9102 admin@127.0.0.1 "/system/device-mode/update container=yes"
# Blocks until power-cycle or timeout
```

## Post-Boot REST Race

`GET /rest/system/device-mode` is subject to the same post-boot race as all endpoints. Briefly after boot it may return wrong data (e.g., `/system/resource` body). The `readDeviceMode()` function in quickchr guards against this by checking for `board-name` / `architecture-name` keys that indicate resource data leaked into the response.

When polling after a power-cycle, use a deadline loop:

```typescript
const deadline = Date.now() + 20_000;
while (Date.now() < deadline) {
  const { status, body } = await restGet(url, auth, 5_000);
  if (status >= 200 && status < 300) {
    const data = JSON.parse(body);
    if (data && typeof data === "object" && !Array.isArray(data) && "mode" in data) {
      return data;
    }
  }
  await Bun.sleep(1_000);
}
```

> **Source:** Lab testing on CHR 7.22.1 x86_64, verified via curl and quickchr integration tests.
