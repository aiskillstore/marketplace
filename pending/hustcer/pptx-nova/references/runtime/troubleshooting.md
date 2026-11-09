# Troubleshooting and Self-Repair

xdoc errors are structured. First read `error.code`, the diagnostics, and `suggestions[]`; executable suggestions are provided in `remediation`:

```json
{
  "code": "<snake_case_code>",
  "severity": "fatal / error / warning / info",
  "message": "human-readable",
  "opIndex": 2,
  "docsRef": "https://...",
  "suggestions": [
    {
      "reason": "Review the corrected selector",
      "remediationUnavailable": { "reason": "context-unavailable" }
    }
  ]
}
```

The example has no executable suggestion. `remediationUnavailable` and `remediation` are mutually exclusive; the reason can only be `identity-unavailable`, `context-unavailable`, `ambiguous-source`, `target-unavailable`, or `payload-limit`. Retain the diagnostics and restore the input or correct the request according to the actual reason. A missing digest does not permit skipping validation.

## CLI Argument Failures

Exit 2 can occur before a document is opened or a JSON report is produced. Retain stderr and the
actual argument array. Check missing values, duplicate single-value options, integer syntax and
overflow, and flags outside the selected action's contract. For example, `--dpi abc` is a parser
failure, while a parsed DPI outside the action's permitted range is a product validation failure;
neither permits silently substituting the default DPI. Follow
[CLI invocation guidance](schema-discovery.md#cli-invocation-and-argument-failures) to build the call.

Query action help separately, then correct the same intended request. Use absolute paths for
option-looking filenames; a newer parser may now treat a literal `--help` or `--field-date` operand
as a filename where an older runtime misinterpreted it. Help text or completion output is discovery
evidence, not a document result. A parser failure alone is not evidence of an authorization problem
or an unsupported PPTX feature. If execution reached publication, use the output-failure checks below
before considering a retry.

## Output Failure: First Determine Whether the Primary File Was Published

The default sidecar is `<output>.xdoc.json`. It must not resolve to the same file as the output PPTX or an input PPTX, patch, brand, bindings, or template data; check path aliases such as symlinks too. `--overwrite` cannot resolve this conflict. Existing sidecars are also protected against overwriting; prefer new candidate/sidecar paths.

One-shot apply/new publishes the PPTX before writing the sidecar; the two are not a joint atomic transaction. A later sidecar failure still returns an error but discloses `primaryOutputPublished:true`, `outputUntouched:false`, `output` (the written PPTX), and `blockedOutput` (the failed sidecar). Retain the report and existing files; check both paths, file digests, and current contents. Do not automatically replay the mutation, add `--overwrite`, or treat the output as having passed delivery gates. If these fields are absent, do not infer that the file is unchanged.

If re-execution is needed, run the complete workflow from the retained original input and patch to new candidate/sidecar paths; do not use the already written candidate as a new input for the same patch. To continue using that candidate, obtain the real evidence required by the current workflow and complete its gates; do not fabricate a missing sidecar or change a failed report to success. A daemon session transaction and the files on disk have separate state. After failure, inspect the session and disk output separately; do not infer one from the other. See `daemon-sessions.md`.

## Conversion Input Quotas and Authorization Failures

If the user has supplied a Runtime license, requests installation/renewal, or encounters unhealthy credentials or an ineffective installation, follow [License Installation and Diagnostics](licensing.md). That workflow covers configuration/source precedence, environment differences, Clock, device admission, and uncertain writes. Ordinary successful tasks need no extra authorization maintenance.

Identify the product and feature being invoked before assessing limits. Read `commands.convert.licensePolicy` from the current `xdoc schema --command convert`; when complete quota facts are needed, read and save `authContract.cliFeatureTask` and `authContract.productLimits` from `xdoc schema --mode full`. Do not substitute SDK descriptions for the local CLI contract or infer published APIs from designs.

- The local CLI Free Baseline currently allows at most 10 slides and 5,242,880 bytes (5 MiB, inclusive) of compressed PPTX input combined. The current contract and actual authorization report govern each task. Total input includes primary and donor/secondary sources; slide count is the maximum of input, planned processing, and planned output slides. Do not infer that `--slides`, a different output format, or another transport removes the quota.
- Converter SDK PDF/Markdown profiles each disclose `freeMaxInputBytes:5242880` and `freeMaxSlides:null`, with no additional Free slide quota. They check compressed PPTX **input**, not final output size; resource and policy limits still apply at or below the boundary. A valid credential must authorize the requested product/format; another product's or format's credential cannot remove the restriction. These facts do not replace CLI task authorization.
- A local `convert` authorization refusal returns exit code 4 under the contract. Retain the actual error/authorization report, input byte count, and task scope; it does not prove chart slot exhaustion, parsing failure, or a bad file. `xdoc auth status` is diagnostic only (`taskAuthorization:not-evaluated`) and does not prove this operation was authorized.
- Do not automatically split tasks, delete slides, change data, relax strict flags, or bypass a refusal across products. Do not retry unchanged input and conditions; use an existing applicable license or explain the missing conditions. Compress input only when the task allows it, content is preserved, and the final candidate is rechecked. Do not fix quotas by changing extensions, selecting only a few slides, or deleting charts.

Ordinary successful tasks need no additional credential query; use this diagnosis only for a refusal, quota question, or explicit user request. See the relevant diagnostics in this file for chart logical slots and resource budgets such as fonts/memory; paid authorization does not automatically remove resource limits.

<a id="两种-remediation-与重试流程"></a>

## Two Remediation Kinds and the Retry Workflow

Identify whether the failure came from the local command, daemon, stdio JSON-RPC, or MCP, and read the corresponding report schema. Retry instructions for different transports are not a universal patch contract: do not apply remote service retry rules to local apply, or automatically replay a mutation based only on `retryable`, HTTP status, error text, or elapsed time. A service contract undisclosed by the current capabilities is not an available route; retain failure evidence and use the disclosed local workflow. Disclosed recovery suggestions remain subject to original input/request identity, output publication state, and existing authorization. Stop repeating the same failure under unchanged conditions; first resolve the prerequisites identified by the diagnostic.

| kind                | Complete payload                                                                   | Execution target                                                                               |
| ------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `replace-request`   | `request`, preserving version, ops, recipe, vars, preconditions, and other context | Re-execute the complete request from the original input; do not append it to the original ops. |
| `apply-to-document` | `patch:{schemaVersion,ops}`, containing only document-repair operations            | Execute once on the exact document used for the diagnosis; do not rerun the original creation. |

`replace-request.target` must contain `kind:"original-input"`, `requestCanonicalization:"jcs-rfc8785"`, `requestSha256`, and `inputSha256`. When explicitly starting from an empty document, `inputSha256:null`; otherwise it must be the input's SHA-256. `apply-to-document.target` must contain `kind:"document"` and the document's `inputSha256`. All digests are 64 lowercase hexadecimal characters. The consumer calculates and compares digests of its own retained original request/document; do not use report digests in place of independently expected values.

`remediation.reason` is a nonempty explanation, `confidence` a finite number from 0 to 1, and `autoRetry` a required boolean. `autoRetry:true` permits an attempt only under existing policy; still validate the complete shape, target, and context, then dry-run, reauthorize, and execute. Removing a failed operation changes request intent and always has `autoRetry:false`. Pass `--reviewed` only after reviewing the specific change; do not use it to bypass approval required by the user's current request.

To retain the request, input, and relative assets across processes, use the snapshot script **before the first submission**. First confirm that the current `xdoc schema --mode full` discloses `commands.pptx.remediationSchema`; the script checks this automatically and provides no legacy-field fallback for older runtimes. The following paths are examples; use new paths for the output and capsule:

```bash
node scripts/cli/runtime/remediation.mjs run \
  --patch request.json --input original.pptx --asset-root assets \
  --capsule run/remediation-context --output run/first.pptx > run/first-report.json

node scripts/cli/runtime/remediation.mjs apply \
  --capsule run/remediation-context --report run/first-report.json \
  --pointer /error/suggestions/0 --output run/repaired.pptx
```

Omit `--input` when starting from an empty document. `run` supports `--transport json-rpc`, `--dry-run`, `--intent intent.json`, and, with existing authorization, `--allow-raw-xml`. The first submission and retry use the same relative asset root in the capsule; subsequent changes to source files of the same name do not replace frozen assets. The capsule contains the private original request, PPTX, and assets; retain it until the retry ends. Without the first submission's capsule, do not automatically apply an old report; prepare a new request with complete context.

If an asset exists but the wrapper reports `ENOENT` or uses the wrong image, check whether the invocation path contains `symlink/..`. On POSIX, traverse according to the filesystem; do not first collapse it with `path.resolve` or ordinary `realpathSync`. Custom Node wrappers can reuse `scripts/lib/runtime/filesystem-paths.mjs`. When `--asset-root` is omitted, assets are relative to **the directory of the submitted patch path**, not the target directory of a patch symlink. The remediation script freezes assets within that directory; asset links escaping the root remain rejected.

`apply` dispatches by kind, selects exactly one JSON Pointer, validates and dry-runs it, then applies it. For document repair also pass `--document diagnosed.pptx`. Successful suggestions record receipts and cannot be executed twice. Original intent, raw XML constraints, and asset byte budgets are not relaxed; xdoc re-evaluates current authorization. Any digest/context mismatch prevents writing the target. After repair, diagnose the new document again before selecting another suggestion; do not blindly combine multiple suggestions for the same old document. Executable suggestions in one report total at most 1 MiB; over-limit suggestions retain diagnostics and the `payload-limit` marker.

## errorCatalog.scenarioCoverage — Repair Scenarios and Manual Templates

`commands.pptx.errorCatalog.scenarioCoverage` provides scenario descriptions and `patchTemplate:{schemaVersion,ops}`, marked `autoApplicable:false`. Templates lack the current request identity and cannot be copied directly as executable retry suggestions.

| id                          | Trigger                                                                                  | Repair strategy                                                                              |
| --------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `missing-shape`             | Selector matches nothing                                                                 | Remove the op as fallback; first `inspect` for the real shape id before retrying.            |
| `ambiguous-selector`        | Selector matches multiple shapes and the report includes candidate ids                   | Rewrite the selector as `{ "shape": { "id": <candidate id> } }`.                             |
| `invalid-chart-kind`        | Misspelled `add-chart.kind` / `variant`                                                  | Rewrite using fuzzy candidates in `enumRegistry.chartKind` / `chartVariant`.                 |
| `font-color-shape-spelling` | Misspelled font, color, theme color, or RGB that is not six uppercase hex digits         | Use fuzzy `enumRegistry` candidates or `1A73E8` (no `#`, uppercase).                         |
| `layout-contract`           | Missing required `populate-slide.content` field or an illegal extra field in strict mode | Add the placeholder or remove the illegal field; see strict mode in `../content/recipes.md`. |

Complete schema, including docsRef and manual templates:

```bash
xdoc schema --mode full | jq '.commands.pptx.errorCatalog.scenarioCoverage'
```

Templates explain diagnostics. Actual automatic attempts consume only `remediation` with complete target identity.

## OOXML Numeric Range Enforcement — Errors Include Bounds and Sources

dry-run / apply enforce **authoritative OOXML ranges** on numeric fields (constraints extracted from the Open-XML-SDK schema, enforced by both ajv and dry-run). Error messages provide the field path, bounds, and OOXML source, for example:

```
set-paragraph.format.lineSpacing must be at most 132
  (line spacing multiple written as a:spcPct val (1.0 = 100000) — OOXML a:spcPct@val 0..13200000)
```

First inspect `suggestions[].remediation`: such errors may provide a clamp/wrap repair with `autoRetry: true` (confidence 0.8), bringing out-of-range values within bounds (angles wrap modulo 360 rather than being clamped). The engine has validated that the repaired op passes contract validation. After checking the original request identity, repeat dry-run with the complete `replace-request.request`:

```
"reason": "Clamp /ops/1 out-of-range values to the OOXML bounds: plot.gapWidth: 501 -> 500 (…)"
```

Only when there is no clamp suggestion, such as an exclusive boundary like `majorUnit <= 0` with no definite replacement, manually change the value according to the message. Using correct ranges before writing the patch can save a dry-run:

| Field (wire units)                       | Allowed range | Common pitfall                            |
| ---------------------------------------- | ------------- | ----------------------------------------- |
| `plot.gapWidth`                          | 0..500        | Bar gap percentage                        |
| `plot.overlap`                           | -100..100     | Bar overlap percentage                    |
| `plot.bubbleScale`                       | 0..300        | Bubble scale percentage                   |
| `marker.size` / line-series `size`       | 2..72         | **Minimum is 2, not 1**                   |
| chart `style`                            | 1..48         | Built-in c:style number                   |
| `format.lineSpacing` (number = multiple) | >0..132       | 1.0 is single spacing; maximum 132        |
| `fill.angle` / shadow `angle` (degrees)  | 0..<360       | **360 is invalid**; use 0 for a full turn |
| `axes.*.scale.majorUnit`/`minorUnit`     | >0            | Zero and negative values are invalid      |
| `alpha` / gradient stop `position`       | 0..1          | Decimal fraction, **not 0..100**          |
| autofit `fontScale`                      | 1..100        | Also requires `mode: "text"`              |

## Writer Self-Check Warnings and semanticIssues[] — Semantic Audit Signals

The apply / dry-run `warnings[]` report contains **writer self-check** prefixes: OOXML checks on parts generated or rewritten by xdoc in this run. The table lists the most common classes; see the `semanticIssues[].code` enum for the complete set:

| Prefix          | Meaning                                                                                                                                                                                                                                                                                                                                            |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `child-order:`  | Child elements were written out of OOXML schema order (includes the full expected order).                                                                                                                                                                                                                                                          |
| `dangling-rel:` | An r:id / r:embed / r:link reference is absent from its owning `.rels`.                                                                                                                                                                                                                                                                            |
| `dangling-ref:` | An animation/build `spid` refers to a shape id (cNvPr) absent from the part.                                                                                                                                                                                                                                                                       |
| `duplicate-id:` | A cNvPr / sldId or other id is duplicated within a part (PowerPoint prompts for repair).                                                                                                                                                                                                                                                           |
| `part-truth:`   | A relationship points to a missing part, has a type mismatch, or a part lacks a Content-Types declaration.                                                                                                                                                                                                                                         |
| `part-graph:`   | A part has the wrong parent (e.g. notes directly under presentation), a slide has two notesSlide parts, a required slideMaster is missing, or a media reference is in a disallowed container. RuleId `sdk/part-graph/<not-allowed\|required\|only-one\|content-type\|data-reference>/<Parent>/<Child>`; reported only, not automatically repaired. |

Example: `child-order: ppt/slides/slide1.xml: <a:pPr> child <a:spcAft> must come
before <a:buChar> (schema order: …)`.

The `conformance:` prefix **is not** one of these self-checks. It indicates that the input package is ISO Strict (or already mixed); untouched parts retain their original bytes and new content is written as Transitional, so inspect reports the output as `conformance.package: "mixed"`. This is informational; PowerPoint opens mixed packages normally. Do not rewrite the patch or rerun for this disclosure.

**Determine the source:** these warnings on a deck generated from scratch by xdoc indicate an internal xdoc writer bug. Do not rewrite the patch to bypass it; report the complete warning to maintainers. When **editing an existing deck**, they are more often pre-existing defects in the source (for example, an external tool deleted a shape but left animation references); use the `semanticIssues[]` repair loop below.

### `semanticIssues[]` — Structured Semantic Issues and Document Repair

The same findings also appear in structured form in the top-level `semanticIssues[]` of the apply / dry-run report:

```jsonc
{
  "code": "dangling-ref", // enum: dangling-rel | rel-type-mismatch | dangling-ref | duplicate-id | part-truth | value-out-of-range | invalid-attribute-value | missing-required-attribute | invalid-attribute-comparison | invalid-xml | invalid-relationships | child-order | child-cardinality | child-choice | part-graph
  "ruleId": "<rule id>",
  "part": "ppt/slides/slide1.xml",
  "message": "<p:spTgt> spid=\"2\" references no <cNvPr> with id=\"2\" in the part",
  "remediation": {
    "kind": "apply-to-document",
    "target": { "kind": "document", "inputSha256": "<64 lowercase hex characters>" },
    "patch": {
      "schemaVersion": "pptx-patch/v1",
      "ops": [{ "op": "set-slide-animations", "slide": 0, "remove": ["5"] }],
    },
    "reason": "remove the 1 animation entries targeting missing shape id 2 …",
    "confidence": 0.9,
    "autoRetry": true,
    "requiresRawXml": false,
  },
}
```

Handling rules:

- Execute `apply-to-document.patch` only on the exact document that can be retrieved again, using the script above with `--document`. An unpublished dry-run candidate cannot stand in for the original; without the target, diagnose read-only.
- `requiresRawXml:true` requires existing permission; do not automatically grant extra permission to execute a suggestion. Permission requirements for restricted `repair-child-order` / `repair-preset-adjustments` / `repair-relationships` remain declared by the current runtime.
- An issue without remediation may have an uncertain repair (multiple candidate orphan parts, preserve-only animation, etc.). Preserve it and report the original message; do not invent a repair.
- `remove-shape` automatically cleans up animation and build references for removed shapes, including children in groups. Removing an animated shape **does not** require manually clearing its animations first; `dangling-ref` usually comes from a pre-existing deck defect, not this operation.

### Duplicate XML Attributes and Namespaces

Duplicate XML attributes cause another kind of parse failure: the same QName, or different prefixes resolving to the same namespace URI + local name, are rejected. The default namespace does not apply to unprefixed attributes. Raw XML editing also reparses the complete part during dry-run and apply. Do not bypass this by choosing the first/last value with a regex, removing namespaces, or enabling raw XML. Retain the input/failure report, identify the exact part and source, then make an evidence-based repair. For geometry edits prefer native shape/OLE operations and preserve namespace aliases and external extension elements with the same name.

### `preset-adjustments`: Office Interoperability Diagnostics and Explicit Repair

A nonempty adjustment list for a known preset with missing entries or irregular order reports `code: "preset-adjustments"` and `ruleId: "office/preset-adjustments/<preset>"`. This is a PowerPoint interoperability risk, not a synonym for XSD invalidity. Empty lists use preset defaults; do not fill all empty lists in bulk to eliminate this finding.

Only when known, unique, integer-constant guides can be safely normalized does the report provide `apply-to-document` remediation with internal action `repair-preset-adjustments`. It preserves explicit values, fills declared defaults, and restores declared order; `autoRetry:false`, `requiresRawXml:false`. Check the repair scope and existing task authorization first; pass `--reviewed` to the remediation helper only after explicitly adopting it. Do not automatically retry merely because a suggestion exists or additionally enable raw XML.

Preserve `target.inputSha256`, `expectedPartSha256`, `elementPath`, `ruleId`, `expectedRuleSha256`, and the reported element guard; do not hand-author or relax them. Unlike child-order repair, preset repair requires the exact SHA of the entire part even with an element hash. If another edit/repair changes the same part, re-audit the new candidate for suggestions; do not chain stale suggestions. Unknown/duplicate guides, nonconstant formulas, extension content, or ambiguous structures may provide diagnostics only; do not invent repair patches.

After repair, rerun full semantic/vision checks, affected-page previews, and PowerPoint clean-open when available. Assess the dry-run/apply new-issue delta separately from the candidate's full inherited debt. Renaming or structural edits may change a finding's ownership identity; if an existing finding reappears in the delta, stop and check source/candidate and current full diagnostics. Do not filter the gate report merely because it appears old by eye.

### Shell Audit of `[Content_Types].xml`

A PPTX is a ZIP. `unzip` matches entry patterns itself, so shell quoting alone still treats brackets as a pattern. Write `[Content_Types].xml` as `'[[]Content_Types].xml'`, where `[[]` means a literal opening bracket. Include ZIP integrity, Content Types XML, and key chart nodes in one reproducible audit:

```bash
set -o pipefail
unzip -t out.pptx
unzip -p out.pptx '[[]Content_Types].xml' | xmllint --noout -
unzip -p out.pptx 'ppt/charts/chart1.xml' |
  rg '<c:(trendline|errBars|dTable|dispUnits|minorGridlines|title)'
```

`chart1.xml` is an example; first find the actual chart part using `unzip -Z1 out.pptx` or `xdoc pptx inspect out.pptx`, then replace the path. `set -o pipefail` ensures the audit fails if upstream `unzip` cannot read or match an entry, instead of a downstream success hiding it.

## Exit Code Reference (`.exitCodes` in `xdoc schema`)

| code | stage         | Meaning                                                                                                          |
| ---- | ------------- | ---------------------------------------------------------------------------------------------------------------- |
| 0    | success       | Success; gate/planner decisions are in JSON, not the exit code.                                                  |
| 1    | failed        | Unclassified failure; report as a bug, do not branch on it.                                                      |
| 2    | args          | CLI argument parsing/validation failed.                                                                          |
| 3    | input         | Invalid/unreadable input, or a structured gate report completed with a non-pass status (report still on stdout). |
| 4    | authorization | Authorization refused (Free limit exceeded, invalid license, etc.); no artifact written.                         |
| 5    | slide         | Slide selection out of range.                                                                                    |
| 6    | parse         | PPTX parsing failed.                                                                                             |
| 7    | pdf           | PDF generation failed.                                                                                           |
| 8    | png           | PNG generation failed.                                                                                           |
| 9    | output        | Output target validation or writing failed (including existing output without `--overwrite`).                    |
| 10   | dependency    | Backend dependency unavailable.                                                                                  |
| 11   | internal      | Internal error.                                                                                                  |
| 12   | batch         | At least one batch item failed (convert/html2md/extract/check); inspect `--report`.                              |

## Error Categories (errorCatalog Registry)

PPTX business error `error.code` uses **snake_case**. Find the current catalog in this run's `xdoc schema` under `commands.pptx.errorCatalog.codes`. Read the complete failure report using the command's `ioContract.failure.schemaRef`; compact errors may omit `severity`, `suggestions`, or `docsRef`, so do not invent repairs. Handle protocol errors separately under the daemon / JSON-RPC / MCP contract; do not treat numeric protocol codes as business error codes. Common categories:

| code                                    | Meaning                                                                                                    | Action                                                                                                                              |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `invalid_json`                          | Patch / recipe is invalid JSON                                                                             | Fix JSON syntax and resubmit.                                                                                                       |
| `invalid_argument`                      | Missing field, wrong shape/value, or unreadable asset path                                                 | Correct fields using `path` / `expected` / `actual`.                                                                                |
| `invalid_arguments`                     | CLI invocation lacks arguments                                                                             | Supply arguments according to help.                                                                                                 |
| `unsupported_feature`                   | Unsupported op / schemaVersion                                                                             | Check capabilities using `xdoc schema --mode ops --ops <name>` and find an alternative.                                             |
| `invalid_operation`                     | Valid patch cannot apply to this deck (selector matches 0 or >1, layout missing, dimension conflict, etc.) | Check message / `candidates[]` and the target of complete `suggestions[].remediation`.                                              |
| `invalid_package` / `invalid_xml`       | Input package structure or OOXML parsing failed                                                            | Use another source or repair first.                                                                                                 |
| `missing_part` / `missing_relationship` | Input package lacks a part / relationship                                                                  | Use repair-relationships or another file.                                                                                           |
| `encrypted_package` / `signed_package`  | Input is encrypted / signed                                                                                | Remove the password first; handle signed files according to policy.                                                                 |
| `zip_error`                             | ZIP read/write failed                                                                                      | Check file integrity and disk.                                                                                                      |
| `patch_too_large` / `asset_too_large`   | Patch / asset exceeds limit                                                                                | Split the patch; compress assets or adjust `XDOC_PPTX_MAX_*`.                                                                       |
| `input_error` / `input_changed`         | Input path unreadable / input changed during request                                                       | Check path; rerun.                                                                                                                  |
| `output_error` / `output_exists`        | Output write failed / output exists                                                                        | First check publication facts and both paths; overwrite this run's file only with existing authorization, otherwise use a new path. |
| `output_collision`                      | Sidecar or report path conflicts with input/primary output                                                 | Use separate paths; `--overwrite` cannot resolve the conflict.                                                                      |
| `session_conflict`                      | Another daemon session occupies the output                                                                 | Use another path or wait for the session to end.                                                                                    |
| `invalid_sidecar`                       | Sidecar is not `pptx-apply-sidecar/v1`                                                                     | Regenerate the sidecar.                                                                                                             |
| `daemon_unavailable` / `shutting_down`  | Daemon unreachable / shutting down                                                                         | Disable `--daemon-strict` or inspect `XDOC_DAEMON_AUTO_SPAWN` / `XDOC_DAEMON_LOG`.                                                  |
| `internal_error` / `unknown_error`      | Internal error                                                                                             | Report with message.                                                                                                                |
| `resource_*` family                     | Engineering safety budget exceeded (input/ZIP/XML/image/chart slots/timeout/temp disk/output)              | Inspect `details.stage/subject/unit/limit/observed` and address the actual limit.                                                   |

`resource_chart_slots_exceeded` has `stage` `chart` and `unit` `slots`; it limits expanded logical chart slots, not compressed PPTX bytes. Very large sparse point indices, declared point counts, or series/style projections can trigger it even in a small file. Locate the diagnostic `subject` and check source data; correct indices/counts only when input is confirmed wrong, otherwise split or reduce data scope according to user intent. Do not compact valid sparse indices, fill missing values with zero, or repeatedly retry the same file to bypass the limit. Purchasing authorization does not remove engineering limits; runtime configuration can only tighten compiled limits. Read actual limits and configuration bounds from the current schema's `resourcePolicy`; do not treat `XDOC_PPTX_MAX_*` as a universal switch for every `resource_*` limit.

## PNG Preview Output Drift / Stale PNGs

If PNG review shows old content, first confirm the actual output directory of this run's `xdoc convert`. Older xdoc versions tied `-o previews` semantics to filesystem state: when `previews` did not exist it wrote `previews/slide-*.png`; when the directory already existed it could silently write `previews/<deck>-img/slide-*.png`, causing an agent to read PNGs from the previous run.

Current workflow safeguards:

1. Put preview output in the current run directory, e.g. `-o <run-dir>/previews`.
2. Without a trailing separator, `-o <dir>` means `<dir>` is the PNG/multi output root; only `-o <dir>/` with a trailing separator selects parent-directory mode.
3. Before rerendering, clean only the current run's preview root or replace it with `--overwrite`. Do not clean user-owned directories.
4. Before review, confirm the modification times of `contact-sheet.png` and `slide-*.png` belong to this command, and include the actual preview directory and contact sheet path in the completion summary.

## Alias-Aware Fuzzy Repair

For misspelled enum names, suggestions use more than Levenshtein distance and prioritize the **alias table**. The following common spellings automatically yield correct candidates (and `autoRetry=true` directly retries):

| Enum type     | Input (alias / typo)                                                                                                        | Correct suggestion                                                                                                                                          |
| ------------- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `themeColor`  | `accent-1` / `text1` / `background1` / `hyperlink` / `followedHyperlink`                                                    | `accent1` / `dk1` / `lt1` / `hlink` / `folHlink`                                                                                                            |
| `fontFamily`  | `aptos-body` / `aptos-display` / `calibri-body` / `calibri-light` / `times` / `times-new-roman` / `courier` / `noto-cjk-sc` | `Aptos` / `Aptos Display` / `Calibri` / `Calibri Light` / `Times New Roman` / `Courier New` / `Noto Sans CJK SC`                                            |
| `layoutName`  | `Title Slide` / `title` / `section` / `two-column` / `picture-caption`                                                      | `title-slide` / `section-header` / `two-content` / `picture-with-caption` (actual deck layout names still match by literal, case, then kebab normalization) |
| `shapePreset` | All shape aliases (see `pptx catalog shapes`)                                                                               | Canonical preset name (e.g. `rectangel` → `rectangle`)                                                                                                      |

**Implication:** if unsure of a canonical enum name, try an intuitive spelling in dry-run; it will likely yield a repair suggestion with `autoRetry: true` rather than an `unsupported_feature` dead end.

`xdoc schema | jq '.commands.pptx.enumRegistry.fuzzySuggest.examples'` provides actual candidate examples for four kinds of common misspellings for offline comparison.

## Common Errors and Repairs

### 1. Selector Matches Multiple Objects (Most Common)

`error.candidates` provides candidate references such as `shape:12` and `shape:27`; use `select` / `inspect` to read their bounding boxes and text. An available suggestion has `remediation.kind` `replace-request`; its `request` retains the entire original request and changes only the corresponding authored node's selector to a specific id.

Repair:

1. Compare candidate bbox / textPreview to determine the target.
2. Check the suggested request, input, and asset context against the first submission's capsule.
3. Run the generic consumer on this page, dry-run again, then execute the complete replacement request from the original input.

### 2. Selector Matches Nothing

```json
{ "code": "invalid_operation", "message": "shape name 'KPI' not found" }
```

Repair:

1. `xdoc pptx inspect input.pptx --json | jq '.slides[].shapes[] | select(.name | test("KPI"))'`
2. Confirm the name spelling, slide index, and that the shape exists.
3. If the shape is nested in a hierarchy (group), use a broader query selector.

### 3. Layout Cannot Be Selected

```json
{
  "code": "invalid_operation",
  "message": "slide layout not found by name 'custom'. available layouts: [{index:0, name:'Title Slide', type:'title'}, {index:1, name:'Title and Content', type:'obj'}, {index:2, name:'Section Header', type:'secHead'}]"
}
```

Repair: copy a `name` / `type` / `index` from the available layouts embedded in `message` (`candidates` is a string array and is `null` in this case; do not rely on it).

### 4. Incorrect Chart Data Shape

Scatter / bubble incorrectly receives `categories + values`:

```json
{
  "code": "invalid_argument",
  "message": "add-chart has invalid data"
}
```

Repair: use `{ series: [{ name, points: [{x,y}] }] }` for scatter / bubble.

### 5. Asset Path Escapes --asset-root

```json
{ "code": "invalid_argument", "message": "assetSource.path escapes --asset-root" }
```

Repair:

1. Copy the required assets to a dedicated asset directory, preserving the user's originals, and reference them by relative path.
2. Explicitly specify an `--asset-root` covering these assets; when omitted, the root is the patch file's directory, not the process cwd. On POSIX both kinds of root resolve symlink/`..` through the real filesystem; do not lexically collapse paths before invocation. Backslashes are ordinary filename characters. When a wrapper needs an absolute path, resolve actual file identity first. Recheck the asset root when relocating the patch; these rules do not relax asset-relative path boundary checks.
3. Paths are subject to both lexical and actual filesystem boundaries: absolute paths, escaping `..`, escaping symlinks, and directory links outside the root are unavailable. Do not widen the root to the whole home/disk to bypass diagnostics. CLI, daemon, and MCP use the same asset policy; changing transport does not remove constraints.

### 6. Invalid Length Format

The newer runtime distinguishes missing from invalid values: an invalid `add-text-box` length returns `invalid_argument`, `error.path` identifies the field (nested ops retain the actual authored path), `expected` describes explicit units, and `actual` retains the original value. A missing field reports `required field` / `actual: "missing"`. Repair the field using the current report, not old message text. When the runtime does not know the intended unit for a bare number, it provides `remediationUnavailable.reason: "input-required"` instead of an automatically executable replacement. Choose units according to design intent; do not delete the entire op, silently guess units, or treat the hint as authorization for automatic retry. Repair:

| Incorrect                           | Correct                                                                      |
| ----------------------------------- | ---------------------------------------------------------------------------- |
| `"1 inch"`                          | `"1in"`                                                                      |
| `"1.5 in"`                          | `"1.5in"` (remove the space)                                                 |
| `1` / `914400` intended as one inch | `"1in"` (bare numbers are rejected; `in/cm/mm/pt/px/emu` units are required) |

### 6a. Source Guard or Shape Autofit Failure

`invalid_parameter` with `details.field: "/ops/<index>/shape"` and `reason: "unsupported"` means the guard requires a numeric ID rather than name/query; `i18n_source_guard_mismatch` indicates source verification failure. Use the structured fields to inspect/scan the same input; see `../edit/inspect-and-edit.md` for complete rules. Do not remove the guard.

When a nested guarded text edit reports `invalid_argument`, explicitly place the operation in top-level `ops[]`. Native shape autofit measurement can return top-level `invalid_operation` after opResults already show local operation success; local success does not mean the candidate was published. Check top-level status and actual files, retain the report, and repair according to its horizontal, single-column rectangular-box and font-metric boundaries. Do not treat a failed candidate as output.

### 7. Invalid Color Format

```json
{ "code": "invalid_argument", "message": "set-shape has invalid fill" }
```

Repair: CSS color names are unsupported; use hex. `blue` → `"0000FF"`, `red` → `"FF0000"`.

### 8. Unsupported Op / Enum Value

```json
{
  "code": "unsupported_feature",
  "message": "unknown patch op 'add-sparkline'",
  "suggestions": [
    {
      "reason": "Replace /ops/0/op 'add-sparkline' with 'add-slide'.",
      "path": "/ops/0/op",
      "expected": "supported patch op",
      "actual": "add-sparkline",
      "replacement": "add-slide",
      "remediation": {
        "kind": "replace-request",
        "autoRetry": false,
        "confidence": 0.78,
        "...": "..."
      }
    }
  ]
}
```

`unsupported_feature` is reserved for unknown op / schemaVersion. Misspelled chart kinds and enum values return `invalid_argument` (e.g. `add-chart has invalid kind 'bogus-kind'`) with a fuzzy `replace-request` suggestion. ChartEx kinds such as `waterfall`, `funnel`, and `treemap` are now in `enumRegistry.chartKind`. Repair: use the suggestion to find an alternative, or tell the user xdoc does not currently support the feature.

### 9. layout.requiredSlot.missing (DeckKit validate-content)

This comes from the DeckKit's `validate-content.mjs` (layout-contract), not xdoc. The hint in this example is translated into English:

```text
[error] slides[3]: required layout slot "data.eyebrow" is missing or empty
  — The swiss-grid interior-page eyebrow is real short top text; fill it according to the content ...
```

Repair: fill the corresponding slot using the hint at the end of the error (from catalog `layoutContract.slotHints`). A common example is swiss-grid's `data.eyebrow`: it is part of the top layout contract and **required without relaxation**. Version 2.0 displays the entire field; provide genuine short text such as `"Origins"` or `"Design Principles"`. Independent page numbers are calculated by the generator from slide position; old `"P · 04"` input is no longer silently suppressed. For slots without hints, compare and fill from the DeckKit's `assets/examples/deckkits/<deckkit>/content.json`.

## Handling visualRisks[] Warnings

`visualRisks[]` are not errors; they are **potential visual issues**. Each risk looks like:

```json
{
  "code": "text-overflow-estimate",
  "severity": "medium",
  "message": "text is unlikely to fit its box at the current font size",
  "target": { "kind": "shape", "slide": 0, "id": 12, "name": "Title" },
  "detail": "textLength=42 estLines=2 fontPt=44"
}
```

Common risk codes:

| code                           | Meaning                                       | Action                                             |
| ------------------------------ | --------------------------------------------- | -------------------------------------------------- |
| `text-overflow-estimate`       | Text may overflow the shape                   | Enlarge the shape / use `fit-text` / shorten text. |
| `text-unexpected-wrap`         | Expected single-line text has a stranded line | Shorten subtitle/label / widen / change layout.    |
| `chart-label-density-possible` | Chart labels are too dense                    | Change `set-chart.dataLabels[].position` or scale. |
| `table-data-outside-grid`      | Table data exceeds the grid                   | Add rows/columns / adjust data.                    |
| `table-cell-overflow-possible` | Table cell text is too long                   | Widen columns / reduce font size / split rows.     |
| `picture-missing-dimension`    | Added picture lacks w/h                       | Add `w` / `h` fields.                              |
| `ole-icon-missing-or-unsized`  | OLE icon has no explicit size                 | Add `iconW` / `iconH` or confirm the default icon. |

Not every risk necessarily needs action; **let the user decide on minor warnings**. For a presentation to a manager, at least address `text-overflow-estimate`, `text-unexpected-wrap`, and chart/table risks.

## Debugging Tips

### Inspect the Full Trace

```bash
xdoc pptx apply -p patch.json -o out.pptx --dry-run --json --log-level trace 2>&1
```

The dry-run report includes `traces[]` by default (`name` / `status` / `durationMs` for each op). `--log-level trace` additionally writes step-by-step diagnostic logs to stderr, so use `2>&1` or redirect streams separately.

### Use `--explain` to See How to Write an Op

```bash
xdoc pptx apply -p patch.json -i in.pptx --dry-run --explain --json > dry.json
```

This adds `explanations[]` to the dry-run report: each op's one-sentence `summary` and `schema.requiredFields` / `optionalFields` / `fieldNotes` directly identify what the op lacks. It is more focused than `xdoc schema --mode ops --ops <name>` alone because it covers only ops **actually used in the current patch**. See the end of `references/runtime/schema-discovery.md`.

### Bisect the Patch

If a failing op is hard to locate in a large patch:

1. Copy the patch and retain only the first N/2 ops.
2. Dry-run; if there is no error, the failure is in the second half.
3. Continue bisecting to locate it.

### Schema validate

```bash
# Check patch schema with jq separately (basic validation)
jq -e '.schemaVersion == "pptx-patch/v1" and (.ops | type == "array")' patch.json
```

### Sidecar Rollback

If a deck was accidentally damaged:

```bash
xdoc pptx rollback --from-sidecar out.pptx.xdoc.json -o restored.pptx
```

Rollback does not replay any ops: it directly copies the pre-edit input recorded in the sidecar (`strategy: "copy-recorded-input"`); for a sidecar from `new`, it outputs a minimal empty deck (`"minimal-deck"`). The report is `pptx-rollback/v1`; `--from-sidecar` and `-o` are required, and positional arguments are not accepted.

## What Not to Do

- ❌ Do not ignore structured diagnostics or treat `remediation` as authorization; first check the target and current request intent.
- ❌ Do not skip the `--dry-run` report by dismissing warnings — designers care about `visualRisks[]`.
- ❌ Do not rewrite the entire patch without reading `opIndex` — it identifies exactly which operation failed.
- ❌ Do not pretend the task succeeded — if apply repeatedly fails, give the user the complete report to decide the next step.
