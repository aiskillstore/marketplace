# Descriptive writing (DSC): application reference

Compressed application guidance for the active descriptive-writing rules. Use
this to know **when** each rule
fires, **which region** of a response it governs, and **how STOW verifies** it.
This file does not restate the rules: for the normative wording, open the cited
`corpus_ref`.

**When the group is active.** These rules apply only while a controlled-technical
writing profile is active and the response contains *descriptive* prose:
explanatory text about how something is or works, as distinct from step-by-step
instructions.

**Region (all DSC rules).** Descriptive prose only. Excluded: code, structured
data, quoted text, and identifiers. Procedural steps, notes, and safety notices
fall under their own groups, not these.

**How to read each entry.** *Trigger* = the observable condition that activates
the rule. *Check* = the STOW enforcement mechanism (kind + validator, with the
configured numeric limit where one applies). *Full text* = the corpus citation.

## Sentence-level

### STOW-DSC-001: pace of new information
- Trigger: a descriptive sentence that mixes unrelated subjects, or a passage that front-loads several facts before the reader has absorbed the first.
- Check: semantic-review; validator `gradual-info-one-subject-per-sentence`. The reviewer confirms that the passage introduces one topic and its facts at a time. Closely related subjects can stay coordinated when that is clearer; do not repeat full subjects mechanically.
- Full text: see `corpus/descriptions.md#STOW-DSC-001`.

### STOW-DSC-003: descriptive sentence length
- Trigger: any sentence inside descriptive prose.
- Check: deterministic word count per sentence; validator `descriptive-sentence-max-25-words`, limit 25. Word counting follows the punctuation-group token conventions (parenthetical text, a hyphenated group, numbers, quoted text, and identifiers each count as one word: see `corpus/punctuation.md#STOW-PCT-004` through `corpus/punctuation.md#STOW-PCT-007`).
- Precedence: on conflict with the presentation-layer *vary structure* preference (`STOW-PRO-007`), the cap governs: vary length below the limit, never above it.
- Full text: see `corpus/descriptions.md#STOW-DSC-003`.

## Paragraph-level

### STOW-DSC-004: grouping into paragraphs
- Trigger: descriptive prose that covers several related facts without organizing them into topic-led paragraphs.
- Check: semantic-review; validator `paragraph-topic-grouping`. The reviewer
  confirms related sentences are grouped, each paragraph opens on its topic,
  and a second topic starts a new paragraph.
- Full text: see `corpus/descriptions.md#STOW-DSC-004`.

### STOW-DSC-006: paragraph sentence count
- Trigger: a paragraph in descriptive prose.
- Check: deterministic sentence count per paragraph; validator `paragraph-max-6-sentences`, limit 6. A colon inside a vertical list closes a sentence for this count (see `corpus/punctuation.md#STOW-PCT-004`).
- Full text: see `corpus/descriptions.md#STOW-DSC-006`.
