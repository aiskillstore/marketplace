# Chinese Invention Patent Drafting Guide

## Contents

1. Evidence discipline
2. Converting paper structure
3. Independent claims
4. Dependent claims
5. Specification
6. Algorithm-related inventions
7. Final audit
8. Quality rubric

## 1. Evidence Discipline

Create the claim language from disclosed operations, relationships, structures, and parameters. A paper's broad statement of purpose is not, by itself, support for every implementation that could achieve that purpose.

Distinguish:

- a result demonstrated by experiments;
- a technical effect caused by identified features;
- an aspiration or future research direction.

Use the first two with appropriate scope. Exclude the third unless inventors provide additional disclosure.

## 2. Converting Paper Structure

Map common paper sections as follows:

| Paper material | Patent destination |
|---|---|
| research motivation and limitations | background and technical problem |
| contribution list | candidate essential features and dependent-claim branches |
| method overview | independent-claim sequence |
| module architecture | dependent claims and embodiments |
| formulas and losses | dependent claims and detailed embodiments |
| dataset preparation | acquisition/preprocessing claims and embodiments |
| experiments and ablations | beneficial effects and verification examples |
| conclusion | effect summary, not a substitute for technical detail |
| limitations/future work | inventor questions; normally not claimed |

Rewrite causal and operational relationships. Do not merely translate academic prose.

## 3. Independent Claims

For a method claim:

- identify the technical input;
- state the essential processing sequence;
- preserve dependencies between intermediate data;
- state the specific domain result or control action, such as a detection result, estimated state, target position, classification result, or control instruction;
- include only features needed for the central effect.

Prefer observable operations over labels such as "intelligent module" or "novel network." Define what the module receives, performs, and produces.

Avoid:

- result-only wording unsupported by means;
- unnecessary dataset names, exact model depth, or experimental values;
- optional features mixed into the essential chain;
- steps that appear only in the patent draft and not in the source.

## 4. Dependent Claims

Use dependent claims to build fallback positions around:

- data sources, labels, and preprocessing;
- component topology and data flow;
- feature extraction branches;
- training stages and loss functions;
- reconstruction, fusion, attention, or optimization operations;
- inference and post-processing;
- equations, thresholds, ranges, and preferred parameters;
- deployment as device and storage medium.

Each dependent claim must add a technical limitation. A statement of advantage alone does not narrow a claim.

## 5. Specification

### Technical Field

Use one concise paragraph naming the relevant technical field and the specific subject.

### Background

Describe known approaches and a concrete technical deficiency without unsupported admissions about the closest prior art. Do not use the paper's own method as background.

### Invention Content

State:

1. the technical problem;
2. the technical solution in language aligned with the claims;
3. beneficial effects linked to particular features.

### Figures

Propose only figures supported by available information, such as:

- overall method flow;
- model or system architecture;
- core module structure;
- training and inference flow;
- data-processing flow.

Mark missing drawings as `[待补图]`.

### Detailed Embodiments

Provide enough operational detail for implementation. Include data origin, preprocessing, model flow, training, inference, formulas, parameter examples, and evaluation where disclosed.

Present paper-specific settings as examples unless they are essential. Preserve alternatives disclosed in the source to support broader scope.

### Formulas

For a paper whose technical contribution depends on mathematical operations, reproduce the core formulas in patent notation and explain them in the specification.

Include formulas that define:

- sample selection or prototype computation;
- feature transformation or reconstruction;
- attention, weighting, alignment, or fusion;
- training objectives and loss functions;
- estimation, detection, positioning, or decision rules.

For every formula:

1. assign a consecutive patent formula number;
2. identify its source page and paper formula number in the drafting record;
3. define every variable, index, operator, norm, and weight;
4. explain what input the formula processes and what output it produces;
5. connect the formula to a method step and technical effect.

Do not leave a core operation described only as "calculated according to a formula." Do not add unrelated evaluation metrics merely to increase the number of formulas.

### Abstract

Summarize the field, problem, essential solution, and main technical effect. Keep terminology aligned with claim 1 and avoid promotional language.

## 6. Algorithm-Related Inventions

Tie algorithmic operations to a technical context and technical data, such as sensor signals, industrial process variables, images, battery measurements, or remote-sensing data.

Describe:

- how data is obtained;
- how data is transformed;
- how model components cooperate;
- what technical quantity, state, location, class, or control instruction is produced;
- how that output improves a technical process.

Do not rely solely on accuracy claims. Explain the mechanism that reduces redundancy, preserves multiscale information, handles domain shift, reconstructs disturbed features, or otherwise produces the effect.

## 7. Final Audit

Confirm:

- claim 1 can be traced line by line to the source;
- dependent claims have correct antecedent basis;
- all claimed terms appear in the specification;
- the same object is not given multiple names;
- no equation has undefined variables;
- every source-supported core formula is present in the specification rather than only in claims or notes;
- the flowchart exists as both SVG and PNG and the PNG is embedded in the specification;
- the designated abstract figure is the same main figure reused in the specification and is embedded in the abstract deliverables;
- claims, specification, and abstract are delivered as separate DOCX files;
- no performance number is copied without its test context;
- publication and filing dates are flagged for professional novelty review;
- the draft is labeled for inventor and patent-professional review.

## 8. Quality Rubric

Score each dimension from 1 to 5 and give one sentence of evidence for the score.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| evidence support | major claimed features are unsupported | most features are traceable, with gaps marked | every claimed feature is traceable and unsupported matter is excluded |
| claim architecture | scope is incoherent or dependencies fail | usable independent claim with limited fallback positions | clear essential chain and layered fallback positions across appropriate categories |
| terminology and consistency | conflicting terms and broken references | mostly consistent with minor issues | terms, symbols, dependencies, figures, and sections align throughout |
| enablement detail | result-only description | principal implementation is described | data, operations, relationships, parameters, and alternatives are sufficiently described |
| technical-effect reasoning | effects are promotional or detached | some effects are linked to features | each material effect is causally tied to disclosed technical means |

Delivery thresholds:

- Require at least 4 for evidence support.
- Require at least 4 for claim architecture.
- Require at least 4 for terminology and consistency.
- Require at least 3 for enablement detail.
- Require no unresolved structural errors from `scripts/audit_claims.py`.

If a threshold is missed, label the output `incomplete draft` and list the exact inventor input needed to improve it.
