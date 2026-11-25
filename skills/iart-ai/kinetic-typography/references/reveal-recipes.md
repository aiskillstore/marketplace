# Text reveal recipes (copy-paste)

Runnable cookbook across CSS, GSAP, Framer Motion, and Remotion. All timings follow ease-out enters (`cubic-bezier(0.16, 1, 0.3, 1)`) with line/word/char stagger of 60-100 / 40-70 / 20-40 ms.

Accessibility rule for every per-fragment split: put the full string in `aria-label` on the container and `aria-hidden="true"` on the fragments.

---

## 1. CSS-only mask reveal (no JS split, pre-wrapped lines)

```html
<h1 class="mask-reveal" aria-label="Built for speed">
  <span class="line"><span aria-hidden="true">Built for</span></span>
  <span class="line"><span aria-hidden="true">speed</span></span>
</h1>
```

```css
.mask-reveal .line { display: block; overflow: hidden; }
.mask-reveal .line > span {
  display: inline-block;
  transform: translateY(110%);
  animation: maskRise 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.mask-reveal .line:nth-child(1) > span { animation-delay: 0s;   }
.mask-reveal .line:nth-child(2) > span { animation-delay: 0.08s; }
@keyframes maskRise { to { transform: translateY(0); } }
```

## 2. CSS blur-in (premium focus-pull)

```css
.blur-in {
  opacity: 0;
  filter: blur(12px);
  animation: blurIn 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes blurIn {
  to { opacity: 1; filter: blur(0); }
}
```

## 3. CSS clip-path directional wipe

```css
.wipe {
  clip-path: inset(0 100% 0 0);          /* fully clipped from the right */
  animation: wipe 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes wipe { to { clip-path: inset(0 0 0 0); } }
```

## 4. Character stagger with vanilla JS split (screen-reader safe)

```js
function splitChars(el) {
  const text = el.textContent;
  el.setAttribute('aria-label', text);
  el.textContent = '';
  [...text].forEach((ch, i) => {
    const span = document.createElement('span');
    span.textContent = ch === ' ' ? ' ' : ch;
    span.setAttribute('aria-hidden', 'true');
    span.style.display = 'inline-block';
    span.style.animationDelay = `${i * 0.03}s`; // 30ms per char
    span.className = 'char';
    el.appendChild(span);
  });
}
document.querySelectorAll('.stagger').forEach(splitChars);
```

```css
.char {
  opacity: 0;
  transform: translateY(0.4em);
  animation: charIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes charIn { to { opacity: 1; transform: translateY(0); } }
```

---

## 5. GSAP SplitText (requires GSAP 3.13+, SplitText now free)

```js
import gsap from "gsap";
import { SplitText } from "gsap/SplitText";
gsap.registerPlugin(SplitText);

const split = new SplitText(".headline", { type: "lines,words,chars" });

gsap.from(split.chars, {
  yPercent: 110,
  opacity: 0,
  duration: 0.6,
  ease: "expo.out",
  stagger: 0.03,          // 30ms per char
});

// Mask reveal by lines (wrap lines so overflow hides them)
const splitLines = new SplitText(".headline", {
  type: "lines",
  linesClass: "split-line",
  mask: "lines",          // SplitText auto-creates overflow:hidden wrappers
});
gsap.from(splitLines.lines, {
  yPercent: 100,
  duration: 0.8,
  ease: "expo.out",
  stagger: 0.1,
});

// Always revert when done to restore the original DOM (and accessibility)
// split.revert();
```

GSAP eases worth knowing: `expo.out`, `power4.out`, `back.out(1.7)` (overshoot), `elastic.out(1, 0.3)` (bouncy).

---

## 6. Framer Motion staggered words/chars

```jsx
import { motion } from "framer-motion";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.04, delayChildren: 0.1 } },
};
const child = {
  hidden: { y: "110%", opacity: 0 },
  show: {
    y: "0%",
    opacity: 1,
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] },
  },
};

export function Headline({ text }) {
  return (
    <motion.h1
      aria-label={text}
      variants={container}
      initial="hidden"
      animate="show"
      style={{ display: "flex", flexWrap: "wrap", overflow: "hidden" }}
    >
      {text.split(" ").map((word, i) => (
        <span key={i} style={{ overflow: "hidden", marginRight: "0.25em" }}>
          <motion.span aria-hidden variants={child} style={{ display: "inline-block" }}>
            {word}
          </motion.span>
        </span>
      ))}
    </motion.h1>
  );
}
```

---

## 7. Remotion per-character reveal

```jsx
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const KineticText = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <h1 aria-label={text} style={{ display: "flex", overflow: "hidden" }}>
      {text.split("").map((char, i) => {
        const delay = i * 2; // 2 frames per char ≈ 33ms at 60fps
        const progress = spring({
          frame: frame - delay,
          fps,
          config: { damping: 200, stiffness: 200, mass: 0.5 },
        });
        const y = interpolate(progress, [0, 1], [110, 0]);
        return (
          <span
            key={i}
            aria-hidden
            style={{
              display: "inline-block",
              transform: `translateY(${y}%)`,
              opacity: progress,
              whiteSpace: "pre",
            }}
          >
            {char}
          </span>
        );
      })}
    </h1>
  );
};
```

---

## 8. Variable-font weight + width animation (CSS)

```css
@keyframes flex {
  0%   { font-variation-settings: "wght" 200, "wdth" 75; }
  100% { font-variation-settings: "wght" 800, "wdth" 125; }
}
.variable {
  font-family: "Roboto Flex", sans-serif;  /* must be a variable font */
  animation: flex 1.2s cubic-bezier(0.65, 0, 0.35, 1) infinite alternate;
}
```

Per-character weight wave (JS, drives a CSS var):

```js
const chars = document.querySelectorAll('.wave .char');
function tick(t) {
  chars.forEach((c, i) => {
    const w = 400 + Math.sin(t / 400 + i * 0.5) * 350; // 50..750
    c.style.fontVariationSettings = `"wght" ${w.toFixed(0)}`;
  });
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
```

---

## 9. SVG stroke draw-on (outline text)

Convert text to outlines in a vector tool (or use a stroked font path), then:

```css
.draw-text path {
  fill: transparent;
  stroke: #fff;
  stroke-width: 2;
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: draw 2s ease forwards;
}
@keyframes draw { to { stroke-dashoffset: 0; } }
```

---

## 10. After Effects expression (per-char delay via index)

On a text layer's position or opacity, using a Text Animator is the native path, but for code-driven control attach this opacity expression with a slider for stagger:

```javascript
// On opacity; "Delay" slider in seconds-per-char
d = thisComp.layer("Controller").effect("Delay")("Slider");
start = inPoint + textIndex * d;   // textIndex via per-character animator
ease(time, start, start + 0.4, 0, 100);
```

In practice prefer AE's Range Selector + offset animator for character stagger; reserve expressions for data-driven or non-linear orderings.

---
Reveal type by line, word, or char with the right rhythm and the words perform. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=kinetic-typography-skills&utm_content=skill_footer&utm_term=kinetic-typography)** — the AI motion agent for editable, on-brand motion graphics.
