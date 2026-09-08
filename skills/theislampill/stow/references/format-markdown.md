# Mixed-Markdown format reference (embedded literals and data)

Application guidance for Markdown output that carries embedded literals or
structured data. This page is a scanned surface, not rule text. It tells a
reviewer *where* each region boundary falls in a Markdown document, *which*
rules may touch each region, and *how* STOW checks the result. The normative
statement of every rule named here lives only in its cited `corpus_ref` file.
Read the corpus for the wording, never this page.

The contract in one line: apply prose guidance only to editable prose, exclude
recognized literal and serialized regions from advisory prose scans, and use a
named host comparator when a contract requires byte fidelity.

## When this page applies

- **Predicate:** the response is Markdown that contains at least one embedded
  literal or structured-data region: a fenced code block, an inline-code span,
  a block quote, YAML front matter, a data fence, a table cell holding a literal,
  or a bare path, identifier, version, or key inside prose.
- Load it together with `references/protected-regions.md`, which defines how STOW
  recognizes a protected literal. This page adds the Markdown-specific boundaries;
  that page defines the literal itself.

## The region model

A Markdown document is not one surface. It interleaves editable prose with
protected literals and structured regions, and the boundaries follow the
delimiters already in the text: fences, backticks, quotation marks, list layout,
front-matter rules, and table pipes. Split the document at those delimiters, then
apply each rule only to the region its scope names, exactly as the kernel
requires (`SKILL.md` section 2).

Two guidance rules hold across every construct below:

- G1 tells the writer not to apply prose edits to code, structured data, quoted
  text, or an identifier. These regions carry the shared scope `exclude` of
  every prose rule.
- A supported structured-data region can receive an independent G2 verdict.
  A prose finding does not replace that verdict, and the reverse.
  Serialization (band 3) and literals (band 4) outrank the profile and
  presentation bands, so a lexical or shaping preference yields on any conflict.

## Fenced code blocks and inline code

- **Trigger:** a fenced block opened by ``` or `~~~`, or an inline span between
  single backticks.
- **Region:** protected literal under G1 generation guidance.
- **How STOW checks it:** the G2 linter excludes recognized fences and inline
  spans from its read-only advisory scan. It does not compare the actual final
  candidate with source bytes. This is the scope behavior the registry records
  on the protected-literal conflicts: see corpus/punctuation.md#STOW-PCT-006 and
  corpus/words/usage.md#STOW-WRD-014.
- When a fence's info string names a data language, also treat its body as a
  structured region (below).

## Embedded structured-data regions

- **Trigger:** YAML front matter delimited by `---` rules at the top of the
  document, and any fenced block whose info string is a data format (for example
  `json`, `yaml`, or `jsonl`).
- **Region:** one independent serialization region per block.
- **How STOW checks it:** each supported region has its own closed format
  contract (`references/format-json.md`, `references/format-yaml.md`, or
  `references/format-jsonl.md`), and `runtime/validate.py` can return a G2
  verdict for caller-supplied bytes. Delivery custody is external. G1 guidance
  excludes keys, mapping order, and values from prose edits. A detector verdict
  applies only to the supplied region.

## Block quotes and inline quotations

- **Trigger:** a `>` block quote, or quotation marks around attributed text in
  prose.
- **Region:** quoted text. Excluded from the lexical prose rules.
- **How STOW checks it:** G1 guidance excludes the quoted span from spelling
  changes (see corpus/words/usage.md#STOW-WRD-014). Recognized quotations are
  excluded or blanked by the current advisory scan where its mask applies. The
  exact one-token semantics in corpus/punctuation.md#STOW-PCT-006 are not
  implemented by that scan; they remain model- and authority-bound guidance.
  Fidelity to the source and the block layout for a long quotation require
  review or a named host comparator over the actual final candidate; see
  corpus/prose-integrity/rules.md#STOW-PRO-023.

## Paths, identifiers, schema keys, and bare literals

- **Trigger:** a file path, code identifier, schema key, version string, or
  alphanumeric identifier appearing in prose, whether or not it sits in backticks.
- **Region:** identifier. Protected.
- **How STOW checks it:** G1 guidance excludes the token from renaming,
  re-casing, or rewording. Recognized identifier spans are excluded or blanked
  by the current advisory scan. The exact one-token semantics in
  corpus/punctuation.md#STOW-PCT-006 are not implemented by that scan; they
  remain model- and authority-bound guidance. Recognition of a bare, un-fenced
  literal is the finite syntax task described in `references/protected-regions.md`.
  General byte fidelity requires a named host comparator over the actual final
  candidate and authoritative source bytes.

## Headings

- **Trigger:** an ATX (`#`) or setext heading line.
- **Region:** the heading text is editable prose, but two presentation checks
  target headings specifically, and any literal inside the heading stays protected.
- **How STOW checks it:** STOW inspects each heading against the concreteness
  constraint at corpus/prose-integrity/rules.md#STOW-PRO-016. Findings are for
  the author, not auto-fixes.

## Lists and tables

- **Trigger:** a bulleted or numbered list, or a pipe (`|`) table.
- **Region:** list-item and cell prose is editable prose; a cell that holds a
  literal stays protected.
- **How STOW checks it:** a multi-step action sequence is rendered as a numbered
  list rather than a table (see corpus/action-shaping.md#STOW-ACT-002 and
  corpus/action-shaping.md#STOW-ACT-011), and complex conditional text is broken
  into a vertical list (see corpus/sentences.md#STOW-SEN-003). The prose inside
  each item is checked as editable prose against the active profile and
  presentation rules.

## Review and G2 checks

The generation guidance asks the writer to confirm each item. The runtime can
check embedded supported data, but it has no general final-output comparator:

- prose edits are confined to editable-prose regions;
- a named host compares contract-fixed literals with their authoritative values
  when byte fidelity is required;
- every embedded structured-data region parses and schema-checks on its own
  through `runtime/validate.py`;
- the top output contract is obeyed: a raw artifact ships raw, with no added
  prose wrapper or fence.

For how STOW recognizes and bounds a protected literal, defer to
`references/protected-regions.md`. For the band ordering that decides any
cross-region conflict, see `references/activation-and-precedence.md`.
