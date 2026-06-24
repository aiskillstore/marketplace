# Corpus Pair Audit

## Purpose

Use the five numbered pairs as examples of drafting transformations, not as unquestioned one-to-one ground truth. File numbering establishes intended pairing only. Technical content and dates determine the strength of each match.

## Pair Assessments

| Pair | Paper subject | Patent subject | Match strength | Important caution |
|---|---|---|---|---|
| 1 | MLEAFormer for grasp detection and classification | ECBAFormer robotic grasp detection method | partial | The task and broad architecture align, but model and module names differ. Verify every feature before transferring it. |
| 2 | MSDMLN for battery SOH under multiple target conditions | battery SOH estimator training using EMD, dense recurrent-convolution extraction, and meta-learning | strong | The patent application predates the paper publication. Use the technical overlap, but do not infer legal priority or inventorship. |
| 3 | ReSiOrCAE with variable rearrangement, dual-path convolution, orthogonality, and soft-introspective training | introspective orthogonal autoencoder process fault detection | partial | The patent strongly covers introspective and orthogonal training but does not necessarily capture every later paper contribution. |
| 4 | AGLNet for adaptive global localization surface-defect detection | AGLNet product surface-defect detection | strong | The patent mirrors the main pipeline closely. Exact legal status and chronology still require source records. |
| 5 | SSDFRN for limited-data mangrove biomass estimation | self-supervised disturbing-feature reconstruction biomass estimation | strong | The core data disturbance, reconstruction, multiview network, and fine-tuning chain align well. |

## Date Cautions

- A publication date is not necessarily the first public disclosure date.
- A patent PDF may show application, publication, or grant dates; distinguish them.
- A paper may have received, accepted, online-publication, and issue dates.
- Never state novelty, priority, ownership, or valid entitlement from these PDFs alone.

## Pair-Mapping Procedure

For each pair:

1. Normalize technical terms without collapsing distinct modules.
2. Map the independent claim feature by feature to paper pages.
3. Map dependent claims to paper methods, formulas, and implementation details.
4. Label patent-only material and exclude it when drafting solely from the paper.
5. Label paper-only material as a candidate contribution, not as proof of patentability.
6. Record chronology separately from technical similarity.

## Safe Uses

Use the corpus to learn:

- how contribution lists become claim branches;
- how model operations become ordered method steps;
- how experiments become effect evidence;
- how software methods expand to device and storage-medium claims.

Do not use it to:

- copy claim language into an unrelated invention;
- assume patent-only detail is supported by the paper;
- determine novelty or freedom to operate;
- infer inventors from paper authors.
