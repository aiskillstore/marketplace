---
name: wrapped-video
description: This skill should be used when the user asks to "make a Spotify Wrapped style video", "build a year in review / year-in-review video", "create a personalized data video", "generate a recap video", "build a wrapped video generator", "turn a data table into shareable videos", or "make per-user stat videos". Covers the data row → one shareable video pattern, the Wrapped scene grammar (big-number reveals, top-X lists, superlatives), animated data counters, vertical 9:16 framing, and batch-rendering many personalized videos from one template.
version: 0.1.0
---

# Wrapped Video

Build a "Spotify Wrapped"-style recap: take a row of data about one person (or account, team, year) and turn it into a punchy, shareable vertical video. The core idea is **one template × a data table → many personalized videos**. Write the template once, then render a unique film for every row.

## When to use

- Year-in-review / "your 2026 wrapped" recaps for any product with per-user stats.
- Personalized data videos: fitness year, reading year, spending recap, gaming stats, sales rep recap, student progress.
- Any time the deliverable is "the same video, but with each person's numbers" — at 1 or 100,000 copies.

This is a **data → share-bait** pattern, not a hand-edited film. If there is no data table (or no per-record data), use a different skill.

## The two non-negotiables

1. **Data drives everything.** Every headline, number, name, and color comes from props, never hardcoded. A scene that can't be filled from a data row does not belong in a Wrapped.
2. **Built to be screenshotted.** Each scene must read in under 2 seconds and look good frozen — that frozen frame is what gets shared to a story. Design for the pause, not the play.

## The Wrapped scene grammar

A Wrapped is a fixed sequence of short scene *types*, each ~2.5–4s. Pick 5–7 and order them as a build. Same grammar every year; only the data and palette change.

| Scene type | Job | Data shape |
|---|---|---|
| Intro / "Your 2026, wrapped" | Brand the moment, set palette | name, year |
| Big-number reveal | One hero stat, counts up huge | one number + unit + label |
| Top-X list | Ranked 1→5, staggered in | array of `{rank, label, value}` |
| Superlative / persona | "You're in the top 1%", an archetype | computed tier/label |
| Comparison | "more than 92% of listeners" | percentile or ratio |
| Time/heatmap | "your busiest month was March" | series or peak |
| Outro / share card | Logo + handle + CTA, holds still | name, handle |

Order as a crescendo: small context first, biggest/most personal stat as the climax, then the still share card. See `references/scene-grammar.md` for a full 7-scene storyboard with timings.

## The recap story arc

The scene grammar is the skeleton; the *arc* is what makes a Wrapped feel like a gift instead of a dashboard. A recap is a tiny five-beat drama about one viewer — sequence it so each reveal feels bigger and more personal than the last.

| Beat | Job | Maps to |
|---|---|---|
| Build-up | Brand the moment, promise it's theirs | Intro: "{name}, your {year}" |
| Escalating reveals | Stack stats that rise in stakes | Top-X, genres, time patterns |
| The "big number" | One hero stat, max scale, held longest | Big-number / count-up climax |
| Personalized superlative | Name *who they are*, not just what they did | Persona/percentile tier |
| Shareable payoff | A still poster they want to post | Outro share card |

**Sequence stats for rising impact — smallest first, biggest last.** Rank every stat by emotional payload (raw size, rarity, how flattering) and play them in ascending order. Never open on the hero number: there's nowhere to climb after it, and the rest of the film feels like a comedown. Hold the climax stat largest and longest; everything before it is set-up.

**The hook is "this is about YOU."** A Wrapped wins because the viewer is the protagonist. Earn that in the first 2 seconds: lead with their name, use their per-user `accent`, and write every line in second person ("You listened to 412 artists"). Generic copy ("Top genre: Indie") breaks the spell — reframe as "You're an Indie kind of person." If a frame would read identically for two different users, it isn't pulling its weight.

**Design the final share-frame as the destination.** The whole arc exists to deliver a poster worth posting. The outro is not a credits roll — it's the payoff: the headline superlative or hero number restated, name + @handle, logo, one short CTA, holding **completely still ≥2s** so a screenshot or auto-loop lands clean. Decide this frame first and build the crescendo toward it. Copywriting tiers and the full storyboard are in `references/scene-grammar.md`.

## Data → video shape

Define a typed schema for one record. The whole video is a pure function of it.

```ts
// src/schema.ts
import { z } from "zod";
export const wrappedSchema = z.object({
  name: z.string(),
  year: z.number(),
  minutesListened: z.number(),
  topArtists: z.array(z.object({ rank: z.number(), label: z.string(), value: z.number() })),
  topGenre: z.string(),
  percentile: z.number(), // 0–100, "top X%"
  accent: z.string(),     // per-user palette, e.g. "#1DB954"
});
export type Wrapped = z.infer<typeof wrappedSchema>;
```

Register it as `defaultProps` + `schema` on the composition so each render just swaps props.

```tsx
// src/Root.tsx
import { Composition } from "remotion";
import { Wrapped as Recap } from "./Wrapped";
import { wrappedSchema } from "./schema";

export const Root = () => (
  <Composition
    id="Wrapped"
    component={Recap}
    schema={wrappedSchema}
    durationInFrames={30 * 22}  // 22s @ 30fps
    fps={30}
    width={1080} height={1920}  // 9:16 vertical — the share format
    defaultProps={{ name: "Sam", year: 2026, minutesListened: 41203,
      topArtists: [{ rank: 1, label: "Phoebe Bridgers", value: 312 }],
      topGenre: "Indie", percentile: 3, accent: "#1DB954" }}
  />
);
```

## The signature move: the big-number counter

The count-up is the heartbeat of every Wrapped. Drive it from `useCurrentFrame()` (never `setState`/`setInterval` — that flickers on render), ease it with a spring, and format with `toLocaleString()`.

```tsx
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

export const BigNumber: React.FC<{ value: number; label: string; accent: string }> =
({ value, label, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame, fps, config: { damping: 200 } }); // 0→1, settles
  const shown = Math.round(interpolate(progress, [0, 1], [0, value]));
  const pop = interpolate(progress, [0, 1], [0.6, 1]); // overshoot-free scale-in
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center",
        justifyContent: "center", height: "100%", transform: `scale(${pop})` }}>
      <span style={{ fontSize: 220, fontWeight: 900, color: accent, lineHeight: 1,
          fontVariantNumeric: "tabular-nums" }}>{shown.toLocaleString()}</span>
      <span style={{ fontSize: 48, color: "#fff", marginTop: 24 }}>{label}</span>
    </div>
  );
};
```

Use `tabular-nums` so digits don't jitter width as they roll. For the top-X list, reuse one spring per item with a staggered `delay` (rank 1 first) — see `references/remotion-recipes.md`.

## Vertical 9:16, designed for the pause

Render **1080×1920**. Stories/Reels/TikTok crop and overlay UI, so keep all type and key numbers inside the **center 80% height**, clear of the **top 12%** and **bottom 18%**. One bold idea per frame, oversized type, high-contrast accent on a flat/gradient background. Per-user `accent` color makes each share feel personal. Full safe-area map in `references/scene-grammar.md`.

## Batch: one template → many videos

The payoff. Render every data row to its own MP4 with `renderMedia`, passing the row as `inputProps`. Generate a CSV of jobs, loop, name files per record.

```ts
// render-all.ts  — run with: npx tsx render-all.ts
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { wrappedSchema } from "./src/schema";
import users from "./users.json"; // array of rows matching the schema

const serveUrl = await bundle({ entryPoint: "./src/index.ts" });
for (const user of users) {
  const props = wrappedSchema.parse(user);            // validate the row
  const comp = await selectComposition({ serveUrl, id: "Wrapped", inputProps: props });
  await renderMedia({
    composition: comp, serveUrl, codec: "h264",
    inputProps: props,
    outputLocation: `out/wrapped-${user.id}.mp4`,
  });
  console.log("rendered", user.id);
}
```

For thousands of rows, fan out across machines/Lambda and dedupe identical prop sets. Pipeline, scaling, and a Node + CLI batch variant are in `references/batch-pipeline.md`.

## Build checklist

- Every visible string/number comes from props; nothing hardcoded.
- 5–7 scenes, crescendo order, biggest/most personal stat as the climax.
- Numbers count up via `useCurrentFrame` + spring, `tabular-nums`, locale-formatted.
- 9:16 1080×1920; key content in center 80%, clear of top 12% / bottom 18%.
- Each scene reads in <2s and looks good frozen (it will be screenshotted).
- One schema validates every row before render; batch script names files per record.

## Deliver & verify (rendered stills → MP4)

> **Packaged helper** (`scripts/`): tile your stills with `scripts/contact-sheet.sh sheet.png f-hook.png f-mid.png f-end.png`, then assert the encode with `scripts/probe-mp4.sh out.mp4 [WxH] [fps]`. See `scripts/README.md`.

A Wrapped is a Remotion composition rendered per data row — frame-deterministic, so any exact frame renders headlessly with no seek harness. The deliverable is an MP4 (often many) carrying each person's exact numbers; verify one representative row by stills before you batch.

**Output contract:**
- A Remotion project with the composition registered (`<Composition>` + zod `schema` + `defaultProps`), all motion frame-driven (no timers / `Date.now()` / `Math.random()` — count-ups via `useCurrentFrame` + spring).
- Deliverable = the rendered `out/wrapped-*.mp4` per row (plus the project, so any row re-renders).
- Per-user stats baked into props and validated by the schema before render; 9:16 1080×1920.
- Duration data-dependent? compute it in `calculateMetadata`, not by hand.

**Verify loop — stills of ONE row → inspect → batch.** Render a representative user's frames first (cheap, no encode); catch a layout/data bug once instead of N times.

```bash
# Frame-exact stills at start / mid / end for ONE representative row — pass that row as props
npx remotion still Wrapped out/f-start.png --frame=0   --props='{...one user...}'
npx remotion still Wrapped out/f-mid.png   --frame=N   --props='{...one user...}'
npx remotion still Wrapped out/f-end.png   --frame=L   --props='{...one user...}'   # L = durationInFrames - 1

# Inspect: every visible string/number comes from that row and is EXACT (big-number reveal lands on the
# real value, top-X ranks/labels correct); key content inside center 80%, clear of top 12% / bottom 18%.

# Only after the representative stills check out, batch-render every row:
npx tsx render-all.ts
```

- `npx remotion compositions` reads `durationInFrames`/`fps` to pick the end frame and the big-number's settle frame.
- **README demo GIF for free**: `npx remotion render Wrapped out/demo.gif --codec=gif --props='{...}'`.

**Before you finish:**
1. `npx remotion still` renders cleanly at frame 0, mid, and last for the representative row — no errors, no missing assets/fonts.
2. Big-number reveal lands on the EXACT prop value at its settle frame; top-X ranks/labels/values match the row.
3. 9:16: key numbers/type inside center 80%, clear of top 12% / bottom 18%; each checked frame reads frozen.
4. Frame-driven only — no `Date.now()` / `Math.random()` / timers; schema validates every row before batch.
5. Representative MP4 encoded and plays; then batch all rows (file per record); (optional) GIF for the README.

## Reference files

- `references/scene-grammar.md` — full 7-scene storyboard with frame timings, the build/crescendo logic, superlative & percentile copywriting patterns, and the 9:16 safe-area map.
- `references/remotion-recipes.md` — runnable scene components: staggered top-X list, percentile bar, scene sequencing with `<Series>`, transitions, fonts, and the no-flicker animation rules.
- `references/batch-pipeline.md` — CSV/JSON → many MP4s: schema validation, the render loop, concurrency, Lambda fan-out, and file naming.
