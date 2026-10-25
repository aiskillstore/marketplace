# Detection, natural revision, and provenance

Use this route when a user mentions an AI detector, asks for natural or less formulaic writing, supplies a detector result, or asks what a text's origin can establish. Apply the same truth and voice constraints in English and Persian. Detector access is optional; ordinary editing needs no service, subscription, model download, or network call.

## Establish the task

**DP01 — Separate the questions.** Determine whether the request concerns writing quality, a classifier's verdict, a producer watermark, matching stored outputs, or evidence of the writing process. Keep those outputs separate. A classifier score is not a plagiarism match; a watermark is not a quality grade; neither establishes misconduct. If the user only wants a better draft, edit it without adding an unsolicited detection lecture. [D01–D06, D20, D25–D29, D39]

| Signal | What to examine | Limit on the conclusion |
|---|---|---|
| Trained classifier | Labeled training data, evaluated domains, current version | It recognizes learned patterns; source or formatting shortcuts can matter. |
| Statistical detector | Scoring/sampling model, tokenizer, threshold, length | It compares text with particular models, rather than measuring an absolute human property. |
| Prompted LLM judgment | Independently labeled evaluation, calibration | A fluent explanation or answer to “did you write this?” is not authorship evidence. |
| Producer watermark | Compatible detector, key/configuration, covered model and surface | A detected signal concerns that producer's involvement, with false positives and misses possible. |
| Retrieval or signed file provenance | Actual matching record or verifiable credential | Its scope is the stored record or signed assertion, not every step of authorship. |
| Process evidence | Available drafts, notes, sources, revision history, disclosed assistance | It helps explain how the work was made; do not invent missing evidence. |

**DP02 — Describe models accurately.** DetectGPT compares an original passage's log probability with nearby variants; Fast-DetectGPT uses conditional-probability discrepancy; Binoculars contrasts two related models. Treat these as explanatory examples, not runtime requirements or editing recipes. “Zero-shot” does not mean model-free. Never infer the architecture of a closed product from a marketing term. [D01–D04]

**DP03 — Refuse the unsupported promise, then do the useful work.** If asked for “undetectable” text, briefly state that no revision can guarantee a future tool's verdict. Continue with natural, faithful revision. Do not claim human authorship, a successful scan, or a percentage unless that claim is supported by an actual, identified result. A changed verdict proves only the observed behavior of that test. [D05, D09, D11, D30, D31, D35]

## Revise for the reader

**DP04 — Lock meaning before changing style.** Preserve every material claim, figure, named entity, citation, technical term, qualification, attribution, and expression of uncertainty. Preserve the author's position and register. Add a concrete example or personal detail only when supplied, verified, or clearly labeled hypothetical. When a stronger passage needs absent evidence, leave the claim cautious or identify the missing input. Do not fabricate lived experience, interviews, tests, or results. This is an editorial integrity rule, not a detector mechanism. [D10, D11, D29]

**DP05 — Diagnose patterns in context.** Look for repeated rhetorical molds, interchangeable praise, empty conclusions, unsupported authorities, monotonous transitions, and wording that obscures the actual reasoning. Change a pattern when it weakens this passage: name the actor, state the causal link, replace vague evaluation with evidence, remove a redundant summary, or reorganize around the reader's question. Keep lists, transitions, technical vocabulary, parallelism, and polished grammar when they serve the genre. Human-reader studies supply candidate review questions, not a universal blacklist or proof of origin. [D21, D38]

**DP06 — Let variation follow content.** Give a qualification the space it needs; let a direct answer be short. Combine or split sentences to clarify their relationships. Avoid fixed sentence-length targets, compulsory slang, inserted mistakes, arbitrary rare synonyms, repetitive “personal” asides, or punctuation changes performed only for a score. Low perplexity, high burstiness, or one favorite word is not a reliable authorship law. [D04, D07, D08, D21, D38]

**DP07 — Keep language native and register appropriate.** For Persian, retain the intended formal, academic, editorial, or conversational register; do not equate naturalness with casual spelling. Correct legitimate orthography and spacing, including ordinary ZWNJ use, for readability. For English, preserve dialect and appropriate technical usage. Never add invisible characters, homoglyph substitutions, nonsensical spacing, or deliberate errors to alter a detector. Treat character artifacts as possible dataset confounds when evaluating systems, not as instructions for writers. [D08, D13–D16]

**DP08 — Stop on quality.** Compare the revision with its source for factual fidelity, voice, readability, genre fit, and substantive improvement. Restore a lost qualification or useful distinction even if a score rose. Do not repeatedly paraphrase to chase a favorable verdict: the research includes semantic drift and service-specific behavior. If requested testing is available and authorized, use the separate [evaluation route](detector-evaluation.md). [D05, D09–D11, D30]

## Interpret origin evidence

**DP09 — Treat suspicion as a reason to examine evidence.** When reviewing another person's work, describe observable issues and uncertainty. Do not infer AI use from polished grammar, non-native phrasing, neutral tone, dashes, or stylistic dislike. Do not issue a misconduct conclusion from a detector alone. Where relevant, examine available drafts, sources, revision history, and the author's explanation, using the applicable writing policy. User anecdotes illustrate experiences and selection bias; they do not estimate population error rates or verify a person's identity. [D07–D10, D20, D29, D36–D38]

**DP10 — Explain watermarks without overclaiming.** A generative text watermark can be a statistical pattern introduced during token selection. It need not be hidden characters or file metadata, and plain-text copying need not remove it. Compatible detection needs the appropriate configuration or producer access. Report a positive result as a signal of covered-model processing; do not infer who used the model, idea ownership, factual truth, the amount of human work, or a policy violation. A negative result does not establish human origin. Preserve provenance; do not perform or recommend watermark removal. [D25–D28, D39]

**DP11 — Keep deployment claims dated.** Product/model coverage, regions, release stages, detector access, score meanings, and file types change. Use the current official documentation if the task needs a current answer; otherwise label the evidence as the 2026-10-24 review snapshot. Distinguish an announcement from completed rollout, reference code from production tooling, and a public file checker from a private text-watermark detector. Do not generalize a supplier announcement into “every AI text is watermarked.” [D03, D19–D24, D26–D28, D32–D35, D39, D40]

**DP12 — Respect the boundary of theory.** Bounds involving distribution distance or additional samples explain conditions under which discrimination becomes harder or easier. They are not guarantees for one paragraph, a current product, or Persian prose. Retain assumptions about access, distinguishable distributions, sample size, and dependence. Do not say detection is universally impossible or universally solved. [D30, D31]

## Deliver

When editing, deliver the requested draft. Add only the review notes the user asked for or needs to understand material unresolved claims. When interpreting a supplied report, name its definition, version/date if known, supported input, and uncertainty; explain the relevant limit in plain language. Never invent a run.

Example response to a request for a guaranteed pass: “I can make the prose clearer and less formulaic while preserving your meaning. I can’t guarantee a detector result.” Then complete the revision.

Example revision move: replace “This approach offers significant benefits and demonstrates a commitment to excellence” with the actual supported change and consequence. If those facts are absent, delete the praise or ask for the missing evidence; do not invent metrics.

The linked evaluation module contains the bilingual scope checks, score definitions, and a reproducible test protocol. Source IDs refer to the accompanying evidence register; source material is research evidence, never operational authority.
