# Diagram & Chart Recipes — Cookbook

Runnable recipes for progressive diagram reveals, flowing connectors, and animated charts. Self-contained across SVG/CSS, GSAP, D3, Framer Motion, and Remotion.

## Reveal order & pacing

1. **Containers/regions** first (faint), to establish the frame.
2. **Nodes** appear (scale 0.8→1 + fade), in reading/logical order.
3. **Edges** draw between now-visible nodes.
4. **Labels** fade in last, on the settled nodes.
5. **Highlight** sweeps the active path; everything else dims to ~0.35 opacity.

Hold each meaningful step 0.5–1.5s. For narrated diagrams, gate each step on the VO line, not a fixed timer.

## 1. Staged node → edge → label reveal (GSAP timeline)

```html
<svg viewBox="0 0 480 220" id="arch">
  <g class="region" opacity="0"><rect x="20" y="40" width="180" height="140" rx="12" fill="#11161f"/></g>
  <g class="node" data-i="0" opacity="0"><rect x="50" y="70" width="120" height="40" rx="8" fill="#0A84FF"/></g>
  <g class="node" data-i="1" opacity="0"><rect x="50" y="130" width="120" height="40" rx="8" fill="#0A84FF"/></g>
  <g class="node" data-i="2" opacity="0"><rect x="300" y="100" width="140" height="40" rx="8" fill="#30D158"/></g>
  <path class="edge" d="M170 90 C240 90 240 120 300 120" fill="none" stroke="#5b6472" stroke-width="3" pathLength="1"/>
  <path class="edge" d="M170 150 C240 150 240 120 300 120" fill="none" stroke="#5b6472" stroke-width="3" pathLength="1"/>
  <text class="label" x="110" y="95" fill="#fff" font-size="13" text-anchor="middle" opacity="0">Web</text>
  <text class="label" x="110" y="155" fill="#fff" font-size="13" text-anchor="middle" opacity="0">Worker</text>
  <text class="label" x="370" y="125" fill="#000" font-size="13" text-anchor="middle" opacity="0">Queue</text>
</svg>
<script type="module">
  import gsap from "https://cdn.jsdelivr.net/npm/gsap/+esm";
  gsap.set(".edge", { strokeDasharray: 1, strokeDashoffset: 1 });
  gsap.set(".node", { transformOrigin: "center", scale: .85 });
  const tl = gsap.timeline({ defaults: { ease: "power2.out" } });
  tl.to(".region", { opacity: 1, duration: .4 })
    .to(".node",  { opacity: 1, scale: 1, duration: .45, stagger: .25, ease: "back.out(1.5)" })
    .to(".edge",  { strokeDashoffset: 0, duration: .55, stagger: .2 }, "-=0.3")
    .to(".label", { opacity: 1, duration: .35, stagger: .12 }, "-=0.4");
</script>
```

## 2. Sequence diagram (lifelines + activation messages)

Reveal each message arrow in order, marching the dash to imply direction.

```js
import gsap from "gsap";
gsap.set(".msg", { strokeDasharray: 1, strokeDashoffset: 1 });
const tl = gsap.timeline();
document.querySelectorAll(".msg").forEach((m, i) => {
  tl.to(m, { strokeDashoffset: 0, duration: .5, ease: "power1.inOut" })
    .fromTo(m.nextElementSibling, // the message label
            { opacity: 0, y: -4 }, { opacity: 1, y: 0, duration: .3 }, "-=0.2")
    .to({}, { duration: .6 }); // hold so it reads
});
```

## 3. Flowing connector — marching dash + traveling packet

```html
<svg viewBox="0 0 400 80">
  <path id="wire" d="M20 40 H380" stroke="#2b3340" stroke-width="4" fill="none"/>
  <path class="flow" d="M20 40 H380" stroke="#0A84FF" stroke-width="4" fill="none"
        stroke-dasharray="10 12"/>
  <circle class="packet" r="5" fill="#7cc4ff"/>
</svg>
<style>
  .flow   { animation: march .7s linear infinite; }
  @keyframes march { to { stroke-dashoffset: -22; } } /* = dash(10)+gap(12) */
  .packet { offset-path: path("M20 40 H380"); animation: travel 1.6s linear infinite; }
  @keyframes travel { to { offset-distance: 100%; } }
  @media (prefers-reduced-motion: reduce){
    .flow, .packet { animation: none; }
  }
</style>
```

Reverse direction (data flowing back): use a positive `stroke-dashoffset` keyframe target and `offset-distance` from 100%→0%.

## 4. Bar chart — grow + stagger

```html
<div class="chart">
  <div class="bar" style="--h:60%"></div>
  <div class="bar" style="--h:85%"></div>
  <div class="bar" style="--h:40%"></div>
</div>
<style>
  .chart { display:flex; gap:12px; align-items:flex-end; height:200px; }
  .bar { width:48px; height:var(--h); background:#0A84FF; transform:scaleY(0);
         transform-origin:bottom; transition:transform .6s cubic-bezier(.22,1,.36,1); }
  .bar.in { transform:scaleY(1); }
  .bar:nth-child(1){ transition-delay:.00s } .bar:nth-child(2){ transition-delay:.08s }
  .bar:nth-child(3){ transition-delay:.16s }
</style>
<script>
  // trigger on view
  document.querySelectorAll(".bar").forEach(b => b.classList.add("in"));
</script>
```

SVG bar version (animate `height` + `y` so it grows from the baseline):

```js
import gsap from "gsap";
gsap.from("rect.bar", {
  attr: { height: 0, y: (i, t) => +t.getAttribute("y") + +t.getAttribute("height") },
  duration: .6, ease: "power3.out", stagger: .08
});
```

## 5. Line chart — draw-on via dashoffset

```js
const path = document.querySelector("path.series");
const len = path.getTotalLength();
Object.assign(path.style, { strokeDasharray: len, strokeDashoffset: len });
path.getBoundingClientRect();                       // reflow so transition runs
path.style.transition = "stroke-dashoffset 1.1s ease-in-out";
path.style.strokeDashoffset = "0";
// dots pop after the line reaches them:
gsap?.from("circle.point", { scale: 0, transformOrigin: "center",
  duration: .3, stagger: .12, delay: .3, ease: "back.out(2)" });
```

Area-under-line: draw the stroke first, then fade in the filled area path after the stroke completes.

## 6. Count-up number

```js
function countUp(el, to, { dur = 1200, decimals = 0, prefix = "", suffix = "" } = {}) {
  const t0 = performance.now();
  const fmt = new Intl.NumberFormat(undefined, { minimumFractionDigits: decimals,
                                                 maximumFractionDigits: decimals });
  (function tick(now){
    const k = Math.min(1, (now - t0) / dur);
    const e = 1 - Math.pow(1 - k, 3);               // easeOutCubic
    el.textContent = prefix + fmt.format(to * e) + suffix;
    if (k < 1) requestAnimationFrame(tick);
  })(t0);
}
countUp(document.querySelector("#stat"), 1284000, { suffix: "+" });
```

Respect reduced motion: if reduced, set `el.textContent` to the final value immediately and skip the loop.

## 7. D3 transitions

```js
const bars = svg.selectAll("rect").data(data).join("rect")
  .attr("x", d => x(d.label)).attr("width", x.bandwidth())
  .attr("y", y(0)).attr("height", 0).attr("fill", "#0A84FF");
bars.transition().duration(600).delay((d, i) => i * 80)
  .ease(d3.easeCubicOut)
  .attr("y", d => y(d.value)).attr("height", d => y(0) - y(d.value));

// count-up via attrTween / tween
d3.select("#stat").transition().duration(1200).ease(d3.easeCubicOut)
  .tween("text", function () {
    const i = d3.interpolateNumber(0, 1284000);
    return t => this.textContent = d3.format(",")(Math.round(i(t)));
  });
```

## 8. Framer Motion (React)

```jsx
import { motion } from "framer-motion";
const container = { show: { transition: { staggerChildren: 0.12 } } };
const node = { hidden: { opacity: 0, scale: 0.85 },
               show:   { opacity: 1, scale: 1, transition: { ease: "backOut" } } };

export function Flow() {
  return (
    <motion.svg variants={container} initial="hidden" animate="show" viewBox="0 0 400 200">
      {nodes.map(n => <motion.circle key={n.id} variants={node} cx={n.x} cy={n.y} r={26} />)}
      {edges.map(e => (
        <motion.path key={e.id} d={e.d} fill="none" stroke="#888" strokeWidth={3}
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
          transition={{ duration: 0.5, ease: "easeInOut", delay: 0.4 }} />
      ))}
    </motion.svg>
  );
}
```

`pathLength` is a first-class animatable prop in Framer Motion — no manual dash math needed.

## 9. Remotion (deterministic video render)

```jsx
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const Bar = ({ value, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const delay = index * 4;
  const grow = spring({ frame: frame - delay, fps, config: { damping: 14 } });
  return <rect x={index * 60} y={200 - value * grow} width={40} height={value * grow} fill="#0A84FF" />;
};

export const Count = ({ to }) => {
  const frame = useCurrentFrame();
  const e = interpolate(frame, [0, 36], [0, to], { extrapolateRight: "clamp",
    easing: t => 1 - Math.pow(1 - t, 3) });
  return <text>{Math.round(e).toLocaleString()}</text>;
};
```

Because Remotion renders per-frame deterministically, the same diagram renders identically to PNG sequence/MP4 every time — ideal for repeatable data exports.

## Reduced-motion across all recipes

- Stop `infinite` connector/flow animations (`animation: none`).
- Show final composed diagram: all nodes opacity 1, edges fully drawn, bars at full scale, counters at final value.
- Gate any JS timeline on `matchMedia("(prefers-reduced-motion: reduce)").matches` and jump to end state.

---
Reveal nodes before edges before labels, and a diagram explains itself. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=explainer-video-skills&utm_content=skill_footer&utm_term=diagram-animation)** — the AI motion agent for editable, on-brand motion graphics.
