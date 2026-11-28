# Draw-On Recipes — Cookbook

Runnable mechanics for the whiteboard "draw-on" look: paths that draw themselves, a hand that tracks the drawing tip, multi-stroke sequencing, handwriting, fills, erase transitions, and the Remotion port.

## 1. The dashoffset draw-on (vanilla)

A stroke draws itself by collapsing one giant dash from its full length to 0.

```js
function makeDrawable(path) {
  const len = path.getTotalLength();
  path.style.strokeDasharray  = len;   // single dash spanning the whole path
  path.style.strokeDashoffset = len;   // offset by full length = hidden
  return len;
}
function draw(path, dur = 1200) {
  const len = makeDrawable(path);
  path.getBoundingClientRect();        // reflow so the transition takes
  path.style.transition = `stroke-dashoffset ${dur}ms linear`;
  path.style.strokeDashoffset = "0";   // animate to drawn
}
```

Normalize with `pathLength="1"` so length is irrelevant:

```html
<path id="s" d="M10 80 C 40 10, 65 10, 95 80 S 150 150, 180 80"
      pathLength="1" fill="none" stroke="#111" stroke-width="4"
      style="stroke-dasharray:1; stroke-dashoffset:1; transition:stroke-dashoffset 1.2s linear" />
<script> requestAnimationFrame(() => document.getElementById("s").style.strokeDashoffset = "0"); </script>
```

`linear` looks like a steady hand. A faint `ease-out` at the very end is fine; `ease-in-out` on a long line makes the nib visibly accelerate/brake.

## 2. Hand follows the tip (the core illusion)

Drive `strokeDashoffset` and the hand position from one progress value `k`. `getPointAtLength(len*k)` gives the on-path tip; place the hand's nib there.

```js
const NIB = { x: 6, y: 4 };   // nib offset measured inside the hand art (SVG units)

function drawOnWithHand(path, hand, dur = 1200) {
  return new Promise((resolve) => {
    const len = path.getTotalLength(), t0 = performance.now();
    path.style.strokeDasharray = len;
    hand.style.opacity = "1";
    (function frame(now) {
      const k = Math.min(1, (now - t0) / dur);
      path.style.strokeDashoffset = len * (1 - k);     // expose start → tip
      const p = path.getPointAtLength(len * k);        // tip in SVG coords
      hand.setAttribute("transform", `translate(${p.x - NIB.x} ${p.y - NIB.y})`);
      if (k < 1) requestAnimationFrame(frame); else resolve();
    })(t0);
  });
}
```

Lift the hand between strokes so it never slides across blank board:

```js
async function liftTo(hand, x, y, ms = 250) {
  hand.style.transition = `transform ${ms}ms ease, opacity 120ms`;
  hand.style.opacity = "0";
  hand.setAttribute("transform", `translate(${x - NIB.x} ${y - NIB.y})`);
  await new Promise(r => setTimeout(r, ms));
  hand.style.transition = "";
}
```

## 3. Multi-stroke drawing in order

Draw each stroke in document order, hopping the hand to each new stroke's start.

```js
async function drawShape(selector, hand, perStroke = 700) {
  const strokes = [...document.querySelectorAll(selector)];
  for (const s of strokes) {
    const start = s.getPointAtLength(0);
    await liftTo(hand, start.x, start.y);   // hop hand to this stroke's start
    await drawOnWithHand(s, hand, perStroke);
  }
}
```

Stagger with small holds for a natural cadence; long primary strokes slower than short connective ones.

## 4. GSAP variants

`DrawSVGPlugin` (free as of GSAP 3.12) draws a stroke from a 0%→100% range and pairs with one master timeline:

```js
import gsap from "gsap";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
gsap.registerPlugin(DrawSVGPlugin);

const tl = gsap.timeline({ defaults: { ease: "none" } });
tl.from("#stroke1", { drawSVG: 0, duration: 1.2 })
  .from("#stroke2", { drawSVG: 0, duration: 0.8 }, "+=0.1")
  .from(".word path", { drawSVG: 0, duration: 0.25, stagger: 0.06 }, "+=0.3");
```

Move the hand along the same path with `MotionPathPlugin` so it tracks the draw:

```js
import { MotionPathPlugin } from "gsap/MotionPathPlugin";
gsap.registerPlugin(MotionPathPlugin);

tl.to("#hand", {
  motionPath: { path: "#stroke1", align: "#stroke1", alignOrigin: [0.1, 0.05] },
  duration: 1.2, ease: "none",
}, "<");   // "<" = same start as the drawSVG tween, so hand and tip move together
```

`alignOrigin` is the GSAP equivalent of the `NIB` offset — it pins the hand's nib to the path point.

## 5. Handwriting

Convert glyphs to paths and draw each in stroke order:

```js
// each letter is <path class="ink"> in writing order
await drawShape(".word-1 .ink", hand, 220);   // fast per-letter strokes
```

Fake-write a whole word by sweeping a reveal mask, hand riding the edge:

```html
<clipPath id="reveal"><rect id="wipe" x="20" y="40" width="0" height="60"/></clipPath>
<text clip-path="url(#reveal)" x="20" y="90" font-family="'Caveat', cursive" font-size="64">hello</text>
```

```js
gsap.timeline()
  .to("#wipe", { attr: { width: 300 }, duration: 1.0, ease: "none" })
  .to("#hand", { x: 320, duration: 1.0, ease: "none" }, "<");  // hand rides the wipe edge
```

Use a handwriting/stroke font (Caveat, Patrick Hand, Shadows Into Light) and split into `.word`/letter spans so the wipe matches reading order.

## 6. Fill after outline

Draw the outline stroke, then bring the fill in behind it so it reads as "colored in."

```js
await drawOnWithHand(outlinePath, hand, 1000);
gsap.to(fillPath, { opacity: 1, duration: 0.4, ease: "power1.out" });   // fill fades in after
```

Or clip-reveal the fill so it appears to flood in:

```css
.fill { clip-path: inset(0 100% 0 0); transition: clip-path .5s linear; }
.fill.in { clip-path: inset(0 0 0 0); }
```

## 7. Erase / wipe transitions

Clear a section before the next. Wipe with a moving clip:

```css
.board-group { clip-path: inset(0 0 0 0); transition: clip-path .6s ease; }
.board-group.wiped { clip-path: inset(0 0 0 100%); }   /* wipe left → right */
```

Reverse draw-on (un-draw, hand following backward):

```js
function unDraw(path, hand, dur = 800) {
  const len = path.getTotalLength(), t0 = performance.now();
  (function frame(now) {
    const k = Math.min(1, (now - t0) / dur);
    path.style.strokeDashoffset = len * k;             // hide tip → start
    const p = path.getPointAtLength(len * (1 - k));
    hand.setAttribute("transform", `translate(${p.x - NIB.x} ${p.y - NIB.y})`);
    if (k < 1) requestAnimationFrame(frame);
  })(t0);
}
```

Pick one wipe direction for the whole piece so transitions feel intentional.

## 8. Remotion port (frame-driven export)

Drive both `strokeDashoffset` and the hand transform from `useCurrentFrame()` so the render is deterministic — no timers, no rAF.

```jsx
import { useCurrentFrame, useVideoConfig, interpolate, staticFile, Img } from "remotion";

export const Stroke = ({ d, startSec, durSec, len, nib = { x: 6, y: 4 } }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  const t = frame / fps;
  const k = interpolate(t, [startSec, startSec + durSec], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ref = React.useRef(null);
  const [p, setP] = React.useState({ x: 0, y: 0 });
  React.useEffect(() => { if (ref.current) setP(ref.current.getPointAtLength(len * k)); }, [k, len]);
  return (
    <>
      <path ref={ref} d={d} fill="none" stroke="#111" strokeWidth={4}
            strokeDasharray={len} strokeDashoffset={len * (1 - k)} />
      {k > 0 && k < 1 && (
        <g transform={`translate(${p.x - nib.x} ${p.y - nib.y})`}>
          <Img src={staticFile("hand.png")} />
        </g>
      )}
    </>
  );
};
```

Sequence strokes by their `startSec`; compute total `durationInFrames` from the last stroke's end via `calculateMetadata`. Verify with `npx remotion still` at a mid-stroke frame — see the explainer-video skill for the stills → encode loop.
