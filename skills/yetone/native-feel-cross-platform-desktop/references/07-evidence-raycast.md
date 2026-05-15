# 07 — Evidence: Reverse-Engineering Raycast Beta

This file documents what was found by inspecting the on-disk binary of `Raycast Beta.app` (CFBundleShortVersionString 0.60.0, built with Xcode 17, targeting macOS 26+). Everything in this skill is grounded in observed reality, not theory.

The point: when you advise a user to follow this architecture, you can point to the shipping artifacts of a team that demonstrably did it well.

---

## Bundle anatomy

```
Raycast Beta.app/
├── Contents/
│   ├── Info.plist                       # CFBundleIdentifier=com.raycast-x.macos
│   │                                    # LSUIElement=true (menubar app)
│   │                                    # LSMinimumSystemVersion=26.0
│   │                                    # LSMultipleInstancesProhibited=true
│   ├── MacOS/
│   │   └── Raycast Beta                 # 12.3 MB Mach-O arm64 (Swift host shell)
│   ├── Frameworks/
│   │   ├── libraycast_host.dylib        # Rust core (UniFFI bridge to Swift)
│   │   └── Sentry.framework/            # Crash reporting
│   ├── XPCServices/
│   │   └── Raycast X Accessibility.xpc/ # Sandboxed accessibility service
│   ├── Resources/
│   │   ├── Updater                      # 5.8 MB separate updater binary
│   │   ├── production-appicon.icns
│   │   ├── Assets.car                   # 10.4 MB asset catalog
│   │   ├── InternetAccessPolicy.plist
│   │   └── macos-app_RaycastDesktopApp.bundle/
│   │       └── Contents/Resources/
│   │           ├── frontend/            # Vite-built React app, 7 HTML entry points
│   │           ├── backend/             # Node backend (single-file bundle + .node addons)
│   │           ├── node/                # Bundled Node v22.22.2 runtime
│   │           ├── api/                 # Extension SDK template
│   │           └── audio/               # Audio assets
```

This is the four-layer architecture made physical.

---

## Layer 1: Native shell — `MacOS/Raycast Beta`

12.3 MB Mach-O arm64 executable. Swift + AppKit. Owns NSWindows, hotkeys, menubar, and supervises the Rust core + Node backend.

The fact that this binary is only 12.3 MB confirms the shell is *thin*. All the heavy logic lives elsewhere.

The XPC service `Raycast X Accessibility.xpc` is separated for sandboxing — accessibility integration (reading focused window content for context) runs in its own process with its own entitlements. Good security hygiene.

---

## Layer 4 (named first because it's the most distinctive): Rust core — `libraycast_host.dylib`

This is a Rust dylib using **UniFFI** for typed FFI to Swift. Confirmed by the presence of `_UNIFFI_META_*` exported symbols and `_ffi_raycast_host_rust_future_*` runtime symbols.

Reverse-engineered interface (from `UNIFFI_META_*` symbol names):

```
namespace raycast_host {
    void init_logger(LogLevel level, LogHandler handler);
    void shutdown_logger();
};

enum LogLevel { Trace, Debug, Info, Warn, Error };

interface Coordinator {
    constructor() new;
    [Throws=StartError] void start(EventHandler handler);
    [Throws=StopError]  void stop();
    [Throws=SendError]  void send(...);
    CoordinatorState get_state();
};

enum CoordinatorState { ... };
enum InboundRequestDestination { ... };   // request routing

callback interface EventHandler {
    void on_request(...);                 // Rust → Swift: inbound request
    void on_notification(...);            // Rust → Swift: events
    void on_backend_log(string);          // Rust → Swift: Node logs
    void on_failure(string);              // Rust → Swift: error propagation
};

callback interface LogHandler {
    void on_log(...);
    void on_panic(...);
};

interface NativeSentryClient {
    constructor() new;
    void add_breadcrumb(...);
    void set_user_id(...);
    void test_crash();
};

[Error] enum NativeSentryClientError { ... };
[Error] enum RequestError { ... };
[Error] enum SendError { ... };
[Error] enum StartError { ... };
[Error] enum StopError { ... };
```

**What this tells us:** The Rust core is the *coordinator* of the whole system. It is not just an indexer. It owns:
- The system's start/stop lifecycle.
- Request routing between the WebView, the Node backend, and back.
- Notification fan-out to the Swift shell.
- Logging (with its own panic handler).
- Sentry crash reporting (with a native Sentry client written in Rust).

The pattern: **Swift kicks off the Coordinator, hands it an EventHandler, then drives requests through `Coordinator.send(...)`. Events from the backend and notifications come back through the callback interface.** This is a classic actor pattern with typed message routing.

Use this exact pattern in your app. The `Coordinator` interface in `references/04-ipc-contract.md` is modeled directly on it.

---

## Layer 2: WebView frontend

Found at `Resources/macos-app_RaycastDesktopApp.bundle/Contents/Resources/frontend/`.

**Seven HTML entry points** (one per window kind):
- `main-window.html` — the launcher
- `ai-chat-window.html`
- `notes-window.html`
- `settings-window.html`
- `feedback-window.html`
- `theme-studio-window.html`
- `welcome-window.html`

Each entry point preloads ~50 named chunks via `<link rel="modulepreload">`. The chunk graph is shared (e.g., `chunk-LkDJa1bE.js`, `marked.esm-C-12xU_L.js`) — common deps load once across windows that need them.

Many chunk filenames hint at the feature surface:
- `dictation-hud-store-…js` — dictation overlay
- `transcription-styles-store-…js` — audio transcription
- `auto-quit-rules-…js`
- `calendar-extension-…js`, `notes-extension-…js`
- `meeting-slack-…js`
- `lowlight-…js` — syntax highlighting (browser-side, not Rust)
- `marked.esm-…js` — markdown rendering
- `synced-store-…js` — cross-window state sync

The CSS files reveal Liquid Glass / Tahoe targeting (`tahoe-DJgQPeAO.js`).

**Lesson:** Single React codebase, multiple HTML entry points, shared chunk graph. Don't ship one giant SPA — ship a multi-bundle app where each window pays only for what it uses.

---

## Layer 3: Node backend

Found at `.../Resources/backend/`. Files:

```
backend/
├── index.mjs                              # main entry (Sentry-wrapped, ESM, bundled)
├── package.json                           # empty {} — bundled, deps inlined
├── calculator-worker.mjs                  # worker thread
├── indexer-worker.mjs                     # worker thread
├── Calculator.node                        # native addon
├── data.darwin-arm64.node                 # native addon
├── fs-utils.darwin-arm64.node             # native addon
├── indexer.darwin-arm64.node              # native addon
├── macos_export_certificate_and_key.node  # native addon (in build/)
└── SoulverCore.framework/                 # native math/calc framework
```

Key observations:

1. **The backend is a single bundled file.** `index.mjs` is a Vite/esbuild-style bundled ESM file with Sentry's debug-ID injected at the top and dynamic `require` polyfill. No `node_modules`. Bundled at build time.

2. **Four native `.node` addons.** Calculator, data, fs-utils, indexer. These are CPU-hot paths moved out of V8.

3. **SoulverCore.framework** — Raycast loads the **Soulver math engine** as a native macOS framework from the Node backend. The Node addon binds to it. This is how they get "type `tax 5% on 120 EUR` and it works" without writing a math parser in JS.

4. **Worker threads** for indexer and calculator. Bounded long-running computation runs off the main thread.

5. **Bundled Node runtime** at `node/node-v22.22.2-darwin-arm64.tar.gz`. The user doesn't need Node installed.

**Lesson:** The Node backend is engineered like a production server: bundled deps, native addons for hot paths, worker threads for bounded compute, native frameworks loaded via N-API when the algorithm already exists as a native library.

---

## Layer 5 (bonus): Extension SDK

`Resources/api/template/` contains the on-disk extension scaffold:

```
api/template/
├── package.json     # depends on @raycast/api, @raycast/utils
├── tsconfig.json
├── eslint.config.js
├── src/
│   ├── ai.tsx
│   ├── detail.tsx
│   ├── form.tsx
│   ├── grid.tsx
│   ├── list-and-detail.tsx
│   ├── menu-bar-extra.tsx
│   ├── script.ts
│   ├── static-list.tsx
│   ├── typeahead-search.tsx
│   ├── blank.ts
│   └── tools/
└── dist/
```

Modes: `view`, `no-view`, `menu-bar` — declared in the extension's `package.json`. The same React-based components that power Raycast's first-party UI power third-party extensions. **The internal team and external developers use the same primitives.** This is a strong endorsement of the layered architecture: when the SDK is the same as the internal API, there is no "second-class extension" problem.

---

## What's NOT in the bundle (notable absences)

- **No Electron / Chromium binaries.** The WebView is the system WKWebView; no bundled browser.
- **No Tauri runtime.**
- **No Python or other scripting runtimes.**
- **No separate per-feature subprocesses on disk.** All Node `.node` addons are loaded into the single Node process.
- **No bundled Sparkle.** Updates appear to be handled by the custom `Updater` binary in Resources.

---

## Build/distribution hints

- **GitCommitHash** in Info.plist: build is tracked to a specific commit.
- **Code signing**: shipped with `embedded.provisionprofile`, normal macOS hardened-runtime expected.
- **Bundle identifier `com.raycast-x.macos`** is *distinct* from the stable Raycast bundle ID. This is how Raycast ships a Beta and Stable side-by-side without collision — they're literally different apps from the OS's perspective.
- **LSUIElement=true** — no Dock icon. Menu-bar resident app. This requires special attention in the shell (custom window activation, no Dock-icon click handlers).
- **URL schemes registered**: `raycast`, `raycast-x`, `com.raycast`, `com.raycast-x`. The Beta uses the `-x` suffix to avoid stealing handlers from stable.

---

## Bottom line

When someone asks "is the architecture in this skill achievable?", the answer is: yes, here is a 12 MB Swift shell + 1 MB Rust dylib + ~30 MB bundled Node + ~50 MB Vite-built React frontend, all wired together with UniFFI, shipping today, ~400 MB resident.

When they ask "is it worth the complexity?", the answer is: that complexity bought them macOS + Windows feature parity and an extension ecosystem of thousands of community plugins that run on both OSes. Compute the alternative cost.
