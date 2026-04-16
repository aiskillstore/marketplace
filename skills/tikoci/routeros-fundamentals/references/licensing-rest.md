# RouterOS `/system/license` REST API Reference

> Lab-verified on CHR 7.22.1 (x86_64). Every response shape below was captured via `curl` against a running instance.

## CHR License Tiers

| Level | Throughput Limit | Notes |
|-------|-----------------|-------|
| `free` | 1 Mbps per interface | Default for CHR |
| `p1` | 1 Gbps per interface | 60-day trial available via `/system/license/renew` |
| `p10` | 10 Gbps per interface | |
| `p-unlimited` | Unlimited | |

Trial upgrades to `p1` require valid MikroTik.com credentials and are limited per account.

## GET `/rest/system/license`

### Free Tier (default)

```json
{"level":"free","system-id":"7WwsTkLUKQG"}
```

Only two fields on a free CHR. No `expiration`, `nlevel`, or `deadline` keys exist.

After a trial upgrade, additional fields appear and `level` changes (e.g., to `"p1"`).

### Via `/rest/execute`

```json
{"ret":"  system-id: 7WwsTkLUKQG\r\n      level: free       "}
```

Standard RouterOS key-value text output with whitespace padding.

## POST `/rest/system/license/renew`

**Async command** — uses the `.section` array response pattern (same as `monitor-traffic`, `check-for-updates`). Blocks while contacting MikroTik license servers.

### Request Fields

| Field | Required | Description |
|-------|----------|-------------|
| `account` | Yes | MikroTik.com email address |
| `password` | Yes | MikroTik.com password |
| `level` | Yes | License level to request (e.g., `"p1"`) |
| `duration` | No | How long to wait for server response (RouterOS duration string: `"10s"`, `"15s"`) |

### Response Shapes

#### Missing credentials — HTTP 400

```bash
curl -u admin: http://127.0.0.1:9100/rest/system/license/renew \
  -X POST -H "Content-Type: application/json" \
  -d '{"level":"p1"}'
```

```json
{"detail":"missing =account=","error":400,"message":"Bad Request"}
```

Immediate response, no blocking.

#### Bad credentials — HTTP 200

```bash
curl -u admin: http://127.0.0.1:9100/rest/system/license/renew \
  -X POST -H "Content-Type: application/json" \
  -d '{"account":"user@example.com","password":"wrong","level":"p1","duration":"10s"}'
```

```json
[
  {".section":"0","status":"connecting"},
  {".section":"1","status":"renewing"},
  {".section":"2","status":"ERROR: Unauthorized"}
]
```

Takes ~2–5s to contact the server and receive the rejection.

#### Successful renewal — HTTP 200

```bash
curl -u admin: http://127.0.0.1:9100/rest/system/license/renew \
  -X POST -H "Content-Type: application/json" \
  -d '{"account":"valid@example.com","password":"correct","level":"p1","duration":"10s"}'
```

```json
[
  {".section":"0","status":"connecting"},
  {".section":"1","status":"done"}
]
```

After success, `GET /rest/system/license` reflects the new level.

#### Trial limit reached — HTTP 200

```json
[
  {".section":"0","status":"connecting"},
  {".section":"1","status":"renewing"},
  {".section":"2","status":"ERROR: Licensing Error: too many trial licences"}
]
```

#### Post-boot REST race (endpoint not initialized)

The response body contains system resource data instead of license data. This is the standard post-boot race condition — the endpoint has not finished initializing. Retry until the response matches the expected shape.

## Error Classification

All `.section` array responses arrive as **HTTP 200**, including errors. The `status` field in the final section entry determines success or failure:

| Last `status` value | Meaning | Action |
|---------------------|---------|--------|
| `"done"` | License accepted | Poll `GET /system/license` to verify level changed |
| `"connecting"` | Still in progress | Should not be final — indicates truncated response or missing `duration` |
| `"ERROR: Unauthorized"` | Bad MikroTik.com credentials | Throw immediately |
| `"ERROR: Licensing Error: too many trial licences"` | Account trial limit reached | Throw immediately |
| Any `"ERROR: ..."` | Server-side rejection | Throw immediately with the error text |

**Critical**: code MUST check the last section's `status` for an `"ERROR:"` prefix and throw immediately. Do NOT misclassify errors as "pending" and enter a polling loop — the error IS the final status.

## Recommended Pattern for quickchr

```
1. POST /rest/system/license/renew with duration="15s"
   Body: {"account":"...","password":"...","level":"p1","duration":"15s"}
2. Parse array response
3. Find the LAST entry (highest .section number)
4. Check its status field:
   - Starts with "ERROR:" → throw with the error message
   - Equals "done"        → poll GET /rest/system/license to verify level changed
5. If no credentials configured → skip renewal entirely (leave as free tier)
```

Use `restPost` from `rest.ts` (never `fetch()`) — see `bun-http.instructions.md` for the connection pool bug.
