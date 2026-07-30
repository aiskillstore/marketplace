#!/usr/bin/env python3
"""Scale one cocktail recipe under an explicit rounding contract."""

from __future__ import annotations

import json
import math
import sys
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
from pathlib import Path
from typing import Any


class InputError(ValueError):
    """Raised when input violates the scaling contract."""


def _decimal(value: Any, field: str, *, allow_zero: bool = False) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise InputError(f"{field} must be a number")
    try:
        number = Decimal(str(value))
    except Exception as error:
        raise InputError(f"{field} must be a number") from error
    if not number.is_finite():
        raise InputError(f"{field} must be finite")
    if allow_zero:
        if number < 0:
            raise InputError(f"{field} cannot be negative")
    elif number <= 0:
        raise InputError(f"{field} must be positive")
    return number


def _yield(data: dict[str, Any], field: str) -> tuple[Decimal, str]:
    raw = data.get(field)
    if not isinstance(raw, dict):
        raise InputError(f"{field} must be an object")
    unit = raw.get("unit")
    if not isinstance(unit, str) or not unit.strip():
        raise InputError(f"{field}.unit must be non-empty")
    return _decimal(raw.get("value"), f"{field}.value"), unit.strip()


def _round_to(value: Decimal, increment: Decimal, mode: str) -> Decimal:
    rounding = {
        "nearest": ROUND_HALF_UP,
        "up": ROUND_CEILING,
        "down": ROUND_FLOOR,
    }[mode]
    steps = (value / increment).to_integral_value(rounding=rounding)
    return steps * increment


def _plain(number: Decimal) -> str:
    return format(number.normalize(), "f")


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    original, original_unit = _yield(data, "original_yield")
    target, target_unit = _yield(data, "target_yield")
    if original_unit != target_unit:
        raise InputError("original_yield.unit and target_yield.unit must match")

    tolerance = _decimal(
        data.get("tolerance_percent"), "tolerance_percent", allow_zero=True
    )
    if tolerance > 10:
        raise InputError("tolerance_percent must be between 0 and 10")

    factor = target / original
    ingredients = data.get("ingredients")
    if not isinstance(ingredients, list) or not ingredients:
        raise InputError("ingredients must be a non-empty list")

    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    blockers: list[str] = []

    for index, ingredient in enumerate(ingredients):
        if not isinstance(ingredient, dict):
            raise InputError(f"ingredients[{index}] must be an object")
        name = ingredient.get("name")
        unit = ingredient.get("unit")
        mode = ingredient.get("mode")
        if not isinstance(name, str) or not name.strip():
            raise InputError(f"ingredients[{index}].name must be non-empty")
        name = name.strip()
        if name in seen:
            raise InputError(f"duplicate ingredient name: {name}")
        seen.add(name)
        if not isinstance(unit, str) or not unit.strip():
            raise InputError(f"{name}.unit must be non-empty")
        if mode not in {"linear", "count_up", "manual"}:
            raise InputError(f"{name}.mode must be linear, count_up, or manual")
        amount = _decimal(ingredient.get("amount"), f"{name}.amount", allow_zero=True)

        if mode == "manual":
            note = ingredient.get("note")
            if not isinstance(note, str) or not note.strip():
                raise InputError(f"{name}.note must explain the manual review")
            results.append(
                {
                    "name": name,
                    "unit": unit.strip(),
                    "mode": mode,
                    "original_amount": _plain(amount),
                    "scaled_amount": None,
                    "status": "manual_review",
                    "note": note.strip(),
                }
            )
            continue

        increment = _decimal(
            ingredient.get("rounding_increment"), f"{name}.rounding_increment"
        )
        rounding_mode = ingredient.get("rounding_mode")
        if mode == "count_up":
            rounding_mode = "up"
        elif rounding_mode not in {"nearest", "up", "down"}:
            raise InputError(f"{name}.rounding_mode must be nearest, up, or down")

        raw = amount * factor
        rounded = _round_to(raw, increment, rounding_mode)
        deviation = Decimal("0") if raw == 0 else abs(rounded - raw) / raw * 100
        status = "within_tolerance" if deviation <= tolerance else "outside_tolerance"
        if status == "outside_tolerance":
            blockers.append(name)
        results.append(
            {
                "name": name,
                "unit": unit.strip(),
                "mode": mode,
                "original_amount": _plain(amount),
                "raw_scaled_amount": _plain(raw),
                "rounded_amount": _plain(rounded),
                "rounding_increment": _plain(increment),
                "rounding_mode": rounding_mode,
                "deviation_percent": _plain(deviation.quantize(Decimal("0.001"))),
                "status": status,
            }
        )

    container = data.get("container_capacity")
    container_result = None
    if container is not None:
        if not isinstance(container, dict):
            raise InputError("container_capacity must be an object")
        capacity = _decimal(container.get("value"), "container_capacity.value")
        unit = container.get("unit")
        if unit != target_unit:
            raise InputError("container_capacity.unit must match target_yield.unit")
        count = math.ceil(target / capacity)
        unused = Decimal(count) * capacity - target
        container_result = {
            "capacity": _plain(capacity),
            "unit": unit,
            "container_count": count,
            "unused_capacity": _plain(unused),
        }

    return {
        "original_yield": {"value": _plain(original), "unit": original_unit},
        "target_yield": {"value": _plain(target), "unit": target_unit},
        "scale_factor": _plain(factor),
        "tolerance_percent": _plain(tolerance),
        "ingredients": results,
        "tolerance_blockers": blockers,
        "container_fit": container_result,
        "review_state": (
            "READY FOR RECIPE REVIEW"
            if not blockers
            else "NOT READY: ROUNDING OR INPUT BLOCKER"
        ),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: scale.py /absolute/path/to/input.json", file=sys.stderr)
        return 2
    try:
        payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise InputError("input must be a JSON object")
        print(json.dumps(calculate(payload), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, InputError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
