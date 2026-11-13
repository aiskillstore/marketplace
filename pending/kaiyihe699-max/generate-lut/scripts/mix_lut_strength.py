#!/usr/bin/env python3
"""Blend a normalized 3D .cube LUT toward identity and save a derivative LUT."""

from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path

from validate_lut import parse_cube


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_domain(path: Path) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    domain_min = (0.0, 0.0, 0.0)
    domain_max = (1.0, 1.0, 1.0)
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            upper = line.upper()
            if upper.startswith("DOMAIN_MIN") or upper.startswith("DOMAIN_MAX"):
                parts = line.split()
                if len(parts) != 4:
                    raise ValueError(f"Line {line_number}: domain header needs three values.")
                try:
                    values = tuple(float(value) for value in parts[1:])
                except ValueError as exc:
                    raise ValueError(f"Line {line_number}: invalid domain value.") from exc
                if not all(math.isfinite(value) for value in values):
                    raise ValueError(f"Line {line_number}: domain has non-finite values.")
                if upper.startswith("DOMAIN_MIN"):
                    domain_min = values
                else:
                    domain_max = values
    return domain_min, domain_max


def is_data_row(line: str) -> bool:
    stripped = line.split("#", 1)[0].strip()
    if not stripped or stripped.startswith("#"):
        return False
    upper = stripped.upper()
    if upper.startswith(("TITLE", "DOMAIN_MIN", "DOMAIN_MAX", "LUT_3D_SIZE")):
        return False
    parts = stripped.split()
    if len(parts) < 3:
        return False
    try:
        for value in parts:
            float(value)
    except ValueError:
        return False
    return True


def mix_lut(input_path: Path, output_path: Path, strength: float, title: str | None = None) -> None:
    if input_path.suffix.lower() != ".cube" or output_path.suffix.lower() != ".cube":
        raise ValueError("Input and output paths must use the .cube extension.")
    if not math.isfinite(strength) or not 0.0 <= strength <= 1.0:
        raise ValueError("Strength must be between 0 and 1.")
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Output path must not overwrite the source LUT.")
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output_path}")

    size, values, _ = parse_cube(input_path)
    domain_min, domain_max = read_domain(input_path)
    if any(not math.isclose(value, 0.0, abs_tol=1e-9) for value in domain_min) or any(
        not math.isclose(value, 1.0, abs_tol=1e-9) for value in domain_max
    ):
        raise ValueError("Strength blending currently requires DOMAIN_MIN 0 and DOMAIN_MAX 1.")
    for row_index, rgb in enumerate(values, 1):
        if any(not math.isfinite(channel) for channel in rgb):
            raise ValueError(f"The LUT contains non-finite values at row {row_index}.")
        if any(channel < 0.0 or channel > 1.0 for channel in rgb):
            raise ValueError(f"The LUT has output values outside 0..1 at row {row_index}; it was not clipped.")

    lines = input_path.read_text(encoding="utf-8-sig").splitlines()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    new_title = title or f"{input_path.stem} {strength:.0%}"
    safe_title = new_title.replace('"', "'").replace("\r", " ").replace("\n", " ")
    source_hash = sha256_file(input_path)
    output_lines: list[str] = []
    row_index = 0
    title_written = False
    inserted_metadata = False
    scale = size - 1

    for raw in lines:
        line = raw.strip()
        upper = line.upper()
        if upper.startswith("TITLE"):
            output_lines.append(f'TITLE "{safe_title}"')
            title_written = True
            output_lines.append(f"# Strength mix: {strength:.6f} (0=identity, 1=source LUT)")
            output_lines.append(f"# Source LUT SHA256: {source_hash}")
            inserted_metadata = True
            continue
        if is_data_row(raw):
            parts = line.split("#", 1)[0].split()
            if len(parts) != 3:
                raise ValueError(f"Only RGB triplet data rows are supported (row {row_index + 1}).")
            r = row_index % size
            g = (row_index // size) % size
            b = row_index // (size * size)
            identity = (r / scale, g / scale, b / scale)
            source_rgb = values[row_index]
            if strength >= 1.0:
                mixed = source_rgb
            elif strength <= 0.0:
                mixed = identity
            else:
                mixed = tuple(identity[channel] + (source_rgb[channel] - identity[channel]) * strength for channel in range(3))
            output_lines.append(" ".join(format(channel, ".17g") for channel in mixed))
            row_index += 1
            continue
        output_lines.append(raw)

    if row_index != size ** 3:
        raise ValueError(f"Found {row_index} RGB data rows while expecting {size ** 3}.")
    if not title_written:
        output_lines.insert(0, f'TITLE "{safe_title}"')
    if not inserted_metadata:
        insert_at = 1 if title_written else 0
        output_lines[insert_at:insert_at] = [
            f"# Strength mix: {strength:.6f} (0=identity, 1=source LUT)",
            f"# Source LUT SHA256: {source_hash}",
        ]
    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {output_path} ({size}^3, strength {strength:.0%}).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adjust any normalized 3D .cube LUT by blending it toward identity.")
    parser.add_argument("--input", required=True, help="Source .cube LUT.")
    parser.add_argument("--output", required=True, help="New .cube output path; source is preserved.")
    parser.add_argument("--strength", type=float, required=True, help="LUT amount from 0 (identity) to 1 (full source LUT).")
    parser.add_argument("--title", help="Optional output TITLE value.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        mix_lut(Path(args.input), Path(args.output), args.strength, args.title)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Could not mix LUT strength: {exc}") from exc


if __name__ == "__main__":
    main()
