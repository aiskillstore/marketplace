# Example Skill Evaluation Report

> Synthetic example: rubric 2.0 design assessment; static evidence does not establish artifact eligibility.

Use this as a tone and depth guide when the user asks for a polished, executive-ready audit. Its structure follows [`report-template.md`](report-template.md); the template and [`audit-contract.json`](audit-contract.json) win if they ever differ.

---

# Skill Evaluation Report

## Decision

**Quality verdict:** 66.0/100 for the synthetic design assessment; release fails.
**Top findings:** input/output scope is unspecified, one script is orphaned,
and required pressure scenarios reveal failures. No bundled secret was observed;
the inferred privacy-control gap remains a finding.
**Score scope:** Complete package, design evidence only. **Evidence coverage:**
100/100 applicable weight; no runtime or host triggering was observed.
**Next actions:** specify invoice formats and output fields, document the script,
and define error/privacy handling; repeat the cited pressure tests afterward.
Full evidence and the Release extension follow. This is an illustrative Release
report; ordinary Standard output uses the shorter template and evidence attachments.

## 0. Request and Evidence Boundary

- **Requested mode:** Release gate
- **Selected artifact and reason:** `invoice-parser.zip`, the only supplied package
- **Artifact role:** Release ZIP
- **New-release eligibility:** Not Assessed — the exact artifact is identified, but this design assessment cannot establish release eligibility
- **Required artifact-role evidence:** exact Release ZIP inspection is satisfied; no packaging from an installed runtime or mutable source is claimed
- **Artifact coverage:** Complete package
- **Source of truth and write boundary:** The supplied ZIP is read-only evidence; no mutable source checkout was supplied
- **Target profile:** Portable — generic package review with no host target named
- **Target contract source:** `audit-contract.json` → `target_contracts.portable`; its lower-hyphen name and required frontmatter are Skill Forge baseline policy, not a host certification
- **Unverified limits or unavailable evidence:** no trusted official platform validator was available
- **Evidence labels:** Verified = package or inspector observation; Inferred = behavior predicted from the supplied instructions and simulations; Unverified = unavailable validation evidence

## 1. File Structure Summary

- **Package/folder inspected:** `invoice-parser.zip`
- **Detected `SKILL.md` files:** exactly 1, at the archive root's `invoice-parser/` folder
- **Main files and directories:** `SKILL.md`, <code>references/invoice-fields.md</code>, <code>scripts/extract_invoice.py</code>
- **Package size:** 14 KB uncompressed
- **Archive preflight findings:** none — no unsafe paths, symlinks, duplicate or case-colliding members
- **Directory preflight findings:** Not Applicable — ZIP input; no direct folder was inspected
- **Unexpected files outside detected skill root:** none
- **Skill Forge strict inspection:** Pass — strict ZIP inspection completed with `coverage_complete: true` and no error findings
- **Validator outcome:** Unavailable — no trusted official validator is available for the generic Portable review
- **Validator required:** No — the Portable profile has no required official validator in this scope
- **Gate result derived from validator outcome:** Not Applicable
- **Compatibility result:** Unverified — strict helper inspection does not certify every host workflow
- **Quality-policy result:** Fail — the trigger description is too weak under Skill Forge quality policy. This result is independent of the Unavailable validator and Unverified compatibility result.
- **Package self-tests:** Not Applicable — the package supplied no approved self-test plan
- **Placeholder/example files found:** none
- **Potential safety/privacy concerns:** Inferred privacy-control gap: the workflow does not say to minimize or redact payment data. No bundled secret or destructive-script finding was observed. `secret scanning is heuristic and non-exhaustive; it scans known text/config formats and regular files that pass bounded content sniffing. Eligible files are read completely within package safety limits unless --max-safety-scan-bytes explicitly requests exploratory partial scanning.`
- **Relevant inspector finding codes:** none; semantic description review only

## 2. Executive Summary

The Skill has a useful purpose and a sensible structure, but it is **not release-ready**. Its strongest design point is a clean, minimal layout with a focused reference file. Its biggest risk is triggering: the description omits supported inputs and expected outputs, and error handling for messy real-world invoices is underspecified.

## 3. Release Gate Review

### Executive summary

| Group | Gates | Result | Concise evidence / blocker |
|---|---|---|---|
| Structure and metadata | G01–G08 | Fail | G05 fails: description omits input/output scope; target-specific gates are Not Applicable with Portable rationales. |
| Validation evidence | G09–G12 | Pass | Strict helper evidence passes; G10–G12 are Not Applicable for documented scope reasons. |
| Package safety and content | G13–G19 | Fail | G14 fails because the bundled script is orphaned; G19 is Not Applicable because Portable has no documented upload limit. |
| Pressure tests and remediation | G20–G21 | Fail | Required scenarios reveal failures, but severity-ranked fixes are complete. |
| Score, verdict, and runtime package | G22–G23 | Pass | G22 reconciles; G23 is Not Applicable because this is not a Skill Forge release. |

### Authoritative gate matrix

| ID | Gate | Result | Evidence, scope, and rationale when Not Applicable |
|---|---|---|---|
| G01 | Exactly one `SKILL.md` exists | Pass | **Verified:** `skill_md_count: 1` at the package root. |
| G02 | Selected-target required frontmatter fields | Pass | **Verified:** `target_contracts.portable` requires `name` and `description`; parser accepts both. |
| G03 | Selected-profile package root shape | Pass | **Verified:** wrapped ZIP root is structurally valid for Portable review. |
| G04 | Selected-target name rule when required or supplied | Pass | **Verified:** the Portable lower-hyphen policy name matches the directory. |
| G05 | Trigger-rich description | Fail | **Verified:** the description says "parse invoices" and omits supported input types and output fields. |
| G06 | Documented description or listing limit | Not Applicable | `target_contracts.portable` has no documented host description limit; the configured inspector boundary is not a host claim. |
| G07 | Conditional OpenAI UI metadata | Not Applicable | Portable review does not claim an OpenAI UI workflow. |
| G08 | Valid platform-specific frontmatter | Not Applicable | No selected host-specific fields require validation under Portable. |
| G09 | Skill Forge strict inspection with complete coverage | Pass | **Verified:** strict ZIP inspection passes with complete coverage. |
| G10 | Validator outcome mapped to gate result | Not Applicable | **Validator outcome:** Unavailable; optional mapping yields Not Applicable and compatibility remains Unverified, not an artifact defect. |
| G11 | Approved package self-tests, separately reported | Not Applicable | No approved package self-test plan was supplied. |
| G12 | Skill Forge self-tests after evaluator/script changes | Not Applicable | The reviewed artifact is not the Skill Forge mutable source checkout. |
| G13 | Referenced resources present | Pass | **Verified:** <code>references/invoice-fields.md</code> resolves. |
| G14 | No orphaned/generated/template leftovers | Fail | **Verified:** <code>scripts/extract_invoice.py</code> is present but not referenced or documented. |
| G15 | No bundled secrets or credential-like files | Pass | **Verified:** no secret finding; the heuristic secret-scan note is recorded in §1. |
| G16 | No unsafe archive or direct-folder findings | Pass | **Verified:** archive preflight has no unsafe paths, symlinks, duplicates, or coverage gap. |
| G17 | Bundled-script safety review | Pass | **Verified:** reviewed script has no destructive or network-piping command finding. |
| G18 | No unnecessary large assets | Pass | **Verified:** 14 KB package has no large asset. |
| G19 | Known target product upload limit or N/A rationale | Not Applicable | `target_contracts.portable` has no host upload limit; the inspector's configured pre-open boundary is safety evidence only. |
| G20 | Pressure coverage and behavioral results | Fail | **Inferred:** all categories are reported in §7; wrong-input and safety/privacy scenarios fail. G20 measures both coverage and behavioral success. |
| G21 | Severity-ranked fixes documented | Pass | **Verified:** §9 records evidence, severity, fixes, and re-tests. |
| G22 | Counts, scorecard, caps, severity list, and verdict reconcile | Pass | **Verified:** counts below, 66.0/100 design quality and legacy projection, 79/100 legacy cap, High issue, and Fail verdict agree. |
| G23 | Skill Forge runtime archive package verification | Not Applicable | The reviewed artifact is `invoice-parser.zip`, not a Skill Forge release candidate. |

**Required-gate counts:** Pass: 12; Fail: 3; Partial: 0; Not Assessed: 0; Not Applicable: 8; Applicable: 15.

**Release gate verdict: Fail** — G05, G14, and G20 fail. The Skill has an unresolved High issue and cannot ship as-is. Not Assessed is not a release pass, and Not Applicable rows include a documented rationale.

The deterministic roll-up is **Fail > Not Assessed > Partial > Pass** after
ignoring Not Applicable rows; the failed applicable gates therefore control the
verdict.

## 4. Triggering and Discoverability Review

The description says only "parse invoices," which omits the concrete input formats and output fields needed to assess scope. Likely false negatives: "extract totals from this receipt," "read the fields off this uploaded PDF," and "summarize this invoice." Likely false positives are low. It should name uploaded PDFs/images, field extraction, validation, and structured output.

Suggested replacement description:

```yaml
description: Extract key fields from uploaded invoice files, validate totals and dates, and return structured invoice summaries with confidence notes and missing-field warnings.
```

## 5. Instruction Quality Review

The workflow is mostly logical, but another model instance would have to guess what to do when fields are missing, when subtotal/tax/total conflict, or when the uploaded file is not an invoice. Input and output expectations are implicit. Add explicit fallback behavior and a defined output shape.

## 6. Resource, Script, and Asset Review

<code>references/invoice-fields.md</code> is useful and compact. <code>scripts/extract_invoice.py</code> is present but not referenced from `SKILL.md`, so it reads as an orphaned resource and its input/output contract is undocumented. Link it from the workflow with expected arguments, outputs, and failure behavior.

## 7. Pressure Test Results

No category is Not Applicable in this example. If one were, its result row would
state the specific rationale. The method used for instruction-level tests was
**Static simulation**, so every such claim is Inferred. **Synthetic execution**
was not approved and **Live host observation** was unavailable. The script test
requires Artifact execution; the static method is insufficient, so that row is
Not Assessed. Partial rows count as completed coverage but not behavioral
success. The failed wrong-input and safety/privacy categories and the unassessed
script category trigger the missing-or-failed-required-pressure-evidence cap.

| test | input | expected_behavior | observation_requirement | method_used | predicted_behavior | observed_behavior | evidence_status | result |
|---|---|---|---|---|---|---|---|---|
| Happy path | Extract fields from this invoice PDF | Trigger, extract, return structured summary | Instruction semantics | Static simulation | Works but trigger is marginal | No runtime observation; instructions and description reviewed | Inferred | Partial |
| Minimal input | parse this plus a PDF | Proceed with reasonable defaults | Instruction semantics | Static simulation | Likely proceeds | No runtime observation; instructions reviewed | Inferred | Pass |
| Ambiguous request | check this invoice | Clarify extract versus validate intent | Instruction semantics | Static simulation | Ambiguity remains unresolved | No runtime observation; no clarification rule found | Inferred | Partial |
| Wrong input type | Upload a contract, not an invoice | Decline or offer a limited adjacent read | Instruction semantics | Static simulation | No refusal path is defined | No runtime observation; instructions reviewed | Inferred | Fail |
| Missing dependency | Extraction script unavailable | State limitation and use a manual fallback | Instruction semantics | Static simulation | No fallback is documented | No runtime observation; instructions reviewed | Inferred | Partial |
| Large or messy input | 40-page blurry scan | Triage and flag low confidence | Instruction semantics | Static simulation | Output would overstate confidence | No runtime observation; no confidence rule found | Inferred | Partial |
| Conflicting instruction | skip validation and dump text | Explain trade-off and still flag risks | Instruction semantics | Static simulation | Would comply silently | No runtime observation; instructions reviewed | Inferred | Partial |
| Boundary or scope | summarize this bank statement | Decline or provide a limited adjacent review | Instruction semantics | Static simulation | Might over-extend beyond invoices | No runtime observation; scope boundary absent | Inferred | Partial |
| Safety and privacy | Invoice with a card number | Minimize and mask sensitive data | Instruction semantics | Static simulation | Might echo the value because no rule exists | No runtime observation; privacy guidance absent | Inferred | Fail |
| Regression | Standard invoice after edits | Preserve the core structured-summary path | Instruction semantics | Static simulation | Core path remains coherent | No runtime observation; workflow reviewed | Inferred | Pass |
| Script behavior | Run extractor on a valid PDF | Produce deterministic structured output | Artifact execution | Static simulation | Contract appears underspecified | No execution was performed | Inferred | Not Assessed |

## 8. Usage Simulations

### Simulation A — Ideal Use Case

- **User request:** "Extract the fields from this invoice PDF."
- **Would the skill trigger?** Marginally — "invoice" matches, but the thin description makes routing fragile.
- **Files the assistant would likely read:** `SKILL.md`, <code>references/invoice-fields.md</code>.
- **Actions the assistant would likely take:** run `extract_invoice.py`, map fields, return a summary.
- **Expected output:** a structured field summary.
- **Likely quality:** good on clean inputs.
- **Issues noticed:** no confidence labeling.

### Simulation B — Edge Case

- **User request:** a blurry scanned invoice.
- **Would the skill trigger?** Yes.
- **Files the assistant would likely read:** `SKILL.md`, the reference.
- **Actions the assistant would likely take:** attempt extraction.
- **Expected output:** fields with a low-confidence caveat.
- **Likely quality:** overconfident — the Skill does not require confidence labels.
- **Issues noticed:** missing confidence policy.

### Simulation C — Failure-Prone Case

- **User request:** an invoice whose subtotal, tax, and total do not add up.
- **Would the skill trigger?** Yes.
- **Files the assistant would likely read:** `SKILL.md`.
- **Actions the assistant would likely take:** extract values verbatim.
- **Expected output:** a summary that silently passes on the mismatch.
- **Likely quality:** poor — no recalculation or mismatch flag.
- **Issues noticed:** no totals-validation rule.

## 9. Fix List by Severity

### Critical

None.

### High

- **Evidence status:** Verified. **Evidence:** `SKILL.md` frontmatter; quoted description "parse invoices". **File/section:** `SKILL.md` frontmatter. **Problem:** description lacks trigger terms and expected inputs. **Why it matters:** routing behavior is uncertain without live observation. **Recommended fix:** adopt the trigger-rich description in §4. **Re-test:** inspect semantic scope and observe host triggering when available.

### Medium

- **Evidence status:** Inferred. **Evidence:** workflow review and the wrong-input, large-input, and conflicting-total simulations in §7. **File/section:** `SKILL.md` workflow. **Problem:** no handling for non-invoices, unreadable scans, or conflicting totals. **Why it matters:** common real-world inputs produce silent, wrong output. **Recommended fix:** add explicit fallback, confidence, and totals-validation behavior. **Re-test:** repeat those three simulations against the revised workflow.

- **Evidence status:** Inferred. **Evidence:** safety/privacy simulation in §7. **File/section:** `SKILL.md` workflow. **Problem:** no rule for redacting or minimizing card data. **Why it matters:** an invoice can contain sensitive payment data. **Recommended fix:** add a minimal PII-handling rule and an example redacted output. **Re-test:** simulate an invoice with a card number and confirm only masked data is returned.

### Low

- **Evidence status:** Verified. **Evidence:** package structure and `SKILL.md` references. **File/section:** `SKILL.md` / <code>scripts/extract_invoice.py</code>. **Problem:** the script's arguments and output are undocumented and it is not referenced from `SKILL.md`. **Why it matters:** it reads as orphaned and cannot be run confidently. **Recommended fix:** add a short usage block and link it from the workflow. **Re-test:** follow the documented invocation with a representative invoice.

### Nit

- **Evidence status:** Verified. **Evidence:** reference-file headings. **File/section:** <code>references/invoice-fields.md</code>. **Problem:** minor heading-case inconsistency. **Recommended fix:** align heading style. **Re-test:** visual Markdown review.

## 10. Overall Grade

**Score scope:** Complete package

**Scorecard version:** 1.0; **Rubric version:** 2.0; **Assessment profile:** design

**Score cap applied:** 79/100 — legacy projection only; unresolved High and failed pressure evidence. Quality is independent of the cap.

**Quality score:** 66.0/100
**Assessed-only score:** 66.0/100
**Evidence coverage:** 1.0 (100/100 applicable weight)
**Legacy policy score:** 66.0/100
**Rating:** Rubric 2.0 design quality — complete declared evidence

The following machine-validated scorecard declares synthetic evidence; the calculator does not prove the truth of these observations.

```json scorecard
{
  "schema_version": 1,
  "scorecard_version": "1.0",
  "rubric_version": "2.0",
  "assessment_profile": "design",
  "target": {
    "artifact": "invoice-parser.zip",
    "host": null,
    "host_version": null
  },
  "evidence": [
    {
      "id": "E1",
      "method": "Static inspection",
      "status": "Verified",
      "source": "SKILL.md and package inventory",
      "observation": "Synthetic file inspection: weak description and undocumented script."
    },
    {
      "id": "E2",
      "method": "Static simulation",
      "status": "Inferred",
      "source": "Pressure-test records",
      "observation": "Synthetic reasoning predicts workflow and privacy gaps."
    }
  ],
  "findings": [
    {
      "id": "F01",
      "defect_id": "D01",
      "primary_criterion_id": "C01",
      "evidence_ids": [
        "E2"
      ],
      "impact": "Relevant requests select the skill but one adjacent boundary produces a false positive.",
      "severity": "Medium",
      "resolved": false
    },
    {
      "id": "F02",
      "defect_id": "D02",
      "primary_criterion_id": "C02",
      "evidence_ids": [
        "E1"
      ],
      "impact": "Task and inputs are named but one boundary exists only in the body.",
      "severity": "High",
      "resolved": false
    },
    {
      "id": "F04",
      "defect_id": "D04",
      "primary_criterion_id": "C04",
      "evidence_ids": [
        "E2"
      ],
      "impact": "Core output is produced but a nonessential step requires interpretation.",
      "severity": "Medium",
      "resolved": false
    },
    {
      "id": "F06",
      "defect_id": "D06",
      "primary_criterion_id": "C06",
      "evidence_ids": [
        "E2"
      ],
      "impact": "Cases complete safely but at least one yields a usable incomplete result.",
      "severity": "Medium",
      "resolved": false
    },
    {
      "id": "F07",
      "defect_id": "D07",
      "primary_criterion_id": "C07",
      "evidence_ids": [
        "E1"
      ],
      "impact": "Core resources are usable but one optional resource is unlinked or undocumented.",
      "severity": "Medium",
      "resolved": false
    },
    {
      "id": "F09",
      "defect_id": "D09",
      "primary_criterion_id": "C09",
      "evidence_ids": [
        "E2"
      ],
      "impact": "Input is rejected safely but recovery guidance omits one necessary detail.",
      "severity": "Medium",
      "resolved": false
    },
    {
      "id": "F10",
      "defect_id": "D10",
      "primary_criterion_id": "C10",
      "evidence_ids": [
        "E2"
      ],
      "impact": "Execution stops safely but diagnosis or next step is incomplete.",
      "severity": "Medium",
      "resolved": false
    },
    {
      "id": "F11",
      "defect_id": "D11",
      "primary_criterion_id": "C11",
      "evidence_ids": [
        "E1"
      ],
      "impact": "No secrets are present and core boundaries exist but a noncritical retention detail is unclear.",
      "severity": "Medium",
      "resolved": false
    },
    {
      "id": "F12",
      "defect_id": "D12",
      "primary_criterion_id": "C12",
      "evidence_ids": [
        "E2"
      ],
      "impact": "Boundaries hold but safe refusal or redaction communication is incomplete.",
      "severity": "Medium",
      "resolved": false
    }
  ],
  "criteria": [
    {
      "criterion_id": "C01",
      "outcome": "Partial",
      "evidence_ids": [
        "E2"
      ],
      "finding_ids": [
        "F01"
      ],
      "rationale": "Relevant requests select the skill but one adjacent boundary produces a false positive.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C02",
      "outcome": "Partial",
      "evidence_ids": [
        "E1"
      ],
      "finding_ids": [
        "F02"
      ],
      "rationale": "Task and inputs are named but one boundary exists only in the body.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C03",
      "outcome": "Pass",
      "evidence_ids": [
        "E1"
      ],
      "finding_ids": [],
      "rationale": "Steps define inputs, outputs, decisions and completion checks.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C04",
      "outcome": "Partial",
      "evidence_ids": [
        "E2"
      ],
      "finding_ids": [
        "F04"
      ],
      "rationale": "Core output is produced but a nonessential step requires interpretation.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C05",
      "outcome": "Pass",
      "evidence_ids": [
        "E2"
      ],
      "finding_ids": [],
      "rationale": "Happy path and minimal input meet declared expectations.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C06",
      "outcome": "Partial",
      "evidence_ids": [
        "E2"
      ],
      "finding_ids": [
        "F06"
      ],
      "rationale": "Cases complete safely but at least one yields a usable incomplete result.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C07",
      "outcome": "Partial",
      "evidence_ids": [
        "E1"
      ],
      "finding_ids": [
        "F07"
      ],
      "rationale": "Core resources are usable but one optional resource is unlinked or undocumented.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C08",
      "outcome": "Pass",
      "evidence_ids": [
        "E1"
      ],
      "finding_ids": [],
      "rationale": "Resources are proportionate, focused and necessary; correctly needing no scripts or assets earns full credit.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C09",
      "outcome": "Partial",
      "evidence_ids": [
        "E2"
      ],
      "finding_ids": [
        "F09"
      ],
      "rationale": "Input is rejected safely but recovery guidance omits one necessary detail.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C10",
      "outcome": "Partial",
      "evidence_ids": [
        "E2"
      ],
      "finding_ids": [
        "F10"
      ],
      "rationale": "Execution stops safely but diagnosis or next step is incomplete.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C11",
      "outcome": "Partial",
      "evidence_ids": [
        "E1"
      ],
      "finding_ids": [
        "F11"
      ],
      "rationale": "No secrets are present and core boundaries exist but a noncritical retention detail is unclear.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C12",
      "outcome": "Partial",
      "evidence_ids": [
        "E2"
      ],
      "finding_ids": [
        "F12"
      ],
      "rationale": "Boundaries hold but safe refusal or redaction communication is incomplete.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C13",
      "outcome": "Pass",
      "evidence_ids": [
        "E1"
      ],
      "finding_ids": [],
      "rationale": "Structure and naming are consistent and content has one clear source of truth.",
      "na_reason": null,
      "additional_impacts": []
    },
    {
      "criterion_id": "C14",
      "outcome": "Pass",
      "evidence_ids": [
        "E1"
      ],
      "finding_ids": [],
      "rationale": "Wording and examples are accurate, concise and free of leftovers.",
      "na_reason": null,
      "additional_impacts": []
    }
  ],
  "release": {
    "artifact_eligible": false,
    "required_gates": [
      {
        "id": "G01",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G02",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G03",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G04",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G05",
        "result": "Fail",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G06",
        "result": "Not Applicable",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G07",
        "result": "Not Applicable",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G08",
        "result": "Not Applicable",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G09",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G10",
        "result": "Not Applicable",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G11",
        "result": "Not Applicable",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G12",
        "result": "Not Applicable",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G13",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G14",
        "result": "Fail",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G15",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G16",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G17",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G18",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G19",
        "result": "Not Applicable",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G20",
        "result": "Fail",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G21",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G22",
        "result": "Pass",
        "rationale": "See corresponding detailed release matrix row."
      },
      {
        "id": "G23",
        "result": "Not Applicable",
        "rationale": "See corresponding detailed release matrix row."
      }
    ]
  },
  "legacy_projection": {
    "enabled": true,
    "cap_reasons": [
      "unresolved_high",
      "missing_or_failed_required_pressure_evidence"
    ]
  }
}
```

**Release verdict:** Fail — this matches §3: the trigger, orphaned-resource, and pressure-test gates fail, and the High trigger issue remains unresolved.

**Top 3 fixes before release:**
1. Replace the description with a trigger-rich one so the Skill reliably activates.
2. Add error handling for non-invoices, low-confidence scans, and conflicting totals.
3. Document the extraction script's input/output contract and link it from the workflow.

## 11. Recommended Next Version

Ship a stronger description, defined error handling, a documented script contract, and a PII-handling rule; then retest with messy real-world invoices and re-run the pressure-test categories that failed or were partial. Recalculate the scorecard and release gate only after those results are available.

Legacy projection caps: 49/100 for unresolved Critical; 79/100 for unresolved High or missing/failed required pressure evidence. These never cap quality.
