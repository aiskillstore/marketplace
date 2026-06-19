SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by optimize_description.py to render description optimization reports."


def render_markdown(report: dict, title: str) -> str:
    lines = [
        f"# {title}",
        "",
        f"Winner: `{report['winner']['label']}`",
        "",
        f"- current tokens: `{report['current_candidate']['estimated_tokens']}`",
        f"- winner tokens: `{report['winner']['estimated_tokens']}`",
    ]
    if report["baseline"]:
        lines.append(f"- baseline tokens: `{report['baseline']['estimated_tokens']}`")
    lines.extend(
        [
            "",
            "## Winner",
            "",
            report["winner"]["description"],
            "",
            "## Candidate Ranking",
            "",
            "| Candidate | Tokens | Dev FP | Dev FN | Dev Near | Holdout FP | Holdout FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for candidate in report["candidates"]:
        holdout = candidate.get("holdout", {})
        lines.append(
            f"| `{candidate['label']}` | {candidate['estimated_tokens']} | {candidate['dev']['false_positives']} | {candidate['dev']['false_negatives']} | {candidate['dev']['near_neighbor_pass_rate']} | {holdout.get('false_positives', '-')} | {holdout.get('false_negatives', '-')} |"
        )

    lines.extend(
        [
            "",
            "## Acceptance Gates",
            "",
            "| Gate | Winner FP | Winner FN | Current FP | Current FN | Baseline FP | Baseline FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for gate_name, gate in (
        ("Holdout", report["acceptance_gates"]["holdout_non_regression"]),
        ("Blind Holdout", report["acceptance_gates"]["blind_holdout_non_regression"]),
        ("Judge Blind Holdout", report["acceptance_gates"]["judge_blind_holdout_non_regression"]),
        ("Adversarial Holdout", report["acceptance_gates"]["adversarial_holdout_non_regression"]),
    ):
        winner_gate = gate.get("winner") or {}
        current_gate = gate.get("current") or {}
        baseline_gate = gate.get("baseline") or {}
        if not winner_gate and not current_gate and not baseline_gate:
            continue
        lines.append(
            f"| {gate_name} | {winner_gate.get('false_positives', '-')} | {winner_gate.get('false_negatives', '-')} | {current_gate.get('false_positives', '-')} | {current_gate.get('false_negatives', '-')} | {baseline_gate.get('false_positives', '-')} | {baseline_gate.get('false_negatives', '-')} |"
        )

    lines.extend(
        [
            "",
            "## Calibration",
            "",
            "| Gate | Winner Gap | Winner Risk | Winner Boundary Rate | Current Gap | Baseline Gap |",
            "| --- | ---: | --- | ---: | ---: | ---: |",
        ]
    )
    for gate_name, gate in (
        ("Holdout", report["acceptance_gates"]["holdout_non_regression"]),
        ("Blind Holdout", report["acceptance_gates"]["blind_holdout_non_regression"]),
        ("Judge Blind Holdout", report["acceptance_gates"]["judge_blind_holdout_non_regression"]),
        ("Adversarial Holdout", report["acceptance_gates"]["adversarial_holdout_non_regression"]),
    ):
        winner_calibration = gate.get("winner_calibration") or {}
        current_calibration = gate.get("current_calibration") or {}
        baseline_calibration = gate.get("baseline_calibration") or {}
        if not winner_calibration and not current_calibration and not baseline_calibration:
            continue
        lines.append(
            f"| {gate_name} | {winner_calibration.get('score_gap', '-')} | {winner_calibration.get('risk_band', '-')} | {winner_calibration.get('boundary_case_rate', '-')} | {current_calibration.get('score_gap', '-')} | {baseline_calibration.get('score_gap', '-')} |"
        )

    lines.extend(
        [
            "",
            "## Judge Blind Summary",
            "",
            "| Gate | Winner Agreement | Winner Mean Confidence | Current Agreement | Baseline Agreement |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    judge_gate = report["acceptance_gates"]["judge_blind_holdout_non_regression"]
    judge_winner = (judge_gate.get("winner") or {}).get("judge_summary") or {}
    judge_current = (judge_gate.get("current") or {}).get("judge_summary") or {}
    judge_baseline = (judge_gate.get("baseline") or {}).get("judge_summary") or {}
    if judge_winner or judge_current or judge_baseline:
        lines.append(
            f"| Judge Blind Holdout | {judge_winner.get('agreement_rate', '-')} | {judge_winner.get('mean_confidence', '-')} | {judge_current.get('agreement_rate', '-')} | {judge_baseline.get('agreement_rate', '-')} |"
        )

    lines.extend(
        [
            "",
            "## Family Health",
            "",
            "| Gate | Winner Clean Families | Winner Weakest Family | Current Clean Families | Baseline Clean Families |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for gate_name, gate in (
        ("Holdout", report["acceptance_gates"]["holdout_non_regression"]),
        ("Blind Holdout", report["acceptance_gates"]["blind_holdout_non_regression"]),
        ("Judge Blind Holdout", report["acceptance_gates"]["judge_blind_holdout_non_regression"]),
        ("Adversarial Holdout", report["acceptance_gates"]["adversarial_holdout_non_regression"]),
    ):
        winner_health = gate.get("winner_family_health") or {}
        current_health = gate.get("current_family_health") or {}
        baseline_health = gate.get("baseline_family_health") or {}
        if not winner_health and not current_health and not baseline_health:
            continue
        weakest = winner_health.get("weakest_family") or {}
        weakest_label = (
            f"{weakest.get('family')} ({weakest.get('errors')} errors)"
            if weakest.get("family")
            else "-"
        )
        lines.append(
            f"| {gate_name} | {winner_health.get('clean_family_count', '-')}/{winner_health.get('family_count', '-')} | {weakest_label} | {current_health.get('clean_family_count', '-')}/{current_health.get('family_count', '-')} | {baseline_health.get('clean_family_count', '-')}/{baseline_health.get('family_count', '-')} |"
        )

    lines.extend(
        [
            "",
            "## Selection Logic",
            "",
            "Ordered by:",
        ]
    )
    for item in report["selection_logic"]["priority"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"
