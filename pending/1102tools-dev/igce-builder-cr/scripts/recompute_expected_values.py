#!/usr/bin/env python3
"""Independently recompute CR cost, fee, and estimated price from raw inputs."""

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


def _setting(
    line: dict[str, Any], assumptions: dict[str, Any], key: str, *, minimum: float = 0
) -> float:
    if key in line:
        value = line[key]
    elif key in assumptions:
        value = assumptions[key]
    else:
        raise InputError(f"missing {key} for {line.get('name', '<unnamed>')}")
    return _number(value, f"{line.get('name', '<unnamed>')}.{key}", minimum=minimum)


def _fee_rate(assumptions: dict[str, Any]) -> tuple[str, float]:
    raw_type = assumptions.get("fee_type")
    if not isinstance(raw_type, str):
        raise InputError("assumptions.fee_type must be CPFF, CPAF, or CPIF")
    fee_type = raw_type.upper()
    primary = _number(assumptions.get("primary_fee_rate"), "primary_fee_rate", minimum=0)
    if fee_type == "CPFF" or fee_type == "CPIF":
        return fee_type, primary
    if fee_type == "CPAF":
        pool = _number(assumptions.get("award_pool_rate"), "award_pool_rate", minimum=0)
        earned = _number(assumptions.get("assumed_earned"), "assumed_earned", minimum=0)
        if earned > 1:
            raise InputError("assumed_earned must not exceed 1")
        return fee_type, primary + pool * earned
    raise InputError("assumptions.fee_type must be CPFF, CPAF, or CPIF")


def _copy_reference(raw: dict[str, Any], result: dict[str, Any], key: str) -> None:
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

    fee_type, effective_fee_rate = _fee_rate(assumptions)
    calculated_labor: list[dict[str, Any]] = []
    fee_bearing_cost = 0.0

    for index, raw in enumerate(labor_lines):
        if not isinstance(raw, dict):
            raise InputError(f"labor_lines[{index}] must be an object")
        name = raw.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InputError(f"labor_lines[{index}].name must be a non-empty string")

        annual_wage = _number(raw.get("annual_wage"), f"{name}.annual_wage", minimum=0)
        aging = _setting(raw, assumptions, "aging_factor")
        fringe = _setting(raw, assumptions, "fringe_rate")
        overhead = _setting(raw, assumptions, "overhead_rate")
        ga = _setting(raw, assumptions, "ga_rate")
        fccm = _setting(raw, assumptions, "fccm_rate")
        hours = _setting(raw, assumptions, "productive_hours")
        fte = _number(raw.get("fte"), f"{name}.fte", minimum=0)
        months = _number(raw.get("months", 12), f"{name}.months", minimum=0)
        period_multiplier = _number(
            raw.get("period_multiplier", 1), f"{name}.period_multiplier", minimum=0
        )

        priced_hours = hours * fte
        if "annual_coverage_hours" in raw:
            coverage = _number(
                raw["annual_coverage_hours"], f"{name}.annual_coverage_hours", minimum=0
            )
            if not math.isclose(priced_hours, coverage, rel_tol=0.005, abs_tol=1.0):
                raise InputError(
                    f"{name}.productive_hours * fte is {priced_hours:.4f}, "
                    f"which does not reconcile to annual_coverage_hours {coverage:.4f}"
                )

        aged_wage = annual_wage * aging
        direct = aged_wage / 2080.0
        fringe_amount = direct * fringe
        labor_fringe = direct + fringe_amount
        overhead_amount = labor_fringe * overhead
        subtotal = labor_fringe + overhead_amount
        ga_amount = subtotal * ga
        fccm_amount = (subtotal + ga_amount) * fccm
        cost_rate = subtotal + ga_amount + fccm_amount
        fee_rate = cost_rate * effective_fee_rate
        price_rate = cost_rate + fee_rate
        period_cost = cost_rate * hours * fte * (months / 12.0) * period_multiplier
        period_fee = period_cost * effective_fee_rate
        period_price = period_cost + period_fee
        fee_bearing_cost += period_cost

        result: dict[str, Any] = {
            "name": name,
            "aged_annual_wage": aged_wage,
            "direct_hourly_rate": direct,
            "estimated_cost_rate": cost_rate,
            "estimated_fee_rate": fee_rate,
            "estimated_price_rate": price_rate,
            "period_cost": period_cost,
            "period_fee": period_fee,
            "period_price": period_price,
        }
        for key in (
            "workbook_cost_rate_cell",
            "workbook_price_rate_cell",
            "workbook_total_cost_cell",
            "workbook_total_price_cell",
        ):
            _copy_reference(raw, result, key)
        calculated_labor.append(result)

    non_fee_cost = 0.0
    calculated_non_labor: list[dict[str, Any]] = []
    for index, raw in enumerate(non_labor_lines):
        if not isinstance(raw, dict):
            raise InputError(f"non_labor_lines[{index}] must be an object")
        name = raw.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InputError(f"non_labor_lines[{index}].name must be a non-empty string")
        amount = _number(raw.get("amount"), f"{name}.amount", minimum=0)
        fee_bearing = raw.get("fee_bearing", False)
        if not isinstance(fee_bearing, bool):
            raise InputError(f"{name}.fee_bearing must be true or false")
        if fee_bearing:
            fee_bearing_cost += amount
        else:
            non_fee_cost += amount
        result = {"name": name, "amount": amount, "fee_bearing": fee_bearing}
        _copy_reference(raw, result, "workbook_total_cell")
        calculated_non_labor.append(result)

    total_cost = fee_bearing_cost + non_fee_cost
    total_fee = fee_bearing_cost * effective_fee_rate
    total_price = total_cost + total_fee
    output: dict[str, Any] = {
        "fee_type": fee_type,
        "effective_fee_rate": effective_fee_rate,
        "labor_lines": calculated_labor,
        "non_labor_lines": calculated_non_labor,
        "fee_bearing_cost": fee_bearing_cost,
        "non_fee_bearing_cost": non_fee_cost,
        "total_estimated_cost": total_cost,
        "total_fee": total_fee,
        "total_estimated_price": total_price,
    }
    for key in (
        "workbook_fee_bearing_cost_cell",
        "workbook_total_cost_cell",
        "workbook_total_fee_cell",
        "workbook_total_price_cell",
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
    parser = argparse.ArgumentParser(description="Recompute expected CR cost and fee totals.")
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
