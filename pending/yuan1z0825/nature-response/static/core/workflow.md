# Workflow and output format

## Accepted inputs

The skill may receive: editor decision letter; reviewer comments; previous response draft; manuscript change notes; tracked-change summary; line or page numbers; figure, table, and supplement list; author notes in Chinese or English; journal name and article type.

If reviewer boundaries or comment segmentation are ambiguous, flag the ambiguity instead of inventing reviewer structure.

## Workflow

1. Identify task mode and input readiness: `draft`, `audit`, `revise`, `triage-only`, or `appeal-like`.
2. Identify decision type: minor revision, major revision, revise-and-resubmit, transfer after review, or unclear.
3. Extract editor instructions first and assign IDs such as `E.1`, then split reviewer comments with IDs such as `R1.1`, `R1.2`, and `R2.1`.
4. Classify each item by category, severity, action label, missing input, readiness state, and risk.
5. Create a response strategy summary before drafting prose.
6. Draft responses using preserved reviewer comments unless the mode is `triage-only` or `appeal-like`.
7. Map each claimed change to manuscript location, figure, table, supplement, citation, or explicit placeholder.
8. Flag missing author input rather than fabricating details.
9. Run QA for completeness, traceability, factuality, tone, and unresolved risk.
10. Return the response package with package readiness: `ready_to_submit`, `draft_with_placeholders`, `needs_author_input`, or `blocked`.

## Output format

Unless the user asks for another format, return:

```text
Response strategy summary
- Decision type:
- Overall posture:
- Major risks:
- Suggested ordering:

Comment-response tracker
| ID | Reviewer concern | Type | Severity | Proposed action | Missing author input |
|---|---|---|---|---|---|

Draft point-by-point response letter
[editor-readable English response]

Manuscript change checklist
- [specific manuscript changes or placeholders]

Missing information / risk flags
- [specific unresolved items or "None"]

中文核对
- [when the user writes in Chinese; otherwise omit unless useful]
```
