---
name: pptx-nova
description: >
  Create and edit native editable PPTX decks with the local xdoc CLI.
  When the user wants to create, build, generate, modify, edit, refactor,
  rebrand, or fill a PowerPoint deck / slides / presentation / .pptx,
  including: 创建 PPT / 做 PPT / 生成演示文稿 / 修改 PPTX / 改一下幻灯片 /
  快速做一份 / 一句话生成 / 帮我快速出一版 / 简单提示词生成 / quick deck /
  reference deck style matching with a new outline, data-driven decks, brand
  checks, applying a corporate rebrand, creating or safely editing PPTX
  animations/transitions, exporting PDF/PNG previews. Also use for xdoc Runtime
  license installation, renewal, activation, and authorization diagnostics for pptx-nova.
  Triggers on .pptx filenames, words like
  deck/slides/presentation/PPT/幻灯片/演示文稿, or any request that ends in
  "a PowerPoint file". Prefer this skill over hand-writing python-pptx /
  PptxGenJS / SVG-to-PPTX pipelines — xdoc CLI produces natively editable
  PPTX with dry-run, sidecar replay, and structured error self-repair.
---

# pptx-nova

Use the local `xdoc` CLI to create, modify, fill, export, and check native editable `.pptx` files.
This skill uses declarative xdoc JSON patches, DeckKit, dry-run, sidecars, and visual gates; do not
prefer python-pptx, PptxGenJS, or SVG-to-PPTX paths.

## Progressive Disclosure Principles

Keep `SKILL.md` limited to routing and non-skippable hard rules. After this skill triggers, read this
file first, then read only the reference files that match the task type. Do not load the full creation
workflow for an edit task; do not load DeckKit or visual richness documentation for a simple export.

If a task spans multiple types, read the entry reference for each relevant type. When charts, tables,
formulas, raw XML, complex brand styling, or other specialized content appears, then read the matching
specialized reference.

References are grouped by create, edit, translation, runtime, review, content, and policies;
see [the reference index](references/README.md) for ownership. Reading paths in references are
relative to the containing document; explicit `references/...` paths start at the skill root.

## Progressive xdoc Capability Discovery

After creating each run, run `<skill-root>/scripts/cli/runtime/probe.mjs` once and save the result as
`xdoc-capabilities.json`. The standard refurbish runner does this inside its own run directory; do not
manually initialize a full run first. An explicit `--run-dir` must be new, empty, or contain only
`xdoc-capabilities.json`. Route from runtime schema and dry-run evidence, never version numbers.
Operation/catalog indexes are not allowlists; missing means `undisclosed`. For semantic routing, read
the exact `capabilities.capabilityTruth.entries[]` feature/subset: `supported` may use its operations,
`partial` requires verification, `preserve-only` stays untouched, and `unsupported` follows its alternative; operation presence never upgrades feature status.
For `partial` entries, follow the declared limits and `recommendation.operations` / `target`, even
when `operations` is empty. Match the exact subset: a model scene's unsupported authoring contract
does not prohibit separately disclosed host-geometry edits.
When an entry has non-null `axes`, route `create` / `edit` / `inspect` / `preserve` / `render` /
`verify` independently. The entry-level status does not upgrade a weaker axis, and static PDF/PNG or
Viewer fallback evidence never upgrades `verify` to PowerPoint playback support.
If a caller-provided run directory is rejected, the guard reports the allowed initial entries, every
detected entry, and a safe recovery hint; preserve that directory as evidence and retry with a new one.

For operation lookup, schema projections, or CLI output flags, read
`references/runtime/schema-discovery.md#focused-lookup-and-output-flags` first. Prefer exact capability truth
and the saved op index; projected schemas discover fields but do not prove patch validity.
For direct CLI calls, use explicit commands and action-local options; follow that reference's
CLI invocation guidance for literal paths, typed arguments, and parser failures.
Derive selectors from inspect, the target op schema, then dry-run suggestions.
Choose one selector lookup method; do not combine `id`, `name`, or `query` with another method.
Combine AND predicates inside one query or its supported inline form, and pair `idx` with `placeholder`.

Block only when the caller explicitly
requires a strict gate and a task-critical capability is still undisclosed; otherwise keep exploring or
use an existing fallback, and never disable new xdoc capabilities only because the snapshot is minimal.

For Agent transport routing, read the exact contracts under `capabilities.agentTransports`, including
`mcp.contract`; command presence alone is insufficient and unknown contracts fail closed. MCP replaces
only disclosed adapter calls, never workflow gates. Read `references/runtime/daemon-sessions.md` for details.
For auth diagnostics or report validation, use the action-specific schema and report reference in
`references/runtime/schema-discovery.md`; the compact capability snapshot is not a complete command contract.
For license installation, renewal, unhealthy credentials, or an authorization refusal, read
`references/runtime/licensing.md`. Keep authorization-only tasks on that route without deck preparation
or deck delivery gates; ordinary successful PPTX tasks need no extra auth-maintenance step.
Use `xdoc schema --command <command.action>` or `--report <schemaVersion>` for focused contracts.
Standard runners freeze the display date in `render-context.json`; preserve it when resuming and
verify the effective `renderContext` in rendering evidence. Manual render sequences must use the
same `--field-date`. Semantic summaries should persist full evidence with `diff --output`, then
read and verify that file when detail is needed; see `references/review/export-and-check.md`.

### Run Reuse and Isolation

`.pptx-nova/<run>/` may be read as historical evidence, but it must not automatically become the
execution context for the current task. Create a new current context for new tasks, old-feedback audits,
tool capability investigations, post-upgrade rechecks, or when the user challenges an old result. Use
old runs read-only to explain what happened at that time.

Reuse an old run for execution only when the user explicitly asks to continue the same task and the
source, output target, and task objective have not changed. Even when reusing a run, probe the current
`xdoc` again first. Old `xdoc-capabilities.json` files only describe what was disclosed at that time and
are not facts about current capabilities. During development, upgrades, or old-run recovery, any
judgment about "missing capabilities" must be checked against the current runtime/schema/help first.

## Artifact Retention and Cleanup Strategy

`.pptx-nova/<slug>-<timestamp>/` is auditable evidence, not an ordinary cache. Keep the current run's
capability snapshot, render context, planning/contract inputs, patch and sidecars, machine-gate reports
(including retained full diff evidence), final
candidate, comparison/contact overview, visual review, and issue-page evidence. Do not invent missing
artifacts. The workflow-specific exact retention set is defined in `references/common-workflow.md`.

Only a successful current run may be slimmed, and only by removing rebuildable heavy previews, caches,
logs, failed intermediate candidates, or unreferenced scratch files. Failed, interrupted, unvalidated,
or resumable runs stay intact. Never delete user inputs/finals, reference resources, another run,
anything outside the workspace, or the whole `.pptx-nova` directory. Cross-run cleanup needs an
explicit request and a reviewed candidate list. `--cleanup` still retains the minimal evidence package
and writes `cleanup-manifest.json`; `--keep-all` preserves everything. State cleanup status in the final
summary.

## Quick Paths

Use these only to choose the entry reference; the routing table owns details.

- **Runtime license / activation / renewal / authorization failure**: `references/runtime/licensing.md`;
  install for the actual execution user/environment, inspect admission, then verify the intended task.
- **Create**: `references/create/create-runner.md` and `references/create/design-quality.md`; the design floor applies even to a one-sentence Express brief. Formal/high-risk work also follows the Studio/design-lock references.
  The runner prepares canonical candidate evidence first; after actual PNG review, use its
  `--finalize --visual-review` phase to publish the same hash-bound candidate without rendering again.
- **Edit or micro-edit**: inspect/select, normalize the Edit Contract, dry-run, apply in the run,
  collect scoped evidence, run the contract gate, then review changed slides. Source-guarded
  `set-run` / `replace-paragraph-text` edits require top-level operations and input-bound numeric
  shape IDs. Read `references/edit/inspect-and-edit.md` for paragraph guards and `textLayout`: ordinary edits
  respect autofit; geometry-preserving edits require the disclosed policy and final fit checks.
- **Connectors / groups / OLE / embedded models**: read `references/edit/native-shape-editing.md` before geometry
  edits or duplication. Use native connection sites, retain owner-specific resources and reject
  unrepresentable transforms. Discover `model-3d/host-geometry-editing` for bounded existing-host
  edits through `set-shape`; retain the scene and cached raster. A `preset-adjustments` finding uses an explicitly reviewed,
  document-bound repair from `references/runtime/troubleshooting.md`; it is not an automatic retry or an XSD failure.
- **Animation**: inspect timing capabilities first; edit only the declared safe subset and preserve
  complex or unsupported timing. Read logical `kind`, all `targets[]`, and `timingSummary.mergeSafe`;
  effect counts and raw behavior metadata do not authorize edits. `references/content/animations.md` covers fixed
  whole-shape Box/Dissolve and their distinct preview limits. For basic effects, follow the disclosed
  repeat/autoReverse/restart/easing contract and its omitted/null/value update semantics.
  For imported group/pattern effects and Web slideshow controls, follow `references/content/animations.md` and its
  conditional playback reference. Shape deletion must preserve surviving timing conditions or reject.
  For P14 transitions, follow `references/content/animations.md`'s per-kind schema and independent capability axes;
  inspect source/fallback timing separately and never equate authoring with playback certification.
  For Morph, use exact `!!` object names, run `morph-check`, and bind delivery evidence to the
  bundled PowerPoint playback probe when that probe is available.
- **Refurbish / translate**: use `references/edit/refurbish-runner.md` / `references/translation/translation-runner.md`. The runner owns route,
  evidence, one canonical comparison, and publication; read only references it names on failure.
- **Chinese / East Asian font normalization**: read `references/edit/font-normalization.md`.
  Discover `text/font-family-normalization`; use Chinese selection when Japanese/Korean must stay intact.
  The document-wide `set-font` op has no shape selector. Use its dedicated Edit Contract target,
  review inferred/ambiguous analysis, and verify all slides; saved geometry does not prove visual fit.
- **Template / cross-deck copy**: edit inherited objects or use one transactional `slide-copy`; keep the
  native `pptx-slide-copy/v1` report as evidence, require a read-only `ready` preflight with current
  target/donor file SHA-256 values, normalized package fingerprints, explicit `template` / `slideSize`
  strategy, auditable `templates[]` outcomes, and no blockers. Default to `register-source`; choose
  `rebind-target` only when target inheritance is intentional. Before apply, run
  `cli/edit/copy-size-gate.mjs` as an independent SHA-bound defense; `require-match` never authorizes
  different slide sizes, and the workflow must not invent `opResults` or silently fit donor geometry.
  Verify independent notes/chart/workbook/classic palette ownership and copied navigation as
  described in `references/edit/template-following.md`; equal previews do not prove editing isolation.
- **Export / diff / preview / check**: use `references/review/export-and-check.md`. Run semantic diff once on a stable
  candidate; only reliable changes are machine facts. Preview is for inspection, while the canonical
  visual-evidence decision remains the delivery authority. Discover each action's DPI bounds/default;
  after upgrades or calendar changes, use fresh rendering evidence as described in `references/review/fidelity-diagnosis.md`.
  For input quota or authorization failures, follow `references/runtime/troubleshooting.md#conversion-input-quotas-and-authorization-failures`;
  use the local CLI contract, keeping SDK product limits and proposed APIs separate.
- **ChartEx or structural risk**: bind the specialized audit and PowerPoint-native evidence when
  required; an unavailable optional evidence route is disclosed risk, not invented proof.
- **Chart numeric precision**: follow `references/content/charts.md`'s numeric checks for long labels, extreme
  histogram ranges, signed percentage stacks and automatic axes/category fitting. Verify source
  values separately from painted or extracted labels; retain explicit bounds and real tail intervals.
  For doughnuts, follow its label-position restrictions and explicit hole-size default.
- **Chart rendering changes**: use `references/content/charts.md` for automatic 2D/3D fitting,
  surface camera/paint, imported stacked ribbons, crossing-plane occlusion, signed-area end caps,
  hidden-axis semantics and gradient cuts. Keep Web texture evidence separate from native PDF evidence.
  For Latin word breaks, distributed paragraphs, table spacing or picture/arrow differences,
  use `references/review/fidelity-diagnosis.md`; parser model fields are not patch fields.
- **Existing Shape 3D / Text 3D**: read the local-declaration guidance in `references/edit/inspect-and-edit.md`.
  Preserve owner-bound XML facts during neighboring edits; render improvements do not grant
  authoring support or PowerPoint fidelity. Query the independent render axis for bounded parallel
  cameras, extrusion/bevels and Text3D; Chart 3D and embedded models have separate contracts.

## Skill Root

Treat the directory that contains this `SKILL.md` as `<skill-root>`. The published skill must be
self-contained: scripts required by user workflows live in `<skill-root>/scripts/`, assets in
`<skill-root>/assets/`, documentation in `<skill-root>/references/`, and benchmarks in
`<skill-root>/benchmarks/`.

When wrapping xdoc or preparing asset inputs, follow `references/common-workflow.md`'s filesystem-path rules.
Resolve POSIX symlink/parent traversal before lexical normalization; keep relative assets rooted
at the submitted patch/manifest directory, including when the file itself is a symlink.

Do not depend on repository-root `tools/`, `Justfile`, or files outside this skill directory in skill
user paths. Repository-root tools are only for maintainers of this repository.

## Directly Supported Input Formats

When creating or modifying PPTX files, this skill can directly consume these inputs:

- Natural-language briefs, chat content, organized outline text, or Markdown outlines.
- HTML files, web URLs, PDFs: source material, not a one-step conversion from web page or PDF to finished deck. Normalize them to Markdown/text with `xdoc html2md` (HTML/URL) or `xdoc pdf extract-text` (PDF); the result is equivalent to a user-provided brief and must still go through outline -> content -> DeckKit -> validation. PDF text fidelity depends on the source file; scanned documents or embedded-font anomalies may cause missing characters or incorrect order. Any facts completed from that material must be written to `deck_lock.assumptions[]`. Store the raw ingestion result in the run directory, such as `source_brief.md` / `source_extract.txt`; see Source Ingestion in `references/common-workflow.md` for details.
- `.pptx`: reference decks, template decks, `slide-copy` sources, `template-fill` templates, or inputs to modify.
- pptx-nova / xdoc workflow JSON: `outline.json`, `deck_lock.json`, `content.json`, `edit-contract.json`, `patch.json`, `assets_manifest.json`, brand/template profiles, and similar files. These are proprietary structured inputs generated by this skill or xdoc, or explicitly provided by the user and compliant with the matching schema; do not treat arbitrary `.json` files as directly usable PPTX content/patch inputs.
- Data-binding JSON: `data.json` may be used as business data for `template-fill` / `bind-data`; `bindings.json` must comply with xdoc's binding structure and declare text/table/chart binding relationships.
- CSV or JSON tabular data: use for table/chart/content data filling, as data for `set-table-data` or `bind-data`, or normalize into DeckKit `content.json`.
- Resource files: images, logos, screenshots, SVG formula assets, and similar files. Register them in `assets_manifest.json` and reference them by asset id or `assetSource.path`.

## Task Routing

Determine the task type first, then read the corresponding files:

For a rendering discrepancy or a preview regression after upgrading xdoc, also read
`references/review/fidelity-diagnosis.md` before changing authored content or layout. This includes
columns/Unicode breaks, tabs/autofit anchors, font/language/placeholder inheritance, merged borders,
chart domains/direction, resized cached SmartArt, Web text clipping, missing/stale reflections, and Shape 3D scale offsets;
identify the actual renderer and its fallback before treating the symptom as a deck defect.

| User intent                                                                              | Required references                                                                                                                                                                                 | Read conditionally                                                                                                                                                        |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Install/renew a Runtime license, activate xdoc, or diagnose authorization failures       | `references/runtime/licensing.md`                                                                                                                                                                   | `references/runtime/schema-discovery.md` for exact action/report contracts; `references/runtime/daemon-sessions.md` when the execution environment differs                |
| Simple prompt / wants speed / default new deck generation                                | `references/create/create-runner.md`                                                                                                                                                                | Follow its preparation routes to `references/create/create-express.md`, `references/create/deckkit-mode.md`, or `references/create/narrative-quality.md` only when needed |
| Investor / client / board / Studio / needs precise control                               | `references/common-workflow.md`, `references/create/deckkit-mode.md`, `references/create/create-studio.md`, `references/create/design-lock-and-assets.md`, `references/create/narrative-quality.md` | `references/review/visual-qa-and-asset-slots.md`, `references/create/rich-deck-patterns.md`                                                                               |
| Strictly follow an existing PPTX template / adapt content to a template                  | `references/common-workflow.md`, `references/edit/template-following.md`, `references/edit/edit-mode.md`                                                                                            | `references/create/design-lock-and-assets.md`, `references/edit/inspect-and-edit.md`                                                                                      |
| Reference PPTX + new outline to generate a new deck                                      | `references/common-workflow.md`, `references/create/reference-create.md`, `references/create/deckkit-mode.md`                                                                                       | `references/create/template-library.md`                                                                                                                                   |
| Polish / refurbish an existing PPTX while preserving original content and changing style | `references/edit/refurbish-runner.md`                                                                                                                                                               | Only the references named by `refurbish-plan.json.requiredReferences[]` after route selection                                                                             |
| Small text/notes/footer/metadata edit                                                    | `references/common-workflow.md`, `references/edit/edit-contract.md`, `references/edit/micro-edit-cheatsheet.md`                                                                                     | If selectors are ambiguous or complex image/multi-object edits are involved, then read `references/edit/edit-mode.md`, `references/edit/inspect-and-edit.md`              |
| Continue the same deck with an explicit future/carryover rule                            | `references/common-workflow.md`, `references/edit/session-rules.md`, `references/edit/edit-contract.md`                                                                                             | `references/edit/edit-mode.md`, `references/edit/inspect-and-edit.md`                                                                                                     |
| Translate an existing `.pptx` while preserving original layout                           | `references/translation/translation-runner.md`                                                                                                                                                      | Follow its preparation/failure routes into `references/translation/translation-mode.md`; load charts/tables only when detected                                            |
| Modify an existing `.pptx`                                                               | `references/common-workflow.md`, `references/edit/edit-contract.md`, `references/edit/edit-mode.md`, `references/edit/inspect-and-edit.md`                                                          | `references/edit/patch-ops-cheatsheet.md`                                                                                                                                 |
| Edit connector/group/OLE/model geometry or duplicate native objects                      | Existing-deck edit references plus `references/edit/native-shape-editing.md`                                                                                                                        | `references/runtime/troubleshooting.md` for guarded preset repairs                                                                                                        |
| Add/modify/delete animations or transitions                                              | `references/common-workflow.md`, `references/edit/edit-mode.md`, `references/content/animations.md`, `references/edit/inspect-and-edit.md`                                                          | `references/edit/patch-ops-cheatsheet.md`; for complex timing, read `references/edit/control-flow-and-raw-xml.md` only for risk judgment                                  |
| Data + template / JSON filling                                                           | `references/common-workflow.md`, `references/content/data-driven.md`                                                                                                                                | `references/content/tables.md`, `references/content/charts.md`                                                                                                            |
| Brand conversion / brand check                                                           | `references/common-workflow.md`, `references/content/styles-and-themes.md`                                                                                                                          | `references/create/template-library.md`                                                                                                                                   |
| Unify Chinese / East Asian font families across an existing deck                         | `references/common-workflow.md`, `references/edit/font-normalization.md`, `references/edit/edit-contract.md`                                                                                        | `references/content/styles-and-themes.md` for local font or theme-only changes                                                                                            |
| Only export PDF/PNG/MD/JSON, extract, check, or compare two PPTX files                   | `references/common-workflow.md`, `references/review/export-and-check.md`                                                                                                                            | No need to read creation/edit docs unless the user then asks for fixes                                                                                                    |
| Long-task split / resume generation                                                      | `references/common-workflow.md`, `references/runtime/resume-split-mode.md`                                                                                                                          | References for the original task type                                                                                                                                     |
| Formulas, charts, tables, raw XML                                                        | Current task references plus the matching `references/content/formulas.md` / `references/content/charts.md` / `references/content/tables.md` / `references/edit/control-flow-and-raw-xml.md`        | `references/runtime/troubleshooting.md`                                                                                                                                   |

When the user provides an HTML file, web URL, or PDF as material, first normalize it to Markdown/text
with xdoc according to Source Ingestion in `references/common-workflow.md`, then route by the real task
type (create / data / edit) in the table above; ingestion itself does not change the target task type.
If the user only wants HTML/URL/PDF converted to Markdown/text without a deck, follow
`references/review/export-and-check.md`.

## Mode Detection

- **Express / Studio**: Speed and a short brief select Express; formal, brand-sensitive, asset-heavy,
  long, or confirmation-sensitive work selects Studio and locks outline/design first.
- **Template / Reference Create**: Template following edits copied/inherited objects; Reference Create
  treats the reference as read-only style/layout evidence for new content.
- **Refurbish**: Preserve the source as read-only content truth, apply the selected DeckKit visibly to
  editable objects, and never rasterize, downgrade content, or silently switch DeckKits.
- **Edit / Micro Edit / Animation**: Inspect before patching. Micro edits use the short contract path;
  animation changes stay inside the capability-declared safe subset.
  Use reported part identities and current inspect order for slide/layout/master selectors;
  filename suffixes and ZIP order are not selector indices. See `references/edit/inspect-and-edit.md`.
- **Translation**: Copy, replace visible text in place, and preserve styling/layout semantics. Repair by
  compressing text, then minimally reducing font, then geometry only with proven whitespace. Changed
  multi-column text requires its bound human-review gate; real overflow/overlap/edge findings and
  rendered chart-title/page-bound collisions never receive a review override. The translation runner
  owns coverage, style/vision audits, comparison parts, and SHA-256 publication binding.
- **Data-driven / Export-Check**: Data plus template selects `references/content/data-driven.md`; conversion, preview,
  extraction, or checking alone must not mutate the PPTX.

## Feedback Mode

If the user prompt contains explicit feedback intent such as `need feedback`, English feedback phrases, or equivalent Chinese phrases meaning "give feedback", "needs feedback", or "any usage feedback", read `references/review/feedback-mode.md`. Once Feedback Mode is triggered, first write `skill-feedback.md` in the current run directory. Create, Refurbish, and Translation feedback must include the workflow's exact seven-dimension 0-10 process scorecard and a correctly weighted overall score, printed in the final response as required by Completion Summary. Before the final response, run the feedback gate with `--workflow create|refurbish|translation|other`: if the original prompt is available, use
`node <skill-root>/scripts/cli/review/feedback-gate.mjs --run-dir <run-dir> --prompt-file <prompt.txt> --workflow <workflow> --strict --overwrite --json > <run-dir>/feedback-gate.json`; if the prompt was not saved but the user feedback request is known, use `--require-feedback`. If the gate fails, add real feedback or correct the scorecard before sending the final response.

During xdoc PPTX creation or editing in Feedback Mode, investigate newly observed, unexpected rendering problems as possible product bugs. Compare with an existing PowerPoint-native screenshot when available; otherwise, if the optional prerequisites are available, try `<skill-root>/scripts/cli/office/powerpoint-snapshot.nu` on the affected slides and compare. Record the evidence and every confirmed new problem in `skill-feedback.md`, and report all of them in the final task summary even when there are more than three feedback items. If native verification is unavailable or inconclusive, label the observation unverified rather than claiming a confirmed product bug. Follow `references/review/feedback-mode.md` for the evidence and reporting details.

## Common Creation Hard Rules

These rules apply to all new decks, including Express and Studio:

- Read `references/create/design-quality.md` before selecting a DeckKit. Infer audience/mode,
  commit to a content-led visual idea, and inspect actual eligible-kit examples; a readiness score
  or absence of overflow is not evidence of aesthetic fit. Respect the user's pinned visual world.
- Review the rendered design as well as its mechanics. Write candidate/manifest-bound
  `design_review.json` with slide-specific observations and a weakest-page assessment; pass it as
  `--design-review` when recording the Create visual review. Repair unresolved craft failures before
  publication. The validator checks the judgment record, not beauty; never invent observations.
- Generate or normalize `outline.json` first, then write `deck_lock.json`; do not jump directly from prompt to patch.
- Default to DeckKit-first: `content.json -> DeckKit -> patch -> xdoc -> PPTX -> validation`.
- Persuasive decks for formal reports, clients, investors, boards, roadshows, strategy, product-platform, and similar contexts must read `references/create/narrative-quality.md`, lock `deckProfile`, and per-slide `claimTitle` / `proofObject` / `rhythm` / `layoutIntent` / `visualDensity` in `deck_lock.json`, then write `narrative_quality_review.json` after PNG review.
- Before writing `content.json` or a manual patch, compare each slide against `deck_lock.slides[]` and confirm page type, rhythm, structural intent, density, and proof object have not drifted from memory. If mismatched, fix the lock or content source first instead of patching around it.
- Non-appendix slides should have a clear point of view or direction. Main titles/subtitles should be short, scannable, and fitted to DeckKit slots. Avoid pure topic labels such as `Product Overview`, `Market Analysis`, or `Roadmap`. Put the full conclusion in `claimTitle`; when needed, move it into the subtitle, callout, or `proofObject`. Do not sacrifice layout merely to make the displayed title conclusion-like.
- Main titles and subtitles do not use terminal periods by default. Use question marks/exclamation marks only when the tone or interactive intent is explicit.
- If the user-provided outline explicitly specifies the main title or subtitle, that wording takes priority. Do not silently rewrite it to be more conclusion-like, shorter, or period-free. Record the source in `titleSource: "user"` / `subtitleSource: "user"`, and adjust only for hard layout overflow or when the user asks for polishing; explain the tradeoff.
- Automatic selection for delivery may use only DeckKits with `readiness in ["production", "default"]`.
- When a production/default DeckKit is available, do not use `deck-generator-template.mjs` as the default delivery path.
- If no usable DeckKit exists, a page type is missing, or component structure must change, create/extend the DeckKit before delivery.
- When referencing templates, brands, or layouts, write `deck_lock.templateFusion` in semantic layers: `brand` / `layout` / `deck`. Do not guess conflicts and overrides temporarily inside the generator.
- If the source outline contains only titles or blanks, factual content completed by AI must be written to `deck_lock.assumptions[]`; do not disguise unverified competitors, metrics, cases, or market facts as user-provided content.
- If the final creation output path already existed before the task began, ask the user to rename, delete, or choose a different path first. Do not overwrite the final path with `--overwrite`.
- For creation tasks, `vision-check` `summary.bySeverity.high` and `summary.bySeverity.medium` must both be 0, and the full-package semantic evidence must be internally consistent with `semanticSummary.passed=true`, `semanticSummary.issueCount=0`, at least 82 source rules / 81 normalized rules, and `semanticIssues=[]`. Dry-run and apply must each disclose `semanticIssues=[]`; a missing semantic field is not proof of safety.
- PNG/contact sheet visual review cannot be skipped. It catches real line breaks, character overlap, contrast, decorative occlusion, page-number rhythm, and composition issues that dry-run and `vision-check` cannot see.

## Common Edit Hard Rules

These rules apply to modifying existing PPTX files:

- Treat the input deck as read-only by default. Inspect first, then dry-run, then write intermediate files in the run directory.
- Keep sidecars distinct from the primary PPTX and every input. On an output failure, inspect publication facts before recovery: `primaryOutputPublished:true` means the PPTX already reached disk even though the command failed. Preserve both paths and the report; never automatically replay or add `--overwrite`. See `references/common-workflow.md` and `references/runtime/troubleshooting.md` for sidecar recovery, including creation tasks.
- Do not edit objects by guessing selectors. When the target object is unclear, first narrow candidates with `xdoc pptx select input.pptx --query '{"textRegex":"..."}' --json` or a query file, then write the patch. Check dry-run `resolvedSelectors[]`; for an ambiguous selector, inspect `suggestions[].remediation` and follow `references/runtime/troubleshooting.md`. Capture the first submission before an automatic retry, validate the complete kind/target shape against retained request/input/asset snapshots, and revalidate and authorize. A replacement request runs once from the original input; document remediation applies only its repair patch to the exact diagnosed bytes. Missing context or `remediationUnavailable` never permits a guessed replay.
- After inspect/select resolves the targets, normalize `edit-contract.json` before patch/apply. Bind each target to its patch `opIndexes[]`, expected categories/values, allowed changes, preserve policy, and required evidence. After the stable candidate is produced, require `edit-contract-gate.json.agentGate.passed=true` before publication. Translation and Refurbish keep their stronger specialized contracts instead of replacing them with this generic gate.
- Only create `session-rules.json` from an explicit current-deck future/carryover instruction. Resolve it from a structured `session-operation.json`; never execute free-form `appliesWhen` text. Pass a successful `session-rules-resolution.json` to the Edit Contract normalizer so rule-owned targets and preserve requirements are hash-bound and verified by the final contract gate. If no active rule applies, continue without extra evidence or user confirmation. Advance the rules to a new revision only after the candidate passes and is accepted.
- After post-apply evidence is stable, generate `evidence-manifest.json` to bind the candidate SHA-256 and exact evidence-file hashes. The gate must reject a missing/stale manifest, including when the candidate is overwritten at the same path.
- Visible text-only edits that must preserve existing formatting require `style-diff` evidence. Whole-frame `set-text-frame` may erase run styling even when dry-run, semantic diff, and vision-check appear clean; use an inspect-proven run/text-node preserving edit or treat `target-text-style-changed` as a blocker.
- Visible edits require changed-scope `vision-diff` by default. Block new or worsened high/medium issues. Dry-run/apply `semanticIssues[]` are a full-package before/after issue delta and must contain no regression introduced by the edit; the edit-contract gate fails closed when that evidence is missing or non-empty. Candidate-only `vision-check.semanticIssues[]` scans the full package—even with `--slides`—so treat it as diagnostic evidence and disclose inherited legacy-deck semantic debt instead of turning it into a false edit blocker.
- When the user requests accessibility, inclusive-design, screen-reader, or alt-text validation, run `xdoc check` with `a11y` named explicitly (or `--checks all`, which includes it); the default `--checks` list does not. Gate on `checks.a11y.status` and `summary.riskLevel`, not exit code. A violation blocks the requested accessibility claim; `inconclusive` requires rendered/manual review and remains unproven. Never apply an a11y `patchTemplate` unchanged: it is a manual placeholder and has no executable remediation target.
- For strict template following, edit copied/inherited objects or template placeholders. Do not use new text boxes, translucent rectangles, or whole-page image overlays to hide old content and manufacture a page that "looks right".
- When copying source slides or filling templates, explicitly fill or delete empty structural placeholders such as title/body/dt/sldNum/ftr. Do not leave empty placeholders in PowerPoint edit state just because they are invisible in PNG output. If an actionable finding is intentionally required by the deck's semantics, preserve it only through a source-hash-bound `pptx-nova-review-policy/v1` rule using the exact `reviewIdentity.sha256` from `layout-final.json`; never use a global boolean exception.
- Native `pptx-slide-copy/v1` must disclose `preflight.strategy.slideSize: "require-match"`; mismatched donor/target dimensions are a core blocker, not a renderer concern. Retain the bundled copy-size gate as independent file-bound evidence, and stop if either native preflight or the gate reports a mismatch. Do not scale implicitly or move this policy into Viewer/PDF rendering.
- Identity assets such as logos, client marks, product screenshots, headshots, app icons, and third-party brand graphics must come from user-provided files, source-deck assets whose reuse is allowed, official verifiable sources, or registered authorized sources. When this cannot be confirmed, use text/native shapes instead of generating pseudo-official assets.
- When using external, reused, generated, or formula assets, `assets_manifest.json` must record `status`, `source.kind`, `licenseRisk`, and PPTX usage slots. `missing` / `needs-user` / `forbidden` blocks delivery.
- If the user asks for in-place modification, still complete validation in the run directory first, then write back only according to the user's explicit intent.
- Preserve SmartArt, macros, complex animations, and unsupported objects by default. Edit animations only inside `inspect.animations[].editable` or the creation-safe subset explicitly supported by the current schema. Explain the boundary when they cannot be edited.
- **PowerPoint Repair blocks delivery**: Any candidate PPTX that shows "PowerPoint found a problem with content", a `Repair` button, automatic repair after opening, or an equivalent corruption warning is a failed candidate. Do not deliver it, and do not treat the PowerPoint-repaired file as a final artifact without root cause. Retain the triggering candidate PPTX, patch, dry-run/apply reports, and minimal reproduction evidence. Locate the specific op / OOXML part / structural order issue before generating a new candidate.
- For high-risk edits involving charts, tables, raw OOXML, relationship packages, embedded workbooks, themes/styles, and similar structures, `xdoc check`, `vision-check`, and PNG preview alone do not prove structural safety. Also perform OPC/OOXML structural validation, such as `unzip -t`, XML well-formedness checks, and targeted semantic audits for chart axis/legend/data-label/gridline child element order, relationship targets, embedded workbook synchronization, and similar risks. If an op generates a PowerPoint Repair file for a certain input class, make that op fail at the xdoc/pptx-gen source instead of generating problematic content.

## Visual and Readability Hard Rules

For client-facing, investor-facing, or formal-report decks, all visible text such as body copy, card descriptions, badges, labels, legends, and table cells must be readable:

- Core body text is usually at least `10.5pt`.
- Label / badge / chart/table text is usually at least `9pt`.
- In newly created or explicitly recolored charts, avoid large black or near-black filled regions; black text and lines are allowed. Prefer suitable grays or theme colors, and review 3D sidewalls as well as front faces. Follow `references/content/charts.md` for palette and contrast checks; this does not authorize recoloring preserved source charts.
- Footers/sources may be `8.5-9pt`, but must not carry critical information.
- DeckKit-first creation uses the catalog `qualityProfile` and that DeckKit's golden baseline as machine gates. Do not damage validated DeckKit layout constants just to satisfy generic font-size hard rules.
- Short labels such as percentages, number+unit, amounts, quarters, years, `ROI`, and `KPI` must not be split.
- Circular or square numbers must be centered horizontally and vertically.
- When text does not fit, shorten it, change the layout, increase container height, or split the page. Do not keep shrinking the font to cram it in.
- Derive connector lines, arrows, central axes, VS marks, and numbered circles from target shape bounding boxes, not by eye.
- Dry-run `text-overflow-estimate` and `vision-check` reuse the same static text overflow estimator. When you see a medium issue, fix height, shorten text, split pages, or adjust autofit before writing the file.
- Expected single-line text such as `subtitle`, `eyebrow`, `kicker`, `badge`, and `label` must not have a stranded trailing word. Handle `vision-check` `text-unexpected-wrap` by shortening copy, widening the container, or changing layout.
- Main titles and subtitles should not break layout in order to express complete sentences. Remove terminal periods by default and move overlong content to subtitle, callout, body, or notes.
- When converting PPTX to PNG/PDF or checking generated PPTX, tool watermarks such as `structurify.io` may appear. These watermarks usually appear only in the top-right corner of a slide, may be ignored during human visual review, and should not be treated as DeckKit composition, occlusion, or content defects.
- Bundled `.nu` PowerPoint helpers are optional, capability-gated evidence integrations, never baseline dependencies. Missing prerequisites remain explicitly unverified and do not block the baseline unless PowerPoint-native proof was explicitly required; never claim missing evidence. Read the routed animation/chart reference for exact use.

PNG/contact-sheet review should be done with a problem-finding mindset, not as a confirmation ritual.
Machine gates cannot see every pixel-level defect. In particular, check:

- For refurbished decks, ask a more direct question first: if the filename is hidden, is this output clearly a redesigned version? If it only adds lines, page numbers, light backgrounds, or local accents to the original, do not deliver it as "refurbished/polished".
- Whether wrapped titles collide with decoration, separators, headers, or logos.
- Whether body text, sources, footnotes, legends, and table cells are truncated, overlapping, or hugging edges.
- Whether adjacent cards, columns, icon circles, numbered circles, arrows, and connectors are aligned, and whether spacing varies wildly.
- Whether text, icons, borders, and gridlines have enough contrast on light/dark backgrounds.
- Whether template pages retain placeholders, old footers, old dates, old page numbers, empty image frames, or invisible-but-editable empty objects.
- Whether multi-page contact sheets show repetitive layout rhythm, meaningless decorative containers, topic-only titles, or awkward blank space.
- Whether chart/table pages pass specialized semantic checks: data dimensions, series/categories, legend/labels, table rows/columns, and binding sources must match the content before checking the PNG for occlusion.
- For deliverable PPTX files, especially formal/enterprise or high-risk chart/table/OOXML changes, run the clean-open smoke gate when macOS + PowerPoint are available. Follow `references/review/export-and-check.md` for the command, prerequisites, delayed Repair-dialog checks, and skipped-evidence disclosure.

## Required Validation

When creating or visually significant modifying a deck, close in this order:

```text
check-lock -> dry-run semanticIssues=0 -> apply semanticIssues=0 -> vision-check visual high/medium=0 + semanticSummary.passed=true for create -> structure-check when needed -> high-risk evidence finalizer when required -> PNG/contact-sheet design review -> design_review.json + visual_review.json -> clean-open gate when available/high-risk -> narrative quality review when required -> optional xdoc check
```

Generic Edit/Micro Edit must additionally close its own contract:

```text
optional session-rules resolve -> edit-contract -> dry-run target coverage -> apply -> one final semantic diff -> declared scoped/style/structure evidence including vision-diff when visible -> edit-contract gate (including applicable session rules) -> PNG review when visible -> publish
```

Refurbish Existing Deck must also append:

```text
refurbish-skin report gate -> source/candidate layout snapshots -> one final pptx semantic diff when source/candidate are stable -> one review-policy evaluation -> non-governing Finding Analysis shadow -> fidelity gate -> one full refurbish-compare render plus lower-layout-DPI Agent review assembly from the same page cache -> refurbish-compare delivery gate -> optional contact-diff aliases from that same compare evidence -> optional legacy supplemental audit
```

Animation, structural, or compatibility high-risk tasks must also append:

```text
OPC zip check -> XML well-formed check -> targeted OOXML semantic audit -> target-Office compatibility gate -> PowerPoint clean-open smoke gate when available
```

Morph authoring requires the exact adjacent-pair `morph-check`. The `.nu` playback probe is optional;
without it the baseline continues but PowerPoint playback stays unverified. An explicit native-proof
requirement blocks that proof gate. Static PNG/PDF or viewer fallback does not prove interpolation.

When the user, template, publishing channel, or deployment policy names a target Office release, run
`xdoc check <candidate> --checks compat --target-office <release> -o <run-dir>/office-compat.json --overwrite`.
The candidate is compatible only when `checks.compat.details.agentGate.passed=true`; a top-level
`warning`, `mc:Ignorable`, an `extLst/ext` extension container, or `AlternateContent` fallback does not prove full-fidelity compatibility.
Read `minimumOfficeVersion`, `unprotectedIssueCount`, `gracefulDegradationIssueCount`, stable `ruleId`,
and `sampleParts` to decide whether to remove the feature, add a fallback, or explicitly change the
target policy. Retain `office-compat.json` as delivery evidence. If no target is specified, do not
invent an older corporate baseline; the xdoc default is Microsoft 365 and still reports the deck's
derived `minimumOfficeVersion`.

If any gate finds PowerPoint Repair, incorrect OOXML child element order, missing relationship targets,
embedded workbook/chart cache mismatch, damaged animation timing tree, or an op that generates
corrupted content for an input combination, stop delivery. First fix the xdoc/pptx-gen source and add a
regression test covering the scenario that previously generated a bad file, asserting that, after the
fix, it either generates a structurally valid file or returns a clear op-level error.

When only exporting or checking files, follow `references/review/export-and-check.md`.

## Common Command Entry Points

Read the routed reference first and use its canonical runner or command sequence. Creation,
refurbishment, and translation entry commands live in `references/create/create-runner.md`, `references/edit/refurbish-runner.md`, and
`references/translation/translation-runner.md`; inspect/apply, export/check, specialized content, visual review, and feedback
commands live in their matching references. Do not preload a command encyclopedia or reconstruct a
runner from individual commands when a standard runner owns the workflow.

## Completion Summary

For authorization-only tasks, report what was actually installed or diagnosed, the selected path/hash,
credential health/admission, whether an intended real task passed, and any remaining reason/action.
Distinguish installed-and-healthy from task-authorized; when no suitable task input was available, say
task authorization remains unverified. Do not invent deck artifacts or apply the deck summary below.

After successfully generating, modifying, exporting, or checking, compress the final response into 4
blocks and avoid dumping the full checklist on the user:

1. **Output**: Absolute path to final PPTX/export file + run directory. For translation/refurbish tasks, list every published compare sibling and its run-directory source. Use the compatible unnumbered PNG for decks up to 20 slides; otherwise list the complete numbered `*-01.png`, `*-02.png`, ... set and manifest. The delivery bundle must be proven by the corresponding `*-compare-gate.json.status=pass` and `finalBinding.status=bound`.
2. **Validation**: One line listing the key gates actually run and their statuses, for example `dry-run semantic=0; apply semantic=0; vision high=0 medium=0 semantic=pass; preview reviewed; clean-open not run`.
3. **Evidence**: List only the 3-6 most important artifacts, such as `patch.json`, `vision.json`, preview manifest/contact sheet, `pptx-diff.json`, and `evidence-summary.json`; do not list artifacts that do not exist.
4. **Risks/next steps**: Include only items the user still needs to know, such as clean-open not run, fonts not embedded, external links, unsupported objects, manually unreviewed asset licensing, AI factual assumptions, or no remaining risk.

Add conditional material only when relevant: for high-risk tasks, list `evidence-summary.json` /
`layout-final.json`; for chart/table/XML risk, list the specialized audit; for refurbish/strict template
following, list fidelity/template/content audits; for formal persuasive decks, list the narrative-quality
conclusion; when cleanup occurs, state retained evidence and deleted rebuildable artifacts. When
Feedback Mode triggers, save feedback according to `references/review/feedback-mode.md` and list the
`skill-feedback.md` path. Show detailed issues only for 3 or fewer feedback items; beyond 3, list only
the detailed-report path. For Create, Refurbish, and Translation, always print the
validated seven-row execution scorecard and weighted overall score regardless of issue count. Retain
`feedback-gate.json` as well. Do not output xdoc version, CLI
schema, or capability-disclosure audit details unless they affect the result, a fallback was used, or
the user explicitly asks.
In Feedback Mode, the three-item limit does not hide newly confirmed unexpected xdoc rendering
problems: summarize every such problem in the final response, with its affected slide/object and
PowerPoint comparison result, and link the detailed evidence in `skill-feedback.md`.

Only output token information when the platform or tooling provides accurate token statistics; do not
estimate.

## Reference Index

Read the files required by routing first; do not read all references at once.
See [the reference index](references/README.md) for the complete grouped guide descriptions.
