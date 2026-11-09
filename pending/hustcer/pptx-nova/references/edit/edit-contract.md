# Edit Contract

Read this reference for Micro Edit, ordinary Edit, and Structural Edit workflows.
Translation and Refurbish already have specialized coverage/fidelity contracts;
do not duplicate those sidecars unless a separate local repair is performed.

`edit-contract.json` is the run-level source of truth for an existing-deck edit:
what may change, what must stay unchanged, which dry-run ops own each target,
and which evidence must pass before publication. It does not replace inspect,
patches, xdoc dry-run, semantic diff, visual review, or structural gates.

When the current deck has explicit future/carryover rules, first follow
`session-rules.md`. A passed `session-rules-resolution.json` is compiled into
this contract; session rules never form a parallel execution or delivery gate.

## Workflow

```text
inspect/select
  -> edit-contract-draft.json
  -> <skill-root>/scripts/cli/edit/contract.mjs
  -> edit-contract.json
  -> patch + dry-run
  -> apply into run directory
  -> semantic diff + scoped evidence
  -> evidence-manifest.json
  -> <skill-root>/scripts/cli/edit/contract-gate.mjs
  -> publish only when agentGate.passed=true
```

Create the contract after target resolution and before writing/applying the
patch. The generator hashes the current source PPTX. If the source later
changes, the gate returns `nextAction: "refresh-inspect"`; do not reuse old
inspect/select/selector evidence.

## Draft Shape

The agent authors a small draft. Slide indexes and `opIndexes` are 0-based.
`selector` should copy the inspect/select-proven patch selector shape.

```json
{
  "schemaVersion": "pptx-nova-edit-contract/v1",
  "request": "Rename the cover title without changing another object",
  "scope": "single-object",
  "operationKind": "text-edit",
  "source": {
    "inspectPath": "inspect.json",
    "selectPaths": ["select.json"]
  },
  "targets": [
    {
      "id": "cover-title",
      "slide": 0,
      "opIndexes": [0],
      "selector": { "shape": { "id": 5 } },
      "resolvedIdentity": { "slide": 0, "id": 5, "name": "Cover Title" },
      "expected": {
        "beforeText": "Old title",
        "afterText": "New title",
        "changeCategories": ["text"]
      }
    }
  ],
  "coverage": {
    "required": true,
    "expectedTargetCount": 1
  },
  "allowedChanges": ["text"],
  "preserve": ["slide-count", "non-target-shapes", "target-text-style"],
  "requiredEvidence": ["dry-run", "semantic-diff", "style-diff", "png-preview", "vision-diff"]
}
```

Generate the normalized contract:

```bash
node <skill-root>/scripts/cli/edit/contract.mjs \
  --draft <run-dir>/edit-contract-draft.json \
  --source source.pptx \
  --output <run-dir>/edit-contract.json \
  --json
```

When a session-rules resolver returned a passed overlay:

```bash
node <skill-root>/scripts/cli/edit/contract.mjs \
  --draft <run-dir>/edit-contract-draft.json \
  --source source.pptx \
  --session-rules-resolution <run-dir>/session-rules-resolution.json \
  --output <run-dir>/edit-contract.json \
  --json
```

The normalizer verifies the rules/operation/resolution hashes and source
revision, merges rule-owned targets and preserve requirements, and expands
required target coverage. Do not manually copy resolver targets into the draft.

The generator validates target IDs, target count, op indexes, evidence names,
stable selector identity, and source existence, then writes the absolute source path, SHA-256, and byte
length. Use `--overwrite` only for the current run after refreshing target
evidence.

Direct id/name selectors are normalized into `resolvedIdentity`. Query or
placeholder selectors must explicitly carry the inspect/select-proven resolved
id or name; a slide-only identity is rejected. Mark an unchanged target with
`expected.alreadyCompliant: true` only when its declared before/after values
match and dry-run still resolves the intended object.

Document-wide `set-font` has a dedicated `kind: "document-fonts"` target under
`scope: "all-slides-style"` / `operationKind: "font-normalization"`; follow
[font normalization](font-normalization.md) for its slide count, exact intent and reviewed analysis digest.
It deliberately has no object selector. The gate accepts only one `set-font` operation, style changes,
and complete slide evidence; this target cannot authorize arbitrary document-wide operations.

Structural scope additionally declares expected slide delta, changed slides,
and allowed object types:

```json
{
  "expectedStructure": {
    "slideCountDelta": 1,
    "changedSlides": [3],
    "objectTypes": ["textBox", "picture"]
  }
}
```

Use `kind: "slide"` for a newly added/removed whole-slide target that has no
pre-existing shape identity. Slide targets are valid only for structural scope;
ordinary object targets still require a stable resolved id or name.

Rule-owned produced objects use `kind: "object"`, `produced: true`, and a stable
shape name declared by `session-operation.json`. Their
`expected.sessionRulePostconditions[]` are limited to machine-verifiable
`font-color` and `fill-color` values.

### Native `slide-copy` structural evidence

`xdoc pptx slide-copy` is a first-class structural command, not a patch op. Its
dry-run/apply report is `pptx-slide-copy/v1` and intentionally has no
`opResults[]`. Never fabricate a `pptx-dry-run/v1` wrapper merely to satisfy the
Edit Contract.

For multiple donor slides, prefer one transactional command:

```bash
xdoc pptx slide-copy -i target.pptx --source donor.pptx \
  --slides 1,3 \
  --template-strategy register-source --size-strategy require-match \
  --output <run-dir>/candidate.pptx \
  --dry-run --json > <run-dir>/dry-run.json
```

CLI `--slides` is 1-based. The report and contract use 0-based
`sourceSlide`/`targetSlide` indexes. `--all` selects all donor slides, the two
selectors are mutually exclusive, and omitting both copies only donor slide 1
(there is no `--slide` option).

Treat the v2 dry-run as a fingerprint-bound execution plan. Require
`status: "success"` with `outcome: "passed"`, `preflight.readOnly: true`, no `preflight.blockers`, and
target/donor `targetFileSha256` / `sourceFileSha256` values that still match the
files immediately before apply. `targetFingerprint` / `sourceFingerprint` are
normalized OPC package fingerprints, not whole-file hashes; require both
contracts without comparing them to each other. Review every `preflight.risks`
item instead of silently accepting it.
`preflight.parts[]` and `preflight.relationships[]` describe the exact planned
package mutation, including dependencies that will be reused rather than added.
Require `preflight.strategy.template` / `slideSize`, inspect every
`preflight.templates[]` source→target layout/master/theme mapping, and retain
its normalized fingerprints, outcome, target-side registration ids/rIds,
affected source slides, and `entire-copy-batch` rollback boundary. Under
`register-source`, `rebound-target` is invalid evidence; under `rebind-target`,
it is an explicit fidelity decision rather than a hidden fallback.

Before apply, bind the report to the donor/target page-size policy:

```bash
node <skill-root>/scripts/cli/edit/copy-size-gate.mjs \
  --target target.pptx \
  --donor donor.pptx \
  --copy-report <run-dir>/dry-run.json \
  --output <run-dir>/copy-size-gate.json \
  --json
```

The normalizer automatically adds `copy-size-gate` to `requiredEvidence` for
`operationKind: "slide-copy"`. The final gate requires its SHA-bound report and
rejects mismatched dimensions with
`nextAction: "choose-explicit-slide-size-strategy"` for compatibility. Native
xdoc now declares `require-match` and blocks the same mismatch in core
preflight; therefore use matching dimensions or stop for a user decision until
a future audited transform strategy exists. Do not silently scale donor
geometry or compensate in a renderer.

Bind each produced slide target to its donor identity:

```json
{
  "scope": "structural",
  "operationKind": "slide-copy",
  "targets": [
    {
      "id": "copied-donor-slide-1",
      "kind": "slide",
      "slide": 10,
      "opIndexes": [0],
      "expected": {
        "changeCategories": ["structure"],
        "copyFrom": { "sourceSlide": 0, "sourcePptx": "/abs/path/donor.pptx" }
      }
    },
    {
      "id": "copied-donor-slide-3",
      "kind": "slide",
      "slide": 11,
      "opIndexes": [1],
      "expected": {
        "changeCategories": ["structure"],
        "copyFrom": { "sourceSlide": 2, "sourcePptx": "/abs/path/donor.pptx" }
      }
    }
  ],
  "coverage": { "required": true, "expectedTargetCount": 2 },
  "allowedChanges": ["structure"],
  "expectedStructure": {
    "slideCountDelta": 2,
    "changedSlides": [10, 11],
    "objectTypes": []
  }
}
```

The gate requires one valid `copied[]` entry for each target, verifies optional
`expected.copyFrom.sourceSlide/sourcePptx`, checks slide and relationship part
names plus every dependency target against aggregate `changedParts[]`, and
rejects copied target slides outside the contract. Flattened
`dependencyMappings[]` remains aggregate audit evidence; it is not converted
into synthetic patch operations.

## Evidence Policy

Choose the smallest policy that can prove the requested edit:

| Edit kind                          | Required evidence                                                                                                                                           |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Notes/core metadata only           | `dry-run`, `semantic-diff`                                                                                                                                  |
| Visible single-object text         | `dry-run`, `semantic-diff`, `style-diff`, `png-preview`, `vision-diff`                                                                                      |
| Visible multi-target/batch text    | Same as visible text, covering every target slide                                                                                                           |
| Single-object fill/line/font style | `dry-run`, `semantic-diff`, `png-preview`, `vision-diff`                                                                                                    |
| Geometry/image/layout              | Above plus `final-inspect`; add `structure-check` when package risk warrants it                                                                             |
| Structural edit                    | `dry-run`, `semantic-diff`, `png-preview`, `vision-diff`, `final-inspect`, and normal structural audits; native `slide-copy` also requires `copy-size-gate` |

For text-only edits that must preserve formatting, include
`preserve: ["target-text-style"]` and require `style-diff`:

```bash
xdoc pptx i18n-style-diff \
  --source source.pptx \
  --candidate <run-dir>/candidate.pptx \
  --json > <run-dir>/style-diff.json
```

The command name is translation-oriented, but its textless OOXML signature is
also the strongest available evidence that an ordinary text replacement kept
neighboring `a:rPr`, `a:pPr`, and `a:bodyPr` structure. A whole-frame
`set-text-frame` can pass dry-run, semantic diff, and vision-check while destroying
small footer/run styling. When style fidelity matters, prefer inspect-proven
`set-run`/run-level edits or another text-node preserving path.

The signature also includes non-text slide structure and geometry. On an existing
`shape` autofit frame, even a guarded `set-run` can change its bbox during native
reflow; dry-run/apply may report only the text change while the final semantic diff
reports both `text` and `shape`. Compare source/candidate inspect bboxes before
declaring a text-only edit. When geometry must stay fixed, stop at that change and
resolve the fitting policy; repeating the same run edit will not restore the frame.
When reflow is intended, declare the narrowly scoped `shape` change before apply,
require final inspect and rendered review, and do not claim `target-text-style`
preservation from a failed style signature. Never widen the contract just to pass.

Consume the actual `pptx-diff/v1` fields: current xdoc reports `baselinePath` /
`targetPath`, `summary.baselineSlideCount` / `targetSlideCount`, and shape
`baseline` / `target`. The gate also accepts the earlier `source` / `candidate`
form. Preserve the original report for path binding, object identity, text,
slide-count delta and allowed object-type checks; do not rewrite it into a fixture.
Request `--detail full` for the final contract diff. The default `summary` report
has per-slide rollups without `shapeChanges[]` and cannot prove object locality;
the gate returns `collect-full-semantic-diff` rather than treating omitted changes
as an empty list. A normal final edit needs one full diff, not summary plus full.

For visible edits, prefer a changed-scope differential visual gate:

```bash
xdoc pptx vision-diff \
  --source source.pptx \
  --candidate <run-dir>/candidate.pptx \
  --slides <1-based-target-slides> \
  --json > <run-dir>/vision-diff.json
```

`vision-diff` allows inherited source issues but blocks newly introduced or
worsened high/medium issues. A candidate-only `vision-check` remains useful for
diagnosis, but it cannot reliably distinguish a regression from pre-existing
noise in a dense legacy deck.

Keep `visual-audit` outside the Edit Contract's semantic `requiredEvidence`
list because it is the separate final visual decision, not another edit-kind
fact. Its fixed pipeline audits both reference and candidate, so a pre-existing
reference problem may correctly produce `decision.action=stop` without proving
a new edit regression. Use `vision-diff` to explain differential risk, then
consume the canonical visual manifest as described in `../review/export-and-check.md`.

## Final Gate

After the candidate and evidence are stable:

```bash
node <skill-root>/scripts/cli/edit/evidence-manifest.mjs \
  --candidate <run-dir>/candidate.pptx \
  --evidence semantic-diff=<run-dir>/pptx-diff.json \
  --evidence style-diff=<run-dir>/style-diff.json \
  --evidence png-preview=<run-dir>/preview.json \
  --evidence vision-diff=<run-dir>/vision-diff.json \
  --output <run-dir>/evidence-manifest.json \
  --json
```

The manifest binds the current candidate SHA-256 to the exact SHA-256 of each
post-apply evidence file. Regenerate it whenever the candidate or evidence
changes.

```bash
node <skill-root>/scripts/cli/edit/contract-gate.mjs \
  --contract <run-dir>/edit-contract.json \
  --candidate <run-dir>/candidate.pptx \
  --dry-run <run-dir>/dry-run.json \
  --copy-size-gate <run-dir>/copy-size-gate.json \
  --diff <run-dir>/pptx-diff.json \
  --style-diff <run-dir>/style-diff.json \
  --preview <run-dir>/preview.json \
  --vision-diff <run-dir>/vision-diff.json \
  --evidence-manifest <run-dir>/evidence-manifest.json \
  --output <run-dir>/edit-contract-gate.json \
  --overwrite --strict --json
```

Omit optional evidence flags only when that evidence is not listed in
`requiredEvidence`. Defaults are resolved beside the contract.

The gate checks:

- current source SHA-256 matches the contract;
- the candidate exists and every loaded report names the same source/candidate;
- the evidence manifest binds current candidate bytes and every post-apply
  report hash; mtime freshness is a supplemental stale-candidate signal;
- every required patch target owns successful dry-run `opResults[]`, or every
  native `slide-copy` slide target owns a complete, fingerprint-current
  `pptx-slide-copy/v1`
  slide/relationship/dependency mapping;
- native `slide-copy` has a passing, target/donor file-bound
  `pptx-nova-copy-size-gate/v1` report with identical slide dimensions;
- every dry-run op index is owned by a contract target;
- patch dry-run `resolvedSelectors[]` and semantic targets match the contract;
  native `slide-copy` evidence instead matches the declared donor and produced
  slide identities without inventing selectors;
- semantic diff source text still matches declared `beforeText` and the final
  candidate matches declared `afterText` when those guards are present;
- dry-run and reliable diff change categories stay inside `allowedChanges`;
- reliable shape changes stay inside resolved contract targets;
- slide count remains stable when `preserve` includes `slide-count`;
- style signatures pass when `style-diff` is required;
- preview and declared vision/vision-diff evidence cover every 1-based target slide;
- vision-diff introduces or worsens no high/medium issues on that scope;
- optional final inspect/structure reports are successful when required.
- structural slide delta, changed slides, and object types match
  `expectedStructure` when declared.
- bound session-rules artifacts are unchanged and still match the contract
  source revision/deck id;
- every applicable produced-object rule is present in final inspect and the
  candidate PPTX bytes contain its required font/fill value.

Derived slide `summaryChanges` are not treated as separate out-of-scope edits:
legitimate text changes can alter keywords and density summaries. Only reliable
shape changes and explicit slide add/remove counts are machine locality facts.
Uncertain/unsupported semantic-diff regions remain `attention` and must be
paired with scoped visual review; they are not proof of pass or failure.

## Stable Next Actions

Read `edit-contract-gate.json.agentGate` first:

| `nextAction`                            | Meaning                                                                                               |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `refresh-inspect`                       | Source hash changed or source is missing; rebuild target evidence and contract                        |
| `run-copy-size-gate`                    | Native copy evidence lacks the required page-size gate; run it before apply                           |
| `refresh-slide-copy-preflight`          | Copy preflight or size evidence is stale; regenerate both from current target/donor files             |
| `choose-explicit-slide-size-strategy`   | Donor/target dimensions differ; stop until an explicit runtime strategy exists or target size changes |
| `regenerate-current-candidate-evidence` | A report belongs to another source/candidate; regenerate evidence from the stable candidate           |
| `retry-dry-run-with-fix-patch`          | Dry-run itself did not succeed                                                                        |
| `rebind-selectors`                      | Target op exists but did not resolve to the contract selector                                         |
| `complete-missing-coverage`             | One or more required targets/expected values were not covered                                         |
| `retry-with-style-preserving-text-edit` | Text changed non-text OOXML style structure                                                           |
| `repair-new-visual-regressions`         | Changed slides contain new/worsened high or medium visual issues                                      |
| `review-out-of-scope-changes`           | Reliable changes escaped the contract or changed forbidden categories                                 |
| `verify-changed-scope`                  | Required preview/vision evidence is missing or incomplete                                             |
| `run-structure-audit`                   | Required package structure evidence failed                                                            |
| `refresh-session-rules-resolution`      | Bound rules/operation/resolution changed; resolve and regenerate the contract                         |
| `apply-session-rules`                   | Candidate bytes do not satisfy an applicable rule postcondition                                       |
| `block-and-request-user-decision`       | A remaining blocker has no safe automatic repair                                                      |
| `publish`                               | Machine contract passed; finish required PNG review before delivery                                   |

`publish` does not waive manual PNG/contact-sheet review. It means the machine
contract, target coverage, locality, and declared evidence passed.

## Boundaries

- Do not create targets by guessing selectors. Contract selectors come from
  current inspect/select evidence.
- Do not list broad `allowedChanges` merely to make the gate pass.
- If a deliberate new target is discovered, update the draft and regenerate
  the contract before applying it.
- Contract targets describe allowed edits, not every derived summary signal.
- Translation uses i18n unit/source-hash coverage; Refurbish uses its
  plan/reference-map/fidelity/content audit. Do not weaken those specialized
  gates by replacing them with the generic contract.
- Keep `edit-contract.json`, `evidence-manifest.json`, and `edit-contract-gate.json` in the retained run
  evidence package.
