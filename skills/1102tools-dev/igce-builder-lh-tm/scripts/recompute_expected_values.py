#!/usr/bin/env python3
"""Independently recompute LH/T&M labor, non-labor, and total estimates."""

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


def _setting(line: dict[str, Any], assumptions: dict[str, Any], key: str) -> float:
    value = line[key] if key in line else assumptions.get(key)
    if value is None:
        raise InputError(f"missing {key} for {line.get('name', '<unnamed>')}")
    return _number(value, f"{line.get('name', '<unnamed>')}.{key}", minimum=0)


def _reference(raw: dict[str, Any], result: dict[str, Any], key: str) -> None:
    if key not in raw:
        return
    value = raw[key]
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{raw.get('name', '<unnamed>')}.{key} must be a non-empty string")
    result[key] = value


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

    contract_type = assumptions.get("contract_type")
    if not isinstance(contract_type, str) or contract_type.upper() not in {"LH", "T&M", "TM"}:
        raise InputError("assumptions.contract_type must be LH or T&M")
    contract_type = "T&M" if contract_type.upper() in {"T&M", "TM"} else "LH"

    labor_results: list[dict[str, Any]] = []
    totals = {"low": 0.0, "mid": 0.0, "high": 0.0}
    estimated_hours_total = 0.0
    ceiling_hours_total = 0.0

    for index, raw in enumerate(labor_lines):
        if not isinstance(raw, dict):
            raise InputError(f"labor_lines[{index}] must be an object")
        name = raw.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InputError(f"labor_lines[{index}].name must be a non-empty string")
        wage = _number(raw.get("annual_wage"), f"{name}.annual_wage", minimum=0)
        aging = _setting(raw, assumptions, "aging_factor")
        hours = _setting(raw, assumptions, "productive_hours")
        fte = _number(raw.get("fte"), f"{name}.fte", minimum=0)
        months = _number(raw.get("months", 12), f"{name}.months", minimum=0)
        period_multiplier = _number(
            raw.get("period_multiplier", 1), f"{name}.period_multiplier", minimum=0
        )
        estimated_hours = hours * fte * (months / 12.0) * period_multiplier
        estimated_hours_total += estimated_hours

        if "annual_coverage_hours" in raw:
            coverage = _number(
                raw["annual_coverage_hours"], f"{name}.annual_coverage_hours", minimum=0
            ) * (months / 12.0) * period_multiplier
            if not math.isclose(estimated_hours, coverage, rel_tol=0.005, abs_tol=1.0):
                raise InputError(
                    f"{name} estimated hours {estimated_hours:.4f} do not reconcile "
                    f"to coverage hours {coverage:.4f}"
                )

        ceiling_hours = _number(
            raw.get("ceiling_hours", estimated_hours), f"{name}.ceiling_hours", minimum=0
        )
        ceiling_hours_total += ceiling_hours
        aged_wage = wage * aging
        direct_rate = aged_wage / 2080.0
        result: dict[str, Any] = {
            "name": name,
            "aged_annual_wage": aged_wage,
            "direct_hourly_rate": direct_rate,
            "estimated_hours": estimated_hours,
            "ceiling_hours": ceiling_hours,
            "ceiling_variance_hours": ceiling_hours - estimated_hours,
        }
        for scenario in ("low", "mid", "high"):
            multiplier = _setting(raw, assumptions, f"burden_{scenario}")
            rate = direct_rate * multiplier
            amount = rate * estimated_hours
            result[f"burdened_{scenario}_rate"] = rate
            result[f"labor_{scenario}_total"] = amount
            totals[scenario] += amount
        for key in (
            "workbook_low_rate_cell",
            "workbook_mid_rate_cell",
            "workbook_high_rate_cell",
            "workbook_mid_total_cell",
        ):
            _reference(raw, result, key)
        labor_results.append(result)

    non_labor_total = 0.0
    non_labor_results: list[dict[str, Any]] = []
    for index, raw in enumerate(non_labor_lines):
        if not isinstance(raw, dict):
            raise InputError(f"non_labor_lines[{index}] must be an object")
        name = raw.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InputError(f"non_labor_lines[{index}].name must be a non-empty string")
        amount = _number(raw.get("amount"), f"{name}.amount", minimum=0)
        category = raw.get("category", "other")
        if not isinstance(category, str):
            raise InputError(f"{name}.category must be a string")
        if contract_type == "LH" and category.lower() == "materials" and amount > 0:
            raise InputError(f"{name} is a positive materials amount in an LH estimate")
        non_labor_total += amount
        result = {"name": name, "amount": amount, "category": category}
        _reference(raw, result, "workbook_total_cell")
        non_labor_results.append(result)

    output: dict[str, Any] = {
        "contract_type": contract_type,
        "labor_lines": labor_results,
        "non_labor_lines": non_labor_results,
        "labor_low_total": totals["low"],
        "labor_mid_total": totals["mid"],
        "labor_high_total": totals["high"],
        "non_labor_total": non_labor_total,
        "low_estimated_total": totals["low"] + non_labor_total,
        "mid_estimated_total": totals["mid"] + non_labor_total,
        "high_estimated_total": totals["high"] + non_labor_total,
        "estimated_hours_total": estimated_hours_total,
        "ceiling_hours_total": ceiling_hours_total,
    }
    ceiling_price = assumptions.get("ceiling_price")
    if ceiling_price is not None:
        ceiling = _number(ceiling_price, "ceiling_price", minimum=0)
        output["ceiling_price"] = ceiling
        output["ceiling_price_variance"] = ceiling - output["mid_estimated_total"]
    for key in (
        "workbook_low_total_cell",
        "workbook_mid_total_cell",
        "workbook_high_total_cell",
        "workbook_ceiling_price_cell",
    ):
        if key in payload:
            value = payload[key]
            if not isinstance(value, str) or not value.strip():
                raise InputError(f"{key} must be a non-empty string")
            output[key] = value
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
    parser = argparse.ArgumentParser(description="Recompute expected LH/T&M totals.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
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
