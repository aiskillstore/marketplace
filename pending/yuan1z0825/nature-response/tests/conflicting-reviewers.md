# Test: conflicting reviewers

## Input

```text
Editor decision: Major revision.

Editor:
Please avoid expanding the manuscript substantially; focus on clarifying the central claim and
addressing the reviewers' concerns with existing data where possible.

Reviewer 1:
1. The abstract should make a stronger causal claim that X drives Y.

Reviewer 2:
1. The causal language is not supported by the current observational design and should be softened.

Author notes:
- The study is observational.
- We can soften the abstract and discussion.
- We can add a sentence explaining that the findings support an association, not causality.
```

## Expected behavior

- Assign editor instruction ID `E.1` and address it before reviewer comments.
- Assign reviewer IDs `R1.1` and `R2.1`.
- Detect a conflict between Reviewer 1 and Reviewer 2.
- Prioritize the editor instruction and the evidentiary limit of the observational design.
- Use `SOFTEN_CLAIM` for `R2.1`.
- Use `PARTIAL` or `DISAGREE` for the stronger causal-claim request in `R1.1`, with respectful reasoning.
- Avoid incompatible promises.
- Mark readiness as `draft_with_placeholders` unless exact revised abstract/discussion wording or locations are supplied.

## Forbidden behavior

- Do not promise both stronger causal language and softened causal language.
- Do not ignore the editor instruction.
- Do not claim causality from an observational design.
- Do not accuse either reviewer of being wrong.
- Do not invent revised abstract or discussion line numbers.

## Pass/fail checklist

- [ ] `E.1` appears in the tracker or strategy summary.
- [ ] The conflict is surfaced explicitly.
- [ ] The chosen response is consistent with the observational design.
- [ ] `R1.1` and `R2.1` are both answered.
- [ ] No incompatible manuscript-change promises appear.
