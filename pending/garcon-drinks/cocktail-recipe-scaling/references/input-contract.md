# Input contract

The calculator accepts one JSON object.

| Field | Requirement |
|---|---|
| `original_yield` | Positive `value` and non-empty `unit` |
| `target_yield` | Positive `value` using the original yield unit |
| `tolerance_percent` | Number from 0 through 10 |
| `ingredients` | Non-empty list with unique names |
| `container_capacity` | Optional positive value using the yield unit |

Each ingredient uses these fields.

| Field | Requirement |
|---|---|
| `name` | Unique non-empty name |
| `amount` | Non-negative number |
| `unit` | Non-empty unit |
| `mode` | `linear`, `count_up`, or `manual` |
| `rounding_increment` | Positive number for `linear` and `count_up` |
| `rounding_mode` | `nearest`, `up`, or `down` for `linear`; `up` for `count_up` |
| `note` | Required explanation for `manual` |

The calculator does not convert units. Ingredient units stay unchanged because
each amount is multiplied independently.

Example input is available at
[`tests/fixtures/success.json`](../tests/fixtures/success.json).
