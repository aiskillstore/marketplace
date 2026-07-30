#!/usr/bin/env python3
"""Calculate a transparent party beverage supply plan."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


CATEGORIES = ("beer", "wine", "cocktails")


class InputError(ValueError):
    """Raised when calculator input violates the contract."""


def _number(data: dict[str, Any], key: str) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{key} must be a number")
    return float(value)


def _integer(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputError(f"{key} must be an integer")
    return value


def _largest_remainder(total: int, shares: dict[str, float]) -> dict[str, int]:
    raw = {key: total * shares[key] for key in shares}
    result = {key: math.floor(value) for key, value in raw.items()}
    remaining = total - sum(result.values())
    order = sorted(shares, key=lambda key: (-(raw[key] - result[key]), key))
    for key in order[:remaining]:
        result[key] += 1
    return result


def _validate_mix(raw_mix: Any) -> dict[str, float]:
    if not isinstance(raw_mix, dict) or set(raw_mix) != set(CATEGORIES):
        raise InputError("mix must contain beer, wine, and cocktails")
    mix: dict[str, float] = {}
    for key in CATEGORIES:
        value = raw_mix[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError(f"mix.{key} must be a number")
        if value < 0:
            raise InputError(f"mix.{key} cannot be negative")
        mix[key] = float(value)
    if not math.isclose(sum(mix.values()), 1.0, abs_tol=0.0001):
        raise InputError("mix shares must total 1.0")
    return mix


def _bounded_number(
    data: dict[str, Any], key: str, minimum: float, maximum: float
) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{key} must be a number")
    number = float(value)
    if not minimum <= number <= maximum:
        raise InputError(f"{key} must be between {minimum:g} and {maximum:g}")
    return number


def _validate_assumptions(raw_assumptions: Any) -> dict[str, Any]:
    if not isinstance(raw_assumptions, dict):
        raise InputError("planning_assumptions must be an object")
    source = raw_assumptions.get("source")
    reviewed_on = raw_assumptions.get("reviewed_on")
    ice_unit = raw_assumptions.get("ice_unit")
    if not isinstance(source, str) or not source.strip():
        raise InputError("planning_assumptions.source must be non-empty")
    if not isinstance(reviewed_on, str) or not reviewed_on.strip():
        raise InputError("planning_assumptions.reviewed_on must be non-empty")
    if ice_unit not in {"lb", "kg"}:
        raise InputError("planning_assumptions.ice_unit must be lb or kg")
    return {
        "alcoholic_servings_per_drinking_guest": _bounded_number(
            raw_assumptions,
            "alcoholic_servings_per_drinking_guest",
            0,
            12,
        ),
        "nonalcoholic_servings_per_guest": _bounded_number(
            raw_assumptions,
            "nonalcoholic_servings_per_guest",
            0,
            24,
        ),
        "water_liters_per_guest": _bounded_number(
            raw_assumptions, "water_liters_per_guest", 0, 10
        ),
        "ice_amount_per_guest": _bounded_number(
            raw_assumptions, "ice_amount_per_guest", 0, 10
        ),
        "ice_unit": ice_unit,
        "source": source.strip(),
        "reviewed_on": reviewed_on.strip(),
    }


def _validate_package_yields(raw_yields: Any) -> dict[str, float]:
    if not isinstance(raw_yields, dict):
        raise InputError("package_yields must be an object")
    result: dict[str, float] = {}
    for key in ("beer_units", "wine_bottles", "spirit_bottles"):
        value = raw_yields.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise InputError(f"package_yields.{key} must be positive")
        result[key] = float(value)
    return result


def _validate_inventory(raw_inventory: Any) -> dict[str, int]:
    inventory = raw_inventory or {}
    if not isinstance(inventory, dict):
        raise InputError("inventory must be an object")
    result: dict[str, int] = {}
    for key in ("beer_units", "wine_bottles", "spirit_bottles"):
        value = inventory.get(key, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise InputError(f"inventory.{key} must be a non-negative integer")
        result[key] = value
    return result


def _cocktail_batches(recipes: Any, cocktail_servings: int) -> list[dict[str, Any]]:
    if recipes is None:
        return []
    if not isinstance(recipes, list) or not recipes:
        raise InputError("cocktail_recipes must be a non-empty list")

    shares: dict[str, float] = {}
    by_name: dict[str, dict[str, Any]] = {}
    for recipe in recipes:
        if not isinstance(recipe, dict):
            raise InputError("each cocktail recipe must be an object")
        name = recipe.get("name")
        share = recipe.get("share")
        ingredients = recipe.get("ingredients")
        if not isinstance(name, str) or not name.strip():
            raise InputError("each cocktail recipe needs a name")
        if name in by_name:
            raise InputError(f"duplicate cocktail recipe name: {name}")
        if isinstance(share, bool) or not isinstance(share, (int, float)) or share <= 0:
            raise InputError(f"{name}.share must be positive")
        if not isinstance(ingredients, list) or not ingredients:
            raise InputError(f"{name}.ingredients must be a non-empty list")
        shares[name] = float(share)
        by_name[name] = recipe

    share_total = sum(shares.values())
    normalized = {name: share / share_total for name, share in shares.items()}
    servings = _largest_remainder(cocktail_servings, normalized)
    batches: list[dict[str, Any]] = []

    for name in sorted(by_name):
        recipe = by_name[name]
        scaled: list[dict[str, Any]] = []
        for ingredient in recipe["ingredients"]:
            if not isinstance(ingredient, dict):
                raise InputError(f"{name} ingredients must be objects")
            ingredient_name = ingredient.get("name")
            amount = ingredient.get("amount_oz")
            if not isinstance(ingredient_name, str) or not ingredient_name.strip():
                raise InputError(f"{name} has an ingredient without a name")
            if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0:
                raise InputError(f"{name}.{ingredient_name}.amount_oz must be positive")
            needed = round(float(amount) * servings[name], 2)
            available = ingredient.get("inventory_oz")
            if available is not None:
                if isinstance(available, bool) or not isinstance(available, (int, float)) or available < 0:
                    raise InputError(f"{name}.{ingredient_name}.inventory_oz cannot be negative")
                missing: float | None = round(max(0.0, needed - float(available)), 2)
            else:
                missing = None
            scaled.append(
                {
                    "name": ingredient_name,
                    "needed_oz": needed,
                    "needed_ml": round(needed * 29.5735),
                    "inventory_oz": available,
                    "shopping_gap_oz": missing,
                }
            )
        batches.append({"name": name, "servings": servings[name], "ingredients": scaled})
    return batches


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    total_guests = _integer(data, "total_guests")
    drinking_guests = _integer(data, "drinking_guests")
    duration = _number(data, "duration_hours")
    country = data.get("country")

    if not 1 <= total_guests <= 10_000:
        raise InputError("total_guests must be between 1 and 10000")
    if not 0 <= drinking_guests <= total_guests:
        raise InputError("drinking_guests must be between 0 and total_guests")
    if not 1 <= duration <= 12:
        raise InputError("duration_hours must be between 1 and 12")
    if not isinstance(country, str) or not country.strip():
        raise InputError("country must be non-empty")

    mix = _validate_mix(data.get("mix"))
    assumptions = _validate_assumptions(data.get("planning_assumptions"))
    package_yields = _validate_package_yields(data.get("package_yields"))
    raw_buffer = data.get("buffer_percent", 10)
    if isinstance(raw_buffer, bool) or not isinstance(raw_buffer, (int, float)):
        raise InputError("buffer_percent must be a number")
    buffer_percent = float(raw_buffer)
    if not 0 <= buffer_percent <= 25:
        raise InputError("buffer_percent must be between 0 and 25")
    inventory = _validate_inventory(data.get("inventory"))

    baseline = (
        drinking_guests
        * assumptions["alcoholic_servings_per_drinking_guest"]
    )
    total_servings = math.ceil(baseline * (1 + buffer_percent / 100))
    servings = _largest_remainder(total_servings, mix)
    packages = {
        "beer_units": math.ceil(servings["beer"] / package_yields["beer_units"]),
        "wine_bottles": math.ceil(
            servings["wine"] / package_yields["wine_bottles"]
        ),
        "spirit_bottles": math.ceil(
            servings["cocktails"] / package_yields["spirit_bottles"]
        ),
    }
    shopping_gaps = {
        key: max(0, packages[key] - inventory[key])
        for key in packages
    }
    non_alcoholic_servings = math.ceil(
        total_guests * assumptions["nonalcoholic_servings_per_guest"]
    )
    non_alcoholic = {
        "servings": non_alcoholic_servings,
        "water_liters": round(
            total_guests * assumptions["water_liters_per_guest"], 1
        ),
        "ice_amount": round(
            total_guests * assumptions["ice_amount_per_guest"], 1
        ),
        "ice_unit": assumptions["ice_unit"],
    }

    return {
        "assumptions": {
            "country": country.strip(),
            "duration_hours": duration,
            "drinking_guests": drinking_guests,
            "buffer_percent": buffer_percent,
            "mix": mix,
            "planning_assumptions": assumptions,
            "package_yields": package_yields,
            "quantity_boundary": "supply estimate, not a consumption target",
        },
        "total_planned_servings": total_servings,
        "servings": servings,
        "packages": packages,
        "shopping_gaps": shopping_gaps,
        "non_alcoholic": non_alcoholic,
        "cocktail_batches": _cocktail_batches(
            data.get("cocktail_recipes"), servings["cocktails"]
        ),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: calculate.py /absolute/path/to/input.json", file=sys.stderr)
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
