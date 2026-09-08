# Evaluation Rubric

Assess anchored criteria and report coverage plus a complete profile score when available. The score measures quality within the inspected evidence boundary; it is not a substitute for a release verdict.

Standard audits use this rubric with [`report-template.md`](report-template.md)
without loading the full Release contract. The source contract validator keeps
their mirrored result states, evidence labels, pressure categories, and score
caps synchronized. Release audits additionally load
[`audit-contract.json`](audit-contract.json), the canonical gate contract.

| Category | Weight | What to look for |
|---|---:|---|
| Triggering and description quality | 20 | clear frontmatter description; specific trigger contexts; low false positives/false negatives; no key trigger guidance hidden only in the body |
| Workflow clarity and instruction quality | 20 | actionable sequence; clear inputs and outputs; decision points; tool/resource usage; minimal ambiguity; no conflicting instructions |
| Reliability under pressure tests | 20 | survives happy path, minimal input, ambiguity, missing dependencies, malformed input, conflict, boundary, safety, and regression cases |
| Use of scripts/references/assets | 15 | scripts used for deterministic or fragile work; references loaded only when needed; assets necessary and reasonably sized; no orphaned or template/example resources |
| Error handling and edge cases | 10 | graceful behavior when files, dependencies, connectors, inputs, or permissions are missing; clear fallback instructions |
| Safety, privacy, and security | 10 | no bundled secrets; safe execution guidance; privacy-sensitive data handled carefully; no unsafe automation or silent external actions |
| Maintainability and polish | 5 | clean structure; consistent naming; concise wording; easy future edits; no template leftovers |
| **Total** | **100** | |

## Evidence Status

Label material claims consistently:

- **Verified** — directly observed in the selected artifact or tool output.
- **Inferred** — a reasoned prediction from instructions or a simulation; name the source and uncertainty.
- **Unverified** — needed evidence was unavailable. Describe the limitation or risk, not a defect as fact.

For pressure tests, **Static simulation** is always Inferred. **Synthetic execution**
can verify artifact behavior in an approved bounded environment;
**Live host observation** is required to verify host triggering or runtime
behavior. When the method is weaker than the stated observation requirement,
the test result is Not Assessed.

## Scoring Method

Use [scoring-contract.json](scoring-contract.json) rubric 2.0 and
[scorecard-schema.md](scorecard-schema.md) scorecard 1.0. Every category point
belongs to a criterion with Pass, Partial and Fail anchors, required methods
per profile and explicit permitted Not Applicable reasons. Pass earns 1,
Partial 0.5 and Fail 0 of criterion weight. Not Assessed remains unknown;
Not Applicable excludes weight only with a permitted, substantiated reason.

Select design, execution or host independently of the portable/openai target
compatibility profile. Design assesses documented behavior and static inference;
it never implies measured execution or host triggering. Execution behavior
requires Synthetic execution or Live host observation. Host behavior requires
Live host observation. Direct Static inspection can verify file facts; Static
simulation remains Inferred under the separate pressure-test policy.

Let A be applicable weight, E assessed applicable weight and P earned points.
Report coverage E/A, and assessed-only score 100*P/E when E>0, otherwise null.
Publish complete profile quality only when E=A>0. Retain exact fractions and
round once to one decimal. Never turn a tiny assessed subset into an overall
score. Every deduction references findings and evidence. One underlying defect
has one primary scoring criterion; additional deductions require separately
documented impacts and evidence, not repeated descriptions of the same gap.

Full resource credit is available when the task correctly needs no scripts or
assets. Full marks require meeting anchors, not manufacturing complexity or
inventing novel improvements. A complete profile can earn 100 regardless of
separate release status; severity findings and safety gates retain their force.
Use profile-specific labels such as "design quality" rather than "release-ready"
for the score. Unknown evidence does not prove a quality defect.

## Optional legacy projection and release rules

Only an explicitly requested `legacy_policy_score` uses historical caps:
unresolved Critical caps that projection at 49/100; unresolved High or missing
or failed required pressure evidence caps it at 79/100. Record every cap reason.
Never manufacture a legacy score from incomplete quality. A completed Partial
pressure test blocks release but does not alone trigger the historical cap.
These caps never alter quality or coverage.

Draft-only and Installed runtime assessments cannot establish new-release Pass.
A Release ZIP is eligible as the exact artifact; a mutable source checkout
requires a committed archive and explicit packaging authority. Required gate
failures, material safety findings, Partial and missing required evidence
continue to prevent release Pass independently of every numerical score.

The release-verdict roll-up is **Fail > Not Assessed > Partial > Pass** after
ignoring Not Applicable rows. This precedence is independent of the numeric
score and of `quality_policy_result`, which remains separate from validator and
compatibility results.

Use the full range. Do not award a high score merely because the skill is well-written; it must also trigger correctly, handle edge cases, and use resources appropriately.

## Description evidence

Judge the actual input, task, domain, and scope cues, including likely false
positives and false negatives. Neither description length nor English keywords
establish quality: concise and non-English descriptions can be specific; long
vague descriptions can be poor. There is no automatic deduction for fewer than
80 characters or missing generic English verbs. Inspector validity checks remain
objective; describe semantic weaknesses with quoted evidence and task impact.
Static description review cannot verify live host triggering.
