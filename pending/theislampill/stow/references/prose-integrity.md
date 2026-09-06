# Contextual prose-integrity application

Use this reference when the request calls for deep prose-integrity guidance.
Judge observable effects on meaning, evidence, navigation, and reader effort.
Do not infer authorship or origin from a surface pattern.

The six-field taxonomy is in `references/descriptive-prose.md`. It defines each
phenomenon by description, rationale, applicability, legitimate counterexample,
rewrite principle, and mechanism. The protected
`corpus/prose-integrity/rules.md` module carries fuller rule text and examples;
apply it through the registry's current qualifiers and precedence.

## Guidance and detection are different

Most prose-integrity rules require contextual G1 review. A listed word,
transition, punctuation mark, heading shape, or paragraph form is not a defect
by itself. Its function in the requested text determines whether revision helps.

`runtime/lint_prose.py` supplies advisory G2 surface detectors for contextual G1
rules. It also implements the four closed G2 compliance predicates named in the
registry. Each check reports only the closed observation it implements over its
masked input. Its public findings retain stable rule identifiers and use neutral
pattern labels. It does not determine
authorship, semantic quality, requested voice, or delivery acceptance.

The CLI exits successfully even when it reports findings or cannot read the
input. A host that needs a blocking policy must define that policy separately;
this repository does not supply a general prose delivery gate.

## Observable review groups

- **Semantic repetition:** remove repeated meaning only when the later passage
  adds no correction, safety value, navigation, emphasis, or terminology value.
- **Empty metadiscourse:** remove framing and process narration that do not
  change the claim, limitation, method, or next action.
- **Manufactured contrast or escalation:** keep contrast and intensity only
  when the discourse or evidence earns them.
- **Hollow evaluation:** bind praise, criticism, or importance to an explicit
  criterion and supporting fact.
- **Mechanical symmetry or fragmentation:** combine or vary repeated shapes
  when their form obscures the relationship between ideas.
- **Heading opacity or unnecessary sectioning:** use a section boundary only
  when it improves navigation, retrieval, or sequence.
- **Epistemic opacity:** identify the source, confidence, evidence boundary,
  attribution, or hypothetical status when it affects the claim.
- **Lexical inflation or cliché clusters:** prefer exact wording, while keeping
  established technical senses, quotations, identifiers, and requested voice.

## Callable advisory signals

The linter can report ten bounded advisory observations: an em dash, an empty
intensifier, a filler phrase, a formulaic `whether you're` opener, a hedging
cluster, a listed transition, a listed action verb, a listed academic phrase,
an unresolved generated placeholder, or a contraction under the controlled profile. These
reports are leads for contextual review. In particular:

- punctuation is not an authorship signal and remains valid under an applicable
  style contract;
- an ordinary connector is valid when it expresses a useful logical relation;
- a listed verb is valid in a precise technical, financial, literal, or domain
  sense;
- a hedge is valid when it represents real uncertainty;
- a repeated layout is valid for procedures, comparisons, checklists, and other
  contract-required structures.

The four blocking-capable G2 predicates are the procedural sentence cap, the
descriptive sentence cap, the controlled-profile semicolon rule, and the Latin
abbreviation rule. They establish only those closed properties; delivery remains
a separate host policy.

For one rule, run `python runtime/query_rules.py <ID>` when execution is
available. Otherwise use `references/rule-index.md` to locate its registry
record and bounded corpus section.

## Region and custody boundary

The advisory linter masks a finite set of recognizable code, quotation,
identifier, and structured-data spans while retaining positions. This is scan
preprocessing, not semantic region classification or final-byte custody. A
caller-supplied or syntactically inferred region can still be wrong, and a clean
advisory report proves only that the implemented patterns were absent from the
supplied observable prose.
