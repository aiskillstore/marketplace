# Script-to-Screen Workflow — Cookbook

The full explainer pipeline with templates, timing math, and a worked example.

## 1. Script formula: problem → solution → how → payoff

| Beat | Goal | Runtime share | Notes |
|---|---|---|---|
| Hook/Problem | Make the viewer feel the pain in one line | ~20% | Open mid-tension; no logo-first intros |
| Solution | Name the product/idea as the fix | ~15% | One sentence, plain language |
| How | Show the mechanism in 1–3 concrete steps | ~45% | This is the meat; each step = one scene |
| Payoff + CTA | The outcome and the single next action | ~20% | One CTA, not three |

Write VO first, in spoken language: contractions, short sentences, one idea per line. Read aloud and time with a stopwatch before touching any animation.

### Worked example (60s, ~138-word budget)

```
[PROBLEM ~12s, ~28w]
Shipping software still means a dozen manual steps.
Someone forgets one, and the release breaks at 2am.

[SOLUTION ~9s, ~21w]
Shipfast turns that whole checklist into one button.
Push your code, and it takes over from there.

[HOW ~27s, ~62w]
First, it runs your tests in parallel — green in seconds, not minutes.
Then it builds, signs, and stages the release automatically.
You get a preview link to click through before anything goes live.
One approval, and Shipfast rolls it out region by region, watching for errors.

[PAYOFF + CTA ~12s, ~27w]
No more 2am pages. No more forgotten steps.
Just ship — and let Shipfast handle the rest.
Start free at shipfast.dev.
```

## 2. VO timing math

- Baseline pace: **2.3 words/sec** (≈140 wpm) for friendly narration.
- Technical/number-heavy lines: slow to **~2.0 w/s**.
- `scene_seconds = line_words / pace + 0.4` (breathing room).
- Visual-only beats: minimum **1.0s** to register, longer if there's reading.
- 30s ≈ 69 words · 60s ≈ 138 words · 90s ≈ 207 words (at 2.3 w/s).

Always cut the script to fit the target runtime before building — it is far cheaper to cut words than scenes.

## 3. Storyboard template (fill in per scene)

```
SCENE 01  | t=00:00–00:12 (12.0s)
VO        : "Shipping software still means a dozen manual steps..."
VISUAL    : Cluttered checklist UI, items stacking up, one turns red
KEY MOTION: items fall in (stagger 0.1s), red item shakes
TRANSITION: hard cut on the word "breaks"
CAPTION   : "Shipping software still means a dozen manual steps."
ASSET     : checklist.svg, error-state.png
NOTES     : keep palette muted here — pain feels gray
---
SCENE 02  | t=00:12–00:21 (9.0s)
VO        : "Shipfast turns that whole checklist into one button."
VISUAL    : Clutter collapses into a single glowing button
KEY MOTION: scale-collapse to center, button pulse
TRANSITION: match-cut button -> next scene
...
```

Rules for the board:

- One idea per scene. If a scene has two ideas, split it.
- Every VO line maps to exactly one visual intent.
- Note the transition (cut / match-cut / wipe) and the exact word it lands on.
- Track assets per scene so the build phase has a shopping list.

## 4. Per-scene build checklist

- [ ] Visual illustrates the spoken line (show, don't decorate).
- [ ] Enter timing matches when the VO introduces the idea.
- [ ] Uses the locked type scale, color grammar, and easing curve.
- [ ] Holds long enough to read (derive from VO + reading time).
- [ ] Exit/transition lands on the planned word.
- [ ] Reduced-motion: scene still reads as a static frame.
- [ ] Caption cue authored with matching in/out times.

### Inlined scene techniques

Progressive diagram reveal (nodes → edges → labels):

```js
import gsap from "gsap";
gsap.set(".edge", { strokeDasharray: 1, strokeDashoffset: 1 });
gsap.timeline({ defaults: { ease: "power2.out" } })
  .from(".node",  { opacity: 0, scale: .85, transformOrigin: "center",
                    duration: .45, stagger: .3, ease: "back.out(1.5)" })
  .to(".edge",   { strokeDashoffset: 0, duration: .5, stagger: .3 }, "-=0.6")
  .from(".label", { opacity: 0, y: 6, duration: .3, stagger: .12 }, "-=0.4");
```

Kinetic keyword stagger:

```js
gsap.from(".headline .word", { yPercent: 120, opacity: 0,
  duration: .4, stagger: .05, ease: "power3.out" });
```

Bar grow + count-up stat:

```css
.bar{ transform:scaleY(0); transform-origin:bottom;
      transition:transform .6s cubic-bezier(.22,1,.36,1); }
.bar.in{ transform:scaleY(1); }
```

```js
function countUp(el,to,dur=1200){const t0=performance.now();(function f(n){
  const k=Math.min(1,(n-t0)/dur),e=1-Math.pow(1-k,3);
  el.textContent=Math.round(to*e).toLocaleString();if(k<1)requestAnimationFrame(f);})(t0);}
```

Remotion caption-from-timing (single source of truth):

```jsx
import { useCurrentFrame, useVideoConfig } from "remotion";
const cues = [
  { from: 0.3, to: 2.6, text: "Managing releases by hand is slow." },
  { from: 2.8, to: 5.4, text: "Shipfast automates the whole pipeline." },
];
export const Captions = () => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  const t = frame / fps;
  const cue = cues.find(c => t >= c.from && t <= c.to);
  return cue ? <div className="cap">{cue.text}</div> : null;
};
```

## 5. Caption authoring guidance

- Assume muted autoplay — captions are not optional.
- ≤2 lines, ≤42 characters/line.
- On-screen ≥1.0s; clear before the next cue appears.
- Break lines at clauses, not mid-phrase.
- Match cue timing to the VO array used for cuts so captions never drift.

Minimal VTT:

```
WEBVTT

00:00.300 --> 00:02.600
Managing releases by hand is slow.

00:02.800 --> 00:05.400
Shipfast automates the whole pipeline.
```

## 6. Style-system spec sheet (lock before scene 2)

```
TYPE     : Display = Inter 700 / 56px ; Body caption = Inter 500 / 28px
COLOR    : bg #0B0F14 · primary #0A84FF · success #30D158 · warn #FF9F0A · text #F5F7FA
           (color = meaning; never reassign mid-video)
EASING   : enter cubic-bezier(.22,1,.36,1) · exit cubic-bezier(.4,0,1,1)
TIMING    : standard enter 0.4s · scene hold ≥1.0s · transition 0.25–0.4s
TRANSITION: default = hard cut on stressed word; match-cut for related scenes
MOTION    : consistent enter/exit across scenes; one idea per beat
SAFE      : keep text inside 90% center safe area for multi-platform crops
```

Consistency is what makes a string of scenes feel like a single film. Reuse the same enter/exit transitions and the same curve everywhere; vary content, not grammar.

---
Lock the script and the VO timing first, and the scenes assemble cleanly. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=explainer-video-skills&utm_content=skill_footer&utm_term=explainer-video)** — the AI motion agent for editable, on-brand motion graphics.
