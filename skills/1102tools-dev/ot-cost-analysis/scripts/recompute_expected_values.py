#!/usr/bin/env python3
"""Independently recompute OT milestone costs from raw validation inputs."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


class InputError(ValueError):
    """Raised for invalid validation inputs."""


def _number(value: Any, label: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{label} must be finite")
    if minimum is not None and result < minimum:
        raise InputError(f"{label} must be at least {minimum}")
    return result


def _ratio(value: Any, label: str) -> float:
    result = _number(value, label, minimum=0)
    if result > 1:
        raise InputError(f"{label} must not exceed 1")
    return result


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{label} must be a non-empty string")
    return value.strip()


def _authority(assumptions: dict[str, Any]) -> tuple[str, str]:
    raw = _text(assumptions.get("authority"), "assumptions.authority").lower()
    aliases = {
        "research": "research",
        "4021": "research",
        "4021 research": "research",
        "prototype": "prototype",
        "4022": "prototype",
        "4022 prototype": "prototype",
        "production": "production",
        "4022(f)": "production",
        "4022(f) production": "production",
    }
    if raw not in aliases:
        raise InputError("assumptions.authority must identify research, prototype, or production")
    authority = aliases[raw]
    path = str(assumptions.get("authority_path", "N/A")).strip().upper()
    if authority == "prototype":
        if path not in {"A", "B", "C", "D"}:
            raise InputError("prototype authority_path must be A, B, C, or D")
    elif path not in {"", "N/A", "NA", "NONE"}:
        raise InputError("authority_path applies only to prototype OTs")
    return authority, path or "N/A"


def validate_authority(assumptions: dict[str, Any], performer_ratio: float) -> tuple[str, str]:
    authority, path = _authority(assumptions)
    if authority == "prototype" and path == "C" and performer_ratio + 1e-12 < (1 / 3):
        raise InputError("4022(d)(1)(C) performer share must be at least one-third")
    if authority == "prototype" and path == "D":
        status = _text(
            assumptions.get("exceptional_circumstances_status"),
            "assumptions.exceptional_circumstances_status",
        )
        if "competition" in status.lower() and "exception" not in status.lower():
            raise InputError("4022(d)(1)(D) is exceptional circumstances, not competition commitment")
    if authority == "research":
        _text(assumptions.get("research_ratio_source"), "assumptions.research_ratio_source")
    if authority == "production":
        source = _text(
            assumptions.get("production_ratio_source"),
            "assumptions.production_ratio_source",
        )
        if "inherit" in source.lower():
            raise InputError("production performer ratio must not be automatically inherited")
    return authority, path


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    assumptions = payload.get("assumptions")
    milestones = payload.get("milestones")
    if not isinstance(assumptions, dict):
        raise InputError("assumptions must be an object")
    if not isinstance(milestones, list) or not milestones:
        raise InputError("milestones must be a non-empty array")

    performer_ratio = _ratio(
        assumptions.get("performer_share_ratio"),
        "assumptions.performer_share_ratio",
    )
    authority, path = validate_authority(assumptions, performer_ratio)
    fee_rate = _ratio(assumptions.get("fee_rate", 0), "assumptions.fee_rate")
    burden = _number(
        assumptions.get("burden_multiplier"),
        "assumptions.burden_multiplier",
        minimum=0,
    )
    aging = _number(
        assumptions.get("labor_aging_factor"),
        "assumptions.labor_aging_factor",
        minimum=0,
    )
    labor_escalation = _ratio(
        assumptions.get("labor_escalation_rate", 0),
        "assumptions.labor_escalation_rate",
    )
    materials_escalation = _ratio(
        assumptions.get("materials_escalation_rate", 0),
        "assumptions.materials_escalation_rate",
    )
    ceiling_margin = _ratio(
        assumptions.get("cost_type_ceiling_margin", 0),
        "assumptions.cost_type_ceiling_margin",
    )

    outputs: list[dict[str, Any]] = []
    total_project_cost = 0.0
    total_government_funding = 0.0
    for index, raw in enumerate(milestones):
        if not isinstance(raw, dict):
            raise InputError(f"milestones[{index}] must be an object")
        milestone_id = _text(raw.get("id"), f"milestones[{index}].id")
        payment_type = _text(
            raw.get("payment_type"),
            f"milestones[{index}].payment_type",
        ).lower()
        if payment_type not in {"fixed", "cost-type"}:
            raise InputError(f"{milestone_id}.payment_type must be Fixed or Cost-Type")
        months = _number(
            raw.get("months_from_start", 0),
            f"{milestone_id}.months_from_start",
            minimum=0,
        )
        labor_factor = aging * ((1 + labor_escalation) ** (months / 12))
        material_factor = (1 + materials_escalation) ** (months / 12)

        labor_lines = raw.get("labor_lines")
        if not isinstance(labor_lines, list) or not labor_lines:
            raise InputError(f"{milestone_id}.labor_lines must be a non-empty array")
        labor_total = 0.0
        calculated_labor: list[dict[str, Any]] = []
        for line_index, line in enumerate(labor_lines):
            if not isinstance(line, dict):
                raise InputError(f"{milestone_id}.labor_lines[{line_index}] must be an object")
            name = _text(line.get("name"), f"{milestone_id}.labor_lines[{line_index}].name")
            annual_wage = _number(line.get("annual_wage"), f"{milestone_id}.{name}.annual_wage", minimum=0)
            hours = _number(line.get("hours"), f"{milestone_id}.{name}.hours", minimum=0)
            line_burden = _number(
                line.get("burden_multiplier", burden),
                f"{milestone_id}.{name}.burden_multiplier",
                minimum=0,
            )
            aged_direct_hourly = (annual_wage / 2080) * labor_factor
            burdened_rate = aged_direct_hourly * line_burden
            cost = burdened_rate * hours
            labor_total += cost
            calculated_labor.append(
                {
                    "name": name,
                    "aged_direct_hourly": aged_direct_hourly,
                    "burdened_rate": burdened_rate,
                    "hours": hours,
                    "cost": cost,
                }
            )

        materials_base = _number(raw.get("materials", 0), f"{milestone_id}.materials", minimum=0)
        materials = materials_base * material_factor
        travel = _number(raw.get("travel", 0), f"{milestone_id}.travel", minimum=0)
        odcs = _number(raw.get("odcs", 0), f"{milestone_id}.odcs", minimum=0)
        project_cost = labor_total + materials + travel + odcs
        ceiling = project_cost * (1 + ceiling_margin) if payment_type == "cost-type" else project_cost
        government_share = ceiling * (1 - performer_ratio)
        performer_share = ceiling * performer_ratio
        fee = ceiling * fee_rate
        government_funding = government_share + fee
        total_project_cost += project_cost
        total_government_funding += government_funding

        output: dict[str, Any] = {
            "id": milestone_id,
            "payment_type": payment_type,
            "labor_lines": calculated_labor,
            "labor_total": labor_total,
            "materials": materials,
            "travel": travel,
            "odcs": odcs,
            "project_cost": project_cost,
            "ceiling_basis": ceiling,
            "government_project_share": government_share,
            "performer_project_share": performer_share,
            "fee": fee,
            "government_funding": government_funding,
        }
        for key in (
            "workbook_project_cost_cell",
            "workbook_government_funding_cell",
            "workbook_ceiling_cell",
            "workbook_performer_share_cell",
        ):
            if key in raw:
                output[key] = _text(raw[key], f"{milestone_id}.{key}")
        outputs.append(output)

    result: dict[str, Any] = {
        "authority": authority,
        "authority_path": path,
        "milestones": outputs,
        "total_project_cost": total_project_cost,
        "total_government_funding": total_government_funding,
    }
    for key in (
        "workbook_total_project_cost_cell",
        "workbook_total_government_funding_cell",
    ):
        if key in payload:
            result[key] = _text(payload[key], key)
    return result


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
    parser = argparse.ArgumentParser(description="Recompute expected OT milestone values.")
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
