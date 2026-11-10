# Sky Compass golden review

## Current review — 0.2.0, 2026-10-25

The 12-slide showcase has been refined after independent visual critique and native-object inspection.
The solid gray cover sector is replaced by four editable, unfilled blue compass arcs above the
uninterrupted navy scope strip. The title and KPI hierarchy is stronger. Explanation surfaces are
quiet ice blue with navy headings. Native table evidence is 11.5pt; headers, owner/date and supporting
labels retain the 10.5pt floor. Wide and rail performance tables have distinct column allocations,
and numeric value/unit cells fail before generation if they cannot fit on one line.

The process target bracket now spans the whole process. Bridge endpoint levels use `%` while
driver increments use `pp`; direct labels remain legible without exaggerating true-scale bars.
Page-specific conclusions replace the repeated sample footer, and action dependencies name the
existing approval requests. All numeric facts remain unchanged.

The current standard Create golden candidate SHA-256 is
`6a752a317e631b390bc770353a86f04e22dbd543be438cf4481267197ac95575`.
All 36 canonical PNGs across golden, alternate and Chinese/mixed-language stress content were
reviewed individually. Subsequent changes affected only performance slide 2; each changed PNG
was reviewed again, with hashes proving the remaining pages unchanged. No blocking visual defect
was observed. Two non-blocking alternate-layout details remain: a short trailing English `plan`
line in a metric cell and tight spacing around the Chinese September tick.

The golden benchmark passes with zero fit errors, zero dry-run/apply semantic issues, zero XML
warnings, and vision high/medium/low=0. Canonical PDF/PNG, content/slot checks, structure checks,
ZIP integrity and all 39 XML/relationship parts pass. Current source reproduces all three reviewed
patches. Readiness remains candidate for explicit selection; this revision does not claim automatic
production selection or arbitrary imported-deck refurbishment.

PowerPoint exported all twelve current golden pages to PDF; cover and performance pages were
visually spot-checked. This is native render evidence, not pixel parity or an edit/save/reopen test.
The Repair-dialog clean-open gate is unverified because UI scripting timed out; structural and
canonical gates do not replace that evidence. Fonts remain unembedded, and independent labels and
data-derived shapes still require regeneration after manual edits.

Current retained evidence: `.tmp/deckkit-sky-compass-20261025-design/`, with final candidates and
canonical review bindings in `iterations/09`, benchmark/readiness under `benchmark/accepted-09`,
the source numeric/pixel binding in `final-source-binding.json`, and current native export in
`powerpoint-accepted-render.json`. core-primitives is unchanged.

## Historical review — 0.1.0

2026-10-25: candidate accepted for explicit selection; all data are synthetic.

All eight source panels were analyzed; source roles map to final golden slides 1–7 and 12.
Twelve roles have 24 registered layouts. Final standard Create candidate SHA-256:
`b0747c8a729cdb98d16e19396ef3a4147fde50f72e50634592f8c2897851113d`.

Benchmark13 repeat 3 passes content/fit, dry-run/apply, zero XML warnings, vision H/M/L=0,
twelve previews and contact sheet. Canonical final-layout gates pass with zero findings.
All 36 final golden/alternate/Chinese manufacturing PNGs were reviewed individually; local
crops verify number centering, section tags, chart values, dense-table footer, Chinese dates
and the bottom-flush gray/navy cover junction. No low-issue waiver or gate relaxation.

PowerPoint 16.114.1 exported and opened both complete English and Chinese samples.
Native text/table/chart data/freeform edits save and reopen without Repair or slide loss.
All 300 golden objects, 2 charts, 4 tables pass readback with the named edits; changed workbook
cells and chart cache both equal 55/29/16. Chinese owned-label editing confirms Noto Sans SC
10.5pt; all 310 objects survive save/reopen. Independent ring labels remain authored text.

Fonts are not embedded. Independent labels and data-derived shapes require content
regeneration for synchronization. Other hosts, full workbook equality and pixel parity
remain unverified. Evidence is retained under the isolated repository-root run
`.tmp/deckkit-sky-compass-20261025/`: final examples in `verification/13/*/reviewed.pptx`,
per-page/crop records in the sibling `run` directories and `review-crops/13`, host records in
`native/13-host-review.json` and `native/13-chinese-host-review.json`, benchmark/readiness in
`benchmark/13` and `readiness-final.json`. These samples supersede earlier rounds; prior
files remain read-only. See `assets/deckkits/sky-compass/intent.md` for decisions/limits.
The maintainer migration report is local-only by user request. core-primitives unchanged.
