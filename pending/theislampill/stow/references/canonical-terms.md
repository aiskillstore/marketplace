# Closed canonical terms and project terminology

Load this reference only when the host supplies an explicit canonical-term map
or explicitly selects a project terminology authority. File presence alone is
not authority and never activates the project overlay. The runtimes use only
the Python standard library.

For a closed map, run
`python runtime/validate_terms.py --map MAP.json --segments SEGMENTS.json`.

For a project authority, run either:

```text
python runtime/dictionary_lookup.py --authority PROJECT.json lookup TERM
python runtime/dictionary_lookup.py --authority PROJECT.json scan --segments SEGMENTS.json
```

The project file follows `rules/project-terminology.schema.json`. It records a
declared authority and candidate, approved, or rejected technical nouns,
technical verbs, abbreviations, and canonical terms. The runtime never writes
the file and never promotes a candidate. Optional good and bad examples are
sparse record context, not authority and not sense proof. Each example declares
whether its origin is `project-authority` or `stow-synthetic`.

Lookup precedence is: caller-labeled protected text; an explicitly selected
project authority; the fixed controlled dictionary; then unresolved contextual
review. An approved project declaration can prevent the generic dictionary from
rewriting that surface. This proves only the supplied declaration. Term
category, intended sense, authority authenticity, and contextual suitability
remain external or contextual.

When the source names an operation or carries advice, permission, uncertainty,
or a time relation, do not substitute it solely because lookup reports an
alternative. A replacement is permitted only when contextual review establishes
equivalent meaning and force. Otherwise preserve the source term, report the
item as unresolved, and do not claim controlled-language conformance.

Approved records can declare approved and nonpreferred forms. The scan reports
a declared nonpreferred form with its supplied preferred form, which supports
consistent reuse without inventing synonyms. Collisions, duplicate keys, and
malformed authority data fail closed. Candidate records remain unresolved even
when the fixed dictionary also reports a lexical fact.

## G2 result boundary

The map is closed. It declares the terms to inspect, the forbidden variants,
the case mode, and either literal or token matching. The candidate separately
labels each text segment as `editable` or `protected`. The validator scans only
segments labeled `editable` and emits one JSON object:

- `COMPLIANT`, exit zero: no declared forbidden variant was found in a supplied
  editable segment.
- `NONCOMPLIANT`, exit one: at least one declared forbidden variant was found.
- `UNKNOWN`, exit two: the map or candidate was invalid, ambiguous, missing, or
  otherwise unobservable.

JSON strings use ASCII escapes, so the result is independent of the host stdout
encoding. A JSON parser recovers the original Unicode strings.

Each finding reports a zero-based segment index, the declared canonical value,
the forbidden variant, and start-inclusive, end-exclusive character offsets.
A list-valued canonical declaration remains a list in the finding. The runtime
does not select a preferred member that the map did not identify.

`COMPLIANT` is a G2 label-policy result. It does not prove that a concept was
present, that a canonical sense was correct, that a caller label was true, or
that the checked bytes were the final candidate.

## Map and candidate contracts

The map object has exactly `schema_version`, `case_sensitive`, and `entries`.
The version is `1`, the case flag is boolean, and entries is nonempty. Each
entry has exactly `canonical`, `forbidden_variants`, and `match`. The term
fields are a nonempty string or a nonempty list of nonempty strings. Match is
`literal` or `token`. Duplicate terms and collisions under the declared case
mode make the result `UNKNOWN`. Case-sensitive terms compare exactly.
Case-insensitive terms use mutual escaped full matches under Python
`re.IGNORECASE`, the same equivalence semantics used during scanning. This
keeps ownership validation aligned with matching while preserving original-text
offsets.

The candidate object has exactly `schema_version` and `segments`. The version
is `1`, and segments is nonempty. Each segment has exactly `kind` and `text`.
Kind is `editable` or `protected`, and text is a string. A candidate with no
editable segment returns `UNKNOWN`.

Literal matching uses exact substrings under the declared case mode. Token
matching also requires a non-word boundary at an edge when the variant starts
or ends with a word character.

## Host conditions for G3

The host owns the conditions needed to promote this G2 check into a G3 gate:

1. Supply trustworthy segmentation.
2. Run the validator against the actual final candidate in host custody.
3. Block delivery on `NONCOMPLIANT` and `UNKNOWN`.
4. Repair only the editable candidate where the host contract permits it.
5. Revalidate the repaired final candidate before delivery.

Without a named host contract that supplies all five conditions, report only
the G2 result.

## Valid but wrong labels

A structurally valid candidate can label protected-looking bytes `editable`
and editable-looking bytes `protected`. The runtime deterministically scans the
first and ignores the second because it applies caller labels as policy. This
negative control proves label-policy mapping only. It cannot establish semantic
classification, trustworthy segmentation, final-output custody, or G3.
