# 05 — Memory: Reading the Map Honestly

T4 (*performance is a property of perception*) and T8 (*separate baseline from margin*) live in this file. Before optimizing memory, learn what the numbers actually mean and which costs you can and cannot influence.

---

## The baseline you cannot beat

For a native shell + system WebView + Node backend architecture:

| Component | Minimum resident (warm) | Notes |
|---|---|---|
| Native shell (Swift/AppKit or C#/WPF) | ~30–40 MB | Mostly shared frameworks. |
| WKWebView (one window, blank page) | ~50 MB | This is *the WebKit content process plus GPU and networking helpers, attributed back to your app*. |
| WebView2 (one window, blank page) | ~80–120 MB | Chromium baseline is heavier than WebKit. |
| Node.js runtime (no app code) | ~12 MB | Just `node` cold. |

So your floor on macOS is ~90 MB, on Windows ~130 MB, *before* you write a line of app code. **This is not negotiable.** This is the *baseline* in T8's sense — rented from the platform, not yours to optimize. If you came here to make a 50 MB cross-platform desktop app, you are in the wrong architecture.

Typical *real* numbers for a mature app like Raycast:

| State | Typical resident |
|---|---|
| Window hidden, backend idle | ~350–450 MB |
| Window visible, search active | ~500–700 MB |
| AI chat with long context | ~800 MB – 1.2 GB |

For comparison, Raycast v1 (pure native AppKit) was 200–300 MB. So **the cross-platform tax is ~150 MB**. You pay it to halve your engineering team's work.

---

## Six things Activity Monitor lies about

### 1. Compressed memory is counted as resident, but isn't

macOS compresses inactive pages. A page that says it occupies 4 KB may, after compression, occupy 0.5 KB. Activity Monitor's "Memory" column counts the *uncompressed* size. If half your dirty pages are compressed, the real cost is half of what you see.

How to actually measure: `vm_stat` shows compressor pages. `footprint` (Xcode's Instruments) shows compressed vs dirty separately.

### 2. Shared frameworks are charged to every process

WKWebView links AppKit, Foundation, JavaScriptCore, ~200 MB of system frameworks. Activity Monitor charges this to *every* process using them. So if you have a Swift shell, a WebContent process, a GPU helper, and a Networking process, all using AppKit, the AppKit memory is counted **four times** in the per-process column. The real cost is once.

This is why "the WebContent process is using 200 MB!" panics are almost always wrong. Of that 200 MB, ~150 is shared code mapped into every Mac process; the real per-process cost is ~50.

### 3. Clean pages cost nothing under pressure

A "clean" page is a memory page backed by a file on disk (mapped executable code, mapped resources). The OS can drop it instantly and re-load it from disk if needed. Its cost under memory pressure: **zero**. Yet Activity Monitor counts it as resident.

The pages that actually cost something are *dirty* pages — anonymous heap allocations that have no on-disk backing. Those are what the OS must page out to swap if pressure rises.

To see the dirty/clean split on macOS:
```
heap <PID>           # see object counts
vmmap --summary <PID>  # see dirty vs swapped vs clean
```

### 4. Memory Pressure ≠ Memory Usage

macOS exposes a "memory pressure" graph in Activity Monitor. **This is the only metric that matters.** Green = the system is fine. Yellow = swapping is starting. Red = you're hurting.

A process can show 1 GB of "memory" and contribute zero to pressure (if it's mostly clean + compressed). Another can show 200 MB and contribute massively (if it's all dirty anonymous heap).

When a user says "your app uses too much memory," ask: "is the memory pressure graph red?" If no, the problem is perception, not reality.

### 5. WebKit/Chromium GPU helper has unusual accounting

The GPU helper process holds video RAM (VRAM) mappings that show up as RAM in Activity Monitor. They're not real RAM costs; they're GPU resources. Subtract this from your accounting.

### 6. Snapshots are misleading; profile over time

A single Activity Monitor reading at one moment is meaningless. Memory bobs up and down as garbage collectors run and caches fill. Trust trends over minutes, not snapshots.

---

## How to actually reduce memory cost

Once you've stopped chasing shadows (T4 — perception over measurement), here is what *actually* moves the needle, in order of impact:

### 1. Tear down secondary windows aggressively

Don't keep `AI Chat`, `Notes`, `Settings`, `Theme Studio` etc. alive when the user isn't using them. Destroy the `WKWebView` / `WebView2` instance on close. Pay the cold-start cost on reopen.

Trade-off explicitly: cold-start latency for those windows goes from ~0 ms (warm) to ~300 ms (cold). Acceptable for rarely-used windows. Not acceptable for the main launcher — keep that prewarmed.

This is exactly what Raycast does: "Windows like AI Chat and Notes are torn down more aggressively to keep memory in check, which means there's a short delay when you open them cold."

### 2. Lazy-load extensions

Extensions (third-party plugins) should not load on launch. Load on first invocation. Unload after idle.

### 3. Bundle splitting per window

Each window kind has its own HTML entry and its own bundle. The launcher should not load the AI chat's dependencies. The settings page should not pull in the markdown renderer.

Verified in Raycast Beta: seven HTML entry points (`main-window.html`, `ai-chat-window.html`, etc.) with separate JS bundles per entry. The chunk graph is shared (so common modules load once via `modulepreload`), but each window only loads what it needs.

### 4. Avoid keeping the search index in JS heap

Search indices are the worst things to put in V8 heap. They are *the* feature people complain about being slow and large. Move the index to a Rust subprocess. JS sends a query string, Rust replies with row IDs. The index never crosses the IPC boundary.

### 5. Use Node addons for image/binary work

Image processing, encryption, file scanning in JS heap leaks memory and is slow. Use `.node` addons (Rust or C++ via N-API).

Verified in Raycast Beta backend: `Calculator.node`, `data.darwin-arm64.node`, `fs-utils.darwin-arm64.node`, `indexer.darwin-arm64.node`, plus `SoulverCore.framework` (a *native* math/calculation framework loaded by the Node backend!).

### 6. Quit Node when idle for long enough

A 12 MB Node baseline doesn't sound like much, but if you can quit it and respawn on demand for a 5-second cold start, do it. Especially for menu-bar apps where the user may not interact for hours.

### 7. Don't ship sourcemaps in production

`.map` files are huge. Strip them. Send them to your crash reporter (Sentry) separately.

---

## What NOT to do

- **Set `--max-old-space-size=...` super low on Node.** This will cause OOM crashes under load. Memory budget is bounded by your workload, not by a fixed cap.
- **Force GC manually.** V8's GC is smarter than your timer.
- **Bundle a Chromium build to "control memory."** It will use more, not less, than the system WebView.
- **Migrate things to native to "save memory" without measurement.** Migration cost is high. Measure first; if your dirty heap is dominated by 3 React components, fix those, not the architecture.

---

## A debugging recipe

When the user says "memory is too high":

1. Check **memory pressure**. If green, stop. The problem is perception. Educate them with this file.
2. Run `vmmap --summary <PID>`. Identify dirty page hotspots.
3. If dirty pages are in WebContent: profile the React heap. Likely a leaky subscription or a giant array in a global store.
4. If dirty pages are in Node: take a heap snapshot (`--inspect`, then Chrome DevTools). Likely a cache without eviction.
5. If dirty pages are in the Rust core: use `valgrind --tool=massif` or `dhat`. Likely a Vec you forgot to bound.
6. Only after 1–5: discuss architectural changes.
