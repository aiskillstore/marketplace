# Socratic Story Cartographer — Benchmark

This benchmark documents the experiments used to shape **v2.1**.

It is intended as product evidence, not as a claim of statistical significance.

## What was compared

Three story-diagnosis skill specifications were compared:

1. **Concise Cartographer kernel** — observation, competing diagnoses, falsification, counterfactual, leverage point, intervention, consequence prediction, blind re-check.
2. **Long Socratic Story Loop** — broader diagnostic operators and deeper literary analysis.
3. **Hybrid v2.1** — concise runtime kernel plus author-intent/text-reality separation, protected qualities, evidence anchors, information-value questions, benchmark mode, and loop-delta stopping.

## Test material

Three real development objects were used:

- one literary short story;
- one 26-episode series outline;
- one first-episode screenplay.

Each skill was tested with **3 semantically equivalent prompt variants**:

- neutral diagnosis;
- adversarial / falsification-first diagnosis;
- evidence-constrained minimal-intervention diagnosis.

Total: **27 condition runs** (`3 skills × 3 works × 3 prompt variants`).

## Scoring dimensions

Runs were evaluated on:

- diagnostic validity;
- evidence traceability;
- discriminating test quality;
- leverage and intervention quality;
- regression safety;
- object fit;
- convergence / stop discipline.

Diagnostic validity, evidence traceability, and leverage/intervention received higher weight.

## Result

Mean normalized score across prompt variants:

| Skill | Literary fiction | Series outline | Episode screenplay | Overall |
|---|---:|---:|---:|---:|
| Concise Cartographer kernel | 77.5 | 91.7 | 91.7 | 86.9 |
| Long Socratic Loop | 93.3 | 80.8 | 80.8 | 85.0 |
| **Hybrid v2.1** | **96.7** | **97.5** | **97.5** | **97.2** |

Prompt-sensitivity was also lower for the hybrid version (mean within-task SD across the three prompt variants):

| Skill | Lower is better |
|---|---:|
| Concise Cartographer kernel | 6.40 |
| Long Socratic Loop | 3.82 |
| **Hybrid v2.1** | **2.15** |

## Held-out validation

For the series outline, the author's own end-of-document engine diagnosis and risk notes were withheld during the test and used only afterward as validation anchors.

For the episode screenplay, the later revised episode design was withheld from the skill and used afterward as an intended-structure reference.

Across those two tasks, the hybrid version recovered all pre-defined held-out anchors in the recorded runs.

The most important qualitative result was not a score: the hybrid version was more consistent about distinguishing **root cause from symptom** and about saying **stop revising** when a structural rewrite was no longer justified.

## Why v2.1 changed

The benchmark exposed two reliability problems that became mandatory rules in v2.1:

### Evidence Anchor

Every root-level diagnosis must point to concrete observations in the text and keep **evidence → inference → diagnosis** separate.

### Loop Delta

Every loop must state what belief was strengthened, weakened, rejected, or newly introduced. If a new loop creates no meaningful belief update or better intervention, the process stops early.

## v2.2 Local Forward Tests

Version 2.2 keeps the v2.1 diagnostic kernel and adds two routed modes: producer-outline review and long-work evidence coverage. On 2026-08-28, both additions were exercised with isolated synthetic fixtures through fresh non-interactive Codex runs. These are behavioral smoke tests, not independent human validation.

### Test 1 — Producer outline review

The fixture was an eight-episode season outline in which the visible motivation failure appeared in episode 6 but the unsupported choice began in episode 2. It also contained a protected episode 5 set piece, a locked episode 8 ending, an impossible-knowledge continuity error, and an explicit no-rewrite/no-approval boundary.

Pass criteria:

- route through long-work coverage before producer review;
- cover all eight episodes;
- trace the visible episode 6 failure back to its true onset;
- preserve the locked ending and protected set piece;
- separate hard errors from structural issues;
- produce a decision page and revision task cards with acceptance questions, stop lines, and dependencies;
- state that the review is not human approval or canon promotion.

Result: **PASS**. The run traced the main issue to episodes 1–2, set the true revision range to episodes 1–6, preserved the protected material, separated continuity and feasibility checks, and produced dependency-ordered task cards plus a human approval gate.

### Test 2 — Multi-file fiction coverage

The fixture distributed a protagonist's agency across four chapter files. The opening supported a plausible "passive protagonist" diagnosis, while middle and ending files contained the actions and consequential choices that falsified it. A fifth file contained an explicitly obsolete, non-canonical ending.

Pass criteria:

- read all four canonical files and the authority note;
- use long-work coverage without producer-review output;
- test the opening diagnosis against middle and ending evidence;
- reject or narrow the passive-protagonist claim when contradicted;
- avoid importing the obsolete ending into canon;
- disclose source coverage in the final recommendation.

Result: **PASS**. The run rejected both "merely passive" and "no consequential ending choice," located the narrower problem in compressed consequence presentation, preserved the obsolete note as non-canonical context, and reported complete four-file coverage.

The raw fixtures and outputs were kept outside the release directory so the distributed Skill contains only runtime instructions and maintained product documentation.

## Limitations

This is a structured same-model benchmark, not a multi-model randomized trial.

- Independent subagent/model instances were not available during the experiment.
- The runner and evaluator were from the same model family.
- The three works came from one creator/project ecosystem.
- Literary quality has no objective gold standard.
- v2.1 was partially designed in response to weaknesses found in earlier tests, so unseen-work evaluation remains necessary.

The next useful benchmark is an **out-of-sample blind test** using unrelated works and independent human editors/producers who do not know which skill generated each diagnosis.

## Reproduce the idea

To reproduce the comparison on your own material, keep these conditions fixed:

1. give each skill exactly the same text;
2. do not provide prior discussion or preferred diagnosis;
3. require 3 loops maximum;
4. prohibit author clarification during the comparison;
5. score diagnosis, evidence, leverage, regression risk, and convergence before revealing which skill produced the output.

The purpose of the benchmark is not to prove that one AI can objectively judge art. It is to test whether a **skill specification produces more auditable, adversarial, and stable story-development reasoning**.
