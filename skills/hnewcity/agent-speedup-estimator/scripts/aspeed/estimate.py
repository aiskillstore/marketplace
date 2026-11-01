from __future__ import annotations

import math
from typing import Dict

from .analyze import AgentAgg

DISK_SPEED = {"unknown": 1.0, "hdd": 1.0, "sata": 3.0, "nvme": 5.0, "nvme_gen4": 6.5}
SCENARIOS = ("conservative", "expected", "optimistic")


def validate_sensitivity(sens: dict) -> None:
    """Reject priors that can create negative or non-finite projected times."""
    cats = sens.get("categories") if isinstance(sens, dict) else None
    if not isinstance(cats, dict) or "other_tool" not in cats:
        raise ValueError("sensitivity must include categories.other_tool")
    for name, p in cats.items():
        if not isinstance(p, dict):
            raise ValueError(f"invalid sensitivity for {name}")
        for key in ("cpu", "disk"):
            values = p.get(key)
            if not isinstance(values, list) or len(values) != len(SCENARIOS):
                raise ValueError(f"{name}.{key} must contain three scenario shares")
        for v in p["cpu"] + p["disk"] + [p.get("mt")]:
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 1:
                raise ValueError(f"{name} shares and mt must be finite numbers between 0 and 1")
        if any(c + d > 1 for c, d in zip(p["cpu"], p["disk"])):
            raise ValueError(f"{name} CPU and disk shares must add up to at most 1")


def disk_ratio(current: str, target: str) -> float:
    cur, tgt = DISK_SPEED.get(current, 1.0), DISK_SPEED.get(target, 1.0)
    if current == "unknown":
        return 1.0
    return max(0.25, (tgt / cur) ** 0.5)


def cpu_ratio(base: dict, target: dict, mt_weight: float) -> float:
    r1 = target["gb6_single"] / base["gb6_single"]
    r2 = target["gb6_multi"] / base["gb6_multi"]
    return (r1 ** (1.0 - mt_weight)) * (r2 ** mt_weight)


def project(agg: AgentAgg, base: dict, target: dict, s_disk: float, sens: dict, idx: int, uncertainty: float = 1.0) -> dict:
    factor = (uncertainty, 1.0, 1.0 / uncertainty)[idx]
    base = {"gb6_single": base["gb6_single"] * factor, "gb6_multi": base["gb6_multi"] * factor}
    cats = sens["categories"]
    fallback = cats["other_tool"]
    tool_old = tool_new = 0.0
    per_cat: Dict[str, dict] = {}
    for name, c in agg.cats.items():
        p = cats.get(name, fallback)
        cf, df = p["cpu"][idx], p["disk"][idx]
        sensitive = c.base + (c.excess if idx == len(SCENARIOS) - 1 else 0.0)
        fixed = c.total - sensitive
        s_cpu = cpu_ratio(base, target, p["mt"])
        new = fixed + sensitive * (1.0 - cf - df + cf / s_cpu + df / s_disk)
        per_cat[name] = {"old_s": round(c.total, 1), "new_s": round(new, 1)}
        tool_old += c.total
        tool_new += new
    total_old = agg.model_s + tool_old
    total_new = agg.model_s + tool_new
    return {
        "tool_old_s": round(tool_old, 1),
        "tool_new_s": round(tool_new, 1),
        "tool_speedup": round(tool_old / tool_new, 3) if tool_new else 1.0,
        "total_old_s": round(total_old, 1),
        "total_new_s": round(total_new, 1),
        "total_speedup": round(total_old / total_new, 3) if total_new else 1.0,
        "saved_s": round(total_old - total_new, 1),
        "per_category": per_cat,
    }


def project_all(agg: AgentAgg, base: dict, target: dict, s_disk: float, sens: dict, uncertainty: float = 1.0) -> dict:
    return {name: project(agg, base, target, s_disk, sens, i, uncertainty) for i, name in enumerate(SCENARIOS)}
