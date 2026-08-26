# Deterministic lettering and reconstruction manifest

`scripts/compose_panels.py` has two bounded uses: render exact bubbles and text
onto one accepted complete unlettered page, or reconstruct an explicitly
accepted fallback from separately generated panels. It does not generate art,
choose a page structure, repair an image, or judge story evidence.

## Contents

- [Runtime](#runtime)
- [Run](#run)
- [Shared fields](#shared-fields)
- [Schema version 1](#schema-version-1)
- [Schema version 2](#schema-version-2)
- [Geometric and artifact safety](#geometric-and-artifact-safety)

## Runtime

- Python 3.10 or newer
- `Pillow==12.1.1` from `scripts/requirements.txt`
- A locally available CJK font whenever a bubble contains `zh-Hans` text

No font, generated image, character, or private case asset is distributed with the script.

## Run

Use `templates/page-native-lettering-manifest.example.json` for the default
text fallback. Use `templates/compositor-manifest.example.json` only for a
disclosed panel-reconstruction fallback. Both are structural templates, not
directly runnable fixtures. Replace every source path and all-zero hash,
choose real output paths, and create each output parent directory.

Validate every path, frozen hash, decoded image, declared size, crop, frame, reading order, protected region, bubble, font glyph, and final text fit without writing output:

```bash
python3 scripts/compose_panels.py \
  --manifest /path/to/filled-compositor-manifest.json \
  --dry-run
```

Compose the fixed PNG and deterministic JSON ledger declared in the manifest:

```bash
python3 scripts/compose_panels.py \
  --manifest /path/to/filled-compositor-manifest.json
```

Existing outputs are protected. Without `--force`, each final path is committed with an atomic no-clobber link, so a file that appears after the early existence check is not overwritten. Use `--force` only after confirming the target paths. Use `--font /path/to/CJK-font.ttf` to override the manifest font candidates.

Run the public-safe synthetic test, which creates all temporary panel art itself and leaves no fixture behind:

```bash
python3 scripts/self_test_compositor.py
```

## Shared fields

- `schema_version`: use `1` for an existing rectangular manifest or `2` for polygon, rotation, controlled overlap, z-order, or paper matte.
- `artifact_stages`: use `page-native-unlettered -> page-native-unlettered`
  for full-page lettering, or `unlettered-panel -> unlettered-page` for a
  reconstruction fallback. These are artifact stages, not run checkpoints.
- `canvas.size`: exact `[width, height]`, with neither edge above 16,384 pixels and no more than 8,000,000 total pixels because overlays render at 4×.
- `canvas.background`: opaque `#RRGGBB`.
- `panels`: one full-canvas borderless source for page-native lettering, or one
  entry per independently generated reconstruction panel.
  - `id`: unique stable panel id.
  - `reading_order`: consecutive `1..N`.
  - `row`, `column`: consecutive semantic reading rows and left-to-right positions.
  - `source`: input path, resolved relative to the manifest.
  - `expected_sha256`: lowercase SHA-256 of the accepted source. Replace the zero placeholders; a changed file is rejected even when its dimensions match.
  - `expected_size`: exact decoded source dimensions. A mismatch is a hard error.
  - `source_crop`: `[left, top, right, bottom]` inside the source. Its aspect ratio must match `frame` within 1%; adjust the crop instead of stretching artwork.
  - `frame`: pre-rotation destination box inside the canvas.
  - `corner_radius`: optional; defaults to `0`.
  - `border`: optional `width` and opaque `color`.
  - `protected_action_regions`: zero or more named final-page-coordinate boxes containing faces, hands, contact points, directional surfaces, or other evidence that no panel or lettering overlay may obscure.
- `bubbles`: optional deterministic overlays.
  - `panel`: target panel id. The shape, tail, text box, and approved safe region must remain inside that panel's final visible footprint.
  - `reading_order`: unique, consecutive page-wide order. Rendering follows this field, not JSON array order.
  - `speaker`: stable character id or `narrator`.
  - `speaker_anchor`: approved final-page-coordinate ownership anchor inside the target panel. It is recorded for QA; geometry alone cannot prove semantic ownership.
  - `shape`: `ellipse` or `rounded_rect`.
  - `bbox`: exact final-page bubble bounds.
  - `safe_region`: approved final-page placement region. The bubble and tail, including a conservative stroke and resampling margin, must remain inside it.
  - `tail`: either empty, exactly three legacy points, or in schema v2 a
    `{style: soft-rounded, points: [...], tip_trim: N}` object. A non-empty
    tail must overlap the body durably, extend outside it, retain a connected
    white interior, and form one hole-free silhouette. New work should use the
    tagged soft-rounded form.
  - `allow_overlap_with`: schema-v2-only array of other bubble ids. A visual-bounds overlap requires mutual declaration. This can authorize a restrained shape/tail intersection, but can never authorize either bubble to cover the other's locked text box.
  - `text`: optional locked Simplified Chinese lettering.
    - `language` must be `zh-Hans`.
    - `exact` is the locked string. It may contain normal spaces, but no embedded control, tab, carriage-return, newline, line-separator, or paragraph-separator character.
    - `lines` are manually approved visual lines and must reconstruct `exact` byte-for-character. Use separate array items, never embedded line breaks.
    - `bbox`, `font_size`, `line_gap`, and `align` determine layout. Ink exceeding the text box is a hard error; the script does not silently shrink or rewrite text.
- `lettering`: ordered local font candidates, collection face index, and opaque text color. Candidates that cannot load or render the locked glyphs are skipped; a tofu box is not accepted as a Chinese glyph. The selected font file is read once during validation, and rendering plus ledger hashing use that frozen byte snapshot even if the source path is later replaced or removed.
- `output.stage`: `lettered-final` when any bubble is rendered, otherwise `unlettered-page`.
- `output.unlettered_image`: required for a `lettered-final` run. It retains the deterministic `unlettered-page` before any bubble is drawn.
- `output.image`, `output.ledger`: fixed output paths, resolved relative to the manifest. Their parent directories must already exist. Outputs may not alias the manifest or any panel, including case-folded and Unicode-normalized aliases.

All boxes use right/bottom-exclusive bounds. Polygon points are page coordinates before panel rotation and may sit on a frame edge.

For `page-native-unlettered`, the manifest must contain exactly one source whose
decoded size, crop, and frame equal the canvas; it must be reading order, row,
and column 1 with no border, clip, rotation, z offset, or overlap permission.
This preserves the complete generated page as one art object. The script emits
an unlettered snapshot and the lettered final; verify that the unlettered output
is pixel-identical to the accepted source.

All schema-bearing objects fail closed on unknown keys: the top-level manifest, `artifact_stages`, `canvas`, `canvas.paper_matte`, every panel, panel border, protected region, bubble, bubble text block, `lettering`, and `output`. A typo such as `rotation_degree`, `clip_polgyon`, `speaker_achor`, or `font_sze` is a hard error with the exact object path; it is never ignored as inert metadata. Keep run notes and application-specific metadata in a separate run record instead of adding undeclared manifest fields.

## Schema version 1

Version 1 remains accepted without migration. It preserves the original rules and rendering path:

- panels are axis-aligned rectangles;
- frames may differ in size and radius but may not overlap;
- later rows may not start above a preceding row's bottom edge;
- panels render in `reading_order`.

Do not place a v2-only field in a version 1 manifest; upgrade the explicit `schema_version` instead. Correctly spelled v2 geometry fields are rejected in a v1 manifest, and misspelled fields are rejected by the shared unknown-key gate.

## Schema version 2

Version 2 adds irregular page geometry while retaining the same frozen-input and lettering contracts.

### Paper matte

`canvas.paper_matte` is optional:

```json
{
  "enabled": true,
  "seed": 20260810,
  "grain_strength": 4,
  "tile_size": 192
}
```

- `seed`: integer `0..4294967295`.
- `grain_strength`: integer `1..24`; use a restrained value such as `3..6` so the matte does not compete with pencil texture.
- `tile_size`: integer `32..512`.

The matte is a deterministic monochrome luminance tile generated by the compositor's recorded `tiled-lcg-luminance-v1` algorithm. It does not read an external texture or weaken source hashing. Set `enabled` to `false` or omit the object for a flat canvas.

### Polygon, rotation, and z-order

Each panel may add:

```json
{
  "clip_polygon": [[48, 500], [488, 486], [476, 986], [60, 974]],
  "rotation_degrees": 8,
  "z_index": 10,
  "allow_overlap_with": ["p3"]
}
```

- `clip_polygon`: optional simple, non-self-intersecting polygon with `3..24` unique points. Every point must remain inside the pre-rotation `frame`. Concave polygons are allowed. When present, `corner_radius` must be omitted or `0`.
- `rotation_degrees`: optional finite number from `-15` through `15`, default `0`. Positive values rotate clockwise around the frame center. The rotated full frame, including a conservative filter halo, must remain inside the canvas.
- `z_index`: optional integer from `-10000` through `10000`, default `0`. Rendering is stable by `(z_index, reading_order)`; higher values paint later.
- `allow_overlap_with`: optional unique panel-id array. Two final visible footprints may overlap only when both panels name each other and their `z_index` values differ. An allow-list entry is permission for that pair, not permission for any other collision.

`row` and `column` still define semantic reading order. Version 2 allows offset rows and explicitly controlled intrusions, but the `reading_order` values and row/column sequence must remain unambiguous.

`protected_action_regions`, bubbles, safe regions, tails, and speaker anchors use final page coordinates after the declared panel rotation. They are not automatically rotated from the pre-rotation frame. Inspect and record them on the actual composed placement.

For every allowed overlap, the higher-z footprint is rejected if it intersects any protected action region of the lower-z panel, including a two-pixel filter halo. A higher-z panel also may not cover a lower panel's bubble safe region or speaker anchor. These checks prevent a decorative inset from hiding the evidence or ownership that made a panel acceptable.

Bubble overlap is controlled separately from panel overlap. The compositor compares each bubble shape and tail using their conservatively expanded visual bounding boxes. Any intersection requires both bubbles to list each other in `allow_overlap_with`; even then, intersection with either locked `text.bbox` remains a hard error. Prefer non-overlapping bubbles unless a small intentional shape/tail join materially improves reading.

## Geometric and artifact safety

The bubble shape and the conservatively expanded bounding box of its tail are rejected when they intersect any protected action region. In schema version 2 this check is page-wide, not limited to the bubble's target panel. The expansion includes half the declared stroke plus two pixels for the 4×→1× LANCZOS filter halo. A diagonal tail can therefore be rejected even when its visible triangle would narrowly miss the box; move it or narrow the safe region instead of weakening the protected evidence. This is geometric validation, not pixel-level saliency detection.

Panel crops are resized from the same frozen byte snapshots that were hashed, using Pillow LANCZOS. Advanced panels are clipped before a deterministic Pillow BICUBIC rotation. Bubble and text overlays render at fixed 4× supersampling and downsample once. Source and font paths are not read again after validation, so replacing or removing either file cannot change the already-validated in-memory render.

PNG compression settings, traversal order, and ledger ordering are fixed. Byte-identical repeatability is claimed only inside the same OS and runtime build with the same Python, Pillow, underlying raster/codec libraries, font bytes, manifest bytes, and input bytes. It is not promised across different FreeType, libjpeg, platform, or Pillow builds even when the high-level inputs look equivalent.

The ledger records the manifest schema and compositor version, Python implementation/version, platform string, Pillow version, raster-library versions Pillow can report (`freetype2`, `libjpeg_turbo`/`jpg`, and `zlib`), paper-matte algorithm and parameters, semantic and render order, z-index, allow-list, source hash, crop, frame, clip polygon, final transformed polygon, rotation, protected regions, locked strings/codepoints, and frozen font snapshot metadata. It also records both `unlettered-page` and `lettered-final` artifact paths and hashes. These fields document the observed environment; they do not prove two independently built environments are raster-equivalent.

Treat a production ledger as private build evidence unless it has been reviewed and sanitized for publication. It may contain local source, font, and output paths even when the generated page itself is safe to share; never publish a ledger merely because its artifact passed visual QA.

Each PNG hash is calculated from the completed temporary file before its atomic commit, rather than by rereading a replaceable destination path. The ledger is written last and acts as the evidence-set commit marker. Multiple filesystem files cannot be committed as one transaction; after any interrupted or failed run, treat a set without its final ledger as incomplete. After an interrupted or failed `--force` run, verify every recorded hash before using any prior output at those paths.

The compositor provides deterministic assembly within the recorded environment, not cross-environment byte identity or semantic correctness. Continue to inspect the composed page at original resolution against the story, continuity, and editorial-layout contracts.
