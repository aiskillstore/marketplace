# Chinese AI-Style Signals

## Purpose

Use `humanizer_zh_reverse_v1` to expose editable writing patterns that commonly appear in LLM output. Treat the result as one feature family for the local detector and as a qualitative style-resemblance assessment, not authorship provenance.

The method is independently implemented from editorial concepts described by [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh), which in turn cites Wikipedia's community-maintained [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). The source repository provides a prompt rubric, not a trained classifier or calibrated “AI rate.”

## Output labels

- `strong_ai_style_patterns`: at least six distinct pattern families and ten total occurrences.
- `some_ai_style_patterns`: at least three families and four occurrences.
- `few_ai_style_patterns`: fewer local patterns; this does not support a human-origin conclusion.
- `not_applicable`: no text or a language outside the Chinese heuristic.

Translate these into AI-assistance language only as:

- `ai_assistance_plausible`
- `ai_assistance_possible`
- `not_supported_by_style_alone`
- `unknown`

Do not report a percentage or use words such as “confirmed,” “certain,” or “proved” from this layer.

## Pattern families

The local scanner reports grounded excerpts for:

- inflated importance or problem framing;
- vague authority, research, or source attribution;
- formulaic investigation transitions;
- reveal-and-overexplain structures;
- clusters of abstract formal vocabulary;
- negative parallelism and generic conclusions;
- chatbot-response residue, promotional language, and overqualification;
- standard transition ladders, symmetric relation templates, and conditional abstract conclusions;
- repeated rhetorical questions, mechanical parallel structure, and stacked enumeration.

Counts are descriptive. A single phrase such as “此外” or a single three-item list is not meaningful by itself.

## Counter-signals and confounds

Always retain counter-signals and genre confounds:

- Concrete dates and topic-specific details reduce the generic-template explanation but do not prove human origin.
- First-person voice, humor, irregular rhythm, and unusual metaphors can be written by either humans or models.
- Satire deliberately uses repetition, inflated claims, and overexplanation.
- Marketing, academic, bureaucratic, SEO, and platform hashtag styles naturally overlap with the pattern list.
- Human-edited AI text can remove these patterns; human writers can reproduce them intentionally or by habit.

When satire or another strong genre confound is present, say that the text has dense AI-associated patterns while the genre supplies a credible alternative explanation for some of them.

## Evidence boundary

Style findings may change the practical description from “no modeled pattern is visible” to `style_patterns_only`. They must not independently produce `strong_pattern_match`, an authorship likelihood, `verified_ai_provenance`, `strong_ai_indicators`, or `no_reliable_ai_evidence`.

Keep Human Reception blind to this scan. Reader aversion and style resemblance remain separate findings.
