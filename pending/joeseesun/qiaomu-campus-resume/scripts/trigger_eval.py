#!/usr/bin/env python3
"""Evaluate the campus-resume trigger and exclusion boundary."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains(text: str, patterns: list[str]) -> list[str]:
    normalized = normalize(text)
    return [pattern for pattern in patterns if normalize(pattern) in normalized]


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} 根节点必须是对象")
    return payload


def description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return text
    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return text
    frontmatter = "\n".join(lines[1:end])
    match = re.search(r"^description:\s*\|?\s*(.*?)(?=^\w[\w_-]*:|\Z)", frontmatter, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else frontmatter


def case_list(cases: dict[str, Any], bucket: str) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for item in cases.get(bucket, []):
        if isinstance(item, str):
            values.append({"text": item, "family": "default"})
        elif isinstance(item, dict):
            values.append(item)
    return values


def evaluate(root: Path, cases_path: Path) -> dict[str, Any]:
    cases = load(cases_path)
    desc = description(root / "SKILL.md")
    required = [str(value) for value in cases.get("description_required_terms", [])]
    missing = [value for value in required if normalize(value) not in normalize(desc)]
    resume_patterns = [str(value) for value in cases.get("resume_patterns", [])]
    student_patterns = [str(value) for value in cases.get("student_patterns", [])]
    negative_patterns = [str(value) for value in cases.get("negative_patterns", [])]

    results: dict[str, list[dict[str, Any]]] = {}
    failures: list[dict[str, Any]] = []
    total = passed = false_positive = false_negative = 0
    for bucket in ("should_trigger", "should_not_trigger", "near_neighbor"):
        expected = bucket == "should_trigger"
        bucket_results: list[dict[str, Any]] = []
        for item in case_list(cases, bucket):
            prompt = str(item.get("text", ""))
            resume_hits = contains(prompt, resume_patterns)
            student_hits = contains(prompt, student_patterns)
            negative_hits = contains(prompt, negative_patterns)
            predicted = bool(resume_hits and student_hits and not negative_hits)
            ok = predicted == expected
            record = {
                "prompt": prompt,
                "family": item.get("family", "default"),
                "expected_trigger": expected,
                "predicted_trigger": predicted,
                "passed": ok,
                "resume_hits": resume_hits,
                "student_hits": student_hits,
                "negative_hits": negative_hits,
            }
            bucket_results.append(record)
            total += 1
            if ok:
                passed += 1
            else:
                kind = "false_negative" if expected else "false_positive"
                false_negative += int(kind == "false_negative")
                false_positive += int(kind == "false_positive")
                failures.append({"bucket": bucket, "kind": kind, **record})
        results[bucket] = bucket_results

    return {
        "ok": not missing and not failures,
        "missing_description_terms": missing,
        "summary": {
            "total": total,
            "passed": passed,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "pass_rate": round(passed / total, 3) if total else 0,
        },
        "failures": failures,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="评估乔木大学生简历技能的触发边界。")
    parser.add_argument("skill_dir", nargs="?", default=".", help="技能目录")
    parser.add_argument("--cases", default="evals/trigger_cases.json", help="触发用例 JSON")
    parser.add_argument("--output", "-o", help="报告输出路径")
    args = parser.parse_args()
    root = Path(args.skill_dir).expanduser().resolve()
    cases_path = Path(args.cases)
    if not cases_path.is_absolute():
        cases_path = root / cases_path
    result = evaluate(root, cases_path)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if not result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
