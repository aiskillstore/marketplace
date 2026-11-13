#!/usr/bin/env python3
"""Compose an ordered chain of normalized 3D .cube LUTs into one LUT."""

from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path

from validate_lut import parse_cube


def domain_for(path: Path) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    domain_min = (0.0, 0.0, 0.0)
    domain_max = (1.0, 1.0, 1.0)
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            upper = line.upper()
            if upper.startswith("DOMAIN_MIN") or upper.startswith("DOMAIN_MAX"):
                parts = line.split()
                if len(parts) != 4:
                    raise ValueError(f"{path.name}:{line_number}: domain header needs three values.")
                try:
                    values = tuple(float(value) for value in parts[1:])
                except ValueError as exc:
                    raise ValueError(f"{path.name}:{line_number}: invalid domain value.") from exc
                if upper.startswith("DOMAIN_MIN"):
                    domain_min = values
                else:
                    domain_max = values
    return domain_min, domain_max


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_metadata(path: Path, label: str) -> str | None:
    prefix = f"# {label}:"
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw in handle:
            line = raw.strip()
            if line.lower().startswith(prefix.lower()):
                return line[len(prefix):].strip()
    return None


def lumix_photo_style(path: Path) -> str | None:
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw in handle:
            parts = raw.strip().split()
            if len(parts) == 2 and parts[0].upper() == "#LUMIXPHOTOSTYLE":
                return parts[1].upper()
    return None


def load_cube(path: Path) -> tuple[int, list[tuple[float, float, float]]]:
    if path.suffix.lower() != ".cube":
        raise ValueError(f"{path.name}: only .cube inputs are supported.")
    size, values, _ = parse_cube(path)
    if size > 128:
        raise ValueError(f"{path.name}: LUT_3D_SIZE above 128 is not supported.")
    domain_min, domain_max = domain_for(path)
    if any(not math.isclose(v, 0.0, abs_tol=1e-9) for v in domain_min) or any(
        not math.isclose(v, 1.0, abs_tol=1e-9) for v in domain_max
    ):
        raise ValueError(f"{path.name}: chain baking currently requires DOMAIN_MIN 0 and DOMAIN_MAX 1.")
    for row_index, rgb in enumerate(values, 1):
        if any(not math.isfinite(channel) for channel in rgb):
            raise ValueError(f"{path.name}: non-finite output at LUT row {row_index}.")
        if any(channel < 0.0 or channel > 1.0 for channel in rgb):
            raise ValueError(f"{path.name}: output outside 0..1 at LUT row {row_index}; clamp or bake this transform separately.")
    return size, values


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def lerp(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


def lookup(size: int, values: list[tuple[float, float, float]], rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    scale = size - 1
    rf, gf, bf = (clamp(channel) * scale for channel in rgb)
    r0, g0, b0 = int(math.floor(rf)), int(math.floor(gf)), int(math.floor(bf))
    r1, g1, b1 = min(r0 + 1, scale), min(g0 + 1, scale), min(b0 + 1, scale)
    tr, tg, tb = rf - r0, gf - g0, bf - b0

    def at(r: int, g: int, b: int) -> tuple[float, float, float]:
        return values[((b * size) + g) * size + r]

    c000, c100 = at(r0, g0, b0), at(r1, g0, b0)
    c010, c110 = at(r0, g1, b0), at(r1, g1, b0)
    c001, c101 = at(r0, g0, b1), at(r1, g0, b1)
    c011, c111 = at(r0, g1, b1), at(r1, g1, b1)
    output = []
    for channel in range(3):
        c00 = lerp(c000[channel], c100[channel], tr)
        c10 = lerp(c010[channel], c110[channel], tr)
        c01 = lerp(c001[channel], c101[channel], tr)
        c11 = lerp(c011[channel], c111[channel], tr)
        output.append(lerp(lerp(c00, c10, tg), lerp(c01, c11, tg), tb))
    return tuple(output)


def bake_chain(
    lut_paths: list[Path], output_path: Path, size: int, title: str,
    photo_style_override: str | None = None,
) -> None:
    if len(lut_paths) < 2:
        raise ValueError("Provide at least two LUTs in the order they should be applied.")
    resolved_output = output_path.resolve()
    if any(resolved_output == path.resolve() for path in lut_paths):
        raise ValueError("Output path must not overwrite an input LUT.")

    if output_path.suffix.lower() != ".cube":
        raise ValueError("Output path must end with .cube.")
    cubes = [(path, *load_cube(path)) for path in lut_paths]
    declared_styles = {style for path in lut_paths if (style := lumix_photo_style(path))}
    if len(declared_styles) > 1 and photo_style_override is None:
        raise ValueError(
            "Input LUTs declare different LUMIX Photo Styles; supply --lumix-photo-style to set the baked LUT's base style."
        )
    output_photo_style = photo_style_override or next(iter(declared_styles), None)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    safe_title = title.replace('"', "'")
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f'TITLE "{safe_title}"\n')
        if output_photo_style:
            handle.write(f"#LUMIXPHOTOSTYLE {output_photo_style}\n")
        handle.write("# Baked by the generate-lut Skill; stages follow the supplied order.\n")
        first_source = next((source_metadata(path, "Source") for path in lut_paths if source_metadata(path, "Source")), None)
        last_target = next((target for path in reversed(lut_paths) if (target := source_metadata(path, "Target"))), None)
        if first_source:
            handle.write(f"# Source: {first_source}\n")
        if last_target:
            handle.write(f"# Target: {last_target}\n")
        for index, path in enumerate(lut_paths, 1):
            handle.write(f"# Stage {index}: {path.name} | SHA256 {sha256_file(path)}\n")
        handle.write("DOMAIN_MIN 0.0 0.0 0.0\n")
        handle.write("DOMAIN_MAX 1.0 1.0 1.0\n")
        handle.write(f"LUT_3D_SIZE {size}\n\n")
        scale = size - 1
        for b in range(size):
            for g in range(size):
                for r in range(size):
                    rgb = (r / scale, g / scale, b / scale)
                    for _, lut_size, lut_values in cubes:
                        rgb = lookup(lut_size, lut_values, rgb)
                    handle.write(f"{rgb[0]:.7f} {rgb[1]:.7f} {rgb[2]:.7f}\n")
    print(f"Wrote {output_path} ({size}^3; {len(cubes)} ordered stages).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bake ordered normalized 3D .cube transforms into one .cube. Supply --lut in application order."
    )
    parser.add_argument("--lut", action="append", required=True, help="Input .cube LUT in application order; repeat at least twice.")
    parser.add_argument("--size", type=int, default=33, help="Output 3D LUT size (default: 33).")
    parser.add_argument("--title", default="Baked LUT Chain", help="Output LUT title.")
    parser.add_argument(
        "--lumix-photo-style",
        choices=sorted({"STD", "VIVD", "NAT", "LCLASN", "FLAT", "LAND", "PORT", "MONO", "LMONO", "LMONOD", "LMONOS", "LEICAMONO", "CNED2", "CNEV2", "709L", "2100HLG", "2100HLGF", "VLOG"}),
        help="Explicit Panasonic base Photo Style tag for the baked LUT; overrides input tags.",
    )
    parser.add_argument("--output", required=True, help="Output .cube path.")
    args = parser.parse_args()
    if len(args.lut) < 2:
        parser.error("provide at least two --lut inputs in application order")
    if args.size < 2 or args.size > 128:
        parser.error("--size must be between 2 and 128")
    return args


def main() -> None:
    args = parse_args()
    paths = [Path(value) for value in args.lut]
    try:
        bake_chain(paths, Path(args.output), args.size, args.title, args.lumix_photo_style)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Could not bake LUT chain: {exc}") from exc


if __name__ == "__main__":
    main()
