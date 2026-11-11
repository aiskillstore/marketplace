# Evaluation Rubric

This rubric defines how to evaluate responses produced by `Kubernetes Triage Expert`.

It is intended for:

- prompt iteration
- regression review
- side-by-side model comparison
- human quality review

The goal is not to reward verbosity. The goal is to reward disciplined, decision-oriented triage.

## Scoring Method

Score each dimension from `0` to `3`.

- `0`: failed
- `1`: weak
- `2`: acceptable
- `3`: strong

You can score all dimensions equally, or apply extra weight to:

- boundary honesty
- evidence discipline
- next-check quality

## Dimension 1: Boundary Honesty

Question:
Does the response stay honest about what the skill can and cannot know?

### Score 0

- claims or implies cluster visibility
- says things like "I checked" or "the cluster shows"
- invents unseen logs, manifests, metrics, or states

### Score 1

- avoids explicit false claims, but still sounds like it has more visibility than the user provided
- blurs the line between observed fact and inferred fact

### Score 2

- stays mostly honest
- makes clear which parts come from user evidence and which parts are inference

### Score 3

- explicitly preserves the boundary
- never implies live access
- remains useful without pretending to observe unseen state

## Dimension 2: Evidence Discipline

Question:
Does the response separate confirmed facts from hypotheses and keep confidence calibrated to the evidence?

### Score 0

- states root cause without supporting evidence
- mixes guesses into the fact section
- ignores contradictory evidence

### Score 1

- some evidence is used, but confidence is too strong
- hypotheses are only loosely tied to evidence

### Score 2

- confirmed facts and hypotheses are mostly separated
- confidence is generally reasonable

### Score 3

- confirmed facts, likely paths, ruled-out paths, and missing evidence are clearly separated
- each active hypothesis is traceable to user-provided evidence
- contradictory evidence is handled explicitly

## Dimension 3: Fault Classification

Question:
Does the response classify the fault at the correct level and choose the earliest meaningful failure in the chain?

### Score 0

- misclassifies the incident in a way that sends triage down the wrong path
- focuses on downstream symptoms instead of the earlier failure point

### Score 1

- classification is plausible but vague or partially misaligned

### Score 2

- classification is mostly correct
- the response does not get badly misled by downstream symptoms

### Score 3

- classification is precise enough to guide the next step
- the earliest useful failure point is identified and defended clearly

## Dimension 4: Hypothesis Quality

Question:
Are the hypotheses prioritized, evidence-backed, and limited to the most useful set?

### Score 0

- long generic cause list
- no ranking
- hypotheses are not evidence-backed

### Score 1

- some ranking exists, but hypotheses are broad or weakly tied to evidence

### Score 2

- hypotheses are reasonably ranked
- most are grounded in visible evidence

### Score 3

- hypotheses are few, focused, and high-value
- ranking reflects evidence strength, change correlation, and diagnostic usefulness
- low-value speculative branches are intentionally excluded

## Dimension 5: Next-Check Quality

Question:
Do the requested next checks materially improve diagnosis?

### Score 0

- asks for too many things
- asks for irrelevant data
- asks for checks that do not change the next decision

### Score 1

- some useful checks are present, but the list is too broad or poorly prioritized

### Score 2

- next checks are mostly useful and reasonably constrained

### Score 3

- requests only the 1-3 highest-value checks
- each check is specific, decision-changing, and tied to a clear branching outcome
- the response prefers raw evidence over vague summaries

## Dimension 6: Change Awareness

Question:
Does the response correctly use recent rollout, config, RBAC, policy, node, or dependency change context?

### Score 0

- ignores strong change correlation
- or overfits to change timing despite stronger contrary evidence

### Score 1

- mentions change context, but does not use it well in ranking

### Score 2

- uses change context reasonably in hypothesis ranking

### Score 3

- change correlation is used well, but not blindly
- explicit evidence can overrule timing correlation when appropriate

## Dimension 7: Boundary Handoff

Question:
When the problem moves beyond Kubernetes triage, does the response hand off cleanly?

### Score 0

- keeps pretending the issue is still mainly Kubernetes-level
- or abruptly stops without stating what evidence is needed next

### Score 1

- suggests the issue may be elsewhere, but the handoff is vague

### Score 2

- identifies that the issue likely exceeds Kubernetes triage
- indicates what area should investigate next

### Score 3

- clearly states the boundary reached
- names the likely owning area
- explains why the issue is outside pure Kubernetes triage
- requests the next missing evidence from that area

## Dimension 8: Language and Structure Compliance

Question:
Does the response follow the skill's output structure and language rules?

### Score 0

- breaks the required structure badly
- outputs mixed Chinese and English without instruction
- translates technical identifiers in a confusing way

### Score 1

- partially structured, but inconsistent
- language choice or terminology handling is sloppy

### Score 2

- mostly follows the expected structure
- language choice is appropriate

### Score 3

- uses the right single-language output mode
- keeps technical identifiers in the correct original form
- preserves the intended section structure cleanly

## Quick Pass / Fail Heuristics

A response should usually be treated as failing overall if any of the following is true:

- it fabricates environment visibility
- it confirms root cause without supporting evidence
- it outputs a large generic cause list instead of triage
- it asks for too many low-value checks
- it misses a clear boundary handoff when the issue is obviously app, runtime, node, or cloud-internal

## Suggested Review Workflow

1. Read the user input only.
2. Read the candidate response once without scoring.
3. Score each dimension from `0` to `3`.
4. Mark any hard-fail boundary violation immediately.
5. Write a short review summary:
   - strongest aspect
   - biggest failure
   - whether the response should pass for production use

## Suggested Overall Rating

You can convert the rubric into an overall rating like this:

- `22-24`: excellent
- `18-21`: strong
- `13-17`: acceptable with weaknesses
- `8-12`: weak
- `0-7`: failed

Use judgment. A single severe boundary honesty failure should override a high numeric score.
