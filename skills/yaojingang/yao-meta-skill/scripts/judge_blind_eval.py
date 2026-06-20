#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from trigger_eval import (
    collect_concept_hits,
    desired_positive_concepts,
    extract_description,
    iter_case_items,
    load_json,
    load_semantic_config,
    normalize,
    phrase_present,
    words,
)


DEFAULT_CONFIG_PATH = Path("evals/semantic_config.json")


def phrase_hits(text: str, phrases: list[str]) -> list[str]:
    normalized = normalize(text)
    return [phrase for phrase in phrases if phrase_present(normalized, phrase)]


def judge_prompt(description: str, prompt: str, config: dict) -> tuple[bool, dict]:
    hints = config.get("optimizer_hints", {})
    generic_exclusion_phrases = [
        "explain",
        "summarize",
        "translate",
        "brainstorm",
        "teach me",
        "plain english",
    ]
    desired = desired_positive_concepts(description, config)
    positive_hits = collect_concept_hits(prompt, config["positive_concepts"])
    negative_hits = collect_concept_hits(prompt, config["negative_concepts"])

    focused_positive = [name for name in desired if name in positive_hits]
    strong_positive = [
        name
        for name in focused_positive
        if config["positive_concepts"][name]["weight"] >= 0.16
    ]
    trigger_action_hits = phrase_hits(prompt, hints.get("trigger_actions", []))
    input_hits = phrase_hits(prompt, hints.get("inputs", []))
    artifact_hits = phrase_hits(prompt, hints.get("artifacts", []))
    exclusion_hits = phrase_hits(prompt, hints.get("exclusions", []))
    generic_exclusion_hits = phrase_hits(prompt, generic_exclusion_phrases)

    capability_words = words(hints.get("capability", ""))
    prompt_words = words(prompt)
    capability_overlap = len(capability_words & prompt_words)

    exclusive_negative = sorted(
        name for name, hit in negative_hits.items() if hit.get("exclusive")
    )
    nonexclusive_negative = sorted(
        name for name, hit in negative_hits.items() if not hit.get("exclusive")
    )

    positive_vote = 0
    if trigger_action_hits:
        positive_vote += 2
    if len(strong_positive) >= 2:
        positive_vote += 2
    elif len(strong_positive) == 1:
        positive_vote += 1
    if len(focused_positive) >= 3:
        positive_vote += 1
    if input_hits or artifact_hits:
        positive_vote += 1
    if capability_overlap >= 1:
        positive_vote += 1

    negative_vote = (2 * len(exclusive_negative)) + len(nonexclusive_negative)
    if exclusion_hits:
        negative_vote += 1
    if generic_exclusion_hits:
        negative_vote += 1

    trigger = positive_vote >= 3 and positive_vote > negative_vote
    if exclusive_negative and positive_vote < 5:
        trigger = False
    if exclusion_hits and positive_vote < 4:
        trigger = False
    if generic_exclusion_hits and positive_vote < 4:
        trigger = False

    margin = positive_vote - negative_vote
    confidence = 0.5 + (0.08 * max(0, margin))
    if exclusive_negative:
        confidence += 0.08
    if trigger_action_hits and len(strong_positive) >= 1:
        confidence += 0.06
    confidence = max(0.0, min(1.0, confidence))

    detail = {
        "mode": "judge-rubric",
        "focused_positive_concepts": focused_positive,
        "strong_positive_concepts": strong_positive,
        "trigger_action_hits": trigger_action_hits,
        "input_hits": input_hits,
        "artifact_hits": artifact_hits,
        "capability_overlap": capability_overlap,
        "exclusive_negative_concepts": exclusive_negative,
        "nonexclusive_negative_concepts": nonexclusive_negative,
        "exclusion_hits": exclusion_hits,
        "generic_exclusion_hits": generic_exclusion_hits,
        "positive_vote": positive_vote,
        "negative_vote": negative_vote,
        "margin": margin,
        "confidence": round(confidence, 3),
        "concept_evidence": {
            "positive": {
                name: positive_hits[name]["matched_phrases"]
                for name in sorted(positive_hits)
            },
            "negative": {
                name: negative_hits[name]["matched_phrases"]
                for name in sorted(negative_hits)
            },
        },
    }
    return trigger, detail


def classify_bucket(bucket: str) -> bool:
    return bucket == "should_trigger"


def evaluate_judge(description: str, cases: dict, config: dict) -> dict:
    results = {"should_trigger": [], "should_not_trigger": [], "near_neighbor": []}
    fp = 0
    fn = 0
    bucket_stats = {}
    family_stats: dict[str, dict] = {}
    misfires = []
    confidence_total = 0.0
    confidence_count = 0

    for bucket in ("should_trigger", "should_not_trigger", "near_neighbor"):
        expected = classify_bucket(bucket)
        items = iter_case_items(cases, bucket)
        total = 0
        passed_count = 0
        for item in items:
            prompt = item["text"]
            family = item.get("family", "default")
            predicted, detail = judge_prompt(description, prompt, config)
            passed = predicted == expected
            total += 1
            confidence_total += detail["confidence"]
            confidence_count += 1
            if passed:
                passed_count += 1
            if not passed and expected:
                fn += 1
            if not passed and not expected:
                fp += 1

            record = {
                "prompt": prompt,
                "family": family,
                "predicted_trigger": predicted,
                "expected_trigger": expected,
                "passed": passed,
                "judge_detail": detail,
            }
            if abs(detail["margin"]) <= 1:
                record["boundary_case"] = True
            results[bucket].append(record)

            family_bucket = family_stats.setdefault(
                family,
                {"total": 0, "passed": 0, "false_positives": 0, "false_negatives": 0},
            )
            family_bucket["total"] += 1
            if passed:
                family_bucket["passed"] += 1
            elif expected:
                family_bucket["false_negatives"] += 1
            else:
                family_bucket["false_positives"] += 1

            if not passed:
                misfires.append(
                    {
                        "bucket": bucket,
                        "family": family,
                        "prompt": prompt,
                        "reason": "false_negative" if expected else "false_positive",
                        "focused_positive_concepts": detail["focused_positive_concepts"],
                        "exclusive_negative_concepts": detail["exclusive_negative_concepts"],
                        "trigger_action_hits": detail["trigger_action_hits"],
                        "margin": detail["margin"],
                    }
                )

        bucket_stats[bucket] = {
            "total": total,
            "passed": passed_count,
            "pass_rate": round(passed_count / total, 3) if total else None,
        }

    for family, stats in family_stats.items():
        stats["pass_rate"] = round(stats["passed"] / stats["total"], 3) if stats["total"] else None

    tp = sum(1 for item in results["should_trigger"] if item["predicted_trigger"])
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None

    return {
        "judge": "rubric-blind-v1",
        "judge_explanation": (
            "The blind judge uses a rubric rather than the main threshold scorer. "
            "It looks for trigger-action evidence, focused capability evidence, and "
            "input or artifact evidence, then blocks on explicit exclusion and "
            "exclusive negative signals. This acts as an independent second opinion "
            "for blind-holdout prompts."
        ),
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 3) if precision is not None else None,
        "recall": round(recall, 3) if recall is not None else None,
        "bucket_stats": bucket_stats,
        "family_stats": family_stats,
        "misfires": misfires,
        "results": results,
        "judge_summary": {
            "agreement_rate": round(
                sum(bucket["passed"] for bucket in bucket_stats.values())
                / sum(bucket["total"] for bucket in bucket_stats.values()),
                3,
            )
            if bucket_stats
            else None,
            "mean_confidence": round(confidence_total / confidence_count, 3)
            if confidence_count
            else None,
            "rubric_version": "blind-v1",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a rubric-based blind trigger judge.")
    parser.add_argument("--description", help="Description string to evaluate")
    parser.add_argument("--description-file", help="Read description text from file")
    parser.add_argument("--cases", required=True, help="JSON file with blind trigger cases")
    parser.add_argument("--semantic-config", default=str(DEFAULT_CONFIG_PATH), help="Semantic config JSON")
    args = parser.parse_args()

    description = args.description
    if args.description_file:
        description = extract_description(Path(args.description_file).read_text(encoding="utf-8"))
    if not description:
        raise SystemExit("Provide --description or --description-file")

    cases = load_json(Path(args.cases))
    config = load_semantic_config(Path(args.semantic_config))
    report = evaluate_judge(description, cases, config)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["false_positives"] > 0 or report["false_negatives"] > 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
