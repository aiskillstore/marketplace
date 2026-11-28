# Locked Benchmark Evaluation Protocol

## Purpose and boundary

This protocol measures the behavior of a detector on a provenance-backed,
leakage-controlled corpus. It does not prove authorship for an individual text.
Rule points and detector scores are not probabilities unless a separate
calibration study establishes that interpretation.

Run the evaluator independently from detector development. Normalize each
document prediction to exactly one of `human`, `ai`, `mixed`, or `abstain`.
Use `abstain` for unresolved, unsupported, or insufficient-length results.

## JSONL manifest

Each non-empty line is one JSON object with these required fields:

- `id`: globally unique sample identifier.
- `gold_label`: `human`, `ai`, or `mixed`.
- `language`, `platform`, `genre`, `length_bucket`, `model_family`, and
  `editorial_state`: non-empty slice values.
- `group_id`: leakage-control group. Put the same author/account, prompt
  template, topic event, near-duplicate family, or derived document in one
  group.
- `split`: `calibration` or `blind`.
- `locked_blind`: boolean; every blind record must be `true`.
- `sentence_labels`: required for `mixed`, as a sentence-aligned list of
  `human` and `ai` containing both labels.

Human samples should have verifiable provenance, such as pre-generative-AI
publication dates or retained drafting history. AI samples should retain model,
version, prompt, and generation logs. Mixed samples should retain exact sentence
boundaries and editing history. Use `model_family: "none"` where it is not
applicable rather than omitting the slice.

No `group_id` may appear in both calibration and blind splits. Keep blind labels
inaccessible to detector developers until code, thresholds, and release gates
are frozen. Preregister the canonical manifest SHA-256 emitted in `blind_test`
and compare it with the final report so that later sample substitutions are
detectable.

## Prediction JSONL

Each prediction record requires:

```json
{"id":"sample-1","predicted_label":"abstain"}
```

For mixed sentence evaluation, add a sentence-aligned prediction list:

```json
{"id":"sample-2","predicted_label":"mixed","sentence_predictions":["human","ai","abstain"]}
```

Sentence predictions use `human`, `ai`, or `abstain`. Their length must match
the manifest's `sentence_labels`. Missing sentence predictions reduce mixed
sentence coverage and fail the default release gate.

## Commands

An auditable standard-library character n-gram Naive Bayes baseline is included to exercise the full train/evaluate/admit path. It is a baseline, not a claim of GPTZero equivalence. Training accepts calibration records only and fingerprints the artifact:

```text
python scripts/local_model.py train --input calibration-with-text.jsonl --output model.json
python scripts/local_model.py predict --model model.json --input benchmark-with-text.jsonl --output predictions.jsonl
```

Each training row requires `id`, `gold_label`, `text`, `language`, `group_id`, and `split: calibration`, with all three document labels represented. The trainer refuses blind rows. For mixed sentence evaluation, prediction input also supplies an explicit `sentences` list aligned one-to-one with `sentence_labels`; automatic sentence splitting is not trusted. Put the resulting `model_id` into the evaluator's frozen thresholds JSON so runtime admission can bind the evaluation to the exact artifact.

Validate leakage and schema before detector execution:

```text
python scripts/evaluate_benchmark.py validate --manifest benchmark.jsonl
```

Evaluate a locked blind split:

```text
python scripts/evaluate_benchmark.py evaluate --manifest benchmark.jsonl --predictions predictions.jsonl --split blind --thresholds frozen-thresholds.json --release-gates release-gates.json --output evaluation.json
```

`--thresholds` accepts an arbitrary JSON object and records it verbatim beside
the results. This preserves the exact detector policy without treating the
values as probabilities. `--release-gates` overrides named defaults; omitted
keys retain their defaults.

## Metrics

The report includes:

- A three-class document confusion matrix with an additional abstention column.
- Per-class precision, recall, false-positive rate, and F1.
- A safety-oriented `ai_assisted` view that treats `ai` and `mixed` as positive.
- Overall abstention count and rate.
- The same document metrics for language, platform, genre, length,
  model-family, and editorial-state slices.
- Mixed-document sentence precision, recall, false-positive rate, F1,
  abstention, and document coverage.
- Locked-blind status, frozen thresholds, release gates, and gate-by-gate output.

Abstentions remain in recall denominators. They are not silently converted to
human predictions. Precision depends on benchmark prevalence, so always report
it with FPR, recall, class counts, and slice results.

## Default release gates

The defaults are intentionally conservative starting points, not claims of
calibrated accuracy:

- AI-assisted FPR at most `0.10`.
- AI-assisted precision at least `0.80`.
- AI-assisted recall at least `0.50`.
- Document abstention rate at most `0.60`.
- Mixed sentence F1 at least `0.60` with `1.00` document coverage.
- At least 100 human and 100 AI-assisted blind samples per language.
- The FPR and recall gates must also pass separately for every language.

Only an evaluation selecting the locked `blind` split is release-eligible.
Calibration results always fail the locked-blind gate even when their metrics
look favorable. If blind evaluation fails, revise the detector under a new
version and use a new untouched blind set; do not tune repeatedly against the
failed blind labels.
