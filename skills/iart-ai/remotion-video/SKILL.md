---
name: remotion-video
description: This skill should be used when the user asks to "make a video with Remotion", "create a programmatic/data-driven video in React", "render an MP4/GIF from code", "animate with useCurrentFrame/interpolate/spring", "sync video to audio/beats", or "render a templated video per record headlessly". Covers building React compositions and rendering them via CLI or @remotion/renderer.
version: 0.1.0
---

# Remotion (Programmatic Video)

Build real MP4/GIF/WebM videos in React. Every frame is a pure function of `useCurrentFrame()`, so output is deterministic, scrubbable, diffable, and renderable in CI. The code-first alternative to After Effects for templated and data-driven motion graphics.

## When to use

- Render MP4/GIF/WebM from code (social clips, title cards, explainers).
- Templated/data-driven videos: one composition, many outputs from props (per-user, per-record, per-row of a CSV/DB).
- Motion graphics that must be versioned, code-reviewed, and rendered in CI without a GUI.
- Programmatic audio sync, charts that animate from data, or embedding shaders/Three.js into video.

## Core techniques

### Frame-driven animation

Animation is derived from the current frame, never from `setState` or `requestAnimationFrame`. `interpolate` maps an input range to an output range; `spring` produces physically natural motion.

```jsx
import {useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';

export const Title = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Fade in over frames 0-30, then stay (clamp prevents over/undershoot).
  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Spring entrance; divide by spring duration is unnecessary — drive transforms directly.
  const scale = spring({frame, fps, config: {damping: 200, mass: 1, stiffness: 100}});

  return <h1 style={{opacity, transform: `scale(${scale})`}}>Hello</h1>;
};
```

Always clamp `interpolate` unless an intentional overshoot is desired — by default it extrapolates linearly past the range, which produces opacity > 1 or negative values.

### Scheduling: Sequence and Series

`<Sequence>` shifts time: children see `frame` reset to 0 at the sequence's `from`. Use it to place clips on a timeline. `<Series>` lays out back-to-back segments without manual offset math.

```jsx
import {Sequence, Series, AbsoluteFill} from 'remotion';

export const Timeline = () => (
  <AbsoluteFill style={{backgroundColor: 'black'}}>
    <Sequence from={0} durationInFrames={60}><Intro /></Sequence>
    <Sequence from={60} durationInFrames={90}><Body /></Sequence>

    {/* Series auto-sequences; offset overlaps the previous segment for crossfades */}
    <Series>
      <Series.Sequence durationInFrames={60}><ShotA /></Series.Sequence>
      <Series.Sequence durationInFrames={60} offset={-15}><ShotB /></Series.Sequence>
    </Series>
  </AbsoluteFill>
);
```

### Composition registration + parametric props

The `<Composition>` declares id, size, fps, duration, and `defaultProps`. A zod schema makes props type-safe and editable in the Studio sidebar.

```jsx
import {Composition} from 'remotion';
import {z} from 'zod';

export const schema = z.object({
  title: z.string(),
  accent: z.string(),
  fps: z.number().default(30),
});

export const Root = () => (
  <Composition
    id="Promo"
    component={Promo}
    durationInFrames={150}
    fps={30}
    width={1080}
    height={1920}
    schema={schema}
    defaultProps={{title: 'Launch', accent: '#5b8cff', fps: 30}}
  />
);
```

To make duration data-dependent, use `calculateMetadata` on the Composition to compute `durationInFrames` from props (e.g. number of rows × frames per row) before render.

### Audio and beat sync

```jsx
import {Audio, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BEATS_SEC = [0.5, 1.0, 1.5, 2.0]; // detected offline
export const Music = ({children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const onBeat = BEATS_SEC.some((b) => Math.abs(t - b) < 1 / fps);
  return (
    <>
      <Audio src={staticFile('track.mp3')} />
      <div style={{transform: `scale(${onBeat ? 1.06 : 1})`}}>{children}</div>
    </>
  );
};
```

Detect beats offline (e.g. with `web-audio-beat-detector` or aubio) and bake the timestamps into props — never analyze audio at render time, since headless rendering has no realtime audio clock.

### Rendering

Preview in the browser-based Studio; render headlessly via CLI or the programmatic API.

```bash
npx remotion studio                                  # interactive preview
npx remotion render Promo out/promo.mp4 \
  --props='{"title":"Launch","accent":"#f43"}'        # pass parametric props
npx remotion render Promo out.gif --codec=gif         # GIF output
```

For batch/data-driven pipelines, render in Node with `@remotion/renderer` (bundle once, render many) — see the reference file.

## Deliver & verify (rendered stills → MP4)

> **Packaged helper** (`scripts/`): tile your stills with `scripts/contact-sheet.sh sheet.png f-hook.png f-mid.png f-end.png`, then assert the encode with `scripts/probe-mp4.sh out.mp4 [WxH] [fps]`. See `scripts/README.md`.

Remotion is frame-deterministic by construction — every frame is a pure function of `useCurrentFrame()`, so you can render any exact frame headlessly with **no seek harness** (this is the heavy-tier counterpart to a web scene's `?t=N`). Use this tier when the output must be an MP4/GIF, must carry exact numbers/text, or batches from data; for a lightweight web animation, deliver standalone HTML instead.

**Output contract:**
- A Remotion project with the composition registered (`<Composition>` + zod `schema` + `defaultProps`), all motion frame-driven (no timers / `Date.now()` / `Math.random()`).
- Deliverable = the rendered `out/*.mp4` (plus the project, so the user can re-render with new props/data).
- Duration data-dependent? compute it in `calculateMetadata`, not by hand.

**Verify loop — render stills → inspect → encode.** Render single frames first (cheap, no video encode), inspect them, and encode the full video only once the frames are right.

```bash
# 1. Frame-exact stills at start / mid / end (PNG, headless, fast)
npx remotion still Promo out/f-start.png --frame=0
npx remotion still Promo out/f-mid.png   --frame=75
npx remotion still Promo out/f-end.png   --frame=149   # last frame = durationInFrames - 1
#    render with the SAME props you'll ship, not just defaultProps:
#    npx remotion still Promo out/f-mid.png --frame=75 --props='{"title":"Launch"}'

# 2. Inspect each PNG — fidelity (matches brief; numbers/text correct) AND
#    artifacts (text overflow, off-canvas, clipped safe-area, missing font, wrong data binding).

# 3. Only after the stills check out, encode the video:
npx remotion render Promo out/promo.mp4 --props='{"title":"Launch"}'
```

- Use `npx remotion compositions` to read each composition's `durationInFrames`/`fps` and pick the end frame.
- **Data-driven / batch**: verify ONE representative props set via stills *before* batch-rendering all rows — catch a layout bug once instead of N times.
- **README demo GIF for free**: `npx remotion render Promo out/demo.gif --codec=gif` produces the first-screen proof clip (Direction D).

**Before you finish:**
1. `npx remotion still` renders cleanly at frame 0, mid, and last — no errors, no missing assets/fonts.
2. Numbers/text are exact and inside safe areas at every checked frame.
3. Frame-driven only — no `Date.now()` / `Math.random()` / timers (determinism holds in CI).
4. Props are zod-typed; the **shipped** props render correctly (not just `defaultProps`).
5. Full MP4 encoded and plays; (optional) GIF rendered for the README.

## Quick reference

| Need | Use |
|---|---|
| Map time → value | `interpolate(frame, [a,b], [x,y], {extrapolateRight:'clamp'})` |
| Natural easing | `spring({frame, fps, config})` |
| Place a clip at t | `<Sequence from durationInFrames>` |
| Back-to-back shots | `<Series>` |
| Audio | `<Audio src={staticFile(...)} />` |
| Frame ↔ seconds | `frame / fps` |
| Loop a value | `frame % period` then interpolate |
| Editable props | zod `schema` on `<Composition>` |
| CI render | `npx remotion render` or `@remotion/renderer` |

## Gotchas

- Never use `Math.random()`, `Date.now()`, or animation timers — they break determinism. Use `random(seed)` from Remotion for stable per-frame randomness.
- Load fonts and assets via `staticFile()` and wait with `delayRender`/`continueRender`, or fonts pop in mid-render.
- Default `interpolate` extrapolates — clamp it.
- `useCurrentFrame` inside a `<Sequence>` is local (starts at 0); use `useVideoConfig().durationInFrames` for absolute timing.

## Reference files

- `references/api-and-patterns.md` — `interpolate` options and `Easing`, spring config recipes, Sequence/Series scheduling, `<Audio>` + beat-sync, parametric `defaultProps` with zod + `calculateMetadata`, CLI flags, programmatic `@remotion/renderer` batch rendering, and embedding GLSL shaders / Three.js (`@remotion/three`).
