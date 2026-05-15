# 02 — The Four-Layer Architecture

This is the structural recommendation. Every layer exists because removing it loses something the other three cannot recover.

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: NATIVE HOST SHELL                                         │
│    macOS:    Swift + AppKit  (Xcode project)                        │
│    Windows:  C#    + WPF / WinUI 3  (Visual Studio project)         │
│    Owns:     NSWindow / Win32 HWND, global hotkeys, menubar /       │
│              system tray, Dock/Taskbar presence, file associations, │
│              accessibility integration, materials (Liquid Glass /   │
│              Acrylic), WebView instantiation & lifecycle, Node      │
│              backend supervision, crash reporting, auto-updater.    │
│    Size:     ~5–15 MB on disk, ~40 MB resident.                     │
└─────────────────────────────────────────────────────────────────────┘
            │ (loads)                       │ (spawns)
            ▼                               ▼
┌────────────────────────────┐  ┌──────────────────────────────────────┐
│  LAYER 2: WEBVIEW          │  │  LAYER 3: NODE BACKEND               │
│    macOS:    WKWebView     │  │    Single long-lived Node process    │
│    Windows:  WebView2      │  │    Bundled Node runtime              │
│    Renders: React + TS,    │  │    Owns: DB (SQLite), extension      │
│      one entry point per   │  │      runtime, network, business      │
│      window (main, ai-     │  │      logic, AI orchestration.        │
│      chat, settings, …)    │  │    Native helpers: .node addons for  │
│    Size: ~50 MB baseline,  │  │      perf-critical CPU work.         │
│      ~150 MB with app code │  │    Size: ~12 MB baseline,            │
│                            │  │      ~150–200 MB with app code.      │
└────────────────────────────┘  └──────────────────────────────────────┘
            │                               │
            └───────────┬───────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 4: RUST CORE                                                 │
│    Compiled to a dylib (libapp_host.dylib) AND/OR helper processes  │
│    Exposed via UniFFI (Rust ↔ Swift / Kotlin / C# / Python)         │
│    Hosts: filesystem indexer, calculator engine, crypto, cloud      │
│      sync schema, any code that must be shared with mobile or       │
│      with the server (same Rust → iOS app + backend service).       │
│    Bonus: Cross-platform without two implementations.               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Per-layer rationale

### Layer 1 — Native shell

**Why this can't move into the WebView:** Global hotkeys, system tray icons, menu bar extras, accessibility roles, transparency materials, drag-and-drop with file URLs, Dock click handlers, URL scheme registration, file type associations, multi-display awareness, native notifications — none of these are reachable from WebKit/WebView2 without a host process. The shell exists to do what the WebView *cannot*.

**Why two implementations is correct:** macOS and Windows have fundamentally different window/material/tray models. Cross-platform abstractions over them (Electron, Tauri) leak in exactly the places you care about for native feel. Two ~10kLoC shells in their idiomatic languages will, on net, be smaller and clearer than one 30kLoC abstraction.

**What to actually write here:**
- `WindowController` / `WindowManager` for each window kind (main launcher, settings, AI chat, etc.).
- `HotkeyManager` listening on `CGEventTap` (mac) / `RegisterHotKey` (Windows).
- `WebViewHost` wrapping `WKWebView` / `WebView2` with the survival flags from `references/03-webview-survival.md`.
- `BackendSupervisor` spawning Node, watching stdin/stdout, restarting on crash, plumbing logs.
- `BridgeCoordinator` running the IPC ↔ UniFFI wiring (see `references/04-ipc-contract.md`).

### Layer 2 — WebView + React

**Why a WebView and not native UI:** Two reasons.

1. *Maintenance halving.* A single React/TS UI codebase running on both OSes versus two parallel UIs (AppKit + WPF/WinUI). Every feature ships twice if you go native.
2. *Iteration speed.* Hot module reload in 200 ms vs Xcode rebuild in 30 s. Compounded over a year of design iteration, this is the difference between shipping and not.

**Why the *system* WebView, not a bundled Chromium:** WebKit ships with macOS, WebView2 ships with Windows. You inherit their security updates without bundling a 200 MB browser. You pay the cost of two engines (KHTML-descended Safari/WebKit and Chromium-descended Edge/WebView2) instead of one — meaning CSS quirks must be tested on both. This is a real tax. Pay it; the alternative is bundling Chromium and inheriting Electron's footprint.

**Multi-entry-point per window:** Each window kind (main launcher, AI chat, notes, settings) gets its own HTML entry point and its own bundle. They share a chunk graph but launch independently. This:
- Lets cold-start of small windows be small.
- Lets the shell tear down a window's WebView fully on close without disturbing others.
- Avoids one giant SPA that always pays for everything.

Verified in Raycast Beta: `main-window.html`, `ai-chat-window.html`, `settings-window.html`, `notes-window.html`, `feedback-window.html`, `theme-studio-window.html`, `welcome-window.html` — seven entry points.

### Layer 3 — Node backend

**Why Node and not pure native:** Two reasons.

1. *Plugin/extension ecosystem.* If your app accepts third-party extensions, JS/TS is the only choice that gives you a low-barrier ecosystem. Native plugins (Swift, .NET) have ~100× fewer authors.
2. *Code sharing.* Your AI integration, your API clients, your business logic — all of it is happiest in TS, where it can share types with the frontend through the IPC schema.

**Why a single long-lived process and not per-window backends:** Database connections, network keep-alive, expensive imports, AI session state. Per-window backends would re-pay these costs every time a window opens. Single process amortizes.

**When to use a native `.node` addon vs Rust subprocess:**
- `.node` addon (Node-API or N-API): for tight, frequent calls from JS where serialization cost dominates. Examples seen in Raycast: `Calculator.node`, `fs-utils.darwin-arm64.node`, `indexer.darwin-arm64.node`, `data.darwin-arm64.node`.
- Rust subprocess: for long-running work that can be torn down independently, or for work that needs cross-process isolation (e.g., a crashy parser shouldn't kill the backend). Spawn it, talk over stdio with a length-prefixed protocol.

### Layer 4 — Rust core

**Why Rust and not C++:** Memory safety + the UniFFI tooling, which generates typed bindings to Swift, Kotlin, C#, Python from a single Rust source. C++ would force you to hand-maintain four bindings or use SWIG, both worse.

**What goes in Rust:**
- Anything CPU-bound where JS would heat the laptop. (File indexing, fuzzy matching, syntax highlighting if you don't trust the WebView's.)
- Anything cross-platform where a single implementation must work identically on Mac/Win/iOS.
- Anything that has a server counterpart (same Rust crates power your backend service → schema can't drift).
- Anything that needs subprocess isolation for crash resilience.

**Verified in Raycast Beta:** `libraycast_host.dylib` is a Rust dylib using UniFFI. Its exported metadata symbols spell out the bridge:
- `Coordinator` (interface): `new`, `start`, `stop`, `send`, `get_state`
- `EventHandler` (callback interface from Swift back to Rust): `on_backend_log`, `on_failure`, `on_notification`, `on_request`
- `LogHandler` (callback): `on_log`, `on_panic`
- `NativeSentryClient` (interface): `new`, `add_breadcrumb`, `set_user_id`, `test_crash`
- `InboundRequestDestination` (enum): request routing
- Errors: `RequestError`, `SendError`, `StartError`, `StopError`, `NativeSentryClientError`

This is exactly the pattern this skill recommends. The Rust core is the *coordinator* — it knows how to start/stop the system, route requests between the WebView and Node backend, and bubble events back to the native shell.

---

## Decision: how many layers does *your* app need?

You may not need all four. A reduced version:

| You have… | You still need |
|---|---|
| A simple utility with no plugin ecosystem | Layer 1 + Layer 2 only. Skip Node; talk straight from the shell to a small Rust core. |
| An app with plugins/extensions | Layers 1, 2, 3. Rust is optional. |
| An app with mobile counterpart or server-side schema parity | All four. Layer 4 is the cross-platform tissue. |
| A launcher / search-heavy app | All four. The indexer must be Rust or it will be slow. |

But: each *added* layer also adds a process boundary, an IPC contract, an error path, and a memory cost. Add layers reluctantly. If you can do without Node, skip Node. If your Rust core is 200 LoC, inline it as an `.node` addon instead of a subprocess.

---

## What this architecture is NOT good for

- **Games / 3D / real-time canvas.** WebView GPU pipelines are not what you want.
- **Apps that must launch in <50 ms.** Cold start of WebView + Node baseline is ~200 ms minimum; visible UI ~400 ms. If you're building a "press hotkey, blink, gone" app like a clipboard popup, prewarm or pick a different stack.
- **Single-platform apps.** If you're macOS-only, just build native. The cross-platform tax isn't worth it.
- **Apps with strict memory budgets (<150 MB).** The WebView + Node floor is real. T8 (*separate baseline from margin*): this floor is baseline, not yours to negotiate.

If any of these match, the answer is "don't use this architecture." Tell the user.
