#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASES = ROOT / "evals" / "output" / "cases.jsonl"
BLIND_SEED = "yao-output-eval-blind-v1"


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"Output eval case at {path}:{line_number} must be an object")
        cases.append(payload)
    return cases


def normalize(text: str) -> str:
    return str(text).casefold()


def validate_case(case: dict[str, Any], cases_root: Path) -> list[str]:
    failures = []
    for key in ("id", "prompt", "baseline_output", "with_skill_output", "assertions"):
        if key not in case:
            failures.append(f"{case.get('id', '<unknown>')}: missing {key}")
    for raw_path in case.get("input_files", []):
        rel = Path(str(raw_path))
        if rel.is_absolute():
            failures.append(f"{case.get('id', '<unknown>')}: input_files must be relative: {raw_path}")
            continue
        target = (cases_root / rel).resolve()
        try:
            target.relative_to(cases_root.resolve())
        except ValueError:
            failures.append(f"{case.get('id', '<unknown>')}: input_file escapes eval folder: {raw_path}")
            continue
        if not target.exists():
            failures.append(f"{case.get('id', '<unknown>')}: input_file is missing: {raw_path}")
    assertions = case.get("assertions", [])
    if not isinstance(assertions, list) or not assertions:
        failures.append(f"{case.get('id', '<unknown>')}: assertions must be a non-empty list")
    for assertion in assertions if isinstance(assertions, list) else []:
        if not isinstance(assertion, dict):
            failures.append(f"{case.get('id', '<unknown>')}: assertion must be an object")
            continue
        if not assertion.get("id") or not assertion.get("description"):
            failures.append(f"{case.get('id', '<unknown>')}: assertion id and description are required")
    return failures


def check_assertion(output: str, assertion: dict[str, Any]) -> dict[str, Any]:
    lowered = normalize(output)
    required = [str(item) for item in assertion.get("required", [])]
    forbidden = [str(item) for item in assertion.get("forbidden", [])]
    missing = [item for item in required if normalize(item) not in lowered]
    present_forbidden = [item for item in forbidden if normalize(item) in lowered]
    passed = not missing and not present_forbidden
    return {
        "id": assertion.get("id", "assertion"),
        "description": assertion.get("description", ""),
        "weight": float(assertion.get("weight", 1) or 0),
        "failure_type": assertion.get("failure_type", "assertion_failed"),
        "passed": passed,
        "missing": missing,
        "present_forbidden": present_forbidden,
    }


def grade_output(output: str, assertions: list[dict[str, Any]]) -> dict[str, Any]:
    checks = [check_assertion(output, assertion) for assertion in assertions]
    total_weight = sum(item["weight"] for item in checks) or len(checks) or 1
    passed_weight = sum(item["weight"] for item in checks if item["passed"])
    failed = [item for item in checks if not item["passed"]]
    return {
        "score": round(passed_weight / total_weight * 100, 2),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
        "failed": failed,
    }


def grade_case(case: dict[str, Any]) -> dict[str, Any]:
    assertions = case.get("assertions", [])
    baseline = grade_output(str(case.get("baseline_output", "")), assertions)
    with_skill = grade_output(str(case.get("with_skill_output", "")), assertions)
    return {
        "id": case["id"],
        "prompt": case["prompt"],
        "input_files": case.get("input_files", []),
        "metadata": case.get("metadata", {}),
        "baseline": baseline,
        "with_skill": with_skill,
        "delta": round(with_skill["score"] - baseline["score"], 2),
        "winner": "with_skill" if with_skill["score"] >= baseline["score"] else "baseline",
        "failure_taxonomy": sorted({item["failure_type"] for item in with_skill["failed"]}),
    }


def blind_variant_order(case_id: str) -> list[str]:
    digest = hashlib.sha256(f"{BLIND_SEED}:{case_id}".encode("utf-8")).hexdigest()
    return ["baseline", "with_skill"] if int(digest[:2], 16) % 2 == 0 else ["with_skill", "baseline"]


def output_for_role(case: dict[str, Any], role: str) -> str:
    return str(case.get("baseline_output" if role == "baseline" else "with_skill_output", ""))


def expected_role(case: dict[str, Any]) -> str:
    review = case.get("human_review", {}) if isinstance(case.get("human_review"), dict) else {}
    winner = str(review.get("expected_winner", "with_skill"))
    return winner if winner in {"baseline", "with_skill"} else "with_skill"


def build_blind_review_pack(cases: list[dict[str, Any]], results: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    result_by_id = {item["id"]: item for item in results}
    pairs = []
    answer_pairs = []
    for case in cases:
        case_id = str(case["id"])
        order = blind_variant_order(case_id)
        variant_a_role, variant_b_role = order
        expected = expected_role(case)
        expected_variant = "A" if variant_a_role == expected else "B"
        assertions = case.get("assertions", []) if isinstance(case.get("assertions"), list) else []
        rubric = [
            {
                "id": str(item.get("id", "assertion")),
                "description": str(item.get("description", "")),
                "weight": float(item.get("weight", 1) or 0),
            }
            for item in assertions
            if isinstance(item, dict)
        ]
        pairs.append(
            {
                "case_id": case_id,
                "prompt": str(case.get("prompt", "")),
                "input_files": case.get("input_files", []),
                "metadata": case.get("metadata", {}),
                "review_instruction": "Pick A or B based only on the rubric. Do not infer which output came from the skill.",
                "rubric": rubric,
                "variant_a": {
                    "blind_id": f"{case_id}:A",
                    "output": output_for_role(case, variant_a_role),
                },
                "variant_b": {
                    "blind_id": f"{case_id}:B",
                    "output": output_for_role(case, variant_b_role),
                },
            }
        )
        scored = result_by_id.get(case_id, {})
        answer_pairs.append(
            {
                "case_id": case_id,
                "variant_a_role": variant_a_role,
                "variant_b_role": variant_b_role,
                "expected_winner_role": expected,
                "expected_winner_variant": expected_variant,
                "score_winner_role": scored.get("winner", ""),
                "delta": scored.get("delta", 0),
            }
        )
    pack = {
        "schema_version": "1.0",
        "seed": BLIND_SEED,
        "summary": {
            "pair_count": len(pairs),
            "answer_key_separate": True,
            "with_skill_hidden_count": sum(
                1
                for pair in answer_pairs
                if pair["variant_a_role"] == "with_skill" or pair["variant_b_role"] == "with_skill"
            ),
        },
        "pairs": pairs,
    }
    answer_key = {
        "schema_version": "1.0",
        "seed": BLIND_SEED,
        "summary": {
            "pair_count": len(answer_pairs),
            "with_skill_expected_count": sum(1 for pair in answer_pairs if pair["expected_winner_role"] == "with_skill"),
            "baseline_expected_count": sum(1 for pair in answer_pairs if pair["expected_winner_role"] == "baseline"),
        },
        "answers": answer_pairs,
    }
    return pack, answer_key


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len(results)
    baseline_average = sum(item["baseline"]["score"] for item in results) / case_count if case_count else 0
    with_skill_average = sum(item["with_skill"]["score"] for item in results) / case_count if case_count else 0
    regressions = [item for item in results if item["delta"] < 0]
    failures = sorted({failure for item in results for failure in item["failure_taxonomy"]})
    file_backed = [item for item in results if item.get("input_files")]
    near_neighbors = [item for item in results if item.get("metadata", {}).get("case_type") == "near_neighbor"]
    boundary_cases = [item for item in results if item.get("metadata", {}).get("case_type") == "boundary"]
    return {
        "case_count": case_count,
        "file_backed_case_count": len(file_backed),
        "near_neighbor_case_count": len(near_neighbors),
        "boundary_case_count": len(boundary_cases),
        "baseline_pass_rate": round(baseline_average, 2),
        "with_skill_pass_rate": round(with_skill_average, 2),
        "delta": round(with_skill_average - baseline_average, 2),
        "regression_count": len(regressions),
        "gate_pass": with_skill_average >= baseline_average and not regressions,
        "failure_taxonomy": failures,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Output Quality Scorecard",
        "",
        "This v0 scorecard compares static without-skill and with-skill outputs using assertion grading.",
        "",
        f"- Cases: `{summary['case_count']}`",
        f"- Baseline pass rate: `{summary['baseline_pass_rate']}`",
        f"- With-skill pass rate: `{summary['with_skill_pass_rate']}`",
        f"- Delta: `{summary['delta']}`",
        f"- Regressions: `{summary['regression_count']}`",
        f"- Blind A/B pairs: `{summary.get('blind_pair_count', 0)}`",
        f"- Gate pass: `{summary['gate_pass']}`",
        "",
        "Blind review artifacts are generated separately so reviewers can inspect A/B outputs without seeing the answer key.",
        "Run output review adjudication after reviewer decisions are recorded; pending cases should stay pending rather than being counted as human agreement.",
        "",
        "## Case Results",
        "",
        "| Case | Baseline | With Skill | Delta | Winner | Failed With-Skill Assertions |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for item in payload["results"]:
        failed = ", ".join(failure["id"] for failure in item["with_skill"]["failed"]) or "None"
        lines.append(
            f"| {item['id']} | {item['baseline']['score']} | {item['with_skill']['score']} | {item['delta']} | {item['winner']} | {failed} |"
        )
    lines.extend(["", "## Failure Taxonomy", ""])
    if summary["failure_taxonomy"]:
        for failure in summary["failure_taxonomy"]:
            lines.append(f"- {failure}")
    else:
        lines.append("- No with-skill assertion failures.")
    lines.extend(
        [
            "",
            "## Next Fixes",
            "",
            "- Add holdout cases before using this as a release gate.",
            "- Promote repeated failed assertions into the output-risk profile.",
            "- Keep assertions tied to material deliverables, not phrasing trivia.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_blind_review_markdown(pack: dict[str, Any]) -> str:
    summary = pack["summary"]
    lines = [
        "# Output Blind A/B Review Pack",
        "",
        "This packet hides whether each variant came from the baseline or the skill-guided output. Use the separate answer key only after review.",
        "",
        f"- Pairs: `{summary['pair_count']}`",
        f"- Seed: `{pack['seed']}`",
        f"- Answer key separate: `{summary['answer_key_separate']}`",
        "",
    ]
    for pair in pack["pairs"]:
        lines.extend(
            [
                f"## Case: {pair['case_id']}",
                "",
                f"Prompt: {pair['prompt']}",
                "",
                "Rubric:",
            ]
        )
        for item in pair["rubric"]:
            lines.append(f"- `{item['id']}` ({item['weight']}): {item['description']}")
        lines.extend(
            [
                "",
                "### Variant A",
                "",
                str(pair["variant_a"]["output"]),
                "",
                "### Variant B",
                "",
                str(pair["variant_b"]["output"]),
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def run_output_eval(
    cases_path: Path,
    output_json: Path,
    output_md: Path,
    blind_pack_json: Path,
    blind_pack_md: Path,
    blind_answer_key_json: Path,
) -> dict[str, Any]:
    cases = load_cases(cases_path)
    validation_failures = [failure for case in cases for failure in validate_case(case, cases_path.parent)]
    if validation_failures:
        blind_pack = {
            "schema_version": "1.0",
            "seed": BLIND_SEED,
            "summary": {"pair_count": 0, "answer_key_separate": True, "with_skill_hidden_count": 0},
            "pairs": [],
        }
        blind_answer_key = {
            "schema_version": "1.0",
            "seed": BLIND_SEED,
            "summary": {"pair_count": 0, "with_skill_expected_count": 0, "baseline_expected_count": 0},
            "answers": [],
        }
        payload = {
            "ok": False,
            "cases": display_path(cases_path),
            "summary": {
                "case_count": len(cases),
                "baseline_pass_rate": 0,
                "with_skill_pass_rate": 0,
                "delta": 0,
                "regression_count": 0,
                "gate_pass": False,
                "blind_pair_count": 0,
                "failure_taxonomy": ["invalid_case"],
            },
            "results": [],
            "failures": validation_failures,
        }
    else:
        results = [grade_case(case) for case in cases]
        blind_pack, blind_answer_key = build_blind_review_pack(cases, results)
        payload = {
            "ok": True,
            "cases": display_path(cases_path),
            "summary": build_summary(results),
            "results": results,
            "failures": [],
        }
        payload["summary"]["blind_pair_count"] = blind_pack["summary"]["pair_count"]
    payload["blind_review"] = {
        "pack": display_path(blind_pack_json),
        "answer_key": display_path(blind_answer_key_json),
        "pair_count": blind_pack["summary"]["pair_count"],
    }
    payload["artifacts"] = {
        "json": display_path(output_json),
        "markdown": display_path(output_md),
        "blind_review_pack_json": display_path(blind_pack_json),
        "blind_review_pack_md": display_path(blind_pack_md),
        "blind_answer_key_json": display_path(blind_answer_key_json),
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    blind_pack_json.parent.mkdir(parents=True, exist_ok=True)
    blind_pack_md.parent.mkdir(parents=True, exist_ok=True)
    blind_answer_key_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    blind_pack_json.write_text(json.dumps(blind_pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    blind_pack_md.write_text(render_blind_review_markdown(blind_pack), encoding="utf-8")
    blind_answer_key_json.write_text(json.dumps(blind_answer_key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Output Eval Lab assertion grading for with-skill vs baseline outputs.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--output-json", default=str(ROOT / "reports" / "output_quality_scorecard.json"))
    parser.add_argument("--output-md", default=str(ROOT / "reports" / "output_quality_scorecard.md"))
    parser.add_argument("--blind-pack-json", default=str(ROOT / "reports" / "output_blind_review_pack.json"))
    parser.add_argument("--blind-pack-md", default=str(ROOT / "reports" / "output_blind_review_pack.md"))
    parser.add_argument("--blind-answer-key-json", default=str(ROOT / "reports" / "output_blind_answer_key.json"))
    args = parser.parse_args()

    payload = run_output_eval(
        Path(args.cases).resolve(),
        Path(args.output_json).resolve(),
        Path(args.output_md).resolve(),
        Path(args.blind_pack_json).resolve(),
        Path(args.blind_pack_md).resolve(),
        Path(args.blind_answer_key_json).resolve(),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(0 if payload["ok"] else 2)


if __name__ == "__main__":
    main()
