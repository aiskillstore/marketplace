#!/usr/bin/env python3
"""Generate creative .cube 3D LUT files."""

from __future__ import annotations

import argparse
import colorsys
import math
from pathlib import Path


LOOKS = {
    "neutral": {
        "contrast": 1.0,
        "saturation": 1.0,
        "warmth": 0.0,
        "exposure": 0.0,
        "lift": 0.0,
        "curve": 0.0,
        "shadow_tint": (0.0, 0.0, 0.0),
        "mid_tint": (0.0, 0.0, 0.0),
        "highlight_tint": (0.0, 0.0, 0.0),
        "bleach": 0.0,
    },
    "cinematic-teal-orange": {
        "contrast": 1.12,
        "saturation": 0.92,
        "warmth": 0.02,
        "exposure": 0.0,
        "lift": -0.005,
        "curve": 0.22,
        "shadow_tint": (-0.020, 0.045, 0.070),
        "mid_tint": (0.004, -0.004, -0.006),
        "highlight_tint": (0.070, 0.032, -0.040),
        "bleach": 0.0,
    },
    "soft-portrait": {
        "contrast": 0.96,
        "saturation": 0.90,
        "warmth": 0.07,
        "exposure": 0.015,
        "lift": 0.018,
        "curve": -0.08,
        "shadow_tint": (0.006, 0.000, 0.010),
        "mid_tint": (0.016, 0.006, -0.004),
        "highlight_tint": (0.040, 0.020, -0.012),
        "bleach": 0.0,
    },
    "warm-film": {
        "contrast": 1.05,
        "saturation": 0.94,
        "warmth": 0.10,
        "exposure": 0.0,
        "lift": 0.012,
        "curve": 0.12,
        "shadow_tint": (-0.006, 0.006, 0.020),
        "mid_tint": (0.010, 0.004, -0.004),
        "highlight_tint": (0.060, 0.034, -0.022),
        "bleach": 0.0,
    },
    "cool-commercial": {
        "contrast": 1.08,
        "saturation": 0.88,
        "warmth": -0.07,
        "exposure": 0.005,
        "lift": 0.0,
        "curve": 0.10,
        "shadow_tint": (-0.004, 0.014, 0.036),
        "mid_tint": (-0.004, 0.004, 0.008),
        "highlight_tint": (-0.010, 0.014, 0.026),
        "bleach": 0.0,
    },
    "moody-green": {
        "contrast": 1.16,
        "saturation": 0.82,
        "warmth": -0.02,
        "exposure": -0.015,
        "lift": -0.018,
        "curve": 0.24,
        "shadow_tint": (-0.026, 0.048, 0.030),
        "mid_tint": (-0.012, 0.018, -0.004),
        "highlight_tint": (0.018, 0.012, -0.010),
        "bleach": 0.0,
    },
    "bleach-bypass": {
        "contrast": 1.25,
        "saturation": 0.58,
        "warmth": -0.015,
        "exposure": 0.0,
        "lift": -0.010,
        "curve": 0.30,
        "shadow_tint": (-0.012, 0.008, 0.020),
        "mid_tint": (0.0, 0.0, 0.0),
        "highlight_tint": (0.018, 0.014, 0.004),
        "bleach": 0.20,
    },
    "kodak-print-ish": {
        "contrast": 1.10,
        "saturation": 0.98,
        "warmth": 0.055,
        "exposure": 0.0,
        "lift": -0.006,
        "curve": 0.18,
        "shadow_tint": (0.000, -0.002, 0.018),
        "mid_tint": (0.012, 0.004, -0.006),
        "highlight_tint": (0.056, 0.030, -0.018),
        "bleach": 0.0,
    },
    "fuji-soft-ish": {
        "contrast": 0.99,
        "saturation": 0.93,
        "warmth": 0.025,
        "exposure": 0.005,
        "lift": 0.010,
        "curve": 0.04,
        "shadow_tint": (-0.004, 0.018, 0.014),
        "mid_tint": (-0.004, 0.008, 0.000),
        "highlight_tint": (0.026, 0.020, -0.006),
        "bleach": 0.0,
    },
    "custom": {
        "contrast": 1.0,
        "saturation": 1.0,
        "warmth": 0.0,
        "exposure": 0.0,
        "lift": 0.0,
        "curve": 0.0,
        "shadow_tint": (0.0, 0.0, 0.0),
        "mid_tint": (0.0, 0.0, 0.0),
        "highlight_tint": (0.0, 0.0, 0.0),
        "bleach": 0.0,
    },
}

LUMIX_PHOTO_STYLE_TAGS = {
    "STD", "VIVD", "NAT", "LCLASN", "FLAT", "LAND", "PORT", "MONO",
    "LMONO", "LMONOD", "LMONOS", "LEICAMONO", "CNED2", "CNEV2", "709L",
    "2100HLG", "2100HLGF", "VLOG",
}


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def mix(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


def mix_rgb(a: tuple[float, float, float], b: tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    return tuple(mix(a[i], b[i], amount) for i in range(3))


def luminance(rgb: tuple[float, float, float]) -> float:
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def adjust_saturation(rgb: tuple[float, float, float], saturation: float) -> tuple[float, float, float]:
    lum = luminance(rgb)
    return tuple(lum + (channel - lum) * saturation for channel in rgb)


def contrast(rgb: tuple[float, float, float], amount: float, pivot: float = 0.5) -> tuple[float, float, float]:
    return tuple((channel - pivot) * amount + pivot for channel in rgb)


def tone_curve_channel(value: float, curve: float) -> float:
    value = clamp(value)
    smooth = value * value * (3.0 - 2.0 * value)
    if curve >= 0:
        return mix(value, smooth, clamp(curve, 0.0, 1.0))
    gentle = 0.5 - math.sin((0.5 - value) * math.pi) / 2.0
    return mix(value, gentle, clamp(-curve, 0.0, 1.0))


def tone_curve(rgb: tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    return tuple(tone_curve_channel(channel, amount) for channel in rgb)


def add_tint(rgb: tuple[float, float, float], tint: tuple[float, float, float], weight: float) -> tuple[float, float, float]:
    return tuple(rgb[i] + tint[i] * weight for i in range(3))


def skin_weight(rgb: tuple[float, float, float]) -> float:
    r, g, b = (clamp(c) for c in rgb)
    hue, saturation, value = colorsys.rgb_to_hsv(r, g, b)
    lum = luminance((r, g, b))
    hue_distance = min(abs(hue - 0.075), abs(hue - 1.075))
    hue_score = max(0.0, 1.0 - hue_distance / 0.075)
    sat_score = max(0.0, min((saturation - 0.12) / 0.20, (0.78 - saturation) / 0.28, 1.0))
    lum_score = max(0.0, min((lum - 0.20) / 0.28, (0.92 - lum) / 0.22, 1.0))
    value_score = max(0.0, min((value - 0.18) / 0.25, 1.0))
    return clamp(hue_score * sat_score * lum_score * value_score)


def apply_transform(
    rgb: tuple[float, float, float],
    params: dict[str, object],
    strength: float,
    protect_skin: bool,
) -> tuple[float, float, float]:
    original = rgb
    tint_keys = {"shadow_tint", "mid_tint", "highlight_tint"}
    is_identity = all((tuple(params[key]) == tuple(value)) if key in tint_keys else params[key] == value
                      for key, value in LOOKS["neutral"].items())
    if is_identity or strength == 0:
        return tuple(clamp(channel) for channel in original)
    exposure = float(params["exposure"])
    out = tuple(channel * (2.0 ** exposure) + float(params["lift"]) for channel in rgb)
    out = contrast(out, float(params["contrast"]))

    lum = luminance(tuple(clamp(channel) for channel in out))
    shadow_weight = clamp((0.58 - lum) / 0.58) ** 1.35
    highlight_weight = clamp((lum - 0.42) / 0.58) ** 1.25
    mid_weight = clamp(1.0 - abs(lum - 0.50) / 0.50) ** 1.60

    out = add_tint(out, params["shadow_tint"], shadow_weight)
    out = add_tint(out, params["mid_tint"], mid_weight)
    out = add_tint(out, params["highlight_tint"], highlight_weight)

    warmth = float(params["warmth"])
    out = (out[0] + 0.12 * warmth, out[1] + 0.025 * warmth, out[2] - 0.11 * warmth)
    out = tone_curve(out, float(params["curve"]))
    out = adjust_saturation(out, float(params["saturation"]))

    bleach = float(params["bleach"])
    if bleach > 0:
        lum_after = luminance(out)
        silver = (lum_after, lum_after, lum_after)
        out = mix_rgb(out, silver, bleach)
        out = contrast(out, 1.0 + bleach * 0.45)

    if protect_skin:
        weight = skin_weight(original)
        if weight > 0:
            out = mix_rgb(out, adjust_saturation(out, 0.88), 0.10 * weight)
            out = mix_rgb(out, original, 0.22 * weight)

    mixed = mix_rgb(original, out, clamp(strength))
    return tuple(clamp(channel) for channel in mixed)


def build_params(args: argparse.Namespace) -> dict[str, object]:
    params = dict(LOOKS[args.look])
    for key in ("contrast", "saturation", "warmth", "exposure", "lift", "curve", "bleach", "shadow_tint", "mid_tint", "highlight_tint"):
        value = getattr(args, key, None)
        if value is not None:
            params[key] = value
    return params


def write_cube(
    path: Path,
    size: int,
    title: str,
    look: str,
    strength: float,
    params: dict[str, object],
    protect_skin: bool,
    lumix_photo_style: str | None = None,
) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing LUT: {path}")
    if not 2 <= size <= 128 or not math.isfinite(strength) or not 0 <= strength <= 1:
        raise ValueError("Invalid LUT size or strength.")
    validate_params(params)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_title = title.replace('"', "'").replace("\r", " ").replace("\n", " ")
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f'TITLE "{safe_title}"\n')
        if lumix_photo_style:
            handle.write(f"#LUMIXPHOTOSTYLE {lumix_photo_style}\n")
        handle.write("# Generated by the generate-lut Codex skill.\n")
        handle.write(f"# Look: {look}\n")
        handle.write(f"# Strength: {strength:.4f} (already baked; preview at 1.0)\n")
        handle.write(f"# Skin protection: {'on' if protect_skin else 'off'}\n")
        handle.write("DOMAIN_MIN 0.0 0.0 0.0\n")
        handle.write("DOMAIN_MAX 1.0 1.0 1.0\n")
        handle.write(f"LUT_3D_SIZE {size}\n")
        handle.write("\n")
        scale = size - 1
        for b in range(size):
            for g in range(size):
                for r in range(size):
                    rgb = (r / scale, g / scale, b / scale)
                    out = apply_transform(rgb, params, strength, protect_skin)
                    handle.write(f"{out[0]:.7f} {out[1]:.7f} {out[2]:.7f}\n")


def validate_params(params: dict) -> None:
    limits = {"contrast": (0, 3), "saturation": (0, 3), "warmth": (-1, 1),
              "exposure": (-8, 8), "lift": (-0.5, 0.5), "curve": (-1, 1), "bleach": (0, 1)}
    for key, (low, high) in limits.items():
        value = float(params[key])
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"{key} must be finite and between {low} and {high}.")
    for key in ("shadow_tint", "mid_tint", "highlight_tint"):
        if len(params[key]) != 3 or any(not math.isfinite(float(v)) or abs(float(v)) > 0.5 for v in params[key]):
            raise ValueError(f"{key} requires three finite RGB offsets in -0.5..0.5.")


def add_look_controls(parser: argparse.ArgumentParser) -> None:
    for key in ("contrast", "saturation", "warmth", "exposure", "lift", "curve", "bleach"):
        parser.add_argument("--" + key, type=float, default=None, help=f"Override {key}; saved in the reproducible recipe.")
    for key in ("shadow-tint", "mid-tint", "highlight-tint"):
        parser.add_argument("--" + key, nargs=3, type=float, metavar=("R", "G", "B"), help="RGB offsets from -0.5 to 0.5.")
    parser.add_argument("--no-protect-skin", action="store_true", help="Disable conservative hue-based skin protection (not face detection).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a creative .cube 3D LUT.")
    parser.add_argument("--output", required=True, help="Path to write the .cube file.")
    parser.add_argument("--look", default="cinematic-teal-orange", choices=sorted(LOOKS), help="Creative preset.")
    parser.add_argument("--size", type=int, default=33, help="3D LUT size, commonly 17, 33, or 65.")
    parser.add_argument("--strength", type=float, default=0.65, help="Blend from identity to the full look, 0..1.")
    parser.add_argument("--title", default=None, help="Optional LUT title.")
    parser.add_argument(
        "--lumix-photo-style",
        choices=sorted(LUMIX_PHOTO_STYLE_TAGS),
        help="Add Panasonic #LUMIXPHOTOSTYLE metadata for the LUT's base Photo Style.",
    )
    add_look_controls(parser)
    args = parser.parse_args()

    if args.size < 2 or args.size > 128:
        parser.error("--size must be between 2 and 128")
    if not math.isfinite(args.strength) or args.strength < 0 or args.strength > 1:
        parser.error("--strength must be between 0 and 1")
    try:
        validate_params(build_params(args))
    except ValueError as exc:
        parser.error(str(exc))
    return args


def main() -> None:
    args = parse_args()
    params = build_params(args)
    title = args.title or f"{args.look} {args.strength:.2f}"
    write_cube(
        Path(args.output), args.size, title, args.look, args.strength, params,
        not args.no_protect_skin, args.lumix_photo_style,
    )
    print(f"Wrote {args.output} ({args.look}, size {args.size}, strength {args.strength:.2f})")


if __name__ == "__main__":
    main()
