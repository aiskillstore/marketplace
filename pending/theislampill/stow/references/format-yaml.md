# YAML output contract

Application guidance for the YAML surface. This is a reference, not a rule
statement: it says *when* the contract applies, *which region* it covers, and
*how STOW checks* it, then points at the checker and the governing corpus
entries. It does not restate any rule's normative text.

STOW emits YAML only when the caller asks for YAML. That output is a
machine-readable, structured-data surface, not prose. Every record in the
registry excludes `structured-data` from its scope, so the controlled-technical
and presentation rules do **not** scan the keys, structure, or scalar tokens of
a YAML document. The surface instead has a mechanical serialization
contract, checked deterministically by the packaged G2 checker
`runtime/validate.py` (`python runtime/validate.py --format yaml <file>`). Run
it on a supplied file to obtain that bounded verdict. A named host creates a G3
delivery gate only when it gives the checker the actual final candidate, blocks
nonzero or unreadable results, permits only authorized repairs, and revalidates
before delivery. Semantics are YAML 1.2 core (safe) schema.

## The contract

Each item below is an observable trigger, the region it covers, and how STOW
checks it. Unless noted, the checker is `runtime/validate.py`.

- **Parse the supplied candidate.** Trigger: a YAML candidate submitted to the
  checker. Region: the whole stream, every document in it. How checked: the G2
  checker composes the input with a safe loader pinned to version 1.2; parser
  failure produces a nonzero verdict. Only the named-host G3 conditions above
  can make that verdict block delivery.

- **Spaces, never tabs, for indentation.** Trigger: nesting a mapping or
  sequence. Region: the leading whitespace of every line. How checked: a tab in
  indentation is not valid 1.2 indentation and surfaces as a parse error above.

- **Quote ambiguous scalars.** Trigger: a plain scalar that a reader easily
  misreads as a boolean (`yes`, `no`, `on`, `off`, `y`, `n`) or that would
  otherwise resolve unexpectedly. Region: scalar keys and values. How checked:
  the checker resolves such tokens to strings under 1.2 but reports each as an
  advisory warning; STOW quotes the intended string so the value cannot be
  misread. Warnings do not change exit status, so quote proactively rather than
  relying on the warning.

- **Reject duplicate keys by source token.** Trigger: the same key written twice
  in one mapping. Region: every mapping node. How checked: the checker walks the
  node graph and compares the raw source token of each scalar key (its written
  text plus resolved tag), never the resolved value. So `1:` and `1.0:` are
  distinct keys, `0x10:` and `16:` are distinct keys, and only the identical
  token appearing twice is a duplicate and an error.

- **Custom tags, anchors, and aliases are off unless requested.** Trigger: a
  `!tag` outside the 1.2 core set, an `&anchor`, an `*alias`, or the merge key
  `<<`. Region: any node. How checked: the checker rejects any non-core tag and
  any declared anchor or alias reuse as errors. Emit these constructs only when
  the caller explicitly asks for them.

- **No leading BOM; UTF-8 only.** Trigger: a byte-order mark or non-UTF-8 bytes.
  Region: the file head and the whole byte stream. How checked: the checker
  rejects a leading U+FEFF, and the command line rejects input that is not valid
  UTF-8.

## Where the prose rules stop

Trigger: STOW producing YAML while a controlled-technical profile is active.
Region: keys, identifiers, quoted literals, and scalar tokens are structured
data rather than editable prose. G1 guidance tells the writer not to rename a
key or identifier or edit quoted text for a lexical preference. The G2 linter
excludes only recognized syntax from its read-only advisory scan, while
`runtime/validate.py` can return a parse verdict for a supplied YAML payload.
Neither mechanism proves preservation in the actual final candidate. General
preservation requires a named host to compare the actual final candidate with
authoritative bytes, block a mismatch, and revalidate after any permitted
repair. The governing records are `corpus/words/usage.md#STOW-WRD-014`,
`corpus/punctuation.md#STOW-PCT-006`, and
`corpus/prose-integrity/rules.md#STOW-PRO-020`.

## Deliver once

Trigger: any raw-output request (no fence, no commentary). Region: the entire
reply. G1 guidance says to compose one raw artifact with no fence or commentary.
The G2 checker can report only on bytes it receives. If it cannot run, its result
is unknown and STOW cannot claim that the artifact was validated. A named host
that owns the actual final candidate may block that unknown result under the G3
conditions above. Validation status belongs outside the raw artifact; a repair,
when authorized, replaces the draft and is revalidated before delivery.
