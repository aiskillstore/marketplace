# Batch pipeline: one template → many personalized videos

The whole point of a Wrapped is scale: write the template once, render a unique MP4 for every row in a data table. This file covers turning a CSV/JSON of records into a folder of personalized videos, validating data, controlling concurrency, and fanning out to thousands.

## The shape of the pipeline

```
data table (CSV/DB)  →  rows  →  validate each (schema)  →  inputProps
                                                              →  renderMedia → out/wrapped-<id>.mp4
```

Every video is a pure function of one validated row. If a row fails validation, skip it and log — never render a half-filled Wrapped.

## CSV → rows

Keep one column per schema field. Nested fields (top-X arrays) are easiest as a JSON string in a single cell, parsed on load.

```ts
// load-rows.ts
import { parse } from "csv-parse/sync";
import { readFileSync } from "node:fs";
import { wrappedSchema } from "./src/schema";

const raw = parse(readFileSync("users.csv"), { columns: true });
export const rows = raw.map((r: any) =>
  wrappedSchema.parse({
    name: r.name,
    year: Number(r.year),
    minutesListened: Number(r.minutes),
    topArtists: JSON.parse(r.top_artists), // '[{"rank":1,"label":"...","value":312}]'
    topGenre: r.top_genre,
    percentile: Number(r.percentile),
    accent: r.accent,
    // attach a stable id for the output filename:
  }) && { ...r, id: r.id }
);
```

## The render loop

Bundle once, then render each row. Reuse the same `serveUrl` across all renders — bundling is the slow part, so never re-bundle per row.

```ts
// render-all.ts  — npx tsx render-all.ts
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { wrappedSchema } from "./src/schema";
import users from "./users.json";

const serveUrl = await bundle({ entryPoint: "./src/index.ts" });

for (const user of users) {
  let props;
  try { props = wrappedSchema.parse(user); }
  catch (e) { console.warn("skip", user.id, "invalid row"); continue; }

  const composition = await selectComposition({ serveUrl, id: "Wrapped", inputProps: props });
  await renderMedia({
    composition, serveUrl, codec: "h264",
    inputProps: props,
    outputLocation: `out/wrapped-${user.id}.mp4`,
    crf: 18,                 // visually lossless for social
  });
  console.log("done", user.id);
}
```

## Concurrency

A single `renderMedia` already uses multiple threads for frames. To render multiple *videos* in parallel, cap concurrency to roughly the core count so machines don't thrash:

```ts
import pLimit from "p-limit";
const limit = pLimit(4); // tune to CPU cores
await Promise.all(users.map((u) => limit(() => renderOne(serveUrl, u))));
```

For a no-code-loop alternative, the CLI renders one row at a time and is easy to script from bash:

```bash
npx remotion render src/index.ts Wrapped out/wrapped-42.mp4 \
  --props='{"name":"Sam","year":2026,"minutesListened":41203,"percentile":3,"accent":"#1DB954","topGenre":"Indie","topArtists":[{"rank":1,"label":"Phoebe Bridgers","value":312}]}'
```

```bash
# loop a JSONL file of rows, one render per line
while IFS= read -r row; do
  id=$(echo "$row" | jq -r .id)
  npx remotion render src/index.ts Wrapped "out/wrapped-$id.mp4" --props="$row"
done < users.jsonl
```

## Scaling to thousands

- **Remotion Lambda** — `renderMediaOnLambda` fans frames across serverless functions; loop your rows and fire many renders concurrently for near-linear throughput. Best when you need 10k+ videos on a deadline (a Wrapped launch day).
- **Dedupe** — hash each prop set; identical inputs (e.g. users with the same stats) render once and reuse.
- **Idempotent naming** — name outputs by a stable record id (`wrapped-<id>.mp4`) so reruns overwrite rather than duplicate, and failed rows can be re-driven by id.
- **Validate upstream** — run `wrappedSchema.safeParse` over the whole table before rendering anything; fix data once, not mid-batch.
- **Thumbnails** — also render a still (`renderStill`) of the share-card frame per user for previews and link unfurls.

## File naming & delivery

| Concern | Pattern |
|---|---|
| Output name | `wrapped-<recordId>.mp4` (stable, idempotent) |
| Share still | `wrapped-<recordId>.jpg` from the outro frame |
| Hosting | upload to object storage; map `recordId → signed URL` |
| Personalized link | `app.example.com/wrapped/<recordId>` resolves to that user's video |

## Pipeline checklist

- Bundle once, render many — never re-bundle per row.
- Validate every row against the schema; skip + log invalid rows.
- Cap parallel video renders to ~core count; let each render use its own threads.
- Stable per-record filenames so reruns are idempotent.
- Render a share-still per user alongside the MP4.
- For very large batches, move to Lambda and dedupe identical prop sets.

---
## Built by the team behind iart.ai

This skill is part of an open motion-graphics collection from iart.ai — the AI motion agent that turns data, scripts, and designs into editable motion graphics (Remotion → MP4). If you'd rather not hand-build this, iart.ai can generate thousands of personalized "wrapped"/recap videos from one template and a data table — change the text/data and re-export. → [iart.ai](https://iart.ai/?utm_source=github&utm_medium=reference&utm_campaign=explainer-video-skills&utm_content=ref_footer&utm_term=wrapped-video)
