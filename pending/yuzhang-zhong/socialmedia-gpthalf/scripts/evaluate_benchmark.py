"""Validate and evaluate a locked, provenance-backed text benchmark.

The evaluator is intentionally independent from the bundled detector. Detector
outputs must be normalized to human/ai/mixed/abstain before evaluation. Any
detector thresholds are recorded as frozen metadata; they are not interpreted
as probabilities here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


GOLD_LABELS = ("human", "ai", "mixed")
PREDICTED_LABELS = ("human", "ai", "mixed", "abstain")
SENTENCE_GOLD_LABELS = ("human", "ai")
SENTENCE_PREDICTED_LABELS = ("human", "ai", "abstain")
SPLITS = ("calibration", "blind")

SLICE_FIELDS = {
    "language": "language",
    "platform": "platform",
    "genre": "genre",
    "length": "length_bucket",
    "model_family": "model_family",
    "editorial_state": "editorial_state",
}

DEFAULT_DECISION_THRESHOLDS = {
    "prediction_contract": list(PREDICTED_LABELS),
    "ai_assisted_positive_labels": ["ai", "mixed"],
    "score_semantics": "detector_specific_not_a_probability",
}

DEFAULT_RELEASE_GATES = {
    "max_ai_assisted_fpr": 0.10,
    "min_ai_assisted_precision": 0.80,
    "min_ai_assisted_recall": 0.50,
    "max_abstention_rate": 0.60,
    "min_mixed_sentence_f1": 0.60,
    "min_mixed_sentence_coverage": 1.0,
    "min_human_per_language": 100,
    "min_ai_assisted_per_language": 100,
}

REQUIRED_MANIFEST_FIELDS = (
    "id",
    "gold_label",
    "language",
    "platform",
    "genre",
    "length_bucket",
    "model_family",
    "editorial_state",
    "group_id",
    "split",
    "locked_blind",
)


class EvaluationError(ValueError):
    """Raised when benchmark inputs violate the evaluation protocol."""


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise EvaluationError(
                    f"{source}:{line_number}: invalid JSON: {error.msg}"
                ) from error
            if not isinstance(value, dict):
                raise EvaluationError(f"{source}:{line_number}: record must be an object")
            records.append(value)
    if not records:
        raise EvaluationError(f"{source}: JSONL file is empty")
    return records


def _require_nonempty_string(record: dict[str, Any], field: str, context: str) -> None:
    if not isinstance(record.get(field), str) or not record[field].strip():
        raise EvaluationError(f"{context}: {field} must be a non-empty string")


def _validate_sentence_labels(
    value: Any,
    *,
    allowed: tuple[str, ...],
    context: str,
    field: str,
) -> list[str]:
    if not isinstance(value, list) or not value:
        raise EvaluationError(f"{context}: {field} must be a non-empty list")
    if any(label not in allowed for label in value):
        raise EvaluationError(f"{context}: {field} values must be one of {allowed}")
    return value


def validate_manifest(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    validated = list(records)
    if not validated:
        raise EvaluationError("manifest is empty")

    seen_ids: set[str] = set()
    group_splits: dict[str, set[str]] = defaultdict(set)
    for index, record in enumerate(validated, start=1):
        context = f"manifest record {index}"
        if not isinstance(record, dict):
            raise EvaluationError(f"{context}: record must be an object")
        missing = [field for field in REQUIRED_MANIFEST_FIELDS if field not in record]
        if missing:
            raise EvaluationError(f"{context}: missing fields: {', '.join(missing)}")
        for field in (
            "id",
            "language",
            "platform",
            "genre",
            "length_bucket",
            "model_family",
            "editorial_state",
            "group_id",
        ):
            _require_nonempty_string(record, field, context)

        sample_id = record["id"]
        if sample_id in seen_ids:
            raise EvaluationError(f"{context}: duplicate id {sample_id!r}")
        seen_ids.add(sample_id)

        if record["gold_label"] not in GOLD_LABELS:
            raise EvaluationError(f"{context}: gold_label must be one of {GOLD_LABELS}")
        if record["split"] not in SPLITS:
            raise EvaluationError(f"{context}: split must be one of {SPLITS}")
        if not isinstance(record["locked_blind"], bool):
            raise EvaluationError(f"{context}: locked_blind must be boolean")
        if record["split"] == "blind" and record["locked_blind"] is not True:
            raise EvaluationError(f"{context}: blind records must set locked_blind=true")

        group_splits[record["group_id"]].add(record["split"])
        sentence_labels = record.get("sentence_labels")
        if record["gold_label"] == "mixed":
            labels = _validate_sentence_labels(
                sentence_labels,
                allowed=SENTENCE_GOLD_LABELS,
                context=context,
                field="sentence_labels",
            )
            if set(labels) != set(SENTENCE_GOLD_LABELS):
                raise EvaluationError(
                    f"{context}: mixed sentence_labels must contain both human and ai"
                )
        elif sentence_labels is not None:
            labels = _validate_sentence_labels(
                sentence_labels,
                allowed=SENTENCE_GOLD_LABELS,
                context=context,
                field="sentence_labels",
            )
            expected = record["gold_label"]
            if any(label != expected for label in labels):
                raise EvaluationError(
                    f"{context}: pure-document sentence_labels must all be {expected!r}"
                )

    leaking = sorted(group_id for group_id, splits in group_splits.items() if len(splits) > 1)
    if leaking:
        raise EvaluationError(
            "group_id leakage across calibration/blind splits: " + ", ".join(leaking)
        )
    return validated


def validate_predictions(
    records: Iterable[dict[str, Any]], manifest_ids: set[str]
) -> dict[str, dict[str, Any]]:
    predictions: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records, start=1):
        context = f"prediction record {index}"
        if not isinstance(record, dict):
            raise EvaluationError(f"{context}: record must be an object")
        _require_nonempty_string(record, "id", context)
        sample_id = record["id"]
        if sample_id not in manifest_ids:
            raise EvaluationError(f"{context}: unknown id {sample_id!r}")
        if sample_id in predictions:
            raise EvaluationError(f"{context}: duplicate id {sample_id!r}")
        if record.get("predicted_label") not in PREDICTED_LABELS:
            raise EvaluationError(
                f"{context}: predicted_label must be one of {PREDICTED_LABELS}"
            )
        sentence_predictions = record.get("sentence_predictions")
        if sentence_predictions is not None:
            _validate_sentence_labels(
                sentence_predictions,
                allowed=SENTENCE_PREDICTED_LABELS,
                context=context,
                field="sentence_predictions",
            )
        predictions[sample_id] = record
    return predictions


def _safe_divide(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _binary_metrics(tp: int, fp: int, fn: int, tn: int) -> dict[str, Any]:
    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    fpr = _safe_divide(fp, fp + tn)
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None and recall is not None and precision + recall
        else None
    )
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "fpr": fpr,
        "f1": f1,
    }


def _document_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    confusion = {
        gold: {predicted: 0 for predicted in PREDICTED_LABELS} for gold in GOLD_LABELS
    }
    for row in rows:
        confusion[row["gold_label"]][row["predicted_label"]] += 1

    per_class: dict[str, Any] = {}
    for label in GOLD_LABELS:
        tp = sum(
            1
            for row in rows
            if row["gold_label"] == label and row["predicted_label"] == label
        )
        fp = sum(
            1
            for row in rows
            if row["gold_label"] != label and row["predicted_label"] == label
        )
        fn = sum(
            1
            for row in rows
            if row["gold_label"] == label and row["predicted_label"] != label
        )
        tn = len(rows) - tp - fp - fn
        per_class[label] = _binary_metrics(tp, fp, fn, tn)

    positive_gold = {"ai", "mixed"}
    positive_prediction = {"ai", "mixed"}
    tp = sum(
        1
        for row in rows
        if row["gold_label"] in positive_gold
        and row["predicted_label"] in positive_prediction
    )
    fp = sum(
        1
        for row in rows
        if row["gold_label"] not in positive_gold
        and row["predicted_label"] in positive_prediction
    )
    fn = sum(
        1
        for row in rows
        if row["gold_label"] in positive_gold
        and row["predicted_label"] not in positive_prediction
    )
    tn = len(rows) - tp - fp - fn
    abstentions = sum(row["predicted_label"] == "abstain" for row in rows)
    return {
        "sample_count": len(rows),
        "confusion_matrix": confusion,
        "per_class": per_class,
        "ai_assisted": _binary_metrics(tp, fp, fn, tn),
        "abstention_count": abstentions,
        "abstention_rate": _safe_divide(abstentions, len(rows)),
    }


def _slice_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for output_name, field in SLICE_FIELDS.items():
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            buckets[row[field]].append(row)
        output[output_name] = {
            value: _document_metrics(bucket_rows)
            for value, bucket_rows in sorted(buckets.items())
        }
    return output


def _mixed_sentence_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    mixed_rows = [row for row in rows if row["gold_label"] == "mixed"]
    evaluated_documents = 0
    tp = fp = fn = tn = abstentions = sentence_count = 0
    for row in mixed_rows:
        predicted = row.get("sentence_predictions")
        if predicted is None:
            continue
        gold = row["sentence_labels"]
        if len(predicted) != len(gold):
            raise EvaluationError(
                f"prediction {row['id']!r}: sentence_predictions length does not match sentence_labels"
            )
        evaluated_documents += 1
        for gold_label, predicted_label in zip(gold, predicted):
            sentence_count += 1
            if predicted_label == "abstain":
                abstentions += 1
            if gold_label == "ai" and predicted_label == "ai":
                tp += 1
            elif gold_label == "human" and predicted_label == "ai":
                fp += 1
            elif gold_label == "ai" and predicted_label != "ai":
                fn += 1
            else:
                tn += 1
    metrics = _binary_metrics(tp, fp, fn, tn)
    return {
        "mixed_document_count": len(mixed_rows),
        "evaluated_document_count": evaluated_documents,
        "document_coverage": _safe_divide(evaluated_documents, len(mixed_rows)),
        "sentence_count": sentence_count,
        "sentence_abstention_rate": _safe_divide(abstentions, sentence_count),
        **metrics,
    }


def _check(value: float | int | None, operator: str, threshold: float | int) -> dict[str, Any]:
    passed = False
    if value is not None:
        passed = value <= threshold if operator == "<=" else value >= threshold
    return {"value": value, "operator": operator, "threshold": threshold, "passed": passed}


def _release_assessment(
    rows: list[dict[str, Any]],
    document: dict[str, Any],
    slices: dict[str, Any],
    mixed_sentence: dict[str, Any],
    gates: dict[str, Any],
    selected_split: str,
) -> dict[str, Any]:
    locked_blind = bool(rows) and selected_split == "blind" and all(
        row["split"] == "blind" and row["locked_blind"] is True for row in rows
    )
    ai_metrics = document["ai_assisted"]
    checks: dict[str, Any] = {
        "locked_blind_only": {
            "value": locked_blind,
            "operator": "is",
            "threshold": True,
            "passed": locked_blind,
        },
        "ai_assisted_fpr": _check(
            ai_metrics["fpr"], "<=", gates["max_ai_assisted_fpr"]
        ),
        "ai_assisted_precision": _check(
            ai_metrics["precision"], ">=", gates["min_ai_assisted_precision"]
        ),
        "ai_assisted_recall": _check(
            ai_metrics["recall"], ">=", gates["min_ai_assisted_recall"]
        ),
        "abstention_rate": _check(
            document["abstention_rate"], "<=", gates["max_abstention_rate"]
        ),
        "mixed_sentence_f1": _check(
            mixed_sentence["f1"], ">=", gates["min_mixed_sentence_f1"]
        ),
        "mixed_sentence_coverage": _check(
            mixed_sentence["document_coverage"],
            ">=",
            gates["min_mixed_sentence_coverage"],
        ),
    }

    language_checks: dict[str, Any] = {}
    for language, language_metrics in slices["language"].items():
        language_rows = [row for row in rows if row["language"] == language]
        human_count = sum(row["gold_label"] == "human" for row in language_rows)
        assisted_count = sum(row["gold_label"] in {"ai", "mixed"} for row in language_rows)
        language_checks[language] = {
            "human_sample_count": _check(
                human_count, ">=", gates["min_human_per_language"]
            ),
            "ai_assisted_sample_count": _check(
                assisted_count, ">=", gates["min_ai_assisted_per_language"]
            ),
            "fpr": _check(
                language_metrics["ai_assisted"]["fpr"],
                "<=",
                gates["max_ai_assisted_fpr"],
            ),
            "recall": _check(
                language_metrics["ai_assisted"]["recall"],
                ">=",
                gates["min_ai_assisted_recall"],
            ),
        }

    all_checks = list(checks.values()) + [
        check for language in language_checks.values() for check in language.values()
    ]
    passed = all(check["passed"] for check in all_checks)
    return {
        "status": "pass" if passed else "fail",
        "release_eligible": locked_blind,
        "checks": checks,
        "language_checks": language_checks,
    }


def _manifest_digest(records: list[dict[str, Any]]) -> str:
    canonical = "\n".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in sorted(records, key=lambda item: item["id"])
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def evaluate(
    manifest_records: Iterable[dict[str, Any]],
    prediction_records: Iterable[dict[str, Any]],
    *,
    split: str = "blind",
    decision_thresholds: dict[str, Any] | None = None,
    release_gates: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if split not in {"all", *SPLITS}:
        raise EvaluationError("split must be all, calibration, or blind")
    manifest = validate_manifest(manifest_records)
    predictions = validate_predictions(
        prediction_records, {record["id"] for record in manifest}
    )
    selected = manifest if split == "all" else [row for row in manifest if row["split"] == split]
    if not selected:
        raise EvaluationError(f"manifest has no records for split {split!r}")
    missing = sorted(row["id"] for row in selected if row["id"] not in predictions)
    if missing:
        raise EvaluationError("missing predictions for ids: " + ", ".join(missing))

    rows = [{**record, **predictions[record["id"]]} for record in selected]
    document = _document_metrics(rows)
    slices = _slice_metrics(rows)
    mixed_sentence = _mixed_sentence_metrics(rows)
    thresholds = {**DEFAULT_DECISION_THRESHOLDS, **(decision_thresholds or {})}
    gates = {**DEFAULT_RELEASE_GATES, **(release_gates or {})}
    release = _release_assessment(rows, document, slices, mixed_sentence, gates, split)
    return {
        "schema_version": "1.0",
        "selected_split": split,
        "blind_test": {
            "locked": split == "blind" and all(row["locked_blind"] for row in rows),
            "manifest_sha256": _manifest_digest(selected),
            "record_count": len(rows),
            "group_count": len({row["group_id"] for row in rows}),
        },
        "decision_thresholds": thresholds,
        "release_gates": gates,
        "document_metrics": document,
        "mixed_sentence_metrics": mixed_sentence,
        "slices": slices,
        "release_assessment": release,
        "limitations": [
            "Metrics describe only the supplied benchmark and do not establish provenance for new text.",
            "Detector scores and rule points are not probabilities unless separately calibrated.",
            "Release decisions require a locked blind split with leakage-controlled groups.",
        ],
    }


def _read_json_object(path: str | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvaluationError(f"{path}: expected a JSON object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a JSONL manifest")
    validate_parser.add_argument("--manifest", required=True)

    evaluate_parser = subparsers.add_parser("evaluate", help="evaluate normalized predictions")
    evaluate_parser.add_argument("--manifest", required=True)
    evaluate_parser.add_argument("--predictions", required=True)
    evaluate_parser.add_argument("--split", choices=("all", *SPLITS), default="blind")
    evaluate_parser.add_argument("--thresholds", help="JSON object recorded as frozen thresholds")
    evaluate_parser.add_argument("--release-gates", help="JSON object overriding release gates")
    evaluate_parser.add_argument("--output", help="write JSON report instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = validate_manifest(read_jsonl(args.manifest))
        if args.command == "validate":
            payload = {
                "valid": True,
                "record_count": len(manifest),
                "group_count": len({record["group_id"] for record in manifest}),
                "split_counts": {
                    split: sum(record["split"] == split for record in manifest)
                    for split in SPLITS
                },
            }
        else:
            payload = evaluate(
                manifest,
                read_jsonl(args.predictions),
                split=args.split,
                decision_thresholds=_read_json_object(args.thresholds),
                release_gates=_read_json_object(args.release_gates),
            )
    except (EvaluationError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, ensure_ascii=False))
        return 2

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if getattr(args, "output", None):
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
