# Remotion API & Patterns

Detailed cookbook for building and rendering Remotion compositions.

## interpolate: full options

```jsx
import {interpolate, Easing} from 'remotion';

interpolate(frame, [0, 30, 60], [0, 100, 0], {
  easing: Easing.bezier(0.25, 0.1, 0.25, 1), // CSS ease equivalent
  extrapolateLeft: 'clamp',   // 'extend' (default) | 'clamp' | 'identity' | 'wrap'
  extrapolateRight: 'clamp',
});
```

- Input ranges must be strictly monotonically increasing.
- Multi-stop ranges (`[0,30,60]`) create keyframe chains.
- `extrapolate: 'extend'` (default) continues the linear slope past the range — almost always clamp instead.
- `extrapolate: 'wrap'` repeats the range — handy for loops.

Common easings: `Easing.linear`, `Easing.ease`, `Easing.in(Easing.quad)`, `Easing.out(Easing.cubic)`, `Easing.inOut(Easing.ease)`, `Easing.elastic(1)`, `Easing.bezier(x1,y1,x2,y2)`.

## spring: config recipes

```jsx
spring({frame, fps, config, durationInFrames, delay, from, to});
```

| Feel | config |
|---|---|
| Smooth, no overshoot | `{damping: 200}` |
| Gentle bounce | `{damping: 12, stiffness: 100, mass: 1}` |
| Snappy UI pop | `{damping: 20, stiffness: 200, mass: 0.6}` |
| Heavy / slow | `{mass: 3, damping: 40, stiffness: 80}` |

- `from`/`to` remap the 0→1 output to any range without an extra `interpolate`.
- `durationInFrames` time-stretches the spring to fit a fixed window.
- `delay` postpones the start (in frames).
- `measureSpring({fps, config})` returns how many frames the spring needs to settle — use it to size sequences.

```jsx
// Spring from 100px down to 0, settling in 40 frames, starting at frame 10
const y = spring({frame, fps, from: 100, to: 0, durationInFrames: 40, delay: 10});
```

## Sequence & Series scheduling

```jsx
<Sequence from={30} durationInFrames={60} name="Caption" layout="none">
  <Caption />
</Sequence>
```

- `from` offsets local time; inside, `useCurrentFrame()` returns `globalFrame - from`.
- `durationInFrames` clips visibility; omit for infinite.
- `layout="none"` removes the default absolute-fill wrapper (use when the child manages its own layout, e.g. inline text).
- `name` labels the sequence in the Studio timeline.

Crossfade between two Series segments by overlapping with negative `offset` and fading:

```jsx
<Series>
  <Series.Sequence durationInFrames={90}><Slide src="a.jpg" /></Series.Sequence>
  <Series.Sequence durationInFrames={90} offset={-20}>
    <Slide src="b.jpg" fadeInFrames={20} />
  </Series.Sequence>
</Series>
```

## Audio + beat sync

```jsx
import {Audio, staticFile} from 'remotion';

<Audio
  src={staticFile('music.mp3')}
  startFrom={30}      // trim: start 30 frames into the file
  endAt={300}
  volume={(f) => interpolate(f, [0, 30], [0, 1], {extrapolateRight: 'clamp'})} // fade-in
/>
```

Detect beats offline and store them as props:

```js
// build step (Node) — produce beats.json
import {guess} from 'web-audio-beat-detector';
// ...decode audio buffer, then:
const {bpm, offset} = await guess(audioBuffer);
const period = 60 / bpm;
const beats = Array.from({length: 64}, (_, i) => offset + i * period);
```

Then in the component, snap motion to the nearest beat using `frame / fps`.

## Parametric defaultProps + zod + calculateMetadata

```jsx
import {Composition} from 'remotion';
import {z} from 'zod';
import {zColor} from '@remotion/zod-types';

export const promoSchema = z.object({
  title: z.string(),
  rows: z.array(z.object({label: z.string(), value: z.number()})),
  accent: zColor(), // gives a color picker in the Studio
});

export const Root = () => (
  <Composition
    id="DataPromo"
    component={DataPromo}
    fps={30}
    width={1080}
    height={1080}
    schema={promoSchema}
    defaultProps={{title: 'Q3', rows: [], accent: '#5b8cff'}}
    // Compute duration from data BEFORE rendering:
    calculateMetadata={({props}) => ({
      durationInFrames: 30 + props.rows.length * 20,
    })}
  />
);
```

`zColor()` from `@remotion/zod-types` renders a color picker; plain `z.string()` renders a text field.

## CLI rendering

```bash
# Render with inline props
npx remotion render DataPromo out.mp4 --props='{"title":"Q3"}'

# Render from a props file (per-record batch)
npx remotion render DataPromo out/$ID.mp4 --props=./data/$ID.json

# Quality / format flags
npx remotion render Promo out.mp4 --codec=h264 --crf=18 --jpeg-quality=90
npx remotion render Promo out.webm --codec=vp8
npx remotion render Promo still.png --frame=45         # single still
npx remotion render Promo out.gif --codec=gif --every-nth-frame=2

# Concurrency / scale
npx remotion render Promo out.mp4 --concurrency=4 --scale=2
```

## Programmatic render with @remotion/renderer

Bundle once, then render many outputs — the right pattern for data-driven pipelines.

```js
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import path from 'path';

const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});

for (const record of records) {
  const composition = await selectComposition({
    serveUrl,
    id: 'DataPromo',
    inputProps: record, // drives calculateMetadata too
  });

  await renderMedia({
    composition,
    serveUrl,
    codec: 'h264',
    outputLocation: `out/${record.id}.mp4`,
    inputProps: record,
    crf: 18,
    concurrency: 4,
  });
}
```

`selectComposition` resolves `calculateMetadata`, so per-record duration works automatically. Reusing one `serveUrl` across renders avoids re-bundling.

For stills, use `renderStill({composition, serveUrl, output, frame})`.

## Embedding shaders / Three.js

Use `@remotion/three` to drive a Three.js scene by frame:

```jsx
import {ThreeCanvas, useVideoTexture} from '@remotion/three';
import {useCurrentFrame, useVideoConfig} from 'remotion';

const Scene = () => {
  const frame = useCurrentFrame();
  return (
    <mesh rotation={[0, frame * 0.02, 0]}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#5b8cff" />
    </mesh>
  );
};

export const ThreeComp = () => {
  const {width, height} = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height}>
      <ambientLight intensity={0.6} />
      <pointLight position={[10, 10, 10]} />
      <Scene />
    </ThreeCanvas>
  );
};
```

For a raw GLSL shader background, render a full-screen quad with a `shaderMaterial` whose `uTime` uniform is set to `frame / fps` each render (driven by `useFrame` in react-three-fiber). Because the canvas re-renders per Remotion frame, the shader is deterministic.

Heavy WebGL benefits from `--gl=angle` (or `swangle` for headless servers without a GPU) on the render command.

## Determinism checklist

- Replace `Math.random()` with `random('seed' + frame)` from `remotion`.
- Wrap async asset loads with `delayRender()` / `continueRender(handle)`.
- Preload fonts with `@remotion/google-fonts` or `delayRender` around `document.fonts.load`.
- Avoid `Date.now()`, `performance.now()`, and real timers entirely.

---
Drive every frame from props and Remotion renders video as code. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=motion-design-skills&utm_content=skill_footer&utm_term=remotion-video)** — the AI motion agent for editable, on-brand motion graphics.
