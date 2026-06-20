#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_snapshots(history_dir: Path) -> list[dict]:
    snapshots = []
    for path in sorted(history_dir.glob("*.json")):
        snapshots.append(json.loads(path.read_text(encoding="utf-8")))
    return snapshots


def render_markdown(snapshots: list[dict]) -> str:
    lines = [
        "# Description Drift History",
        "",
        "| Date | Label | Target | Winner | Tokens | Holdout FP | Holdout FN | Blind FP | Blind FN | Judge Blind Errors | Judge Agreement | Adv FP | Adv FN | Adv Gap | Adv Risk | Drift Note |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]

    previous_by_target: dict[str, dict] = {}

    def display(value: object) -> str:
        return "-" if value is None else str(value)

    def family_display(target: dict, gate: str) -> str:
        family = (target.get("family_health", {}) or {}).get(gate) or {}
        if not family:
            return "-"
        weakest = family.get("weakest_family") or {}
        weakest_label = weakest.get("family") or "-"
        return f"{family.get('clean_family_count', 0)}/{family.get('family_count', 0)} clean; weakest={weakest_label}"

    for snapshot in snapshots:
        for target in snapshot.get("targets", []):
            previous = previous_by_target.get(target["name"])
            drift_note = target.get("drift_note")
            if not drift_note and previous:
                token_delta = target["winner_tokens"] - previous["winner_tokens"]
                blind_prev = previous.get("winner_blind_holdout_total_errors")
                blind_now = target.get("winner_blind_holdout_total_errors")
                token_note = f"token delta {token_delta:+d}"
                if blind_prev is None or blind_now is None:
                    blind_note = "blind gate unchanged"
                else:
                    blind_note = f"blind error delta {blind_now - blind_prev:+d}"
                adv_prev = previous.get("winner_adversarial_holdout_total_errors")
                adv_now = target.get("winner_adversarial_holdout_total_errors")
                if adv_prev is None or adv_now is None:
                    adv_note = "adversarial gate unchanged"
                else:
                    adv_note = f"adversarial error delta {adv_now - adv_prev:+d}"
                drift_note = f"{token_note}; {blind_note}; {adv_note}"
            if not drift_note:
                drift_note = "initial snapshot"
            adversarial_calibration = (target.get("calibration", {}) or {}).get("adversarial_holdout") or {}
            judge_blind = (target.get("judge_blind") or {}).get("winner") or {}
            judge_errors = target.get("winner_judge_blind_holdout_total_errors")
            lines.append(
                f"| {snapshot['date']} | {snapshot['label']} | `{target['name']}` | `{target['winner_label']}` | {target['winner_tokens']} | {target['winner_holdout_fp']} | {target['winner_holdout_fn']} | {display(target.get('winner_blind_holdout_fp'))} | {display(target.get('winner_blind_holdout_fn'))} | {display(judge_errors)} | {display(judge_blind.get('agreement_rate'))} | {display(target.get('winner_adversarial_holdout_fp'))} | {display(target.get('winner_adversarial_holdout_fn'))} | {display(adversarial_calibration.get('score_gap'))} | {display(adversarial_calibration.get('risk_band'))} | {drift_note} |"
            )
            previous_by_target[target["name"]] = target

    lines.extend(
        [
            "",
            "## Family Coverage",
            "",
            "| Date | Label | Target | Blind Families | Judge Blind Families | Adversarial Families |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for snapshot in snapshots:
        for target in snapshot.get("targets", []):
            lines.append(
                f"| {snapshot['date']} | {snapshot['label']} | `{target['name']}` | {family_display(target, 'blind_holdout')} | {family_display(target, 'judge_blind_holdout')} | {family_display(target, 'adversarial_holdout')} |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render description optimization drift history.")
    parser.add_argument("--history-dir", default="evals/history/description_optimization")
    parser.add_argument("--output", default="reports/description_drift_history.md")
    args = parser.parse_args()

    snapshots = load_snapshots(Path(args.history_dir))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(snapshots), encoding="utf-8")


if __name__ == "__main__":
    main()
