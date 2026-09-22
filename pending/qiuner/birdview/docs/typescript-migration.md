# Full TypeScript migration work plan

[中文](typescript-migration.zh.md)

Status: CLI and canonical contracts implemented; remaining stages pending. The user has authorized atomic commits, issues, linked PRs and merging after checks. This document authorizes no additional product behavior or release.

## Goal and scope

Make TypeScript the maintained source language for first-party executable code: Node commands, validation, rendering, browser interactions, repository tools and tests. CSS, HTML, Markdown and JSON/JSONL data remain appropriate formats. Distributed JavaScript is generated output, not a second implementation.

The migration should improve data contracts, state modeling and change safety. It is not a framework rewrite, a performance claim or evidence of better AI coding scores. Preserve frozen evaluation artifacts and existing benchmark runs.

## Baseline and work isolation

- `e04b808` migrated the mode CLI to `src/birdview.mts`, generating `scripts/birdview.mjs`. Strict checking, build verification and CI integration already exist.
- The initial temporary `src/render.d.mts` declaration is replaced by the real `src/render.mts` implementation in issue #12.
- The working tree also contains separate constraint, website and evaluation work. These changes are not part of this migration. Do not stage, overwrite or revert them. Coordinate ownership before migrating shared files such as `scripts/render.mjs`, `scripts/validate.mjs`, schemas and `package.json`.
- Before each stage, record its base commit, relevant pending changes, owned files and commands that currently pass. Do not label another task's unfinished code a migration regression.

## Target structure and decisions

```text
src/
  contracts/         runtime definitions and inferred domain types
  core/              semantic validation and pure layout/state logic
  node/              CLI, rendering, Git inspection and repository tools
  viewer/            browser entry, interactions, state and DOM code
test/                 TypeScript unit, integration and browser tests
scripts/*.mjs         distributed Node entry points and supporting output
assets/viewer.js      generated browser bundle embedded into standalone HTML
schemas/*.json        generated exchange schemas, if retained for consumers
```

Move the existing CLI into this layout only when output mapping is ready; keep its public path working throughout. Node ESM and browser DOM need separate TypeScript configurations. Share domain types through explicit imports, not ambient globals.

Use a TypeScript runtime-schema definition as the canonical structural contract. Stage 1 selected TypeBox 0.34.41 with the existing Ajv 8.20.0 validator instead of the initial Zod candidate: it directly represents existing `uniqueItems`, `dependentRequired`, pattern-property and strict-object rules. Infer types from the definitions. Generate published JSON Schema from them; do not hand-maintain parallel definitions. JSON/JSONL remains the AI-facing exchange format. Literal unions export as `anyOf` instead of `enum`; accepted JSON is compared with the old schemas, while detailed Ajv message wording/count may differ. Existing public schema IDs and definition anchors remain available. The existing date-time annotation-only policy is unchanged.

Keep cross-record and repository checks as explicit semantic validation: schema revision binding, ownership, event order, constraint references and Git comparisons do not become true merely because an object has a TS type. Parse external input as `unknown`, validate it, then narrow it. Separate wire data from UI state and computed layout.

Use `tsc` for strict checking and Node output. Use a small browser bundler, preferably esbuild after compatibility verification, to turn explicit imports into one self-contained script. Inline that script into the generated HTML; opening via `file://` must not require a server, CDN or runtime module fetch. Do not introduce a UI framework solely for this migration.

## Stages and acceptance

### 0. Freeze the migration baseline

- Inventory maintained scripts, browser entry points, tests, inline scripts in templates/site pages and release assets. Classify experimental previews separately; migrate only if they are accepted as maintained product code.
- Capture CLI exit behavior, exported functions, valid/invalid fixtures, multilingual views and standalone HTML behavior.
- Resolve shared-file ownership with ongoing work. Record baseline failures separately.

Acceptance: a bounded file inventory, baseline results and an agreed first batch; no unrelated work enters a migration commit.

### 1. Introduce the canonical contracts

- Define architecture, activity, constraints, evidence, translations and validation results in `src/contracts/` and infer their types.
- Preserve missing-versus-null behavior, optional legacy fields, unknown-field rejection, string/path restrictions, cross-schema references and validation options. Do not silently coerce values or strip invalid fields.
- Run old and new validation against the same positive and negative fixture corpus. Explain every acceptance difference; keep existing error codes and locations where consumed.
- Test JSON Schema export separately: refinements may not be representable. Document the structural/semantic boundary instead of claiming the exported schema enforces everything.

Acceptance: fixture parity, useful type narrowing after validation and reproducible schema export. Deliberate data-format breaks require a versioned migration and fixtures, not an accidental change during translation.

### 2. Migrate the Node core

- Migrate `validate.mjs`, `render.mjs` and accepted constraint-inspection functionality to typed sources in dependency order. Replace `src/render.d.mts` with the real typed implementation.
- Type options, results, diagnostics and filesystem/process boundaries. Preserve safe path checks, output replacement behavior and CLI exit codes.
- Migrate repository build/documentation tools too. Keep stable command paths using generated entry points where needed.

Acceptance: CLI, contract and Git-fixture tests pass against emitted JS; `doctor` works outside the repository; installed bundles work without invoking a TS compiler.

### 3. Migrate the browser implementation

- Start with routing/layout and translation logic; then migrate activity state, constraints, guide and main view.
- Replace textual script insertion and implicit shared variables with explicit imports and a small, typed viewer state. Avoid replacing globals with one untyped context object or inventing a large state-machine framework.
- Model view modes and event phases as unions. Handle absent modules/events and DOM nodes deliberately; do not silence them with blanket casts or non-null assertions.
- Replace tests that evaluate source strings with direct module tests, while retaining real-browser tests of the generated page.

Acceptance: Chinese/English, architecture/changes/comparison, selection, hover, zoom, guide, constraint details and narrow layouts behave as before. Test empty/legacy data, escaping and browser errors. The page remains offline and self-contained.

### 4. Complete tools, tests and distribution

- Migrate remaining maintained helpers, browser tests and site/template executable logic. Third-party code is not rewritten. Use a supported compiled-test directory excluded from Git, and point browser tests at built assets.
- Keep compiler and bundler as development dependencies. Include required JS, runtime dependencies, assets, generated schemas and license notices in release installation checks.
- Expand `check:build` to cover every generated artifact, including added/deleted outputs. Maintain an explicit output inventory; never clean arbitrary paths or mix generated cleanup with source deletion.
- Avoid circular bootstrapping: npm scripts must be able to build the TS build-check tool before using it, or ship and verify its generated JS.

Acceptance: a clean source archive installs and runs using the documented commands; generated output is reproducible across Windows/Linux and supported Node versions, independent of CRLF/LF checkout.

### 5. Remove transitional paths and release

- Remove temporary declaration shims and duplicate handwritten JS only after parity is demonstrated. Ajv remains the chosen validator for TypeBox contracts, not a migration leftover. Update dependency lockfiles, notices, skill instructions and paired installation/contribution documents.
- Keep external command names and exported data compatibility unless an explicit migration is documented. Archive baseline results and list verified platforms, skipped browser checks and remaining gaps.
- Publish only after authorization. Do not replace the skill snapshot of an evaluation already in progress.

Acceptance: all maintained first-party executable sources and tests are TS; remaining JS is identified generated output or third-party code; no temporary bypass remains unexplained.

## Quality gates and execution rules

- Require `strict`, `noUncheckedIndexedAccess` and `noEmitOnError`. Enable stricter optional-property checking in the new contracts. No broad `any`, `@ts-nocheck` or unchecked double assertions to make migration appear complete.
- For each batch: typecheck, build/output consistency, affected behavior tests and reviewed diff. Run browser checks when browser behavior/build changes; run the full matrix at integration milestones.
- CI must ultimately cover Windows/Linux, the supported Node versions, semantic/contract fixtures, generated-output consistency, documentation and browser smoke tests. Existing browser coverage is not automatically CI coverage.
- A successful schema/type check does not establish architectural truth or product correctness. Report actual results and limits.
- One coherent stage or module per commit. Keep independent product changes separate. Roll back a failing batch together with its generated outputs and dependency changes; retain the previous release until installation and browser gates pass.

## Progress record

| Stage | Status | Evidence / next step |
| --- | --- | --- |
| Initial CLI | Complete | `e04b808`; strict compilation, output comparison and 7 mode tests passed |
| 0: baseline | Complete | Isolated worktree; frozen schema/routing/i18n baselines, CLI fixtures and visual comparisons; unrelated work excluded |
| 1: contracts | Complete | PR #7; TypeBox source, inferred types, Ajv narrowing, schema export and mutation/type-negative parity |
| 2: Node core | Complete | PRs #9, #11 and #13; repository checks, semantic validation and renderer; no declaration shim |
| 3: browser | Complete | PRs #15, #17 and #19; strict DOM/activity/constraints/guide entry and offline bundle; 24 identical visual cases |
| 4: distribution | Complete | PR #21 site/bootstrap; #22 typed tests, explicit artifact inventory, clean archive installation and CI browser/platform gates |
| 5: cleanup/release | Cleanup complete; release separate | Maintained code/tests are TS; remaining JS is generated. No release requested |

Update this table after each batch with commit, owned files, checks actually run and unresolved issues. Estimated completion dates are not substitutes for acceptance evidence.

The batch notes below retain their status at the time; the table and final verification record describe the current state.

Viewer completion (#18): the existing execution order now lives in `src/viewer/main.mts`, importing routing and i18n explicitly and emitting `assets/viewer.js`. DOM access is narrowed at runtime; optional nodes remain optional. View modes, guide restoration, constraints and activity records are typed without `any` or disabled checks. Legacy script fragments are removed. Chromium passed viewer, guide, constraints and viewport checks, including state/focus restoration; 24 desktop/mobile language/theme/view screenshots match byte-for-byte. CSS is unchanged. Guide tests now inspect rendered DOM state instead of global variables. Remaining work: site/template inline execution, remaining tests and distribution cleanup.

Translation-core batch (#16): move the unchanged UI catalog, locale discovery, URL/storage/base selection and text/array fallback into `src/viewer/i18n.mts`. The DOM adapter keeps its existing update sequence and styles. Direct module tests cover precedence, Chinese subtags, missing translations, empty translated text, question arrays and old catalog/example parity. Local typecheck, build/output checks and 80 tests passed. This batch does not claim the whole DOM translation layer has migrated.

Routing batch (#14): `src/viewer/routing.mts` exports typed geometry, preserving dimensions, lane selection, costs and corner radii. The existing viewer accesses the generated IIFE through a single `BirdviewRouting` bridge until its own migration. Direct ESM tests compare exact coordinates and SVG paths against a frozen pre-migration implementation, including reversed edges, self edges, blockers, empty layouts and three example maps. Typecheck, generated-output checks and 77 tests passed locally. Chromium screenshots were byte-identical across 24 cases (Chinese/English, light/dark, 1440×900/390×844, architecture/changes/compare) with no page errors; animations were disabled only during capture. This is static visual parity, not exhaustive interaction coverage. CSS and the HTML template are untouched; only generated script content changes in the demo. Windows/Linux Node 18/24 CI remains the merge gate.

Renderer batch (#12): `src/render.mts` replaces the temporary declaration and generates the existing CLI. Local typecheck, build/output comparison and 76 tests passed. The rebuilt tracked demo is byte-identical. A TypeScript CLI test verifies invalid map/JSONL input preserves existing output, rejects input/output collisions and non-HTML output, and renders complete embedded assets from outside the repository. Browser scripts are unchanged; browser interaction checks were not rerun. Windows/Linux Node 18/24 CI remains the merge gate. Pending constraint-inspection work from other tasks is excluded.

Validator batch (#10): `src/validate.mts` owns semantic validation and the CLI, emitting the existing `scripts/validate.mjs` entry point. External map/event values remain unknown until schema validation. Diagnostics, options, translation fields, constraints and collaboration locks are typed. Existing semantic/render tests plus a TypeScript CLI test cover schema rejection, malformed JSONL, usage errors and execution outside the repository. Browser code and unrelated pending constraint additions are excluded.

Stage 1 inventory: owns `src/contracts/`, emitted `scripts/contracts/`, schema export/build checks and contract parity/type tests. Shared `schemas/`, `scripts/validate.mjs` and package files receive only the migration integration. Uncommitted constraint additions remain in the original workspace and are excluded from this PR. The mutation corpus compares runtime and exported schemas with pre-migration schemas and checks input non-mutation. It is not an exhaustive proof of equivalence. Browser code and the frozen public benchmark are not migrated in this batch; cross-platform execution remains a CI gate.

Stage 1 snapshot verification before PR integration: typecheck, build, generated-output comparison and 72 tests passed in an isolated committed snapshot. The isolated PR contains 23 documentation pairs. Browser tests were not run for this contract-only batch. The PR's Windows/Linux Node 18/24 matrix must pass before merging.

Integration: PR #7 passed Windows/Linux Node 18/24 CI and was merged. The next batch migrates `check-docs` and `check-build`, retaining their command paths and distributing generated JavaScript. Two TypeScript integration tests passed locally: documentation drift/invalid records do not overwrite the saved record; a real compiler build detects stale and missing artifacts. Strict typecheck, build and output comparison also passed. The new test compilation output is ignored; remaining tests and browser code still await migration. PR checks remain required before merging this batch.

Site/bootstrap batch (#20): website language switching and installation/copy flows now live in `src/site/main.mts`; the template theme bootstrap is generated from `src/viewer/theme.mts`. Local browser checks compared 12 desktop/mobile, language and agent combinations: identical full-page screenshots and commands, with copy success/failure and no page errors. Existing styles and text are unchanged. Remaining test migration and clean-distribution audit follow separately.

Final migration gates (#22): all maintained test sources are now strict TypeScript. Typed fixture loaders validate JSON before use; deliberate invalid mutations remain runtime tests. Tests compile into ignored `.test-build/` and import shipped JS, preserving CLI main guards. Local verification passed 80 tests, all five Chromium suites (viewer, guide, constraints, viewport, site), typecheck, reproducible build, examples, documentation and a committed source archive installation. The archive used fresh dependencies, ran doctor and setup/uninstall for Codex, Claude Code and DeepSeek before any build, then reproduced artifacts. npm audit reported zero vulnerabilities. The final demo is unchanged by this batch.

`build-artifacts.json` is the explicit distribution inventory: every JS file in scripts/assets/docs is generated from `src/**/*.mts`; exchange schemas are generated from the TypeBox contracts. After migration acceptance, the frozen routing/i18n implementations and v1 schema copies were removed. Current behavioral tests and runtime/exported-schema consistency checks remain. No JS implementation or test remains as a transitional source. CI gates cover Windows/Linux Node 18/24, source archive installation, and Linux Node 24 Chromium. Static visual parity was established in earlier batches; it does not prove every possible interaction. The original dirty workspace and ongoing evaluation snapshots are excluded. No tag or release is created by this migration.

[CI verification](https://github.com/Qiuner/birdview/actions/runs/35326765780) of final code commit `a8fb911` passed: Windows/Linux Node 18/24 completed unit tests, documentation/examples and clean archive installation; all five Linux Chromium browser suites passed. PR #23 delivers the migration and closes Issue #22.
