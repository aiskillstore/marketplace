#!/usr/bin/env python3
import argparse
import hashlib
import json
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

from run_output_eval import DEFAULT_CASES, display_path, grade_output, load_cases, validate_case


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "output_execution_runs.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "output_execution_runs.md"
VARIANTS = ("baseline", "with_skill")


def output_for_variant(case: dict[str, Any], variant: str) -> str:
    return str(case.get("baseline_output" if variant == "baseline" else "with_skill_output", ""))


def output_key(variant: str) -> str:
    return "baseline_output" if variant == "baseline" else "with_skill_output"


def parse_runner_command(value: str | None) -> list[str]:
    if not value:
        return []
    stripped = value.strip()
    if stripped.startswith("["):
        payload = json.loads(stripped)
        if not isinstance(payload, list) or not all(isinstance(item, str) and item for item in payload):
            raise ValueError("--runner-command JSON must be a non-empty string list")
        return payload
    return shlex.split(stripped)


def display_command(command: list[str]) -> list[str]:
    displayed: list[str] = []
    for item in command:
        path = Path(item)
        if path.is_absolute() and path.exists():
            displayed.append(display_path(path))
        else:
            displayed.append(item)
    return displayed


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, round(len(text) / 4))


def parse_runner_stdout(stdout: str) -> tuple[str, dict[str, Any]]:
    stripped = stdout.strip()
    if not stripped:
        return "", {}
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return stdout, {}
    if not isinstance(payload, dict):
        return stdout, {}
    return str(payload.get("output", "")), payload


def usage_payload(payload: dict[str, Any], prompt: str, output: str) -> dict[str, Any]:
    usage = payload.get("usage", {}) if isinstance(payload.get("usage"), dict) else {}
    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
    total_tokens = usage.get("total_tokens")
    estimated = bool(usage.get("estimated", False))
    if input_tokens is None:
        input_tokens = estimate_tokens(prompt)
        estimated = True
    if output_tokens is None:
        output_tokens = estimate_tokens(output)
        estimated = True
    if total_tokens is None:
        total_tokens = int(input_tokens or 0) + int(output_tokens or 0)
        estimated = True
    return {
        "input_tokens": int(input_tokens or 0),
        "output_tokens": int(output_tokens or 0),
        "total_tokens": int(total_tokens or 0),
        "estimated": estimated,
    }


def recorded_fixture_run(case: dict[str, Any], variant: str, assertions: list[dict[str, Any]]) -> dict[str, Any]:
    output = output_for_variant(case, variant)
    grade = grade_output(output, assertions)
    return {
        "case_id": str(case.get("id", "")),
        "variant": variant,
        "status": "pass",
        "execution_mode": "recorded_fixture",
        "model_executed": False,
        "command_executed": False,
        "duration_ms": None,
        "provider": "",
        "model": "",
        "usage": usage_payload({}, str(case.get("prompt", "")), output),
        "score": grade["score"],
        "passed_count": grade["passed_count"],
        "failed_count": grade["failed_count"],
        "failed_assertions": [item["id"] for item in grade["failed"]],
        "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "failure": "",
    }


def command_run(
    case: dict[str, Any],
    variant: str,
    assertions: list[dict[str, Any]],
    command: list[str],
    timeout_seconds: float,
) -> dict[str, Any]:
    request = {
        "case_id": str(case.get("id", "")),
        "variant": variant,
        "prompt": str(case.get("prompt", "")),
        "input_files": case.get("input_files", []),
        "metadata": case.get("metadata", {}),
        "fixture_output": output_for_variant(case, variant),
        "output_key": output_key(variant),
    }
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            input=json.dumps(request, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
    except subprocess.TimeoutExpired as exc:
        return {
            "case_id": request["case_id"],
            "variant": variant,
            "status": "fail",
            "execution_mode": "command",
            "model_executed": False,
            "command_executed": True,
            "duration_ms": round(timeout_seconds * 1000, 2),
            "provider": "",
            "model": "",
            "usage": usage_payload({}, request["prompt"], ""),
            "score": 0,
            "passed_count": 0,
            "failed_count": len(assertions),
            "failed_assertions": [str(item.get("id", "assertion")) for item in assertions],
            "output_sha256": "",
            "failure": f"runner timed out after {timeout_seconds}s: {exc}",
        }
    output, payload = parse_runner_stdout(proc.stdout)
    grade = grade_output(output, assertions)
    execution_kind = str(payload.get("execution_kind", "command"))
    provider = str(payload.get("provider", ""))
    model = str(payload.get("model", ""))
    model_executed = execution_kind == "model" and bool(model and provider)
    return {
        "case_id": request["case_id"],
        "variant": variant,
        "status": "pass" if proc.returncode == 0 and output else "fail",
        "execution_mode": execution_kind if execution_kind in {"command", "model"} else "command",
        "model_executed": model_executed,
        "command_executed": True,
        "duration_ms": duration_ms,
        "provider": provider,
        "model": model,
        "usage": usage_payload(payload, request["prompt"], output),
        "score": grade["score"] if output else 0,
        "passed_count": grade["passed_count"] if output else 0,
        "failed_count": grade["failed_count"] if output else len(assertions),
        "failed_assertions": [item["id"] for item in grade["failed"]] if output else [str(item.get("id", "assertion")) for item in assertions],
        "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest() if output else "",
        "failure": "" if proc.returncode == 0 and output else (proc.stderr.strip() or "runner returned no output"),
    }


def build_summary(runs: list[dict[str, Any]]) -> dict[str, Any]:
    variant_run_count = len(runs)
    case_ids = sorted({item["case_id"] for item in runs})
    baseline = [item for item in runs if item["variant"] == "baseline"]
    with_skill = [item for item in runs if item["variant"] == "with_skill"]
    baseline_average = sum(item["score"] for item in baseline) / len(baseline) if baseline else 0
    with_skill_average = sum(item["score"] for item in with_skill) / len(with_skill) if with_skill else 0
    regression_count = sum(
        1
        for case_id in case_ids
        if max((item["score"] for item in with_skill if item["case_id"] == case_id), default=0)
        < max((item["score"] for item in baseline if item["case_id"] == case_id), default=0)
    )
    failure_count = sum(1 for item in runs if item["status"] != "pass")
    command_executed_count = sum(1 for item in runs if item.get("command_executed"))
    model_executed_count = sum(1 for item in runs if item.get("model_executed"))
    recorded_fixture_count = sum(1 for item in runs if item.get("execution_mode") == "recorded_fixture")
    timing_observed_count = sum(1 for item in runs if item.get("duration_ms") is not None)
    token_estimated_count = sum(1 for item in runs if item.get("usage", {}).get("estimated"))
    token_observed_count = variant_run_count - token_estimated_count
    return {
        "case_count": len(case_ids),
        "variant_run_count": variant_run_count,
        "command_executed_count": command_executed_count,
        "model_executed_count": model_executed_count,
        "recorded_fixture_count": recorded_fixture_count,
        "timing_observed_count": timing_observed_count,
        "token_observed_count": token_observed_count,
        "token_estimated_count": token_estimated_count,
        "baseline_pass_rate": round(baseline_average, 2),
        "with_skill_pass_rate": round(with_skill_average, 2),
        "delta": round(with_skill_average - baseline_average, 2),
        "regression_count": regression_count,
        "failure_count": failure_count,
        "gate_pass": failure_count == 0 and with_skill_average >= baseline_average and regression_count == 0,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Output Execution Runs",
        "",
        "This report records how output-eval variants were produced and whether timing or token evidence is observed or estimated.",
        "",
        f"- Cases: `{summary['case_count']}`",
        f"- Variant runs: `{summary['variant_run_count']}`",
        f"- Command executed: `{summary['command_executed_count']}`",
        f"- Model executed: `{summary['model_executed_count']}`",
        f"- Recorded fixtures: `{summary['recorded_fixture_count']}`",
        f"- Timing observed: `{summary['timing_observed_count']}`",
        f"- Token observed: `{summary['token_observed_count']}`",
        f"- Token estimated: `{summary['token_estimated_count']}`",
        f"- Delta: `{summary['delta']}`",
        f"- Gate pass: `{summary['gate_pass']}`",
        "",
    ]
    if summary["model_executed_count"] == 0:
        lines.extend(
            [
                "No model-executed runs are recorded yet.",
                "",
                "Use `python3 scripts/yao.py output-exec --provider-runner openai` or `--runner-command` with a reviewed provider-backed runner to replace recorded fixtures with real model output evidence.",
                "",
            ]
        )
    if summary["command_executed_count"] > 0:
        lines.extend(
            [
                "Command runner evidence is present. This proves the eval harness executed an external command, but it is not provider-backed model evidence unless the runner reports model metadata.",
                "",
            ]
        )
    lines.extend(
        [
            "## Runs",
            "",
            "| Case | Variant | Mode | Model | Duration ms | Tokens | Score | Status |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for item in payload["runs"]:
        usage = item.get("usage", {})
        duration = "" if item.get("duration_ms") is None else str(item["duration_ms"])
        model = item.get("model") or item.get("provider") or ""
        lines.append(
            f"| {item['case_id']} | {item['variant']} | {item['execution_mode']} | {model} | "
            f"{duration} | {usage.get('total_tokens', 0)} | {item['score']} | {item['status']} |"
        )
    failures = [item for item in payload["runs"] if item.get("failure")]
    if failures:
        lines.extend(["", "## Failures", ""])
        for item in failures:
            lines.append(f"- `{item['case_id']}` `{item['variant']}`: {item['failure']}")
    lines.extend(
        [
            "",
            "## Next Fixes",
            "",
            "- Keep recorded fixtures as reproducible baselines, but do not describe them as model-executed evidence.",
            "- Use `scripts/provider_output_eval_runner.py` for provider-backed holdout cases when release confidence depends on real generation behavior.",
            "- Compare timing, token cost, and assertion deltas before promoting a skill to governed reuse.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def run_output_execution(
    cases_path: Path,
    output_json: Path,
    output_md: Path,
    runner_command: list[str],
    timeout_seconds: float,
) -> dict[str, Any]:
    cases = load_cases(cases_path)
    validation_failures = [failure for case in cases for failure in validate_case(case, cases_path.parent)]
    runs: list[dict[str, Any]] = []
    if not validation_failures:
        for case in cases:
            assertions = case.get("assertions", []) if isinstance(case.get("assertions"), list) else []
            for variant in VARIANTS:
                if runner_command:
                    runs.append(command_run(case, variant, assertions, runner_command, timeout_seconds))
                else:
                    runs.append(recorded_fixture_run(case, variant, assertions))
    summary = build_summary(runs)
    failures = validation_failures + [f"{item['case_id']} {item['variant']}: {item['failure']}" for item in runs if item.get("failure")]
    payload = {
        "schema_version": "1.0",
        "ok": not failures and summary["gate_pass"],
        "cases": display_path(cases_path),
        "runner": {
            "mode": "command" if runner_command else "recorded_fixture",
            "command": display_command(runner_command),
            "timeout_seconds": timeout_seconds if runner_command else None,
        },
        "summary": summary,
        "runs": runs,
        "failures": failures,
        "artifacts": {
            "json": display_path(output_json),
            "markdown": display_path(output_md),
        },
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Record output-eval execution evidence for static, command, or model-backed runs.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--runner-command", help="Command string or JSON string list. Receives a JSON request on stdin.")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    args = parser.parse_args()

    try:
        runner_command = parse_runner_command(args.runner_command)
    except (json.JSONDecodeError, ValueError) as exc:
        payload = {
            "schema_version": "1.0",
            "ok": False,
            "cases": display_path(Path(args.cases).resolve()),
            "runner": {"mode": "invalid", "command": [], "timeout_seconds": args.timeout_seconds},
            "summary": build_summary([]),
            "runs": [],
            "failures": [str(exc)],
            "artifacts": {"json": display_path(Path(args.output_json).resolve()), "markdown": display_path(Path(args.output_md).resolve())},
        }
        output_json = Path(args.output_json).resolve()
        output_md = Path(args.output_md).resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        output_md.write_text(render_markdown(payload), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        raise SystemExit(2)

    payload = run_output_execution(
        Path(args.cases).resolve(),
        Path(args.output_json).resolve(),
        Path(args.output_md).resolve(),
        runner_command,
        args.timeout_seconds,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(0 if payload["ok"] else 2)


if __name__ == "__main__":
    main()
