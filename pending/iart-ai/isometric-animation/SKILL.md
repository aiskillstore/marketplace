---
name: isometric-animation
description: This skill should be used when the user asks to "make an isometric animation", "build a 2.5D isometric scene", "create an isometric infographic", "animate an exploded diagram", "do an isometric city/stack build", "show stacked layers in iso", "extrude blocks with depth", or "add a gentle camera drift to an iso scene". Covers CSS 3D transforms, SVG iso planes, and Three.js OrthographicCamera for true 3D iso — no build step.
version: 0.1.0
---

# Isometric (2.5D) Animation

Isometric scenes give explainers, UI walkthroughs, and infographics a built, dimensional feel without true perspective: equal-foreshortened axes, stacked Z layers, extruded blocks, exploded diagrams. The look is geometric and deliberate — depth comes from consistent axes and per-face shading, motion from revealing structure one layer at a time.

## When to use

- 2.5D scenes for explainers, product UI, or "how it works" infographics.
- Stacked layers / floors / a tech-stack tower that builds bottom-up.
- Extruded blocks, isometric grids, isometric city/server-rack scenes.
- Exploded-view diagrams that pull apart along Z and reassemble.
- A static iso illustration that needs gentle life: camera drift, parallax, hover lift.

## Projection: get the axes right first

Two conventions — pick one and never mix:

- **True isometric** — all three axes 120° apart; on screen the X/Y ground axes run at **±30° from horizontal**. This is the math-correct iso. Use for CSS/Three.js.
- **2:1 dimetric ("pixel-art iso")** — tiles drawn 2 wide : 1 tall, so axes sit at **~26.57°** (`atan(0.5)`). Cleaner pixels, the game-art default. Use for tile/sprite scenes.

For DOM/SVG the fastest true-iso plane is a CSS 3D transform on a `perspective: none` (orthographic-feeling) container:

```css
.scene { transform-style: preserve-3d; }
/* rotate a flat plane onto the iso ground */
.iso-plane { transform: rotateX(60deg) rotateZ(45deg); }
```

`rotateX(60deg) rotateZ(45deg)` tips a flat element back 60° then spins it 45° — the standard "true iso" pair that lands the ground-plane axes at ±30° on screen. Any flat SVG/DOM (a floorplan, a UI mock, a grid) placed on `.iso-plane` is now an iso surface; lift children toward the camera with `translateZ()`.

Equivalent grid-to-screen math when you place tiles by code (2:1 dimetric):

```js
// tile (col, row) → screen pixels, TILE = full tile width
const screenX = (col - row) * (TILE / 2);
const screenY = (col + row) * (TILE / 4);
```

Keep `perspective` OFF (or very large) — iso is parallel projection, so far objects must NOT shrink. A small `perspective` reads as a tilted 3D card, not iso.

## Building scenes

### Stacked Z layers (cards / floors)

Each layer is the same flat shape on the iso plane, separated along Z. Lift later layers higher; stagger reveals bottom-up.

```html
<div class="scene"><div class="iso-plane">
  <div class="layer" style="--z:0">  <!-- base --></div>
  <div class="layer" style="--z:40"> <!-- mid  --></div>
  <div class="layer" style="--z:80"> <!-- top  --></div>
</div></div>
```
```css
.layer { transform: translateZ(calc(var(--z) * 1px)); }
```

### Extruded block (faces + per-face shading = depth)

A solid block is a top + two visible side faces. Shade by face so the eye reads volume — **top lightest, left mid, right darkest** (a fixed light direction). This is the single most important trick for believable iso depth.

```css
.block .top   { background:#3a9bff; }              /* lit   */
.block .left  { background:#2c78c8; transform: rotateY(-90deg); transform-origin:left; }
.block .right { background:#1f5896; transform: rotateX(90deg);  transform-origin:bottom; } /* shade */
```

Same shading rule in SVG: draw three polygons (top rhombus, left + right parallelograms) and fill them light/mid/dark. SVG is often simpler than 3D-CSS for many small blocks (see references).

### Isometric grid

A floor grid is just two sets of parallel lines on `.iso-plane` (drawn flat, the rotation makes them iso). Author it flat in SVG, drop it on the plane, animate lines drawing on with `stroke-dashoffset`.

### Exploded-view diagram

Same as stacked layers but the resting state is **pulled apart** along Z; assemble = animate every layer's `translateZ` toward its seated value. Explode = reverse. Keep one shared `--gap` variable so the whole stack opens/closes together.

## Motion

| Goal | Mechanism | Easing |
|---|---|---|
| Layer reveal (build) | per-layer `opacity` + `translateZ` from below, staggered | `back.out(1.4)`, stagger 0.12s |
| Explode / assemble | tween shared `--gap` (or each `translateZ`) | `power3.inOut`, 0.7–1s |
| Tower / stack build | layers drop in bottom→top | `back.out(1.5)`, stagger 0.15s |
| Camera drift | slow `rotateZ` / `translate` on `.scene`, looped yoyo | `sine.inOut`, 6–12s |
| Parallax | layers shift by depth on pointer/scroll (`--z` ∝ shift) | `power2.out` |
| Hover lift | one block `translateZ(+12px)` + soft shadow | `power2.out`, 0.25s |

Rules that keep it reading as iso:

- **Lift along Z, never scale** to fake height — scaling breaks parallel projection.
- Camera drift must be tiny and slow (a few degrees / pixels). Big moves expose that it's a flat plane.
- Stagger builds by **physical position** (bottom layer first), not DOM order, so the structure assembles logically.
- Keep the light direction fixed for the whole scene — every block shades the same way.

## Three.js OrthographicCamera (true 3D iso) — alternative

When blocks must occlude correctly, cast real shadows, or rotate in 3D, use real geometry under an **orthographic** camera (parallel projection = genuine iso; a `PerspectiveCamera` is NOT iso).

```js
const aspect = innerWidth / innerHeight, d = 8;
const cam = new THREE.OrthographicCamera(-d*aspect, d*aspect, d, -d, 0.1, 100);
cam.position.set(10, 10, 10);   // equal X,Y,Z → classic iso vantage
cam.lookAt(0, 0, 0);
```

Equal `position` components give the 30° iso view; `OrthographicCamera` keeps far objects the same size. Light from one direction, enable shadows, and stagger `mesh.position.y` / scale-in for the build. Full setup in references.

## Build-tool choice

- **CSS 3D transforms** — best for a handful of blocks/layers with crisp DOM/text on faces; one HTML file.
- **Inline SVG (iso polygons)** — best for many small blocks, grids, and infographics; easiest to animate with GSAP/CSS, no 3D-transform z-fighting.
- **Three.js + OrthographicCamera** — when you need real occlusion, shadows, or 3D rotation; still shippable as one HTML file via CDN.
- **Pixel/tile (2:1)** — game-art or map scenes; use the `(col-row, col+row)` projection.

## Output checklist

- Axes land at the right angle (±30° true-iso, ~26.57° for 2:1); no accidental perspective shrink.
- Every block shaded top-light / side-mid / side-dark from one fixed light.
- Layers stack with believable depth — no z-fighting, no two faces flickering, no overlap errors.
- Build staggers by physical position (bottom-up), one idea per beat.
- Camera drift is small and slow; explode/assemble seats every layer exactly.
- `prefers-reduced-motion` shows the final assembled scene with no looping drift.

## Deliver & verify (standalone HTML)

> **Packaged helper** (`scripts/`): `scripts/seek-shot.sh anim.html 0 1.5 3` freezes the `?t=N` harness and screenshots each moment; `scripts/contact-sheet.sh sheet.png frame-*.png` tiles them for one-glance review. See `scripts/README.md`.

For a self-contained iso scene (stack build, exploded diagram, drifting infographic) the deliverable is **one HTML file that opens directly in a browser** — no build step, no framework, no render pipeline. A single file is the right tier for web motion; reach for a bundler only when one file genuinely can't carry it. (If the scene is part of a rendered video, build it as a Remotion composition and verify with `remotion still` instead.)

**Output contract:**
- One `.html` file: CSS 3D transforms or inline SVG (or Three.js from CDN), markup, and all motion in one inline `<script>` on **one master timeline** (`const tl = gsap.timeline()`) — a single playhead you can seek.
- Include the seek harness so any moment can be frozen for a screenshot.

**Seek harness — freeze an exact moment for screenshots.** The web parallel of a frame-pin: `?t=N` seeks the master timeline to `N` seconds and pauses, so a screenshot lands on a deterministic still.

```html
<script>
  // ... build your master timeline as `tl` (the layer build / explode / drift) ...
  const t = new URLSearchParams(location.search).get("t");
  if (t !== null) { tl.pause(); tl.seek(parseFloat(t)); }  // frozen at t seconds
  // no ?t → plays normally
  window.__ready = true;            // ready signal for headless wait
  console.log("duration", tl.duration());
</script>
```

For a Three.js scene with no GSAP timeline, drive the build from a single `clock`/progress value and set it from `?t=N`, then render one frame — same idea, one deterministic still.

**Verify loop — render → freeze → screenshot → check:**
1. Open the file at three moments — start, mid, end:
   `…/iso.html?t=0`, `?t=<dur/2>`, `?t=<dur>` (read `tl.duration()` from the console).
2. Headless-screenshot each frozen frame:
   ```bash
   npx playwright screenshot --wait-for-timeout=500 "file://$PWD/iso.html?t=1.2" frame-mid.png
   ```
3. **INSPECT the projection, not just "did it animate":**
   - **Axes** — ground lines run at the intended angle (±30° true-iso / ~26.57° dimetric); verticals stay vertical; nothing is foreshortened like perspective.
   - **Depth** — layers stack in the right Z order, blocks occlude correctly, per-face shading reads volume; **no z-fighting** (flickering coincident faces) and **no overlap errors** (a back block punching through a front one).
   - **Build** — at mid-frame the stack is partway assembled in physical order; at end every layer is exactly seated (explode fully closed), no drift left mid-tween.
   - **Artifacts** — clipped/skewed text on faces, off-canvas blocks, FOUC before fonts, jagged grid seams.
4. Iterate: fix angle/shading/Z-order, re-freeze the same `?t` values, re-screenshot until it reads as solid iso.

**Before you finish:**
1. Opens standalone in a browser — no console errors, no missing CDN.
2. One master timeline (or one Three.js progress value); `?t=N` freezes on a deterministic still.
3. Screenshotted at start / mid / end — axes correct, depth/Z-order correct, no z-fighting, build seats exactly.
4. Per-face shading consistent from one fixed light; no accidental perspective shrink.
5. `prefers-reduced-motion` shows the final assembled scene without looping drift.

## Reference files

- `references/isometric-recipes.md` — fuller runnable code: the projection math (true-iso vs 2:1 dimetric, transform vs matrix), flat-SVG/DOM → iso-plane conversion, extruded-block faces with per-face shading (CSS and SVG), stacked-layer and exploded-view builds, isometric grid, camera drift / parallax / hover, and a complete Three.js `OrthographicCamera` iso scene — with easing notes and reduced-motion handling.
