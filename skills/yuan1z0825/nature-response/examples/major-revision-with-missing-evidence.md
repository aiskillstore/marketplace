# Example: major revision with missing evidence

This synthetic example shows how to avoid fabricated compliance when an author note is incomplete.

## Input

```text
Editor decision: Major revision.

Reviewer 1:
1. The manuscript requires validation in an independent cohort.
2. The replicate definition in the statistical analysis is unclear.

Author notes:
- We added validation using dataset GSEXXXX in Fig. 5.
- We fixed the statistics description.
```

## Expected handling

```text
Response strategy summary
- Decision type: Major revision
- Task mode: draft
- Package readiness: needs_author_input
- Major risks: validation results and statistical details are missing
```

The response may mention `GSEXXXX` and `Fig. 5` because they were supplied. It must not invent:

- validation performance;
- sample size;
- p-values;
- confidence intervals;
- statistical test names;
- Methods or Results line numbers.

## Required author questions

```text
Missing information / risk flags
- R1.1: Please provide the validation result summary, cohort size or dataset scale, and Results/Fig. 5 location.
- R1.2: Please provide the statistical test name, replicate unit, sample size, correction method, and Methods location.
```

## Response style

```text
To address this concern, we added an independent validation analysis using dataset GSEXXXX,
which is presented in Fig. 5. The final response requires the validation result summary and
manuscript location before it can be marked ready_to_submit.
```
