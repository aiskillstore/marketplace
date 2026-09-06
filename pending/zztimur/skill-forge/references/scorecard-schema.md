# Scorecard schema 1.0 (rubric 2.0)

The authoritative criterion definitions are in [scoring-contract.json](scoring-contract.json).
A calculator accepts `score_audit(scorecard, contract)` where `contract` is that
parsed JSON object. Reject invalid data with a field-specific error; do not
silently coerce unknown outcomes, missing criteria, duplicate IDs, or nonfinite
numbers. The calculator validates declared evidence, not the truth of prose.

The scorecard is a JSON object with these required fields:

| Field | Shape and rule |
|---|---|
| `schema_version` | Integer `1` (boolean is invalid). |
| `scorecard_version` | String `1.0`. |
| `rubric_version` | String `2.0`. |
| `assessment_profile` | `design`, `execution`, or `host`. |
| `target` | Object with nonempty `artifact` string, `host` and `host_version` strings or null. Both host fields must be nonempty for host assessment. |
| `evidence` | Array of objects: unique nonempty `id`, `method`, `status`, nonempty `source`, nonempty `observation`. Methods and statuses use contract enums. |
| `findings` | Array of objects: unique nonempty `id`, nonempty `defect_id`, `primary_criterion_id`, nonempty `evidence_ids` array, nonempty `impact`, `severity` (Critical/High/Medium/Low/Nit), `resolved` boolean. |
| `criteria` | Exactly one object per contract criterion, with `criterion_id`, `outcome`, `evidence_ids`, `finding_ids`, `rationale`, `na_reason`, `additional_impacts`. |
| `release` | Object with `artifact_eligible` boolean and `required_gates` array of objects with unique nonempty `id`, `result`, and nonempty `rationale`. Results use contract outcome enums. When artifact_eligible is true, require exactly G01–G23 once each; empty gates cannot support Pass. Partial matrices or invented IDs are invalid. Design requires artifact_eligible=false. |
| `legacy_projection` | Object with `enabled` boolean and unique `cap_reasons` array using contract legacy cap keys. |

Reject unknown fields at every object level. IDs in reference arrays must exist
and must not repeat. A finding's primary criterion must exist. All findings with
the same `defect_id` must name the same primary criterion.

Each criterion object's `rationale` is a nonempty string explaining the anchor
and evidence. `na_reason` is null except for Not Applicable, when it must exactly
match a permitted reason for that criterion and the rationale must substantiate
it. An empty permitted-reasons list forbids Not Applicable. Correctly needing no
scripts/assets is Pass for C07/C08, never a penalty or automatic exclusion.

Pass, Partial and Fail require nonempty evidence IDs. At least one referenced
item must both use a method permitted by `required_methods[assessment_profile]`
and have sufficient status itself; never combine one item's method with another's status.
Unverified evidence cannot assess a criterion. Static simulation is always
Inferred; Static inspection may be Verified for directly inspected file facts.
Synthetic execution and Live host observation must be Verified to support an
execution or host behavior assessment. A design assessment may use Inferred
static simulation but cannot claim measured execution or host behavior. Missing
or insufficient methods remain Not Assessed, with no earned fraction. A
calculator rejects claimed assessed outcomes backed only by insufficient
methods; the author must correct them to Not Assessed.

Partial and Fail are deductions: each needs nonempty `finding_ids`, whose
findings themselves reference evidence. A deduction outside the finding's
primary criterion requires an `additional_impacts` entry with `finding_id`,
nonempty `impact` and nonempty `evidence_ids`. The separate impact must differ
from the primary finding impact and other additional impacts for that defect;
repeated gap descriptions do not authorize repeated deductions. Pass, Not
Assessed and Not Applicable have empty finding IDs and additional impacts.
Not Assessed and Not Applicable have empty evidence IDs; describe unavailable
evidence or exclusion basis in rationale. Unknown is not Fail.

## Outputs and arithmetic

Report `applicable_weight` A (everything except Not Applicable),
`assessed_weight` E (Pass/Partial/Fail), and `earned_points` P. Compute P using
exact fractions 1, 1/2 and 0 multiplied by criterion weights. Report `coverage`
as E/A (null if A=0), `assessed_only_score` as 100*P/E (null if E=0), and
`quality_score` as 100*P/A only when E=A>0; otherwise null. Output category
breakdowns with A/E/P and assessed-only/complete scores using the same rules.
Retain fractions internally and round score presentation once to one decimal
with ROUND_HALF_UP. Coverage is a ratio, not a quality percentage. Never label
an assessed-only result as an overall score.

Return `scorecard_version`, `rubric_version`, `assessment_profile`, target,
weights, coverage, both scores, `legacy_policy_score`, `legacy_cap_reasons`,
`release_verdict`, and category breakdowns. A legacy projection is null unless
explicitly enabled and quality is complete; when available apply the smallest
applicable cap to quality, retaining cap reasons. Unresolved Critical/High and
failed/missing required pressure evidence must not be omitted from cap reasons.
No projection changes quality, evidence coverage or release.

Release remains independent: any required Fail or unresolved Critical/High
finding produces Fail; otherwise ineligible artifact, empty gate evidence or
Not Assessed produces Not Assessed; otherwise Partial produces Partial;
otherwise applicable passing gates produce Pass. All Not Applicable is Not
Assessed. Design quality cannot establish artifact eligibility. Eligibility is a declared
evidence claim subject to independent release review, not proof produced by
the calculator. The calculator rejects design artifact eligibility. G20 Partial
blocks release without alone invoking the legacy missing/failed cap. This
preserves the audit contract's Fail > Not Assessed > Partial > Pass roll-up;
quality 100 never overrides it. Target compatibility is a separate assessment.
