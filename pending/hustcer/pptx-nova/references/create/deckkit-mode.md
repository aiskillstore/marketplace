# DeckKit Mode

Read this file for any create workflow that can use an existing DeckKit, and for
maintaining user-facing DeckKit examples.

DeckKit is the default path for delivery-quality new decks. It keeps the visual
language, page geometry, density limits, and reusable components in a frozen
generator so ordinary creation only needs a small `content.json`.

If the selected catalog entry has `designContract`, also read `design-contracts.md` and its
`intent.md`. Discover allowed layouts with `cli/deckkits/design.mjs`; use registered
`layoutId` values rather than writing coordinates. The normal build/create runner owns the
resolved design plan, style checks and post-apply native-data readback.

## Selection

Read [Design quality](design-quality.md) before selection. The current catalog determines eligible
production/default kits; scenario, language, density and required slide types govern ranking.

Before writing `content.json`, select a DeckKit from
`assets/deckkits/catalog.json`:

```bash
node <skill-root>/scripts/cli/deckkits/select.mjs \
  --brief '<user brief>' --language zh --target delivery --json
```

An explicit `--scenario` overrides brief inference. Known Chinese/English topic aliases only route
the topic; they do not choose a visual identity. Missing or unknown intent earns no match points
and yields a warning. Open the leading eligible rendered examples before committing to a kit.
Readiness proves engineering eligibility, not taste; explicit style and content fit still win.

Use the selected DeckKit's `visualGrammar` as the deck's visual contract:
positioning, mood, signature elements, composition rules, and avoid list.
For refurbishing or rebuilding an existing deck, that contract also covers the
target palette, typography hierarchy, header/footer, page numbers, backgrounds,
rules, chart/table treatments, and page chrome. If you copy a source slide or
source object for fidelity, re-theme the editable object into the target DeckKit
style; do not preserve the source deck's old color system, master chrome, header,
or footer unless that visible detail is itself user-confirmed content.
For existing-deck refurbishment, apply the DeckKit contract with the native
skin-first command before considering a rebuild:
`xdoc pptx refurbish-skin --source source.pptx --deckkit <id> --output out.pptx --json`.
It copies and preserves the source deck, replaces old chrome/background, applies
DeckKit chrome, remaps text/shapes/tables/charts, and runs audit/vision gates.
Use the lower-level `chrome-detect -> chrome-remove -> remap-theme --scope
text,shapes,tables,charts -> chrome-apply` chain only when the deck needs a
custom chrome-removal policy, a native skinning DeckKit is unavailable, or a
page-level repair requires inspecting intermediate reports.

For the standard existing-deck workflow, run the bundled orchestrator:

```bash
node <skill-root>/scripts/cli/refurbish/run.mjs \
  --deckkit <id> \
  --source source.pptx \
  --output candidate.pptx \
  --json
```

It creates a new run directory, saves the plan and inspect evidence, executes the
native or fallback route, fails closed on machine gates, renders PNG/contact-sheet
artifacts, and publishes the requested output only after those gates pass. Exit 0
means the machine pipeline completed; `status: "needs-human-review"` remains until
the contact sheet and suspicious full-size PNGs are reviewed.

For Agent callers, `--json` keeps stdout reserved for the compact Agent result and saves the complete
summary in the run directory. It streams structured `pptx-nova-progress/v1` JSONL on stderr. Compare parts and
heartbeats make long high-DPI renders observable. Each run persists the catalog
readiness decision in `catalog-readiness.json`; optional live benchmark readiness
uses the separate `delivery-readiness.json` artifact.

The final refurbish comparison defaults to 20 slides per PNG. Small decks keep
the single `refurbish-compare.png`; larger decks receive numbered parts and a
coverage manifest. Each part starts at 192 DPI. Only a structured retryable
`render_error` may retry that part once at 144 DPI; any second failure blocks the
compare gate and prevents both compare publication and final PPTX publication.
Use `--compare-chunk-size <n>` only when the environment requires a different
upper bound.

To inspect the route without executing it, generate the plan directly:

```bash
node <skill-root>/scripts/cli/refurbish/plan.mjs \
  --deckkit <id> \
  --source source.pptx \
  --output candidate.pptx \
  --json > refurbish-plan.json
```

If the user explicitly named a non-production DeckKit, add `--explicit`. The plan
is the source of truth for native skinning availability, `requiredGates[]`,
fallback style ops, and duplicate chrome policy. A `blocked` plan is a real
blocker; do not discover the same failure later by trial-running `xdoc`.
For DeckKits without native skinning, the plan should return `manual-fallback`
or `explicit-manual-fallback` instead of blocking when a generic inspect-driven
fallback can preserve source slides and editable objects. In that route, run
`scripts/cli/refurbish/fallback-patch.mjs` after `inspect` and
`chrome-detect` to generate `patch.json`, `deck_lock.json`, baseline
`content-audit.json`, and `reference-map.json` from the DeckKit's
`refurbishProfile.fallback` or, when absent, from `visualGrammar`.

The runner uses the same structured plan API; it does not execute the human-readable
shell strings in `commands[]`. In `--route auto`, only native
`UnsupportedComplexity` triggers a recorded switch to the catalog-driven fallback.
Other native failures stop the run, and the runner never switches DeckKit silently.

For the selected DeckKit, run readiness:

```bash
node <skill-root>/scripts/cli/deckkits/readiness.mjs \
  --deckkit <id> \
  --target delivery
```

By default readiness uses the persisted `catalog.quality.benchmark` evidence,
not a cwd-local `.tmp` benchmark directory. Passing `--out <dir>` requests a live
benchmark evidence check for that directory; promotion/CI workflows that must
fail when live benchmark artifacts are missing should use
`--benchmark-mode required-live`.

Delivery auto-selection only allows `readiness in ["production", "default"]`.
Use `candidate` only for drafts, migration checks, or explicit human approval.
When the user explicitly names a candidate DeckKit for an existing-deck
refurbish, keep that DeckKit as the visual target, but record the readiness
exception in `deck_lock`/final summary and tighten the gates: `vision-diff`
must have no new high/medium from the agent's restyle, PNG review must confirm
the target visual grammar is visible, and content audit must prove no source
content/object semantics were reduced.
Use `--explicit` with readiness in this case so the JSON reports
top-level `agentGate.canContinue` / `agentGate.nextAction` as the authoritative
Agent decision, plus `explicitSelection.passedByExplicitException`,
`explicitSelection.canUseExplicitException`, `mode`, native skinning, fallback
profile, and required gates instead of acting like a terminal command failure.
Do not treat `explicitSelection` as the overall readiness decision: production
and default DeckKits usually do not need an explicit exception at all.

Do not assume every DeckKit id is supported by every xdoc skinning command.
`refurbish-skin` and `chrome-apply --deckkit` require native skinning catalog
entries; unsupported ids must fail with JSON instead of silently falling back.
For a named DeckKit without native chrome/remap support, implement the visual
contract with the fallback patch generator plus inspect-driven patch ops for
background, text, fills, lines, and page chrome; save command error JSON as
evidence instead of silently switching to another DeckKit. The generator is the
default starting point for all DeckKits because it uses catalog data rather than
DeckKit-specific hardcoding.
Fallback minimums are mandatory, not suggestions:

- Run and save `refurbish-plan.json`, `chrome-detect.json`, dry-run/apply report,
  `vision-diff.json`, and final `refurbish-audit` or supplemental audit report.
- Run and save `fallback-patch-report.json` from
  `cli/refurbish/fallback-patch.mjs` when route is `manual-fallback` or
  `explicit-manual-fallback`.
- For whole text-frame restyling, use `set-text-frame` with a `font` object;
  use indexed `set-run` only after inspect exposes the
  actual paragraph/run target or a minimal smoke proves the index exists.
- Duplicate page chrome must resolve by `replace`, `restyle-existing`,
  `skip-duplicate`, or `add`; do not nudge overlapping duplicate header/footer,
  page number, or rule shapes into place.
- The fallback must show target palette, typography, background, rules, and page
  number chrome in inspect/PNG evidence; a text-only or light-line pass is not a
  refurbish deliverable.

Before writing `content.json`, generate the DeckKit slot reference and keep it
beside the run artifacts:

```bash
node <skill-root>/scripts/cli/deckkits/slots.mjs \
  --deckkit <id> \
  > deckkit-slots.md
```

Use it as the per-slide quick reference for fields, required slots, item limits,
and approximate text budgets. Do not infer slot limits by reading `.kit.mjs`
source when a schema row exists.

For formal persuasive decks, also read `narrative-quality.md` before
`content.json`. The DeckKit chooses visual grammar; the narrative layer chooses
what each slide must prove.

## Production Path

Use this flow for DeckKit-first creation:

```text
outline.json
  -> deck_lock.json
  -> content.json
  -> <skill-root>/scripts/cli/create/run.mjs
  -> PNG/contact-sheet review
```

The preferred agent-facing command is:

```bash
node <skill-root>/scripts/cli/create/run.mjs \
  --deckkit <id> \
  --content content.json \
  --lock deck_lock.json \
  --output out.pptx \
  --run-dir <run-dir> \
  --json
```

It executes the normal machine chain (`validate-content -> build ->
check-lock -> dry-run -> apply -> vision-check -> preview/contact-sheet ->
publish`) and preserves each report in the run directory. Read
`create-run-summary.json.agentSummary` first for gate status and artifact
pointers; open low-level reports only when a gate fails or needs diagnosis.

The equivalent manual command sequence for debugging is:

```bash
node <skill-root>/assets/deckkits/validate-content.mjs \
  content.json --deckkit <id> --mode delivery
node <skill-root>/scripts/cli/create/build.mjs \
  --deckkit <id> \
  content.json \
  -o patch.json \
  --quality-json quality.json
node <skill-root>/scripts/cli/create/check-lock.mjs \
  --lock deck_lock.json --content content.json --patch patch.json --json
xdoc pptx apply -p patch.json -o <run-dir>/candidate.pptx --overwrite --dry-run --json
xdoc pptx apply -p patch.json -o <run-dir>/candidate.pptx --overwrite --json
xdoc pptx vision-check <run-dir>/candidate.pptx --json
```

`--overwrite` is safe here only because `candidate.pptx` is a rebuildable artifact inside the current
run directory; never use this pattern to replace a pre-existing user final output. If either apply
command exits non-zero, stop immediately and do not run vision-check on a stale candidate. After a
successful retry, confirm the candidate modification time or SHA-256 changed before continuing.

Use the generic build driver by default. Only write a run-dir `build.mjs` when
developing a new DeckKit or debugging the generator itself. Keep the content
layer separate from the visual generator.

## Content Rules

`content.json` is the change layer. It should contain business content, page
types, and structured slide data. Do not put arbitrary `customOps` in delivery
content unless the DeckKit contract explicitly allows it.

For formal decks, content must preserve the lock's claim/proof intent:

- use `claimTitle` to derive the strongest display headline only when it fits
  the DeckKit title slot; otherwise keep the complete claim in `deck_lock` and
  use a shorter `data.title` / `data.subtitle` plus callout or proof object
- map `proofObject` to structured fields such as chart data, table rows, stages,
  workflow nodes, timeline items, or comparison columns
- keep `rhythm`, `layoutIntent` / `macroLayout`, and `visualDensity` aligned with
  the chosen slide type and the slot budget
- if a DeckKit cannot express the proof object without generic bullets, extend
  the DeckKit rather than hiding the argument in prose
- display `title` and `subtitle` should be short, scannable, and layout-safe;
  avoid sentence-ending periods in both fields, with `?` / `!` only when the
  rhetoric explicitly needs them
- user-specified outline titles/subtitles override these style preferences:
  preserve them as display text, mark `titleSource: "user"` /
  `subtitleSource: "user"` in `deck_lock`, and only adjust after a fit failure
  or explicit polishing request

Before running `validate-content.mjs`, read the slide row in `deck_lock.json`
beside the content slide you are writing. This is not a new approval step; it is
the guard against long-deck drift. If the current content would change the slide
from "evidence chart" to "generic bullets", or from `breathing` to a dense grid,
fix the source plan or choose a different DeckKit slide type before generating
patch ops.

Run validation before dry-run. In delivery mode, missing required slots,
disallowed `customOps`, schema errors, blocking fit diagnostics, and diversity
gate failures must be fixed before any apply. Slot budget warnings are still
actionable: fix likely subtitle/label widow lines and dense text before relying
on PNG review.

If validation reports density/fit warnings, prefer deleting text, splitting
slides, changing a slide type, or using a DeckKit-supported layout variant.
Avoid patching around the DeckKit with raw coordinates.

When a deck has more slides than reusable page types, reuse is expected. Keep
the same slide type at least three slides apart when possible, and vary accent,
density, `layoutIntent`, title structure, or content rhythm on reused layouts.
If the outline forces closer reuse, note the tradeoff in `deck_lock.assumptions[]`
and rely on PNG/contact-sheet review to verify the rhythm.

For decks covered by `narrative-quality.md`, repeated slide types also need a
different `macroLayout`, proof object, or density treatment. A clean repeated
template is still weak if the contact sheet reads like a template pack.

## When DeckKit Is Not Enough

Do not fall back to a one-off large patch just because a page is hard. If the
deck needs a new reusable page type, component, or visual language, read
`deck-generator-workflow.md` and create or extend a DeckKit. The old showcase examples have retired as the production path; production and regression now
flow through DeckKit plus `benchmarks/visual/`.

For refurbishing or rebuilding an existing deck, the source content contract
outranks the current DeckKit catalog. If no existing page type can carry the
source slide's full text, table/chart semantics, media objects, diagrams, notes,
or editability requirements, extend the target DeckKit first. Do not squeeze the
source into an unsuitable card/table/menu layout by summarizing, dropping
objects, merging fields, rasterizing editable content, or changing slide
ownership.

When extending an existing DeckKit, update every public contract in the same
change: the `.kit.mjs` dispatch, `assets/deckkits/catalog.json`
(`coverage.slideTypes`, `supportedSlideTypes`, `layoutContract.slideTypes`,
`visualGrammar.slideRhythm`, and `diversityGate.groups`), and
`schemas/content.schema.json`. If the new page type consumes image assets such
as user-provided photos, product screenshots, or source deck picture objects,
keep `content.json` paths short and resolve them with `--asset-root` so fit
diagnostics do not treat long filesystem paths as visible text. For refurbish
workflows, do not design page types that depend on rendered source-slide
screenshots; those PNGs are review evidence, not deliverable content.

Use `assets/examples/generator/deck-generator-template.mjs` only as a development starting
point for creating or extending DeckKits. Do not use it as the default delivery
path when a production/default DeckKit is available.

## User-Facing Examples

Curated examples live in:

```text
assets/examples/deckkits/<deckkit>/
```

Each directory contains `deck.pptx`, `contact-sheet.webp`, `content.json`,
`brief.md`, and `summary.json`. Use them to understand the DeckKit's expected
content shape and visual output.

Maintain examples with:

```bash
just deckkit-examples
just deckkit-examples check
just deckkit-examples all
just deckkit-examples all --update-baseline
```

The update script runs golden benchmark cases, verifies gates, converts contact
sheets to WebP, and writes only changed hashes. When DeckKit code, content, and
xdoc output logic do not change, repeated `just deckkit-examples` runs should
not create git-visible changes.

`just deckkit-examples all` runs every visual benchmark case currently registered
in `benchmarks/visual/index.json`. Add `--update-baseline` only after reviewing
the current low-severity vision findings; it writes reviewed
`*.vision-baseline.json` files so future runs surface only new or changed low
findings.

## Deep References

- `express-mode.md` for quick prompt-to-deck creation.
- `deck-generator-workflow.md` for creating/extending DeckKits.
- `design-lock-and-assets.md` for `deck_lock.json` and asset manifests.
- `../review/visual-qa-and-asset-slots.md` for image slots and visual QA.
- `rich-deck-patterns.md` only when a DeckKit is unavailable and the deck needs
  manual richness patterns.
