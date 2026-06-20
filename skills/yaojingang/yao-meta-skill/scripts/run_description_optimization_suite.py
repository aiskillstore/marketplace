#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from optimize_description import optimize, read_description, render_markdown
from trigger_eval import load_json, load_semantic_config


ROOT = Path(__file__).resolve().parent.parent


TARGETS = [
    {
        "name": "yao-meta-skill",
        "title": "Root Description Optimization",
        "description_file": ROOT / "SKILL.md",
        "baseline_file": ROOT / "evals" / "baseline_description.txt",
        "dev_cases": ROOT / "evals" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "evals" / "holdout" / "trigger_cases.json",
        "blind_holdout_cases": ROOT / "evals" / "blind_holdout" / "trigger_cases.json",
        "adversarial_cases": ROOT / "evals" / "adversarial" / "trigger_cases.json",
        "semantic_config": ROOT / "evals" / "semantic_config.json",
        "output_json": ROOT / "reports" / "description_optimization.json",
        "output_md": ROOT / "reports" / "description_optimization.md",
    },
    {
        "name": "team-frontend-review",
        "title": "Frontend Review Description Optimization",
        "description_file": ROOT / "examples" / "team-frontend-review" / "generated-skill" / "SKILL.md",
        "baseline_file": ROOT / "examples" / "team-frontend-review" / "optimization" / "baseline_description.txt",
        "dev_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "holdout" / "trigger_cases.json",
        "blind_holdout_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "blind_holdout" / "trigger_cases.json",
        "adversarial_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "adversarial" / "trigger_cases.json",
        "semantic_config": ROOT / "examples" / "team-frontend-review" / "optimization" / "semantic_config.json",
        "output_json": ROOT / "examples" / "team-frontend-review" / "optimization" / "reports" / "description_optimization.json",
        "output_md": ROOT / "examples" / "team-frontend-review" / "optimization" / "reports" / "description_optimization.md",
    },
    {
        "name": "governed-incident-command",
        "title": "Governed Incident Description Optimization",
        "description_file": ROOT / "examples" / "governed-incident-command" / "generated-skill" / "SKILL.md",
        "baseline_file": ROOT / "examples" / "governed-incident-command" / "optimization" / "baseline_description.txt",
        "dev_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "holdout" / "trigger_cases.json",
        "blind_holdout_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "blind_holdout" / "trigger_cases.json",
        "adversarial_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "adversarial" / "trigger_cases.json",
        "semantic_config": ROOT / "examples" / "governed-incident-command" / "optimization" / "semantic_config.json",
        "output_json": ROOT / "examples" / "governed-incident-command" / "optimization" / "reports" / "description_optimization.json",
        "output_md": ROOT / "examples" / "governed-incident-command" / "optimization" / "reports" / "description_optimization.md",
    },
]


def report_errors(report: dict) -> tuple[int, int]:
    if "false_positives" in report and "false_negatives" in report:
        return (report["false_positives"], report["false_negatives"])
    return (
        report["holdout"]["false_positives"] if report.get("holdout") else report["dev"]["false_positives"],
        report["holdout"]["false_negatives"] if report.get("holdout") else report["dev"]["false_negatives"],
    )


def load_existing_snapshots(history_dir: Path, current_output: Path) -> list[dict]:
    snapshots = []
    for path in sorted(history_dir.glob("*.json")):
        if path == current_output:
            continue
        snapshots.append(json.loads(path.read_text(encoding="utf-8")))
    return snapshots


def target_error_total(target: dict, prefix: str) -> int | None:
    fp = target.get(f"{prefix}_fp")
    fn = target.get(f"{prefix}_fn")
    if fp is None or fn is None:
        return None
    return fp + fn


def calibration_gap(target: dict, gate: str) -> float | None:
    calibration = target.get("calibration", {}).get(gate) or {}
    return calibration.get("score_gap")


def family_gate_note(target: dict, gate: str) -> str:
    family = target.get("family_health", {}).get(gate) or {}
    if not family:
        return "n/a"
    weakest = family.get("weakest_family") or {}
    weakest_label = weakest.get("family") or "-"
    return f"{family.get('clean_family_count', 0)}/{family.get('family_count', 0)} clean; weakest={weakest_label}"


def drift_note_for_target(target: dict, previous: dict | None) -> str:
    if not previous:
        return "initial description optimization snapshot"

    notes = []
    token_delta = target["winner_tokens"] - previous["winner_tokens"]
    if token_delta == 0:
        notes.append("tokens stable")
    else:
        notes.append(f"tokens {token_delta:+d}")

    previous_blind = previous.get("winner_blind_holdout_total_errors")
    current_blind = target.get("winner_blind_holdout_total_errors")
    if previous_blind is None and current_blind is not None:
        notes.append(f"blind gate added with {current_blind} errors")
    elif previous_blind is not None and current_blind is not None:
        delta = current_blind - previous_blind
        if delta == 0:
            notes.append(f"blind stable at {current_blind}")
        else:
            notes.append(f"blind error delta {delta:+d}")

    previous_adv = previous.get("winner_adversarial_holdout_total_errors")
    current_adv = target.get("winner_adversarial_holdout_total_errors")
    if previous_adv is None and current_adv is not None:
        notes.append(f"adversarial gate added with {current_adv} errors")
    elif previous_adv is not None and current_adv is not None:
        delta = current_adv - previous_adv
        if delta == 0:
            notes.append(f"adversarial stable at {current_adv}")
        else:
            notes.append(f"adversarial error delta {delta:+d}")

    previous_holdout = target_error_total(previous, "winner_holdout")
    current_holdout = target_error_total(target, "winner_holdout")
    if previous_holdout is not None and current_holdout is not None:
        delta = current_holdout - previous_holdout
        if delta == 0:
            notes.append(f"holdout stable at {current_holdout}")
        else:
            notes.append(f"holdout error delta {delta:+d}")

    previous_gap = calibration_gap(previous, "adversarial_holdout")
    current_gap = calibration_gap(target, "adversarial_holdout")
    if previous_gap is None and current_gap is not None:
        notes.append(f"adversarial calibration {current_gap:+.3f}")
    elif previous_gap is not None and current_gap is not None:
        delta = current_gap - previous_gap
        if abs(delta) < 0.001:
            notes.append(f"adversarial calibration stable at {current_gap:+.3f}")
        else:
            notes.append(f"adversarial calibration delta {delta:+.3f}")

    previous_risk = (previous.get("calibration", {}).get("adversarial_holdout") or {}).get("risk_band")
    current_risk = (target.get("calibration", {}).get("adversarial_holdout") or {}).get("risk_band")
    if previous_risk != current_risk and current_risk:
        notes.append(f"risk {previous_risk or 'n/a'} -> {current_risk}")

    return "; ".join(notes)


def build_history_snapshot(summary: dict, args: argparse.Namespace) -> dict:
    existing_snapshots = load_existing_snapshots(Path(args.history_snapshot_output).parent, Path(args.history_snapshot_output))
    previous_by_target = {}
    for snapshot in existing_snapshots:
        for target in snapshot.get("targets", []):
            previous_by_target[target["name"]] = target

    targets = []
    for target in summary["targets"]:
        item = dict(target)
        item["drift_note"] = drift_note_for_target(item, previous_by_target.get(item["name"]))
        targets.append(item)

    return {
        "snapshot_id": args.snapshot_id,
        "date": args.snapshot_date,
        "commit": args.snapshot_commit,
        "label": args.snapshot_label,
        "targets": targets,
        "notes": [
            "recorded family-level blind, judge-backed blind, and adversarial routing evidence",
            "published calibration and drift history for description optimization",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run description optimization across root and example skills.")
    parser.add_argument("--history-snapshot-output")
    parser.add_argument("--snapshot-date")
    parser.add_argument("--snapshot-id", default="adversarial-calibration-and-family-drift")
    parser.add_argument("--snapshot-label", default="Adversarial Calibration And Family Drift")
    parser.add_argument("--snapshot-commit", default="local-snapshot")
    args = parser.parse_args()

    summary = {"targets": [], "ok": True}
    for target in TARGETS:
        current_description = read_description(target["description_file"])
        baseline_description = read_description(target["baseline_file"])
        dev_cases = load_json(target["dev_cases"])
        holdout_cases = load_json(target["holdout_cases"])
        blind_holdout_cases = load_json(target["blind_holdout_cases"])
        adversarial_cases = load_json(target["adversarial_cases"])
        config = load_semantic_config(target["semantic_config"])

        report = optimize(
            current_description,
            dev_cases,
            holdout_cases,
            config,
            baseline_description,
            blind_holdout_cases,
            adversarial_cases,
        )
        target["output_json"].parent.mkdir(parents=True, exist_ok=True)
        target["output_json"].write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        target["output_md"].write_text(render_markdown(report, target["title"]), encoding="utf-8")

        winner_fp, winner_fn = report_errors(report["winner"])
        current_fp, current_fn = report_errors(report["current_candidate"])
        baseline_fp, baseline_fn = report_errors(report["baseline"])
        blind_winner_fp, blind_winner_fn = report_errors(report["acceptance_gates"]["blind_holdout_non_regression"]["winner"])
        blind_current_fp, blind_current_fn = report_errors(report["acceptance_gates"]["blind_holdout_non_regression"]["current"])
        blind_baseline_fp, blind_baseline_fn = report_errors(report["acceptance_gates"]["blind_holdout_non_regression"]["baseline"])
        judge_blind_winner_fp, judge_blind_winner_fn = report_errors(
            report["acceptance_gates"]["judge_blind_holdout_non_regression"]["winner"]
        )
        judge_blind_current_fp, judge_blind_current_fn = report_errors(
            report["acceptance_gates"]["judge_blind_holdout_non_regression"]["current"]
        )
        judge_blind_baseline_fp, judge_blind_baseline_fn = report_errors(
            report["acceptance_gates"]["judge_blind_holdout_non_regression"]["baseline"]
        )
        adversarial_winner_fp, adversarial_winner_fn = report_errors(
            report["acceptance_gates"]["adversarial_holdout_non_regression"]["winner"]
        )
        adversarial_current_fp, adversarial_current_fn = report_errors(
            report["acceptance_gates"]["adversarial_holdout_non_regression"]["current"]
        )
        adversarial_baseline_fp, adversarial_baseline_fn = report_errors(
            report["acceptance_gates"]["adversarial_holdout_non_regression"]["baseline"]
        )

        target_ok = (
            (winner_fp, winner_fn) <= (current_fp, current_fn)
            and (winner_fp, winner_fn) <= (baseline_fp, baseline_fn)
            and (blind_winner_fp, blind_winner_fn) <= (blind_current_fp, blind_current_fn)
            and (blind_winner_fp, blind_winner_fn) <= (blind_baseline_fp, blind_baseline_fn)
            and (judge_blind_winner_fp, judge_blind_winner_fn) <= (judge_blind_current_fp, judge_blind_current_fn)
            and (judge_blind_winner_fp, judge_blind_winner_fn) <= (judge_blind_baseline_fp, judge_blind_baseline_fn)
            and (adversarial_winner_fp, adversarial_winner_fn) <= (adversarial_current_fp, adversarial_current_fn)
            and (adversarial_winner_fp, adversarial_winner_fn) <= (adversarial_baseline_fp, adversarial_baseline_fn)
        )
        summary["targets"].append(
            {
                "name": target["name"],
                "winner_label": report["winner"]["label"],
                "winner_description": report["winner"]["description"],
                "winner_tokens": report["winner"]["estimated_tokens"],
                "current_tokens": report["current_candidate"]["estimated_tokens"],
                "winner_holdout_fp": winner_fp,
                "winner_holdout_fn": winner_fn,
                "current_holdout_fp": current_fp,
                "current_holdout_fn": current_fn,
                "baseline_holdout_fp": baseline_fp,
                "baseline_holdout_fn": baseline_fn,
                "winner_blind_holdout_fp": blind_winner_fp,
                "winner_blind_holdout_fn": blind_winner_fn,
                "current_blind_holdout_fp": blind_current_fp,
                "current_blind_holdout_fn": blind_current_fn,
                "baseline_blind_holdout_fp": blind_baseline_fp,
                "baseline_blind_holdout_fn": blind_baseline_fn,
                "winner_blind_holdout_total_errors": blind_winner_fp + blind_winner_fn,
                "winner_judge_blind_holdout_fp": judge_blind_winner_fp,
                "winner_judge_blind_holdout_fn": judge_blind_winner_fn,
                "current_judge_blind_holdout_fp": judge_blind_current_fp,
                "current_judge_blind_holdout_fn": judge_blind_current_fn,
                "baseline_judge_blind_holdout_fp": judge_blind_baseline_fp,
                "baseline_judge_blind_holdout_fn": judge_blind_baseline_fn,
                "winner_judge_blind_holdout_total_errors": judge_blind_winner_fp + judge_blind_winner_fn,
                "winner_adversarial_holdout_fp": adversarial_winner_fp,
                "winner_adversarial_holdout_fn": adversarial_winner_fn,
                "current_adversarial_holdout_fp": adversarial_current_fp,
                "current_adversarial_holdout_fn": adversarial_current_fn,
                "baseline_adversarial_holdout_fp": adversarial_baseline_fp,
                "baseline_adversarial_holdout_fn": adversarial_baseline_fn,
                "winner_adversarial_holdout_total_errors": adversarial_winner_fp + adversarial_winner_fn,
                "calibration": {
                    "holdout": report["acceptance_gates"]["holdout_non_regression"]["winner_calibration"],
                    "blind_holdout": report["acceptance_gates"]["blind_holdout_non_regression"]["winner_calibration"],
                    "adversarial_holdout": report["acceptance_gates"]["adversarial_holdout_non_regression"]["winner_calibration"],
                },
                "judge_blind": {
                    "winner": (report["acceptance_gates"]["judge_blind_holdout_non_regression"]["winner"] or {}).get("judge_summary"),
                    "current": (report["acceptance_gates"]["judge_blind_holdout_non_regression"]["current"] or {}).get("judge_summary"),
                    "baseline": (report["acceptance_gates"]["judge_blind_holdout_non_regression"]["baseline"] or {}).get("judge_summary"),
                },
                "family_health": {
                    "holdout": report["acceptance_gates"]["holdout_non_regression"]["winner_family_health"],
                    "blind_holdout": report["acceptance_gates"]["blind_holdout_non_regression"]["winner_family_health"],
                    "judge_blind_holdout": report["acceptance_gates"]["judge_blind_holdout_non_regression"]["winner_family_health"],
                    "adversarial_holdout": report["acceptance_gates"]["adversarial_holdout_non_regression"]["winner_family_health"],
                },
                "drift_note": "blind, judge-backed blind, adversarial, and calibration gates active",
                "ok": target_ok,
            }
        )
        if not target_ok:
            summary["ok"] = False

    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    (ROOT / "reports" / "description_optimization_suite.json").write_text(rendered + "\n", encoding="utf-8")
    lines = [
        "# Description Optimization Suite",
        "",
        "| Target | Winner | Winner Tokens | Holdout FP | Holdout FN | Blind FP | Blind FN | Judge Blind Errors | Adv FP | Adv FN | Adv Gap | Adv Risk | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for target in summary["targets"]:
        lines.append(
            f"| `{target['name']}` | `{target['winner_label']}` | {target['winner_tokens']} | {target['winner_holdout_fp']} | {target['winner_holdout_fn']} | {target['winner_blind_holdout_fp']} | {target['winner_blind_holdout_fn']} | {target['winner_judge_blind_holdout_total_errors']} | {target['winner_adversarial_holdout_fp']} | {target['winner_adversarial_holdout_fn']} | {(target['calibration']['adversarial_holdout'] or {}).get('score_gap', '-')} | {(target['calibration']['adversarial_holdout'] or {}).get('risk_band', '-')} | {'ok' if target['ok'] else 'fail'} |"
        )
    lines.extend(
        [
            "",
            "## Family Coverage",
            "",
            "| Target | Blind Families | Judge Blind Families | Adversarial Families |",
            "| --- | --- | --- | --- |",
        ]
    )
    for target in summary["targets"]:
        lines.append(
            f"| `{target['name']}` | {family_gate_note(target, 'blind_holdout')} | {family_gate_note(target, 'judge_blind_holdout')} | {family_gate_note(target, 'adversarial_holdout')} |"
        )
    (ROOT / "reports" / "description_optimization_suite.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if args.history_snapshot_output:
        snapshot_path = Path(args.history_snapshot_output)
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot = build_history_snapshot(summary, args)
        snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(rendered)
    if not summary["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
