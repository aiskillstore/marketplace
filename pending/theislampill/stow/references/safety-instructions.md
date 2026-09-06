# Safety-instruction references (SAF group)

Application guidance for the three safety rules: `STOW-SAF-001`, `STOW-SAF-002`,
and `STOW-SAF-003`. This page is a scanned surface, not the rule text. It tells a
reviewer *when* each rule fires, *which* region of the output it governs, and
*how* STOW checks it. The normative statement of each rule lives only in the
cited `corpus_ref` file. Read the corpus for the wording, never this page.

These are the highest-precedence rules in the registry: all three sit in the
**system** precedence band and outrank every profile-band and presentation-band
rule on conflict.

## Shared trigger and region

- **Trigger (all three):** the response emits a safety notice: a warning, a
  caution, a hazard callout, or any instruction whose purpose is to prevent
  injury, death, or damage. Unlike the controlled-technical profile rules, these
  do **not** wait for a writing profile to be active. The activation predicate is
  the presence of a safety notice alone, so the SAF rules fire in any response
  that contains one.
- **Region:** the safety-prose block only. STOW excludes code, structured data,
  quoted text, and identifiers from the check: the rules govern the notice's own
  prose, not surrounding material.
- **Granularity:** the checks apply per safety notice. Each warning or caution in
  the response is evaluated on its own.

## Per-rule checks

### STOW-SAF-001: risk-level identification

- **Fires when:** a safety notice is present in the safety-prose region.
- **How STOW checks it:** semantic review (`safety-risk-level-label`). STOW
  inspects each notice for the risk-level signal word that heads it and confirms
  the chosen level matches the severity, using the level classification defined in
  the corpus. Not auto-fixed: flagged for the author.
- **Full text:** see corpus/safety.md#STOW-SAF-001.

### STOW-SAF-002: opening of the notice

- **Fires when:** a safety notice is present in the safety-prose region.
- **How STOW checks it:** parser (`safety-starts-with-command-or-condition`).
  STOW reads the opening of each notice's instruction line and confirms it begins
  in the form the corpus specifies, rather than with an abstract lead-in. Not
  auto-fixed: flagged for the author.
- **Full text:** see corpus/safety.md#STOW-SAF-002.

### STOW-SAF-003: statement of the risk

- **Fires when:** a safety notice is present in the safety-prose region.
- **How STOW checks it:** semantic review (`safety-states-consequence`). STOW
  confirms each notice carries the explanatory clause the corpus calls for, so the
  reader can see the outcome tied to the instruction. Not auto-fixed: flagged for
  the author.
- **Full text:** see corpus/safety.md#STOW-SAF-003.

## Applying the group together

A single safety notice is normally in scope of all three checks at once: it needs
the correct label, the specified opening, and the explanatory clause. When STOW
reports SAF findings, resolve them against the corpus text for each rule above,
and remember that a system-band SAF finding takes precedence over any profile- or
presentation-band finding on the same span.

Meeting the required notice order does not authorize changing the named operation.
If a dictionary alternative could denote a different action, preserve the source
operation and report the lexical item as unresolved unless contextual authority
establishes equivalence.
