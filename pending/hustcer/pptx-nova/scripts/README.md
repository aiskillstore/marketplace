# pptx-nova Scripts

Required published runtime code is self-contained in this directory and uses only Node built-ins
and the disclosed xdoc executable. Optional Office integrations also require the prerequisites
listed below, including Nushell where indicated. Repository-only checks remain under tools/.

```text
scripts/
├── README.md
├── cli/                        # <workflow>/<command>.mjs entry points
│   └── office/                 # Optional macOS evidence integrations
└── lib/<domain>/<module>.mjs     # Internal reusable modules
```

CLI workflows are runtime, create, edit, refurbish, translation, deckkits, review, assets,
animation, and office. Internal domains are runtime, create, edit, refurbish, translation,
review, pptx, assets, and animation. Use concise names inside these namespaces; do not add
flat scripts or repeat the pptx-nova prefix. Internal modules must not import CLI entries or
run a CLI on import. Shared resources and child commands use lib/runtime/skill-paths.mjs,
anchored to the installed skill rather than the caller's working directory.

All paths below are relative to scripts/. Run Node entries with
`node <skill-root>/scripts/cli/<workflow>/<command>.mjs`.
The public release audit checks this layout and local module imports.

## Runtime and recovery

- `cli/runtime/probe.mjs` - capture a compact runtime capability snapshot,
  including capability truth, schema-slicing support, patch operations, bundled
  resources, compact compatibility indexes, and the exact published daemon/
  stdio JSON-RPC/MCP Agent transport contracts. Complete contracts are retained
  at `capabilities.agentTransports.daemon.contract`,
  `capabilities.agentTransports.jsonRpc.contract`, and
  `capabilities.agentTransports.mcp.contract`. Use repeatable `--require-*`
  flags for task-specific attention or strict gates instead of inferring
  features from version strings or command presence.

- `cli/runtime/init-run.mjs` - create a new `.pptx-nova/<slug>-<timestamp>/` run
  directory with starter `outline.json`, `deck_lock.json`, and `content.json`
  for a DeckKit (`--slug`, `--deckkit`, optional `--mode express|studio|edit|export`).

- `cli/runtime/remediation.mjs` - `run` captures the first `apply` submission
  into a private capsule (request, input, and asset snapshots) before any
  automatic retry; `apply` replays exactly one verified `suggestions[]`
  pointer from a retained report. A report alone cannot restore context.

- `cli/runtime/clean-open.mjs` - macOS-only live PowerPoint clean-open smoke gate;
  launches through macOS document routing and waits eight seconds by default
  so delayed chart/ChartEx Repair prompts are observable
  for deliverable PPTX files. It stages the candidate inside PowerPoint's
  sandbox tmp directory, opens that staged copy, checks System Events UI state
  for Repair dialogs, distinguishes plain Cancel buttons from repair prompts,
  and writes clean-open.json. Windows/Linux, macOS without PowerPoint, or
  missing UI scripting return `skipped`. This does not prove a clean open; the task's
  delivery policy determines whether that missing evidence is acceptable.

## Create

- `cli/create/run.mjs` - execute the standard DeckKit-first create
  pipeline from existing `content.json` and `deck_lock.json`, with optional
  `--choreography` JSON for native animation and Morph operations. It retains
  both the DeckKit and composed patches and runs
  validate-content, build, check-lock, dry-run, apply, vision-check, and
  PNG/contact-sheet preview through the shared runner runtime, preserves every
  artifact in the run directory, then atomically publishes the final output
  through `--finalize` after machine gates and hash-bound visual review pass.
  Every Create review includes `design_review.json` via the review helper's `--design-review`:
  slide-specific craft observations and a weakest-page assessment, not just mechanical passes.
  Finalization requires its audience mode to match the bound `deck_lock.artDirection.mode`;
  the locked mode controls whether a signature moment is required.
  Dry-run/apply require explicit zero semantic issues;
  vision requires a consistent, passing full-package semantic summary. `--json`
  emits a compact Agent result with
  performance evidence; use `--json-full` or the persisted
  `create-run-summary.json` only for full diagnostics.

- `cli/create/build.mjs` - build the xdoc patch JSON from DeckKit `content.json`
  (`--deckkit <id> content.json -o patch.json`), optionally writing
  `--quality-json` and failing on `--fail-on-quality warning|error`.

- `cli/create/check-lock.mjs` - validate `deck_lock.json`, `assets_manifest.json`,
  DeckKit content, and patch output before xdoc dry-run.

## Edit and templates

- `cli/edit/session-rules.mjs` - normalize explicit current-deck rules against
  the current PPTX revision, or advance a verified rule artifact after an
  accepted candidate. The default artifact name is `session-rules.json`.

- `cli/edit/session-rules-resolve.mjs` - resolve active rules against a
  structured operation plan and emit the deterministic Edit Contract overlay,
  conflicts, and stable `agentGate.nextAction`.

- `cli/edit/contract.mjs` - normalize an agent-authored existing-deck edit
  contract and bind it to the current source PPTX SHA-256 before patch/apply;
  optionally merge and hash-bind a passed session-rules resolution.

- `cli/edit/evidence-manifest.mjs` - bind the stable candidate SHA-256 to
  the exact post-apply evidence hashes before the final contract gate.

- `cli/edit/contract-gate.mjs` - verify source freshness, dry-run target
  coverage, reliable semantic-diff locality, optional text style fidelity, and
  scoped preview/vision-diff/structure evidence before an Edit or Micro Edit is
  published. Structural copy workflows may supply native `pptx-slide-copy/v1`
  evidence; the gate requires a read-only `ready` preflight whose target/donor
  whole-file SHA-256 values still match the current files, validates normalized
  package fingerprints, then validates donor/target slide
  identities, part/dependency mappings, and aggregate changed parts without
  requiring or fabricating patch `opResults`. Native copy evidence also requires
  a manifest-bound passing copy-size gate. When session rules apply, it verifies produced-object
  identity and font/fill postconditions directly from candidate PPTX bytes.
  Read its stable `agentGate.nextAction` for repair routing.
  A dedicated `document-fonts` target accepts one runtime-disclosed `set-font`
  op with exact family/selection intent, a reviewed analysis digest when needed,
  and full-deck evidence; see `references/edit/font-normalization.md`.

- `cli/edit/copy-size-gate.mjs` - inspect donor and target slide dimensions,
  verify the current `pptx-slide-copy/v1` whole-file SHA-256 bindings separately
  from its normalized OPC package fingerprints, and fail closed before apply
  when the dimensions differ. Current policy is identical-size-only: xdoc's
  `--size-strategy` accepts only `require-match` (no implicit scaling), and the
  script never asks a renderer to hide the mismatch.

- `cli/edit/template-gate.mjs` - validate strict template-following artifacts:
  frame-map coverage, empty placeholders, overlay-like additions, and identity
  asset provenance.

## Refurbish

- `cli/refurbish/plan.mjs` - build the preflight route for existing-deck
  refurbishment: readiness exception, native skinning support, fallback strategy,
  duplicate chrome policy, and required gates.

- `cli/refurbish/run.mjs` - execute the audited existing-deck refurbishment
  pipeline in a new run directory. It selects the native or fallback route, saves
  every JSON report, writes `pptx-diff.json` as the default final semantic diff,
  generates source/candidate layout snapshots, one shared
  `review-policy-evaluation.json`, and a non-governing `finding-analysis.json`
  shadow report before fidelity,
  fails closed on machine gates, renders PNG/contact-sheet evidence, and
  publishes the final output atomically. A successful run still
  reports `needs-human-review`; it never claims the visual review is complete.
  Read compact stdout first, then `refurbish-run-summary.json.agentSummary` only when deeper phase
  evidence is needed.

- `cli/refurbish/fallback-patch.mjs` - generate generic inspect-driven
  fallback artifacts (`patch.json`, `deck_lock.json`, baseline
  `content-audit.json`, and `reference-map.json`) for DeckKits without native
  skinning. It should use `refurbishProfile.fallback` when present, otherwise
  derive palette/fonts from `visualGrammar`, and consume `chrome-detect.json`
  for existing chrome restyling; do not hardcode a single DeckKit id.

- `cli/refurbish/audit.mjs` - legacy supplemental Refurbish Existing Deck audit:
  use native `xdoc pptx refurbish-audit` as the default content-preservation gate;
  keep this script only for checks not yet native, especially OOXML visible text
  leaks and forbidden shape-name regex scans.

## Translation

- `cli/translation/prepare.mjs` - scan and classify translation units,
  bind an optional external prompt and project glossary, create the compact
  translation memory plus protected-token constraints, and resume a bound review
  partition without rescanning. Constraint violations stop before `i18n-plan`.

- `cli/translation/run.mjs` - finalize an already stable translated candidate. It snapshots
  source/candidate/translation contracts, runs style, target-consistency, vision, preview, semantic,
  full-deck comparison, and publication-binding gates, and can materialize `contact-diff` aliases
  from the same compare evidence without another render. `--json` emits a compact Agent result;
  `--json-full` or `translation-run-summary.json` provides complete diagnostics. Machine success
  remains `needs-human-review`.

- `cli/translation/classify-chart-units.mjs` - convert xdoc's structurally
  inventoried but language-uncertain chart review units into explicit
  translate/preserve decisions. It binds decisions to the source scan and unit
  hashes and fails closed unless every review-only chart unit is classified.

- `cli/translation/classify-review-units.mjs` - preferred classifier for all
  language-uncertain `visibleBody`, `visibleTextAttr`, and `chartVisibleCache`
  review units. It binds decisions to the source scan and unit hashes and fails
  closed before `i18n-plan` unless every such review unit is classified.

## DeckKits

- `cli/deckkits/select.mjs` - select an eligible DeckKit from the bundled catalog.

- `cli/deckkits/design.mjs` - discover a DeckKit's design contract, registered layouts,
  content fields, and capacity guidance before authoring content.

- `cli/deckkits/readiness.mjs` - audit catalog and visual benchmark readiness.
  It uses persisted catalog benchmark evidence by default; pass `--out <dir>`
  for a live benchmark check or `--benchmark-mode required-live` for strict
  promotion gates after a benchmark run.

- `cli/deckkits/benchmark.mjs` - run bundled visual benchmark cases.

- `cli/deckkits/catalog-update.mjs` - update bundled DeckKit quality metadata.

- `cli/deckkits/refurbish-profile-fill.mjs` - generate missing
  `refurbishProfile` catalog entries for delivery DeckKits. It uses
  DeckKit-specific palette/font overrides where available, preserves true native
  skinning declarations, defaults to dry-run, and supports `--check` for CI.

- `cli/deckkits/slots.mjs` - print the slot reference (`--format md|json`)
  for one DeckKit's supported slide types.

- `cli/deckkits/slot-consistency.mjs` - maintainer guard that every
  schema-declared text slot reaches the generated patch (no ghost slots).

## Evidence and review

- `cli/review/finding-analysis.mjs` - replay source/candidate layout, semantic diff,
  optional operation evidence, and a complete review evaluation through the draft
  Finding Analysis contract. Standalone replay is always `advisory-replay`; only
  the refurbish runner emits `runner-observed` shadow evidence. Full analysis is
  written to disk while stdout stays compact.

- `cli/review/layout-snapshot.mjs` - normalize a final `xdoc pptx inspect` JSON
  into `layout-final.json`; structural layout risks are warnings, not a gate.

- `cli/review/fidelity-gate.mjs` - summarize template-following or refurbish
  evidence (`--mode template-following|refurbish`) after the template gate or
  the vision-diff/refurbish-audit steps.

- `cli/review/visual-evidence-gate.mjs` - evaluate a canonical
  `pptx-visual-evidence/v1` manifest; exit code reflects its
  `decision.action` (proceed / stop / needs human confirmation).
  Reviewed Create evidence also requires `--lock` with the run's locked audience mode.

- `cli/review/finalize-evidence.mjs` - finalize existing high-risk routes from
  the final candidate/inspect plus their existing vision/fidelity reports. It
  detects ChartEx package parts and conditionally consumes a candidate-bound
  `pptx-nova-powerpoint-snapshot.nu --method pdf-render` report. When the optional
  macOS + PowerPoint + Nushell + xdoc PDFium route is available,
  missing/stale/incomplete ChartEx evidence blocks; otherwise the baseline
  continues with an explicit unverified warning. It writes
  `layout-final.json` and `evidence-summary.json`; it intentionally excludes
  Micro Edit and does not replace mode-specific gates or PNG review. New-deck
  modes fail on missing/failed semantic vision evidence; existing-deck modes
  disclose full-package semantic residuals without incorrectly scoping them to changed
  slides. Read
  `evidence-summary.json.agentSummary` for the stable agent-facing summary.
  It refuses to replace `layout-final.json` or `evidence-summary.json` unless
  `--overwrite` is passed for the current run.

- `cli/review/feedback-gate.mjs` - final-response guard for Feedback Mode. It
  detects feedback trigger phrases from the original prompt or accepts
  `--require-feedback`, checks that `<run-dir>/skill-feedback.md` exists and is
  not a TODO template, and writes `feedback-gate.json`. For `create`,
  `refurbish`, and `translation`, pass `--workflow`; the gate also validates the
  workflow's exact seven-row 0-10 process scorecard, fixed weights, evaluations,
  and weighted overall score. Use `--strict` before the final response when the
  task requested skill feedback, then print the validated scorecard in the
  terminal response.

- `cli/review/multi-column-scaffold.mjs` - generate the structured manual
  review record from the final candidate, final `vision-diff`, and final xdoc
  preview manifest. It resolves each zero-based vision slide to the one-based
  preview page, verifies actual PNG hashes and dimensions against the manifest,
  and leaves only reviewer, decision, checks, and note for manual completion.

- `cli/review/multi-column-gate.mjs` - bind final translation candidate,
  final vision-diff, exact multi-column slide/shape findings, and full-size PNG
  human-review evidence. It can close only
  `multi-column-text-layout-review`; all other new or worsened high/medium
  vision findings remain fail-closed blockers.

- `cli/review/compare.mjs` - write a high-DPI full-deck before/after compare by
  delegating atomic parts to `xdoc pptx contact-diff`. With `--slide-count`,
  decks over the default 20-slide chunk size produce numbered PNGs and a
  `pptx-nova-compare-manifest/v1`; a retryable 192 DPI `render_error` retries
  only that part once at 144 DPI.

- `cli/review/compare-gate.mjs` - delivery guard for compare artifacts. It
  validates either the compatible single PNG or every multipart path, hash,
  report, attempt history, and exact slide coverage. It also requires the
  xdoc-reported candidate identity, staged final PPTX, and published final PPTX
  to share one SHA-256. With `--publish`, it stages the complete delivery
  bundle, publishes compare siblings first and the final PPTX last, verifies
  every destination, and writes `<kind>-compare-gate.json` only after
  `finalBinding.status=bound`.

- `cli/review/semantic-audit.mjs` - lightweight chart/table semantic audit for
  data-driven, Studio, structural edit, template-following, and refurbish runs
  that contain native chart/table ops. Through the shared chart normalizer it
  validates classic `data`, ChartEx `dataEx`, source/claim disclosure, and final
  native chart/table object presence without attempting a full OOXML
  equivalence audit. Existing reports require an explicit current-run
  `--overwrite`.

- `cli/review/visual-review.mjs` - structured PNG/contact-sheet review helper. It
  records required visual QA checks into visual_review.json, validates that
  visual evidence and reviewed slide counts are present, and leaves actual
  visual judgment to the human or agent reviewer.

- `cli/review/structure-check.mjs` - lightweight PPTX OOXML structure check. It
  scans XML inside the PPTX for expected font declarations, expected sRGB/theme
  colors, and empty/default-text placeholder residue, then writes
  structure-check.json for the final evidence summary. Existing reports require
  an explicit current-run `--overwrite`.

## Asset tools

- `cli/assets/icons.mjs` - query and generate the bundled Tabler icon pack.

- `cli/assets/formula-render.mjs` - materialize literal-LaTeX draft SVGs from a dedicated
  formula manifest (`--provider auto|text-svg`, `--dry-run`). It does not typeset math or skip
  existing/native entries; use fresh paths and preserve supplied or externally typeset assets.

## Animation

- `cli/animation/examples.mjs` - executable focus, KPI zoom, and rotated exit
  examples using the public xdoc operations. Writes patches and structural evidence
  to a new run directory; see `references/content/morph-choreography.md` for the workflow
  and the separate PowerPoint evidence requirements.

## Optional Office integrations

- `cli/office/morph-playback.nu` - optional macOS-only PowerPoint-native Morph semantic
  playback probe. It verifies the recognized by-object/by-word/by-char entry
  effect, exact adjacent slide navigation, animation-enabled slide show, and
  required expected duration plus optional resave evidence. It does not capture
  interpolation frames and therefore does not establish visual rendering parity.
  It starts at the requested source using a temporary slide-show range on the
  staged copy and restores the original range before resaving. Navigation and
  playback use separate bounded timeouts. Optional resave requires
  editing-enabled PowerPoint and `unzip`; empty or corrupt packages fail before
  publishing the resaved file or a passing report.

- `cli/office/powerpoint-snapshot.nu` - optional macOS-only evidence helper that stages the exact candidate in
  PowerPoint's sandbox, render requested slides through PowerPoint PDF export,
  and emit candidate/hash/image-bound `pptx-snapshot/v1` evidence. `window`
  mode additionally fails closed unless the foreground process, presentation,
  slide, canvas, and screenshot scale remain stable before and after capture.
  It requires Nushell and, for the preferred `pdf-render` route, xdoc PDFium rendering; when
  unavailable, the baseline Node/xdoc workflow continues with explicit
  unverified evidence and must not claim PowerPoint-native verification.

- `cli/office/slide-visibility.mjs` - read-only PPTX visibility helper used by the optional PowerPoint snapshot integration.

## Internal modules

- `lib/review/policy.mjs` - shared pure policy evaluator for hash-bound
  reviewed findings. It never deletes detector output: exact source SHA-256,
  slide part, shape id, placeholder type/idx, and expected state are required
  before an actionable finding can be reclassified as `reviewed`. Stale,
  duplicate, ambiguous, and unused rules fail closed. Fidelity and strict
  template gates use this same module instead of local boolean allowlists.

- `lib/review/layout-snapshot.mjs` - pure layout detector shared by the layout CLI and
  refurbish source/candidate adapters. `lib/review/finding-analysis.mjs` is the pure FA
  decision seam; neither module reads files, launches commands, or renders.

- `lib/runtime/progress.mjs`, `lib/refurbish/style.mjs`,
  `lib/edit/session-rules.mjs`, `lib/review/vision-baseline.mjs`, and the
  remaining `lib/<domain>/*.mjs` files are import-only shared modules used by the
  runners and gates above; they have no CLI entry point.

- `lib/pptx/chart-semantics.mjs` - shared classic Chart/ChartEx semantic normalizer
  used by lock checking and semantic audit. It resolves `data` versus `dataEx`,
  slide-level semantic sources, and kind-specific dimensions from one contract
  instead of duplicating divergent validation logic.

- `lib/assets/tabler-icons.mjs` - reusable icon pack generation, loading and lookup;
  `cli/assets/icons.mjs` owns only command invocation and error reporting.

Repository-root `tools/` contains maintainer gates for this public repository,
including `tools/pptx-nova-smoke-test.mjs` and
`tools/pptx-nova-audit-public.mjs`. Published skill users should call runtime
scripts from this directory.
