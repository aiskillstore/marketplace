# Workflow references

Use the task routing in [SKILL.md](../SKILL.md) to select what to read. This index describes
ownership; it does not require loading every guide. Paths in reading instructions and Markdown
links are relative to the containing document. Explicit `references/...` paths in runtime
`requiredReferences[]` and command examples are relative to the installed skill root.

The [common workflow](common-workflow.md) owns shared run setup, source ingestion, filesystem
rules, evidence retention, and delivery conventions.

## Create

New-deck preparation, DeckKit selection, narrative and design authoring:

- [Standard create runner](create/create-runner.md) — Standard Create runner contract, compact output, performance, progressive preparation and failure routing
- [Express preparation](create/create-express.md) — Quick deck generation from a simple prompt
- [Design quality](create/design-quality.md) — Audience modes, art direction, rendered kit selection, craft floor and candidate-bound design review for every Create
- [Express golden path](create/express-mode.md) — Full golden path for Express mode
- [Studio preparation](create/create-studio.md) — Confirmation, design lock, and split for high-risk/formal/precision decks
- [DeckKit workflow](create/deckkit-mode.md) — DeckKit selection, readiness, content, user-visible examples
- [Reference-based creation](create/reference-create.md) — Reference PPTX + new outline generation
- [Template and asset catalogs](create/template-library.md) — Brand/layout/deck/chart/icon catalog fusion
- [Design lock and assets](create/design-lock-and-assets.md) — `deck_lock.json`, `assets_manifest.json`, check-lock
- [Narrative quality](create/narrative-quality.md) — Deck profile, claim spine, contact-sheet plan, comeback review
- [Design contracts](create/design-contracts.md)
- [Rich deck patterns](create/rich-deck-patterns.md) — Rich visual patterns when no suitable DeckKit exists
- [DeckKit generator workflow](create/deck-generator-workflow.md) — Creating or extending DeckKits

## Edit

Existing-deck changes, template following, refurbishment and guarded patch operations:

- [Edit workflow](edit/edit-mode.md) — Inspect/dry-run/selector workflow for modifying existing PPTX files
- [Inspection and selectors](edit/inspect-and-edit.md) — Selectors, inspect output, and edit details
- [Edit contract](edit/edit-contract.md) — Existing-deck edit scope, source hash, target coverage, locality/style evidence, and final contract gate
- [Micro-edit quick reference](edit/micro-edit-cheatsheet.md) — Fast path for small text, notes, footer, metadata, and single-object edits
- [Native shape editing](edit/native-shape-editing.md) — Native connector sites, exact group transforms, OLE/model preview geometry, and object-copy ownership
- [Font normalization](edit/font-normalization.md) — Chinese/East Asian selection, document-level Edit Contract, ambiguity review and full-deck font checks
- [Refurbish runner](edit/refurbish-runner.md) — Compact standard refurbish route, Agent output, comparison reuse, failure-driven disclosure, and review boundary
- [Session rules](edit/session-rules.md) — Explicit current-deck future/carryover rules, revision lifecycle, deterministic resolver, and Edit Contract integration
- [Template following and slide copy](edit/template-following.md) — Strict template following: copy source slides, edit inherited objects, placeholder QA
- [Patch operations quick reference](edit/patch-ops-cheatsheet.md) — Patch op quick reference
- [Control flow and raw XML](edit/control-flow-and-raw-xml.md) — `if` / `foreach` / `try` / raw OOXML

## Translation

- [Translation runner](translation/translation-runner.md) — Translation finalizer, stable candidate, compact output, compare reuse, publication binding, and failure routing
- [Translation preparation and detailed gates](translation/translation-mode.md) — PPTX translation, visible text coverage, source/candidate comparison, and layout-consistency gates

## Runtime

- [Runtime licensing](runtime/licensing.md) — License installation/renewal, source and environment diagnosis, admission checks, strict task verification, and bounded recovery
- [Schema discovery](runtime/schema-discovery.md) — Progressive xdoc schema / dry-run --explain capability discovery
- [Daemon, JSON-RPC and MCP sessions](runtime/daemon-sessions.md) — Daemon/stdio JSON-RPC/MCP selection, exact contracts, tuning, and troubleshooting
- [Split and resume](runtime/resume-split-mode.md) — Split handoff and resume generation
- [Troubleshooting and remediation](runtime/troubleshooting.md) — Common errors and automatic repair suggestions

## Review

- [Export, comparison and checks](review/export-and-check.md) — Export, extract, checks, semantic diff, and canonical unified visual evidence
- [Fidelity diagnosis](review/fidelity-diagnosis.md) — Distinguish authored semantics, renderer behavior and environment differences before repairing a deck
- [Visual QA and asset slots](review/visual-qa-and-asset-slots.md) — Image slots, AI image prompt guard, P0/P1 QA
- [Skill feedback](review/feedback-mode.md) — Skill usage feedback, old-run feedback audit, and feedback persistence rules

## Content

Specialized object authoring and rendering guidance, loaded only when the task needs it:

- [Charts](content/charts.md) — Chart creation/editing and OOXML chart semantics
- [Tables](content/tables.md) — Table creation/editing, CSV, formulas
- [Formulas](content/formulas.md) — LaTeX/math formula strategy and formula assets
- [Data-driven filling](content/data-driven.md) — `template-fill` and `bind-data`
- [Styles and themes](content/styles-and-themes.md) — Colors, gradients, fonts, themes, masters
- [Theme packs](content/theme-packs.md) — themePack / stylePack built-ins, `catalog themes`, swap-theme / swap-style / apply-brand commands, generator usage
- [Recipes](content/recipes.md) — Recipe op schema and examples
- [Animations and transitions](content/animations.md) — PPTX animation/transition creation, safe edits, preserve-only boundaries, validation
- [Morph choreography](content/morph-choreography.md)
- [Viewer playback](content/viewer-playback.md)

## Policies

- [Finance research](policies/finance-research.md), only when the requested content needs it.
