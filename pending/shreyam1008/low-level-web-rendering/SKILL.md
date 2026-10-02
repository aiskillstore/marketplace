---
name: low-level-web-rendering
description: "Chooses between DOM, SVG, Canvas, WebGL, WebGPU, and worker rendering, or evaluates experimental HTML-in-Canvas. Use for renderer selection or architecture tradeoffs, not routine work in an already-selected GPU library."
---

# Low-Level Web Rendering

Choose the least specialized renderer that meets the product need. A GPU path is not automatically faster, and “painting without the DOM” is usually the wrong model for text, controls, or accessible application UI.

## Production decision router

| Need | Default | Why / boundary |
|---|---|---|
| Text, forms, navigation, selectable content | DOM + CSS | Native semantics, layout, accessibility, input, search, and internationalization. |
| Scalable diagrams with addressable elements | SVG | DOM semantics plus vector rendering; watch very large node counts. |
| Dense custom 2D pixels, drawing, charts, sprites | Canvas 2D | Immediate-mode rendering; supply a semantic DOM alternative for interaction. |
| Canvas work blocks input/scroll | OffscreenCanvas + Worker | Moves supported rendering and preparation off the main thread. Feature-detect. |
| Portable 3D/shaders | WebGL2 | Mature compatibility; use an engine unless raw API control is the product. |
| Compute, storage buffers, explicit modern GPU pipelines | WebGPU | Progressive enhancement with a WebGL/CPU fallback; see `webgpu`. |
| vgpu-based shader effects, procedural visuals, or custom 3D | Vercel vgpu over WebGPU | Use the installed version's docs; see `vgpu`. Preserve the surrounding semantic UI. |
| CPU-heavy parsing, simulation, codecs | Worker, then WASM if measured | WASM accelerates compute; it does not replace the DOM or choose the renderer. |
| Video frame decode/encode or transforms | WebCodecs when supported | Specialized media frames; retain `<video>` / server paths where compatibility matters. |

Apply the table in this order:

1. Preserve semantics first. If users read, edit, focus, select, search, translate, or automate it, keep a server-rendered or pre-rendered real DOM representation.
2. Measure the bottleneck: DOM count/layout, paint, main-thread JS, draw calls, fill rate, GPU time, transfers, or memory.
3. Change only the constrained layer. Moving pixels to a canvas does not fix unrelated data or scripting work.
4. Define fallback and recovery before adopting a less portable API.

## Browser frame pipeline

Each frame may perform:

`JavaScript → style → layout → paint → composite`

- Batch geometry reads before writes; reading layout after a mutation can force synchronous layout.
- Prefer transforms and opacity for motion when they avoid layout/paint, but verify in DevTools—compositing is an implementation decision, not a promise.
- Use `will-change` only around a measured transition; permanent layers consume memory.
- Reduce DOM/layout scope before replacing accessible markup with custom pixels (`contain`, `content-visibility`, virtualization, smaller subtrees).

## Canvas 2D baseline

Size the backing store from actual display pixels and update it when the element changes:

```js
function resizeCanvas(canvas, ctx) {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const width = Math.max(1, Math.round(rect.width * dpr));
  const height = Math.max(1, Math.round(rect.height * dpr));
  if (canvas.width === width && canvas.height === height) return;
  canvas.width = width;
  canvas.height = height;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
```

- Clamp DPR when fill rate, VRAM, memory, or power matters; expose quality as a product decision.
- Drive animation with `requestAnimationFrame`; use its timestamp and stop when nothing changes.
- Reuse paths, images, typed arrays, and state. Avoid allocations, text measurement, filters, and readbacks in hot loops.
- Layer static and dynamic content only when it reduces measured redraw cost.
- Use dirty rectangles only when tracking/overdraw complexity beats a full redraw in measurements.

## OffscreenCanvas and workers

```js
if ('transferControlToOffscreen' in canvas) {
  const offscreen = canvas.transferControlToOffscreen();
  worker.postMessage({ canvas: offscreen }, [offscreen]);
} else {
  startMainThreadRenderer(canvas);
}
```

- Keep input, accessibility, and DOM state on the main thread; send compact state snapshots or commands.
- Transfer ownership once. Do not copy large frame payloads when transferable buffers or shared state are justified.
- Worker support differs by context/API. Test the exact browser matrix; the fallback is part of the architecture.

## HTML-in-Canvas and CSS Paint: lab only

HTML-in-Canvas is a **WICG proposal**, not a production rendering dependency. The current explainer keeps real DOM descendants under `<canvas layoutsubtree>`, marks drawn elements with `drawable`, and uses `drawElementImage()`, `texElementSubImage2D()`, and `GPUQueue.drawElementImageToTexture()` for Canvas 2D, WebGL, and WebGPU. Earlier drafts used different names. It is not DOM-free painting, and vgpu does not require it.

Current status reviewed 9 September 2026:

- Chromium records the origin trial as M148–M150, subsequently extended through M154.
- Gecko and WebKit have no positive implementation signal.
- The API shape, privacy rules, hit testing, and accessibility behavior are still being developed.
- The explainer now includes `CanvasPaintEvent.changedElements`, transferable `ElementImage` snapshots for workers, and explicit element geometry updates. Snapshot drawing and DOM updates are distinct: mutations during `paint` appear in the next rendering update.
- WebGL/WebGPU experiments must update element geometry for hit testing and accessibility; 2D drawing can update it automatically. Captured snapshots do not make DOM layout or input independent of the main thread.
- Cross-origin embedded content and readback are restricted; consult the current privacy rules rather than treating this as unrestricted DOM screenshot access.

Rules:

- Use it only for a lab/prototype or a separately guarded enhancement.
- Feature-detect the exact method; never infer it from a Chrome version.
- Keep an equivalent semantic DOM path visible and meaningful when the experimental drawing method is absent; descendants used only as ordinary canvas fallback content are not enough in a canvas-capable browser.
- Production fallback: DOM overlay for interactive UI; DOM/SVG/Canvas 2D for 2D content; DOM overlay or established texture pipeline for WebGL/WebGPU scenes.
- Never make an origin-trial token or browser flag a normal-user requirement.

CSS Paint worklets are also a specialized progressive enhancement, not an escape hatch from DOM/CSS architecture. Keep an ordinary CSS background/border fallback and do not put content or essential state only in paint output.

## Accessibility and input

- Canvas pixels do not create semantics. Provide DOM controls, names, focus order, keyboard behavior, announcements, and equivalent text/data.
- Keep hit testing in one coordinate system and account for CSS size, backing-store size, camera transforms, zoom, and DPR.
- Preserve no-JS content, reduced motion, forced colors, text scaling, and high contrast outside custom rendering where possible.
- Do not duplicate an interactive control in both canvas and DOM accessibility trees.

## Measure before escalating

- Record a representative interaction in the Performance panel; identify scripting, layout, paint, raster, or GPU work.
- Count DOM nodes, draw calls, submissions, buffer/texture uploads, and frame allocations.
- Set explicit pixel, texture/VRAM, frame-time, and power budgets before increasing visual complexity.
- Test integrated GPUs, mobile thermal throttling, high-DPR displays, and background/hidden tabs.
- Compare against the simpler renderer. Keep the specialized path only when the user-visible win survives target-device testing.

## Ship gate

- [ ] The renderer matches the content’s semantic and interaction needs.
- [ ] The bottleneck was measured before the architecture changed.
- [ ] DPR, resize, visibility, context/device loss, and cleanup are handled.
- [ ] Unsupported browsers and no-JS users get a usable path, not an empty canvas.
- [ ] The main thread remains responsive and accessibility/reduced-motion behavior is verified.
- [ ] Experimental APIs are isolated and removable.

## Reference

- WHATWG: [HTML canvas element](https://html.spec.whatwg.org/multipage/canvas.html).
- W3C: [WebCodecs](https://www.w3.org/TR/webcodecs/) and [CSS Painting API](https://drafts.css-houdini.org/css-paint-api/).
- MDN: [Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API), [OffscreenCanvas](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas), and [WebCodecs](https://developer.mozilla.org/en-US/docs/Web/API/WebCodecs_API).
- WICG: [HTML-in-Canvas explainer](https://github.com/WICG/html-in-canvas).
- Chromium: [HTML-in-Canvas intent](https://groups.google.com/a/chromium.org/g/blink-dev/c/t_nGEmJ_v4s) and [experiment extension](https://groups.google.com/a/chromium.org/g/blink-dev/c/BpWbzJ9P22s).
- web.dev: rendering performance and avoiding large, complex layouts and layout thrashing.
