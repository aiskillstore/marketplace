# Protected regions (mask first, scan second)

Protected regions are spans the generation guidance tells a writer not to edit
on its own: code, quotations, machine identifiers, and serialized data. The
shipped implementation is narrower. `runtime/lint_prose.py` blanks recognized
spans in an in-memory copy before its advisory scans and never edits the input.
This behavior is STOW-authored, so no `corpus_ref` citation applies.

The masking functions cover their documented fence, inline-code, block-quote,
URL, path, and identifier patterns. Spaces replace matched characters while line
and column geometry stays stable. Different advisory checks use the masking
layer suited to that check, so the implementation is a finite syntax recognizer,
not a semantic partition of arbitrary text.

The exclusion is declared per rule in `skills/stow/rules/registry.yaml` under
`scope.exclude` (every prose record excludes `code`, `structured-data`,
`quoted-text`, and `identifiers`). Serialized spans are additionally validated
for well-formedness by `skills/stow/runtime/validate.py`, which reads them but
never mutates them.

## Guidance and runtime behavior

1. **Bound.** Generation guidance uses visible delimiters and the declared
   output contract to identify protected material.
2. **Mask for advisory scans.** The linter blanks only the span patterns its
   code recognizes and scans the copy.
3. **Keep custody external.** A host that requires byte fidelity must compare
   the actual final candidate with the authoritative literals and block a
   mismatch.

A linter finding may still refer to the text around a blanked span. The linter
does not rewrite either the span or its surroundings.

## Region taxonomy

Each entry gives the observable trigger, the region the linter attempts to
mask, and the advisory effect. It is grouped by `scope.exclude` class.

### Code (`scope.exclude: code`)

- **Fenced code blocks.** Trigger: a line opening with a triple-backtick or
  triple-tilde fence, through the matching closing fence at the same indent.
  Region: the fence lines and everything between them. G1 guidance tells the
  writer to exclude that region from prose edits. For its finite G2 advisory
  scan, the linter locates a recognized fence pair and masks the whole block.
- **Inline code.** Trigger: a backtick-delimited span inside prose. Region: the
  span including its backticks. G1 guidance treats the span as protected. The
  G2 linter masks recognized inline spans in its read-only scan copy.

### Serialized data (`scope.exclude: structured-data`)

- **Schema keys.** Trigger: an object key or field name in serialized data (for
  example a mapping key in YAML or JSON). Region: the key token. G1 guidance
  excludes it from prose edits. A supported serialized payload can receive a
  separate G2 parse verdict from `validate.py`, which is read-only.
- **Serialized-data spans.** Trigger: a recognizable JSON, JSONL, or YAML
  fragment (structural punctuation, quoting, and indentation). Region: the whole
  serialized span. G1 guidance excludes it from prose edits. The G2 linter masks
  only the serialized forms it recognizes, and `validate.py` can check a
  caller-supplied supported payload separately.

### Quotations (`scope.exclude: quoted-text`)

- **Block quotations.** Trigger: a line prefixed with a block-quote marker, and
  its continuation lines. Region: the quoted lines. G1 guidance tells the writer
  not to rewrite borrowed wording. The G2 linter masks recognized block quotes
  only in its read-only scan copy. Neither mechanism proves byte fidelity in the
  actual final candidate.

### Identifiers (`scope.exclude: identifiers`)

- **File paths.** Trigger: a slash- or backslash-delimited path, with or without
  an extension. Region: the full path token. G1 guidance excludes it from prose
  edits; the G2 linter masks a recognized path in its scan copy.
- **Identifiers.** Trigger: an alphanumeric symbol, a dotted or snake/camel name,
  or a code-like token. Region: the identifier token. G1 guidance excludes it
  from prose edits; the G2 linter masks the finite identifier forms it recognizes.
- **URLs.** Trigger: a `scheme://host/...` reference or a bare host with a path.
  Region: the whole URL. G1 guidance excludes it from prose edits. The G2 linter
  masks recognized URLs in its scan copy, where word-length scanners see one
  placeholder.

## Claim boundary

The shipped linter masks a finite set of recognizable spans before advisory
scanning; because it is read-only, it performs no restoration step and proves no
general final-output byte preservation.

Byte-preserving generation remains G1 guidance unless a named host owns the
actual final candidate, compares it with authoritative bytes, blocks mismatch,
and rechecks after any permitted repair.
