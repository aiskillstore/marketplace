# Conformance guidance (no overclaim)

This reference governs how STOW may describe its own output against the underlying controlled-technical writing standard. It is application guidance, not a restatement of any rule. For the normative text of a cited rule, open its `corpus_ref`.

STOW gives **guided** alignment, never certification. The strict, fully conformant profile is **locked and unavailable in this release**. A cold lexical index can report exact dictionary membership and explicitly listed forms. A caller can also explicitly select a project terminology authority whose approved and nonpreferred forms take precedence over the generic dictionary. Neither mechanism decides meaning, part of speech in context, replacement suitability, technical-term category, authority authenticity, official directives, complete contextual review, final-output validation, or delivery custody. STOW must never state that its output fully conforms on the basis of these lookups alone.

Each group below lists: the observable **Trigger**, the output **Region** it applies to, how STOW **Checks** it (or why the check is unavailable), and a `corpus_ref` **Reference** for the full rule text.

## 1. Conformance-claim guard

- **Trigger:** the assistant is about to label, certify, or otherwise describe output as meeting the controlled-technical writing standard, or a user asks whether output conforms.
- **Region:** assistant statements about output status, not the prose itself.
- **Check:** STOW asserts only guided alignment. It emits no conformance certificate. Any claim of full or strict conformance is downgraded to *guided, partial*, because the strict profile is locked in this release. STOW names which checks ran and which are unavailable instead of making a blanket claim.
- **Reference:** the profile-gated rule set as a whole; representative see corpus/words/selection.md#STOW-WRD-001.

## 2. Dictionary-dependent checks: PARTIAL lexical lookup

- **Trigger:** prose under an active controlled-technical profile whose evaluation would require looking a word up in the controlled dictionary, confirming its approved sense, part of speech, or inflection, testing technical-noun or technical-verb category membership, checking approved connectors, company or industry terminology, phrasal-verb admissibility, or false-friend status.
- **Region:** all-prose, including procedural and descriptive prose; excludes code, structured data, quoted text, and identifiers.
- **Check:** exact membership and explicitly listed-form lookup are available through a cold, sparse index. An explicitly selected project file can add approved and nonpreferred terminology declarations; candidates never become approved, and file presence alone grants no authority. Sense, contextual part of speech, replacement choice, technical-noun or technical-verb category, authority authenticity, and directive checks remain external or contextual. Report which facts and declarations were checked, name the remaining boundary, and never count lookup alone as conformance.
- **Reference:** see corpus/words/selection.md#STOW-WRD-001,
  corpus/words/selection.md#STOW-WRD-002,
  corpus/words/usage.md#STOW-WRD-003, corpus/sentences.md#STOW-SEN-004,
  corpus/style/economy.md#STOW-STY-003, and
  corpus/general-practice.md#STOW-GEN-005.

## 3. Structural and mechanical checks: AVAILABLE (guided)

- **Trigger:** surface features STOW can read directly: words per sentence, sentences per paragraph, length of a multi-word noun, presence of a semicolon, presence of a contraction or an omitted word, and the token-counting mechanics those measures rely on.
- **Region:** procedural, descriptive, and all-prose regions; excludes code, structured data, quoted text, and identifiers.
- **Check:** callable checks measure their declared observable properties over caller-supplied prose; other items remain review guidance. Results support a guided assessment only. Passing them does not establish conformance, because the dictionary-dependent rules in Group 2 stay unverified.
- **Reference:** see corpus/procedures.md#STOW-PRC-001,
  corpus/procedures.md#STOW-PRC-005,
  corpus/descriptions.md#STOW-DSC-003,
  corpus/descriptions.md#STOW-DSC-006,
  corpus/multiword-nouns.md#STOW-MWN-001,
  corpus/punctuation.md#STOW-PCT-001,
  corpus/punctuation.md#STOW-PCT-004, and
  corpus/punctuation.md#STOW-PCT-006.

## 4. Grammar and construction checks: PARTIAL (best-effort, guided)

- **Trigger:** procedural or descriptive prose where clause shape can be read from the text: whether an instruction opens in the imperative, whether a sentence carries more than one instruction, whether a leading condition is separated by a comma, which verb tense and voice appear, and whether an action is expressed as a nominalization.
- **Region:** procedural and descriptive prose.
- **Check:** STOW inspects sentence structure and flags likely deviations. These are judgment calls, not certified parses, so STOW reports them as guidance rather than pass or fail.
- **Reference:** see corpus/procedures.md#STOW-PRC-002,
  corpus/procedures.md#STOW-PRC-003,
  corpus/procedures.md#STOW-PRC-004,
  corpus/verbs/technical-verbs.md#STOW-VRB-002, and
  corpus/verbs/verb-forms.md#STOW-VRB-006.

## 5. Safety checks: ALWAYS ACTIVE (system precedence)

- **Trigger:** the response contains a safety instruction, warning, caution, or hazard notice, whether or not a controlled-technical profile is active.
- **Region:** safety-prose.
- **Check:** STOW reviews the safety item for a risk-level label, a command-or-condition opening, and a stated consequence. These run at system precedence and outrank the profile, but they still yield guided review, not certification.
- **Reference:** see corpus/safety.md#STOW-SAF-001, corpus/safety.md#STOW-SAF-002, corpus/safety.md#STOW-SAF-003.

## Bottom line

Lexical lookup and an explicitly selected project authority do not supply contextual semantics, authenticate the named authority, complete validation, or delivery custody. STOW must not claim that any output fully conforms to the controlled-technical writing standard. Report closed lexical facts and project declarations separately from guided structural and safety review, and name every unavailable boundary.

For vocabulary admission, exact dictionary membership is the closed boundary;
technical nouns, technical verbs, and canonical project terms require an
explicitly selected external terminology authority. STOW can read that
authority without a model call, but it cannot authenticate the source or decide
category and sense.
For approved-word meaning, contextual sense review is intentionally deferred
when an approved meaning is not supplied. These are accounted limitations, not
lexical failures and not evidence of conformance.
