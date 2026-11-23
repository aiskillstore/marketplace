# Isometric Recipes — Cookbook

Runnable recipes for 2.5D iso scenes: the projection math, flat → iso-plane conversion, extruded blocks with per-face shading, stacked-layer and exploded builds, the iso grid, camera drift / parallax / hover, and a true-3D Three.js `OrthographicCamera` scene. Self-contained across CSS 3D, SVG, and Three.js.

## 0. Projection math — pick a convention and lock it

| Convention | Axes on screen | Tile ratio | Use for |
|---|---|---|---|
| **True isometric** | ground axes at **±30°**, all three axes 120° apart | 1.732 : 1 | CSS 3D, SVG polygons, Three.js |
| **2:1 dimetric** ("pixel iso") | ground axes at **~26.57°** = `atan(0.5)` | 2 : 1 | tile/sprite/map scenes |

Coordinate transforms:

```js
// 2:1 dimetric — grid (col,row) → screen px. TILE = tile WIDTH; height = TILE/2.
const sx = (col - row) * (TILE / 2);
const sy = (col + row) * (TILE / 4);

// inverse: screen px → grid (for click/hover picking)
const col = (sx / (TILE / 2) + sy / (TILE / 4)) / 2;
const row = (sy / (TILE / 4) - sx / (TILE / 2)) / 2;
```

```js
// True iso — world (x,y,z) → screen px (y is up). 30° = Math.PI/6.
const c = Math.cos(Math.PI / 6), s = Math.sin(Math.PI / 6);
const sx = (x - z) * c;
const sy = (x + z) * s - y;     // subtract height y so taller = higher on screen
```

Keep parallel projection: **no perspective shrink**. In CSS that means `perspective: none` (the default) on the scene; in Three.js it means `OrthographicCamera`.

## 1. Flat DOM/SVG → iso plane (CSS 3D)

The cheapest true-iso surface: take any flat element and tip it onto the ground plane. Children lift toward camera with `translateZ`.

```html
<div class="scene">
  <div class="iso-plane">
    <svg viewBox="0 0 200 200"><!-- a flat floorplan / UI mock / grid --></svg>
    <div class="pin" style="--z:60">marker</div>
  </div>
</div>
```
```css
.scene     { perspective: none; transform-style: preserve-3d;
             transform: rotateX(8deg); }          /* optional tiny tilt for framing only */
.iso-plane { transform-style: preserve-3d;
             transform: rotateX(60deg) rotateZ(45deg); }   /* THE iso pair → axes at ±30° */
.pin       { transform: translateZ(calc(var(--z) * 1px))   /* lift off the plane */
                        rotateZ(-45deg) rotateX(-60deg); }  /* un-rotate so text faces camera */
```

`rotateX(60deg) rotateZ(45deg)` is the canonical true-iso pair. To keep a label readable, apply the **inverse** rotation (`rotateZ(-45deg) rotateX(-60deg)`) to that child so it billboards back to the screen.

Matrix equivalent (one transform, no compositing surprises):

```css
.iso-plane { transform: matrix3d(
  0.707, 0.409, 0, 0,
 -0.707, 0.409, 0, 0,
      0, 0.816, 1, 0,
      0,     0, 0, 1); }   /* = rotateX(60)·rotateZ(45), precomputed */
```

## 2. Extruded block — faces + per-face shading

A block = top face + left face + right face. **Top lightest, left mid, right darkest**, one fixed light. This is what sells depth.

```html
<div class="iso-plane">
  <div class="block" style="--w:80;--d:80;--h:60">
    <div class="face top"></div>
    <div class="face left"></div>
    <div class="face right"></div>
  </div>
</div>
```
```css
.block { position:absolute; transform-style:preserve-3d;
         width:calc(var(--w)*1px); height:calc(var(--d)*1px); }
.face  { position:absolute; inset:0; }
.face.top   { background:#3a9bff;
              transform: translateZ(calc(var(--h)*1px)); }          /* lit  */
.face.left  { background:#2c78c8; width:calc(var(--h)*1px);
              transform-origin:left;  transform: rotateY(-90deg); } /* mid  */
.face.right { background:#1f5896; height:calc(var(--h)*1px);
              transform-origin:bottom; transform: rotateX(90deg); } /* dark */
```

### Same block in SVG (often simpler for many blocks — no z-fighting)

```html
<svg viewBox="0 0 120 140">
  <!-- top rhombus -->   <polygon points="60,10 110,40 60,70 10,40" fill="#3a9bff"/>
  <!-- left face -->     <polygon points="10,40 60,70 60,130 10,100" fill="#2c78c8"/>
  <!-- right face -->    <polygon points="110,40 60,70 60,130 110,100" fill="#1f5896"/>
</svg>
```

SVG sidesteps CSS 3D z-fighting entirely: paint order = depth. Sort polygons back-to-front and they occlude correctly. Best for grids, infographics, and dozens of small blocks.

## 3. Stacked Z layers + bottom-up build (GSAP)

```html
<div class="iso-plane" id="stack">
  <div class="layer" style="--z:0"></div>
  <div class="layer" style="--z:40"></div>
  <div class="layer" style="--z:80"></div>
  <div class="layer" style="--z:120"></div>
</div>
```
```css
.layer { position:absolute; inset:0; transform: translateZ(calc(var(--z)*1px)); }
```
```js
import gsap from "https://cdn.jsdelivr.net/npm/gsap/+esm";
const layers = gsap.utils.toArray("#stack .layer");
// build bottom (largest --z appears last? no — physical bottom first):
layers.sort((a,b)=> (+a.style.getPropertyValue("--z")) - (+b.style.getPropertyValue("--z")));
const tl = gsap.timeline({ defaults:{ ease:"back.out(1.4)", duration:.5 } });
tl.from(layers, {
  opacity:0,
  z:(i,el)=> (+el.style.getPropertyValue("--z")) - 60,   // rise into place from below
  stagger:.12,
});
```

Stagger by physical Z, not DOM order, so the tower assembles bottom-up.

## 4. Exploded-view diagram (assemble / explode)

Resting state pulled apart; one shared `--gap` opens the whole stack.

```css
.layer { transform: translateZ(calc((var(--i) * var(--gap, 0)) * 1px)); }
```
```js
const plane = document.querySelector(".iso-plane");
const tl = gsap.timeline({ paused:true });
tl.fromTo(plane, { "--gap": 90 }, { "--gap": 40, duration:.9, ease:"power3.inOut" });
// tl.play() = assemble ; tl.reverse() = explode
```

(Register the CSS var as animatable: `CSS.registerProperty({name:"--gap",syntax:"<number>",inherits:true,initialValue:"0"})`, or animate each layer's `z` directly if you skip Houdini.)

## 5. Isometric grid

Author flat lines, drop on the plane, draw on.

```html
<svg class="grid" viewBox="0 0 200 200" style="position:absolute">
  <g stroke="#2a3340" stroke-width="1" fill="none" pathLength="1"></g>
</svg>
```
```js
const g = document.querySelector(".grid g");
for (let i = 0; i <= 200; i += 20) {
  g.insertAdjacentHTML("beforeend",
    `<path d="M${i} 0 V200"/><path d="M0 ${i} H200"/>`);  // flat grid; .iso-plane makes it iso
}
gsap.set(".grid path", { strokeDasharray:1, strokeDashoffset:1 });
gsap.to(".grid path", { strokeDashoffset:0, duration:.6, stagger:.02, ease:"power2.out" });
```

## 6. Camera drift, parallax, hover lift

```js
// drift: tiny, slow, looped — big moves expose the flat plane
gsap.to(".scene", { rotationZ:"+=3", duration:9, yoyo:true, repeat:-1, ease:"sine.inOut" });
```
```js
// parallax: deeper layers shift more with the pointer
addEventListener("pointermove", e => {
  const dx = (e.clientX / innerWidth  - .5);
  const dy = (e.clientY / innerHeight - .5);
  gsap.utils.toArray(".layer").forEach(el => {
    const k = +el.style.getPropertyValue("--z") / 40;
    gsap.to(el, { x: dx*8*k, y: dy*8*k, duration:.6, ease:"power2.out" });
  });
});
```
```css
/* hover lift: raise one block along Z + soften its shadow */
.block { transition: transform .25s cubic-bezier(.22,1,.36,1); }
.block:hover { transform: translateZ(12px); }
```

## 7. Three.js — true 3D iso (OrthographicCamera)

When you need real occlusion, shadows, or 3D rotation. Orthographic = parallel projection = genuine iso.

```html
<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js";

const scene = new THREE.Scene();
const aspect = innerWidth / innerHeight, d = 6;
const cam = new THREE.OrthographicCamera(-d*aspect, d*aspect, d, -d, 0.1, 100);
cam.position.set(10, 10, 10);    // equal X,Y,Z → 30° classic iso vantage
cam.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const key = new THREE.DirectionalLight(0xffffff, 1);
key.position.set(8, 12, 6); key.castShadow = true; scene.add(key);   // ONE fixed light dir

// a stack of blocks that builds bottom-up
const blocks = [];
for (let i = 0; i < 4; i++) {
  const m = new THREE.Mesh(
    new THREE.BoxGeometry(3, 0.8, 3),
    new THREE.MeshStandardMaterial({ color:0x3a9bff }));
  m.position.y = i * 0.9; m.castShadow = m.receiveShadow = true;
  m.scale.set(0, 1, 0);                  // hidden until build
  scene.add(m); blocks.push(m);
}

// single progress value drives the build → deterministic, seekable
function setProgress(p) {                 // p in 0..1
  blocks.forEach((m, i) => {
    const local = THREE.MathUtils.clamp(p * blocks.length - i, 0, 1);
    const e = 1 - Math.pow(1 - local, 3); // easeOutCubic
    m.scale.set(e, 1, e);
  });
  renderer.render(scene, cam);
}

const t = new URLSearchParams(location.search).get("t");
if (t !== null) { setProgress(THREE.MathUtils.clamp(parseFloat(t), 0, 1)); }  // freeze
else {
  const start = performance.now();
  (function loop(now){ setProgress(Math.min(1,(now-start)/2000)); requestAnimationFrame(loop); })(start);
}
window.__ready = true;
</script>
```

A `PerspectiveCamera` is NOT iso — it foreshortens. Equal camera-position components give the 30° view; one directional light keeps shading consistent with the CSS/SVG rules above. Drive the build from a single normalized progress value so `?t=N` freezes a deterministic frame for screenshots.

## Reduced-motion across all recipes

- Stop looping drift / parallax (`gsap.globalTimeline` not started; no `repeat:-1`).
- Jump to the final assembled state: all layers seated (`--gap` at minimum), all blocks at full scale, grid fully drawn.
- Gate any JS timeline on `matchMedia("(prefers-reduced-motion: reduce)").matches` and seek to the end.

---
Lock the axes, shade every face from one light, and build bottom-up — the scene reads as solid before a single thing moves. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=explainer-video-skills&utm_content=skill_footer&utm_term=isometric-animation)** — the AI motion agent for editable, on-brand motion graphics.
