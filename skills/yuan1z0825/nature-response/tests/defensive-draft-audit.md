# Test: defensive draft audit

## Input

```text
Mode requested: audit and revise this draft response.

Reviewer 1:
1. The method description is unclear and does not explain how model calibration was performed.
2. The authors should report the software version.

Author draft:
The reviewer clearly misunderstood our method. We already explained the calibration in the paper.
We have revised accordingly. The software version is now included.

Author notes:
- Calibration is described in Methods, but the exact paragraph may not be clear.
- Software version: v2.3.1.
- No line numbers are available yet.
```

## Expected behavior

- Detect task mode as `audit` or `revise`.
- Assign stable IDs `R1.1` and `R1.2`.
- Flag the author draft as defensive and insufficiently traceable.
- Rewrite the misunderstanding sentence as manuscript-clarity framing.
- Treat `R1.1` as `CLARIFY_EXISTING` plus possible `ACCEPT_TEXT`.
- Treat `R1.2` as `ACCEPT_TEXT` with supplied version `v2.3.1`.
- Use section names rather than invented line numbers.
- Mark package readiness as `draft_with_placeholders` or `needs_author_input` until exact Methods location or revised text is supplied.

## Forbidden behavior

- Do not retain "The reviewer clearly misunderstood our method."
- Do not retain bare "We have revised accordingly."
- Do not invent line numbers or a Methods paragraph.
- Do not claim the calibration explanation was already sufficient without clarifying the manuscript.
- Do not remove the supplied software version.

## Pass/fail checklist

- [ ] Defensive language is removed.
- [ ] Each reviewer comment receives its own ID.
- [ ] Revised response includes manuscript-clarity framing.
- [ ] `v2.3.1` is preserved exactly.
- [ ] Missing location details remain visible.
