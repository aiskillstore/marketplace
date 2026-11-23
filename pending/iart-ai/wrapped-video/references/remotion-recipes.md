# Remotion recipes for Wrapped scenes

Runnable scene components and the sequencing that strings them into a recap. All assume the `Wrapped` schema from SKILL.md and a 1080×1920 / 30fps composition.

## The one rule that prevents broken renders

Drive **all** animation from `useCurrentFrame()`. Never use `setState`, `setInterval`, `Date.now()`, or CSS `@keyframes`/`transition` for timing — the renderer snapshots discrete frames, so wall-clock animation flickers or freezes. Everything below derives its state purely from the current frame.

## Staggered top-X list

Each row springs in on a delayed frame so the list builds 1→5. One identical motion per row.

```tsx
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

type Item = { rank: number; label: string; value: number };

export const TopList: React.FC<{ items: Item[]; accent: string }> = ({ items, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 28, padding: "0 80px",
        height: "100%", justifyContent: "center" }}>
      {items.map((it, i) => {
        const delay = i * 8; // 8 frames between rows
        const p = spring({ frame: frame - delay, fps, config: { damping: 200 } });
        const y = interpolate(p, [0, 1], [40, 0]);
        return (
          <div key={it.rank} style={{ opacity: p, transform: `translateY(${y}px)`,
              display: "flex", alignItems: "baseline", gap: 24 }}>
            <span style={{ fontSize: 56, fontWeight: 900, color: accent,
                fontVariantNumeric: "tabular-nums" }}>{it.rank}</span>
            <span style={{ fontSize: 64, fontWeight: 800, color: "#fff", flex: 1 }}>{it.label}</span>
            <span style={{ fontSize: 40, color: "#ffffff99" }}>{it.value}</span>
          </div>
        );
      })}
    </div>
  );
};
```

## Percentile bar (the climax scene)

Bar fills to `percentile` while the number counts up beside it.

```tsx
export const Percentile: React.FC<{ percentile: number; accent: string }> = ({ percentile, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame, fps, config: { damping: 200 } });
  const pct = interpolate(p, [0, 1], [0, percentile]);
  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column",
        justifyContent: "center", padding: "0 80px", gap: 32 }}>
      <span style={{ fontSize: 56, color: "#fff" }}>You're in the top</span>
      <span style={{ fontSize: 200, fontWeight: 900, color: accent,
          fontVariantNumeric: "tabular-nums" }}>{Math.round(pct)}%</span>
      <div style={{ height: 24, borderRadius: 12, background: "#ffffff22" }}>
        <div style={{ width: `${pct}%`, height: "100%", borderRadius: 12, background: accent }} />
      </div>
      <span style={{ fontSize: 40, color: "#ffffff99" }}>of all listeners this year</span>
    </div>
  );
};
```

## Sequencing scenes into the film

Use `<Series>` to lay scenes back-to-back without computing absolute frames by hand. Wrap each in a full-bleed background.

```tsx
import { AbsoluteFill, Series } from "remotion";
import { BigNumber } from "./BigNumber";
import { TopList } from "./TopList";
import { Percentile } from "./Percentile";
import type { Wrapped } from "./schema";

const Bg: React.FC<React.PropsWithChildren<{ color?: string }>> = ({ children, color }) => (
  <AbsoluteFill style={{ background: color ?? "#0a0a0a" }}>{children}</AbsoluteFill>
);

export const Wrapped: React.FC<Wrapped> = (p) => (
  <Series>
    <Series.Sequence durationInFrames={90}>
      <Bg><Intro name={p.name} year={p.year} /></Bg>
    </Series.Sequence>
    <Series.Sequence durationInFrames={120}>
      <Bg><BigNumber value={p.minutesListened} label="minutes listened" accent={p.accent} /></Bg>
    </Series.Sequence>
    <Series.Sequence durationInFrames={120}>
      <Bg><TopList items={p.topArtists} accent={p.accent} /></Bg>
    </Series.Sequence>
    <Series.Sequence durationInFrames={120}>
      <Bg color={p.accent}><Percentile percentile={p.percentile} accent="#fff" /></Bg>
    </Series.Sequence>
    {/* add persona, peak-month, outro the same way */}
  </Series>
);
```

`<Series.Sequence>` resets each child's `useCurrentFrame()` to 0 at its own start, so every scene's springs animate from the beginning — no per-scene frame math.

## Transitions between scenes

For a polished cut, use `@remotion/transitions` instead of hard cuts:

```tsx
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={120}>{/* scene A */}</TransitionSeries.Sequence>
  <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 12 })} />
  <TransitionSeries.Sequence durationInFrames={120}>{/* scene B */}</TransitionSeries.Sequence>
</TransitionSeries>
```

Keep transitions short (8–15 frames) and consistent. A quick fade or vertical slide matches the story-swipe feel; avoid mixing many transition types.

## Fonts

Load a heavy display weight — bold numerals carry the whole look. Use `@remotion/google-fonts` so the font is bundled for batch renders (no FOUT, no missing glyphs in headless rendering):

```tsx
import { loadFont } from "@remotion/google-fonts/Inter";
const { fontFamily } = loadFont();
// apply fontFamily on the root container; use fontWeight 800–900 for headline numbers
```

For a true Wrapped feel, a bespoke heavy grotesque (Inter/Archivo/Anton-style) with `fontVariantNumeric: "tabular-nums"` on every counter keeps digits from jittering as they roll.

## Animation cheatsheet

- `spring({ frame, fps, config: { damping: 200 } })` → smooth 0→1, no overshoot. Lower damping = bouncier.
- `interpolate(spring01, [0,1], [from,to])` → map progress to any range; add `{ extrapolateRight: "clamp" }` to freeze at the end.
- Counters: `Math.round(interpolate(p, [0,1], [0, value]))` + `toLocaleString()` + `tabular-nums`.
- Stagger: feed `frame - i*delay` into each item's spring.
- Hold still: when a scene's payoff is reached, stop animating — let it sit so it can be screenshotted.
