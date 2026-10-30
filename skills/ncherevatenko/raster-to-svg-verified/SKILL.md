---
name: raster-to-svg-verified
description: Convert raster line drawings and diagrams into path-based SVG, optionally recover separately editable closed regions, and verify a rendered PNG against the source. Use for faithful tracing and fill removal on white-background line art, rather than generating a new illustration.
license: MIT
---

# Verified raster to SVG

Trace the supplied pixels in their original coordinate system. Keep visible ink
separate from optional editable regions, then verify structure and appearance
as different properties. Read [the method reference](references/method.md) for
signal selection, region recovery, or interpreting comparison scores.

## Choose the scope

Use this workflow for dark line art on a white or bright background. Inspect
the source before choosing a signal:

- Use the default `luminance` signal to preserve grayscale drawing detail.
- Use `channel-max` only when the user wants bright flat fills removed while
  preserving black or neutral gray ink. It can erase colored strokes and does
  not reliably remove dark fills. See the reference before selecting it.
- For photographs, faithful full-color conversion, or alpha-faithful assets,
  choose another workflow. This helper composites input transparency on white.

The user may want a visually faithful drawing, independently editable regions,
or both. A traced ink silhouette does not by itself recover semantic objects.
Do not add interaction, animation, delivery integrations, or subject-specific
geometry unless the user requests them separately.

## Trace and render

Use an existing suitable environment, or create a task-local virtual
environment. The helper needs Python 3.10+, Potrace on `PATH`, and the packages
in `requirements.txt`. It does not install software or use a hosted API.

```bash
python scripts/vectorize.py drawing.png --out output
```

For explicitly requested bright-fill removal:

```bash
python scripts/vectorize.py drawing.png --out output --signal channel-max
```

The command produces SVG paths, a PNG render, the normalized comparison target,
an ink overlay, a difference image, and a JSON report. It preserves canvas
dimensions and never embeds the source bitmap. Existing output files require
`--overwrite`; the input remains unchanged.

## Recover editable regions when needed

Supply a region specification only when individual closed areas are part of
the requested result. Inspect the raster at 1:1, choose seeds inside its visible
areas, and use the [synthetic example](examples/regions.json) as the schema.

```bash
python scripts/vectorize.py drawing.png --out output --regions regions.json
```

Use source-pixel coordinates throughout. The specification records seed points,
optional local barrier repairs, clipping polygons, excluded areas, and merging
settings. Barriers affect region extraction only; they do not rewrite source
pixels or the visible ink layer. A seed that reaches the canvas boundary is
rejected unless an explicit clipping polygon bounds the reconstruction.

Review each recovered area. Preserve meaningful holes, check neighboring
regions for overlap, and assign stable IDs from observed objects or neutral
region names. Never reuse connected-component numbers across a changed mask.
Disclose repaired or inferred borders; closed geometry does not prove identity.

## Verify the result

Read the report and inspect the source, rendered PNG, and overlay at the same
scale. For editable regions, review their boundaries independently of the ink.

- Check valid SVG, the expected `viewBox`, unique IDs, and real paths.
- Check that there are no embedded images, executable content, external asset
  references, or live text requiring a matching font.
- Check every editable region has explicitly closed subpaths and a distinct ID.
- Compare ink F1, foreground RMSE, and boundary distance, together with the
  images. Whole-image RMSE can conceal errors in a mostly blank canvas.

Fix the discrepancy indicated by the comparison, re-render, and compare again.
Change trace parameters for visible-ink errors; change the region specification
for boundary leaks or incorrect region membership. Preserve intermediate output
when the user asks to review it. Do not interpret a visual score as proof of
semantic correctness, and do not claim pixel-perfect equivalence.

Deliver the requested SVG and preview with a concise statement of what was
checked and any reconstructed borders. Publication and messaging require the
user's authorization; this skill does not provide it.
