# Paper type: algorithmic or device

A procedure, tool, or system is proposed; the paper must show it performs reliably and advantageously.

## Argument chain

`task definition + scope -> what the system is -> why it works (design rationale) -> how well it works (evaluation) -> ablations isolating the contribution -> failure modes + cost characteristics -> applicability boundary`

## Drafting rules

- Separate "what the system is" from "why it works" from "how well it works." Do not braid them. A common failure is mixing design rationale with evaluation results in the same paragraph.
- Every performance claim must specify dataset, metric, baseline, and conditions. Bare numbers do not survive review.
- Avoid marketing verbs (`leverages`, `enables`, `empowers`) unless they carry concrete information.
- The Discussion must name the failure modes the experiments revealed, not only the wins. Reviewers trust papers that report their own limits.

## Module / pipeline writing

For module-level writing (each component of a pipeline), open `references/method.md` for:

- the three-element pattern (motivation, mechanism, evidence)
- module-motivation templates
- overview-template for the pipeline figure caption + first paragraph
