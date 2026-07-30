# Audit contract

The verifier accepts one JSON object.

| Field | Requirement |
|---|---|
| `snapshot_date` | Non-empty date or label |
| `records` | List with unique non-empty `id` values |
| `observations` | List with unique non-empty `id` values |
| `links` | List of one-to-one record and observation links |
| `record_dispositions` | Unlinked record IDs with `missing` or `needs_review` |
| `observation_dispositions` | Unlinked observation IDs with `added`, `duplicate`, or `needs_review` |

A link uses `record_id`, `observation_id`, `status`, and `note`. Allowed link
states are `matched`, `location_mismatch`, `fill_mismatch`, and `needs_review`.

Each input item can appear exactly once in a link or unlinked disposition. The
verifier checks accounting, not bottle identity. The host and user own the
evidence used to propose a link.
