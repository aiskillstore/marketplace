# Export And Check

Read this file when the user only wants conversion, extraction, preview, or
validation of an existing deck. Do not load create/edit mode details unless the
user also asks to change the PPTX.

Read `../common-workflow.md` before this file. Export/check tasks still write
artifacts, so use a run directory by default and follow its `--overwrite` safety
rules.

## Preview authorization constraints

Read `xdoc schema --command pptx.preview` or action help before supplying strict constraints.
Slide preview binds caller intent to `feature=convert`, `outputType=png`; layout preview binds
to `feature=modify`, `outputType=pptx` and reuses that admitted intent for PNG rendering.
When supported, pass either `--intent <file-or-inline-json>` or the required strict flags
(`--require-entitlement`, `--require-unwatermarked`, `--allow-fallback`); never combine the two
forms. Preserve the user's constraints through rendering. A preview refusal is not permission
to drop flags, change transport or silently accept watermarked fallback. Keep the actual
authorization/error report and disclose unavailable evidence. Ordinary preview needs no
additional authorization-maintenance step.

For a conversion input-limit or authorization refusal, follow
`../runtime/troubleshooting.md#conversion-input-quotas-and-authorization-failures` and retain the actual report.
The local CLI task contract owns its combined input-byte and slide limits;
Converter SDK profiles have a different slide-limit policy. Markdown/text output,
a selected slide range, or a successful read-only inspect does not prove the
conversion task is authorized. Keep caller constraints when choosing another route.

## Semantic PPTX Diff

When the user only asks to compare two decks or audit before/after changes, use
the read-only semantic diff path:

```bash
xdoc pptx diff --source before.pptx --candidate after.pptx \
  --detail summary --output <run-dir>/pptx-diff-full.json \
  --json > <run-dir>/pptx-diff.json
```

The default `summary` detail is the normal Agent path. It reports
`pptx-diff/v1`, `agentGate`, `summary` (`reliableChanges` / `uncertainChanges` /
`unsupportedRegions` and `byCategory`), `styleChangeSummary`, and per-slide
rollups; there is no `changeRollup` field.
Use `--detail full` directly when a generic Edit Contract consumes the report,
because its object locality and expected text checks require `shapeChanges[]`.
For observation-only audits, read `fullEvidence.path` when the summary identifies a suspicious
slide/object. `--output` persists the full report in the same comparison; verify its SHA-256
and both `inputBinding` hashes before consuming it. Translation and Refurbish runners perform
these checks automatically and retain both files. Without `--output`, a summary truthfully
reports `fullEvidenceAvailable=false`; it does not promise evidence that requires another run.
Existing output files and input/output aliases are rejected. Use a fresh evidence path.

Use only `reliable` entries as machine-checkable facts. Treat `uncertain` and
`unsupported` as review signals. The report's `visualEvidence` block identifies
the canonical handoff; semantic diff and PNG preview remain advisory and never
authorize delivery.

For schema validation, execute `policyRef.discoveryCommand` (`xdoc schema --report pptx-diff/v1`)
and resolve `policyRef.schemaRef` for the policy text. The report schema remains at
`commands.pptx.diffReportSchema`. `pptx-diff/v1` has distinct `detail`
branches: summary slide rollups are not full `shapeChanges[]` evidence. Do not pad omitted
fields with null, mix branch fields, or drop unknown fields to make validation pass. Fixed
objects are closed; category/style maps permit dynamic keys with typed counts. Full shape
bounds can contain signed extents from malformed source geometry: retain them as diagnostics,
not as permission to author negative sizes. Schema acceptance proves report shape only;
the existing reliability, scope and delivery gates still apply.

## Reproducible Dynamic Fields

One-shot rendering commands accept `--field-date YYYY-MM-DD`, with `XDOC_FIELD_DATE` as the
environment fallback. The flag takes precedence. Omission captures the host's local date once;
invalid dates fail before rendering. This controls displayed dynamic fields only, never
authorization or expiry clocks. Preview/contact-diff reports, conversion manifests and canonical
visual manifests disclose `renderContext` with the effective date and cache binding.

Create, Translation, Refurbish and Compare runners persist `render-context.json` in the run directory
and pass its date to child commands. Resume/finalize reuses that date; a conflicting override
requires a new run directory. For manual multi-command diagnosis, pass the same explicit date to
every render and inspect the reported context. Keep native fields editable. Bitmap caches validate
the actual PDF SHA-256; the skill's comparison cache also includes the frozen date.

## Unified Visual Evidence (Canonical Agent Gate)

`xdoc pptx visual-audit` is the only xdoc report whose `decision` is consumed
as the final Agent visual action. Run it once after the candidate is stable;
`preview`, `diff`, `vision-diff`, and `contact-diff` remain specialized
observation/review reports. The canonical transaction packages:

- final PDF text-frame fit and rendered page-bound findings;
- the actual selected-slide typeface/style resolution, attributed back to the
  PPTX objects that requested it;
- normalized same-renderer pixel changes between a reference and candidate,
  with changed regions mapped to every overlapping object candidate;
- one atomically published, hash-bound manifest with the exact PDF and PNG
  artifacts used by those checks.

Visible PDF page-bound checks exclude invisible selection/OCR text layers and clip-only glyphs;
their text bounds do not prove painted overflow. Chart labels still supply ink-region evidence
for collision checks, but renderer-created label positioning boxes are not authored text frames
and are excluded from frame-height fit auditing. Authored text frames and visible out-of-page
glyphs remain checked. These exclusions do not certify clipping paths, OCR correctness or chart
layout; do not waive actual overlap/overflow findings. Re-audit the original bytes with the current
runtime before changing a deck to compensate for an older synthetic-frame finding.

Create reuses canonical PNGs for its actual visual review; existing-deck diagnosis still
uses `vision-diff` or `contact-diff`; those reports explain the result but do
not create a second delivery verdict. `visual-audit` performs the governing
render transaction, does not create a contact sheet, and v1 implements neither
OCR overflow nor an independent PowerPoint/Office renderer.

Confirm the current runtime disclosed the command:

```bash
node <skill-root>/scripts/cli/runtime/probe.mjs \
  --require-command pptx.visual-audit --strict --json
```

For candidate-only final-render/font diagnosis:

```bash
xdoc pptx visual-audit \
  --candidate deck.pptx \
  --output-dir <run-dir>/visual-evidence \
  --json > <run-dir>/visual-audit.json
```

For a genuinely new deck, first verify that the runtime discloses
`capabilities.visualAudit.modes` containing `create`, then add `--visual-mode create`.
This explicit policy checks the complete candidate and rejects `--reference` and `--slides`.
It reports `policyId=pptx-visual-oracle-create/v1` and, when candidate checks pass,
`assurance=candidate-checks`. This is not regression equivalence, content-intent acceptance or
PowerPoint parity. Review the exact manifest PNGs and the content contract before delivery.
The standard Create runner handles preparation and finalization as described in `../create/create-runner.md`.
Create reviews also require the slide-specific design judgment from
[Design quality](../create/design-quality.md), supplied as `--design-review` to the visual-review
helper. Mechanical passes alone do not authorize a newly created deck.
Old runtimes keep the legacy candidate-only confirmation boundary; do not remove it in the consumer.

For a stable before/after same-renderer comparison, use the same 1-based scope
as the edit review:

```bash
xdoc pptx visual-audit \
  --reference before.pptx \
  --candidate after.pptx \
  --slides 2,5-7 \
  --output-dir <run-dir>/visual-evidence \
  --json > <run-dir>/visual-audit.json
```

The command atomically publishes `<run-dir>/visual-evidence/manifest.json` and
its referenced PDF/PNG files. An existing output directory requires
`--overwrite`; use it only for this current-run generated evidence directory.
The stdout JSON is the same canonical manifest and should remain outside the
output directory so shell redirection does not fail before xdoc creates it.

Interpret the result in this order:

If the command fails with `--json`, retain its stdout error report even when
no manifest directory was published. It still uses `pptx-visual-evidence/v1`,
with `status="error"` and `error.code`, `message`, `stage`, `retryable`, and
`details`. Conversion failures preserve their original classification and
resource/authorization details. Do not infer a code from the stage or retry
solely because rendering was involved; a failure report has no visual decision.
This local report's `retryable` field remains part of its own schema. Do not
replace it with a transport-specific retry directive, or treat it as permission
to replay an edit; follow the reporting command's current contract and the
publication checks in `../runtime/troubleshooting.md`.

1. A process exit code of `0` means only that the evidence transaction
   completed. First require `schemaVersion="pptx-visual-evidence/v1"` and
   `status="success"`, then read `decision.action`.
2. `stop` means a required check found a hard content problem. Inspect which
   subject owns the finding before calling it a regression: both reference and
   candidate receive static-layout, final-layout, raster, and font checks.
3. `require-human-confirmation` means review the referenced PNGs and findings;
   default regression-mode candidate-only runs reach this action even when all required candidate
   checks pass because regression equivalence is unavailable.
4. Regression `proceed / same-renderer-regression` proves unchanged normalized pixels plus passing
   required checks. Create `proceed / candidate-checks` proves only candidate machine checks;
   actual visual review and content acceptance remain required. A machine verdict does not prove PowerPoint parity or
   visual intent.

Consume the persisted manifest fail-closed:

```bash
node <skill-root>/scripts/cli/review/visual-evidence-gate.mjs \
  --manifest <run-dir>/visual-evidence/manifest.json \
  --candidate <current.pptx> \
  --output <run-dir>/visual-evidence-gate.json \
  --json
```

Only exit status `0` and `deliveryAuthorized=true` authorize an automated
delivery. Exit `4` is a content blocker. Exit `5` requires actual human
confirmation; an Agent must not reinterpret it as success. Invalid or
internally inconsistent manifests exit `3`.

Always bind the gate to the current candidate. For Create, after actually reviewing the canonical PNGs,
also pass `--review <visual_review.json> --lock <run-dir>/deck_lock.json`. Record that review with both `--candidate` and `--manifest` using
`cli/review/visual-review.mjs`. The consumer verifies candidate, PDF/PNG and manifest hashes, complete
slide coverage and all required review checks. Create authorization requires the review mode to match
the supplied lock's valid `artDirection.mode`; that locked mode controls the signature-moment requirement.
Use the standard runner for publication with its input-bound lock. Exit `6` means machine checks passed but actual
visual review is missing; it does not require another user permission question. Stale or failed
reviews do not authorize delivery. Use a fresh run after changing the candidate.

Edit, Translation and Refurbish continue to use the common consumer with the default regression
policy and their approved source/reference. Producing a new output filename does not make an edit
a Create task. Keep each workflow's semantic/style/fidelity checks; do not substitute Create mode
for explaining intended changes.

`ocr-overflow=skipped` and `independent-reference=skipped` are expected v1
limitations, not passing evidence. Keep manual PNG/contact-sheet review and
PowerPoint snapshot/clean-open evidence when those policies apply. Never replace
a specialized semantic, Edit Contract, Translation, Refurbish, or Office gate
with this manifest.

## PPTX PNG Preview

For external/PowerPoint PDF evidence, use `xdoc pdf render` (PDFium) and retain
the exact PDF and rasterizer identities when available. The bundled optional
Office snapshot helper records them while preserving logical-slide/page mapping.
If rotated text appears missing or oversized in a MuPDF capture, re-render the
same PDF with PDFium before attributing it to the deck; see
[fidelity diagnosis](fidelity-diagnosis.md).

Read `options[]` for the exact rendering action before choosing `--dpi`. The current CLI
accepts integers from 1 through 1200 for `convert`, `pdf render`, `pptx preview`,
`pptx visual-audit` and `pptx contact-diff`. Their defaults are 144 except contact-diff's 72;
skill runners may explicitly choose other values, such as 192 for comparison evidence.
Preserve those explicit workflow settings. The shared parent option is not an action's default.
A legal DPI is not a guarantee that a large deck/contact sheet fits resource limits. Use
normal workflow DPI and chunking for real decks; test extreme DPI only on tiny fixtures.

For PPTX visual review, use `xdoc pptx preview` as the default PNG/contact-sheet
path:

```bash
xdoc pptx preview deck.pptx \
  --output-dir <run-dir>/previews \
  --contact-sheet --contact-output <run-dir>/previews/contact-sheet.png \
  --overwrite --json > <run-dir>/preview.json

xdoc pptx preview deck.pptx --slides 25-38 \
  --output-dir <run-dir>/previews \
  --contact-sheet --contact-output <run-dir>/previews/contact-sheet.png \
  --overwrite --json > <run-dir>/preview.json

xdoc pptx preview deck.pptx --layout 1 \
  --output-dir <run-dir>/layout-preview \
  --overwrite --json > <run-dir>/layout-preview.json
```

`--layout N` is a 1-based registered-layout preview and is mutually exclusive
with `--slides`. xdoc builds a one-slide candidate from that layout and its
master/theme inheritance chain, persists
`layout-preview-<index>-candidate.pptx` inside the requested output directory
(`<index>` and the reported `layoutIndex` are 0-based: `--layout 1` writes
`layout-preview-0-candidate.pptx` with `layoutIndex: 0`), and
does not mutate the input deck. Require `previewTarget.kind: "layout"`, the
expected 0-based `layoutIndex`, `candidatePersisted: true`, a readable
`candidate.status: "ok"`, and `inputMutated: false` before treating the PNG as
layout-level evidence. The manifest's `visualEvidence.command` must reference
that persisted candidate, never an already-deleted temporary path.

The stdout manifest is `pptx-preview/v1`. It is observation-only and carries a
`visualEvidence` handoff to the canonical decision. Its status fields are
two-level by design, and the two levels use different enums on purpose:

- Top-level `status` is the **command result**: `success` | `error`.
- Each `pages[].file.status` and `contactSheet.status` is a **per-artifact file
  check** (PNG written and readable): `ok` | `error`.

The top-level `status` does **not** aggregate file-level failures, so
`status=="success"` alone does not prove every page rendered. A correct
readiness gate must assert both levels:

```bash
jq -e '.status=="success"
  and (.pages | length > 0)
  and all(.pages[]; .file.status == "ok")' <run-dir>/preview.json
```

Do not gate on `pages[].status`; the per-page status lives at
`pages[].file.status`. Field semantics are authoritative from the
`pptx-preview/v1` schema — inspect it with the top-level `xdoc schema` command
(`xdoc schema | jq '.commands.pptx.previewReportSchema'`; there is no
`xdoc pptx schema` action) rather than assuming a single shared enum.

After the gate passes, PNG filenames preserve original slide numbers, so
`slide-025.png` still refers to slide 25 even when the contact sheet only
contains a scoped range.

Read the contact sheet first to detect cross-slide issues such as rhythm, page
number jumps, inconsistent dark/light pages, and obvious layout problems. Then
inspect full-size PNGs for suspicious slides.

For Web clipping, missing/stale text reflections, or scale-dependent Shape 3D
offsets, follow [fidelity diagnosis](fidelity-diagnosis.md#web-clipping-reflections-and-display-scale)
before changing the deck. Verify the actual Web build after fonts/layout settle;
native PNG/PDF evidence does not exercise the Web renderer's decoration budgets
or refresh lifecycle. A missing decoration alone does not prove lost text.

Use `xdoc convert --to png` only for non-PPTX or generic conversion fallback,
or when debugging the lower-level convert pipeline.

## Conversion

Use `xdoc convert` for PDF/Markdown/JSON/text exports and non-PPTX or fallback
PNG conversion:

```bash
xdoc convert deck.pptx --to pdf -o <run-dir>/out/
xdoc convert deck.pptx --to md -o <run-dir>/out/
xdoc convert deck.pptx --to json -o <run-dir>/out/
xdoc convert deck.pptx --to text -o <run-dir>/out/
xdoc convert deck.pptx --to png -o <run-dir>/previews --overwrite --contact-sheet # fallback/debug only
```

The command shape is `xdoc convert <pptx> --to <format>`, not
`xdoc <pptx> -t png`.

Use canonical tokens: Markdown is `md`, plain text is `text`, and the
compatibility check is `compat`. Retired `markdown`, `txt`, and `compatibility`
aliases are rejected; the same rule applies inside comma-separated lists.

Without an installed License, PPTX conversion runs the Free Baseline: at most
10 slides and 5 MiB (5,242,880 bytes) of compressed PPTX input per task, and
visual outputs (PDF/PNG) carry a watermark. Inputs beyond those limits fail
with exit code `4` (`no_executable_mode`). `--allow-fallback` pre-authorizes the
Free Baseline for automation; `--require-unwatermarked` fails instead of
producing a watermarked export.

Do not add `--json` to top-level `xdoc convert` unless the current
`xdoc convert --help` explicitly discloses it. The structured JSON result for
PPTX visual review comes from `xdoc pptx preview --json`; generic convert may
write a manifest/report file depending on the selected output options, but it
is not the default Agent path for a machine-readable PNG preview manifest.

For PNG and multi-format outputs, path shape matters:

- `-o <run-dir>/previews` means `<run-dir>/previews` is the output root. It
  contains `slide-001.png`, `manifest.json`, and `contact-sheet.png`.
- `-o <run-dir>/previews/` means parent-directory mode. It creates
  `<run-dir>/previews/<deck>-img/` for PNG or `<deck>.xdoc/` for multi-format
  output.

Separate single-file conversions such as `result.md` and `result.pdf` can both
claim `result.manifest.json`. Use distinct stems (for example `result-md.md` /
`result-pdf.pdf`) or one multi-format bundle; do not add `--overwrite` merely
to silence a sidecar collision from the other conversion.

Use `--overwrite` only when replacing outputs that belong to this conversion
run, usually under `<run-dir>`. If the user explicitly requests a final export
path that already exists, ask before replacing it.

## Contact Sheet

Generate contact sheets through `xdoc pptx preview` for PPTX decks. If you need
custom columns, thumbnail size, background, or a legacy contact output path,
fall back to `xdoc convert --to png --contact-sheet` and record that fallback in
the final summary:

```bash
xdoc convert deck.pptx --to png -o <run-dir>/previews --overwrite --contact-sheet
```

Adjust fallback contact sheet options only when needed:

- `--contact-cols 3` or `4` for longer decks
- `--contact-thumb 960x540` when small text must be readable
- `--contact-background EEEEEE` to see page edges better
- `--contact-output path/to/contact-sheet.png` for a custom output path

## Preflight Checks

For fonts, links, and compatibility:

```bash
xdoc check deck.pptx \
  --checks fonts,links,compat \
  --target-office 2016 \
  -o <run-dir>/check.json \
  --pretty \
  --overwrite
```

`xdoc check` is not a visual gate. It does not replace `vision-check` or PNG
review for created/edited decks.

`--target-office` accepts `2007|2010|2013|2016|2019|2021|365` and defaults to
`365`. For Agent decisions, inspect `checks.compat.details.agentGate`, not only
the command status:

- `agentGate.passed=true` means the disclosed compatibility checks pass for
  the requested target release, including parser readability and package
  integrity when those checks are disclosed; it is not a playback certificate.
- `unprotectedIssueCount>0` means newer markup has no recognized compatibility
  protection and is a structural interoperability risk.
- `gracefulDegradationIssueCount>0` means `mc:Ignorable`, an OOXML
  `extLst/ext` extension container, or an `AlternateContent` fallback should
  let older Office open the deck, but the
  newer feature may disappear or be replaced; this still fails exact-fidelity
  delivery to that target.
- `minimumOfficeVersion` is the derived minimum release for full semantics.
  Each issue includes a stable `ruleId`, occurrence count, and sample OOXML
  parts so an Agent can produce a focused repair or policy decision.

For a single PPTX, use `-o <run-dir>/check.json` as the canonical structured
preflight artifact. Do not add `--json` unless `xdoc check --help` discloses it.
If `--report` is available, treat it as a batch summary/report sidecar; it does
not replace the per-file diagnostic JSON written by `-o`.

When `compat` discloses `checks.compat.details.packageIntegrity`, require
`scope: "full-package"`, `scanStatus: "completed"`, `passed: true`, and
`issueCount: 0` before claiming package integrity passed. This checks XML/OPC
structure, namespace bindings, relationships and owner identities independently
of the target Office version. `fullyCompatible: true` alone is insufficient;
also read `checks.compat.status`, `details.agentGate` and the actual issues.
A failed or missing scan is not a clean package. On older runtimes that omit
this field, keep the existing semantic gates and disclose this evidence as
unavailable when package integrity is required. A slide-scoped check does not
narrow this full-package scan. Keep inherited source findings separate from
new edit regressions; follow the Edit Contract rather than silently repairing
unrelated source debt. None of these checks proves Office clean-open or pixels.

The structural scan does not run element-schema, child-particle or element-reference
rules; for example, duplicate shape IDs still need the full semantic audit.
Keep dry-run/apply semantic checks and candidate `vision-check`/`vision-diff`
evidence. A full-package scan is not a complete XSD validation.

Markup-compatibility checks also cover XML-like/custom and extensionless parts;
renaming a slide/layout/master/theme away from `.xml` does not exempt its
`MustUnderstand` declarations. Resolve parts through Content Types and
relationships, retain MC diagnostics, and preserve unselected branches. Do not
repair a compatibility failure by stripping namespaces or renaming the part.

For `fonts`, `missingRiskCandidates` excludes common system fonts such as
Arial, Aptos, Calibri, Times New Roman, Courier New, Helvetica, Verdana, and
Tahoma. These may appear under `systemFontCandidates`: acceptable for many
internal decks, but still a cross-machine consistency risk for strict external
delivery. Non-system `font_not_embedded` warnings should be fixed by embedding
the font or switching to an approved system/DeckKit font.

Font preflight inventories, resolved family/style, embedded font bytes and final
glyph coverage are separate evidence. Use canonical visual-audit font findings
and actual PDF/PNG review; a system font candidate or valid font file does not
prove every codepoint rendered. Include visible bullets, chart axis/depth titles,
display-unit labels, combo groups and local SVG text when diagnosing missing
glyphs. Browser CSS fonts and browser PDF font bytes have separate lifecycles;
font discovery does not imply that remote SVG images/stylesheets were loaded.

If an existing browser export integration actually supplies a `cjkFallback`
report, retain its status, required/covered/missing/unknown codepoints and
coverage sources. `complete` concerns only that resolver's returned CJK fallback
assets; it excludes original-family/embedded/Latin/emoji fonts and does not prove
final PDF shaping or style fidelity. `partial`, `missing`, `unknown`, `not-checked`
and `not-needed` are distinct; declared CSS unicode ranges and decoded cmap
coverage are different evidence. Apply the task's export policy and review the
output. This optional SDK report is not an xdoc CLI preflight field: do not
fabricate it, add an SDK dependency to the baseline, or block native CLI export
merely because it is absent.

### Accessibility is outside the default list

`a11y` is deliberately excluded from the default check set, but `--checks all`
does include it. Name it explicitly:

```bash
xdoc check deck.pptx \
  --checks fonts,links,compat,assets,policy,a11y \
  --target-office 365 \
  -o <run-dir>/check.json \
  --pretty --overwrite
```

The outer report remains `preflight/v1`; the accessibility details identify
`pptx-a11y/v1`. A completed scan with findings still exits 0, so never gate on
the process status alone. Read `checks.a11y.status` and `summary.riskLevel`:

- `passed`: every rule ran and produced no in-scope finding;
- `warning`: at least one decided violation;
- `inconclusive`: no decided violation, but static package facts could not
  resolve at least one rule; this is not a pass and requires rendered/manual
  review;
- `failed`: the scan did not run and provides no accessibility evidence.

The current render-free rules cover structured slide titles, descriptions or
decorative metadata for visual objects, Office-version support for the
decorative extension, and statically resolvable text contrast. They do not
audit reading/tab order, table navigation, full WCAG conformance, screen-reader
behavior, or description quality. Gradients, pictures, and pattern backgrounds
may make contrast inconclusive.

Findings may include `patchSelector` and `patchTemplate`. The template contains
placeholder prose, has `autoApplicable: false`, and has no executable remediation
target; replace it with a truthful description and dry-run it, never merge
the placeholder unchanged. With `--target-office` earlier than 2019, a visual
marked only as decorative still needs a description fallback or produces
`a11y_decorative_not_supported`. Scoped `--slides` findings do not prove a
deck-wide pass; verify `details.scope.outOfScopeFindingCount` and deck coverage.

## Extract

Use extract for notes, resources, links, and fonts:

```bash
xdoc extract deck.pptx --parts notes,resources,links,fonts
```

Save extracted JSON/report files in the run directory unless the user asks for a
specific output location.

## Ingest HTML / URL / PDF (inbound)

The commands above send a PPTX outward. These two go the other way: they turn an
external HTML page, URL, or PDF into Markdown/text. Use them when the user just
wants the converted Markdown/text. If the result will become a new or edited
deck, follow `../common-workflow.md` -> Source Ingestion instead.

```bash
# HTML file / glob / directory / URL -> Markdown (omit -o for stdout)
xdoc html2md page.html -o <run-dir>/page.md
xdoc html2md "https://example.com/post" -o <run-dir>/page.md
xdoc html2md ./pages --recursive --output-dir <run-dir>/md     # batch
xdoc html2md page.html --html-base-url "https://site.com/"  # resolve relative links
xdoc html2md ./pages --recursive --report <run-dir>/html2md-report.json

# PDF -> copyable text (omit -o for stdout)
xdoc pdf extract-text input.pdf -o <run-dir>/text.txt
xdoc pdf extract-text input.pdf --pages 1,3-5 --mode layout
xdoc pdf extract-text input.pdf --engine pdfium --json --pretty  # pdf-text/v1
```

Notes:

- `xdoc html2md` and `xdoc convert <input> --from html --to md` share the same
  HTML-to-Markdown engine; a URL passed to `convert` auto-detects as `html`.
- `xdoc pdf extract-text`: `--engine auto` resolves to PDFium in native builds
  (`pdflite` is not yet available); `--pages` is 1-based; `--mode layout` keeps
  visual order, `natural` is the reading flow. With `--json --pretty` inspect
  `summary` and `warnings` for dropped/reordered characters.
- `pdf extract-text --output` writes one text or JSON file. Existing files are
  preserved with exit code 9 unless `--overwrite` is explicit; use it only for
  current-run outputs. The complete result is staged before replacement. Omit
  `--output` to keep the result on stdout; no manifest sidecar is generated.
- This is text only. Images, styles, and layout from the source are not imported.
- `html2md -o file.md` also writes a `file.manifest.json` sidecar and refuses to
  overwrite an existing output; add `--overwrite` for current-run files, or use
  `--manifest false` (or stdout without `-o`) for a single clean file.

## When Export Finds A Problem

For image-heavy decks, distinguish compressed PPTX size, expanded image/JSON size, font discovery
and actual rendering time before changing content or lowering DPI. Current consumers can share
repeated background/raster work and native font discovery can avoid reading every full font file;
these are internal optimizations, not new input formats or a universal speed guarantee. Preserve
public image payload/alpha and font choice. Do not persist internal Worker transport envelopes as
deck JSON, add private SDK/WASM dependencies to CLI runners, or bypass resource limits on a retry.

When rechecking after an xdoc upgrade, create a fresh run and render the same
source bytes with the current binary before changing the deck. Text inheritance,
kerning, autofit, CJK wrapping, mixed-size line metrics, Office math, gradients,
shadows, and partial 3D rendering can change pixels without a PPTX edit. Old
screenshots remain historical evidence. The bundled page cache binds PPTX bytes,
DPI, and renderer bytes; retain that binding and use a fresh cache when fonts or
the rendering environment change. Supported dynamic short-date fields also use the operation's
local calendar date and effective language. Record date/timezone and use fresh evidence/cache
after a date or timezone change; unchanged PPTX bytes do not prove unchanged rendered dates.

For a before/after edit comparison, render both decks with the same current
binary, fonts, scope, and DPI. Otherwise a renderer change can masquerade as an
edit regression. Review actual line breaks, baseline/bullet alignment, equation
bounds, and effect clipping before adding manual line breaks, shrinking fonts,
or moving shapes. Preserve authored spacing and editable equations unless the
current evidence calls for an authorized edit. A renderer improvement does not
prove PowerPoint parity; use `../edit/inspect-and-edit.md` for Shape 3D boundaries and
the existing native-evidence route when independent Office proof is required.

For a rendering discrepancy, follow [fidelity diagnosis](fidelity-diagnosis.md)
before compensating in the deck. It covers authored overflow, sparse chart
data, image/clip semantics and valid single-variable probes.

If conversion/check reveals a problem and the user asks you to fix it, switch to
`../edit/edit-mode.md` plus the relevant domain reference (`../content/styles-and-themes.md`,
`../content/charts.md`, `../content/tables.md`, or `../edit/patch-ops-cheatsheet.md`).

## PowerPoint clean-open gate

- For deliverable PPTX files, especially for formal/enterprise users or high-risk chart/table/OOXML changes, if the current environment is macOS and Microsoft PowerPoint for Mac is installed, run the clean-open smoke gate:
  `node <skill-root>/scripts/cli/runtime/clean-open.mjs --pptx out.pptx --output <run-dir>/clean-open.json --json`.
  The live clean-open helper supports only macOS + PowerPoint for Mac + `osascript`/System Events; Windows/Linux have no equivalent clean-open run. If macOS lacks PowerPoint, `osascript`, or UI scripting permission, the helper returns `status: "skipped"` and does not block delivery. The final summary must explicitly state that the clean-open gate did not run and list the alternate structural checks performed. The helper stages the file in the PowerPoint sandbox, opens the candidate automatically, waits through PowerPoint's delayed chart/ChartEx loading window, and uses System Events to check Repair-like modals. Checking only that the presentation object opened is insufficient: PowerPoint may open it and show a Repair dialog at the same time. An ordinary `Cancel` button is not a failure; only Repair wording, a `Repair` button, or an equivalent repair prompt blocks. `--classify-ui` is only for offline UI snapshot classification tests and may run cross-platform.
