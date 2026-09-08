# Example: inspect a normalized list

## User says

```text
Report duplicates in this list. Ignore string case and surrounding whitespace, but keep number types distinct: [" A ", "a", 1, 1.0]
```

## Request

The command reads `examples/list-request.json`.

```json
{
  "adapter": "list",
  "mode": "normalized",
  "items": [" A ", "a", 1, 1.0],
  "normalization": {
    "casefold": true,
    "whitespace": "collapse"
  }
}
```

## Command

```text
$ python3 scripts/dedupe.py inspect --request examples/list-request.json
{"adapter": "list", "canonical_count": 3, "canonical_indices": [0, 2, 3], "duplicate_count": 1, "groups": [{"canonical_index": 0, "key_sha256": "980410da9522db17c3ab8743541f192a5ab27772a6154dbc7795ee909e653a5c", "kind": "normalized", "member_indices": [0, 1]}], "identity_conflicts": [], "mode": "normalized", "mutated": false, "normalization": {"casefold": true, "whitespace": "collapse"}, "provenance": [], "similarity_candidates": [], "source_count": 4, "unresolved": [], "unresolved_count": 0, "url_policy": {}}
exit 0
```

## Reply

Inspection found one normalized duplicate group: indices 0 and 1, with index 0 proposed as canonical by first-seen order. Integer `1` and float `1.0` remain separate. Counts reconcile as `4 = 3 + 1 + 0`. No input changed.
