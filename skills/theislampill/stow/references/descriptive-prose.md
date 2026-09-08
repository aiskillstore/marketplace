# Contextual descriptive prose review

Use this reference when the task calls for a contextual prose-quality review.
Judge observable effects on meaning, evidence, navigation, and reader effort.
Do not infer a writer or origin from a surface pattern. A callable matcher is an
advisory lead, not a verdict.

## Semantic repetition

- **Description:** A later passage, including a functionless conclusion or restatement, repeats an earlier meaning without adding a fact, distinction, consequence, or useful reminder.
- **Rationale:** Repetition consumes attention and can make the reader search for a difference that is not present.
- **Applicability:** Review repeated claims across nearby sentences, list items, and sections.
- **Legitimate counterexample:** Repetition can serve correction, safety, navigation, deliberate emphasis, or stable terminology.
- **Rewrite principle:** Keep the strongest statement once, or make the later occurrence perform a distinct function.
- **Mechanism:** Apply contextual review with `corpus/prose-integrity/rules.md#STOW-PRO-006` and the active terminology constraints.

## Empty metadiscourse

- **Description:** Framing describes the act of explaining, searching, or organizing without advancing the answer.
- **Rationale:** Process narration delays the claim and obscures the information the reader needs.
- **Applicability:** Review generic audience openers, filler transitions, research narration, and section previews that add no orientation.
- **Legitimate counterexample:** Keep a failed verification, material limitation, method, or audience distinction when it changes the conclusion or action.
- **Rewrite principle:** Remove framing or process language only when it adds no information or decision value. Preserve material limitations, methods, audience distinctions, progress states, and requested voice.
- **Mechanism:** Review `corpus/prose-integrity/rules.md#STOW-PRO-011` in context; the active rule consolidates functionless framing, audience setup, and process narration.

## Manufactured contrast or escalation

- **Description:** Intensity, urgency, contrast, or enthusiasm exceeds what the evidence and task support.
- **Rationale:** Manufactured emphasis distorts priority and makes ordinary facts harder to weigh.
- **Applicability:** Review unsupported intensifiers, urgency, dramatic pivots, celebratory language, and corrective contrasts that reject a characterization absent from the discourse or materially implausible in context.
- **Legitimate counterexample:** Keep genuine correction, material contrast, measured risk, or a requested expressive voice when the facts support it. A discourse-present correction that names the real differentiator remains legitimate.
- **Rewrite principle:** Use urgency or intensified emphasis only when a decision-relevant reason is stated. Remove a corrective contrast when nobody asserted or plausibly implied the rejected characterization; otherwise keep the correction and name the actual difference.
- **Mechanism:** Apply semantic review with `corpus/prose-integrity/rules.md#STOW-PRO-009` for unsupported intensity and `corpus/prose-integrity/rules.md#STOW-PRO-020` for a stock corrective construction. These remain contextual judgments, not lexical bans.

## Hollow evaluation

- **Description:** Praise, criticism, or a verdict appears without the observable basis needed to assess it.
- **Rationale:** An unsupported evaluation substitutes stance for evidence.
- **Applicability:** Review evaluative adjectives, abstract conclusions, and generic claims of quality or importance.
- **Legitimate counterexample:** A requested evaluation is useful when it names the criterion and evidence behind the judgment.
- **Rewrite principle:** Replace the verdict with the supporting fact, or bind the judgment to an explicit criterion.
- **Mechanism:** Review `corpus/prose-integrity/rules.md#STOW-PRO-005` and `corpus/prose-integrity/rules.md#STOW-PRO-013` under the requested voice.

## Mechanical symmetry or fragmentation

- **Description:** Repeated block shapes or excessive fragments make the structure more visible than the content.
- **Rationale:** Mechanical form can hide relationships, split one idea across unnecessary units, or imply false equivalence.
- **Applicability:** Review consecutive sections, bullets, repeated paragraph openings, uniform sentence or paragraph shapes, and short fragments when they repeat one template or divide one thought without purpose.
- **Legitimate counterexample:** Predictable structure helps recurring procedures, comparisons, checklists, and deliberate rhetorical emphasis.
- **Rewrite principle:** Match the structure to the content's function and evidence depth. Avoid mechanical repetition only when it obscures function; do not vary sentence or paragraph length merely to look less uniform. Preserve deliberate parallelism, recurring terminology, house style, and required layouts.
- **Mechanism:** Apply the contextual structure review in `corpus/prose-integrity/rules.md#STOW-PRO-007` while preserving contract-required layouts.

## Heading opacity or unnecessary sectioning

- **Description:** A vague or dramatic heading hides its subject, or a section boundary exists without a navigation benefit.
- **Rationale:** Opaque labels and needless sections force the reader to reconstruct hierarchy instead of following it.
- **Applicability:** Review headings that could label unrelated content and sections that contain too little distinct work.
- **Legitimate counterexample:** Long, reference-oriented, or independently addressable material benefits from explicit section navigation. A requested expressive heading remains valid when it still identifies the subject and does not manufacture risk or importance.
- **Rewrite principle:** Name the section's actual subject and merge boundaries that do not improve retrieval or sequence.
- **Mechanism:** Use the heading check in `corpus/prose-integrity/rules.md#STOW-PRO-016` only when headings are present.

## Epistemic opacity

- **Description:** A claim hides its source, confidence, evidence boundary, attribution, or status as a hypothetical; blanket hedging can hide the specific proposition that is unknown.
- **Rationale:** Readers cannot distinguish verified fact, inference, uncertainty, and invention without those boundaries.
- **Applicability:** Review quantities, history, scenarios, attributed positions, strong certainty, and capability claims.
- **Legitimate counterexample:** Keep justified uncertainty, labeled hypotheticals, and bounded claims when they accurately represent available evidence.
- **Rewrite principle:** State the source or boundary, label inference and hypothesis, and replace stacked generic qualifiers with the specific known and unknown. Remove precision the evidence cannot support, but never remove justified uncertainty.
- **Mechanism:** Apply accuracy before presentation, using `corpus/prose-integrity/rules.md#STOW-PRO-002`, `corpus/prose-integrity/rules.md#STOW-PRO-015`, and `corpus/prose-integrity/rules.md#STOW-PRO-017` through `corpus/prose-integrity/rules.md#STOW-PRO-019`.

## Lexical inflation or cliché clusters

- **Description:** Stock phrasing, vague action verbs, figurative nouns, or dense clichés replace exact wording.
- **Rationale:** Inflated wording can blur the action and make unrelated passages sound interchangeable.
- **Applicability:** Treat closed-list matches as leads and judge the term's function, density, and technical meaning in context. Severity comes from the independent writing harm, not the token or its statistical association with an origin.
- **Legitimate counterexample:** A literal or established technical sense, ordinary vocabulary, quotations, identifiers, and a deliberate requested voice remain valid. A protected quotation, identifier, code, path, or data value is not editable presentation prose.
- **Rewrite principle:** Prefer the shortest term that preserves the exact meaning; keep specialized wording when a plainer substitute would lose precision.
- **Mechanism:** Use the report-only matchers linked to `corpus/prose-integrity/rules.md#STOW-PRO-020` as advisory leads; the active rule owns transition, vague-verb, and stock-phrase signals.

### Compact paired examples

| Pathology | Bounded repair | Preserve |
|---|---|---|
| A generic opener announces that an explanation follows, and the conclusion repeats the already-complete result. | Start on the result; remove the functionless conclusion. | Keep a requested summary, safety reminder, meaningful next step, or navigational close. |
| Three sections use the same opening, sentence count, and closing even though one has substantially more evidence. | Let each section's structure reflect its actual content. | Keep a required template, deliberate parallelism, stable terminology, and house style. |
| A documented fact is wrapped in several generic hedges, while the real unknown is not named. | State the fact, then name the exact unknown and its evidence boundary. | Keep every justified uncertainty; do not manufacture confidence. |
| A figurative stock noun and inflated adjective replace the actual operation, while the same noun also appears as a literal technical term. | Replace only the inflated use with the exact operation. | Keep the literal or technical use and all protected text byte-for-byte. |

Before delivery, ask: Does this match reveal an independent writing harm here?
What legitimate function would a rewrite need to preserve? Which exact fact,
uncertainty, term, voice feature, structure, or protected literal must survive?
