---
name: web-performance
description: "Diagnoses browser loading, Core Web Vitals, main-thread work, and layout/paint bottlenecks. Use for a slow page or measured browser-performance issue; isolated React renders and GPU passes have specialist workflows."
---

# Web Performance

Two distinct problems: **load fast** (get to useful content quickly) and **stay responsive and smooth** at the active display refresh rate. Measure first—optimize the dominant cost, not what's easy.

## Core Web Vitals (the targets)

- **LCP** (Largest Contentful Paint) ≤ 2.5s — largest element visible. Fix: optimize the hero image/font, preconnect, reduce render-blocking CSS/JS, server response time.
- **INP** (Interaction to Next Paint) ≤ 200ms — input delay + handler work + presentation delay. Fix the measured phase rather than assuming every INP problem is a long task.
- **CLS** (Cumulative Layout Shift) ≤ 0.1 — visual stability. Fix: set `width`/`height`/`aspect-ratio` on media, reserve space for dynamic content, preload fonts.

Evaluate these thresholds at the **75th percentile of field visits**, segmented by mobile and desktop. A fast Lighthouse run does not prove healthy field Core Web Vitals.

## The frame budget

At 60Hz, one frame is **~16.7ms**; at 120Hz it is **~8.3ms**. The actual budget follows the display and must leave browser/OS headroom for JavaScript, style, layout, paint, and composite work.

```
JS → Style → Layout → Paint → Composite
            (transform/opacity may avoid earlier stages; verify)
```

## Load fast

- Ship less JS: code-split by route, lazy-load below-the-fold and heavy libs, tree-shake, audit the bundle.
- Don't block the critical path: `defer`/`module` scripts, inline critical CSS, lazy non-critical CSS.
- Prioritize the measured LCP resource (`fetchpriority="high"` where useful). Preload only a few critical, late-discovered resources; unnecessary preloads compete with the real critical path.
- Images: right-sized, modern formats (AVIF/WebP), `srcset`/`<picture>`, `loading="lazy"` off-screen.
- Fonts: subset and self-host when justified; choose `font-display: swap`, `fallback`, or `optional` by product needs, and align fallback metrics to limit layout shift. Preload only a truly critical font.
- Stream/SSR where possible so first paint has content.

## Stay smooth at the active refresh rate

- Prefer **`transform`/`opacity`** for hot motion, then verify the trace; compositor promotion is not guaranteed. Avoid width/top/left in frame-by-frame loops.
- Drive visual updates with **`requestAnimationFrame`**, never `setInterval`/`setTimeout`. Use the rAF timestamp / a fixed timestep; don't assume 60Hz.
- **Avoid layout thrash**: batch DOM reads, then writes. Reading `offsetWidth`/`getBoundingClientRect` after a write forces synchronous layout.
- If profiling shows GC pressure in a hot loop, reduce transient allocations; object pools, typed arrays, and manual reuse are targeted fixes, not universal defaults.

## Keep interactions responsive

- Break long tasks (>50ms) into chunks; **yield** between them:
  - Feature-detect `scheduler.yield()` / `scheduler.postTask()` and retain a timer-based fallback where support is missing.
  - Use `requestIdleCallback` only for deferrable work; required work needs a supported fallback or a timeout because idle callbacks may be delayed indefinitely.
- Move heavy compute to a **Web Worker** (parsing, image/audio, physics, search indexing). Use `OffscreenCanvas` to render in a worker.
- Consider **WebAssembly** for measured CPU kernels (see `wasm-rust`). Preserve an existing GPU renderer when investigating its cost; evaluate a renderer change only when the bottleneck and support requirements justify it.
- Debounce/throttle scroll/resize/pointer handlers; use passive event listeners.

## Game-loop pattern

```js
let last = performance.now();
const maxDt = 0.05;
function loop(now) {
  const dt = Math.min((now - last) / 1000, maxDt);
  last = now;
  update(dt);   // use a bounded fixed-step accumulator for physics
  render();     // mutate transforms / draw to canvas
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

document.addEventListener('visibilitychange', () => {
  if (!document.hidden) last = performance.now(); // rAF pauses in hidden tabs
});
```

## Measure (don't guess)

- **PageSpeed Insights** combines CrUX field data (when available) with a Lighthouse lab run; read them separately.
- **Performance panel**: record an interaction, find long tasks, forced reflows, dropped frames; check the FPS/GPU track.
- **web-vitals** library for real-user (field) INP/LCP/CLS.
- DevTools Performance Monitor for live CPU/DOM/listener counts.
- For GPU paths, measure representative integrated/discrete GPUs, DPR, VRAM/texture budgets, power modes, upload/readback cost, and context/device loss—not just desktop FPS.

## Triage checklist

- [ ] Measured; dominant cost identified (load vs runtime).
- [ ] The LCP resource is discovered early and appropriately prioritized; preload only when measurement shows critical late discovery.
- [ ] Hot animations prefer transform/opacity and are verified in a trace; updates use rAF.
- [ ] No layout thrash (reads batched before writes).
- [ ] Long tasks split/yielded; heavy compute in a worker/WASM.
- [ ] Media sized to prevent CLS.

## Reference

- web.dev: Core Web Vitals, "Optimize long tasks", "Rendering performance", RAIL.
- `GoogleChrome/modern-web-guidance-src` (performance guides); Addy Osmani's web performance writing.
- MDN: `requestAnimationFrame`, `OffscreenCanvas`, Performance API.
- Chrome for Developers: `scheduler.postTask`/`scheduler.yield`, Web Workers.
