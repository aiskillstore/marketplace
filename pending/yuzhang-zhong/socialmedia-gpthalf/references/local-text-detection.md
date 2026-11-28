# Local Text Detection

## What is borrowed

`zh_descriptive_pattern_proxy_v2` borrows four public ideas associated with GPTZero and the wider detector literature:

1. Predictability matters: generated text may favor statistically regular phrasing.
2. Burstiness matters: sentence length and local surprise may vary less across a generated document.
3. Sentence and document summaries are different: highlight locally influential sentences and aggregate them separately.
4. Partial pattern concentration must remain distinct from a full-document pattern match.

GPTZero's 2026 paper describes a supervised hierarchical multi-task detector trained on large human/AI datasets. It predicts Human, AI, and Mixed at the document level and a binary label per sentence. Its architecture details and hyperparameters are proprietary. This skill does not reproduce that model and does not use its API.

## Local implementation

The offline analyzer computes:

- sentence-length coefficient of variation;
- variation in document self-surprisal across sentences;
- normalized unit entropy;
- repeated four-unit sequence ratio;
- compression ratio;
- sentence-opener reuse;
- the share of sentences with grounded template, rhetorical, attribution, reveal, enumeration, or regularity cues;
- the separate Chinese style-pattern findings from `humanizer_zh_reverse_v1`.

Document self-surprisal uses frequencies inside the inspected document. Compression and repetition use only that same text. These are predictability proxies, not language-model perplexity. True perplexity requires a reference language model and tokenizer; swapping in a self-frequency statistic while retaining the word “perplexity” would be misleading.

## Decision logic

The analyzer exposes transparent indicator points and the drivers that added them. Points are not percentages or calibrated probabilities.

- `strong_pattern_match`: full Chinese length coverage, at least eight indicator points, at least three listed feature families, and at least 45% of sentences carrying locally grounded pattern signals.
- `localized_pattern_match`: at least five points and at least two listed feature families, but the text does not meet the full-document rule.
- `unresolved`: usable text without enough convergence.
- `insufficient_evidence`: text below the local coverage floor or absent.
- `unsupported_language`: English, mixed, other, or unknown input; the bundled rules are Chinese-specific.

For Chinese, 500 Han characters are required for `strong_pattern_match`; 200–499 Han characters can produce only a limited descriptive result. Crossing the coverage threshold permits a pattern label but is not itself positive evidence. English and mixed text are not implemented and must not be forced through the Chinese rules.

## Feature families

- `template_and_style`: multiple explainable Chinese pattern families, not isolated buzzwords.
- `sentence_level_concentration`: a meaningful share of locally highlighted sentences.
- `structural_regularity`: at least five sentences plus sentence-length CV at or below 0.40, or opener reuse at or above 0.30.
- `lexical_predictability_proxy`: repeated four-unit ratio at or above 0.05, or compression ratio at or below 0.55 on at least 500 encoded bytes.

Document self-surprisal variation remains visible for inspection but does not add indicator points because a within-document frequency model is too weak to stand in for reference-model likelihood.

The families overlap: style rules and sentence cues may describe the same wording. Do not call them statistically independent evidence. Concrete details, humor, hashtags, satire, marketing, and formal institutional prose remain possible confounds and must stay visible in the report.

## Interpretation boundary

`strong_pattern_match` means only that the inspected text strongly resembles the rules encoded here. It supports the descriptive practical label `strong_ai_like_drafting_signals`, not an authorship likelihood. Its bundled tests verify code behavior, not accuracy on unseen human and AI writing. Valid C2PA, a platform label, or an explicit author disclosure remains categorically stronger source evidence.

Do not promote this proxy to a Human/AI/Mixed classifier until a separately trained model and frozen thresholds pass [evaluation-protocol.md](evaluation-protocol.md) on a provenance-backed blind set.

Never use this result for punishment, hiring, education discipline, legal findings, automated moderation, or claims about the author's character. Corroborate consequential judgments with drafting history, source files, disclosure, or direct author clarification.
