#!/usr/bin/env python3
"""Generate a deterministic public Dittobot quality scorecard."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from failure_taxonomy import unique_failure_buckets, unique_failure_codes
from live_report import read_records, summarize as summarize_live
from package_files import PACKAGE_FILES
from regression_100 import Case, make_cases, validate


ROOT = Path(__file__).resolve().parents[1]
SKILL_WORD_LIMIT = 1900
SUITE_NAME = "dittobot-regression-100"
SCHEMA_VERSION = "dittobot.scorecard.v1"
GuardrailCheck = Callable[[Case], bool]


GUARDRAILS: tuple[tuple[str, GuardrailCheck], ...] = (
    ("voice_preservation", lambda case: bool(case.preserve_voice)),
    ("protected_facts", lambda case: bool(case.protected)),
    ("claim_fidelity", lambda case: bool(case.required_claims or case.forbid_assertions)),
    ("uncertainty_handling", lambda case: case.preserve_uncertainty),
    ("source_only_default_inference", lambda case: case.prompt_mode == "source_only"),
    ("exact_word_constraints", lambda case: case.exact_words is not None),
    ("no_dash_constraints", lambda case: case.no_dash),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_value(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def family(case_id: str) -> str:
    parts = case_id.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else case_id


def rate(passed: int, total: int) -> float:
    return passed / total if total else 0.0


def row(name: str, passed: int, total: int) -> dict[str, Any]:
    return {
        "name": name,
        "cases": total,
        "passed": passed,
        "failed": total - passed,
        "rate": rate(passed, total),
    }


def guardrail_names(case: Case) -> list[str]:
    return [name for name, check in GUARDRAILS if check(case)]


def case_manifest(cases: list[Case]) -> list[dict[str, Any]]:
    return [
        {
            "id": case.id,
            "family": family(case.id),
            "prompt_mode": case.prompt_mode,
            "guardrails": guardrail_names(case),
        }
        for case in cases
    ]


def deterministic_records(cases: list[Case]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in cases:
        errors = validate(case)
        records.append(
            {
                "case": case.id,
                "family": family(case.id),
                "prompt_mode": case.prompt_mode,
                "guardrails": guardrail_names(case),
                "errors": errors,
                "failure_codes": unique_failure_codes(errors),
                "failure_buckets": unique_failure_buckets(errors),
            }
        )
    return records


def normalize_transcript_records(records: list[dict[str, Any]], cases: dict[str, Case]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        case_id = str(record.get("case", "unknown"))
        case = cases.get(case_id)
        errors = [str(error) for error in record.get("errors", []) if str(error)]
        normalized.append(
            {
                "case": case_id,
                "family": str(record.get("family") or family(case_id)),
                "prompt_mode": str(record.get("prompt_mode") or (case.prompt_mode if case else "unknown")),
                "guardrails": guardrail_names(case) if case else [],
                "errors": errors,
                "failure_codes": unique_failure_codes(errors),
                "failure_buckets": unique_failure_buckets(errors),
            }
        )
    return normalized


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    passed = sum(1 for record in records if not record["errors"])
    by_family_counter: dict[str, list[bool]] = {}
    by_prompt_counter: dict[str, list[bool]] = {}
    by_guardrail_counter: dict[str, list[bool]] = {}
    failure_codes: Counter[str] = Counter()
    failure_buckets: Counter[str] = Counter()
    failed_cases: list[dict[str, Any]] = []
    for record in records:
        ok = not record["errors"]
        by_family_counter.setdefault(record["family"], []).append(ok)
        by_prompt_counter.setdefault(record["prompt_mode"], []).append(ok)
        for guardrail in record["guardrails"]:
            by_guardrail_counter.setdefault(guardrail, []).append(ok)
        for code in record["failure_codes"]:
            failure_codes[code] += 1
        for bucket in record["failure_buckets"]:
            failure_buckets[bucket] += 1
        if record["errors"]:
            failed_cases.append(
                {
                    "case": record["case"],
                    "family": record["family"],
                    "prompt_mode": record["prompt_mode"],
                    "failure_codes": record["failure_codes"],
                    "failure_buckets": record["failure_buckets"],
                }
            )
    by_family = [
        row(name, sum(values), len(values))
        for name, values in sorted(by_family_counter.items())
    ]
    by_prompt_mode = [
        row(name, sum(values), len(values))
        for name, values in sorted(by_prompt_counter.items())
    ]
    by_guardrail = [
        row(name, sum(values), len(values))
        for name, values in sorted(by_guardrail_counter.items())
    ]
    family_balanced = (
        sum(item["rate"] for item in by_family) / len(by_family)
        if by_family else 0.0
    )
    guardrail_floor = min((item["rate"] for item in by_guardrail), default=0.0)
    case_pass_rate = rate(passed, total)
    return {
        "case_pass_rate": case_pass_rate,
        "family_balanced_pass_rate": family_balanced,
        "guardrail_floor": guardrail_floor,
        "public_score": min(case_pass_rate, family_balanced, guardrail_floor) * 100,
        "passed": passed,
        "total": total,
        "by_family": by_family,
        "by_prompt_mode": by_prompt_mode,
        "by_guardrail": by_guardrail,
        "failure_codes": dict(failure_codes.most_common()),
        "failure_buckets": dict(failure_buckets.most_common()),
        "failed_cases": failed_cases,
    }


def integrity(records: list[dict[str, Any]], known_cases: set[str], require_complete_suite: bool, raw_records: list[dict[str, Any]] | None) -> dict[str, Any]:
    ids = [str(record["case"]) for record in records]
    counts = Counter(ids)
    duplicates = sorted(case_id for case_id, count in counts.items() if count > 1)
    unknown_cases = sorted(case_id for case_id in counts if case_id not in known_cases)
    missing_cases = sorted(known_cases - set(ids)) if require_complete_suite else []
    raw_text_present = False
    if raw_records is not None:
        raw_text_present = any(
            "source" in record or "output" in record
            for record in raw_records
        )
    return {
        "complete_suite": not missing_cases and not unknown_cases and not duplicates,
        "duplicates": duplicates,
        "unknown_cases": unknown_cases,
        "missing_cases": missing_cases,
        "raw_text_present": raw_text_present,
    }


def skill_summary() -> dict[str, Any]:
    skill = ROOT / "SKILL.md"
    words = len(skill.read_text(encoding="utf-8").split())
    missing_package_files = [rel for rel in PACKAGE_FILES if not (ROOT / rel).exists()]
    return {
        "skill_words": words,
        "skill_word_limit": SKILL_WORD_LIMIT,
        "skill_under_budget": words <= SKILL_WORD_LIMIT,
        "package_files": len(PACKAGE_FILES),
        "missing_package_files": missing_package_files,
    }


def plugin_summary(plugin_dir: str | None, version: str | None) -> dict[str, Any] | None:
    if not plugin_dir:
        return None
    plugin = Path(plugin_dir).expanduser().resolve()
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    errors: list[str] = []
    manifest: dict[str, Any] = {}
    if not manifest_path.exists():
        errors.append("missing .codex-plugin/plugin.json")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("name") != "dittobot":
            errors.append("plugin name must be dittobot")
        if version and manifest.get("version") != version:
            errors.append(f"plugin version must be {version}")
        if manifest.get("skills") != "./skills/":
            errors.append("plugin skills path must be ./skills/")
    for rel in PACKAGE_FILES:
        source = ROOT / rel
        packaged = plugin / "skills" / "dittobot" / rel
        if not packaged.exists():
            errors.append(f"missing packaged file: {rel}")
        elif source.exists() and digest(source) != digest(packaged):
            errors.append(f"packaged file differs: {rel}")
    return {
        "checked": True,
        "status": "PASS" if not errors else "FAIL",
        "version": manifest.get("version"),
        "errors": errors,
    }


def scorecard(args: argparse.Namespace) -> dict[str, Any]:
    cases = make_cases()
    case_by_id = {case.id: case for case in cases}
    manifest = case_manifest(cases)
    raw_live_records = read_records(args.transcript) if args.transcript else None
    normalized = (
        normalize_transcript_records(raw_live_records, case_by_id)
        if raw_live_records is not None
        else deterministic_records(cases)
    )
    summary = summarize_records(normalized)
    suite_integrity = integrity(
        normalized,
        set(case_by_id),
        args.require_complete_suite or raw_live_records is None,
        raw_live_records,
    )
    plugin = plugin_summary(args.plugin_dir, args.version)
    subject_models = sorted(
        {str(record.get("model")) for record in raw_live_records or [] if record.get("model")}
    )
    status = "PASS"
    if (summary["public_score"] / 100) < args.fail_under_score:
        status = "FAIL"
    if not suite_integrity["complete_suite"] or (args.public and suite_integrity["raw_text_present"]):
        status = "FAIL"
    skill = skill_summary()
    if not skill["skill_under_budget"] or skill["missing_package_files"]:
        status = "FAIL"
    if plugin and plugin["status"] != "PASS":
        status = "FAIL"
    live_summary = summarize_live(raw_live_records) if raw_live_records else None
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "live_transcript" if raw_live_records is not None else "deterministic_fixture",
        "project": "dittobot",
        "suite": {
            "name": SUITE_NAME,
            "case_count": len(cases),
            "family_count": len({item["family"] for item in manifest}),
            "case_manifest_sha256": sha256_text(json.dumps(manifest, sort_keys=True)),
            "validator_sha256": digest(ROOT / "scripts" / "regression_100.py"),
        },
        "subject": {
            "commit": git_value(["rev-parse", "--short", "HEAD"]),
            "dirty": bool(git_value(["status", "--short"]) or ""),
            "skill_sha256": digest(ROOT / "SKILL.md"),
            "plugin_version": plugin.get("version") if plugin else None,
            "models": subject_models,
        },
        "score": {
            "status": status,
            "public_score": round(summary["public_score"], 2),
            "case_pass_rate": summary["case_pass_rate"],
            "family_balanced_pass_rate": summary["family_balanced_pass_rate"],
            "guardrail_floor": summary["guardrail_floor"],
        },
        "skill": skill,
        "coverage": {
            "prompt_modes": {
                item["name"]: item["cases"] for item in summary["by_prompt_mode"]
            },
            "guardrails": [
                {"name": item["name"], "cases": item["cases"]}
                for item in summary["by_guardrail"]
            ],
        },
        "results": {
            "passed": summary["passed"],
            "total": summary["total"],
            "by_guardrail": summary["by_guardrail"],
            "by_family": summary["by_family"],
            "by_prompt_mode": summary["by_prompt_mode"],
            "failure_codes": summary["failure_codes"],
            "failure_buckets": summary["failure_buckets"],
            "failed_cases": summary["failed_cases"],
        },
        "integrity": suite_integrity,
        "live_eval": live_summary,
        "plugin": plugin,
    }


def percent(value: float) -> str:
    return f"{value:.1%}"


def write_markdown(report: dict[str, Any]) -> None:
    score = report["score"]
    results = report["results"]
    print("# Dittobot Public Eval Scorecard")
    print()
    print(f"Suite: {report['suite']['name']}")
    print(f"Status: {score['status']}")
    print(f"Public score: {score['public_score']:.1f}")
    print()
    print("| Metric | Result |")
    print("|---|---:|")
    print(f"| Cases | {results['passed']}/{results['total']} |")
    print(f"| Case pass rate | {percent(score['case_pass_rate'])} |")
    print(f"| Family-balanced pass rate | {percent(score['family_balanced_pass_rate'])} |")
    print(f"| Guardrail floor | {percent(score['guardrail_floor'])} |")
    source_only = report["coverage"]["prompt_modes"].get("source_only", 0)
    print(f"| Source-only cases | {source_only} |")
    print(f"| Skill words | {report['skill']['skill_words']}/{report['skill']['skill_word_limit']} |")
    print()
    print("| Guardrail | Cases | Passed | Rate |")
    print("|---|---:|---:|---:|")
    for item in results["by_guardrail"]:
        print(f"| {item['name']} | {item['cases']} | {item['passed']} | {percent(item['rate'])} |")
    print()
    print("## Failures")
    if results["failed_cases"]:
        for item in results["failed_cases"][:10]:
            codes = ", ".join(item["failure_codes"]) or "other"
            print(f"- {item['case']}: {codes}")
    else:
        print("None.")
    print()
    print("## Integrity")
    integrity = report["integrity"]
    print(f"- Complete suite: {'yes' if integrity['complete_suite'] else 'no'}")
    print(f"- Duplicate records: {', '.join(integrity['duplicates']) or 'none'}")
    print(f"- Unknown cases: {', '.join(integrity['unknown_cases']) or 'none'}")
    print(f"- Missing cases: {len(integrity['missing_cases'])}")
    print(f"- Raw text present: {'yes' if integrity['raw_text_present'] else 'no'}")
    plugin = report.get("plugin")
    if plugin:
        print(f"- Plugin package: {plugin['status']} ({plugin.get('version') or 'unknown'})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", action="append", default=[], help="Optional live eval JSONL transcript.")
    parser.add_argument("--plugin-dir", help="Optional generated plugin package to check.")
    parser.add_argument("--version", default="0.2.0", help="Expected plugin version.")
    parser.add_argument("--require-complete-suite", action="store_true")
    parser.add_argument("--public", action="store_true", help="Fail if transcript records contain raw source/output text.")
    parser.add_argument("--fail-under-score", type=float, default=1.0)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--json", action="store_true", help="Backward-compatible alias for --format json.")
    args = parser.parse_args()

    if not 0 <= args.fail_under_score <= 1:
        raise SystemExit("--fail-under-score must be between 0 and 1.")

    report = scorecard(args)
    if args.json or args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        write_markdown(report)
    return 0 if report["score"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
