# Evaluate detector claims and revision outcomes

Use only when a user asks to evaluate a detector, interpret its report, or measure revision outcomes. A writing request alone does not authorize uploading text to an external service. No paid detector, third-party installation, or network service is required for normal skill use.

## Define the experiment before seeing scores

**DE01 — Record the question and labels.** Decide whether the target is full generation, light editing, substantial rewriting, translation, mixed passages, or producer-watermark presence. Record those classes separately. Retain an unknown class for uncertain origin. A recent published text is not confirmed human merely because it was published; an AI-assisted refinement is not equivalent to an unmodified human text or a wholly generated draft. Authorship policy and statistical labels are separate decisions. [D09, D10, D20, D23, D38–D40]

**DE02 — Freeze a run specification.** Record detector name, exact version if returned (otherwise unknown), date/time, endpoint or interface, mode, language, score definition, threshold and comparison direction, qualifying text, truncation, and treatment of errors and abstentions. For statistical methods, also record model/tokenizer pair and settings. Retain raw output and exact tested text when permitted. A method name alone does not identify an implementation. [D01–D04, D19–D24, D34, D35, D40]

**DE03 — Verify permitted inputs and data handling.** Check support for the actual language, genre, length, file type, and feature. An accepted request is not proof of validated support. Plagiarism coverage, an AI classifier, and phrase explanations may have different language lists. Obtain appropriate authorization before an external upload, respect confidentiality and service terms, and minimize retained content. If testing is unavailable, report that limit and finish the quality review locally. [D19, D20, D24, D32–D36]

**DE04 — Use honest, matched controls.** Obtain evidence-backed human texts and known generated counterparts matched as closely as practical for topic, genre, length, time, and source presentation. Record remaining confounds. Keep originals and rewritten versions linked. Include held-out authors, documents, topics, generators, and later dates as the claim requires. Group variants of the same topic/document before splitting; do not let fragments or paired versions leak between calibration and test sets. A source-provided split is a starting point to inspect. [D06, D08, D09, D12–D16, D38, D40]

**DE05 — Test bilingual scope explicitly.** Evaluate English and Persian separately, then by register and genre. If relevant, create separate strata for English by non-native writers, translated writing, conversational Persian, mixed Persian/English, poetry, quotations, code, and short passages. Inspect extraction/encoding artifacts and length differences without disguising text. Apply any documented normalization consistently to both classes and retain the original. Do not transfer Arabic, Urdu, or English performance to Persian. [D07, D08, D13–D18, D22, D24, D32–D35]

## Interpret the evidence available

**DE06 — Rank evidence by what it can establish.** Distinguish independent research, a preprint, implementation documentation, dataset-author assertions, vendor evaluation, official support documentation, and user discussion. A vendor rerunning a public benchmark remains a vendor evaluation. A historical result applies to the tested versions and conditions. Neither a strong result on direct generations nor a weak result on shifted data settles all use cases. [D01–D12, D19–D24, D33–D38, D40]

The following source-specific checks prevent recurring inference errors; they are not product recommendations or a live support directory:

| Sources | Check before using the evidence |
|---|---|
| D01–D04 | Probability methods use particular scoring models and thresholds. Strong original results coexist with later failures under different distributions. |
| D05, D06 | Examine low-FPR recall, held-out tasks/models, decoding settings, per-domain errors, and benchmark exposure. Do not convert attack findings into writing tricks. |
| D07, D08 | The 2023 English bias study and 2026 Czech follow-up differ in language, data, and tools. Audit the intended group rather than universalizing either result. |
| D09 | June 2026 versions, roughly 500-word passages, author clustering, and the handling of “Mixed” verdicts limit transfer. |
| D10, D11 | Abstract proxy labels and base/instruct comparisons diagnose failure modes. They do not validate grammar-only assistance, semantic preservation, all generators, or future services. |
| D12, D13 | Two English Q&A corpora and an older multilingual news benchmark do not establish general Persian performance. Inspect naturalness and artifacts. |
| D14, D15 | The matched Persian Wikipedia corpus is encyclopedic; the other card is AI-only and gated. Card counts, model identities, and quality require record-level verification before use. |
| D16–D18 | MULTITuDE's reviewed language list excludes Persian. AbjadGenEval announced Persian, but its final reviewed results cover Arabic and Urdu. |
| D19–D24 | Input requirements, qualifying text, supported features, modes, and score semantics are versioned vendor facts. A language list is not independent accuracy evidence. |
| D25, D26 | Reference watermark detectors test a matching configuration; the code has research-use caveats and statistical assumptions. No code execution is claimed here. |
| D27, D28, D39 | Rollout and access statements are supplier-specific snapshots. Watermark involvement is distinct from full authorship or misconduct. |
| D29–D31 | LLM self-attribution and theoretical detectability are different questions. Preserve the access and sample assumptions of a theoretical claim. |
| D32–D35 | Check each feature's language list, model version, truncation, and score units. The reviewed Winston page has inconsistent language lists; do not silently choose one as definitive. |
| D36, D37 | Conflicting anecdotes and an unverified claim to be a study author cannot establish error rates or amend a paper. Use them to identify questions for verification. |
| D38, D40 | Human judgments need blinded comparison and relevant readers. Vendor class mappings and failed-request exclusions can change benchmark conclusions. |

## Measure and report

**DE07 — Keep scoring semantics intact.** A score can mean a model confidence, a document class, estimated qualifying-text fraction, or a producer-specific test statistic. Read its definition. Do not call every “90% AI” a 90% probability of AI authorship, compare raw percentages across products, or interpret highlights as independently tested sentences unless documented. Specify how Mixed, abstained, unsupported, and failed results enter each metric. Predeclare mappings and, if consequential, report sensitivity to another reasonable mapping. [D03, D09, D20, D23, D26, D34, D35, D40]

**DE08 — Calibrate separately from the final test.** Select a threshold on an appropriate calibration set for a stated error tolerance, then freeze it before evaluating the held-out set. Use the same policy to compare systems, report any domain-specific thresholds, and show actual per-domain and per-language FPR. Do not tune on the final test or naively assume that 0.5 is correct for every score. [D04–D06, D18]

**DE09 — Report counts and relevant rates.** Define AI as positive only for the declared binary task, then report TP, FP, TN, FN, denominators, and exclusions. Use:

- FPR = FP / (FP + TN); FNR = FN / (FN + TP).
- Recall/TPR = TP / (TP + FN); specificity = TN / (TN + FP).
- Precision = TP / (TP + FP); accuracy = (TP + TN) / all classified cases.

Mark a zero-denominator metric undefined. Include recall at a specified low FPR when appropriate, alongside AUROC if available. AUROC describes ranking across thresholds and can conceal poor behavior at the chosen low-FPR operating point. Accuracy and precision depend on class proportions; report them with those proportions. [D04–D06, D09, D40]

**DE10 — Put sample uncertainty next to the rate.** Zero observed false positives is not zero population error. Report sample size, uncertainty method, and clustering by author/document/topic. Do not apply independent-binomial certainty claims to repeated excerpts without acknowledging dependence. Sparse cells support tentative descriptions, not precise claims about rare errors. Show subgroup results and the rate of unsupported inputs or failed requests. [D06, D08, D09, D38, D40]

An original arithmetic illustration: suppose 100 of 10,000 texts are generated. A detector finds 90 of them and incorrectly flags 1% of 9,900 human texts. It produces 90 true flags and 99 false flags, so precision is 90/189, about 47.6%. These are hypothetical values, not results for any product.

**DE11 — Evaluate revision on independent axes.** Retain the input and final draft. Review factual and semantic fidelity first, then voice/register, clarity, usefulness, genre fit, and unnecessary formulaic phrasing. Use blinded, randomized comparisons by suitable readers where possible. A lower detector score does not count as a quality improvement or evidence of human authorship. Automated semantic judgments can assist comparison but do not verify facts or replace a claims check. [D09–D11, D13, D29, D30, D38]

**DE12 — Avoid adaptive score chasing.** Predefine the editorial revision and comparison before checking the result. If exploring multiple versions, record all attempts and separate exploration from a fresh held-out evaluation. Report fidelity losses, unchanged or increased scores, and failures. Never cherry-pick a favorable paragraph or claim that a tested sample certifies future outputs. Repeated paraphrasing, hidden-character substitution, invented experience, and watermark removal are outside the revision workflow. [D05, D06, D09, D11, D30, D31]

**DE13 — Keep watermark evaluations separate.** Test only a compatible watermark configuration and covered outputs. Record key/configuration identity without exposing secret values, the text unit/length, null hypothesis, threshold, masking, and abstentions. A p-value is not the probability of human authorship. A reference implementation does not certify production security or detector access to another producer's mark. Do not perform removal or spoofing experiments as an editing service. [D25–D28, D39]

**DE14 — Report the result at its actual scope.** State what was tested, by whom, using which texts and versions, what improved, what did not, and what remains unknown. If only documentation was reviewed, say so. If no detector was run, say no detector was run. Preserve contradictions rather than rounding them into certainty. Prefer “on these English abstracts, at this threshold” to “detectors work/fail.” [D05–D12, D17–D24, D33–D40]

Suggested report fields: purpose; labels/provenance; sample strata and sizes; detector/version/date; supported input and truncation; threshold and mapping; counts/rates/uncertainty; failures; quality/fidelity review; limits. Store no confidential text beyond the user's authorized workflow.
