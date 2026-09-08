# Release Report Extension

Load only for Release. Append to the Standard decision and evidence report.
Keep every safety finding, limitation, pressure record, and scorecard attachment.
The full G01–G23 matrix below is mandatory for each canonical profile.

## Release artifact and provenance evidence

- New-release eligibility: exact artifact / packaging source with an archive built from a committed revision and explicit packaging authority / installed-state evidence only / ineligible
- Required artifact-role evidence and whether it is satisfied:
- Independent evaluator pins and schema: complete-tree SHA-256; candidate SHA-256; optional inspector SHA-256; exact inspector schema version 6 / exact `v2.0.0` schema 5 to 6 bootstrap transition / Not Assessed with reason
- Independent evidence class: independent schema match / bootstrap transition evidence; the latter never counts as an independent schema-6 pass and is not reusable after `v2.0.0`
- Independent evaluator result: pass / fail / not_assessed / Not Applicable; report all canonical-profile results and trust/sandbox limitations
- Skill Forge runtime manifest archive integrity: Pass / Fail / Not Assessed / Not Applicable
- Skill Forge local source proof: Pass / Fail / Not Assessed / Not Applicable; name the caller-selected repository and do not imply remote or signer authenticity
- Runtime-manifest digest binding: Pass / Fail / Not Assessed / Not Applicable
- Canonical archive and manifest SHA-256 values, when applicable:

## 3. Release Gate Review (when applicable)

Consult `../references/audit-contract.json` and `../references/release-gate-checklist.md`. Keep `validator_outcome`, `gate_result`, `compatibility_result`, and `quality_policy_result` separate. Use exactly these gate and quality-policy results: Pass / Fail / Partial / Not Assessed / Not Applicable. A Not Applicable result requires a rationale. Repeat the complete G01–G23 matrix and release verdict independently for every selected canonical profile. The five rows below are an executive roll-up only.

### Per-profile results

| Requested surface | Canonical profile | Compatibility result | Release verdict | Evidence / limitation |
|---|---|---|---|---|
|  |  | Compatible / Incompatible / Unverified / Not Applicable | Pass / Fail / Partial / Not Assessed |  |

**Overall cross-profile verdict:** Pass / Fail / Partial / Not Assessed — derive from the per-profile verdicts without changing or hiding any member result.

Use **Fail > Not Assessed > Partial > Pass** after ignoring Not Applicable rows
for both per-profile and overall release-verdict roll-ups. If every row is Not
Applicable, use Not Assessed.

### Executive summary

| Group | Gates | Result | Concise evidence / blocker |
|---|---|---|---|
| Structure and metadata | G01–G08 | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| Validation evidence | G09–G12 | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| Package safety and content | G13–G19 | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| Pressure tests and remediation | G20–G21 | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| Score, verdict, and runtime package | G22–G23 | Pass / Fail / Partial / Not Assessed / Not Applicable |  |

### Authoritative gate matrix

| ID | Gate | Result | Evidence, scope, and rationale when Not Applicable |
|---|---|---|---|
| G01 | Exactly one `SKILL.md` exists | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G02 | Selected-target required frontmatter fields | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G03 | Selected-profile package root shape | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G04 | Selected-target name rule when required or supplied | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G05 | Trigger-rich description | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G06 | Documented description or listing limit | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G07 | Conditional OpenAI UI metadata | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G08 | Valid platform-specific frontmatter | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G09 | Skill Forge strict inspection with complete coverage and stated evaluator provenance/schema | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G10 | Validator outcome mapped to gate result | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G11 | Approved package self-tests, separately reported | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G12 | Skill Forge source-only tests and extracted-runtime tests after evaluator/script changes | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G13 | Referenced resources present | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G14 | No orphaned/generated/template leftovers | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G15 | No bundled secrets or credential-like files | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G16 | No unsafe archive or direct-folder findings | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G17 | Bundled-script safety review | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G18 | No unnecessary large assets | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G19 | Known target product upload limit or N/A rationale | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G20 | Pressure coverage and behavioral results | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G21 | Severity-ranked fixes documented | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G22 | Counts, scorecard, caps, severity list, and verdict reconcile | Pass / Fail / Partial / Not Assessed / Not Applicable |  |
| G23 | Skill Forge canonical runtime-manifest, source-proof, profile, and extracted-runtime package verification | Pass / Fail / Partial / Not Assessed / Not Applicable |  |

**Required-gate counts:** Pass: 0; Fail: 0; Partial: 0; Not Assessed: 0; Not Applicable: 0; Applicable: 0.

**Release gate verdict:** Pass / Fail / Partial / Not Assessed — concise explanation. Derive it with Fail > Not Assessed > Partial > Pass after ignoring Not Applicable rows. Only Pass is release-ready. A required applicable Partial, Fail, or Not Assessed result is not a pass. For G09 in a Skill Forge self-audit, an incompatible independent-inspector schema is Not Assessed, never Pass, except for the exact `v2.0.0` schema 5 to 6 path when every `independent_evaluator_policy.bootstrap_transition` requirement passes. Label that result bootstrap transition evidence, not an independent schema-6 pass, and never reuse it after `v2.0.0`. For G10, use `validator_outcome_gate_results`: unavailable optional validation is Not Applicable, unavailable required validation is Not Assessed, and an execution error is Not Assessed. Only Artifact Fail may establish a validator-derived defect. For G11, a missing optional self-test plan is Not Applicable. G23 applies only to Skill Forge Release ZIP and Mutable source checkout roles. Local source proof does not establish remote or signer authenticity. See `../references/validator-evidence.md` and `../references/runtime-manifest-schema.md`.
