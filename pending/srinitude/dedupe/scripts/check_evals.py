#!/usr/bin/env python3
"""Schema checks for a skill's eval files.

Validates evals/evals.json (skill_name plus a list of cases with id,
prompt, expected_output, and assertions) and evals/trigger-queries.json
(a list of query and should_trigger pairs with both labels present).

Exit codes:
  0  both files pass
  1  at least one check failed
  2  usage or input error

Examples:
  python3 scripts/check_evals.py .
  python3 scripts/check_evals.py path/to/skill --min-cases 4 --min-queries 8
"""
import argparse
import json
import sys
from pathlib import Path


def nonempty(value):
    return isinstance(value, str) and value.strip()


def check_case(case, index, skill, problems):
    where = f"evals.json case {index}"
    if not isinstance(case.get("id"), int):
        problems.append(f"{where}: id must be an integer")
    for key in ["prompt", "expected_output"]:
        if not nonempty(case.get(key)):
            problems.append(f"{where}: {key} must be a non-empty string")
    assertions = case.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        problems.append(f"{where}: assertions must be a non-empty list")
    elif not all(nonempty(a) for a in assertions):
        problems.append(f"{where}: every assertion must be a string")
    for name in case.get("files", []):
        if not (skill / name).is_file():
            problems.append(f"{where}: listed file missing: {name}")


def check_cases(doc, skill, minimum, problems):
    if not nonempty(doc.get("skill_name")):
        problems.append("evals.json: skill_name must be a non-empty string")
    cases = doc.get("evals")
    if not isinstance(cases, list) or len(cases) < minimum:
        problems.append(f"evals.json: needs at least {minimum} cases")
        return
    ids = [case.get("id") for case in cases]
    if len(set(ids)) != len(ids):
        problems.append("evals.json: case ids must be unique")
    for index, case in enumerate(cases, start=1):
        check_case(case, index, skill, problems)


def check_queries(queries, minimum, problems):
    if not isinstance(queries, list) or len(queries) < minimum:
        problems.append(f"trigger-queries.json: needs at least {minimum} "
                        "queries")
        return
    labels = set()
    for index, entry in enumerate(queries, start=1):
        if not isinstance(entry, dict):
            problems.append(f"trigger-queries.json entry {index}: "
                            "must be an object")
            continue
        if not nonempty(entry.get("query")):
            problems.append(f"trigger-queries.json entry {index}: "
                            "query must be a non-empty string")
        flag = entry.get("should_trigger")
        if not isinstance(flag, bool):
            problems.append(f"trigger-queries.json entry {index}: "
                            "should_trigger must be true or false")
        labels.add(flag)
    if not {True, False} <= labels:
        problems.append("trigger-queries.json: needs positive and "
                        "negative queries")


def load(path, problems):
    if not path.is_file():
        problems.append(f"missing {path.parent.name}/{path.name}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        problems.append(f"{path.name}: invalid JSON: {error}")
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_dir", help="path to the skill directory")
    parser.add_argument("--min-cases", type=int, default=4)
    parser.add_argument("--min-queries", type=int, default=4)
    args = parser.parse_args(argv)
    skill = Path(args.skill_dir).resolve()
    if not skill.is_dir():
        print(f"error: no such directory: {skill}", file=sys.stderr)
        return 2
    problems = []
    doc = load(skill / "evals" / "evals.json", problems)
    if doc is not None:
        check_cases(doc, skill, args.min_cases, problems)
    queries = load(skill / "evals" / "trigger-queries.json", problems)
    if queries is not None:
        check_queries(queries, args.min_queries, problems)
    for problem in problems:
        print(problem)
    print(f"eval checks: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
