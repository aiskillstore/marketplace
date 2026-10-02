---
name: vgpu
description: "Builds shader effects, materials, particles, and 3D visual surfaces with Vercel vgpu. Use when vgpu is requested or installed, including integration and GPU debugging. Read version-matched docs; do not migrate other renderers implicitly."
---

# vgpu: shaders, 3D, and visual UI

Use vgpu to create the visual surface the task needs while keeping the surrounding application usable. It renders GPU pixels into a canvas; it does not provide HTML layout, accessible controls, text selection, or an automatic WebGL fallback. HTML-in-Canvas is a separate experimental proposal.

## Resolve the project's version first

Inspect the owning workspace's manifest and lockfile. Use its installed executable without downloading a different version:

```sh
npm exec --no -- vgpu --version
npm exec --no -- vgpu docs --help
npm exec --no -- vgpu docs cat getting-started.md
```

Use the equivalent local executable for the project's package manager, such as `pnpm exec vgpu` or a resolved `node_modules/.bin/vgpu`. Bare `bunx vgpu` / `npx vgpu` can fetch a package, so they are not reliable checks of what the project has installed.

If dependencies are missing, preserve the version selected by the lockfile. Restore them when installation is part of the task, or read that exact version's bundled docs with `bunx vgpu@<selected-version> docs …`. For a new dependency with no version selected, resolve the stable tag and record the resulting version; do not choose a prerelease merely because the repository defaults to a development branch.

**Reference check: 9 September 2026.** npm stable was `0.4.1`; the development branch already used different WGSL loader entry points. This is a review baseline, not a version to force on future projects. Installed docs and exports take precedence over hosted examples, remembered APIs, and this skill's API hints.

## Find the right implementation

Start with `vgpu docs find "<topic>"`, then read the returned guide or symbol path through the same local executable. Documentation filenames and commands can change; use that version's help when a path is missing.

| Requested result | Starting point |
|---|---|
| Animated gradients, grain, distortion, liquid/glass effects, raymarching | Fullscreen fragment effects; `concepts-effects.md` and `shader-workflow.md`. |
| Meshes, procedural geometry, instancing, particle draws | `concepts-draws.md`, then the relevant geometry, storage, or compute API. |
| Occluding 3D objects, lighting, cameras, post-processing | `two-pass-rendering.md`; inspect `vgpu/scene` helpers available in that version. |
| Reusable WGSL inside an existing Three.js scene | `threejs.md`; let Three keep ownership of its renderer and frame loop. |
| React/Next.js or Vite integration | `nextjs.md`; use the loader and type declarations documented for the installed package and actual bundler. |
| Static captures, numerical checks, shader diagnostics | `no-bundler.md`, `shader-debugging.md`, and CLI `check --help`. |
| Slow or power-hungry visuals | `performance-playbook.md`, `measuring.md`, and `adaptive-quality.md`. |

Use the gallery to find a suitable starting point: `vgpu examples search "<effect>"`, then `show` or `cat`. Inspect an example's dependencies and API compatibility before adapting it: the CLI can query a live gallery newer than the installed package. Pull source into a new directory when useful; do not overwrite the application with a demo.

## Make the visual deliberate

- Identify the focal subject, palette, depth cues, material behavior, and interaction before adding effects. Match the existing product's typography and hierarchy around the canvas.
- Establish composition, camera framing, and readable silhouettes before layering blur, bloom, noise, or distortion. A complex shader cannot repair a weak composition.
- Make pointer or scroll responses proportional to their purpose. Preserve scrolling and touch interaction; a decorative canvas should not intercept pointer events.
- Keep essential headings, navigation, forms, status, and actions in semantic DOM. Hide purely decorative canvas output from assistive technology; provide equivalent controls and text/data for meaningful interactive graphics.
- Reserve the canvas's layout space and show a useful poster, CSS treatment, or simpler renderer until the first valid frame. Keep that path available if GPU initialization fails.
- Support reduced motion with a still frame or lower-motion treatment. Pause continuous work when offscreen or hidden, and resume without a large simulation-time jump.

## Implement the GPU layer

Create the context, resources, shaders, and render targets once per owned rendering surface or shared renderer. Pass the context explicitly. Keep frame updates to changing state and reuse buffers and textures.

For the reviewed 0.4.1 API:

- Bind values by the WGSL declaration's name. Uniform struct fields nest under the struct binding in `set()`; they are not implicit globals.
- Time comes from the context clock; resolution comes from the target. Update size-dependent bindings on resize, and time-dependent bindings during frames.
- Import WGSL through the documented loader and preserve the complete shader artifact. Extracting just its string can discard export metadata needed by integrations.
- Occluding 3D geometry needs an offscreen target with depth, then a presentation pass to the canvas. A canvas surface itself has no depth attachment in this version. Resize the target and camera aspect together.
- Encode a multi-pass operation in one `frame()`/frame-loop callback. Do not nest one-shot draw methods that independently submit work inside it.
- Scene-tree descriptors alone do not prove a working renderer exists. Check the installed rendering API before assuming `scene()` performs drawing.
- A Three/TSL adapter consumes reusable shader functions while Three owns the scene and bindings. Do not share a canvas between two independently configured rendering loops.

Treat these as versioned constraints; verify the corresponding docs before writing API calls.

In React, initialize after mount on the client. Handle asynchronous initialization completing after unmount, rejected setup, repeated effects, and device loss. Stop the loop, remove observers/listeners, and dispose owned resources on teardown. Do not dispose a shared context from a component that only borrows it, or update React state every frame just to animate GPU uniforms.

## Keep the visual within its budget

Measure CPU submission, GPU passes, startup compilation, transfers, and memory separately. Clamp effective DPR and render-target dimensions for the device and visual; a fullscreen multi-pass effect becomes expensive quickly as pixel count rises.

Reuse pipelines and resource identities, precompile for the actual target where supported, instance repeated geometry, and render static scenes on demand. Avoid per-frame allocation and GPU readback. Use separate ping-pong targets when an effect needs the previous output; do not sample from a texture being written in the same pass.

Use optional GPU timing only when supported. Compare any proposed quality tradeoff on a representative device, preserve the intended look, and report the measured effect. Do not promise a frame rate based on a library choice or silently remove the user's main visual to improve a benchmark.

## Verify the result

Run the project's typecheck/build plus the installed shader checker. In 0.4.1, `vgpu check <shader.wgsl> --require-validation` requires actual shader validation; a successful bundler build alone does not establish WGSL validity.

For a numerical or multi-pass bug, render deterministic small targets and compare readback with expected values. `vgpu/mock` tests API behavior; it is not proof that WGSL compiles, renders correctly on hardware, or meets a GPU performance budget. Use `vgpu doctor` to diagnose a headless environment before relying on it.

Inspect real frames for appearance. Exercise resize/DPR changes, mobile/touch, reduced motion, hidden-tab resume, unsupported WebGPU, initialization failure, device loss, and mount/unmount as relevant to the integration. State which visual and hardware checks were actually performed.

## Reference and attribution

- [Vercel vgpu](https://github.com/vercel-labs/vgpu) and [official documentation](https://vgpu.sh/) — project and version-matched CLI documentation.
- [Upstream vgpu skill](https://github.com/vercel-labs/vgpu/blob/canary/skills/vgpu/SKILL.md) — the version-aware documentation routing informed this skill; upstream is MIT licensed.
- [WebGPU specification](https://www.w3.org/TR/webgpu/) — browser capabilities and resource rules.
- [HTML-in-Canvas proposal](https://github.com/WICG/html-in-canvas) — a distinct experimental DOM snapshot path, not a requirement for vgpu.

This collection adds visual direction, application integration, and rendering decision guidance. It is not an official Vercel skill or a frozen copy of the API manual.
