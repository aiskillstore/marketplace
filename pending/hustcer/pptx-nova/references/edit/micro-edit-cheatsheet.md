# Micro Edit Cheatsheet

Read this file instead of the full edit stack when the user asks for a small,
localized edit to an existing `.pptx`: one or two text replacements, speaker
notes, footer/date/page-number text, document metadata, a small color/font tweak,
or a single image replacement.

The goal is speed without weakening selector or edit-contract safety.

## Scope

Use Micro Edit only when all of these are true:

- The input is an existing PPTX.
- The requested change is localized and easy to describe.
- The edit should preserve slide count, layout, theme, and visible structure.
- No new deck narrative, DeckKit selection, brand system, or design lock is
  needed.

Escalate to `edit-mode.md` when the task touches charts/tables, many slides,
layout changes, template fidelity, brand rework, complex images/crops, ambiguous
selectors, SmartArt, animations, or any user-visible redesign.

## Minimal Flow

Create a run directory and capture xdoc capability evidence as required by
`../common-workflow.md`. Then keep the loop short:

```bash
xdoc pptx inspect input.pptx --daemon --json > <run-dir>/inspect.json
xdoc pptx select input.pptx --query '{"textRegex":"old text"}' --json > <run-dir>/select.json # optional target lookup
node <skill-root>/scripts/cli/edit/contract.mjs \
  --draft <run-dir>/edit-contract-draft.json --source input.pptx \
  --output <run-dir>/edit-contract.json --json
xdoc pptx apply -p <run-dir>/patch.json -i input.pptx -o <run-dir>/candidate.pptx \
  --daemon --overwrite --dry-run --json > <run-dir>/dry-run.json
xdoc pptx apply -p <run-dir>/patch.json -i input.pptx -o <run-dir>/candidate.pptx \
  --daemon --overwrite --json > <run-dir>/apply.json
```

Before apply, verify `dry-run.json`:

- every op resolved the intended slide and object
- each selector resolved to exactly one target unless the user asked for a
  multi-object edit
- every `suggestions[]` diagnostic has been reviewed; any selected remediation has a verified target and preserved context
- any text-fit or visual-risk warning is either fixed or triggers changed-slide
  preview

Do not write back to the user-requested final path until the run-dir candidate
has passed the relevant checks.

After apply, run one final semantic diff plus the evidence declared in
`edit-contract.json`, then require `edit-contract-gate.json.agentGate.passed`.
Use `xdoc pptx diff --source input.pptx --candidate <run-dir>/candidate.pptx
--detail full --json`; the default summary cannot prove per-object locality.
For visible text replacement, preserve `target-text-style` and run style diff;
use `set-run` or another inspect-proven run/text-node edit when `set-text-frame` would
replace meaningful run formatting.

## Selector Preference

Use the most stable selector inspect exposes:

1. `id` from `<run-dir>/inspect.json`
2. shape `name`
3. placeholder selector such as `{ "placeholder": "title" }`
4. query selector only when the previous selectors are not available

If the exact target text/name is known but buried in a large deck, run
`xdoc pptx select input.pptx --query '{"textRegex":"..."}' --json` first and
copy `matches[0].patchSelector` only when `summary.matchCount == 1` and the
`text`/`bbox` confirms the target.

If the selector is ambiguous, stop the micro path and use `edit-mode.md` plus
`inspect-and-edit.md`.

## Example Matrix

Use `assets/examples/edit/micro-edit-matrix.json` as the quick fixture matrix for
the common small-edit surface:

| Case                    | Minimal success pattern                                       | Failure trigger                                                         |
| ----------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Replace text            | `set-text-frame` on one inspect-proven `shape`                | selector resolves multiple objects or run indexes are unknown           |
| Speaker notes           | `set-slide-notes` on one slide                                | rich notes structure or many-slide synchronization is required          |
| Footer/date/page number | `set-text-frame` on one footer/date/page-number placeholder   | inherited footer source or batch target set is unclear                  |
| Metadata                | `set-document-properties` only                                | visible slide text or custom package metadata also needs reconciliation |
| Replace image           | remove one inspected picture and `add-image` at the same bbox | crop, mask, aspect ratio, identity, or provenance is unclear            |
| Single-object color     | `set-shape` on one named object                               | request is theme, brand, contrast, or deck-wide style work              |
| Delete placeholder      | `remove-shape` on one empty/default placeholder               | placeholder contains user content or is layout/master-owned             |

The matrix examples are minimal patterns. Inspect and dry-run selector evidence
always outrank the sample selectors.

## One-Screen Op Recipes

### Replace text

Use `set-text-frame` for whole-shape text replacement:

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "set-text-frame",
      "slide": 2,
      "shape": { "id": 7 },
      "text": "Updated title"
    }
  ]
}
```

Use `set-paragraph`, `set-run`, or rich text ops only when whole-shape
replacement would destroy needed formatting. If run/paragraph counts are
unknown, inspect more deeply or escalate.

### Edit notes

Use `set-slide-notes` (plain `text` or rich `paragraphs`). Notes-only edits usually do
not need PNG rendering.

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [{ "op": "set-slide-notes", "slide": 4, "text": "Speaker note update." }]
}
```

### Footer, date, or page number

Inspect the target slide/object and use `set-text-frame`. Do not blanket-clear footer
or page-number placeholders across the deck unless the user explicitly asked for
a batch edit and dry-run proves the target set.

### Color or font tweak

For a single text frame, prefer `set-text-frame` over
run-level edits:

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "set-text-frame",
      "slide": 1,
      "shape": { "name": "Subtitle 2" },
      "font": { "name": "Aptos", "color": "1F2937" }
    }
  ]
}
```

If this becomes a theme or brand change, leave Micro Edit and read
`../content/styles-and-themes.md`.

### Replace one image

Use inspect to capture the old picture bbox and crop context. Replace only the
intended picture. Render the changed slide PNG unless the replacement is the same
asset with minor metadata changes. If crop, aspect ratio, provenance, or identity
assets matter, escalate to normal Edit and asset handling.

## Lightweight QA

Always keep these artifacts:

- `inspect.json`
- `edit-contract.json`
- `patch.json`
- `dry-run.json`
- `apply.json`
- `pptx-diff.json`
- `evidence-manifest.json`
- `edit-contract-gate.json`
- `xdoc-capabilities.json` when generated by the run setup

Run changed-slide PNG preview when any of these are true:

- replacement text is materially longer
- language or script changes
- title, subtitle, footer, date, page number, or tight bbox is touched
- font, color, crop, image, or visible style changes
- dry-run reports text-fit, overflow, or visual-risk warnings

Changed-slide preview command:

```bash
xdoc convert <run-dir>/candidate.pptx --to png --slides <1-based-slide> \
  -o <run-dir>/previews --overwrite
```

Run changed-scope `vision-diff` when the edit can affect layout, text fit, image
visibility, or style. It distinguishes new/worsened high or medium regressions
from inherited issues. Candidate-only `vision-check` may still diagnose the
final object, but inherited deck noise is not itself an edit failure.

Visible text edits require changed-slide preview because dry-run and static
vision checks can miss run-style loss in tight title/footer/label frames.
Notes/core-metadata-only edits may omit PNG rendering when the contract does
not require it; say that explicitly in the final summary.

## Final Summary

Report:

- final output path and run directory
- changed slide indexes
- selector evidence from dry-run
- whether changed-slide PNG and `vision-diff` ran, or why either was skipped
- any pre-existing issue that was not caused by the micro edit
