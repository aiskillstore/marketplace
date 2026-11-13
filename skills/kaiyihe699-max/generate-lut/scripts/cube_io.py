"""Strict shared reader for normalized 3D .cube files (red changes fastest)."""
from __future__ import annotations

import math
from pathlib import Path


def read_cube(path: Path) -> tuple[int, list[tuple[float, float, float]], list[str]]:
    size = None
    values = []
    seen = set()
    for line_number, raw in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        key = parts[0].upper()
        where = f"{Path(path).name}:{line_number}"
        if key in {"TITLE", "LUT_3D_SIZE", "DOMAIN_MIN", "DOMAIN_MAX"}:
            if key in seen:
                raise ValueError(f"{where}: duplicate {key} header.")
            if values:
                raise ValueError(f"{where}: headers must precede RGB data.")
            seen.add(key)
            if key == "TITLE":
                continue
            if key == "LUT_3D_SIZE":
                if len(parts) != 2:
                    raise ValueError(f"{where}: LUT_3D_SIZE needs one integer.")
                size = int(parts[1])
                if not 2 <= size <= 128:
                    raise ValueError(f"{where}: LUT_3D_SIZE must be between 2 and 128.")
            else:
                if len(parts) != 4:
                    raise ValueError(f"{where}: {key} needs three numbers.")
                domain = tuple(float(v) for v in parts[1:])
                expected = 0.0 if key == "DOMAIN_MIN" else 1.0
                if any(not math.isfinite(v) or abs(v - expected) > 1e-9 for v in domain):
                    raise ValueError(f"{where}: non-default domains are not supported; use DOMAIN_MIN 0 0 0 and DOMAIN_MAX 1 1 1. No remapping was performed.")
            continue
        if key.startswith("LUT_1D"):
            raise ValueError(f"{where}: 1D or combined 1D/3D LUTs are not supported.")
        if size is None:
            raise ValueError(f"{where}: missing LUT_3D_SIZE before RGB data.")
        if len(parts) != 3:
            raise ValueError(f"{where}: expected exactly three RGB numbers.")
        try:
            rgb = tuple(float(v) for v in parts)
        except ValueError as exc:
            raise ValueError(f"{where}: invalid RGB data or unsupported header.") from exc
        if any(not math.isfinite(v) or not 0.0 <= v <= 1.0 for v in rgb):
            raise ValueError(f"{where}: RGB outputs must be finite and within 0..1; no clipping was performed.")
        values.append(rgb)
        if len(values) > size ** 3:
            raise ValueError(f"{where}: too many RGB rows for size {size}.")
    if size is None:
        raise ValueError("Missing LUT_3D_SIZE.")
    if len(values) != size ** 3:
        raise ValueError(f"Expected {size ** 3} entries for size {size}, found {len(values)}.")
    return size, values, []
