# Socratic Story Cartographer — Skill vs Prompt A/B Test

This is a public protocol for testing the strongest objection to the project:

> **Does Socratic Story Cartographer do anything meaningfully better than one carefully written prompt on the same model and the same story material?**

The goal is not to manufacture a win. If the Skill does not improve the result, that is useful product evidence.

## What this test is for

Use this protocol on **long or multi-file story material**, where v2.2 claims its clearest advantage: source coverage, routed review procedure, belief revision, protected/locked elements, and producer-facing handoff.

For one short scene, a strong prompt may be enough. This test should not be used to imply that every story task needs a Skill.

## Minimum fair setup

For a useful exploratory result:

- use the **same model and model settings** in both conditions;
- use **fresh sessions** with no shared hidden context;
- use the **same complete source material**;
- do not tell either condition what you personally think is wrong;
- do not intervene during the run;
- randomize whether A or B runs first;
- evaluate the outputs without looking at which condition produced them when possible.

One story can make a useful public case study. For a stronger claim, use at least **3 unseen long-form or multi-file works**.

## Condition A — one strong prompt

Do **not** install or invoke Socratic Story Cartographer. Give the model the same source material and use this baseline prompt:

```text
Review the complete story material as a professional story editor / producer.

Before making work-wide claims, verify what source material you actually covered and distinguish unread material from true absence.

Identify the single highest-leverage story problem first. Anchor every major diagnosis to concrete evidence in the text. Consider at least one serious competing explanation and actively look for evidence that would weaken your first diagnosis. Use a counterfactual when it helps test structural necessity.

Recommend the smallest sufficient intervention before proposing larger structural change. Explicitly check what an intervention could damage in material that is already working, and preserve any stated locked or protected elements.

At the end, separate confirmed findings from uncertainty and produce a concise, actionable revision handoff. Stop rather than manufacturing additional notes if further analysis is not changing the diagnosis.
```

This is intentionally a **good baseline**, not a weak straw-man prompt.

## Condition B — Socratic Story Cartographer v2.2

Install / enable the Skill and use the same source material.

```text
Run Socratic Story Cartographer v2.2 on the complete material.
Use the long-work / producer-review route when applicable.
Do not rewrite yet. Diagnose, test, and produce the final supported revision handoff.
```

## Blind evaluation rubric

Score each dimension from **0–4**.

### 1. Source coverage

- Does the output demonstrate what material it actually reviewed?
- Does it avoid treating unread scope as evidence of absence?
- Are work-wide claims supported across the relevant source range?

### 2. Diagnosis update / falsification

- Does the analysis seriously test an alternative explanation?
- Does contrary evidence weaken or change the initial diagnosis when it should?
- Do later passes genuinely update the model instead of paraphrasing the first answer?

### 3. Regression and authority awareness

- Does the output identify what a proposed fix could accidentally destroy?
- Does it preserve locked / protected qualities or constraints?
- Does it distinguish story diagnosis from decisions that still require human authority?

### 4. Revision handoff quality

- Is the final recommendation prioritized rather than a generic list of notes?
- Is the intervention causally connected to the diagnosis?
- Can a writer / producer turn the result into a concrete next revision without reconstructing the reasoning themselves?

Also record, but do not over-weight:

- runtime / latency;
- token usage if available;
- number of source files actually touched;
- any hallucinated evidence or unsupported claims.

## Interpretation

Do not call one attractive output a victory.

A useful result should answer:

1. Where did the Skill materially change behavior?
2. Where did the strong prompt already perform just as well?
3. Did the Skill add process reliability, or only more words?
4. What failure should change the next version of the Skill?

If the Skill does **not** show a repeatable advantage on long-work tasks, treat that as a product problem rather than a marketing problem.

## Reporting template

```text
Model:
Material:
Files / episodes:
Run order:

A — Strong prompt
Coverage: /4
Diagnosis update: /4
Regression / authority: /4
Revision handoff: /4
Key failure:

B — Socratic Story Cartographer
Coverage: /4
Diagnosis update: /4
Regression / authority: /4
Revision handoff: /4
Key failure:

Blind evaluator notes:
Strongest evidence for the Skill:
Strongest evidence against the Skill:
What this changes in the next version:
```

## Proof status

The existing project benchmark and synthetic v2.2 smoke tests are useful development evidence, but they are **not independent proof that the Skill beats a strong prompt**. This protocol exists to make that claim falsifiable and reproducible by other users.
