# Text and list adapters

Owner: `dedupe`. Load when the `text` or `list` adapter is selected. Backlink: `SKILL.md` PD-002.

## Text adapter

### Unit

Declare one unit before comparison:

- line
- paragraph
- section
- message
- document
- caller-supplied string item

Changing the unit changes the result. Do not split or join content silently.

### Exact key

Use the literal string or declared byte encoding. Preserve line endings, Unicode form, whitespace, punctuation, and case.

### Normalized key

Disclose transformations and order. The deterministic inspector supports:

- `unicode`: a Python Unicode normalization form, default `NFC`
- `casefold`: boolean, default `false`
- `whitespace`: `preserve` or `collapse`, default `preserve`

Other changes, including punctuation removal, markup stripping, stemming, transliteration, or diacritic removal, need an explicit external policy and must remain visible in the report.

### Similarity

The inspector uses Python `difflib.SequenceMatcher` on normalized strings. Require `similarity_threshold` between 0 and 1. Report pairwise scores and do not collapse items.

For another algorithm, record its name, version, representation, threshold, and reason. Re-run the logic audit before accepting candidates.

### Canonical and merge

Default to first-seen only when source order matters. For paragraphs or documents, compare unique passages before selecting. Preserve additions and disagreements in the conflict ledger.

## List adapter

### Unit and order

Each array member is one item. Preserve:

- original index
- value type
- stable order
- multiplicity
- structured member boundaries

Do not turn a list into a set before provenance and multiplicity are recorded.

### Exact key

Use canonical JSON with types preserved. Exact equality does not coerce strings, numbers, booleans, nulls, arrays, or objects.

### Normalized key

For scalar strings, apply the declared text normalization. Prefix comparison keys with the source type so string `"1"`, integer `1`, float `1.0`, and boolean `true` remain distinct.

Structured arrays and objects use canonical JSON unless a schema-specific record policy is selected. Do not flatten nested structures.

### Retention policies

Supported deterministic policies include:

- keep first
- keep last
- keep an explicit index
- keep by a disclosed score and tie-breaker

Stable order defaults to the first appearance of each canonical item. If multiplicity is meaningful, report duplicates without reducing the list.

## Request examples

Text normalized inspection:

```json
{
  "adapter": "text",
  "mode": "normalized",
  "items": [" Café ", "café", "tea"],
  "normalization": {
    "unicode": "NFKC",
    "casefold": true,
    "whitespace": "collapse"
  }
}
```

List exact inspection:

```json
{
  "adapter": "list",
  "mode": "exact",
  "items": ["a", "a", 1, "1"]
}
```

## Adapter checks

- The item unit is explicit.
- Exact and normalized groups are labeled separately.
- String normalization is recorded.
- Types and source indices remain visible.
- Similarity candidates do not reduce counts.
- Canonical order and multiplicity policy are stated.
