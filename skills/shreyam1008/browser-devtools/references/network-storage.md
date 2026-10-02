# Network requests and browser storage

Use this for failed/slow requests, authentication/cookies, stale data, redirects, caching, offline behavior, and streaming connections.

## Capture the actual transaction

Attach request/response/failure listeners or enable the tool's network capture before navigation and the failing action. In the [Network panel](https://developer.chrome.com/docs/devtools/network/), open the panel before reproduction and preserve navigation history when needed. Filter by the relevant endpoint/type/origin and examine the exact request ID; similar URLs and repeated fetches are not interchangeable.

Collect only details needed to distinguish the cause:

- Method, redacted URL/query/body shape, status or transport failure, redirect/preflight chain, resource type, frame/worker, and initiating source/stack.
- Relevant request/response headers and a bounded response excerpt. Inspect payload content type: a nominally successful HTML login page is not the expected JSON API result.
- Timing phases, transferred/decoded size, protocol and cache/service-worker source, when the backend exposes them. A long wait for the first byte alone does not prove slow application code on the server.
- The application-visible error and resulting UI state. `fetch` does not reject merely because an HTTP response has an error status; distinguish HTTP errors from transport/browser failures.

For CDP, relevant domains include `Network` and optionally `Fetch` for **intentional** interception. Correlate request/response and extra-info events by ID; redirect hops can reuse an ID and extra-info events can arrive out of order. Read a body only after its relevant response finishes; evicted, streamed, binary, redirected, or uncaptured bodies may be unavailable. Decode base64 only when the response says it is encoded. Do not infer an empty response from a failed body lookup.

Use the tool's current request-detail operation before dumping a whole HAR. Capture WebSocket frames or SSE event evidence only when relevant; preserve the distinction between handshake success and application-message success.

## Diagnose before replay

Follow the initiator into the request-building code and its state. Compare the observed request with the intended API contract. Inspect CORS/preflight and console diagnostics, credentials behavior, redirect destinations, and browser blocked reasons. Do not disable browser security to make a failure disappear.

Prefer repeating the authorized UI action in a test environment. A replay can create another order, send a message, refresh a token, or invalidate state. Preserve the user-authorized target and operation; do not assume a method is harmless solely because it is GET. A terminal HTTP request omits browser CORS, service workers, cookie policies, and possibly the current session; its success is separate evidence.

When request editing/interception is useful and authorized, label it as a controlled experiment. Apply the narrow route, avoid forwarding secrets to a different host, and restore interception/headers afterward. A mocked success is not proof the real API works.

## Storage, cookies, and caches

Inspect the intended origin/frame and partition. Start with names, metadata, sizes, versions, and selected diagnostic values rather than exporting all session data.

| Surface | Useful evidence |
|---|---|
| Cookies | Domain/path, expiry, Secure/HttpOnly/SameSite, partition, inclusion/exclusion reasons, Set-Cookie acceptance |
| localStorage/sessionStorage | Origin/frame, relevant key, value shape/version, reads/writes in initiating code |
| IndexedDB | Database/store/index schema, relevant bounded read-only records, upgrade/version state |
| Cache Storage | Owned cache names and matching resource/response metadata |
| Service worker | Scope, active/waiting version, controlling worker, intercept/cache behavior |
| HTTP cache/CDN/application cache | Response headers and source; distinguish each layer |

`document.cookie` cannot inspect HttpOnly cookies. Page script cannot generally inspect cross-origin frames/storage. Use the authorized browser tool for scoped cookie metadata and blocked reasons; an absent cookie is not proof the server failed to set one.

Prefer browser tooling for IndexedDB inspection. `indexedDB.open()` can create a database, so it is not an unconditional read-only probe; verify an existing database and avoid upgrade callbacks or writes. Cache APIs and service-worker operations can also change persistent state. Do not clear an entire origin or unregister a worker as the first diagnostic step.

Keep a warm/normal baseline before a labelled cache-disabled or service-worker-bypass comparison. Bypassing the HTTP cache does not bypass every cache layer. If a clean profile fixes the issue, identify the responsible stored state before proposing a scoped reset. Verify the repair with the real worker/cache conditions restored.

Export HAR only when useful, with the backend's sensitive-data controls checked. Sanitization may not remove secrets from query strings or bodies; inspect/redact before sharing.

Primary references: [Network reference](https://developer.chrome.com/docs/devtools/network/reference/), [cookies](https://developer.chrome.com/docs/devtools/application/cookies), [Application panel](https://developer.chrome.com/docs/devtools/application/), [PWA and service-worker debugging](https://developer.chrome.com/docs/devtools/progressive-web-apps), [CDP Network](https://chromedevtools.github.io/devtools-protocol/tot/Network/) (match the target schema).
