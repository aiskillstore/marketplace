---
name: explainer-video
description: This skill should be used when the user asks to "make an explainer video", "turn this into a short explainer", "write a script and storyboard for a product video", "produce a how-it-works/onboarding video", "sync narration and captions", or "build a 30–90s animated explainer". Covers script→storyboard→scene build→narration/caption sync→edit→polish.
version: 0.1.0
---

# Explainer Video

Turn one message into a paced, narrated 30–90s short. Run the full pipeline: script → storyboard → scene build → narration/caption sync → edit → polish, with a consistent style system throughout.

## When to use

- Produce a 30–90s product, how-it-works, onboarding, or concept video.
- Go from a raw idea or feature to a script, storyboard, and assembled piece.
- Sync narration to visuals and add captions for muted playback.

## Story structure (decide this first)

An explainer is an argument, not a feature tour. Before any pipeline step, lock the narrative so every later choice serves it.

- **One core idea.** A single sentence the viewer should be able to repeat afterward. If you can't state it in one line, the video has no spine — cut scope until you can. Everything that doesn't serve that idea gets dropped, not shrunk.
- **Script-first.** The VO is the spine; visuals illustrate the line being spoken, never lead it. Write and time the words before you storyboard or animate — it is far cheaper to cut a sentence than a built scene.
- **Earn the "how" with stakes.** Don't jump from problem to mechanism. Make the viewer *feel* the cost of the problem first; that tension is what makes them watch the solution.

The explainer story arc — a beat per stage, in order:

| Stage | Narrative job | What the viewer should think |
|---|---|---|
| Problem | Name the pain in their words | "That's me." |
| Stakes | Show what the pain costs (time, money, risk) | "I need this fixed." |
| Solution | Introduce the product/idea as the fix, in one line | "Oh — that solves it." |
| How it works | The mechanism in 1–3 concrete steps | "I get how it does that." |
| Payoff / CTA | The after-state + one next action | "I want that. I'll do X." |

(The `Script formula` table below maps these stages to runtime shares and word budgets — this section is the *why* and order; that one is the *how long*.)

### Pick one analogy and ride it

Abstract mechanisms land when mapped to something the viewer already knows. Choose a single metaphor and keep it consistent across scenes — switching analogies mid-video resets comprehension.

- Pick a metaphor from the viewer's world (a queue, a thermostat, an assembly line), not the engineering domain.
- One metaphor per video; reuse it for both the visual grammar and the VO wording.
- Test it: if the analogy needs its own explanation, it's the wrong one.

### Pacing per beat

Pace tracks tension. Move quickly through Problem/Stakes to reach the value; slow down on the "how" so each step lands; let the payoff breathe.

| Beat | Feel | Cut rhythm |
|---|---|---|
| Problem / Stakes | Brisk, a little tense | Faster cuts, short holds |
| Solution | A beat of relief | One clear hold |
| How it works | Deliberate, one step at a time | Slowest — hold each step to read |
| Payoff / CTA | Confident, open | Hold the end card; one CTA |

## The pipeline

1. **Script** — one core message. Structure: problem → solution → how → payoff. Write tight voiceover (VO); time it at ~2.3 words/second (≈140 wpm). A 60s video is ~138 words.
2. **Storyboard** — one idea per scene. Sketch each frame plus its transition; map each VO line to a visual.
3. **Build scenes** — animate diagrams/data, kinetic text/keywords, and backgrounds (techniques inlined below).
4. **Narration & captions** — record/generate VO, align scene cuts to VO beats, burn in captions (most plays are muted).
5. **Edit** — cut to the narration, hold each idea long enough to land, remove any scene that doesn't advance the message.
6. **Polish** — color pass, consistent easing, audio mix, end card.

## Script formula

| Beat | Job | Share of runtime |
|---|---|---|
| Problem | Name the pain the viewer feels | ~20% |
| Solution | Introduce the product/idea as the fix | ~15% |
| How | Show the mechanism, 1–3 concrete steps | ~45% |
| Payoff | The outcome + a clear next step (CTA) | ~20% |

Write VO first, in spoken language (contractions, short sentences). Read it aloud and time it before building anything.

## VO timing math

- Pace: ~2.3 words/sec (140 wpm) for clear, friendly narration; slow technical lines to ~2.0.
- Estimate scene length from its VO line: `seconds = words / 2.3`, then add ~0.4s breathing room.
- A scene with no VO (pure visual beat) still needs ≥1.0s to register.

## Scene-build techniques (inlined)

Diagram / data reveal (progressive disclosure: nodes → edges → labels):

```js
import gsap from "gsap";
gsap.set(".edge", { strokeDasharray: 1, strokeDashoffset: 1 });
gsap.timeline()
  .from(".node", { opacity: 0, scale: .85, transformOrigin: "center",
                   duration: .45, stagger: .3, ease: "back.out(1.5)" })
  .to(".edge",  { strokeDashoffset: 0, duration: .5, stagger: .3 }, "-=0.6");
```

Kinetic keyword (word pops in on the stressed syllable):

```css
.kw { display:inline-block; opacity:0; transform:translateY(18px); }
.kw.in { opacity:1; transform:none; transition:all .4s cubic-bezier(.22,1,.36,1); }
```

Count-up stat:

```js
function countUp(el, to, dur=1200){ const t0=performance.now(); (function f(n){
  const k=Math.min(1,(n-t0)/dur), e=1-Math.pow(1-k,3);
  el.textContent=Math.round(to*e).toLocaleString(); if(k<1)requestAnimationFrame(f);})(t0); }
```

Render the assembled piece with Remotion (data-driven, deterministic) or After Effects.

## Caption sync

Captions are mandatory — assume muted autoplay. Use a `.srt`/`.vtt` cue list keyed to the VO. Keep ≤2 lines, ≤42 chars/line, on-screen ≥1.0s, gone before the next line starts.

```
1
00:00:00,300 --> 00:00:02,600
Managing releases by hand is slow.

2
00:00:02,800 --> 00:00:05,400
Shipfast automates the whole pipeline.
```

In Remotion, drive captions from the same timing array used for scene cuts so they never drift.

## Style-system consistency

Lock one type scale, one color grammar (color = meaning, never reassigned), and one easing curve before building scene 2. Reuse the same enter/exit transitions across scenes so the piece feels like one object, not a montage of experiments. Visuals must illustrate the VO line currently spoken — show, don't decorate.

## Output checklist

- Single clear message; every scene advances it.
- VO timed (~2.3 w/s); scene lengths derived from VO.
- Storyboard maps each VO line to a visual.
- Captions burned/available; ≤2 lines, readable.
- Consistent type/color/motion system across all scenes.
- End card with one clear CTA.

## Deliver & verify (rendered stills → MP4)

> **Packaged helper** (`scripts/`): tile your stills with `scripts/contact-sheet.sh sheet.png f-hook.png f-mid.png f-end.png`, then assert the encode with `scripts/probe-mp4.sh out.mp4 [WxH] [fps]`. See `scripts/README.md`.

The assembled explainer is a Remotion composition — frame-deterministic, so any exact frame renders headlessly with no seek harness. Use this tier when the deliverable is an MP4/GIF that carries baked narration and burned captions; for a single web scene, deliver standalone HTML instead.

**Output contract:**
- A Remotion project with the composition registered (`<Composition>` + zod `schema` + `defaultProps`), all motion frame-driven (no timers / `Date.now()` / `Math.random()`).
- Deliverable = the rendered `out/*.mp4` (plus the project, so VO/script/data can be re-rendered).
- Narration via `<Audio src={staticFile()}>`; VO/scene timing baked into props (no realtime audio at render). Captions driven from that same timing array so they never drift.
- Duration data-dependent? compute it in `calculateMetadata`, not by hand.

**Verify loop — render stills → inspect → encode.** Render single frames first (cheap, no encode), inspect them, encode only once the frames are right.

```bash
# Frame-exact stills at start / mid / end — render with the SHIPPED props, not just defaults
npx remotion still Explainer out/f-start.png --frame=0   --props='{...}'
npx remotion still Explainer out/f-mid.png   --frame=N   --props='{...}'
npx remotion still Explainer out/f-end.png   --frame=L   --props='{...}'   # L = durationInFrames - 1

# Inspect: script→storyboard→scene maps onto frames — sample a frame inside EACH scene's hold,
# confirm narration line and caption are synced to the visual at that frame, no text overflow / off-canvas.

# Only after the stills check out, encode:
npx remotion render Explainer out/explainer.mp4 --props='{...}'
```

- `npx remotion compositions` reads `durationInFrames`/`fps` to pick the end frame and per-scene hold frames.
- **README demo GIF for free**: `npx remotion render Explainer out/demo.gif --codec=gif`.

**Before you finish:**
1. `npx remotion still` renders cleanly at frame 0, a frame inside each scene's hold, and last — no errors, no missing assets/fonts.
2. At every sampled scene frame, the caption and the spoken VO line match the visual on screen (no drift).
3. Captions are inside safe areas, ≤2 lines, readable; text is exact and not clipped.
4. Frame-driven only — no `Date.now()` / `Math.random()` / timers; the **shipped** props render correctly (not just `defaultProps`).
5. Full MP4 encoded and plays with narration; (optional) GIF rendered for the README.

## Reference files

- `references/script-to-screen-workflow.md` — full pipeline detail: the problem→solution→how→payoff script formula with a worked example and word budget, VO timing tables, a fill-in storyboard template with timecodes, a per-scene build checklist, caption authoring guidance (VTT/SRT), and a style-system spec sheet for cross-scene consistency.
