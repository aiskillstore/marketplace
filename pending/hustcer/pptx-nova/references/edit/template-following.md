# Template Following

Read this file when the user provides an existing PPTX and asks to strictly
follow it as a template: "套这个模板", "按这份 PPT 改", "保留原模板版式",
"use this deck as the template", or similar. This is not the same as
Reference Create. The goal is to preserve the source deck's structure and edit
inherited objects, not rebuild a similar-looking deck from blank slides.

## Contract

- Source PPTX is read-only unless the user explicitly asks for in-place output.
- Inspect the full source deck before planning. Do not sample only the first or
  most attractive slides.
- Every output slide must map to a source slide, an existing template
  placeholder slide, or an explicit allowed insertion.
- Prefer `duplicate-slide`, `slide-copy`, `template-fill`, or edits to copied source
  objects. Do not rebuild mapped slides with fresh coordinates just because the
  visual style looks easy.
- Preserve source typography, spacing, alignment, crop, brand chrome, footers,
  page markers, section rails, images, chart/table frames, and layout furniture
  unless the user explicitly asks to restyle.
- If new copy does not fit, shorten the copy, choose a better source slide, or
  split the content. Do not silently shrink text below readability floors or
  cover old content with overlay shapes.

## Run Artifacts

Place these in the run directory:

- `template-inspect.json`: full `xdoc pptx inspect` output for the source deck.
- `template-audit.json`: reusable slide patterns, placeholders, brand chrome,
  asset provenance, unsupported objects, and preserve rules.
- `template-affordances.json`: source slide layout affordances inferred from
  inspect geometry, text density, placeholders, chart/table frames, and visual
  chrome.
- `template-frame-map.json`: one mapping entry per output slide.
- `template-edit-plan.json`: object-level edits, deletes, replacements, and
  intentional insertions.
- `pptx-diff.json`: optional final `xdoc pptx diff` report when source/candidate
  semantic changes need audit evidence.
- `deviation-log.json`: only when a mapped slide intentionally departs from the
  source pattern.
- `assets_manifest.json`: only when allowed external/reused/generated assets
  are used.

Minimum `template-frame-map.json`:

```json
{
  "source": "/abs/path/source-template.pptx",
  "outputSlides": [
    {
      "outputSlide": 0,
      "sourceSlide": 3,
      "reuseMode": "duplicate-slide",
      "narrativeRole": "opening thesis",
      "layoutAffordance": "hero statement with subtitle",
      "fitReason": "large title slot and protected brand chrome match the opening claim",
      "editTargets": [{ "shape": { "placeholder": "title" }, "action": "rewrite" }]
    }
  ],
  "omittedSourceSlides": [{ "sourceSlide": 4, "reason": "appendix pattern not needed" }]
}
```

## Workflow

1. Inspect the source deck:

```bash
xdoc pptx inspect source.pptx --daemon --json > template-inspect.json
```

2. Review source slide images if available, or render a source contact sheet with
   `xdoc convert`. Identify slide roles, recurring chrome, typography, object
   frames, media crops, placeholder-like text, and unsupported objects.
3. Write `template-audit.json` and `template-affordances.json`, then use those
   affordances to write `template-frame-map.json`.
4. Build the starter deck by duplicating or copying mapped source slides into a
   run-dir PPTX. Do not create blank mapped slides. When several source slides
   are needed, copy them in one transaction:

   ```bash
   xdoc pptx slide-copy -i <run-dir>/starter.pptx --source source.pptx \
     --slides 1,3,5-8 \
     --template-strategy register-source --size-strategy require-match \
     --output <run-dir>/mapped.pptx \
     --dry-run --json > <run-dir>/dry-run.json
   ```

   `--slides` is 1-based and `--all` copies the complete source. These two
   selectors are mutually exclusive; there is no `--slide` single-slide option
   (the parser rejects it). Reuse the native `pptx-slide-copy/v1` report as the
   structural Edit Contract evidence, including its read-only `ready` preflight,
   current target/donor whole-file SHA-256 values, normalized OPC package
   fingerprints, per-slide/dependency mappings, and `templates[]` closure
   outcomes. Strict template following accepts `registered-source` or
   `reused-source`; a `rebound-target` outcome means the requested faithful
   template route was not preserved and must stop;
   do not loop through one slide at a time or synthesize patch `opResults`.

   Cross-deck copy also carries source presentation-level paragraph/run defaults
   below local/list/template overrides, retaining theme font references and
   effective primary/alternate languages (`lang` / `altLang`). This may materialize
   defaults locally; byte-identical slide XML is not the preservation criterion.
   Check text, empty paragraphs, fields, breaks and used list levels as well as
   fonts and final rendering. If preflight reports `unsupported-text-defaults`
   (including presentation-owned relationships or an unset source language that
   would inherit the destination language), stop and retain the report. Do not
   guess an application locale, strip defaults or raw-copy XML to bypass it.
   Resolve source language/defaults only with grounded task intent and re-preflight.
   `rebind-target` intentionally adopts target inheritance; its exemption is not
   a faithful-copy workaround.

   For SmartArt, diagramData belongs to each destination slide occurrence.
   Different slides must not share it merely because its bytes match; importing
   the same donor again must still give the new occurrence independent data.
   Cache/layout/style/color resources may legitimately be reused. Let native
   `slide-copy` / `duplicate-slide` manage these identities and sidecars; do not
   deduplicate or rename parts manually, including extensionless/custom paths
   and Strict relationship spellings. Inspect each copied occurrence and retain
   full-package compatibility plus semantic evidence; equal previews do not
   prove independent ownership. SmartArt copying does not enable content editing.

   Notes parts and their relationship sidecars belong to each copied slide;
   shared notes masters/resources may remain shared. Classic/ChartEx chart parts
   and embedded workbooks must be independent per destination occurrence.
   Classic chart color-style palettes follow the chart owner; do not deduplicate
   them across charts. Valid ChartEx style/color sharing has a different contract.
   For `duplicate-slide` and repeated donor selections, edit one disposable copy's
   notes/data and verify the source and other copies remain unchanged, using actual
   part/relationship readback as well as inspect. Do not demand that every resource
   be cloned, or treat matching pixels as proof of independent editing.

   Native copy reserves the selected destinations together so forward/cyclic
   navigation can resolve among selected slides. Repeated selections retain
   per-copy self links; incoming links resolve to the first copied occurrence.
   Check the requested selection order and actual jump/return actions separately
   from static previews. Do not promise remapping of unselected destinations or
   split the transaction into separate per-slide imports.

   A `ready` preflight is not sufficient when the decks use different slide
   dimensions. Before apply, run:

   ```bash
   node <skill-root>/scripts/cli/edit/copy-size-gate.mjs \
     --target <run-dir>/starter.pptx \
     --donor source.pptx \
     --copy-report <run-dir>/dry-run.json \
     --output <run-dir>/copy-size-gate.json \
     --json
   ```

   Require `agentGate.passed=true` in addition to native
   `preflight.strategy.slideSize: "require-match"` and no size blocker. A
   mismatch remains a stop condition; do not silently scale the donor slide or
   compensate in Viewer/PDF rendering.

5. Write `template-edit-plan.json` from inspect IDs, names, placeholders, and
   bbox evidence. Default every inherited object to `keep`.
6. Apply edits to the copied objects. Use new objects only for explicit allowed
   insertions with bounded zones and reasons.
7. Run dry-run, apply, template gate, `vision-check`, PNG/contact-sheet review,
   and the placeholder/chrome QA below.

```bash
node <skill-root>/scripts/cli/edit/template-gate.mjs \
  --frame-map template-frame-map.json \
  --source-inspect template-inspect.json \
  --edit-plan template-edit-plan.json \
  --template-audit template-audit.json \
  --assets assets_manifest.json \
  --patch patch.json \
  --dry-run dry-run.json \
  --final-pptx out.pptx \
  --json > template-gate.json

node <skill-root>/scripts/cli/review/fidelity-gate.mjs \
  --mode template-following \
  --source-inspect template-inspect.json \
  --final-inspect final-inspect.json \
  --frame-map template-frame-map.json \
  --template-gate template-gate.json \
  --json > fidelity-gate.json

node <skill-root>/scripts/cli/review/finalize-evidence.mjs \
  --mode template-following \
  --run-dir <run-dir> \
  --candidate out.pptx \
  --final-inspect final-inspect.json \
  --vision vision.json \
  --fidelity-gate fidelity-gate.json \
  --json
```

Omit optional inputs only when they truly do not exist. For example, pure text
template filling may have no `assets_manifest.json`, but a deck that replaces or
keeps logos, screenshots, customer marks, product UI, or photos should include
one.

When the final mapped candidate is stable, run `xdoc pptx diff` once if the
template contract needs auditable before/after evidence:

```bash
xdoc pptx diff --source source.pptx --candidate out.pptx \
  --detail summary --json > pptx-diff.json
```

Use reliable entries to confirm that changes match `template-edit-plan.json` and
`deviation-log.json`. Reliable deletions or style/geometry changes to protected
template chrome are blockers unless explicitly approved. Treat
`uncertain`/`unsupported` as review signals and use PNG/contact-sheet or
template gate evidence to cover them.

## Layout Affordance Pass

Treat the source deck as a slide library, not an ordered outline. Before mapping
new content, infer what each reusable source slide is good at expressing:

| Inspect / preview signal                  | Affordance to record                                |
| ----------------------------------------- | --------------------------------------------------- |
| One large title slot, little body text    | hero claim, section divider, closing statement      |
| Two balanced content zones                | comparison, before/after, problem/solution          |
| Three to five equal modules               | capability list, pillar model, workflow stages      |
| Numeric cards or KPI-sized text boxes     | metric row, scorecard, executive summary            |
| Wide chart/table frame                    | data proof, trend, ranking, operating review        |
| Timeline-like geometry or repeated arrows | roadmap, process, phased plan                       |
| Image-dominant frame                      | product screenshot, customer proof, visual evidence |

Each `template-affordances.json` entry should record the source slide index,
`affordance`, likely capacity, reusable objects to preserve, and risks such as
small label slots or hard-coded old page markers. Then each `template-frame-map`
entry must cite the chosen affordance and a short `fitReason`.

Do not preserve source order by default. The target story controls output order;
a good source slide may be reused for several output slides, and weak source
slides may be omitted. If no source slide's affordance fits a target message,
shorten/split the content or ask for an allowed insertion instead of pouring a
dense argument into a label-sized placeholder.

## Edit Rules

- Use the most stable selector available: inspect id, source object name,
  placeholder selector, then query. Verify `resolvedSelectors[]` in dry-run.
- `editTargets: []` means preserve-only. Do not add narrative content to that
  mapped slide unless the frame map is updated first.
- Do not blanket-clear text. Never run logic equivalent to "clear every text
  shape, then add new boxes".
- Do not use opaque or semi-opaque overlays to hide old template text, footer,
  page number, logo, or image. Remove or rewrite the inherited object itself.
- Empty structural placeholders count as objects. Fill or delete title/body/
  date/footer/slide-number placeholders explicitly.
- Source assets are not automatically licensed for reuse. If a logo, customer
  mark, screenshot, photo, or icon is copied from the template, register it in
  `assets_manifest.json` with source and permission status.

## Asset Provenance

For template following, identity assets have stricter rules than decorative
layout:

- Allowed: user-provided assets, source-deck assets the user explicitly allows
  reusing, official/verified public assets with recorded source, built-in icon
  packs with license metadata.
- Not allowed: generated lookalike logos, fake screenshots, fake product UI,
  invented customer marks, unofficial app icons, or copied third-party marks
  without permission.
- If provenance is missing, keep the template frame but replace the asset with
  a text label, neutral native shape, or `needs-user` placeholder. Formal
  delivery cannot keep `needs-user`, `missing`, or unconfirmed placeholders.

## Placeholder And Chrome QA

Before delivery, inspect or otherwise verify:

- No visible sample text remains, such as `Title goes here`, `Name goes here`,
  `Slide Number`, `Date`, `Footer`, or template authoring notes.
- No structural placeholder is empty unless it is intentionally deleted in
  `template-edit-plan.json`.
- Required inherited brand chrome, footers, page markers, section rails, and
  reusable frames remain visible unless intentionally removed.
- Added objects do not cover inherited objects except for an explicitly logged
  replacement inside the same bbox.
- Before/after slide images for changed slides preserve the source template's rhythm,
  alignment, crop treatment, and typography.

If these checks fail, fix the inherited object mapping or choose another source
slide. Do not switch to a parallel rebuild that only resembles the template.

`cli/edit/template-gate.mjs` machine-checks the highest-risk subset:

- every mapped output slide has a valid source slide unless it is an explicit
  allowed insertion;
- unplanned `add-*` patch ops are blocked because they often indicate a
  parallel rebuild or overlay cover-up;
- added objects with coordinates are compared against source slide bboxes and
  flagged when they cover inherited objects;
- final PPTX slide XML is scanned for empty structural placeholders and common
  default prompt text;
- identity assets in `assets_manifest.json` / `template-audit.json` must have
  approved provenance and cannot be generated lookalikes.

`<skill-root>/scripts/cli/review/fidelity-gate.mjs --mode template-following` is the delivery summary
gate. It does not replace `template-gate`; it verifies the final inspect,
template frame-map coverage, and `template-gate.json` result into one
`fidelity-gate.json` artifact. A failed `template-gate` remains a failed
fidelity gate.

`cli/review/finalize-evidence.mjs` runs the layout snapshot and records final
object bbox, text, font, color, placeholder, frame, and z-order evidence into
`layout-final.json`, then summarizes the existing vision/fidelity reports in
`evidence-summary.json`. Treat layout risks as QA warnings, not as a replacement
for the template gate or PNG/contact-sheet review.
