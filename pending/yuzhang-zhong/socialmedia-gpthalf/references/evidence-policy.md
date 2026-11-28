# Origin Evidence Policy

## Core rule

Assess provenance and detector signals without claiming certainty that the evidence cannot support. Reader reaction is never origin evidence. Style, grammar, repetitiveness, and genericness belong in the separate `style_pattern_assessment`; they may describe resemblance but cannot support an authorship likelihood until a separately trained model passes the frozen blind evaluation protocol.

## Verdicts

Use exactly one verdict:

- `verified_ai_provenance`: a valid C2PA manifest, explicit platform label, or unambiguous author disclosure identifies generative AI for a specific asset.
- `strong_ai_indicators`: a versioned external image detector supplies a strong positive signal, but no verified provenance exists.
- `conflicting_evidence`: strong positive and strong negative evidence address the same content.
- `no_reliable_ai_evidence`: adequate checks ran and found no reliable positive signal.
- `insufficient_evidence`: content is short, unavailable, unsupported, unchecked, or affected by provider failure.

Never translate `no_reliable_ai_evidence` into “human-written” or “authentic.”

## Practical inference

Keep `practical_assessment` separate from `origin_assessment`:

- `verified_ai_provenance_present` / high: verified provenance exists for the listed scopes; an image-only scope does not verify the text or whole post.
- `strong_model_signal` / medium: a versioned image-detector signal crosses the policy threshold; this is not provenance.
- `strong_ai_like_drafting_signals` / descriptive only: uncalibrated local Chinese rules show dense pattern convergence.
- `localized_ai_like_patterns` / descriptive only: local Chinese rules show limited or partial pattern concentration.
- `style_patterns_only` / descriptive only: style resemblance exists without a local document-level pattern result.
- `conflicting_ai_evidence` / low: strong evidence conflicts for the same asset.
- `no_reliable_ai_signal` / medium: a completed calibrated image check supplies a strong negative signal; this is not proof of human origin.
- `no_conclusion` / low: useful coverage is absent.

Practical confidence describes the stability of this layered inference. Provenance confidence describes source verification only. Never present the latter as an overall AI likelihood.

## Evidence hierarchy

1. Verified provenance: valid C2PA generative source type, explicit platform AI label, or unambiguous author disclosure.
2. Calibrated external model signal: versioned Hive image output.
3. Local explainable text description: untrained document/sentence rules using predictability proxies, rhythm variation, and style patterns.
4. Context only: language, text length, individual cues, visual anomalies, and platform conventions.

Local text rules cannot establish provenance, create `strong_ai_indicators`, or justify “likely generated.” Read [local-text-detection.md](local-text-detection.md) and [ai-style-signals.md](ai-style-signals.md).

## Text calibration

- Normalize whitespace before counting.
- Treat Chinese text as sufficient only at 500 or more Han characters.
- The bundled local rule proxy supports Simplified Chinese only. English, mixed, other, and unknown are `unsupported_language` regardless of length.
- Treat the 500-Han-character threshold as a coverage threshold, not an AI-likelihood cutoff.
- Do not call GPTZero or send target text to third-party detectors in the default skill workflow.
- Use `strong_pattern_match` only as a descriptive result; do not assign an authorship likelihood from it.
- Keep the origin verdict `insufficient_evidence` until verified provenance or a qualifying external asset signal exists.

## Image calibration

- Verify C2PA locally before calling an image detector.
- Treat `trainedAlgorithmicMedia` as created using generative AI for that file.
- Treat `compositeWithTrainedAlgorithmicMedia` as verified generative editing/involvement, not proof that the whole file was generated.
- Treat `algorithmicallyEnhanced` as ordinary algorithmic alteration and never as generative provenance by itself.
- Treat missing C2PA as absence of evidence.
- Treat invalid or tampered C2PA as a provenance warning, not proof of AI generation.
- Treat Hive `ai_generated >= 0.9` as a strong positive model signal.
- Treat Hive `not_ai_generated >= 0.9` as a strong negative model signal.
- Keep carousel findings per asset. Never average files into a post-wide probability.

## Disclosures

Accept only a structured `confirmed` observation or an unambiguous, asset-scoped positive label/admission such as:

- “AI-generated”
- “generated with AI”
- “synthetic media”
- “AI 生成”
- “使用 AI 生成”

Reject negated, quoted, debated, or ambiguous phrases such as “not AI-generated,” “the AI-generated claim is false,” “AI discussion,” or a hashtag that merely mentions AI. Preserve observation scope (`post`, `text`, or an image ID).

## Conflicts

Declare conflict only when evidence addresses the same text or image. A positive image result and a negative text result are separate asset findings, not a conflict.

Verified provenance normally outranks detector disagreement. Still report the disagreement in evidence details.

## Confidence

- High: valid, unambiguous provenance.
- Medium: strong calibrated model signal without provenance, or adequate negative checks.
- Low: partial coverage, medium signals, language mismatch, short text, missing keys, or provider failure.

## Required limitations

Always state:

- AI detectors can produce false positives and false negatives.
- Missing AI evidence does not prove human authorship.
- Short and out-of-domain text is especially unreliable.
- Findings apply only to the inspected text or assets.
- High-stakes decisions require corroboration and human review.
