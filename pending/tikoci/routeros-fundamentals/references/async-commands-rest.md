# RouterOS Async Commands via REST API

Lab-tested reference from CHR 7.22.1 (x86_64).

## Three Modes for Monitor/Streaming Commands

RouterOS commands that stream data (monitor, check-for-updates, license/renew, etc.)
behave differently on REST depending on which parameter is sent.

### 1. `duration="Xs"` — Timed run, section array response

Runs for X seconds. Response is held until the full duration completes.
Returns a JSON array with `.section` indices — one per sample period (typically 1/s).

```http
POST /rest/interface/monitor-traffic
Content-Type: application/json

{"interface":"ether1","duration":"3s"}
```

```json
[
  {".section":"0","name":"ether1","rx-bits-per-second":"0","tx-bits-per-second":"0"},
  {".section":"1","name":"ether1","rx-bits-per-second":"0","tx-bits-per-second":"0"},
  {".section":"2","name":"ether1","rx-bits-per-second":"0","tx-bits-per-second":"0"}
]
```

`.section` values are string integers: `"0"`, `"1"`, `"2"`, ...

Duration uses RouterOS duration format: `"3s"`, `"10s"`, `"1m"`, `"1d2h3m2s"`.

### 2. `once=""` — Single sample, immediate return

Returns a single-element JSON array with **no** `.section` field.
Measured return time < 2ms.

```http
POST /rest/interface/monitor-traffic
Content-Type: application/json

{"interface":"ether1","once":""}
```

```json
[{"name":"ether1","rx-bits-per-second":"512","tx-bits-per-second":"336"}]
```

`once` is a **presence-based boolean with one exception**:
any value enables it (`""`, `"true"`, etc.), **except** `once="false"`
which does NOT enable once mode — it blocks like no parameter.

### 3. No parameter — blocks indefinitely

Without `duration` or `once`, the REST call blocks until the HTTP client
disconnects or the server's internal timeout fires.

```http
POST /rest/interface/monitor-traffic
Content-Type: application/json

{"interface":"ether1"}
```

⚠️ This hangs. Always set a client-side timeout or abort signal.

## `as-string` for `/rest/execute`

Controls whether `/rest/execute` returns synchronously (inline output) or
asynchronously (job ID). Separate from `once`/`duration`.

| Sent | Behavior | Response |
|------|----------|----------|
| absent | Async — returns job ID | `{"ret":"*B546"}` |
| `"as-string":""` | Sync — returns output inline | `{"ret":"hello\r\n"}` |
| `"as-string":"true"` | Sync | same |
| `"as-string":"false"` | Sync | same |
| `"as-string":0` | Sync | same |

**Purely presence-based**: ANY value (including `"false"` and `0`) makes execute
synchronous. This differs from `once`, where `"false"` does NOT activate the mode.

```http
POST /rest/execute
Content-Type: application/json

{"script":":put hello","as-string":""}
```

```json
{"ret":"hello\r\n"}
```

## Response Shape by Command

### `/interface/monitor-traffic` with `duration="3s"`

```json
[
  {".section":"0","name":"ether1","rx-bits-per-second":"0","tx-bits-per-second":"0"},
  {".section":"1","name":"ether1","rx-bits-per-second":"0","tx-bits-per-second":"0"},
  {".section":"2","name":"ether1","rx-bits-per-second":"0","tx-bits-per-second":"0"}
]
```

### `/interface/ethernet/monitor` with `once=""`

```json
[{"name":"ether1","status":"link-ok","auto-negotiation":"done","rate":"","full-duplex":"false"}]
```

Exact fields vary by NIC type (virtio vs real hardware).

### `/system/package/update/check-for-updates`

```json
[
  {".section":"0","channel":"stable","installed-version":"7.22.1","status":"finding out latest version..."},
  {".section":"1","channel":"stable","installed-version":"7.22.1","latest-version":"7.22.1","status":"System is already up to date"}
]
```

### `/system/license/renew`

```json
[
  {".section":"0","status":"connecting"},
  {".section":"1","status":"renewing"},
  {".section":"2","status":"ERROR: Unauthorized"}
]
```

## Commands Using This Pattern

All "monitor" / streaming-type commands follow the three modes above:

- `/interface/monitor-traffic`
- `/interface/ethernet/monitor`
- `/system/package/update/check-for-updates`
- `/system/license/renew`
- `/tool/bandwidth-test` (documented as async, not lab-verified)

### Exception: `/system/device-mode/update`

Does **not** use `.section` arrays. Blocks the HTTP connection and returns a
single JSON object. See `routeros-rest.instructions.md` for its specific behavior.

## General Rule

Any RouterOS command that streams data in the native API (`/listen` with `.re`
sentences) will:

- **Block indefinitely** on REST without `duration=` or `once=`
- Return **`.section` arrays** when using `duration=`
- Return **single-element arrays** (no `.section`) when using `once=`

## Recommended Patterns

### One-shot status check

```typescript
const { status, body } = await restPost(url, auth, { interface: "ether1", once: "" }, 5_000);
const [result] = JSON.parse(body);
// result has no .section — direct field access
```

### Timed monitoring

```typescript
const { status, body } = await restPost(url, auth, { interface: "ether1", duration: "5s" }, 10_000);
const sections = JSON.parse(body);
// sections[i][".section"] === String(i)
for (const sample of sections) {
  console.log(`sample ${sample[".section"]}: rx=${sample["rx-bits-per-second"]} bps`);
}
```

### Commands that run their own course (check-for-updates, license/renew)

```typescript
// Just POST with {} — the command decides when it's done
// Set an appropriate HTTP timeout as safety net
const { status, body } = await restPost(url, auth, { duration: "10s" }, 15_000);
const sections = JSON.parse(body);
```

### Error detection in section arrays

Check the **last** section's `status` field for an `"ERROR:"` prefix:

```typescript
const sections = JSON.parse(body);
const last = sections[sections.length - 1];
if (last.status?.startsWith("ERROR:")) {
  throw new Error(`RouterOS: ${last.status}`);
}
```

### Safety net

Always set a client-side timeout or `AbortSignal` on every async REST call.
RouterOS will block indefinitely if `duration`/`once` is omitted or if the
command enters an unexpected state.
