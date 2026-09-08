# Closed-list advisory lookup

The protected self-check material points here for the location and limits of
the shared term lists. This page is a pointer, not a copy.

- **Data location.** The versioned term, phrase, and construction tables live
  in `corpus/prose-integrity/banned-lists.md`.
- **Callable mechanism.** `runtime/lint_prose.py` reads selected tables and
  reports closed matches with stable rule identifiers and neutral labels.
- **Guidance-only tables.** Adjective and metaphor tables remain guidance-only.
  The runtime does not match them because literal technical uses and figurative
  uses need contextual judgment; their presence in the corpus is not a ban.
- **Region handling.** The linter masks a finite set of recognizable protected
  spans before it scans. Masking is advisory preprocessing; it is not semantic
  classification or final-output preservation.
- **Interpretation.** A match is evidence that a declared surface pattern is
  present. It is not evidence of authorship, poor quality, or a required rewrite.
  Review its discourse function, density, technical sense, requested voice, and
  legitimate counterexamples under `references/descriptive-prose.md`.

The linter can miss an undesirable construction that is not in its closed
tables and can report a legitimate use that needs no change. Its CLI does not
block delivery. Treat every finding as an advisory lead and report only the
observable pattern that was found.
