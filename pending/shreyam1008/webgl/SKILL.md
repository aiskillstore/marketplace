---
name: webgl
description: "Implements or debugs raw WebGL/WebGL2 contexts, GLSL, buffers, textures, and GL draw calls. Use for direct WebGL API work, not generic 3D tasks owned by a higher-level renderer."
---

# WebGL

Low-level GPU rendering in the browser. The mental model: minimize state changes and draw calls, move work to the GPU, and never block the main thread.

## Context setup

```js
const gl = canvas.getContext('webgl2', {
  alpha: false,              // skip compositing transparency if unneeded
  antialias: true,
  powerPreference: 'high-performance', // optional performance/power hint
  preserveDrawingBuffer: false, // true is slow; only for readback/screenshots
});
if (!gl) throw new Error('WebGL2 unavailable; show the product fallback.');
```

- Prefer **WebGL2** (instancing, VAOs, MRT, 3D textures are core). Fall back to WebGL1 only if you must.
- Handle context loss: call `event.preventDefault()` in `webglcontextlost` to allow restoration, stop rendering, and recreate resources on `webglcontextrestored` before restarting.

## Confirm which GPU you actually got

```js
const ext = gl.getExtension('WEBGL_debug_renderer_info');
if (ext) console.log(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL));
```

The extension may be unavailable for privacy reasons. `powerPreference` is a hint; it does not guarantee a discrete GPU, and renderer strings do not establish performance. Measure on target hardware.

## DPR & viewport

```js
const dpr = Math.min(window.devicePixelRatio, 2); // clamp; full DPR is costly
canvas.width  = Math.floor(canvas.clientWidth  * dpr);
canvas.height = Math.floor(canvas.clientHeight * dpr);
gl.viewport(0, 0, canvas.width, canvas.height);
```

## The cost model (profile to find the dominant cost)

1. **Draw calls** — batch geometry, use instancing, sort by material to avoid redundant binds.
2. **State changes** — `useProgram`, `bindTexture`, `bindBuffer`, enabling/disabling are not free. Group draws that share state.
3. **Fragment shader work** — overdraw and expensive per-pixel math. Cull, depth-sort opaque front-to-back, avoid huge `discard` usage.
4. **Bandwidth** — texture size/format. Use mipmaps and compressed textures.

## Geometry & buffers

- Upload geometry once into VBOs; use **VAOs** to capture attribute state and rebind in one call.
- Use **indexed** drawing (`drawElements`) with element buffers.
- Use `gl.drawArraysInstanced` / `drawElementsInstanced` for repeated objects (one call, N copies).
- Set buffer usage hints correctly: `STATIC_DRAW` for immutable, `DYNAMIC_DRAW` for frequently updated.

## Shaders

- Compile/link programs once at init, never per frame. Cache uniform locations.
- Prefer `mediump` precision in fragment shaders unless you need `highp`.
- Minimize branching and dependent texture reads; avoid `discard` where possible (it defeats early-Z).
- Move constant math to the vertex shader or to the CPU as uniforms.

## Textures

- Power-of-two enables full mipmap/wrap support in WebGL1; WebGL2 relaxes this but mipmaps still help.
- Generate mipmaps for anything minified; set sensible min/mag filters.
- Use compressed formats (`WEBGL_compressed_texture_*`, KTX2/Basis) to cut VRAM and bandwidth.
- Use texture atlases to reduce binds and enable batching.

## The render loop

```js
function frame(t) {
  // update (use real delta time)
  // clear only what you need
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
  // draw, grouped by program/material
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```

- Always drive with `requestAnimationFrame`. Skip rendering entirely when nothing changed (on-demand).
- Avoid synchronous GPU→CPU reads (`readPixels`, `getError` in hot paths) — they stall the pipeline.
- Offload heavy CPU prep to a worker; consider `OffscreenCanvas` for worker-side rendering.

## Debug & profile

- `gl.getError()` only while debugging (it forces a flush) — strip from hot paths.
- Use the browser's WebGL/Spector.js inspector to count draw calls and inspect state.
- Watch for: too many programs bound per frame, per-frame buffer reallocation, uncompressed large textures.

## When to step up

- Need compute, storage buffers, or modern GPU features → use the `webgpu` skill, but keep WebGL2 as the production fallback unless the product controls its browser/GPU matrix.
- Building a full scene graph → use Three.js / React Three Fiber instead of hand-rolling (see the `react-three-fiber` skill).

WebGL is also the fallback boundary for an experimental HTML-in-Canvas texture path. The explainer reviewed on 9 September 2026 uses `texElementSubImage2D()`, replacing earlier `texElementImage2D()` examples. Keep this experimental method feature-detected and preserve semantic DOM or an established texture pipeline when it is unavailable. See `low-level-web-rendering`.

## Reference

- MDN: [WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices), [renderer info extension](https://developer.mozilla.org/en-US/docs/Web/API/WEBGL_debug_renderer_info); WebGL2 Fundamentals.
- Khronos WebGL best practices.
