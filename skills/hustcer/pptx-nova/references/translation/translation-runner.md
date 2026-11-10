# Translation Finalization Runner

Use this reference when a translated candidate is already stable and must pass the final machine
gates, full-deck visual comparison, publication binding, and manual-review handoff. This runner does
not scan source text, create translations, repair target segments, or mark human review complete.

## Inputs

The finalizer requires:

- the read-only source `.pptx`;
- the stable translated candidate `.pptx`;
- the effective source `pptx-i18n-scan/v1` inventory consumed by the translation plan
  (classified when review classification was needed);
- the matching `pptx-i18n-translations/v1` data;
- a new or empty run directory and a final output path.

Pass the complete effective source inventory used by planning. Preserve the
top-level `part` on every shape `textPlan` unit; it is source identity, not
optional display metadata. If xdoc rejects incomplete identity as `invalid_data`,
regenerate the inventory from the bound source and rebuild the translation plan
before finalization. Do not fill the gap from logical slide filenames or from
the candidate, and do not reuse a stale candidate report after an input error.

Before these inputs exist, read `references/translation/translation-mode.md` for scan, classification, planning,
apply, repair, chart/table coverage, and multi-column review preparation. Do not invoke the finalizer
with an intermediate candidate.

For a new translation, prefer `cli/translation/prepare.mjs`. It creates a hash-bound,
content-deduplicated translation memory, resumes bound review classification, and sequentially applies
the planner artifacts. When supported by the current xdoc contract, preparation also consumes
high-confidence `i18n-anchor-draft` merge material and reruns `i18n-plan`; it never treats the draft
as apply authorization. This finalizer begins only after that preparation result is `prepared`.
Preparation keeps review partitions count-only by default; use
`--expand-review <languageUncertain|shared|embeddedWorkbook|other>` to persist
one bound partition when its individual units are actually needed.
Retain the planner's disclosed `textLayout: "preserve-geometry"`; see `translation-mode.md` for pending reflow, fitting and older runtimes. Keep all gates; avoid a default geometry-restoration pass.
Use `artifacts.units`: the inventory and SHA-256 recorded in `summary.units` and used by planning,
including when `--apply` reuses approved classification. With older preparation scripts, use
`artifacts.classifiedScan` when non-null, otherwise `artifacts.scan` after checking the translation
memory's bound units path/hash. No classification work means no `i18n-scan-classified.json`; do not
invent that file or reclassify to satisfy a filename. Use the same effective inventory as the
successful plan, plus `artifacts.candidate` and `artifacts.translations`.

## Standard command

```bash
node <skill-root>/scripts/cli/translation/run.mjs \
  --source source.pptx \
  --candidate <run-dir>/candidate-final.pptx \
  --units-file <effective-units-file> \
  --translations <run-dir>/translations.json \
  --output translated.pptx \
  --run-dir <run-dir>/finalize \
  --json
```

Add `--allow-text-attrs tooltip,descr,title` only for explicitly translated typed text attributes.
Add `--multi-column-review-gate <path>` only when the final `vision-diff` contains exclusively bound
`review-only` multi-column findings and the gate belongs to the same candidate bytes. Add
`--contact-diff` when compatibility aliases are needed; aliases are copied from the final compare and
must not trigger another full-deck render.

Before creating the run directory or starting xdoc, the finalizer reads the
bound units and translations and derives the exact changed
`visibleTextAttr` attribute names. If the explicit `--allow-text-attrs` list
does not cover them, it fails with the changed attribute names, unit counts,
and a copyable retry flag. It never grants the authorization automatically;
this avoids a full finalizer rerun caused by a late style-gate failure.

Compare parts render concurrently (`--compare-concurrency`, default 3). `--prompt-text`/`--prompt-file`
archive the original user request to `<run-dir>/prompt.txt` for the feedback gate. The full progress
event stream is archived to `<run-dir>/progress.jsonl` by default (`--progress-file none` disables);
while active, stderr carries only single-line phase-boundary summaries.

The finalizer re-runs the bundled multi-column gate before accepting it. Candidate bytes, the bound
vision report, exact slide/shape finding set, reviewed PNG hashes/dimensions, and decisions must all
remain valid; a previously passing but stale gate fails closed. Current and reviewed vision reports
use a normalized evidence identity that ignores only their run-local source/candidate path strings;
all other report fields must match.

The finalizer owns this sequence:

```text
snapshot immutable inputs
-> source inspect
-> i18n style diff
-> candidate target consistency
-> vision diff and optional bound review-only exception
-> one candidate full preview/contact sheet
-> semantic diff
-> one full translation compare
-> optional contact aliases from the same evidence
-> compare publish gate and final hash binding
```

## Agent-facing output

`--json` prints a compact `pptx-nova-translation-result/v1` result with status, paths, machine-gate
summary, performance, conditional `requiredReferences[]`, and terminal error. The complete
`pptx-nova-translation-run/v1` report is persisted as
`<run-dir>/translation-run-summary.json`; read it only for diagnosis or evidence inspection. Use
`--json-full` only when complete stdout compatibility is explicitly required.

Successful machine finalization returns `status=needs-human-review`,
`machineGatesPassed=true`, and `deliveryReady=false`. The runner never records manual review as
completed.

## Visual evidence and performance

The candidate preview and translation compare serve different policies:

- preview proves every candidate slide rendered and supplies the candidate contact sheet;
- compare binds every source/candidate slide pair for final visual review;
- optional `contact-diff` files are compatibility aliases of compare evidence, not a second render.

Performance records preview invocations, compare parts, actual retry attempts, estimated pixels,
pair-cache hits, page-bitmap hits/misses/population, saved render invocations, saved alias invocations,
render share, and invocation/pixel budgets. Multipart compare must cover
every slide without overlap or gaps. A 192 DPI part may retry once at 144 DPI; every retry remains
visible in the report. Compare evidence is content-addressed by source/candidate bytes, selector, DPI,
and xdoc executable bytes. Below that pair-level cache, preview and compare share page bitmaps keyed by
PPTX SHA-256, one-based slide, DPI, and the xdoc renderer binary SHA-256. The default cache is shared
beside the run directory and survives failed finalize runs. A validated pair-cache hit is rebound to the
current artifact paths and counts as zero actual render invocations.

## Failure routing

Always follow `requiredReferences[]` first. For visual blockers without a supplied review gate, load
the named `Visual Parity Gate` section in `references/translation/translation-mode.md`. Load deeper sections only
for the detected problem:

- missing or inconsistent target text: `I18n Plan Gate` and translation repair rules;
- changed style signatures: `Style Signature Gate`;
- charts or tables: the matching translation-mode section plus `../content/charts.md` or `../content/tables.md`;
- multi-column review-only findings: `Visual Parity Gate` and the scaffold/gate workflow;
- real overflow, overlap, edge, or other high/medium regressions: repair the candidate; they cannot be
  waived by a multi-column review gate.

Never retry finalization with stale review evidence. Recreate any gate whose candidate, vision report,
page PNG, byte length, dimensions, or SHA-256 no longer matches.

## Delivery boundary

The final output is published only after the compare gate passes and binds the exact candidate bytes.
After machine success, inspect the candidate contact sheet, every compare part, and all bound
review-only full-size pages. Preserve the summary, scans, style and vision reports, semantic diff,
preview manifest, compare reports/images, compare gate, and final PPTX binding as audit evidence.
