# Corpus-Derived Paper-to-Patent Patterns

## Scope

These heuristics were derived from five paired research-paper and Chinese-patent examples covering robotic grasping, battery health estimation, industrial fault detection, surface defect detection, and remote-sensing biomass estimation.

They describe recurring drafting choices. They do not establish patentability or legal sufficiency.

## Recurring Transformations

| Academic contribution | Typical patent treatment |
|---|---|
| end-to-end model | method claim with ordered data and model operations |
| new backbone or feature extractor | dependent claim defining stages, branches, or topology |
| attention, fusion, or reconstruction module | dependent claims defining input, operation, and output |
| training strategy | method steps plus loss-function dependent claims |
| inference rule | post-processing or decision step |
| dataset extension | data acquisition, annotation, or preprocessing dependent claim |
| experimental advantage | beneficial effect tied to the responsible features |
| software implementation | device and computer-readable-medium claims |

## Claim-Layer Pattern

The examples commonly use:

1. one method claim covering the complete technical pipeline;
2. dependent claims unpacking each contribution in the same order as the pipeline;
3. dependent claims for formulas or parameterized operations;
4. device and storage-medium claims for software-controlled implementations.

Do not copy this shape blindly. Use it only where supported by the source and appropriate for the invention.

## Problem-Solution Patterns

### Multi-task Interference

When a paper addresses interference between tasks, claim the cooperating feature paths or reconstruction operations rather than only stating that interference is reduced.

### Domain Shift and Generalization

When a paper addresses multiple operating conditions, claim domain construction, meta-training/meta-testing or adaptation operations, feature fusion, and model updating. Treat generalization as an effect, not an unsupported step.

### Redundant Latent Features

When orthogonality or introspective training is used, separate the detection pipeline from training-specific dependent claims. Define positive/negative samples and loss terms before relying on their effects.

### Detection Accuracy and Speed

For multiscale detection, claim the feature hierarchy, candidate-region generation, and localization operations. Place exact backbone depth, anchor parameters, and benchmark values in narrower claims or embodiments.

### Limited Samples

For self-supervised reconstruction, claim how auxiliary/disturbed data is generated, how residual data is formed, how reconstruction pretraining works, and how the downstream estimator is fine-tuned.

## Drafting Lessons

- Papers often emphasize novelty by naming modules; patents must disclose the module's operations and relationships.
- The paper's contribution list is a strong candidate list for dependent claims, not necessarily for separate independent claims.
- Experimental tables support effect statements but usually should not define claim scope.
- Model names can remain in embodiments, but independent claims should generally use technically descriptive language.
- A paper and its patent may differ in terminology or implementation detail. Treat the paper as evidence, not permission to import unexplained features from another patent.
- Publication timing, prior disclosures, and inventorship require separate factual and professional review.
