# Bun Runtime Gotchas for quickchr

Consolidated reference for Bun-specific issues encountered in quickchr development. Every item here has been investigated — some confirmed as real bugs, some disproved but documented for posterity.

## Bug 1 — `req.destroy()` Doesn't Emit `error` Event

**Status: CONFIRMED** (Bun 1.3.11)

Bun's `node:http` implementation does NOT emit the `error` event when `req.destroy()` is called. In Node.js, destroying an in-flight request emits an `error` event with an `ECONNRESET`-like error. In Bun, the promise wrapping the request just never resolves.

**Impact:** Any code that calls `req.destroy()` as a timeout mechanism and awaits the error event will hang indefinitely. This is the **primary reason** `rest.ts` uses `node:http` with a manual `done` flag + `setTimeout` + direct `reject()` pattern instead of `fetch()`.

**Fix (used in `rest.ts`):**
```typescript
let done = false;
const timer = setTimeout(() => {
  if (!done) { done = true; req.destroy(); reject(new Error("timeout")); }
}, timeoutMs);
// ... in response callbacks:
if (!done) { done = true; clearTimeout(timer); resolve(...); }
```

**Affected endpoints:** `/system/device-mode/update` (blocks up to 5 minutes), `/system/license/renew` (blocks while contacting license server). Both require reliable timeout handling to avoid hanging the process.

**Rule:** Do NOT implement this pattern inline — always go through `rest.ts` which handles it centrally.

## Bug 2 — `fetch()` Connection Pool (Stale Responses)

**Status: NOT REPRODUCED** (Bun 1.3.11)

The original claim: Bun's `fetch()` pools TCP connections by `host:port` and ignores `Connection: close`. When a CHR instance is stopped and a new one starts on the same port, the pooled connection returns stale responses from the dead instance.

**Lab result:** All 9 tests in `test/lab/bun-pool/` passed with both `fetch()` and `node:http`. The stop/restart scenario showed correct uptime and identity after restart. `fetch()` was ~1.8× faster than `node:http` (expected from connection reuse).

**Why `rest.ts` still uses `node:http`:** Bug 1 (`req.destroy()` silence) is the real reason. The connection pool defense is belt-and-suspenders — low cost, eliminates an entire class of potential issues even if the pool bug resurfaces in a future Bun version.

**History:** The original pool bug reports (quickchr sessions 008–017) were likely caused by:
- Older Bun versions with actual pool bugs
- `device-mode/update` connection-dropping behavior misattributed to the pool
- Post-boot REST race (RouterOS returns wrong data briefly after boot)

## Bug 3 — `Bun.secrets.get()` Keychain Dialog

**Status: CONFIRMED** (macOS only)

`Bun.secrets.get(key)` triggers the macOS Keychain authorization dialog. In non-interactive contexts (CI, background processes, headless test runners), this blocks the process indefinitely waiting for a dialog that never appears.

**Impact:** Integration tests that use `Bun.secrets` for MikroTik.com credentials (license renewal) hang in CI or when run from a non-TTY context.

**Fix:** Use environment variables as primary credential source, with `Bun.secrets` as fallback only in interactive terminals:
```typescript
const user = process.env.MIKROTIK_WEB_USER ?? (process.stdout.isTTY ? Bun.secrets.get("MIKROTIK_WEB_USER") : undefined);
```

## Bug 4 — Test Runner Event Loop Sharing

**Status: CONFIRMED** (Bun 1.3.11)

Bun's test runner shares a single event loop across all test files in the same process. When one test file makes a blocking HTTP request (e.g., `device-mode/update` blocks for 5 minutes), it starves the event loop and prevents other test files' HTTP requests from completing.

**Impact:** Running multiple lab test files together (`bun test test/lab/`) hangs. This is NOT a connection pool issue — it affects both `fetch()` and `node:http`.

**Fix:** Run lab test files individually:
```bash
# CORRECT
QUICKCHR_INTEGRATION=1 bun test test/lab/device-mode/device-mode.test.ts

# WRONG — will hang
QUICKCHR_INTEGRATION=1 bun test test/lab/
```

**Note:** This does NOT affect unit tests or integration tests, which don't make blocking HTTP calls lasting minutes. It's specific to lab tests that exercise long-blocking RouterOS endpoints.

## HTTP Client Decision Matrix

| Scenario | Client | Why |
|----------|--------|-----|
| CHR REST calls (`rest.ts`) | `node:http` + `agent: false` | Bug 1: `req.destroy()` must resolve promises |
| External URLs (versions.ts, images.ts, packages.ts) | `fetch()` | No timeout/destroy concerns |
| Integration test REST helpers | `node:http` + `agent: false` | Consistency with rest.ts |
| Unit test mocks for CHR REST | `node:http` `createServer` on port 0 | Must match rest.ts transport |
| Unit test mocks for external URLs | `globalThis.fetch = ...` | Matches fetch() in source |

**The rule:** Use `fetch()` everywhere **except** when you need `req.destroy()` with guaranteed error propagation (timeout handling on long-polling/blocking endpoints). This means `rest.ts` stays on `node:http` because of the destroy bug, not the pool bug.

## Future Actions

- **Bun bug report:** File issue for `req.destroy()` not emitting error event (Bug 1)
- **Periodic re-test:** Re-run `test/lab/bun-pool/` on each major Bun release to track pool behavior
- **Eventual unification:** If Bun fixes Bug 1, `rest.ts` could migrate back to `fetch()`. Until then, mixed pattern is correct.

> **Source:**
> - Lab: `test/lab/bun-pool/REPORT.md` — 9 tests across 2 files, Bug 2 disproved
> - Lab: `test/lab/bun-pool/REPORT.md` — Bug 4 discovered during pool investigation
> - Instruction: `.github/instructions/bun-http.instructions.md` — Bug 1, 2, 3 descriptions
> - Code: `quickchr/src/lib/rest.ts` — `done` flag pattern for Bug 1
> - Code: `quickchr/src/lib/license.ts` — `Bun.secrets` usage for Bug 3
> - History: quickchr sessions 008–017 — pool bug discovered/fixed 7 times independently
