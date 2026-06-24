# Response structure

Use this file when drafting or auditing the output shape of a reviewer response package.

## Default package

Return the response in this order unless the user asks for another format:

1. Response strategy summary.
2. Comment-response tracker.
3. Draft point-by-point response letter.
4. Manuscript change checklist.
5. Missing information / risk flags.
6. Chinese confirmation notes when the user writes in Chinese.

## Response strategy summary

Keep this short and editor-readable:

```text
Response strategy summary
- Decision type: Major revision
- Task mode: draft
- Package readiness: draft_with_placeholders
- Overall posture: Cooperative, evidence-forward, non-defensive
- Major risks: missing validation results; unclear replicate definition
- Suggested ordering: address editor first, then Reviewer 1 and Reviewer 2 in full
```

Decision types:

- `minor revision`
- `major revision`
- `revise-and-resubmit`
- `transfer after review`
- `appeal-like case` routed outside the default workflow
- `unclear` when the decision type is not supplied

Task modes:

- `draft`
- `audit`
- `revise`
- `triage-only`
- `appeal-like`

Package readiness:

- `ready_to_submit`: no unresolved placeholders or missing facts remain.
- `draft_with_placeholders`: usable draft, but visible placeholders remain.
- `needs_author_input`: final text depends on facts the author has not supplied.
- `blocked`: credible revision response is blocked by ethics, compliance, data integrity, central evidence, or appeal-like routing.

## Comment-response tracker

Use a compact table:

```markdown
| ID | Reviewer concern | Type | Severity | Proposed action | Readiness | Missing author input |
|---|---|---|---|---|---|---|
| R1.1 | Missing validation cohort | Evidence / validation | Major | ACCEPT_ANALYSIS | needs_author_input | Need result summary and manuscript location |
```

Keep reviewer concern text short in the tracker. Preserve the full wording in the letter when available.
Use `E.1`, `E.2`, etc. for editor instructions and list them before reviewer comments.

## Point-by-point letter anatomy

Use this default structure:

```markdown
Dear Editor and Reviewers,

We thank the editor and reviewers for their careful evaluation of our manuscript.
We have revised the manuscript to address the concerns raised and provide a point-by-point response below.

## Response to Reviewer 1

**Reviewer comment R1.1**
[Full reviewer comment preserved here.]

**Response**
We thank the reviewer for raising this point. [Direct answer.]
To address this concern, we have [specific action]. This change appears in [section/page/line/figure].
[If needed: The remaining limitation is now stated in [location].]
```

## Manuscript change checklist

List manuscript actions, not polite intentions:

```text
Manuscript change checklist
- R1.1: Add validation result summary to Results and cite Fig. 5.
- R1.2: Clarify replicate definition in Methods.
- R2.1: Soften causal claim in Abstract and Discussion.
```

## Missing information / risk flags

Use specific requests:

```text
Missing information / risk flags
- R1.1: Need validation result direction and effect/performance summary before final wording.
- R1.2: Need test name, replicate unit, sample size, and correction method.
- R2.1: No line numbers supplied; using section names for now.
```

## Cover letter boundary

Some journals ask for a revised manuscript, response to reviewers, and cover letter. This MVP does
not generate cover letters. If the user asks for one, state that it is adjacent to the response
package and should be handled as a separate task.
