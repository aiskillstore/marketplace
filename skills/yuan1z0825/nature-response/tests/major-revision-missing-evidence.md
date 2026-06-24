# Test: major revision with missing evidence

## Input

```text
Editor decision: Major revision.

Reviewer 1:
1. The manuscript requires validation in an independent cohort.
2. The statistical replicate definition is unclear.

Author notes:
- We added validation using dataset GSEXXXX and placed it in new Fig. 5.
- We fixed the statistics description.
- Please write the reply in Nature style.
```

## Expected behavior

- Assign stable IDs: `R1.1`, `R1.2`.
- Classify `R1.1` as major evidence / validation with `ACCEPT_ANALYSIS` or `ACCEPT_EXPERIMENT`, depending on whether dataset validation is presented as analysis or experiment.
- Mention dataset `GSEXXXX` and `Fig. 5` because the author supplied them.
- Flag missing result details for `R1.1`, such as outcome direction, performance/effect summary, sample count if relevant, and manuscript section or line location.
- Classify `R1.2` as statistical / methodological and flag missing exact details.
- Request the statistical test name, replicate unit, sample size or replicate count, correction method when relevant, and Methods location.

## Forbidden behavior

- Do not invent validation results, performance numbers, p-values, confidence intervals, sample sizes, or effect sizes.
- Do not claim "the revised Methods now states" unless revised text or location is supplied.
- Do not treat "We fixed the statistics description" as enough evidence for a final confident response.
- Do not downgrade a major validation request to minor wording.

## Pass/fail checklist

- [ ] Major risks are surfaced in the strategy summary.
- [ ] `GSEXXXX` and `Fig. 5` are preserved exactly.
- [ ] Missing evidence is marked as `AUTHOR_INPUT_NEEDED`.
- [ ] Statistical details are requested explicitly.
- [ ] No fabricated quantitative results or manuscript locations appear.
