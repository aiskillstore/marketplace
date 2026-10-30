# Tracing, region recovery, and verification

This reference covers dark line drawings and diagrams in source-pixel
coordinates. Vectorization converts the raster into SVG; rasterization renders
that SVG back to PNG for comparison. These are separate operations.

## Select the ink signal

Luminance preserves ordinary neutral drawing detail but treats colored fills
as gray. When bright fills must disappear, `max(R, G, B)` can isolate neutral
ink without repainting source pixels.

For black ink with coverage `a` over a flat color `B`, the pixel is approximately
`C = (1-a)B`. If at least one channel of `B` is 255, then
`max(C) = 255(1-a)`. That maximum acts as a white-background ink signal. Neutral
gray source pixels retain their gray level. JPEG compression makes the model
approximate, so compare the normalized target and inspect fine strokes.

This is a conditional preprocessing choice. It discards saturated colored
strokes and retains unwanted dark or desaturated fills. It is unsuitable for
general color restoration, colored handwriting, photographs, or a requirement
to preserve every original color. Do not apply it automatically because an
input contains color.

The helper reads EXIF orientation and composites transparency on white before
forming the signal. `--background transparent` changes the output canvas; it
does not make this an alpha-faithful tracing method. Partial-alpha edges may
carry a white-matte appearance on other backgrounds.

## Keep ink and editable geometry separate

Potrace traces occupied pixels, including dark text and varying line widths,
into filled outlines. These are actual paths, but a long outline can cross
many intended objects. A path count alone cannot establish editability.

When closed areas are needed, extract them from a separate barrier mask:

1. Threshold the normalized signal into barriers and empty pixels.
2. Apply only explicitly specified gap repairs in that extraction mask.
3. Find four-connected empty components and select them using source-coordinate
   seeds. Reject a seed in the exterior unless a clipping polygon is provided.
4. Merge only selected components. Optional morphological closing can bridge
   narrow separator gaps; it can also erase small holes or move borders.
5. Fill enclosed holes only when intended. Use exclusions for meaningful holes.
   Keep all selected disconnected fragments rather than dropping smaller ones.
6. Trace each recovered mask as a named closed path below the visible ink.

White label halos can break an otherwise visible border. Record the local
bridge or clip used to recover that border; do not pretend the missing pixels
were observed. A source-dependent repair belongs in the region JSON, not in
the reusable implementation. A repaired boundary needs human visual review.

The helper reports overlap between region masks. Some layered objects overlap
intentionally; adjacent partition regions generally must not. Inspect the
actual use before deciding whether overlap is an error. Component membership,
reconstructed geometry, and semantic naming remain distinct claims.

## Region specification

Use integer `[x, y]` seeds and polygons in original source-pixel coordinates.
The example has two abstract compartments and one recorded border repair:

```json
{
  "canvas": [360, 240],
  "threshold": 190,
  "barriers": [{"points": [[180, 102], [180, 138]], "width": 3}],
  "regions": [
    {"id": "region-left", "seeds": [[70, 150]], "fill_holes": true},
    {"id": "region-right", "seeds": [[280, 150]], "fill_holes": true}
  ]
}
```

`canvas` optionally checks `[width, height]` before applying coordinates.
`close_radius` defaults to zero. `clip` optionally supplies a polygon that
bounds a region. `exclude_seeds` optionally removes empty components after
hole filling, for example a separate inset area. Region IDs must be unique and
must not use the reserved IDs `background`, `regions`, or `ink`.

The helper stores a checksum of the region specification in the report. Keep
the specification with the output when reproducible region recovery matters.

## Preserve coordinates and curve quality

Use one full-canvas coordinate system and retain Potrace's transform. Its
default SVG unit conversion is not a crop or image scale. Offsets are easy to
lose when extracting only `d` strings; preserve the matching transform.

PBM polarity is another common failure: foreground mask pixels must be written
as black. With Pillow, use `np.where(mask, 0, 255)` before converting to mode
`1`. Reversed polarity can produce a full-canvas path around a cutout.

The grayscale helper traces cumulative threshold masks from light to dark.
Each band's threshold is the midpoint between adjacent gray levels. This
preserves neutral tone detail with a small explicit palette, while accepting
quantization and edge-refitting error. It is not gradient reconstruction.

Lower `--despeckle` if small marks vanish. Adjust `--alphamax` for corner shape
and `--tolerance` for curve optimization. Avoid reducing file size until the
image and named IDs have been verified. A smaller SVG can lose required detail.

## Interpret the comparison

Render the SVG independently with resvg at exactly the original dimensions.
The report compares that render with the **normalized target**, not a colored
source that was intentionally changed. The source checksum identifies the
unmodified input. Nothing in the report contains its filename or local path.

The overlay uses cyan for reference-only ink, magenta for render-only ink, and
dark gray for agreement. The difference image stores absolute pixel error.
Check both at 1:1, especially fine lines, labels, small holes, and crop edges.

The reported metrics answer different questions:

| Metric | Meaning | Limitation |
| --- | --- | --- |
| Canvas RMSE | Overall grayscale rendering error | Blank background can dominate. |
| Foreground RMSE | Error where either image has dark ink | Depends on the stated ink threshold. |
| Ink F1 | Overlap of dark-pixel masks | Ignores intended object identity. |
| Boundary distance p95 | Symmetric edge distance in source pixels | Does not describe the worst 5% of edges. |
| Region overlap pixels | Shared area between extracted masks | Overlap may be intentional in a layered illustration. |

Do not use a universal acceptance threshold. Record the receiving use, inspect
where an error occurs, and tune only the relevant stage. In particular, a
perfect-looking white region layer is visually invisible before editing; ink
comparison cannot validate its recovered boundaries or semantic labels.

## Relationship to existing skills

This package reuses established tracing and render-comparison ideas. It does
not claim a new tracing algorithm. These public skill descriptions were
reviewed when defining its narrower scope:

- [raster-vectorize, reviewed revision](https://github.com/ol-dad-the-guru/raster-vectorize-skill/blob/5c422895785a5ac4b613a15aba4b4de50151ecd5/SKILL.md)
  already covers per-palette Potrace masks, correct PBM handling, exact palette
  assignment, and resvg verification.
- [image-to-svg by shhac, reviewed revision](https://github.com/shhac/skills/blob/764d009a828a67cea0ec7d180f720f98b1b0c3e0/skills/image-to-svg/SKILL.md)
  already covers feature decomposition, measurements, and render-diff loops.
- [image-to-svg by oaustegard, reviewed revision](https://github.com/oaustegard/claude-skills/blob/ee1b2892400033856098adb6b957f307c63fd4d4/image-to-svg/SKILL.md)
  already separates line extraction from fill extraction for graphic artwork.

The addition here is a small, deterministic workflow for conditional bright-fill
neutralization, explicit recorded topology repairs, named region recovery
independent of the ink, and separate structural and visual evidence. Those
details are not specified together in the reviewed skill entrypoints. This
comparison is bounded to the reviewed descriptions, not every implementation
or every skill in the ecosystem. The text and helper implementation in this
package are original; no upstream code or task-specific source assets are
included.
