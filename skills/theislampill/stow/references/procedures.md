# Procedural writing: application reference

Compressed application guidance for the procedure rules (`PRC`) and for the
punctuation and word-count rules (`PCT`) as they act on procedural output. This
page tells you **when** each rule fires, **which region** of the response it
governs, and **how STOW checks** it. It does not restate the rules: for the
governed wording, open the cited `corpus_ref` page.

These rules belong to the controlled-technical rules and carry `profile`
precedence, so they apply only while a controlled-technical profile is active
and the response contains procedural prose. Two of them (`PRC-001`, `PRC-003`)
also reach safety-labelled steps. The `PCT` word-count rules do not stand alone
here: they define how the token counting behind the `PRC-001` and `PRC-005`
sentence caps is performed, so read them together with the procedure caps.

Each entry uses the same shape: what puts the rule in play, the output region to
inspect, the validator STOW runs, and the full-text citation.

## Procedures (PRC)

### STOW-PRC-001
- **Fires when:** the response contains numbered or step-form instructions, or safety steps written as sentences.
- **Region:** every sentence inside a step body (procedural and safety scope).
- **How STOW checks:** deterministic length validator `procedural-sentence-max-20-words`, computed with the `PCT` token rules below.
- **Full text:** `corpus/procedures.md#STOW-PRC-001`

### STOW-PRC-002
- **Fires when:** a single step sentence bundles more than one action.
- **Region:** each command sentence in the procedure body; the simultaneous-action exception is set out in the corpus page.
- **How STOW checks:** parser validator `one-instruction-per-sentence`.
- **Full text:** `corpus/procedures.md#STOW-PRC-002`

### STOW-PRC-003
- **Fires when:** the source already authorizes an instruction or safety command. Do not silently strengthen advice, permission, or uncertainty into a command; preserve the source force or request an authority decision.
- **Lexical precedence:** Dictionary status never authorizes changing source force. If a listed alternative cannot be shown to preserve advice, permission, uncertainty, or the named action, preserve the source wording and report the unresolved lexical item.
- **Region:** the opening verb of each step sentence (procedural and safety scope).
- **How STOW checks:** planned parser validator `imperative-mood` can inspect command form only after the authority boundary is resolved. It does not decide whether source advice may become a command.
- **Full text:** `corpus/procedures.md#STOW-PRC-003`

### STOW-PRC-004
- **Fires when:** a step depends on a precondition, state, or timing the reader must know before acting.
- **Region:** the sentence opening and the comma boundary that separates the condition from the command.
- **How STOW checks:** parser validator `condition-first-comma-separator`.
- **Full text:** `corpus/procedures.md#STOW-PRC-004`

### STOW-PRC-005
- **Fires when:** a note is attached to a procedure.
- **Region:** the note text, kept distinct from the surrounding step commands.
- **How STOW checks:** contextual review asks whether the note gives information and does not introduce an action. The separate `STOW-DSC-003` sentence-length predicate supplies the 25-word cap when the note is descriptive prose. STOW does not claim that it can classify note function with a parser.
- **Full text:** `corpus/procedures.md#STOW-PRC-005`

## Punctuation and word count in procedures (PCT)

### STOW-PCT-001
- **Fires when:** a semicolon appears in a step or a note.
- **Region:** all step and note prose.
- **How STOW checks:** deterministic validator `no-semicolon`. Where this meets the presentation-layer em-dash ban (`STOW-PRO-001`), the registry conflict note directs you to use neither and pick the substitute the active profile prescribes.
- **Full text:** `corpus/punctuation.md#STOW-PCT-001`

### STOW-PCT-003
- **Fires when:** parentheses appear in a step or a note.
- **Region:** step and note prose.
- **How STOW checks:** contextual guidance permits parentheses only for references, item identifiers, step identifiers, abbreviations, singular/plural forms, explanations, or alternatives. The named heuristic is planned, not callable.
- **Full text:** `corpus/punctuation.md#STOW-PCT-003`

### STOW-PCT-004
- **Fires when:** a colon introduces a vertical list of steps.
- **Region:** the lead-in line of a vertical or numbered step list.
- **How STOW checks:** deterministic validator `colon-as-sentence-boundary-in-list`. This closes the counted sentence, so the lead-in is measured against the `STOW-PRC-001` cap up to the colon.
- **Full text:** `corpus/punctuation.md#STOW-PCT-004`

### STOW-PCT-005
- **Fires when:** a step or note sentence contains a parenthetical.
- **Region:** the word-count computation for that sentence.
- **How STOW checks:** deterministic validator `parenthetical-counts-as-one-word`, feeding the `PRC-001` (20) and `PRC-005` (25) caps.
- **Full text:** `corpus/punctuation.md#STOW-PCT-005`

### STOW-PCT-006
- **Fires when:** a step or note contains a number, number with unit, abbreviation, identifier, quoted string, title or label, or proper name.
- **Region:** the word-count computation for that sentence.
- **How STOW checks:** contextual guidance counts each listed element as one word. The shipped counter does not yet implement every listed class, so `word-count-token-rules` remains planned rather than a callable compliance predicate. When a token sits in a protected region, preserve it rather than rewriting it to satisfy a count.
- **Full text:** `corpus/punctuation.md#STOW-PCT-006`

### STOW-PCT-007
- **Fires when:** words are joined by a hyphen in a step or note.
- **Region:** the prose that selects the hyphenated relationship and the word-count computation for that sentence.
- **How STOW checks:** contextual guidance permits a hyphen only between directly related words that operate as one unit. The deterministic `count_words` helper then counts that hyphenated group as one word when it feeds the callable sentence caps; it is not an independent delivery gate.
- **Full text:** `corpus/punctuation.md#STOW-PCT-007`
