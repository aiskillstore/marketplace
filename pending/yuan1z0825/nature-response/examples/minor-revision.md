# Example: minor revision response package

This synthetic example shows the expected output shape for a minor revision. It is not based on
real reviewer comments.

## Input

```text
Editor decision: Minor revision.

Reviewer 1:
1. Please define cross-domain calibration in the Introduction.
2. Figure 2 legend does not explain the colour scale.

Author notes:
- Cross-domain calibration means adjusting the model output across datasets with different feature distributions.
- We added a definition in the Introduction.
- We revised the Figure 2 legend to define the colour scale.
- No line numbers are available.
```

## Expected response strategy summary

```text
Response strategy summary
- Decision type: Minor revision
- Task mode: draft
- Package readiness: draft_with_placeholders
- Overall posture: Cooperative and concise
- Major risks: line numbers are not available
- Suggested ordering: Reviewer 1 comments in order
```

## Expected tracker

```markdown
| ID | Reviewer concern | Type | Severity | Proposed action | Readiness | Missing author input |
|---|---|---|---|---|---|---|
| R1.1 | Define cross-domain calibration | Editorial / presentation | Minor | ACCEPT_TEXT | draft_with_placeholders | Line or section location |
| R1.2 | Explain Figure 2 colour scale | Editorial / figure | Minor | ACCEPT_FIGURE | draft_with_placeholders | Line or legend location |
```

## Response style

```text
We agree that the original Introduction did not define this term clearly. We have revised the
Introduction to define cross-domain calibration as adjustment of model output across datasets with
different feature distributions. This change appears in the Introduction [location].
```

Do not invent line numbers.
