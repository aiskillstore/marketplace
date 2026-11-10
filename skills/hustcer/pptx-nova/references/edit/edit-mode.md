# Edit Mode

Read this file when the user wants to modify an existing `.pptx`: change text,
add/remove slides, update tables/charts, replace images, add notes, rebrand an
existing deck, or copy slides from another deck.

Editing is selector-sensitive. The main risk is changing the wrong object.

## Load Order

For small localized text, notes, footer/date/page-number, metadata, color/font,
or single-image edits, read `micro-edit-cheatsheet.md` instead of this file. Come
back here only when the selector is ambiguous, the edit touches complex objects,
or the request grows beyond a localized change.

For existing deck edits read:

1. `../common-workflow.md`
2. `edit-contract.md`
3. `session-rules.md` only when `deck_lock.sessionRulesPath` exists or the user
   explicitly states a future/carryover rule
4. This file
5. `inspect-and-edit.md` for selector details and common edit patterns
6. `patch-ops-cheatsheet.md` only when writing patch ops

Read `../content/charts.md`, `../content/tables.md`, `../content/styles-and-themes.md`, `../content/animations.md`, or
`../content/data-driven.md` only when the requested edit touches those domains.

## Standard Edit Flow

Inspect first:

```bash
xdoc pptx inspect input.pptx --daemon --json
```

Save the inspect output in the run directory. Use it to identify slide indexes,
shape IDs, names, placeholders, bounding boxes, table/chart facts, notes, and
warnings such as SmartArt or transitions.

When the target object is not immediately obvious from a small inspect snippet,
use read-only `select` to get a compact candidate list:

```bash
xdoc pptx select input.pptx --query '{"textRegex":"Revenue"}' --json \
  > <run-dir>/select.json
xdoc pptx select input.pptx --query query.json --slides 2-4 --json \
  > <run-dir>/select-scoped.json
```

Use `matches[].patchSelector` only after confirming `summary.matchCount`,
`text`, `bbox`, and `name` match the user intent.

If current-deck session rules exist, write `session-operation.json` and run
`<skill-root>/scripts/cli/edit/session-rules-resolve.mjs --strict` before the contract. A passed
resolution contributes rule-owned targets and preserve requirements. If no
active rule applies, continue normally without additional evidence or user
confirmation.

After target resolution, write `edit-contract-draft.json` and normalize it to
`edit-contract.json` with `cli/edit/contract.mjs`. Bind each target to the
patch `opIndexes[]`, expected change categories, allowed changes, preserve
rules, and required evidence. Do this before writing/applying the patch so the
contract remains the source of truth rather than a description of whatever the
candidate happened to change.

When the resolver produced an overlay, pass
`--session-rules-resolution <run-dir>/session-rules-resolution.json`. Do not
manually copy rule targets into the draft; the normalizer must bind and merge
the resolution.

Write a patch using the most specific stable selector available:

1. `id` from inspect
2. designer-provided `name`
3. placeholder `{ type, idx }`
4. query selector only when ID/name/placeholder are not enough

Dry-run before writing:

```bash
xdoc pptx apply -p patch.json -i input.pptx -o out.pptx \
  --daemon --dry-run --json
```

Check `opResults[].resolvedSelectors[]` for every op: require numeric
`resolved.slide` and `resolved.id`, and check the operation-time target against
the intended object. The normalized `input` echo uses explicit integer EMU
geometry; it is not a complete authored patch. If a selector is ambiguous, use the
reported `suggestions[].remediation`: verify its original request/input target,
then dry-run its complete replacement request from the retained original input.
Use the snapshot consumer in `../runtime/troubleshooting.md` for cross-process retries. Do not ignore ambiguous or
unexpected selector resolution. Require an explicit empty `semanticIssues[]`;
it is the full-package before/after semantic regression gate for the proposed
edit, including indirect relationship and content-type effects.

After dry-run is clean, apply to a run-dir output:

```bash
xdoc pptx apply -p patch.json -i input.pptx -o out.pptx --daemon --json
```

Apply must also return `semanticIssues: []`. Stop and repair the patch when it
reports a semantic issue; do not rely on a later full-deck scan to distinguish
the edit from inherited debt.

Semantic issues may carry `remediation.kind="apply-to-document"` with a guarded
`repair-child-order`, `repair-preset-adjustments` or `repair-relationships` patch. Match `target.inputSha256`
against the exact delivered document before applying that repair-only patch
once. Preserve existing intent and raw XML permissions; the restricted repair
actions declare `requiresRawXml:false`. Dry-run candidates have no delivered
target and cannot supply executable document repairs. On legacy decks,
`vision-check.semanticIssues[]` exposes inherited relationship debt. After a
verified repair, re-run vision-check on the new bytes before selecting another
proposal. Never merge repair operations into the original creation request.
Keep findings without executable remediation as diagnostics and follow their
unavailable reason; do not invent a target or an automatic repair.
Preset-adjustment normalization has `autoRetry:false`: review and explicitly adopt
the proposed change within the authorized task before using `--reviewed`. It requires
the exact part hash even when an element hash is supplied; any intervening edit to
that part requires fresh diagnosis. See `../runtime/troubleshooting.md` for its Office
interoperability boundary and `native-shape-editing.md` for geometry edits.

Once the candidate is stable, run one semantic diff and the evidence required
by `edit-contract.json`, then run `<skill-root>/scripts/cli/edit/contract-gate.mjs --strict`.
Do not publish while `agentGate.passed=false`. For visible text-only edits that
must preserve formatting, require `style-diff`; whole-frame `set-text-frame` can
silently replace small styled runs even when dry-run and vision-check pass.

Run changed-scope `vision-diff` and render PNG/contact-sheet previews when the edit changes
layout, visual style, chart/table contents, images, or anything user-visible
enough to risk regression. For append or targeted edit workflows, inspect the
changed slide indexes explicitly and review their PNG images at full size before
using candidate-only `vision-check` for diagnosis rather than treating its full-deck summary as blocking. Existing decks often
have unrelated legacy issues; separate "changed-slide blockers" from
"pre-existing residual risk" in the final summary.
`vision-check.semanticIssues[]` is always full-package evidence, including when
`--slides` is present. Disclose unresolved entries and compare them with the
source/edit evidence; do not reinterpret them as slide-scoped findings.

For targeted visual edits, run scoped machine and PNG gates first:

```bash
xdoc pptx vision-diff --source input.pptx --candidate out.pptx --slides 25-38 --json > <run-dir>/vision-diff.json
xdoc pptx preview out.pptx --slides 25-38 \
  --output-dir <run-dir>/previews \
  --contact-sheet --contact-output <run-dir>/previews/contact-sheet.png \
  --overwrite --json > <run-dir>/preview.json
```

Require `vision-diff.agentGate.passed=true`: inherited source issues may remain,
but new or worsened high/medium issues block. Use a separate scoped
`vision-check` only when its diagnostics are needed, and disclose residual
full-deck risk separately.

For structural edits—slide/object additions or deletion, geometry/layout,
theme/brand, chart/table, image/crop, or multi-slide visual changes—save
`final-inspect.json` after apply and run
`<skill-root>/scripts/cli/review/finalize-evidence.mjs --mode structural-edit --changed-slides 25-38`
with `vision.json` before PNG review. It writes `layout-final.json` and
`evidence-summary.json`. With a changed-slide scope, high/medium issues outside
the scope are recorded as `deckResidualRisk` rather than keeping the finalizer in
warn. Localized Micro Edit remains on its separate fast path.

For every generic Edit Contract, run one semantic diff after the final
candidate is stable. Structural edits and user-requested change audits already
need this evidence:

```bash
xdoc pptx diff --source input.pptx --candidate out.pptx \
  --detail full --json > <run-dir>/pptx-diff.json
```

Check `schemaVersion == "pptx-diff/v1"` and `status == "success"`.
The Edit Contract requires `detail=full` because summary rollups do not disclose
per-object identity, text or field-level locality. Collect this once on the stable
candidate rather than running summary first and immediately repeating it.
Compare `agentGate.semanticStatus`, `summary.reliableChanges`, `summary.byCategory`,
`styleChangeSummary`, and `slides[]` against the intended edit scope. Reliable changes outside the
requested slides or object categories are blockers until explained or fixed.
`uncertainChanges` and `unsupportedRegions` trigger targeted review; do not use
them as proof that nothing changed. Avoid running this in each patch iteration
because it is slower than inspect/select/dry-run.

## Micro Edit Flow

Micro edits have a separate one-screen route in `micro-edit-cheatsheet.md`.
Follow that file first. This document is the escalation path when the task needs
deeper selector analysis, multi-object edits, chart/table/image semantics,
template rules, brand/style changes, or full visual QA.

## Common Edit Operations

- Text replacement: `set-text-frame`, `set-paragraph`, `set-run`.
- Paragraph formatting: `set-paragraph` with a nested `format` object; do not put
  `alignment` at the op top level.
- Theme/font changes: `set-theme` (`colors` / `fonts`), or brand helpers.
- Slide duplication: `duplicate-slide`.
- Cross-deck whole-slide copy: `xdoc pptx slide-copy -i target.pptx`. Use
  `--slides 1,3,5-8` for a 1-based selector or `--all`; the two selectors are
  mutually exclusive and omitting both copies only donor slide 1 (there is no
  `--slide` option). Default to
  `--template-strategy register-source --size-strategy require-match`; use
  `rebind-target` only as an explicit target-inheritance decision. Copy multiple
  slides in one transaction and retain the native `pptx-slide-copy/v1` report
  for the structural Edit Contract. Require its read-only `ready` preflight,
  current target/donor fingerprints, explicit strategies, reviewed
  `templates[]` outcomes, and no blockers instead of creating intermediate
  decks or fake patch `opResults`.
- Chart data: `set-chart-data`; read `../content/charts.md` for chart semantics.
- Table edits: `set-table` (cells/style/dimensions/borders), `set-table-data`
  (matrix/CSV/JSON bulk replacement); read `../content/tables.md` for formulas and CSV imports.
- Image replacement and crop/mask changes: use `set-image` for an existing
  picture (`crop` / `maskPreset`) or remove/add a picture when replacing media.
- Notes: `set-slide-notes` (plain `text` or rich `paragraphs`).
- Animations/transitions: read `../content/animations.md`; use `set-slide-transition` or
  `set-slide-animations` only after inspect/dry-run proves the timing is in the
  supported safe subset.

## Preserve Constraints

Preserve SmartArt, VBA macros, unsupported animation/timing, and complex objects
unless the user explicitly asks for a destructive transformation and the tool
supports it. SmartArt stays read-only, but inspect's `preserveOnly[]` now embeds
a `diagram` summary on `diagramData` entries (layoutId, node/connection counts,
textPreview, hosting shape id/name) — use it to describe the diagram, decide
preserve vs native-shape rebuild, and flag SmartArt text that `replace-text`
and i18n ops cannot reach. Basic editable animation steps are no longer automatically
preserve-only: inspect `animations[].editable` and `animationCapabilities`
before deciding. If inspect reports unsupported objects, say what can be
preserved and what cannot be edited.

## Template-Sensitive Edits

When the input deck is a template or the user asks to preserve the source deck's
look, apply the stricter `template-following.md` rules:

- Edit inherited objects in place whenever possible. New objects are allowed
  only for explicit additions, not as a cover-up for old content.
- Do not overlay opaque shapes, screenshots, or full-slide images to hide
  template text, logos, footers, page numbers, or placeholders. Rewrite,
  replace, or delete the original object.
- Do not blanket-clear all text. Default unmentioned source objects to keep.
- Treat empty structural placeholders as real objects. Fill or delete title,
  body, date, footer, and slide-number placeholders explicitly.
- If replacing logos, product screenshots, customer marks, people photos, app
  icons, or other identity assets, register provenance in `assets_manifest.json`
  or leave a `needs-user` placeholder. Do not generate lookalike official
  assets.

## In-Place Edits

If the user asks to modify the source file in place, still dry-run and validate
against a run-dir copy first. Only write back after validation succeeds.
