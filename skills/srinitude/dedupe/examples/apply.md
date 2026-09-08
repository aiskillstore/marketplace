# Example: apply an approved in-memory plan

## Prior evidence

`examples/inspect.md` reported one normalized group, `[0, 1]`, and proposed index 0 as canonical. The source list and policy have not changed.

## User says

```text
Apply that exact plan to the list. Keep index 0, omit index 1, and preserve the remaining order.
```

## Approved plan

```json
{
  "source": [" A ", "a", 1, 1.0],
  "actions": [
    {
      "action": "omit-index",
      "index": 1,
      "canonical_index": 0
    }
  ],
  "destination": "reply only",
  "conflicts": [],
  "preserve_order": true
}
```

## Result

```json
[" A ", 1, 1.0]
```

## Verification

- Planned actions: 1
- Applied actions: 1
- Skipped actions: 0
- Failed actions: 0
- Output count: 3
- Reinspection under the approved normalization finds no remaining duplicate.

No file or persisted record changed. Authority covered only the returned in-memory list.
