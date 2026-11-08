# Cartesian 2.0

Cartesian is a quiet museum-catalog language: warm stone, regular serif headlines,
clean sans supporting text, hairline rules and compass rings. Preserve hierarchy
through type and space. Cards are tracing-paper rectangles; lists/timelines are
ruled registers, not decorated flowcharts. No saturated accent, shadow, gradient,
rounded cards or italic display. Numeric/geometry facts live in design.json.

Use the standard discovery → content → validate → build → create workflow. All ten
existing slide type names remain. Each page resolves a registered composition;
`layoutId: "auto"` is deterministic and chooses among fitting frames. Explicit
layout IDs still undergo capacity checks. No fit means reorganize or split;
content is never truncated or shrunk to an unreadable size. Short extracts can
set `meta.designScope: "excerpt"`; complete decks open with cover and end with closing.

Cover hero/wide, agenda split/stacked, statement centered/reading, columns rail/wide,
image-left/image-right, cards row/register, line wide/rail and timeline horizontal/vertical
change actual geometry. Team/closing have one count-driven or centered composition.
Generic slot budgets describe default maximum-count geometry; actual resolver checks
combined strings, every repeated item and the selected layout. PNG/PDF review remains necessary.

## Content migration

The two chart types now require explicit `data.unit` and `data.source`. Use authoritative
metadata; do not infer currency, percentage or a real source from the template.
`chart.categories` and both `series[].name/values` remain unchanged. Values must be
finite and match category counts. An authored valueAxis may not clip source data.
The old implicit 0–60 maximum and smooth line interpolation are removed. Data stays
in native editable chart series; tiny observations on a common linear scale may
not have individually visible pixels. Display formatting does not alter raw values.

All other visible field names remain. Optional agenda `textLayout: "paragraphs"`
retains native `S{index}_AgendaParagraphs` and per-item `level` for choreography;
levels in independent-row mode fail rather than being silently ignored. Numbering
and neutral Roman markers can be generated; every business label/value comes from content.

`image.editorial` remains a caller-provided assets-manifest slot. With no image,
the editable crossed frame is intentional. contain/cover/crop-safe/no-crop use
normal asset resolution; no source photo or full-page screenshot is bundled.
Stats are display strings; no numeric graphic is derived from those strings.

## Design adaptations and limits

Small source labels are darkened and enlarged for readability; paragraphs and KPI
rules reserve actual clearance. Circle markers/initials own their text and use
horizontal/vertical centering. Browser navigation, hover and transitions are omitted.
The skin carries no business policy. Bundled numbers/claims are explicitly synthetic.

Latin uses Playfair Display and Inter; Chinese display uses Songti SC and supporting
text uses Arial Unicode MS. Fonts are not bundled. Recheck actual regular/bold glyphs,
font availability and final canonical PNGs on another machine; Fontconfig alone does
not describe the xdoc/Office font resolver. Readback proves supported object/text/geometry
and chart categories/names/values, not full OOXML/workbook equivalence or host parity.

Creation readiness and existing theme/style native refurbishment are separate
capabilities; this migration does not prove arbitrary source-deck preservation.

## Native specimen exhibits

Five opt-in page types extend the editorial frame: `cartesianExhibitSlide` for bounded native geometry, `cartesianAnalyticalSlide` for a single data view, `cartesianComparisonSlide` for paired views, `cartesianSceneSlide` for projected chart scenes, and `cartesianFormulaSlide` for math exhibits. All share registered `wide` and `rail` layouts; the actual chart count changes the stage geometry. `label`, `title`, `body`, `source`, and a structured `specimen` are required. The specimen accepts `nodes`, `charts`, or `equations`, never executable operations. Geometry is normalized to the stage and cannot leave it. Node text is fit-checked rather than shrunk.

Preflight requires the selected branch's payload and rejects fields from inactive branches. All specimen text, including chart/equation captions, paragraphs and display words, is checked against the actual frame before rendering; CJK wrapping is retained in the rendered text. Rotated nodes must fit with their rotated bounds. Empty `nodes: []` remains an explicit declaration placeholder; equations and charts cannot be empty. Ordinary editorial layouts are unchanged.

Exhibit decks opt into six muted scientific theme accents; background, type, rules and ordinary components retain the Cartesian language. These colors also prevent nearly black surface-chart value bands. Native chart kind, data shape, styles and camera parameters still require the current xdoc contract and dry-run; the content schema is a bounded preparation aid, not a replacement for native validation. Complex data, text and scene fidelity require canonical PNG and applicable host review.

The standard creation readback supplements the xdoc JSON projection with native chart caches, bound by registered slide and shape name. It checks all combo series and their axis assignment, exact 3D families, XY coordinates, bubble sizes and ChartEx source dimensions. Hierarchy checks cover displayed leaf values and label paths, not internal node ids or unused parent aggregate values. This is not complete chart XML/workbook equivalence or a proof of camera/style fidelity. Maintainers edit `cartesianExhibitSlide.schema.json` and the Exhibit layouts, then run `node tools/update-pptx-nova-cartesian-exhibits.mjs --write` from the repository root to synchronize self-contained published copies; omit `--write` to check for drift. This maintenance command is not a user runtime dependency.

`equations` uses only the disclosed `native-omml` creation subset. It does not add matrix, cases or arbitrary OMML authoring. A user-authorized complex-math declaration remains a separate high-risk workflow with its own source binding, structure, Office and Web evidence. Empty node stages may serve that explicitly documented declaration workflow; they are not proof of a completed math page. See `cartesian/examples/native-exhibits-content.json` and the `cartesian.native-exhibits` benchmark. No generic raw XML hook or custom operation slot is enabled.
