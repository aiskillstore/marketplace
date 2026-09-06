# Controlled-technical writing profile: application reference

This reference is compressed application guidance for the controlled-technical
writing profile: **when and where** each rule fires, **which output region** it
governs, **how STOW checks it**, and a link to the corpus file that holds the
full normative text. It does not restate the rules themselves: read the linked
corpus file for the wording that governs.

**Guided, not conformant.** This profile is *guided*. STOW applies the checks
below as best-effort shaping of prose. Passing them is not a claim of full
conformance to any controlled-language standard, and it does not certify the
output against the external standard the rules trace to. Treat a clean pass as
*shaped toward the controlled-technical rules*, not *verified compliant*.

**Activation gate (shared by every rule here).** These are profile-precedence
rules. They apply only when a controlled-technical writing profile is active and
the response contains prose. They govern prose only and skip the protected
regions: code, structured data, quoted text, and identifiers. Unless a row says
otherwise, the region is *all prose*; the two exceptions are called out
explicitly.

**Sparse dictionary lookup.** When this profile is active and dictionary
checking is useful, pass only caller-labelled editable segments to
`runtime/dictionary_lookup.py scan --segments <file>`, then retrieve the few
matched records. The helper reports closed membership, preserved alternatives,
and explicitly listed forms. It does not decide part of speech, sense,
technical-noun or technical-verb status, the correct replacement, or
conformance. It skips caller-labelled protected segments and does not classify
regions itself.

A listed alternative is evidence to review, not replacement authorization.
Before a repair, confirm that it preserves the source action, force, time
relation, and intended meaning. If that equivalence is not established,
preserve the source term and mark the item unresolved rather than substituting
a different operation or weakening advice merely to remove a lexical finding.

**How to read each entry.** Every row names the *observable trigger* (the output
feature that invokes the check), the *region*, *how STOW checks it* (the
enforcement kind plus the named validator, with any numeric limit), and the
*corpus_ref* for the governing text. The controlled-technical rules are grouped
below as WRD (words), MWN (multi-word nouns), VRB (verbs, voice, tense), SEN
(sentences, lists, articles), STY (writing-practice consistency), and GEN
(general recommendations).

## WRD: words

| Rule | Observable trigger | Region | How STOW checks | Full text |
| --- | --- | --- | --- | --- |
| WRD-001 | Controlled vocabulary is requested and dictionary or explicitly selected project terminology authority is available | all prose | sparse deterministic lookup applies protected, project, fixed-dictionary, then unresolved precedence; the project supplies approval while technical category and sense remain contextual | see corpus/words/selection.md#STOW-WRD-001 |
| WRD-002 | An approved word is used in a part of speech or inflected form, including a past participle used as an adjective | all prose | deterministic lookup can confirm an explicitly listed form; contextual review still decides actual part of speech and role | see corpus/words/selection.md#STOW-WRD-002 |
| WRD-003 | An approved meaning is supplied for contextual review | all prose | contextual guidance only; lexical membership and listed alternatives do not establish sense or equivalent action, so preserve the source and defer when the required meaning is unavailable | see corpus/words/selection.md#STOW-WRD-003 |
| WRD-007 | A technical-noun token is functioning as a verb | all prose | parser · `no-technical-noun-as-verb` | see corpus/words/selection.md#STOW-WRD-007 |
| WRD-008 | An explicitly selected project authority declares a preferred technical noun | all prose | deterministic sparse lookup reports the declaration and its nonpreferred forms; file presence and candidate status grant no authority | see corpus/words/usage.md#STOW-WRD-008 |
| WRD-010 | A candidate technical noun looks regional, slang, or jargon | all prose | semantic-review · `no-slang-or-jargon-noun` | see corpus/words/usage.md#STOW-WRD-010 |
| WRD-011 | A referent, logical relation, or recurring work context is named more than once | all prose | contextual review · keep one technical noun per referent, preserve key words and key phrases that organize the logic, and reuse the same wording for the same recurring context | see corpus/words/usage.md#STOW-WRD-011 |
| WRD-014 | A word has a spelling variant (skips quoted text) | all prose | deterministic · `american-english-spelling` | see corpus/words/usage.md#STOW-WRD-014 |

WRD-011 and WRD-014 carry recorded conflict resolutions (with the presentation
layer and with protected regions respectively); the corpus file states the
resolution.

## MWN: multi-word nouns

| Rule | Observable trigger | Region | How STOW checks | Full text |
| --- | --- | --- | --- | --- |
| MWN-001 | A coined or approved noun phrase contains stacked nouns or modifiers | all prose | contextual review · keep it to three words and keep coined terms short and easy; for a longer approved term, preserve same-item identity, write it in full first, and then restructure it or use an approved abbreviation, clear hyphenation, or declare a new short form before reuse; preserve clear natural pronoun coordination instead of repeating full subjects only to make reference explicit; project-authorized terms and protected identifiers take priority; no noun parser is claimed | see corpus/multiword-nouns.md#STOW-MWN-001 |

## VRB: verbs, voice, and tense

| Rule | Observable trigger | Region | How STOW checks | Full text |
| --- | --- | --- | --- | --- |
| VRB-002 | A verb carries tense or aspect marking | all prose | contextual guidance · allow only infinitive, imperative, simple present, simple past, simple future, and a listed past participle used as an adjective; the named parser is planned, not callable | see corpus/verbs/technical-verbs.md#STOW-VRB-002 |
| VRB-005 | An `-ing` word appears outside a declared technical noun | all prose | contextual guidance · decide whether the form is verbal, a technical noun, or a modifier; no reliable parser is claimed | see corpus/verbs/technical-verbs.md#STOW-VRB-005 |
| VRB-006 | A clause is in the passive voice | all prose | parser · `active-voice-required-unless-agentless-descriptive` | see corpus/verbs/verb-forms.md#STOW-VRB-006 |
| VRB-007 | An action is expressed as a noun, or a technical verb is used in a non-verb role | all prose | contextual review · express the action with the verb; a listed past participle can act as an adjective | see corpus/verbs/verb-forms.md#STOW-VRB-007 |

## SEN: sentences, lists, and articles

| Rule | Observable trigger | Region | How STOW checks | Full text |
| --- | --- | --- | --- | --- |
| SEN-002 | A contraction or a dropped word appears | all prose | deterministic · `no-contractions-no-word-omission` | see corpus/sentences.md#STOW-SEN-002 |
| SEN-003 | A sentence packs complex or enumerated content | all prose | heuristic · `vertical-list-formatting` | see corpus/sentences.md#STOW-SEN-003 |
| SEN-004 | Adjacent sentences share a related topic | all prose | heuristic · `approved-connectors-only` | see corpus/sentences.md#STOW-SEN-004 |
| SEN-005 | A noun or multi-word noun appears without an article or demonstrative | all prose | parser · `article-and-demonstrative-usage` | see corpus/sentences.md#STOW-SEN-005 |

## STY: writing-practice consistency

| Rule | Observable trigger | Region | How STOW checks | Full text |
| --- | --- | --- | --- | --- |
| STY-001 | A sentence where a word-for-word swap does not hold | all prose | semantic-review · `rewrite-construction-preserve-meaning` | see corpus/style/economy.md#STOW-STY-001 |
| STY-003 | A verb-plus-particle pairing appears | all prose | parser · `no-phrasal-verbs` | see corpus/style/economy.md#STOW-STY-003 |

## GEN: general recommendations

| Rule | Observable trigger | Region | How STOW checks | Full text |
| --- | --- | --- | --- | --- |
| GEN-002 | A `with` phrase has two plausible attachments | all prose | contextual guidance · name the intended attachment and leave a clear `with` phrase unchanged | see corpus/general-practice.md#STOW-GEN-002 |
| GEN-003 | A pronoun appears | all prose | parser · `approved-and-unambiguous-pronoun` | see corpus/general-practice.md#STOW-GEN-003 |
| GEN-005 | A source-language form or intended English meaning is supplied | all prose | external meaning authority plus contextual guidance; spelling resemblance alone is not evidence of a false friend | see corpus/general-practice.md#STOW-GEN-005 |
| GEN-006 | A Latin-derived abbreviation appears | all prose | deterministic · `no-latin-abbreviations` | see corpus/general-practice.md#STOW-GEN-006 |
| GEN-007 | A human role is named and gender is unknown or irrelevant | all prose | contextual guidance · name the role or use an inclusive reference; preserve gender when supplied or materially relevant | see corpus/general-practice.md#STOW-GEN-007 |
