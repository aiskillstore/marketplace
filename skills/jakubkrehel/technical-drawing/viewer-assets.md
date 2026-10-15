# Build the reusable viewer

Use the bundled viewer for a standalone page with editable drawing state. It includes linework, spacing, dimensions, part selection, coloring and export panels.

Keep the target project's existing components when integrating into an application. The assets provide a working standalone starting point, not a requirement to replace that interface.

## Describe the drawings and their controls

Create a JSON configuration beside the model scripts. Paths resolve relative to that configuration.

```json
{
  "dependencies": "vendor/node_modules",
  "modelScripts": ["model.js"],
  "drawings": [{
    "id": "sleeve",
    "title": "Knurled sleeve",
    "description": "Illustrative sleeve concept with a through bore.",
    "parts": [{"id": "sleeve", "name": "Knurled sleeve"}],
    "parameters": [{
      "key": "length",
      "label": "Sleeve length",
      "min": 20,
      "max": 40,
      "default": 30,
      "step": 1,
      "unit": "mm"
    }]
  }]
}
```

Use an empty `parameters` array when the object has no suitable editable dimensions. IDs stay stable, and drawing IDs use lowercase slugs.

Set `initialView` to `assembled` when the object's normal form or scale is the main subject. Assemblies otherwise start exploded; single-part drawings start assembled.

Install `jspdf`, `svg2pdf.js` and `@fontsource-variable/inter` into the output project's dependency directory, using its existing package manager. Keep its lockfile with the generator.

The builder embeds those packages, the Inter font and its license. The generated page makes no runtime network requests.

## Implement the model boundary

Each model script registers a function in `self.DrawingModels`, keyed by drawing ID. The worker already provides `TechnicalGeometry` and `TechnicalProjection`.

Preserve existing registrations when the viewer includes multiple model scripts.

```js
self.DrawingModels ??= {};
self.DrawingModels.sleeve = (parameters, options) => {
  const G = TechnicalGeometry;
  const p = G.part('sleeve', 'Knurled sleeve', [25, 0, 0]);
  const length = parameters.length;
  if (!Number.isFinite(length) || length < 20 || length > 40) {
    throw Error('Length must be 20–40');
  }
  G.lathe(p, [[0, 5], [length, 5], [length, 3], [0, 3]]);
  G.knurl(p, {x0: 2, x1: length - 2, radius: 5.01, starts: 12, pitch: 40});
  return TechnicalProjection.render([p], options);
};
```

Validate parameter ranges inside the model too. A different renderer may return `{markup}` with SVG geometry using the same group and line-role contract.

Group complete parts with `data-item`, a unique named `id` and a `title`. Apply `data-line-role` to every ink path, preserving explicit surface fills and opening geometry.

Mark filled ink, including engraved text and arrowheads, with `data-ink-fill`. The viewer resolves its source color before export and adapts its preview color with the linework.

Keep occluding faces unmarked and explicitly paper-colored. A filled-ink marker identifies content to recolor, not every closed surface.

Return coordinates in millimeters on the 420 × 297 mm sheet. `TechnicalProjection.render` already fits them, and the viewer draws them unscaled. Model scripts handle `explosion` and `isolated` before projecting, including newly exposed surfaces.

Treat model code as generator source you control. Sanitize imported SVG before it reaches this boundary, following [preview-page.md](preview-page.md).

## Build one portable file

Run [scripts/build-viewer.cjs](scripts/build-viewer.cjs) with the configuration and destination:

```sh
node /path/to/technical-drawing/scripts/build-viewer.cjs drawing.json dist/index.html
```

Deliver the resulting HTML alongside the configuration, model scripts, dependency lockfile and copies of the required builder assets. Record a local regeneration command using those copies.

[assets/viewer.html](assets/viewer.html) owns the shell, [assets/viewer.js](assets/viewer.js) owns interaction state and [assets/export.js](assets/export.js) owns export snapshots.

[assets/theme.js](assets/theme.js) resolves system appearance and saved overrides before the page paints. Run `node scripts/test-theme.cjs` from the skill directory after changing appearance behavior.

[assets/worker.js](assets/worker.js) runs model generation away from the controls. [assets/render-queue.js](assets/render-queue.js) runs one job at a time. A newer preview supersedes queued and running previews, an optional delay debounces slider input and captured export requests always run.

Downloads wait for the current drawing. Run `node scripts/test-render-queue.cjs` from the skill directory after changing request scheduling.

Use [verification.md](verification.md) for geometry checks and [preview-page.md](preview-page.md) for browser and downloaded-file checks. Run `node scripts/test-viewer-builder.cjs` from the skill directory after changing packaging. Successful bundling does not establish visual correctness.
