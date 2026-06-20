# Frontend Review Description Optimization

Winner: `Current`

- current tokens: `50`
- winner tokens: `50`
- baseline tokens: `52`

## Winner

Review frontend code for accessibility, UI security, missing states, and UX regressions. Use when asked to review React components, run a pre-merge frontend review, or check a11y and unsafe rendering.

## Candidate Ranking

| Candidate | Tokens | Dev FP | Dev FN | Dev Near | Holdout FP | Holdout FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Current` | 50 | 0 | 3 | 1.0 | 0 | 0 |
| `Guardrail` | 62 | 0 | 3 | 1.0 | 0 | 0 |
| `Balanced` | 64 | 0 | 3 | 1.0 | 0 | 0 |
| `Artifact Aware` | 84 | 0 | 3 | 1.0 | 0 | 0 |
| `Boundary` | 90 | 0 | 3 | 1.0 | 0 | 0 |

## Acceptance Gates

| Gate | Winner FP | Winner FN | Current FP | Current FN | Baseline FP | Baseline FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Holdout | 0 | 0 | 0 | 0 | 0 | 0 |
| Blind Holdout | 0 | 0 | 0 | 0 | 0 | 0 |
| Judge Blind Holdout | 0 | 0 | 0 | 0 | 0 | 0 |
| Adversarial Holdout | 0 | 0 | 0 | 0 | 0 | 0 |

## Calibration

| Gate | Winner Gap | Winner Risk | Winner Boundary Rate | Current Gap | Baseline Gap |
| --- | ---: | --- | ---: | ---: | ---: |
| Holdout | 0.285 | tight | 0.167 | 0.285 | 0.278 |
| Blind Holdout | 0.088 | tight | 0.333 | 0.088 | 0.082 |
| Adversarial Holdout | 0.509 | healthy | 0.0 | 0.509 | 0.519 |

## Judge Blind Summary

| Gate | Winner Agreement | Winner Mean Confidence | Current Agreement | Baseline Agreement |
| --- | ---: | ---: | ---: | ---: |
| Judge Blind Holdout | 1.0 | 0.703 | 1.0 | 1.0 |

## Family Health

| Gate | Winner Clean Families | Winner Weakest Family | Current Clean Families | Baseline Clean Families |
| --- | --- | --- | --- | --- |
| Holdout | 6/6 | security_and_a11y (0 errors) | 6/6 | 6/6 |
| Blind Holdout | 6/6 | blind_premerge (0 errors) | 6/6 | 6/6 |
| Judge Blind Holdout | 6/6 | blind_premerge (0 errors) | 6/6 | 6/6 |
| Adversarial Holdout | 6/6 | adversarial_quality_gate_review (0 errors) | 6/6 | 6/6 |

## Selection Logic

Ordered by:
- fewest false positives
- fewest false negatives
- highest near-neighbor pass rate
- highest negative pass rate
- highest precision
- highest recall
- shortest description
