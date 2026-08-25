#!/usr/bin/env python3
"""Independently recompute FFP labor and grand totals from raw JSON inputs."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


class InputError(ValueError):
    """Raised when validation inputs are missing or invalid."""


def _number(value: Any, label: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{label} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{label} must be finite")
    if minimum is not None and result < minimum:
        raise InputError(f"{label} must be at least {minimum}")
    return result


def _rate(value: Any, label: str) -> float:
    return _number(value, label, minimum=0)


def _setting(
    line: dict[str, Any],
    assumptions: dict[str, Any],
    key: str,
    *,
    rate: bool = False,
    minimum: float | None = None,
) -> float:
    if key in line:
        value = line[key]
    elif key in assumptions:
        value = assumptions[key]
    else:
        raise InputError(f"missing {key} for labor line {line.get('name', '<unnamed>')}")
    label = f"{line.get('name', '<unnamed>')}.{key}"
    return _rate(value, label) if rate else _number(value, label, minimum=minimum)


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    assumptions = payload.get("assumptions")
    labor_lines = payload.get("labor_lines")
    non_labor_lines = payload.get("non_labor_lines", [])

    if not isinstance(assumptions, dict):
        raise InputError("assumptions must be an object")
    if not isinstance(labor_lines, list) or not labor_lines:
        raise InputError("labor_lines must be a non-empty array")
    if not isinstance(non_labor_lines, list):
        raise InputError("non_labor_lines must be an array")

    calculated_labor: list[dict[str, Any]] = []
    labor_total = 0.0

    for index, raw_line in enumerate(labor_lines):
        if not isinstance(raw_line, dict):
            raise InputError(f"labor_lines[{index}] must be an object")
        name = raw_line.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InputError(f"labor_lines[{index}].name must be a non-empty string")

        annual_wage = _number(raw_line.get("annual_wage"), f"{name}.annual_wage", minimum=0)
        fringe = _setting(raw_line, assumptions, "fringe_rate", rate=True)
        overhead = _setting(raw_line, assumptions, "overhead_rate", rate=True)
        ga = _setting(raw_line, assumptions, "ga_rate", rate=True)
        profit = _setting(raw_line, assumptions, "profit_rate", rate=True)
        aging = _setting(raw_line, assumptions, "aging_factor", minimum=0)
        hours = _setting(raw_line, assumptions, "productive_hours", minimum=0)
        fte = _number(raw_line.get("fte"), f"{name}.fte", minimum=0)
        annual_priced_hours = hours * fte
        annual_coverage_hours: float | None = None
        if "annual_coverage_hours" in raw_line:
            annual_coverage_hours = _number(
                raw_line["annual_coverage_hours"],
                f"{name}.annual_coverage_hours",
                minimum=0,
            )
            if not math.isclose(
                annual_priced_hours,
                annual_coverage_hours,
                rel_tol=0.005,
                abs_tol=1.0,
            ):
                raise InputError(
                    f"{name}.productive_hours * fte is {annual_priced_hours:.4f}, "
                    f"which does not reconcile to annual_coverage_hours "
                    f"{annual_coverage_hours:.4f}"
                )
        months = _number(raw_line.get("months", 12), f"{name}.months", minimum=0)
        period_multiplier = _number(
            raw_line.get("period_multiplier", 1),
            f"{name}.period_multiplier",
            minimum=0,
        )

        aged_annual_wage = annual_wage * aging
        direct_hourly = aged_annual_wage / 2080.0
        fully_burdened_rate = (
            direct_hourly
            * (1 + fringe)
            * (1 + overhead)
            * (1 + ga)
            * (1 + profit)
        )
        total = fully_burdened_rate * hours * fte * (months / 12.0) * period_multiplier
        labor_total += total

        result: dict[str, Any] = {
            "name": name,
            "aged_annual_wage": aged_annual_wage,
            "direct_hourly_rate": direct_hourly,
            "fully_burdened_rate": fully_burdened_rate,
            "annual_priced_hours": annual_priced_hours,
            "labor_total": total,
        }
        if annual_coverage_hours is not None:
            result["annual_coverage_hours"] = annual_coverage_hours
        for key in ("workbook_fbr_cell", "workbook_total_cell"):
            if key in raw_line:
                if not isinstance(raw_line[key], str) or not raw_line[key].strip():
                    raise InputError(f"{name}.{key} must be a non-empty string")
                result[key] = raw_line[key]
        calculated_labor.append(result)

    calculated_non_labor: list[dict[str, Any]] = []
    non_labor_total = 0.0
    for index, raw_line in enumerate(non_labor_lines):
        if not isinstance(raw_line, dict):
            raise InputError(f"non_labor_lines[{index}] must be an object")
        name = raw_line.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InputError(f"non_labor_lines[{index}].name must be a non-empty string")
        amount = _number(raw_line.get("amount"), f"{name}.amount")
        non_labor_total += amount
        result = {"name": name, "amount": amount}
        if "workbook_total_cell" in raw_line:
            if not isinstance(raw_line["workbook_total_cell"], str):
                raise InputError(f"{name}.workbook_total_cell must be a string")
            result["workbook_total_cell"] = raw_line["workbook_total_cell"]
        calculated_non_labor.append(result)

    grand_total = labor_total + non_labor_total
    output: dict[str, Any] = {
        "labor_lines": calculated_labor,
        "non_labor_lines": calculated_non_labor,
        "labor_total": labor_total,
        "non_labor_total": non_labor_total,
        "grand_total": grand_total,
    }
    grand_total_cell = payload.get("workbook_grand_total_cell")
    if grand_total_cell is not None:
        if not isinstance(grand_total_cell, str) or not grand_total_cell.strip():
            raise InputError("workbook_grand_total_cell must be a non-empty string")
        output["workbook_grand_total_cell"] = grand_total_cell
    return output


def load_payload(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise InputError("top-level JSON value must be an object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recompute expected FFP rates and totals from raw validation inputs."
    )
    parser.add_argument("input", type=Path, help="Validation-input JSON file")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    try:
        result = calculate(load_payload(args.input))
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: cannot write {args.output}: {exc}", file=sys.stderr)
            return 2
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
