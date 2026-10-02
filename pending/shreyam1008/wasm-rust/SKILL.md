---
name: wasm-rust
description: "Implements Rust/WebAssembly modules and wasm-bindgen integration. Use for measured CPU kernels, wasm packaging, and JS-WASM transfers; not GPU shader execution or DOM styling."
---

# Rust + WebAssembly

Run near-native Rust in the browser. WASM wins for **compute-heavy, long-running** work — not for DOM-bound or trivial tasks where the JS↔WASM boundary cost dominates.

## When WASM is worth it

- ✅ Heavy number crunching: image/audio/video processing, physics, simulation, compression, crypto, parsers, geometry.
- ✅ Workloads that run for milliseconds+ per call and touch large typed-array buffers.
- ✅ Code you want to share with a native/Rust backend.
- ❌ Small/occasional ops where boundary marshaling > the compute saved.
- ❌ DOM-heavy logic (WASM can't touch the DOM directly; it calls back into JS).

Rule of thumb: **fewer, bigger calls** beat many tiny calls.

WASM and WebGPU solve different bottlenecks. WASM runs CPU kernels in browser-managed linear memory; WebGPU submits sandboxed work to a browser-managed GPU device. Neither is “GPU Direct.” Profile first, keep transfer boundaries coarse, and preserve a JavaScript/CPU fallback when the support contract requires it. Use `low-level-web-rendering` to choose the renderer and `webgpu` for GPU pipelines.

## Toolchain

```bash
rustup target add wasm32-unknown-unknown
cargo install wasm-pack       # bundles wasm + JS glue + TS types

wasm-pack build --target web --release
# outputs pkg/: .wasm, JS bindings, .d.ts
```

- `--target web` → native ESM import; `--target bundler` → for webpack/Vite; `--target nodejs` for Node.
- `wasm-bindgen` generates the JS glue and TypeScript types automatically.
- Keep the crate, generated glue, and CLI versions compatible. The reviewed 0.2.128 release adds `web-sys` OffscreenCanvas overloads for WebGL texture uploads; confirm the selected `web-sys` version and feature flags before using them. This does not add browser support by itself.

## Minimal crate

```toml
# Cargo.toml
[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"

[profile.release]
opt-level = 3
lto = true          # smaller, faster binary
codegen-units = 1
```

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn sum(data: &[f32]) -> f32 {   // JS Float32Array is copied into WASM memory
    data.iter().sum()
}
```

```js
import init, { sum } from './pkg/my_crate.js';
await init();
sum(new Float32Array([1, 2, 3]));   // 6
```

## The boundary is the bottleneck — minimize copies

- Passing JS arrays as `&[T]` / `Vec<T>` **copies** data across the boundary. For big/hot buffers, keep data in WASM linear memory and operate in place.
- For zero-copy access, allocate and own the buffer in WASM, expose its pointer/length with an explicit lifetime contract, and construct a JS typed-array view over `memory.buffer`. Recreate views after memory growth; do not retain views across Rust operations that free or reallocate that buffer.
- Don't call a tiny WASM function in a tight JS loop — move the loop into Rust.
- Strings cost encoding/decoding; prefer numeric buffers for hot paths.

```rust
#[wasm_bindgen]
pub fn process_in_place(buf: &mut [u8]) { /* mutate the temporary WASM copy */ }
```

When called with a JS typed array, `&mut [u8]` bindings copy in and copy the mutations back on return. This convenience API is not zero-copy.

## Go faster: SIMD & threads

- **SIMD**: benchmark `RUSTFLAGS="-C target-feature=+simd128"` for vectorizable loops. Speedup depends on the algorithm, memory traffic, and compiler; feature-detect or provide a non-SIMD build for unsupported targets.
- **Threads**: `wasm-bindgen-rayon` + shared memory needs cross-origin isolation headers:
  - `Cross-Origin-Opener-Policy: same-origin`
  - `Cross-Origin-Embedder-Policy: require-corp`
- Run WASM in a **Web Worker** to keep the main thread responsive; `OffscreenCanvas` if it renders.

## Size & loading

- `wasm-opt` (via wasm-pack) shrinks output; enable `lto` + `opt-level = "z"`/`3`.
- Start with the default allocator; change it only after measuring size, speed, and maintenance tradeoffs.
- Serve `.wasm` with `Content-Type: application/wasm` so streaming compilation (`instantiateStreaming`) works.
- Lazy-load the module; `await init()` before first use.

## Debugging

- `console_error_panic_hook` to surface Rust panics in the JS console.
- `web-sys` / `js-sys` for typed access to browser/JS APIs from Rust.
- Profile with the browser Performance panel; confirm the boundary isn't the cost (look for many short WASM calls).

## Reference

- The wasm-bindgen guide: [number slices](https://wasm-bindgen.github.io/wasm-bindgen/reference/types/number-slices.html); `wasm-pack` docs; Rust and WebAssembly book.
- Vite: `vite-plugin-wasm` / `vite-plugin-top-level-await` for clean integration.
