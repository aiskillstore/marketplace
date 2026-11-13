#!/usr/bin/env python3
"""Small color science toolkit for LUT generation.

The built-in transforms cover common RGB primaries, chromatic adaptation,
and transfer functions. Use OCIO for facility-specific pipelines.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


Vec3 = tuple[float, float, float]
Mat3 = tuple[Vec3, Vec3, Vec3]


@dataclass(frozen=True)
class RGBColorSpace:
    name: str
    red: tuple[float, float]
    green: tuple[float, float]
    blue: tuple[float, float]
    white: tuple[float, float]


D65 = (0.3127, 0.3290)
D60_ACES = (0.32168, 0.33767)


RGB_COLORSPACES: dict[str, RGBColorSpace] = {
    "srgb": RGBColorSpace("sRGB", (0.6400, 0.3300), (0.3000, 0.6000), (0.1500, 0.0600), D65),
    "rec709": RGBColorSpace("Rec.709", (0.6400, 0.3300), (0.3000, 0.6000), (0.1500, 0.0600), D65),
    "display-p3": RGBColorSpace("Display P3", (0.6800, 0.3200), (0.2650, 0.6900), (0.1500, 0.0600), D65),
    "p3-d65": RGBColorSpace("P3-D65", (0.6800, 0.3200), (0.2650, 0.6900), (0.1500, 0.0600), D65),
    "rec2020": RGBColorSpace("Rec.2020", (0.7080, 0.2920), (0.1700, 0.7970), (0.1310, 0.0460), D65),
    "bt2020": RGBColorSpace("BT.2020", (0.7080, 0.2920), (0.1700, 0.7970), (0.1310, 0.0460), D65),
    "acescg": RGBColorSpace("ACEScg AP1", (0.7130, 0.2930), (0.1650, 0.8300), (0.1280, 0.0440), D60_ACES),
    "aces-ap1": RGBColorSpace("ACES AP1", (0.7130, 0.2930), (0.1650, 0.8300), (0.1280, 0.0440), D60_ACES),
    "aces2065-1": RGBColorSpace("ACES2065-1 AP0", (0.7347, 0.2653), (0.0000, 1.0000), (0.0001, -0.0770), D60_ACES),
    "aces-ap0": RGBColorSpace("ACES AP0", (0.7347, 0.2653), (0.0000, 1.0000), (0.0001, -0.0770), D60_ACES),
    "panasonic-v-gamut": RGBColorSpace("Panasonic V-Gamut", (0.7300, 0.2800), (0.1650, 0.8400), (0.1000, -0.0300), D65),
    "v-gamut": RGBColorSpace("Panasonic V-Gamut", (0.7300, 0.2800), (0.1650, 0.8400), (0.1000, -0.0300), D65),
}


TRANSFER_NAMES = (
    "linear",
    "srgb",
    "rec709",
    "gamma2.2",
    "gamma2.4",
    "pq",
    "hlg",
    "panasonic-vlog",
    "v-log",
)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def mat_vec_mul(m: Mat3, v: Vec3) -> Vec3:
    return (dot(m[0], v), dot(m[1], v), dot(m[2], v))


def mat_mul(a: Mat3, b: Mat3) -> Mat3:
    bt = tuple(zip(*b))
    return tuple(tuple(dot(row, col) for col in bt) for row in a)  # type: ignore[return-value]


def mat_inv(m: Mat3) -> Mat3:
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-12:
        raise ValueError("Matrix is singular.")
    inv_det = 1.0 / det
    return (
        ((e * i - f * h) * inv_det, (c * h - b * i) * inv_det, (b * f - c * e) * inv_det),
        ((f * g - d * i) * inv_det, (a * i - c * g) * inv_det, (c * d - a * f) * inv_det),
        ((d * h - e * g) * inv_det, (b * g - a * h) * inv_det, (a * e - b * d) * inv_det),
    )


def xy_to_xyz(xy: tuple[float, float]) -> Vec3:
    x, y = xy
    if y == 0:
        raise ValueError("Invalid chromaticity with y=0.")
    return (x / y, 1.0, (1.0 - x - y) / y)


def rgb_to_xyz_matrix(space: RGBColorSpace) -> Mat3:
    r = xy_to_xyz(space.red)
    g = xy_to_xyz(space.green)
    b = xy_to_xyz(space.blue)
    w = xy_to_xyz(space.white)
    primaries: Mat3 = (
        (r[0], g[0], b[0]),
        (r[1], g[1], b[1]),
        (r[2], g[2], b[2]),
    )
    scale = mat_vec_mul(mat_inv(primaries), w)
    return (
        (primaries[0][0] * scale[0], primaries[0][1] * scale[1], primaries[0][2] * scale[2]),
        (primaries[1][0] * scale[0], primaries[1][1] * scale[1], primaries[1][2] * scale[2]),
        (primaries[2][0] * scale[0], primaries[2][1] * scale[1], primaries[2][2] * scale[2]),
    )


BRADFORD: Mat3 = (
    (0.8951, 0.2664, -0.1614),
    (-0.7502, 1.7135, 0.0367),
    (0.0389, -0.0685, 1.0296),
)
BRADFORD_INV = mat_inv(BRADFORD)


def chromatic_adaptation_matrix(source_white: tuple[float, float], target_white: tuple[float, float]) -> Mat3:
    if abs(source_white[0] - target_white[0]) < 1e-8 and abs(source_white[1] - target_white[1]) < 1e-8:
        return ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    src_cone = mat_vec_mul(BRADFORD, xy_to_xyz(source_white))
    dst_cone = mat_vec_mul(BRADFORD, xy_to_xyz(target_white))
    scale: Mat3 = (
        (dst_cone[0] / src_cone[0], 0.0, 0.0),
        (0.0, dst_cone[1] / src_cone[1], 0.0),
        (0.0, 0.0, dst_cone[2] / src_cone[2]),
    )
    return mat_mul(mat_mul(BRADFORD_INV, scale), BRADFORD)


def conversion_matrix(source_key: str, target_key: str) -> Mat3:
    source = RGB_COLORSPACES[source_key]
    target = RGB_COLORSPACES[target_key]
    src_to_xyz = rgb_to_xyz_matrix(source)
    adaptation = chromatic_adaptation_matrix(source.white, target.white)
    xyz_to_target = mat_inv(rgb_to_xyz_matrix(target))
    return mat_mul(mat_mul(xyz_to_target, adaptation), src_to_xyz)


def srgb_decode(v: float) -> float:
    v = clamp(v)
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def srgb_encode(lin: float) -> float:
    lin = max(0.0, lin)
    return 12.92 * lin if lin <= 0.0031308 else 1.055 * (lin ** (1.0 / 2.4)) - 0.055


def rec709_decode(v: float) -> float:
    v = clamp(v)
    return v / 4.5 if v < 0.081 else ((v + 0.099) / 1.099) ** (1.0 / 0.45)


def rec709_encode(lin: float) -> float:
    lin = max(0.0, lin)
    return 4.5 * lin if lin < 0.018 else 1.099 * (lin ** 0.45) - 0.099


def pq_eotf(v: float) -> float:
    v = clamp(v)
    m1 = 2610.0 / 16384.0
    m2 = 2523.0 / 32.0
    c1 = 3424.0 / 4096.0
    c2 = 2413.0 / 128.0
    c3 = 2392.0 / 128.0
    n = v ** (1.0 / m2)
    return 10000.0 * (max(n - c1, 0.0) / (c2 - c3 * n)) ** (1.0 / m1)


def pq_inverse_eotf(nits: float) -> float:
    nits = max(0.0, nits)
    m1 = 2610.0 / 16384.0
    m2 = 2523.0 / 32.0
    c1 = 3424.0 / 4096.0
    c2 = 2413.0 / 128.0
    c3 = 2392.0 / 128.0
    y = (nits / 10000.0) ** m1
    return ((c1 + c2 * y) / (1.0 + c3 * y)) ** m2


def hlg_decode(v: float) -> float:
    v = clamp(v)
    a = 0.17883277
    b = 1.0 - 4.0 * a
    c = 0.5 - a * math.log(4.0 * a)
    return (v * v) / 3.0 if v <= 0.5 else (math.exp((v - c) / a) + b) / 12.0


def hlg_encode(lin: float) -> float:
    lin = max(0.0, lin)
    a = 0.17883277
    b = 1.0 - 4.0 * a
    c = 0.5 - a * math.log(4.0 * a)
    return math.sqrt(3.0 * lin) if lin <= (1.0 / 12.0) else a * math.log(12.0 * lin - b) + c


def panasonic_vlog_decode(v: float) -> float:
    v = clamp(v)
    cut = 0.181
    b = 0.00873
    c = 0.241514
    d = 0.598206
    return (v - 0.125) / 5.6 if v < cut else (10.0 ** ((v - d) / c)) - b


def panasonic_vlog_encode(lin: float) -> float:
    lin = max(0.0, lin)
    cut = 0.01
    b = 0.00873
    c = 0.241514
    d = 0.598206
    return 5.6 * lin + 0.125 if lin < cut else c * math.log10(lin + b) + d


def decode_transfer(value: float, transfer: str, peak_nits: float = 1000.0) -> float:
    key = transfer.lower()
    if key == "linear":
        return value
    if key == "srgb":
        return srgb_decode(value)
    if key == "rec709":
        return rec709_decode(value)
    if key == "gamma2.2":
        return clamp(value) ** 2.2
    if key == "gamma2.4":
        return clamp(value) ** 2.4
    if key == "pq":
        return pq_eotf(value) / peak_nits
    if key == "hlg":
        return hlg_decode(value)
    if key in ("panasonic-vlog", "v-log"):
        return panasonic_vlog_decode(value)
    raise KeyError(f"Unknown transfer: {transfer}")


def encode_transfer(value: float, transfer: str, peak_nits: float = 1000.0) -> float:
    key = transfer.lower()
    if key == "linear":
        return value
    if key == "srgb":
        return srgb_encode(value)
    if key == "rec709":
        return rec709_encode(value)
    if key == "gamma2.2":
        return max(0.0, value) ** (1.0 / 2.2)
    if key == "gamma2.4":
        return max(0.0, value) ** (1.0 / 2.4)
    if key == "pq":
        return pq_inverse_eotf(max(0.0, value) * peak_nits)
    if key == "hlg":
        return hlg_encode(value)
    if key in ("panasonic-vlog", "v-log"):
        return panasonic_vlog_encode(value)
    raise KeyError(f"Unknown transfer: {transfer}")


def luminance(rgb: Vec3) -> float:
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def tone_map(rgb: Vec3, mode: str, exposure: float = 0.0) -> Vec3:
    scaled = tuple(channel * (2.0 ** exposure) for channel in rgb)
    if mode == "none":
        return scaled
    if mode == "reinhard":
        return tuple(channel / (1.0 + max(0.0, channel)) for channel in scaled)
    if mode == "luminance-reinhard":
        y = max(0.0, luminance(scaled))
        mapped_y = y / (1.0 + y)
        ratio = mapped_y / y if y > 1e-8 else 1.0
        return tuple(channel * ratio for channel in scaled)
    raise KeyError(f"Unknown tone map: {mode}")


def convert_rgb(
    rgb_code: Vec3,
    source_space: str,
    source_transfer: str,
    target_space: str,
    target_transfer: str,
    source_peak_nits: float = 1000.0,
    target_peak_nits: float = 1000.0,
    exposure: float = 0.0,
    tone_map_mode: str = "none",
    clamp_output: bool = True,
) -> Vec3:
    matrix = conversion_matrix(source_space, target_space)
    source_linear = tuple(decode_transfer(channel, source_transfer, source_peak_nits) for channel in rgb_code)
    target_linear = mat_vec_mul(matrix, source_linear)
    target_linear = tone_map(target_linear, tone_map_mode, exposure)
    target_code = tuple(encode_transfer(channel, target_transfer, target_peak_nits) for channel in target_linear)
    if clamp_output:
        return tuple(clamp(channel) for channel in target_code)
    return target_code
