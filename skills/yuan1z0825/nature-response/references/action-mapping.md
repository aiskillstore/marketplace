# Action mapping

Use this file to map every reviewer concern to a concrete response action.

## Action labels

| Action label | Meaning | Use when |
|---|---|---|
| `ACCEPT_TEXT` | Revised wording, structure, title, abstract, Methods detail, Discussion, or legend | The author supplied or can supply a text change |
| `ACCEPT_ANALYSIS` | Added or revised analysis | The response depends on real analysis output |
| `ACCEPT_EXPERIMENT` | Added experimental data | The author performed a real experiment and supplied enough detail |
| `ACCEPT_FIGURE` | Added or modified figure, table, panel, legend, or supplement | A visual or tabular item addresses the concern |
| `CLARIFY_EXISTING` | Existing data already address the concern, but manuscript presentation needed clarification | The evidence exists and location can be cited |
| `ADD_CITATION` | Added verified citation | The citation is genuinely relevant and metadata is supplied or flagged |
| `SOFTEN_CLAIM` | Reduced claim strength or added boundary | The original claim was too broad, causal, novel, clinical, or mechanistic |
| `PARTIAL` | Partly addressed with explicit remaining limitation | A valid concern cannot be fully resolved in the revision |
| `DISAGREE` | Respectfully disagree with evidence or scope-based reasoning | The reviewer interpretation is not supported by the manuscript facts |
| `OUT_OF_SCOPE` | Valid suggestion but outside current manuscript scope | The request requires a new cohort, system, longitudinal design, or different study |
| `AUTHOR_INPUT_NEEDED` | Cannot draft final answer without real details | The author note is vague, missing, or unsupported |
| `BLOCKING` | Revision cannot be credible until author action occurs | Missing ethics, compliance, central evidence, integrity explanation, or required data |

## Internal tracker fields

Use this shape internally when organizing a response:

```yaml
comment_id: R1.3
reviewer: Reviewer 1
severity: major
category: methodological
action: ACCEPT_ANALYSIS
author_input_needed: true
readiness: draft_with_placeholders
risk_level: high
manuscript_location: Methods; Results; Supplementary Fig. S2
```

## Readiness state

| State | Meaning |
|---|---|
| `ready_to_submit` | Enough facts are supplied to draft final text with traceable manuscript location |
| `draft_with_placeholders` | Draft can proceed, but placeholders must remain visible |
| `needs_author_input` | Do not draft final wording until author supplies facts |
| `blocked` | Revision response would be misleading or non-credible without author action |

## Risk level

| Risk | Use when |
|---|---|
| `low` | Wording, format, or straightforward clarification |
| `medium` | Citation, figure, method detail, or presentation issue requiring verification |
| `high` | Evidence, statistics, validation, claim strength, or out-of-scope request |
| `blocking` | Ethics, compliance, data integrity, missing central evidence, or unsupported response |

## Mapping rules

- If the author says only "we revised it", use `AUTHOR_INPUT_NEEDED` until the location and nature of the revision are known.
- If the author says "we added an experiment", request experiment name, condition, sample size or replicate unit, result summary, and figure/table location.
- If the author says "we added a citation", request verified bibliographic detail unless already supplied.
- If a reviewer asks for impossible or out-of-scope work, use `PARTIAL` or `OUT_OF_SCOPE` plus claim softening or limitation.
- If a reviewer is factually wrong, usually combine `CLARIFY_EXISTING` with a small text clarification.
- If a central claim remains unsupported, use `SOFTEN_CLAIM` or `BLOCKING`, not confident compliance language.
