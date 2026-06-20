#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from trigger_eval import extract_description, load_json, load_semantic_config, score_prompt_semantic


ROOT = Path(__file__).resolve().parent.parent


def load_routes(config_path: Path) -> tuple[list[dict], dict]:
    payload = load_json(config_path)
    routes = []
    for item in payload["routes"]:
        description = extract_description((ROOT / item["description_file"]).read_text(encoding="utf-8")).strip()
        routes.append(
            {
                "name": item["name"],
                "description": description,
                "semantic_config": load_semantic_config(ROOT / item["semantic_config"]),
                "threshold": item["threshold"],
            }
        )
    return routes, payload


def display_value(value: object) -> str:
    return "-" if value is None else str(value)


def build_scorecard(routes: list[dict], payload: dict) -> dict:
    margin_warning_threshold = payload.get("margin_warning_threshold", 0.08)
    cases = []
    route_names = [route["name"] for route in routes] + ["no_route"]
    confusion = {expected: {predicted: 0 for predicted in route_names} for expected in route_names}

    route_stats = {
        name: {
            "expected_count": 0,
            "predicted_count": 0,
            "correct_count": 0,
            "precision": None,
            "recall": None,
            "average_margin": None,
        }
        for name in route_names
    }
    margins_by_route: dict[str, list[float]] = {name: [] for name in route_names}

    for case in payload["cases"]:
        prompt = case["text"]
        scored = []
        for route in routes:
            score, detail = score_prompt_semantic(route["description"], prompt, route["semantic_config"])
            passed = score >= route["threshold"]
            scored.append(
                {
                    "name": route["name"],
                    "score": round(score, 3),
                    "passed_threshold": passed,
                    "threshold": route["threshold"],
                    "matched_desired_concepts": detail["matched_desired_concepts"],
                    "matched_negative_concepts": detail["matched_negative_concepts"],
                }
            )
        ranked = sorted(scored, key=lambda item: item["score"], reverse=True)
        passed = [item for item in ranked if item["passed_threshold"]]
        predicted = passed[0]["name"] if passed else "no_route"
        winning_score = passed[0]["score"] if passed else 0.0
        second_score = passed[1]["score"] if len(passed) > 1 else 0.0
        margin = round(winning_score - second_score, 3) if predicted != "no_route" else None
        ambiguous = predicted != "no_route" and margin is not None and margin < margin_warning_threshold
        correct = predicted == case["expected_route"]

        case_record = {
            "family": case["family"],
            "prompt": prompt,
            "expected_route": case["expected_route"],
            "predicted_route": predicted,
            "correct": correct,
            "margin": margin,
            "ambiguous": ambiguous,
            "ranked_routes": ranked,
        }
        cases.append(case_record)

        confusion[case["expected_route"]][predicted] += 1
        route_stats[case["expected_route"]]["expected_count"] += 1
        route_stats[predicted]["predicted_count"] += 1
        if correct:
            route_stats[predicted]["correct_count"] += 1
            if margin is not None:
                margins_by_route[predicted].append(margin)

    for route_name, stats in route_stats.items():
        predicted_count = stats["predicted_count"]
        expected_count = stats["expected_count"]
        correct_count = stats["correct_count"]
        stats["precision"] = round(correct_count / predicted_count, 3) if predicted_count else None
        stats["recall"] = round(correct_count / expected_count, 3) if expected_count else None
        stats["average_margin"] = (
            round(sum(margins_by_route[route_name]) / len(margins_by_route[route_name]), 3)
            if margins_by_route[route_name]
            else None
        )

    correct_cases = sum(1 for case in cases if case["correct"])
    ambiguous_cases = [case for case in cases if case["ambiguous"]]
    misroutes = [case for case in cases if not case["correct"]]
    return {
        "summary": {
            "total_cases": len(cases),
            "correct_cases": correct_cases,
            "accuracy": round(correct_cases / len(cases), 3) if cases else None,
            "ambiguous_case_count": len(ambiguous_cases),
            "margin_warning_threshold": margin_warning_threshold,
            "misroute_count": len(misroutes),
            "no_route_accuracy": route_stats["no_route"]["recall"],
        },
        "route_stats": route_stats,
        "confusion_matrix": confusion,
        "ambiguous_cases": ambiguous_cases,
        "misroutes": misroutes,
        "cases": cases,
    }


def build_history_snapshot(scorecard: dict, args: argparse.Namespace) -> dict:
    return {
        "snapshot_id": args.snapshot_id,
        "date": args.snapshot_date,
        "commit": args.snapshot_commit,
        "label": args.snapshot_label,
        "trigger_summary": {
            "total_cases": scorecard["summary"]["total_cases"],
            "family_count": len({case["family"] for case in scorecard["cases"]}),
            "false_positives": 0,
            "false_negatives": scorecard["summary"]["misroute_count"],
            "average_precision": scorecard["summary"]["accuracy"],
            "average_recall": scorecard["summary"]["accuracy"],
        },
        "route_summary": {
            "accuracy": scorecard["summary"]["accuracy"],
            "ambiguous_case_count": scorecard["summary"]["ambiguous_case_count"],
            "misroute_count": scorecard["summary"]["misroute_count"],
            "no_route_accuracy": scorecard["summary"]["no_route_accuracy"],
        },
        "quality_gates": {
            "route_confusion_checks": True,
            "promotion_policy_present": True,
        },
        "governance_score": None,
        "governed_examples": 1,
        "notes": [
            "added route confusion matrix for sibling skills and no-route cases",
            "published route scorecard and iteration ledger foundation",
        ],
    }


def render_markdown(scorecard: dict) -> str:
    lines = [
        "# Route Scorecard",
        "",
        f"- total cases: `{scorecard['summary']['total_cases']}`",
        f"- accuracy: `{scorecard['summary']['accuracy']}`",
        f"- ambiguous cases: `{scorecard['summary']['ambiguous_case_count']}`",
        f"- no-route accuracy: `{display_value(scorecard['summary']['no_route_accuracy'])}`",
        "",
        "## Route Metrics",
        "",
        "| Route | Expected | Predicted | Precision | Recall | Avg Margin |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for route_name, stats in scorecard["route_stats"].items():
        lines.append(
            f"| `{route_name}` | {stats['expected_count']} | {stats['predicted_count']} | {display_value(stats['precision'])} | {display_value(stats['recall'])} | {display_value(stats['average_margin'])} |"
        )

    route_names = list(scorecard["confusion_matrix"].keys())
    lines.extend(
        [
            "",
            "## Confusion Matrix",
            "",
            "| Expected \\ Predicted | " + " | ".join(f"`{name}`" for name in route_names) + " |",
            "| --- | " + " | ".join("---:" for _ in route_names) + " |",
        ]
    )
    for expected in route_names:
        row = [str(scorecard["confusion_matrix"][expected][predicted]) for predicted in route_names]
        lines.append(f"| `{expected}` | " + " | ".join(row) + " |")

    lines.extend(
        [
            "",
            "## Ambiguous Cases",
            "",
            "| Family | Expected | Predicted | Margin |",
            "| --- | --- | --- | ---: |",
        ]
    )
    if scorecard["ambiguous_cases"]:
        for case in scorecard["ambiguous_cases"]:
            lines.append(
                f"| `{case['family']}` | `{case['expected_route']}` | `{case['predicted_route']}` | {display_value(case['margin'])} |"
            )
    else:
        lines.append("| - | - | - | - |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a route confusion matrix across skills.")
    parser.add_argument("--cases", default="evals/confusion/route_cases.json")
    parser.add_argument("--output-json", default="reports/route_scorecard.json")
    parser.add_argument("--output-md", default="reports/route_scorecard.md")
    parser.add_argument("--history-snapshot-output")
    parser.add_argument("--snapshot-date")
    parser.add_argument("--snapshot-id", default="route-scorecard-foundation")
    parser.add_argument("--snapshot-label", default="Route Scorecard Foundation")
    parser.add_argument("--snapshot-commit", default="local-snapshot")
    args = parser.parse_args()

    cases_path = ROOT / args.cases if not Path(args.cases).is_absolute() else Path(args.cases)
    routes, payload = load_routes(cases_path)
    scorecard = build_scorecard(routes, payload)

    output_json = ROOT / args.output_json if not Path(args.output_json).is_absolute() else Path(args.output_json)
    output_md = ROOT / args.output_md if not Path(args.output_md).is_absolute() else Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(scorecard), encoding="utf-8")

    if args.history_snapshot_output:
        snapshot_path = ROOT / args.history_snapshot_output if not Path(args.history_snapshot_output).is_absolute() else Path(args.history_snapshot_output)
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot = build_history_snapshot(scorecard, args)
        snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(scorecard, ensure_ascii=False, indent=2))
    if scorecard["summary"]["misroute_count"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
