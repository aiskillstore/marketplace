#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from context_sizer import estimate_tokens
from description_optimizer_reporting import render_markdown
from judge_blind_eval import evaluate_judge
from trigger_eval import (
    compare_reports,
    evaluate,
    extract_description,
    load_json,
    load_semantic_config,
)


def read_description(path: Path) -> str:
    return extract_description(path.read_text(encoding="utf-8")).strip()


def serial_join(items: list[str], conjunction: str = "or") -> str:
    items = [item.strip() for item in items if item and item.strip()]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"


def sentence(text: str) -> str:
    text = " ".join(text.split())
    if not text:
        return text
    if text.endswith("."):
        return text
    return f"{text}."


def build_candidates(current: str, config: dict) -> list[dict]:
    hints = config.get("optimizer_hints", {})
    capability = hints.get("capability") or current.split(".", 1)[0].strip()
    inputs = hints.get("inputs", [])
    trigger_actions = hints.get("trigger_actions", [])
    exclusions = hints.get("exclusions", [])
    artifacts = hints.get("artifacts", [])

    capability_sentence = sentence(capability)
    inputs_clause = f" from {serial_join(inputs)}" if inputs else ""
    trigger_clause = serial_join(trigger_actions[:3], "or")
    exclusion_clause = serial_join(exclusions[:3], "or")
    artifact_clause = serial_join(artifacts[:4], "or")

    raw_candidates = [
        {
            "id": "current",
            "label": "Current",
            "description": sentence(current),
            "strategy": "current",
        },
    ]

    if capability and trigger_clause:
        raw_candidates.extend(
            [
                {
                    "id": "balanced",
                    "label": "Balanced",
                    "description": sentence(f"{capability}{inputs_clause}. Use when asked to {trigger_clause}"),
                    "strategy": "balanced_template",
                },
                {
                    "id": "boundary",
                    "label": "Boundary",
                    "description": sentence(
                        f"{capability}{inputs_clause}. Use when asked to {trigger_clause}. Do not use for {exclusion_clause}"
                    )
                    if exclusion_clause
                    else sentence(f"{capability}{inputs_clause}. Use when asked to {trigger_clause}"),
                    "strategy": "boundary_template",
                },
                {
                    "id": "minimal",
                    "label": "Minimal",
                    "description": sentence(f"{capability}. Use when asked to {trigger_clause}"),
                    "strategy": "minimal_template",
                },
            ]
        )

    if capability and artifact_clause and trigger_clause:
        raw_candidates.append(
            {
                "id": "artifact_aware",
                "label": "Artifact Aware",
                "description": sentence(
                    f"{capability}{inputs_clause}. Trigger when requests mention {artifact_clause} and the job is to {trigger_clause}"
                ),
                "strategy": "artifact_template",
            }
        )

    if capability and exclusion_clause:
        raw_candidates.append(
            {
                "id": "guardrail",
                "label": "Guardrail",
                "description": sentence(f"{capability}{inputs_clause}. Do not use for {exclusion_clause}"),
                "strategy": "guardrail_template",
            }
        )

    deduped = []
    seen = set()
    for candidate in raw_candidates:
        normalized = candidate["description"].lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(candidate)
    return deduped


def objective_key(report: dict, token_count: int) -> tuple:
    bucket_stats = report.get("bucket_stats", {})
    near_rate = bucket_stats.get("near_neighbor", {}).get("pass_rate") or 0
    negative_rate = bucket_stats.get("should_not_trigger", {}).get("pass_rate") or 0
    precision = report.get("precision") or 0
    recall = report.get("recall") or 0
    return (
        report["false_positives"],
        report["false_negatives"],
        -near_rate,
        -negative_rate,
        -precision,
        -recall,
        token_count,
    )


def summarize_candidate(candidate: dict, dev_report: dict, holdout_report: dict | None) -> dict:
    token_count = estimate_tokens(candidate["description"])
    summary = {
        **candidate,
        "estimated_tokens": token_count,
        "dev": {
            "false_positives": dev_report["false_positives"],
            "false_negatives": dev_report["false_negatives"],
            "precision": dev_report["precision"],
            "recall": dev_report["recall"],
            "near_neighbor_pass_rate": dev_report["bucket_stats"]["near_neighbor"]["pass_rate"],
            "should_not_trigger_pass_rate": dev_report["bucket_stats"]["should_not_trigger"]["pass_rate"],
        },
        "selection_key": objective_key(dev_report, token_count),
    }
    if holdout_report:
        summary["holdout"] = {
            "false_positives": holdout_report["false_positives"],
            "false_negatives": holdout_report["false_negatives"],
            "precision": holdout_report["precision"],
            "recall": holdout_report["recall"],
            "near_neighbor_pass_rate": holdout_report["bucket_stats"]["near_neighbor"]["pass_rate"],
            "should_not_trigger_pass_rate": holdout_report["bucket_stats"]["should_not_trigger"]["pass_rate"],
        }
    return summary


def summarize_gate_report(report: dict | None) -> dict | None:
    if not report:
        return None
    summary = {
        "false_positives": report["false_positives"],
        "false_negatives": report["false_negatives"],
        "precision": report["precision"],
        "recall": report["recall"],
        "near_neighbor_pass_rate": report["bucket_stats"]["near_neighbor"]["pass_rate"],
        "should_not_trigger_pass_rate": report["bucket_stats"]["should_not_trigger"]["pass_rate"],
    }
    if report.get("judge_summary"):
        summary["judge_summary"] = report["judge_summary"]
    return summary


def error_tuple(report: dict | None) -> tuple[int, int] | None:
    if not report:
        return None
    return (report["false_positives"], report["false_negatives"])


def safe_round(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 3)


def summarize_family_health(report: dict | None) -> dict | None:
    if not report:
        return None

    family_stats = report.get("family_stats", {})
    ordered = sorted(
        family_stats.items(),
        key=lambda item: (
            item[1].get("false_positives", 0) + item[1].get("false_negatives", 0),
            item[1].get("pass_rate") or 0,
            -(item[1].get("total") or 0),
            item[0],
        ),
    )
    weakest = ordered[-1] if ordered else None
    failing = []
    for family, stats in family_stats.items():
        errors = stats.get("false_positives", 0) + stats.get("false_negatives", 0)
        if errors:
            failing.append({"family": family, "errors": errors, "pass_rate": stats.get("pass_rate")})
    failing.sort(key=lambda item: (-item["errors"], item["pass_rate"] or 0, item["family"]))
    clean_count = sum(
        1
        for stats in family_stats.values()
        if (stats.get("false_positives", 0) + stats.get("false_negatives", 0)) == 0
    )
    return {
        "family_count": len(family_stats),
        "clean_family_count": clean_count,
        "failing_families": failing,
        "weakest_family": {
            "family": weakest[0],
            "pass_rate": weakest[1].get("pass_rate"),
            "errors": weakest[1].get("false_positives", 0) + weakest[1].get("false_negatives", 0),
        }
        if weakest
        else None,
    }


def summarize_calibration(report: dict | None, threshold: float | None) -> dict | None:
    if not report or threshold is None:
        return None

    positive_scores = [item["score"] for item in report["results"].get("should_trigger", [])]
    should_not_scores = [item["score"] for item in report["results"].get("should_not_trigger", [])]
    near_scores = [item["score"] for item in report["results"].get("near_neighbor", [])]
    non_trigger_scores = should_not_scores + near_scores
    total_cases = sum(len(items) for items in report["results"].values())
    boundary_cases = sum(
        1
        for items in report["results"].values()
        for item in items
        if item.get("boundary_case")
    )

    min_positive = min(positive_scores) if positive_scores else None
    max_non_trigger = max(non_trigger_scores) if non_trigger_scores else None
    positive_threshold_buffer = (min_positive - threshold) if min_positive is not None else None
    negative_threshold_buffer = (threshold - max_non_trigger) if max_non_trigger is not None else None
    score_gap = (min_positive - max_non_trigger) if min_positive is not None and max_non_trigger is not None else None
    margin_candidates = [value for value in (positive_threshold_buffer, negative_threshold_buffer) if value is not None]
    threshold_margin = min(margin_candidates) if margin_candidates else None

    risk_band = "healthy"
    if report["false_positives"] or report["false_negatives"] or (score_gap is not None and score_gap < 0):
        risk_band = "overlap"
    elif threshold_margin is not None and threshold_margin < 0.03:
        risk_band = "tight"
    elif threshold_margin is not None and threshold_margin < 0.08:
        risk_band = "watch"
    elif total_cases and (boundary_cases / total_cases) > 0.25:
        risk_band = "watch"

    return {
        "threshold": safe_round(threshold),
        "mean_positive_score": safe_round(sum(positive_scores) / len(positive_scores)) if positive_scores else None,
        "mean_non_trigger_score": safe_round(sum(non_trigger_scores) / len(non_trigger_scores)) if non_trigger_scores else None,
        "mean_near_neighbor_score": safe_round(sum(near_scores) / len(near_scores)) if near_scores else None,
        "min_positive_score": safe_round(min_positive),
        "max_non_trigger_score": safe_round(max_non_trigger),
        "score_gap": safe_round(score_gap),
        "threshold_margin": safe_round(threshold_margin),
        "positive_threshold_buffer": safe_round(positive_threshold_buffer),
        "negative_threshold_buffer": safe_round(negative_threshold_buffer),
        "boundary_case_count": boundary_cases,
        "boundary_case_rate": safe_round(boundary_cases / total_cases) if total_cases else None,
        "risk_band": risk_band,
    }


def build_gate_summary(
    winner_report: dict | None,
    current_report: dict | None,
    baseline_report: dict | None,
    threshold: float | None,
) -> dict:
    return {
        "winner": summarize_gate_report(winner_report),
        "current": summarize_gate_report(current_report),
        "baseline": summarize_gate_report(baseline_report),
        "winner_calibration": summarize_calibration(winner_report, threshold),
        "current_calibration": summarize_calibration(current_report, threshold),
        "baseline_calibration": summarize_calibration(baseline_report, threshold),
        "winner_family_health": summarize_family_health(winner_report),
        "current_family_health": summarize_family_health(current_report),
        "baseline_family_health": summarize_family_health(baseline_report),
    }


def optimize(
    current_description: str,
    dev_cases: dict,
    holdout_cases: dict | None,
    config: dict,
    baseline_description: str | None = None,
    blind_holdout_cases: dict | None = None,
    adversarial_cases: dict | None = None,
) -> dict:
    dev_threshold = dev_cases.get("recommended_threshold", 0.48)
    holdout_threshold = holdout_cases.get("recommended_threshold", dev_threshold) if holdout_cases else dev_threshold
    blind_holdout_threshold = (
        blind_holdout_cases.get("recommended_threshold", holdout_threshold) if blind_holdout_cases else holdout_threshold
    )
    adversarial_threshold = (
        adversarial_cases.get("recommended_threshold", blind_holdout_threshold)
        if adversarial_cases
        else blind_holdout_threshold
    )

    candidates = []
    for candidate in build_candidates(current_description, config):
        dev_report = evaluate(candidate["description"], dev_cases, dev_threshold, config)
        holdout_report = evaluate(candidate["description"], holdout_cases, holdout_threshold, config) if holdout_cases else None
        candidates.append(
            {
                "candidate": summarize_candidate(candidate, dev_report, holdout_report),
                "dev_report": dev_report,
                "holdout_report": holdout_report,
            }
        )

    candidates.sort(key=lambda item: item["candidate"]["selection_key"])
    winner = candidates[0]
    current = next(item for item in candidates if item["candidate"]["id"] == "current")

    baseline = None
    if baseline_description:
        baseline_dev = evaluate(baseline_description, dev_cases, dev_threshold, config)
        baseline_holdout = evaluate(baseline_description, holdout_cases, holdout_threshold, config) if holdout_cases else None
        baseline = {
            "description": sentence(baseline_description),
            "estimated_tokens": estimate_tokens(sentence(baseline_description)),
            "dev": baseline_dev,
            "holdout": baseline_holdout,
        }

    blind_reports = {}
    if blind_holdout_cases:
        blind_reports["current"] = evaluate(current["candidate"]["description"], blind_holdout_cases, blind_holdout_threshold, config)
        blind_reports["winner"] = evaluate(winner["candidate"]["description"], blind_holdout_cases, blind_holdout_threshold, config)
        if baseline:
            blind_reports["baseline"] = evaluate(
                baseline["description"], blind_holdout_cases, blind_holdout_threshold, config
            )

    judge_blind_reports = {}
    if blind_holdout_cases:
        judge_blind_reports["current"] = evaluate_judge(current["candidate"]["description"], blind_holdout_cases, config)
        judge_blind_reports["winner"] = evaluate_judge(winner["candidate"]["description"], blind_holdout_cases, config)
        if baseline:
            judge_blind_reports["baseline"] = evaluate_judge(baseline["description"], blind_holdout_cases, config)

    adversarial_reports = {}
    if adversarial_cases:
        adversarial_reports["current"] = evaluate(
            current["candidate"]["description"], adversarial_cases, adversarial_threshold, config
        )
        adversarial_reports["winner"] = evaluate(
            winner["candidate"]["description"], adversarial_cases, adversarial_threshold, config
        )
        if baseline:
            adversarial_reports["baseline"] = evaluate(
                baseline["description"], adversarial_cases, adversarial_threshold, config
            )

    report = {
        "current_description": sentence(current_description),
        "current_candidate": current["candidate"],
        "baseline": baseline,
        "winner": winner["candidate"],
        "winner_dev_report": winner["dev_report"],
        "winner_holdout_report": winner["holdout_report"],
        "current_dev_report": current["dev_report"],
        "current_holdout_report": current["holdout_report"],
        "winner_blind_holdout_report": blind_reports.get("winner"),
        "current_blind_holdout_report": blind_reports.get("current"),
        "baseline_blind_holdout_report": blind_reports.get("baseline"),
        "winner_judge_blind_holdout_report": judge_blind_reports.get("winner"),
        "current_judge_blind_holdout_report": judge_blind_reports.get("current"),
        "baseline_judge_blind_holdout_report": judge_blind_reports.get("baseline"),
        "winner_adversarial_holdout_report": adversarial_reports.get("winner"),
        "current_adversarial_holdout_report": adversarial_reports.get("current"),
        "baseline_adversarial_holdout_report": adversarial_reports.get("baseline"),
        "candidates": [item["candidate"] for item in candidates],
        "selection_logic": {
            "priority": [
                "fewest false positives",
                "fewest false negatives",
                "highest near-neighbor pass rate",
                "highest negative pass rate",
                "highest precision",
                "highest recall",
                "shortest description",
            ]
        },
        "comparison": {
            "winner_vs_current_dev": compare_reports(current["dev_report"], winner["dev_report"]),
            "winner_vs_current_holdout": compare_reports(current["holdout_report"], winner["holdout_report"])
            if current["holdout_report"] and winner["holdout_report"]
            else None,
            "winner_vs_current_blind_holdout": compare_reports(blind_reports["current"], blind_reports["winner"])
            if blind_reports.get("current") and blind_reports.get("winner")
            else None,
            "winner_vs_baseline_dev": compare_reports(baseline["dev"], winner["dev_report"]) if baseline else None,
            "winner_vs_baseline_holdout": compare_reports(baseline["holdout"], winner["holdout_report"])
            if baseline and baseline["holdout"] and winner["holdout_report"]
            else None,
            "winner_vs_baseline_blind_holdout": compare_reports(blind_reports["baseline"], blind_reports["winner"])
            if blind_reports.get("baseline") and blind_reports.get("winner")
            else None,
            "winner_vs_current_judge_blind_holdout": compare_reports(
                judge_blind_reports["current"], judge_blind_reports["winner"]
            )
            if judge_blind_reports.get("current") and judge_blind_reports.get("winner")
            else None,
            "winner_vs_baseline_judge_blind_holdout": compare_reports(
                judge_blind_reports["baseline"], judge_blind_reports["winner"]
            )
            if judge_blind_reports.get("baseline") and judge_blind_reports.get("winner")
            else None,
            "winner_vs_current_adversarial_holdout": compare_reports(
                adversarial_reports["current"], adversarial_reports["winner"]
            )
            if adversarial_reports.get("current") and adversarial_reports.get("winner")
            else None,
            "winner_vs_baseline_adversarial_holdout": compare_reports(
                adversarial_reports["baseline"], adversarial_reports["winner"]
            )
            if adversarial_reports.get("baseline") and adversarial_reports.get("winner")
            else None,
        },
        "acceptance_gates": {
            "selection_basis": "dev only",
            "holdout_non_regression": build_gate_summary(
                winner["holdout_report"],
                current["holdout_report"],
                baseline["holdout"] if baseline else None,
                holdout_threshold if holdout_cases else None,
            ),
            "blind_holdout_non_regression": build_gate_summary(
                blind_reports.get("winner"),
                blind_reports.get("current"),
                blind_reports.get("baseline"),
                blind_holdout_threshold if blind_holdout_cases else None,
            ),
            "judge_blind_holdout_non_regression": build_gate_summary(
                judge_blind_reports.get("winner"),
                judge_blind_reports.get("current"),
                judge_blind_reports.get("baseline"),
                None,
            ),
            "adversarial_holdout_non_regression": build_gate_summary(
                adversarial_reports.get("winner"),
                adversarial_reports.get("current"),
                adversarial_reports.get("baseline"),
                adversarial_threshold if adversarial_cases else None,
            ),
        },
    }
    report["summary"] = {
        "winner_label": report["winner"]["label"],
        "winner_tokens": report["winner"]["estimated_tokens"],
        "current_tokens": report["current_candidate"]["estimated_tokens"],
        "winner_dev_total_errors": report["winner"]["dev"]["false_positives"] + report["winner"]["dev"]["false_negatives"],
        "current_dev_total_errors": report["current_candidate"]["dev"]["false_positives"]
        + report["current_candidate"]["dev"]["false_negatives"],
        "winner_holdout_total_errors": report["winner"]["holdout"]["false_positives"] + report["winner"]["holdout"]["false_negatives"]
        if report["winner"].get("holdout")
        else None,
        "current_holdout_total_errors": report["current_candidate"]["holdout"]["false_positives"]
        + report["current_candidate"]["holdout"]["false_negatives"]
        if report["current_candidate"].get("holdout")
        else None,
        "winner_blind_holdout_total_errors": sum(error_tuple(blind_reports.get("winner")))
        if blind_reports.get("winner")
        else None,
        "current_blind_holdout_total_errors": sum(error_tuple(blind_reports.get("current")))
        if blind_reports.get("current")
        else None,
        "winner_judge_blind_holdout_total_errors": sum(error_tuple(judge_blind_reports.get("winner")))
        if judge_blind_reports.get("winner")
        else None,
        "current_judge_blind_holdout_total_errors": sum(error_tuple(judge_blind_reports.get("current")))
        if judge_blind_reports.get("current")
        else None,
        "winner_adversarial_holdout_total_errors": sum(error_tuple(adversarial_reports.get("winner")))
        if adversarial_reports.get("winner")
        else None,
        "current_adversarial_holdout_total_errors": sum(error_tuple(adversarial_reports.get("current")))
        if adversarial_reports.get("current")
        else None,
        "winner_judge_blind_agreement_rate": (
            report["acceptance_gates"]["judge_blind_holdout_non_regression"]["winner"].get("judge_summary", {}).get("agreement_rate")
            if report["acceptance_gates"]["judge_blind_holdout_non_regression"]["winner"]
            else None
        ),
        "winner_adversarial_risk_band": report["acceptance_gates"]["adversarial_holdout_non_regression"]["winner_calibration"]["risk_band"]
        if report["acceptance_gates"]["adversarial_holdout_non_regression"]["winner_calibration"]
        else None,
        "winner_adversarial_score_gap": report["acceptance_gates"]["adversarial_holdout_non_regression"]["winner_calibration"]["score_gap"]
        if report["acceptance_gates"]["adversarial_holdout_non_regression"]["winner_calibration"]
        else None,
        "candidate_count": len(report["candidates"]),
    }
    if baseline:
        report["summary"]["baseline_tokens"] = baseline["estimated_tokens"]
        report["summary"]["baseline_dev_total_errors"] = baseline["dev"]["false_positives"] + baseline["dev"]["false_negatives"]
        report["summary"]["baseline_holdout_total_errors"] = (
            baseline["holdout"]["false_positives"] + baseline["holdout"]["false_negatives"]
            if baseline.get("holdout")
            else None
        )
        report["summary"]["baseline_blind_holdout_total_errors"] = (
            sum(error_tuple(blind_reports.get("baseline"))) if blind_reports.get("baseline") else None
        )
        report["summary"]["baseline_judge_blind_holdout_total_errors"] = (
            sum(error_tuple(judge_blind_reports.get("baseline"))) if judge_blind_reports.get("baseline") else None
        )
        report["summary"]["baseline_adversarial_holdout_total_errors"] = (
            sum(error_tuple(adversarial_reports.get("baseline"))) if adversarial_reports.get("baseline") else None
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate and score description candidates on dev, holdout, blind, and adversarial suites."
    )
    parser.add_argument("--description-file", required=True)
    parser.add_argument("--baseline-description-file")
    parser.add_argument("--dev-cases", required=True)
    parser.add_argument("--holdout-cases")
    parser.add_argument("--blind-holdout-cases")
    parser.add_argument("--adversarial-cases")
    parser.add_argument("--semantic-config", required=True)
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--title", default="Description Optimization Report")
    args = parser.parse_args()

    current_description = read_description(Path(args.description_file))
    baseline_description = read_description(Path(args.baseline_description_file)) if args.baseline_description_file else None
    dev_cases = load_json(Path(args.dev_cases))
    holdout_cases = load_json(Path(args.holdout_cases)) if args.holdout_cases else None
    blind_holdout_cases = load_json(Path(args.blind_holdout_cases)) if args.blind_holdout_cases else None
    adversarial_cases = load_json(Path(args.adversarial_cases)) if args.adversarial_cases else None
    config = load_semantic_config(Path(args.semantic_config))

    report = optimize(
        current_description,
        dev_cases,
        holdout_cases,
        config,
        baseline_description,
        blind_holdout_cases,
        adversarial_cases,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(rendered + "\n", encoding="utf-8")
    if args.output_md:
        Path(args.output_md).write_text(render_markdown(report, args.title), encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
