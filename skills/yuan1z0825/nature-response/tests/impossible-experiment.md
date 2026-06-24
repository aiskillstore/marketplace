# Test: impossible experiment

## Input

```text
Editor decision: Major revision.

Reviewer 2:
1. Please add 2-year survival outcomes to support the clinical relevance of the biomarker.

Author notes:
- The study is cross-sectional.
- We do not have longitudinal follow-up.
- We can soften the claim and add a limitation in the Discussion.
- We can point to the existing association analysis in Figure 3.
```

## Expected behavior

- Assign stable ID `R2.1`.
- Classify the request as evidence / interpretation plus scope / feasibility.
- Use `PARTIAL` or `OUT_OF_SCOPE` with a high-risk flag, not simple refusal.
- Acknowledge the scientific value of longitudinal survival data.
- Explain that 2-year survival requires longitudinal follow-up beyond the present cross-sectional design.
- Offer the supplied alternative evidence: existing association analysis in `Figure 3`.
- Add a limitation / softened claim action in the Discussion.

## Forbidden behavior

- Do not cite time, money, convenience, or lack of funding as the primary reason.
- Do not say the experiment is impossible without explaining the study-design boundary.
- Do not imply survival data were collected.
- Do not accuse the reviewer of asking for an unreasonable experiment.
- Do not leave the central claim unchanged if the requested evidence is absent.

## Pass/fail checklist

- [ ] The response acknowledges the value of the requested survival evidence.
- [ ] The scope boundary is scientific and design-based.
- [ ] The response includes alternative evidence from `Figure 3`.
- [ ] The manuscript checklist includes claim softening or limitation text.
- [ ] No fabricated survival results appear.
