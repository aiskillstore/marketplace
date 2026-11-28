"""Train and run a small, auditable character n-gram text baseline.

This baseline is intentionally ordinary rather than branded as a GPTZero clone.
It becomes an origin-layer model signal only when a matching frozen blind
evaluation report passes every release gate.  Otherwise callers must abstain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


CLASSES = ("human", "ai", "mixed")


class LocalModelError(ValueError):
    pass


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _ngrams(text: str, minimum: int, maximum: int) -> Counter[str]:
    normalized = _normalize(text)
    values: Counter[str] = Counter()
    for size in range(minimum, maximum + 1):
        values.update(normalized[index : index + size] for index in range(len(normalized) - size + 1))
    return values


def _canonical_hash(value) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def train(records: Iterable[dict], *, ngram_min: int = 3, ngram_max: int = 5, max_features: int = 50000, alpha: float = 1.0) -> dict:
    rows = list(records)
    if not rows:
        raise LocalModelError("training records are empty")
    if not (1 <= ngram_min <= ngram_max <= 8):
        raise LocalModelError("ngram bounds must satisfy 1 <= min <= max <= 8")
    if max_features < 100:
        raise LocalModelError("max_features must be at least 100")
    if alpha <= 0:
        raise LocalModelError("alpha must be positive")

    class_counts = Counter()
    token_counts = {label: Counter() for label in CLASSES}
    global_counts = Counter()
    languages: set[str] = set()
    seen_ids: set[str] = set()
    provenance_rows: list[dict] = []
    for index, row in enumerate(rows):
        if row.get("split") != "calibration":
            raise LocalModelError("training accepts calibration records only; blind labels must stay sealed")
        sample_id = str(row.get("id") or "")
        label = row.get("gold_label")
        text = row.get("text")
        group_id = str(row.get("group_id") or "")
        language = str(row.get("language") or "")
        if not sample_id or sample_id in seen_ids or label not in CLASSES or not isinstance(text, str) or not text.strip() or not group_id or not language:
            raise LocalModelError(f"invalid training record at index {index}")
        seen_ids.add(sample_id)
        languages.add(language)
        features = _ngrams(text, ngram_min, ngram_max)
        token_counts[label].update(features)
        global_counts.update(features)
        class_counts[label] += 1
        provenance_rows.append({"id": sample_id, "label": label, "group_id": group_id, "language": language, "text_sha256": hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()})

    if any(class_counts[label] == 0 for label in CLASSES):
        raise LocalModelError("training requires human, ai, and mixed examples")
    vocabulary = {token for token, _ in global_counts.most_common(max_features)}
    filtered = {label: {token: count for token, count in token_counts[label].items() if token in vocabulary} for label in CLASSES}
    core = {
        "schema_version": "1.0",
        "method": "char_ngram_multinomial_nb_v1",
        "ngram_min": ngram_min,
        "ngram_max": ngram_max,
        "alpha": alpha,
        "class_document_counts": dict(class_counts),
        "class_token_counts": filtered,
        "languages": sorted(languages),
        "training_corpus_sha256": _canonical_hash(sorted(provenance_rows, key=lambda item: item["id"])),
    }
    core["model_id"] = _canonical_hash(core)
    return core


def _validate_model(model: dict) -> None:
    if model.get("schema_version") != "1.0" or model.get("method") != "char_ngram_multinomial_nb_v1":
        raise LocalModelError("unsupported local model artifact")
    claimed = model.get("model_id")
    core = {key: value for key, value in model.items() if key != "model_id"}
    if not isinstance(claimed, str) or claimed != _canonical_hash(core):
        raise LocalModelError("local model artifact fingerprint mismatch")


def predict(model: dict, text: str, *, abstain_margin: float = 0.15) -> dict:
    _validate_model(model)
    if not isinstance(text, str) or not text.strip():
        return {"predicted_label": "abstain", "reason": "empty_text", "model_id": model["model_id"]}
    features = _ngrams(text, int(model["ngram_min"]), int(model["ngram_max"]))
    counts = model["class_token_counts"]
    vocabulary = {token for label in CLASSES for token in counts[label]}
    total_documents = sum(int(model["class_document_counts"][label]) for label in CLASSES)
    alpha = float(model["alpha"])
    scores: dict[str, float] = {}
    for label in CLASSES:
        class_docs = int(model["class_document_counts"][label])
        total_tokens = sum(int(value) for value in counts[label].values())
        denominator = total_tokens + alpha * max(len(vocabulary), 1)
        score = math.log(class_docs / total_documents)
        for token, frequency in features.items():
            if token in vocabulary:
                score += frequency * math.log((int(counts[label].get(token, 0)) + alpha) / denominator)
        scores[label] = score
    peak = max(scores.values())
    exponentials = {label: math.exp(value - peak) for label, value in scores.items()}
    total = sum(exponentials.values())
    normalized = {label: value / total for label, value in exponentials.items()}
    ranked = sorted(normalized, key=normalized.get, reverse=True)
    margin = normalized[ranked[0]] - normalized[ranked[1]]
    label = ranked[0] if margin >= abstain_margin else "abstain"
    return {
        "predicted_label": label,
        "class_scores": {key: round(value, 6) for key, value in normalized.items()},
        "decision_margin": round(margin, 6),
        "not_calibrated_probability": True,
        "model_id": model["model_id"],
    }


def admit(model: dict, evaluation: dict, language: str) -> None:
    """Validate evaluation metadata for descriptive research use only.

    This is not a cryptographic attestation. Runtime callers must not elevate a
    user-supplied model/evaluation pair into provenance or a strong origin
    signal without a separately trusted signature chain.
    """

    _validate_model(model)
    if language not in model.get("languages", []):
        raise LocalModelError("model artifact does not declare support for this language")
    release = evaluation.get("release_assessment") or {}
    blind = evaluation.get("blind_test") or {}
    thresholds = evaluation.get("decision_thresholds") or {}
    language_checks = release.get("language_checks") or {}
    if evaluation.get("schema_version") != "1.0":
        raise LocalModelError("unsupported evaluation report schema")
    if evaluation.get("selected_split") != "blind" or not blind.get("locked"):
        raise LocalModelError("model evaluation is not a locked blind test")
    digest = blind.get("manifest_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise LocalModelError("evaluation omitted a valid blind manifest fingerprint")
    if not isinstance(blind.get("record_count"), int) or blind["record_count"] < 1:
        raise LocalModelError("evaluation blind record count is invalid")
    if not release.get("release_eligible") or release.get("status") != "pass":
        raise LocalModelError("model evaluation did not pass release gates")
    if thresholds.get("model_id") != model.get("model_id"):
        raise LocalModelError("evaluation model_id does not match the artifact")
    required_overall = {
        "locked_blind_only", "ai_assisted_fpr", "ai_assisted_precision",
        "ai_assisted_recall", "abstention_rate", "mixed_sentence_f1",
        "mixed_sentence_coverage",
    }
    overall = release.get("checks")
    if not isinstance(overall, dict) or set(overall) != required_overall or not all(
        isinstance(item, dict) and item.get("passed") is True for item in overall.values()
    ):
        raise LocalModelError("evaluation overall gate details are incomplete")
    checks = language_checks.get(language)
    required_language = {"human_sample_count", "ai_assisted_sample_count", "fpr", "recall"}
    if not isinstance(checks, dict) or set(checks) != required_language or not all(
        isinstance(item, dict) and item.get("passed") is True for item in checks.values()
    ):
        raise LocalModelError("model has no passing blind language slice for this input")


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise LocalModelError(f"line {number} must be an object")
            rows.append(value)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train or run the gated local character n-gram baseline")
    commands = parser.add_subparsers(dest="command", required=True)
    train_parser = commands.add_parser("train")
    train_parser.add_argument("--input", required=True, type=Path)
    train_parser.add_argument("--output", required=True, type=Path)
    predict_parser = commands.add_parser("predict")
    predict_parser.add_argument("--model", required=True, type=Path)
    predict_parser.add_argument("--input", required=True, type=Path)
    predict_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.command == "train":
        model = train(_read_jsonl(args.input))
        args.output.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        model = json.loads(args.model.read_text(encoding="utf-8"))
        output = []
        for row in _read_jsonl(args.input):
            result = predict(model, str(row.get("text") or ""))
            prediction = {"id": row.get("id"), "predicted_label": result["predicted_label"]}
            if row.get("sentence_labels") is not None:
                sentences = row.get("sentences")
                if not isinstance(sentences, list) or len(sentences) != len(row["sentence_labels"]):
                    raise LocalModelError("mixed evaluation rows require sentence-aligned sentences")
                sentence_predictions = []
                for sentence in sentences:
                    sentence_label = predict(model, str(sentence or ""))["predicted_label"]
                    sentence_predictions.append(
                        sentence_label if sentence_label in {"human", "ai"} else "abstain"
                    )
                prediction["sentence_predictions"] = sentence_predictions
            output.append(prediction)
        args.output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in output), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
