# Iteration Bundle: team-frontend-review

- decision: `keep_current`
- winner label: `Current`
- winner changed: `False`
- next action: Keep the current description and open a new candidate only when fresh route evidence appears.

## Cause Tags

- `no_candidate_outperformed_current`
- `current_holdout_risk`

## Gate Status

| Gate | Pass |
| --- | --- |
| `visible_holdout_non_regression` | True |
| `blind_holdout_non_regression` | True |
| `judge_blind_non_regression` | True |
| `judge_blind_agreement` | True |
| `adversarial_non_regression` | True |
| `adversarial_risk_ok` | True |
| `route_confusion_clean` | True |
| `family_stability` | True |

## Candidate Registry

| Role | Label | Ranking State | Promotion State | Tokens | Dev Errors | Holdout Errors |
| --- | --- | --- | --- | ---: | ---: | ---: |
| baseline | `Baseline` | reference | reference | 52 | 3 | 0 |
| current | `Current` | selected_by_dev | kept_current | 50 | 3 | 0 |
| candidate | `Guardrail` | not_selected | blocked | 62 | 3 | 0 |
| candidate | `Balanced` | not_selected | blocked | 64 | 3 | 0 |
| candidate | `Artifact Aware` | not_selected | blocked | 84 | 3 | 0 |
| candidate | `Boundary` | not_selected | blocked | 90 | 3 | 0 |

## Human Review Stub

- target: team-frontend-review
- current description: Review frontend code for accessibility, UI security, missing states, and UX regressions. Use when asked to review React components, run a pre-merge frontend review, or check a11y and unsafe rendering.
- candidate description: Review frontend code for accessibility, UI security, missing states, and UX regressions. Use when asked to review React components, run a pre-merge frontend review, or check a11y and unsafe rendering.
- review focus: no_candidate_outperformed_current, current_holdout_risk

## Artifact Paths

- skill: `examples/team-frontend-review/generated-skill/SKILL.md`
- optimization_report: `examples/team-frontend-review/optimization/reports/description_optimization.json`
- promotion_decisions: `reports/promotion_decisions.json`
- candidate_registry: `reports/candidate_registry.json`
- regression_cause_taxonomy: `references/regression-cause-taxonomy.md`
- human_review_template: `references/human-review-template.md`
