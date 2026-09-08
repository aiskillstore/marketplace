# Neutral outcome schema v1

This source-only schema measures independently reviewed finding outcomes. It is
separate from the rubric-only grading ablation and has no quality-score field.
`check_outcomes.py --example` prints a complete **unreviewed synthetic example**.
No independent reviewer or live result is supplied by the repository.

The frozen suite contains:

| Field | Required meaning |
| --- | --- |
| `schema_version` | Integer `1`. |
| `benchmark` | `neutral-findings`. |
| `split` | `pilot` or `holdout`; never relabel a used pilot as holdout. |
| `conditions` | `current` and `baseline`, each an exact SHA-256 candidate or fixed-context identity. |
| `protocol` | Frozen lowercase SHA-256 `prompt_hash`, nonempty exact `model`, positive integer `max_output_tokens`, explicit `tools` list (empty for no tools), nonempty `reading_policy`, positive integer `repeats`. |
| `labels` | `status` is `unreviewed` or `independently-reviewed`; the latter requires `reviewer` and `evidence` references. Document reviewer independence in that evidence. |
| `cases` | Nonempty unique IDs, exact synthetic `artifact`, its `case_hash`, and independently labeled `findings` (unique `id`, severity Low/Medium/High/Critical). |
| `frozen_hash` | SHA-256 of canonical JSON for the entire suite excluding this field. Includes labels, cases, conditions and protocol. |

Canonical JSON is UTF-8 encoding of `json.dumps(value, sort_keys=True,
separators=(',', ':'), ensure_ascii=True)`. `case_hash` hashes the artifact with
that same rule. Freeze only after review; changing anything requires a new suite.
Checks detect identity drift, not dishonest provenance assertions.

Each JSONL observation contains:

| Field | Required meaning |
| --- | --- |
| `suite_hash`, `case_hash`, `condition_hash` | Exact frozen identities. |
| `case_id`, `condition`, `repeat` | Pair key; condition current/baseline; repeat defaults to 1 and must fit protocol. Duplicate observations are rejected. |
| `model`, `prompt_hash` | Exact frozen protocol values. Record actual reported model/version in external transport evidence; do not claim protocol identity from an alias alone. |
| `status` | `Observed` or `Not Assessed`. Missing/failed sessions do not become zero scores. |
| `findings` | Adjudicated distinct finding IDs: matched labels use their IDs; each unmatched finding uses a distinct non-label ID (false positive). Labels must not be exposed to the evaluated model. |
| `matching_review` | Separate blind matching review with nonempty text `reviewer` and `evidence`, and lowercase 64-character SHA-256 `output_sha256` identifying the retained model output. Digest syntax is checked; the external output and review remain unauthenticated assertions. |
| `duration_seconds` | Finite, nonnegative elapsed time for an observed session. |
| `token_usage` | Actual `input_tokens` and `output_tokens`, or null when unavailable. |

Precision = matched predictions / all predictions; recall = matched labels / all
labels. Zero denominators are null (undefined), not perfect scores. Severe misses
count unmatched High/Critical labels. No reviewed observations means null counts,
not zero severe misses. Aggregate precision/recall pool counts; raw case/repeat
metrics and current-minus-baseline differences remain visible. Unknown token usage
makes the corresponding sum/difference null; dollar cost is not inferred.

A complete paired set with at least two distinct cases yields descriptive
comparison status only. `superiority` remains Not Assessed: this checker neither
establishes a statistical claim nor independently authenticates label review,
finding matching, host execution, or model transport. Preserve those evidence
artifacts separately and report failures, sample size, label limitations and
resource consumption alongside metrics.
