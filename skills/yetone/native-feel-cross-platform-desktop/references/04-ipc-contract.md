# 04 — The IPC Contract is the Spine

T2 (*one schema, many languages*) and T6 (*cross boundaries intentionally*) converge in this file. The architecture is many processes glued together; the glue is the IPC contract; the quality of the glue is the quality of the app.

You have **four runtimes** that must speak to each other:

```
   Native shell  ──┐
   (Swift / C#)    │
                   ├──► Rust core (dylib via UniFFI)
                   │
                   ├──► Node backend (subprocess via stdio)
                   │
                   └──► WebView/React (via WebKit message handlers /
                                       WebView2 host objects)
```

Plus pairwise: Node ↔ React (the WebView posts messages, Node responds), Rust ↔ Node (events from the indexer reach the backend).

This is six possible edges. If each side hand-rolls its serialization and types, **types drift within a sprint**. Schema cracks lead to runtime errors that look like `undefined is not a function` or `failed to deserialize: missing field "x"` and no one can find them. Avoid this from day one.

---

## The principle: one declaration, generated clients

```
                  ┌──────────────────────┐
                  │  schema/             │
                  │    requests.proto    │ ← single source of truth
                  │    events.proto      │   (or .ts, or .udl,
                  │    types.ts          │    or .json schema)
                  └──────────┬───────────┘
                             │  codegen
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Swift types     C# types      TS types      Rust types
        (for shell)     (for shell)   (frontend+    (for core)
                                       backend)
```

When the schema changes, *all sides* fail to compile. Drift becomes impossible.

---

## Recommended toolchains, ranked

### Rust ↔ Swift / Kotlin / C# / Python: **UniFFI**

Mozilla's UniFFI consumes a Rust crate and a `.udl` (UniFFI Definition Language) file, then generates idiomatic bindings for Swift, Kotlin, C#, Python, Ruby. The generated Swift looks like:

```swift
let coordinator = Coordinator()
try coordinator.start(handler: MyEventHandler())
coordinator.send(request: req)
```

Verified in Raycast Beta — `libraycast_host.dylib` symbols contain `_UNIFFI_META_*` prefixes for:
- `Coordinator` interface (`new`, `start`, `stop`, `send`, `get_state`)
- `EventHandler` callback interface (`on_backend_log`, `on_failure`, `on_notification`, `on_request`)
- `LogHandler` callback (`on_log`, `on_panic`)
- `NativeSentryClient` interface (`new`, `add_breadcrumb`, `set_user_id`, `test_crash`)
- Enum `InboundRequestDestination` for request routing
- Errors `RequestError`, `SendError`, `StartError`, `StopError`

This is the proven pattern. Use UniFFI.

```toml
# Cargo.toml
[package]
name = "app_host"

[lib]
crate-type = ["cdylib", "staticlib"]

[dependencies]
uniffi = { version = "0.27", features = ["cli"] }

[build-dependencies]
uniffi = { version = "0.27", features = ["build"] }
```

```udl
// app_host.udl
namespace app_host {
    void init_logger(LogLevel level, LogHandler handler);
};

enum LogLevel { "Trace", "Debug", "Info", "Warn", "Error" };

interface Coordinator {
    constructor();
    [Throws=StartError]
    void start(EventHandler handler);
    [Throws=StopError]
    void stop();
    [Throws=SendError]
    void send(InboundRequest req);
    CoordinatorState get_state();
};

callback interface EventHandler {
    void on_request(OutboundRequest req);
    void on_notification(string payload);
    void on_backend_log(string line);
    void on_failure(string reason);
};

[Error]
enum StartError { "AlreadyRunning", "BackendSpawnFailed", "Io" };
```

Generated Swift uses native types (`String`, `[String]`, `Result<T, E>`). Generated C# uses `string`, `List<>`, exceptions. No marshalling glue in your hand-written code.

### Node ↔ Frontend: **WebKit message handlers (Mac) / Host objects (Windows)**

```swift
// Swift: register a handler
webViewConfig.userContentController.add(self, name: "appBridge")

// In WKScriptMessageHandler:
func userContentController(_ ucc: WKUserContentController, didReceive msg: WKScriptMessage) {
    guard msg.name == "appBridge", let body = msg.body as? [String: Any] else { return }
    coordinator.send(InboundRequest.fromDict(body))  // route to Rust
}
```

```csharp
// C#: register a host object
webView.CoreWebView2.AddHostObjectToScript("appBridge", bridge);
```

```ts
// React: a single typed sender
declare global {
  interface Window {
    webkit?: { messageHandlers: { appBridge: { postMessage(msg: unknown): void } } };
    chrome?: { webview: { hostObjects: { appBridge: AppBridge } } };
  }
}

export function sendToHost<T extends RequestKind>(req: Request<T>): Promise<Response<T>> {
  // serialize, route through whichever bridge exists, await response
}
```

The frontend doesn't care which platform. The host abstracts it.

### Node ↔ Rust: **length-prefixed JSON over stdio**, or **gRPC-over-uds**

If Rust is in-process via UniFFI (the recommended path), Node doesn't talk to Rust directly. The native shell mediates: `Node → shell → Rust → shell → Node`.

If Rust runs as its *own* subprocess (e.g., the file indexer is too crashy to share lifetime with the backend), use length-prefixed JSON on stdio. Don't roll a custom binary protocol unless profiling shows JSON is the bottleneck. It almost never is at the message rates apps generate.

---

## Request/response vs events

Two distinct shapes:

**Request/response** (synchronous semantics): "Search for 'foo'", "Save this note", "Run extension X". The caller awaits a response. Use a correlation ID.

**Events** (fire-and-forget pub/sub): "File index updated", "Network came online", "User changed theme". Multiple subscribers, no response.

Mixing them is the most common IPC design mistake. Have two distinct schemas:

```
schema/
  requests.{kind}.ts     // ResolveRequest<T> → ResolveResponse<T>
  events.{kind}.ts       // EventOf<T> — broadcast, no response
```

The transport may share a channel, but the schema doesn't. `RequestKind` and `EventKind` are disjoint enums.

---

## Versioning across runtimes

You will ship a Mac app at version N while a user is still on version N-1 of the Windows app. The frontend bundle and the native shell update on different cadences (auto-update of the shell is slower than CDN updates of the JS).

**Rule:** the IPC schema is versioned, every message carries the version it was generated against, and the receiving side either:
- Accepts the message if version matches or is older (forward compatibility);
- Returns a `VersionMismatch` error if the message is newer than what the receiver understands.

Practically: bump a `SCHEMA_VERSION` constant any time you make a breaking change. Add new fields as optional. Never remove or rename fields without a deprecation window.

---

## Anti-patterns

- **Stringly-typed message names.** `postMessage({type: "search", payload: ...})` with type checked at runtime only. Codegen the type union.
- **Hand-written marshalling per language.** Drift inevitable. Generate.
- **Shared mutable state across processes via a "memory file".** Just send a message.
- **Synchronous bridge calls from React.** `await sendToHost(...)` is fine; blocking on a sync return inside a React render is not.
- **Tracing only in production.** Trace every IPC call in development — log `{requestId, kind, durationMs}`. You'll find slow handlers you didn't know existed.

---

## What "good" looks like

When you've done this right, adding a new feature involves:
1. Edit one `.udl` or `.proto` file to add the new message types.
2. Run the codegen.
3. Implement the handler on the receiving side; the IDE autocompletes the fields.
4. Call it from the sending side; the IDE autocompletes the fields.

If adding a feature involves editing four runtimes by hand to keep types in sync, the IPC layer has failed.
