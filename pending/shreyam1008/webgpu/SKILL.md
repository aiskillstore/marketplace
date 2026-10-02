---
name: webgpu
description: "Implements or debugs raw browser WebGPU/WGSL pipelines, compute, buffers, textures, and device loss. Use for direct GPU API work; vgpu-library APIs and R3F scenes have separate workflows."
---

# WebGPU

WebGPU is a browser-mediated, sandboxed graphics and compute API. It is not “GPU Direct,” and it is not the default answer for a visual web page.

## Decide before building

Use WebGPU when at least one of these is true:

- the workload needs compute shaders, storage buffers, or modern explicit GPU pipelines;
- measured CPU or draw-call overhead is the bottleneck in a substantial WebGL workload;
- a renderer already has a tested WebGPU backend and a real fallback;
- the product controls its target browsers and GPUs.

Prefer something simpler when it fits:

- semantic UI, text, forms, and ordinary motion → DOM/CSS;
- custom 2D drawing → Canvas 2D, optionally in a worker;
- portable 3D with broad compatibility → WebGL2 or an engine with WebGL fallback;
- CPU-heavy parsing, codecs, or simulation → Worker/WASM before moving unrelated work to the GPU.

Recent major browser releases include WebGPU, but MDN still marks it **limited availability / not Baseline** across browser, OS, and device combinations. Treat it as progressive enhancement unless the product has an explicit tested support contract.

## Capability gate, not browser detection

Initialize asynchronously and make fallback a first-class result:

```ts
type GpuStart = { device: GPUDevice; adapter: GPUAdapter } | null;

export async function startWebGpu(): Promise<GpuStart> {
  if (!navigator.gpu) return null;

  try {
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) return null; // unsupported, disabled, blocked, or no usable adapter
    const device = await adapter.requestDevice();
    device.lost.then((info) => {
      console.warn(`WebGPU device lost: ${info.reason}`, info.message);
      // Stop submissions, dispose app-side state, then retry or enter fallback.
    });
    return { adapter, device };
  } catch {
    return null;
  }
}
```

- Check every optional `feature` and required `limit`; never assume the development GPU is typical.
- Request only capabilities the workload uses. A request exceeding adapter limits rejects.
- `powerPreference` is a hint, not a guarantee of a discrete GPU or higher performance.
- WebGPU requires a secure context. Development exceptions do not replace production HTTPS.

## Architecture that survives production

- Give one application service ownership of the adapter, device, queue, caches, and loss recovery.
- Keep render/compute code independent from product state. Pass compact frame data across the boundary.
- Create pipelines, bind-group layouts, samplers, and stable resources outside the frame loop.
- Label devices, buffers, textures, pipelines, and passes; validation messages become actionable.
- Make resource lifetime explicit. Destroy large buffers/textures when they are no longer reusable; do not rely on JavaScript GC to understand GPU memory pressure.
- Keep a working Canvas/WebGL/CPU path behind the same high-level renderer contract when broad support matters.

## Buffers, textures, and transfers

- Choose usage flags at creation time and keep them as narrow as practical.
- Reuse buffers and textures; avoid per-frame allocation and pipeline compilation.
- Use `queue.writeBuffer()` / `writeTexture()` for bounded uploads. Stage or ring-buffer sustained streaming after measuring.
- Avoid GPU-to-CPU readback in the frame loop; it introduces synchronization and often erases the GPU win.
- Respect alignment, row-pitch, format, feature, and limit requirements from the active device—not a hard-coded “common GPU.”
- Put frequently reused resources into stable bind groups. Rebuild only when their bindings actually change.

## WGSL and pipelines

- Keep WGSL deterministic and reviewable; do not construct shaders from untrusted strings.
- Validate shader modules and use `createRenderPipelineAsync()` / `createComputePipelineAsync()` when compilation latency could block interaction.
- Keep shader interfaces and bind-group layouts versioned together.
- Prefer fewer pipeline variants. Branching in a shader can be cheaper than a combinatorial pipeline cache, but benchmark the real workload.
- Capture validation errors around synchronous fallible setup work. Async pipeline creation rejects separately, so handle that rejection rather than leaving an error scope open:

```ts
device.pushErrorScope('validation');
const pipeline = device.createRenderPipeline(descriptor);
const validationError = await device.popErrorScope();
if (validationError) throw validationError;
```

Also listen for `uncapturederror` during development; do not use it instead of scoped handling for expected failures.

## Canvas and frame loop

```ts
const context = canvas.getContext('webgpu');
if (!context) return useFallback();

const format = navigator.gpu.getPreferredCanvasFormat();
context.configure({ device, format, alphaMode: 'premultiplied' });
```

- Resize the backing store from observed device pixels and clamp resolution when fill-rate is expensive.
- Reconfigure after meaningful size/device changes; avoid doing so every frame.
- Acquire the current texture only for the frame being encoded.
- Encode related passes together and minimize queue submissions; submission boundaries are not free.
- Render on demand when the scene is static. For continuous animation, use `requestAnimationFrame` and its timestamp.

## Measure the GPU path

- Benchmark the WebGPU path against its fallback on target devices. WebGPU can be slower than WebGL for small or poorly batched workloads.
- Separate CPU frame time, GPU time, upload/readback cost, pipeline creation, and memory pressure.
- Use timestamp queries only after checking the feature; keep a non-timestamp profiling path.
- Watch for pipeline churn, redundant bind groups, too many submissions, oversized textures, overdraw, and hidden readbacks.
- Test integrated GPUs, battery-saving modes, blocklisted adapters, software fallbacks, and device loss—not only a desktop discrete GPU.

## Experimental HTML-in-Canvas boundary

The proposed `GPUQueue.drawElementImageToTexture()` HTML-in-Canvas path (formerly `copyElementImageToTexture()`) is not a production WebGPU primitive yet. The explainer was rechecked on 9 September 2026; it remains separate from the core WebGPU specification. Keep semantic DOM or another renderer as the shipping path and feature-detect experiments against the current draft. See `low-level-web-rendering` for the routing and fallback rule. For Vercel's vgpu library and shader-based visual UI, use `vgpu`; it does not depend on HTML-in-Canvas.

## Ship gate

- [ ] WebGPU is feature-detected and HTTPS is guaranteed.
- [ ] Required features/limits are checked before device creation.
- [ ] Adapter absence, device loss, and validation errors reach a usable fallback.
- [ ] Resources and pipelines are reused; cleanup is explicit.
- [ ] No synchronous readback sits in the hot path.
- [ ] Accessibility and product UI remain in semantic DOM where appropriate.
- [ ] Performance was measured on representative integrated and discrete GPUs.

## Reference

- W3C: [WebGPU specification](https://www.w3.org/TR/webgpu/) and [WGSL specification](https://www.w3.org/TR/WGSL/).
- GPU for the Web: [WebGPU explainer](https://gpuweb.github.io/gpuweb/explainer/) and [samples](https://webgpu.github.io/webgpu-samples/).
- MDN: [WebGPU API](https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API), including compatibility and secure-context status.
- Chrome for Developers: [WebGPU overview](https://developer.chrome.com/docs/web-platform/webgpu/overview), [troubleshooting](https://developer.chrome.com/docs/web-platform/webgpu/troubleshooting-tips), and [WebGL-to-WebGPU migration](https://developer.chrome.com/docs/web-platform/webgpu/from-webgl-to-webgpu).
