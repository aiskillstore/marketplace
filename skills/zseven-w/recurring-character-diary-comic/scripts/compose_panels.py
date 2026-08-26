#!/usr/bin/env python3
"""Deterministically letter a full page or reconstruct validated comic panels."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import io
import json
import math
import os
import platform
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

import PIL
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, UnidentifiedImageError, features


COMPOSITOR_VERSION = "2.1.0"
MAX_CANVAS_EDGE = 16_384
MAX_CANVAS_PIXELS = 8_000_000
MAX_SOURCE_PIXELS = 40_000_000
MAX_SOURCE_FILE_BYTES = 128 * 1024 * 1024
MAX_TOTAL_SOURCE_BYTES = 512 * 1024 * 1024
OVERLAY_SCALE = 4
MAX_BUBBLE_STROKE_WIDTH = 8
MAX_TAIL_TIP_TRIM = 32
SOFT_TAIL_CURVE_SEGMENTS = 12
MAX_POLYGON_POINTS = 24
MAX_ROTATION_DEGREES = 15.0
MAX_ABS_Z_INDEX = 10_000
PANEL_FILTER_HALO = 2

MANIFEST_KEYS = frozenset(
    {"schema_version", "artifact_stages", "canvas", "lettering", "panels", "bubbles", "output"}
)
ARTIFACT_STAGE_KEYS = frozenset({"panel_inputs", "composition"})
CANVAS_KEYS = frozenset({"size", "background", "paper_matte"})
PAPER_MATTE_KEYS = frozenset({"enabled", "seed", "grain_strength", "tile_size"})
PANEL_KEYS = frozenset(
    {
        "id",
        "reading_order",
        "row",
        "column",
        "source",
        "expected_sha256",
        "expected_size",
        "source_crop",
        "frame",
        "corner_radius",
        "border",
        "protected_action_regions",
        "clip_polygon",
        "rotation_degrees",
        "z_index",
        "allow_overlap_with",
    }
)
BORDER_KEYS = frozenset({"width", "color"})
PROTECTED_REGION_KEYS = frozenset({"id", "bbox"})
BUBBLE_KEYS = frozenset(
    {
        "id",
        "panel",
        "reading_order",
        "speaker",
        "allow_overlap_with",
        "speaker_anchor",
        "shape",
        "bbox",
        "safe_region",
        "corner_radius",
        "tail",
        "fill",
        "stroke",
        "stroke_width",
        "text",
    }
)
BUBBLE_TEXT_KEYS = frozenset(
    {"language", "exact", "lines", "bbox", "font_size", "line_gap", "align"}
)
LETTERING_KEYS = frozenset({"font_candidates", "face_index", "color"})
OUTPUT_KEYS = frozenset({"stage", "unlettered_image", "image", "ledger"})


class ManifestError(ValueError):
    """A user-actionable manifest or asset validation failure."""


@dataclass(frozen=True)
class PanelSpec:
    panel_id: str
    reading_order: int
    row: int
    column: int
    source_label: str
    source_path: Path
    source_bytes: bytes
    source_sha256: str
    source_size: tuple[int, int]
    source_crop: tuple[int, int, int, int]
    frame: tuple[int, int, int, int]
    corner_radius: int
    border_width: int
    border_color: tuple[int, int, int, int]
    clip_polygon: tuple[tuple[int, int], ...] | None
    final_polygon: tuple[tuple[float, float], ...]
    rotation_degrees: float
    z_index: int
    allow_overlap_with: tuple[str, ...]
    protected_action_regions: tuple[tuple[str, tuple[int, int, int, int]], ...]


@dataclass(frozen=True)
class PaperMatteSpec:
    seed: int
    grain_strength: int
    tile_size: int


@dataclass(frozen=True)
class ValidatedManifest:
    manifest_path: Path
    manifest_sha256: str
    schema_version: int
    raw: dict[str, Any]
    canvas_size: tuple[int, int]
    background: tuple[int, int, int, int]
    paper_matte: PaperMatteSpec | None
    panels: tuple[PanelSpec, ...]
    bubbles: tuple[dict[str, Any], ...]
    font_name: str | None
    font_bytes: bytes | None
    font_sha256: str | None
    font_face_index: int
    font_color: tuple[int, int, int, int]
    input_stage: str
    composition_stage: str
    output_stage: str
    unlettered_path: Path | None
    output_path: Path
    ledger_path: Path


def fail(message: str) -> NoReturn:
    raise ManifestError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def glyph_signature(font: ImageFont.FreeTypeFont, character: str) -> tuple[Any, ...]:
    mask = font.getmask(character, mode="L")
    return mask.size, mask.getbbox(), bytes(mask), round(float(font.getlength(character)), 4)


def missing_glyphs(font: ImageFont.FreeTypeFont, text: str) -> list[str]:
    notdef_signatures = {
        glyph_signature(font, "\U0010FFFF"),
        glyph_signature(font, "\u0378"),
    }
    missing: list[str] = []
    for character in dict.fromkeys(text):
        if character.isspace():
            continue
        signature = glyph_signature(font, character)
        if signature[1] is None or signature in notdef_signatures:
            missing.append(character)
    return missing


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def reject_unknown_keys(
    value: dict[str, Any],
    allowed: frozenset[str] | set[str],
    label: str,
) -> None:
    unknown = sorted(set(value) - allowed)
    if not unknown:
        return
    field_label = "field" if len(unknown) == 1 else "fields"
    fail(
        f"{label} contains unknown {field_label}: "
        + ", ".join(repr(field) for field in unknown)
    )


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be an array")
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def require_int(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        fail(f"{label} must be an integer >= {minimum}")
    return value


def require_bounded_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        fail(f"{label} must be an integer from {minimum} through {maximum}")
    return value


def require_number(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(f"{label} must be a number from {minimum:g} through {maximum:g}")
    number = float(value)
    if not math.isfinite(number) or not minimum <= number <= maximum:
        fail(f"{label} must be a finite number from {minimum:g} through {maximum:g}")
    return number


def require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        fail(f"{label} must be true or false")
    return value


def require_pair(value: Any, label: str, minimum: int = 1) -> tuple[int, int]:
    items = require_list(value, label)
    if len(items) != 2:
        fail(f"{label} must contain exactly 2 integers")
    return (
        require_int(items[0], f"{label}[0]", minimum),
        require_int(items[1], f"{label}[1]", minimum),
    )


def require_bbox(value: Any, label: str) -> tuple[int, int, int, int]:
    items = require_list(value, label)
    if len(items) != 4:
        fail(f"{label} must contain exactly 4 integers [left, top, right, bottom]")
    box = tuple(require_int(item, f"{label}[{index}]") for index, item in enumerate(items))
    if box[2] <= box[0] or box[3] <= box[1]:
        fail(f"{label} must have positive width and height, got {list(box)}")
    return box  # type: ignore[return-value]


def require_point(value: Any, label: str) -> tuple[int, int]:
    return require_pair(value, label, minimum=0)


def require_string_list(value: Any, label: str) -> tuple[str, ...]:
    items = require_list(value, label)
    result = tuple(require_string(item, f"{label}[{index}]") for index, item in enumerate(items))
    if len(set(result)) != len(result):
        fail(f"{label} must not contain duplicates")
    return result


def parse_color(value: Any, label: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str) or not value.startswith("#") or len(value) != 7:
        fail(f"{label} must be #RRGGBB; compositor outputs are opaque RGB")
    try:
        channels = tuple(int(value[index : index + 2], 16) for index in range(1, len(value), 2))
    except ValueError:
        fail(f"{label} contains a non-hexadecimal color: {value!r}")
    return channels + (255,)  # type: ignore[return-value]


def require_sha256(value: Any, label: str) -> str:
    candidate = require_string(value, label)
    if len(candidate) != 64 or any(character not in "0123456789abcdef" for character in candidate):
        fail(f"{label} must be exactly 64 lowercase hexadecimal characters")
    return candidate


def require_inline_text(value: Any, label: str) -> str:
    text = require_string(value, label)
    for character in text:
        if unicodedata.category(character) in {"Cc", "Zl", "Zp"}:
            fail(
                f"{label} contains forbidden control or line-break character "
                f"U+{ord(character):04X}; use the lines array for visual line breaks"
            )
    return text


def inside(inner: tuple[int, int, int, int], outer: tuple[int, int, int, int]) -> bool:
    return (
        outer[0] <= inner[0]
        and outer[1] <= inner[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
    )


def point_inside(point: tuple[int, int], box: tuple[int, int, int, int]) -> bool:
    return box[0] <= point[0] < box[2] and box[1] <= point[1] < box[3]


def points_bbox(points: tuple[tuple[int, int], ...]) -> tuple[int, int, int, int]:
    return (
        min(point[0] for point in points),
        min(point[1] for point in points),
        max(point[0] for point in points) + 1,
        max(point[1] for point in points) + 1,
    )


def expand_box(box: tuple[int, int, int, int], margin: int) -> tuple[int, int, int, int]:
    return box[0] - margin, box[1] - margin, box[2] + margin, box[3] + margin


def intersects(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> bool:
    return (
        max(first[0], second[0]) < min(first[2], second[2])
        and max(first[1], second[1]) < min(first[3], second[3])
    )


def polygon_area2(points: tuple[tuple[float, float], ...]) -> float:
    return sum(
        first[0] * second[1] - second[0] * first[1]
        for first, second in zip(points, points[1:] + points[:1])
    )


def point_on_segment(
    point: tuple[float, float],
    first: tuple[float, float],
    second: tuple[float, float],
    epsilon: float = 1e-7,
) -> bool:
    cross = (point[0] - first[0]) * (second[1] - first[1]) - (
        point[1] - first[1]
    ) * (second[0] - first[0])
    if abs(cross) > epsilon:
        return False
    return (
        min(first[0], second[0]) - epsilon <= point[0] <= max(first[0], second[0]) + epsilon
        and min(first[1], second[1]) - epsilon <= point[1] <= max(first[1], second[1]) + epsilon
    )


def orientation(
    first: tuple[float, float],
    second: tuple[float, float],
    third: tuple[float, float],
) -> float:
    return (second[0] - first[0]) * (third[1] - first[1]) - (
        second[1] - first[1]
    ) * (third[0] - first[0])


def segments_intersect(
    first_start: tuple[float, float],
    first_end: tuple[float, float],
    second_start: tuple[float, float],
    second_end: tuple[float, float],
) -> bool:
    first_a = orientation(first_start, first_end, second_start)
    first_b = orientation(first_start, first_end, second_end)
    second_a = orientation(second_start, second_end, first_start)
    second_b = orientation(second_start, second_end, first_end)
    epsilon = 1e-7
    if ((first_a > epsilon and first_b < -epsilon) or (first_a < -epsilon and first_b > epsilon)) and (
        (second_a > epsilon and second_b < -epsilon)
        or (second_a < -epsilon and second_b > epsilon)
    ):
        return True
    return (
        abs(first_a) <= epsilon and point_on_segment(second_start, first_start, first_end)
    ) or (
        abs(first_b) <= epsilon and point_on_segment(second_end, first_start, first_end)
    ) or (
        abs(second_a) <= epsilon and point_on_segment(first_start, second_start, second_end)
    ) or (
        abs(second_b) <= epsilon and point_on_segment(first_end, second_start, second_end)
    )


def validate_simple_polygon(points: tuple[tuple[int, int], ...], label: str) -> None:
    if len(points) < 3 or len(points) > MAX_POLYGON_POINTS:
        fail(f"{label} must contain 3 through {MAX_POLYGON_POINTS} points")
    if len(set(points)) != len(points):
        fail(f"{label} must not repeat a point")
    float_points = tuple((float(x), float(y)) for x, y in points)
    if abs(polygon_area2(float_points)) < 1.0:
        fail(f"{label} must enclose a non-zero area")
    edge_count = len(points)
    for first_index in range(edge_count):
        first_start = float_points[first_index]
        first_end = float_points[(first_index + 1) % edge_count]
        for second_index in range(first_index + 1, edge_count):
            if second_index in {first_index, (first_index + 1) % edge_count}:
                continue
            if first_index == 0 and second_index == edge_count - 1:
                continue
            second_start = float_points[second_index]
            second_end = float_points[(second_index + 1) % edge_count]
            if segments_intersect(first_start, first_end, second_start, second_end):
                fail(f"{label} must be a simple non-self-intersecting polygon")


def round_div_signed(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if numerator >= 0:
        return (numerator + denominator // 2) // denominator
    return -((-numerator + denominator // 2) // denominator)


def soft_tail_trim_points(
    tail: tuple[tuple[int, int], ...],
    tip_trim: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    first_base, tip, second_base = tail
    scale = OVERLAY_SCALE
    tip_high = (tip[0] * scale, tip[1] * scale)
    trim_distance = tip_trim * scale

    def trim_toward_base(base: tuple[int, int]) -> tuple[int, int]:
        delta_x = (base[0] - tip[0]) * scale
        delta_y = (base[1] - tip[1]) * scale
        squared_length = delta_x * delta_x + delta_y * delta_y
        length = math.isqrt(squared_length)
        if length * length < squared_length:
            length += 1
        return (
            tip_high[0] + round_div_signed(delta_x * trim_distance, length),
            tip_high[1] + round_div_signed(delta_y * trim_distance, length),
        )

    return trim_toward_base(first_base), trim_toward_base(second_base)


def validate_tail_render_options(
    tail: tuple[tuple[int, int], ...],
    tail_style: str,
    tail_tip_trim: int,
    stroke_width: int,
    label: str,
) -> None:
    if tail_style not in {"pointed", "soft-rounded"}:
        fail(f"{label}.style must be pointed or soft-rounded")
    if tail_style == "pointed":
        if tail_tip_trim != 0:
            fail(f"{label}.tip_trim is only valid with style soft-rounded")
        return
    if len(tail) != 3:
        fail(f"{label}.style soft-rounded requires exactly three points")
    minimum_tip_trim = max(2, stroke_width * 2)
    tip = tail[1]
    shortest_leg = min(
        math.isqrt((base[0] - tip[0]) ** 2 + (base[1] - tip[1]) ** 2)
        for base in (tail[0], tail[2])
    )
    maximum_tip_trim = min(MAX_TAIL_TIP_TRIM, shortest_leg // 2)
    if maximum_tip_trim < minimum_tip_trim:
        fail(f"{label} is too short for a soft-rounded tip at stroke_width {stroke_width}")
    if not minimum_tip_trim <= tail_tip_trim <= maximum_tip_trim:
        fail(
            f"{label}.tip_trim must be between {minimum_tip_trim} and "
            f"{maximum_tip_trim} for this tail and stroke"
        )
    first_trim, second_trim = soft_tail_trim_points(tail, tail_tip_trim)
    cap_dx = first_trim[0] - second_trim[0]
    cap_dy = first_trim[1] - second_trim[1]
    minimum_cap = max(4, stroke_width * 2 + 2) * OVERLAY_SCALE
    if cap_dx * cap_dx + cap_dy * cap_dy < minimum_cap * minimum_cap:
        fail(
            f"{label} soft-rounded tip is still needle-like; effective cap width "
            f"must be at least {minimum_cap // OVERLAY_SCALE}px"
        )


def soft_rounded_tail_polygon(
    tail: tuple[tuple[int, int], ...],
    tip_trim: int,
) -> tuple[tuple[int, int], ...]:
    first_base, tip, second_base = tail
    scale = OVERLAY_SCALE
    first_trim, second_trim = soft_tail_trim_points(tail, tip_trim)
    tip_high = (tip[0] * scale, tip[1] * scale)
    curve: list[tuple[int, int]] = []
    denominator = SOFT_TAIL_CURVE_SEGMENTS * SOFT_TAIL_CURVE_SEGMENTS
    for step in range(SOFT_TAIL_CURVE_SEGMENTS + 1):
        inverse = SOFT_TAIL_CURVE_SEGMENTS - step
        curve.append(
            (
                round_div_signed(
                    inverse * inverse * first_trim[0]
                    + 2 * inverse * step * tip_high[0]
                    + step * step * second_trim[0],
                    denominator,
                ),
                round_div_signed(
                    inverse * inverse * first_trim[1]
                    + 2 * inverse * step * tip_high[1]
                    + step * step * second_trim[1],
                    denominator,
                ),
            )
        )
    return (
        (first_base[0] * scale, first_base[1] * scale),
        *curve,
        (second_base[0] * scale, second_base[1] * scale),
    )


def bubble_shape_masks(
    shape: str,
    bbox: tuple[int, int, int, int],
    corner_radius: int,
    tail: tuple[tuple[int, int], ...],
    stroke_width: int,
    tail_style: str,
    tail_tip_trim: int,
) -> tuple[tuple[int, int], Image.Image, Image.Image, Image.Image]:
    validate_tail_render_options(tail, tail_style, tail_tip_trim, stroke_width, "tail")
    xs = [bbox[0], bbox[2], *(point[0] for point in tail)]
    ys = [bbox[1], bbox[3], *(point[1] for point in tail)]
    padding = stroke_width + 2
    left = min(xs) - padding
    top = min(ys) - padding
    right = max(xs) + padding + 1
    bottom = max(ys) + padding + 1
    scale = OVERLAY_SCALE
    size = ((right - left) * scale, (bottom - top) * scale)
    body = Image.new("L", size, 0)
    body_box = (
        (bbox[0] - left) * scale,
        (bbox[1] - top) * scale,
        (bbox[2] - left) * scale - 1,
        (bbox[3] - top) * scale - 1,
    )
    body_draw = ImageDraw.Draw(body)
    if shape == "ellipse":
        body_draw.ellipse(body_box, fill=255)
    else:
        body_draw.rounded_rectangle(body_box, radius=corner_radius * scale, fill=255)
    tail_mask = Image.new("L", size, 0)
    if tail:
        if tail_style == "soft-rounded":
            points = [
                (x - left * scale, y - top * scale)
                for x, y in soft_rounded_tail_polygon(tail, tail_tip_trim)
            ]
        else:
            points = [((x - left) * scale, (y - top) * scale) for x, y in tail]
        ImageDraw.Draw(tail_mask).polygon(points, fill=255)
    return (left, top), body, tail_mask, ImageChops.lighter(body, tail_mask)


def erode_mask(mask: Image.Image, radius: int) -> Image.Image:
    result = mask
    for _ in range(radius):
        result = result.filter(ImageFilter.MinFilter(3))
    return result


def validate_bubble_tail_topology(
    shape: str,
    bbox: tuple[int, int, int, int],
    corner_radius: int,
    tail: tuple[tuple[int, int], ...],
    stroke_width: int,
    label: str,
    tail_style: str,
    tail_tip_trim: int,
) -> None:
    if tail:
        validate_simple_polygon(tail, label)
    origin, body, tail_mask, union = bubble_shape_masks(
        shape,
        bbox,
        corner_radius,
        tail,
        stroke_width,
        tail_style,
        tail_tip_trim,
    )
    hole_probe = union.copy()
    ImageDraw.floodfill(hole_probe, (0, 0), 127, thresh=0)
    if hole_probe.histogram()[0]:
        fail(f"{label} must not enclose a hole inside the bubble silhouette")
    erosion_radius = stroke_width * OVERLAY_SCALE
    interior = erode_mask(union, erosion_radius)
    if interior.getbbox() is None:
        fail(f"{label} leaves no white bubble interior after applying the stroke")
    if not tail:
        return

    def point_is_in_body(point: tuple[int, int]) -> bool:
        x = (point[0] - origin[0]) * OVERLAY_SCALE
        y = (point[1] - origin[1]) * OVERLAY_SCALE
        return 0 <= x < body.width and 0 <= y < body.height and body.getpixel((x, y)) > 0

    if tail_style == "soft-rounded":
        if not point_is_in_body(tail[0]) or not point_is_in_body(tail[2]) or point_is_in_body(tail[1]):
            fail(f"{label} soft-rounded order must be [body base, exterior tip, body base]")
    intersection = ImageChops.multiply(body, tail_mask)
    if intersection.getbbox() is None:
        fail(f"{label} must overlap the bubble body to form one closed silhouette")
    durable_neck = erode_mask(intersection, erosion_radius)
    if durable_neck.getbbox() is None:
        fail(f"{label} attachment is too narrow to remain open after the bubble stroke")
    if ImageChops.subtract(tail_mask, body).getbbox() is None:
        fail(f"{label} must extend outside the bubble body")
    exterior = ImageChops.multiply(interior, ImageChops.invert(body))
    if exterior.getbbox() is None:
        fail(f"{label} must retain white interior outside the body; a black plug is invalid")
    traversable = interior.tobytes()
    seeds = ImageChops.multiply(interior, durable_neck).tobytes()
    targets = exterior.tobytes()
    start = seeds.find(b"\xff")
    if start < 0:
        fail(f"{label} leaves no bubble-body interior after applying the stroke")
    width, height = interior.size
    visited = bytearray(len(traversable))
    visited[start] = 1
    pending: deque[int] = deque([start])
    while pending:
        current = pending.popleft()
        if targets[current]:
            return
        x = current % width
        neighbors = []
        if x > 0:
            neighbors.append(current - 1)
        if x + 1 < width:
            neighbors.append(current + 1)
        if current >= width:
            neighbors.append(current - width)
        if current + width < width * height:
            neighbors.append(current + width)
        for neighbor in neighbors:
            if traversable[neighbor] and not visited[neighbor]:
                visited[neighbor] = 1
                pending.append(neighbor)
    fail(f"{label} white interior does not connect the bubble body to the exposed tail")


def rotate_point(
    point: tuple[float, float],
    center: tuple[float, float],
    degrees: float,
) -> tuple[float, float]:
    radians = math.radians(degrees)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    offset_x = point[0] - center[0]
    offset_y = point[1] - center[1]
    return (
        center[0] + offset_x * cosine - offset_y * sine,
        center[1] + offset_x * sine + offset_y * cosine,
    )


def transform_polygon(
    points: tuple[tuple[int, int], ...],
    frame: tuple[int, int, int, int],
    degrees: float,
) -> tuple[tuple[float, float], ...]:
    if degrees == 0.0:
        return tuple((float(x), float(y)) for x, y in points)
    center = ((frame[0] + frame[2]) / 2.0, (frame[1] + frame[3]) / 2.0)
    return tuple(rotate_point((float(x), float(y)), center, degrees) for x, y in points)


def polygon_bbox(points: tuple[tuple[float, float], ...]) -> tuple[float, float, float, float]:
    return (
        min(point[0] for point in points),
        min(point[1] for point in points),
        max(point[0] for point in points),
        max(point[1] for point in points),
    )


def point_in_polygon(
    point: tuple[float, float],
    polygon: tuple[tuple[float, float], ...],
    *,
    include_boundary: bool = True,
) -> bool:
    for first, second in zip(polygon, polygon[1:] + polygon[:1]):
        if point_on_segment(point, first, second):
            return include_boundary
    inside_polygon = False
    previous = polygon[-1]
    for current in polygon:
        if (current[1] > point[1]) != (previous[1] > point[1]):
            crossing_x = (
                (previous[0] - current[0])
                * (point[1] - current[1])
                / (previous[1] - current[1])
                + current[0]
            )
            if point[0] < crossing_x:
                inside_polygon = not inside_polygon
        previous = current
    return inside_polygon


def bbox_polygon(box: tuple[int, int, int, int], margin: int = 0) -> tuple[tuple[float, float], ...]:
    left, top, right, bottom = expand_box(box, margin)
    return (
        (float(left), float(top)),
        (float(right), float(top)),
        (float(right), float(bottom)),
        (float(left), float(bottom)),
    )


def polygon_interior_edge_samples(
    polygon: tuple[tuple[float, float], ...],
) -> tuple[tuple[float, float], ...]:
    direction = 1.0 if polygon_area2(polygon) > 0 else -1.0
    samples: list[tuple[float, float]] = []
    for first, second in zip(polygon, polygon[1:] + polygon[:1]):
        delta_x = second[0] - first[0]
        delta_y = second[1] - first[1]
        length = math.hypot(delta_x, delta_y)
        if length <= 1e-7:
            continue
        midpoint = ((first[0] + second[0]) / 2.0, (first[1] + second[1]) / 2.0)
        inward = (
            -delta_y / length * direction * 1e-3,
            delta_x / length * direction * 1e-3,
        )
        candidate = (midpoint[0] + inward[0], midpoint[1] + inward[1])
        if point_in_polygon(candidate, polygon, include_boundary=False):
            samples.append(candidate)
    return tuple(samples)


def polygons_overlap(
    first: tuple[tuple[float, float], ...],
    second: tuple[tuple[float, float], ...],
) -> bool:
    first_box = polygon_bbox(first)
    second_box = polygon_bbox(second)
    if (
        max(first_box[0], second_box[0]) >= min(first_box[2], second_box[2])
        or max(first_box[1], second_box[1]) >= min(first_box[3], second_box[3])
    ):
        return False
    for first_start, first_end in zip(first, first[1:] + first[:1]):
        for second_start, second_end in zip(second, second[1:] + second[:1]):
            first_a = orientation(first_start, first_end, second_start)
            first_b = orientation(first_start, first_end, second_end)
            second_a = orientation(second_start, second_end, first_start)
            second_b = orientation(second_start, second_end, first_end)
            if first_a * first_b < -1e-7 and second_a * second_b < -1e-7:
                return True
    if any(point_in_polygon(point, second, include_boundary=False) for point in first):
        return True
    if any(point_in_polygon(point, first, include_boundary=False) for point in second):
        return True
    if any(
        point_in_polygon(point, second, include_boundary=False)
        for point in polygon_interior_edge_samples(first)
    ):
        return True
    if any(
        point_in_polygon(point, first, include_boundary=False)
        for point in polygon_interior_edge_samples(second)
    ):
        return True
    first_center = (
        sum(point[0] for point in first) / len(first),
        sum(point[1] for point in first) / len(first),
    )
    second_center = (
        sum(point[0] for point in second) / len(second),
        sum(point[1] for point in second) / len(second),
    )
    return point_in_polygon(first_center, second, include_boundary=False) or point_in_polygon(
        second_center, first, include_boundary=False
    )


def polygon_contains_bbox(
    polygon: tuple[tuple[float, float], ...],
    box: tuple[int, int, int, int],
) -> bool:
    left, top, right, bottom = (float(value) for value in box)
    corners = (
        (left, top),
        (right, top),
        (right, bottom),
        (left, bottom),
    )
    if not all(point_in_polygon(point, polygon) for point in corners):
        return False
    if any(
        left < point[0] < right and top < point[1] < bottom
        for point in polygon
    ):
        return False
    box_edges = tuple(zip(corners, corners[1:] + corners[:1]))
    for polygon_start, polygon_end in zip(polygon, polygon[1:] + polygon[:1]):
        for box_start, box_end in box_edges:
            first_a = orientation(polygon_start, polygon_end, box_start)
            first_b = orientation(polygon_start, polygon_end, box_end)
            second_a = orientation(box_start, box_end, polygon_start)
            second_b = orientation(box_start, box_end, polygon_end)
            if first_a * first_b < -1e-7 and second_a * second_b < -1e-7:
                return False
    samples = (
        ((left + right) / 2.0, top),
        (right, (top + bottom) / 2.0),
        ((left + right) / 2.0, bottom),
        (left, (top + bottom) / 2.0),
        ((left + right) / 2.0, (top + bottom) / 2.0),
    )
    return all(point_in_polygon(point, polygon) for point in samples)


def resolve_path(raw: Any, base: Path, label: str) -> tuple[str, Path]:
    original = require_string(raw, label)
    candidate = Path(original).expanduser()
    if not candidate.is_absolute():
        candidate = base / candidate
    return original, candidate.resolve()


def path_collision_key(path: Path) -> str:
    return unicodedata.normalize("NFC", str(path)).casefold()


def paths_alias(first: Path, second: Path) -> bool:
    if path_collision_key(first) == path_collision_key(second):
        return True
    if first.exists() and second.exists():
        try:
            return os.path.samefile(first, second)
        except OSError:
            return False
    return False


def load_json(path: Path) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        fail(f"manifest does not exist or is not a file: {path}")
    try:
        raw_bytes = path.read_bytes()
        parsed = json.loads(raw_bytes.decode("utf-8"))
    except UnicodeDecodeError as error:
        fail(f"manifest must be UTF-8: {error}")
    except json.JSONDecodeError as error:
        fail(f"manifest is not valid JSON at line {error.lineno}, column {error.colno}: {error.msg}")
    return require_mapping(parsed, "manifest"), hashlib.sha256(raw_bytes).hexdigest()


def inspect_image(path: Path, label: str, expected_sha256: str) -> tuple[bytes, tuple[int, int], str]:
    if not path.is_file():
        fail(f"{label} does not exist or is not a file: {path}")
    try:
        file_size = path.stat().st_size
        if file_size > MAX_SOURCE_FILE_BYTES:
            fail(f"{label} exceeds the {MAX_SOURCE_FILE_BYTES:,}-byte source-file limit")
        source_bytes = path.read_bytes()
        actual_sha256 = hashlib.sha256(source_bytes).hexdigest()
        if actual_sha256 != expected_sha256:
            fail(
                f"{label} sha256 mismatch: expected {expected_sha256}, got {actual_sha256}; "
                "do not silently replace an accepted panel"
            )
        with Image.open(io.BytesIO(source_bytes)) as image:
            if getattr(image, "n_frames", 1) != 1:
                fail(f"{label} must be a single-frame image, got {image.n_frames} frames")
            if image.width * image.height > MAX_SOURCE_PIXELS:
                fail(f"{label} exceeds the {MAX_SOURCE_PIXELS:,}-pixel decoded source limit")
            image.load()
            return source_bytes, image.size, actual_sha256
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
        fail(f"{label} cannot be decoded as an image: {error}")


def validate_paper_matte(canvas: dict[str, Any], schema_version: int) -> PaperMatteSpec | None:
    raw = canvas.get("paper_matte")
    if raw is None:
        return None
    if schema_version < 2:
        fail("canvas.paper_matte requires schema_version 2")
    matte = require_mapping(raw, "canvas.paper_matte")
    reject_unknown_keys(matte, PAPER_MATTE_KEYS, "canvas.paper_matte")
    enabled = require_bool(matte.get("enabled", True), "canvas.paper_matte.enabled")
    if not enabled:
        return None
    return PaperMatteSpec(
        seed=require_bounded_int(
            matte.get("seed", 1),
            "canvas.paper_matte.seed",
            0,
            0xFFFFFFFF,
        ),
        grain_strength=require_bounded_int(
            matte.get("grain_strength", 4),
            "canvas.paper_matte.grain_strength",
            1,
            24,
        ),
        tile_size=require_bounded_int(
            matte.get("tile_size", 192),
            "canvas.paper_matte.tile_size",
            32,
            512,
        ),
    )


def validate_panel(
    item: Any,
    index: int,
    base: Path,
    canvas_box: tuple[int, int, int, int],
    schema_version: int,
) -> PanelSpec:
    panel = require_mapping(item, f"panels[{index}]")
    prefix = f"panels[{index}]"
    reject_unknown_keys(panel, PANEL_KEYS, prefix)
    panel_id = require_string(panel.get("id"), f"{prefix}.id")
    reading_order = require_int(panel.get("reading_order"), f"{prefix}.reading_order", 1)
    row = require_int(panel.get("row"), f"{prefix}.row", 1)
    column = require_int(panel.get("column"), f"{prefix}.column", 1)
    source_label, source_path = resolve_path(panel.get("source"), base, f"{prefix}.source")
    expected_sha256 = require_sha256(panel.get("expected_sha256"), f"{prefix}.expected_sha256")
    source_bytes, source_size, source_sha256 = inspect_image(
        source_path,
        f"{prefix}.source",
        expected_sha256,
    )
    expected_size = require_pair(panel.get("expected_size"), f"{prefix}.expected_size")
    if source_size != expected_size:
        fail(
            f"{prefix}.expected_size mismatch for {source_label!r}: "
            f"expected {expected_size[0]}x{expected_size[1]}, got {source_size[0]}x{source_size[1]}"
        )
    source_crop = require_bbox(panel.get("source_crop"), f"{prefix}.source_crop")
    if not inside(source_crop, (0, 0, source_size[0], source_size[1])):
        fail(f"{prefix}.source_crop {list(source_crop)} exceeds source size {list(source_size)}")
    frame = require_bbox(panel.get("frame"), f"{prefix}.frame")
    if not inside(frame, canvas_box):
        fail(f"{prefix}.frame {list(frame)} exceeds canvas {list(canvas_box)}")
    corner_radius = require_int(panel.get("corner_radius", 0), f"{prefix}.corner_radius")
    if corner_radius * 2 > min(frame[2] - frame[0], frame[3] - frame[1]):
        fail(f"{prefix}.corner_radius is too large for frame {list(frame)}")
    border = require_mapping(panel.get("border", {}), f"{prefix}.border")
    reject_unknown_keys(border, BORDER_KEYS, f"{prefix}.border")
    border_width = require_int(border.get("width", 0), f"{prefix}.border.width")
    if border_width * 2 >= min(frame[2] - frame[0], frame[3] - frame[1]):
        fail(f"{prefix}.border.width is too large for frame {list(frame)}")
    border_color = parse_color(border.get("color", "#1f1f1d"), f"{prefix}.border.color")
    advanced_fields = {"clip_polygon", "rotation_degrees", "z_index", "allow_overlap_with"}
    if schema_version < 2 and any(field in panel for field in advanced_fields):
        fail(f"{prefix} v2 geometry fields require schema_version 2")
    clip_polygon: tuple[tuple[int, int], ...] | None = None
    if "clip_polygon" in panel:
        clip_items = require_list(panel.get("clip_polygon"), f"{prefix}.clip_polygon")
        clip_polygon = tuple(
            require_point(point, f"{prefix}.clip_polygon[{point_index}]")
            for point_index, point in enumerate(clip_items)
        )
        validate_simple_polygon(clip_polygon, f"{prefix}.clip_polygon")
        for point in clip_polygon:
            if not (
                frame[0] <= point[0] <= frame[2]
                and frame[1] <= point[1] <= frame[3]
            ):
                fail(
                    f"{prefix}.clip_polygon point {list(point)} must remain inside frame {list(frame)}"
                )
        if corner_radius:
            fail(f"{prefix}.corner_radius must be 0 when clip_polygon is present")
    rotation_degrees = require_number(
        panel.get("rotation_degrees", 0),
        f"{prefix}.rotation_degrees",
        -MAX_ROTATION_DEGREES,
        MAX_ROTATION_DEGREES,
    )
    z_index = require_bounded_int(
        panel.get("z_index", 0),
        f"{prefix}.z_index",
        -MAX_ABS_Z_INDEX,
        MAX_ABS_Z_INDEX,
    )
    allow_overlap_with = require_string_list(
        panel.get("allow_overlap_with", []),
        f"{prefix}.allow_overlap_with",
    )
    if panel_id in allow_overlap_with:
        fail(f"{prefix}.allow_overlap_with may not contain its own panel id")
    unrotated_polygon = clip_polygon or (
        (frame[0], frame[1]),
        (frame[2], frame[1]),
        (frame[2], frame[3]),
        (frame[0], frame[3]),
    )
    final_polygon = transform_polygon(unrotated_polygon, frame, rotation_degrees)
    rotated_frame = transform_polygon(
        (
            (frame[0], frame[1]),
            (frame[2], frame[1]),
            (frame[2], frame[3]),
            (frame[0], frame[3]),
        ),
        frame,
        rotation_degrees,
    )
    rotated_frame_box = polygon_bbox(rotated_frame)
    canvas_halo = PANEL_FILTER_HALO if rotation_degrees else 0
    if not (
        rotated_frame_box[0] >= canvas_halo
        and rotated_frame_box[1] >= canvas_halo
        and rotated_frame_box[2] <= canvas_box[2] - canvas_halo
        and rotated_frame_box[3] <= canvas_box[3] - canvas_halo
    ):
        fail(
            f"{prefix}.rotation_degrees moves the panel outside the canvas; "
            "increase the margin or reduce the rotation"
        )
    crop_width = source_crop[2] - source_crop[0]
    crop_height = source_crop[3] - source_crop[1]
    frame_width = frame[2] - frame[0]
    frame_height = frame[3] - frame[1]
    aspect_error = abs(crop_width * frame_height - crop_height * frame_width) / max(
        crop_width * frame_height,
        crop_height * frame_width,
    )
    if aspect_error > 0.01:
        fail(
            f"{prefix}.source_crop aspect ratio differs from frame by {aspect_error:.1%}; "
            "adjust the crop to avoid stretching"
        )
    protected_items = require_list(panel.get("protected_action_regions", []), f"{prefix}.protected_action_regions")
    protected_regions: list[tuple[str, tuple[int, int, int, int]]] = []
    protected_ids: set[str] = set()
    for region_index, region_value in enumerate(protected_items):
        region_prefix = f"{prefix}.protected_action_regions[{region_index}]"
        region = require_mapping(region_value, region_prefix)
        reject_unknown_keys(region, PROTECTED_REGION_KEYS, region_prefix)
        region_id = require_string(region.get("id"), f"{region_prefix}.id")
        if region_id in protected_ids:
            fail(f"{prefix}.protected_action_regions contains duplicate id {region_id!r}")
        protected_ids.add(region_id)
        region_bbox = require_bbox(region.get("bbox"), f"{region_prefix}.bbox")
        if clip_polygon is None and rotation_degrees == 0.0:
            if not inside(region_bbox, frame):
                fail(f"{region_prefix}.bbox must remain inside panel {panel_id!r}")
        elif not inside(region_bbox, canvas_box) or not polygon_contains_bbox(final_polygon, region_bbox):
            fail(
                f"{region_prefix}.bbox must remain inside the final clipped/rotated "
                f"footprint of panel {panel_id!r}"
            )
        protected_regions.append((region_id, region_bbox))
    return PanelSpec(
        panel_id=panel_id,
        reading_order=reading_order,
        row=row,
        column=column,
        source_label=source_label,
        source_path=source_path,
        source_bytes=source_bytes,
        source_sha256=source_sha256,
        source_size=source_size,
        source_crop=source_crop,
        frame=frame,
        corner_radius=corner_radius,
        border_width=border_width,
        border_color=border_color,
        clip_polygon=clip_polygon,
        final_polygon=final_polygon,
        rotation_degrees=rotation_degrees,
        z_index=z_index,
        allow_overlap_with=allow_overlap_with,
        protected_action_regions=tuple(protected_regions),
    )


def validate_panel_flow(panels: tuple[PanelSpec, ...], schema_version: int) -> None:
    if not panels:
        fail("panels must contain at least one panel")
    ids = [panel.panel_id for panel in panels]
    if len(set(ids)) != len(ids):
        fail("panel ids must be unique")
    orders = [panel.reading_order for panel in panels]
    if sorted(orders) != list(range(1, len(panels) + 1)):
        fail(f"panel reading_order values must be consecutive 1..{len(panels)}")

    ordered = sorted(panels, key=lambda panel: panel.reading_order)
    rows = [panel.row for panel in ordered]
    if rows != sorted(rows):
        fail("panel rows must be nondecreasing in reading_order")

    panel_by_id = {panel.panel_id: panel for panel in panels}
    for panel in panels:
        unknown = [panel_id for panel_id in panel.allow_overlap_with if panel_id not in panel_by_id]
        if unknown:
            fail(
                f"panel {panel.panel_id!r}.allow_overlap_with contains unknown panel ids: "
                + ", ".join(repr(panel_id) for panel_id in unknown)
            )

    for first_index, first in enumerate(panels):
        for second in panels[first_index + 1 :]:
            if schema_version == 1:
                if intersects(first.frame, second.frame):
                    fail(f"panel frames overlap: {first.panel_id!r} and {second.panel_id!r}")
                continue
            if not polygons_overlap(first.final_polygon, second.final_polygon):
                continue
            if (
                second.panel_id not in first.allow_overlap_with
                or first.panel_id not in second.allow_overlap_with
            ):
                fail(
                    f"panel footprints overlap without mutual allow_overlap_with: "
                    f"{first.panel_id!r} and {second.panel_id!r}"
                )
            if first.z_index == second.z_index:
                fail(
                    f"overlapping panels {first.panel_id!r} and {second.panel_id!r} "
                    "must have different z_index values"
                )
            lower, upper = (
                (first, second) if first.z_index < second.z_index else (second, first)
            )
            for region_id, protected_bbox in lower.protected_action_regions:
                protected_polygon = bbox_polygon(protected_bbox, PANEL_FILTER_HALO)
                if polygons_overlap(upper.final_polygon, protected_polygon):
                    fail(
                        f"upper panel {upper.panel_id!r} overlaps protected action region "
                        f"{region_id!r} in lower panel {lower.panel_id!r}"
                    )

    seen_rows: dict[int, list[PanelSpec]] = {}
    for panel in ordered:
        seen_rows.setdefault(panel.row, []).append(panel)
    expected_rows = list(range(1, len(seen_rows) + 1))
    if sorted(seen_rows) != expected_rows:
        fail(f"panel row values must be consecutive 1..{len(seen_rows)}")

    previous_bottom = 0
    for row_number in expected_rows:
        row_panels = seen_rows[row_number]
        columns = [panel.column for panel in row_panels]
        if columns != list(range(1, len(row_panels) + 1)):
            fail(f"row {row_number} columns must be consecutive and follow reading_order")
        lefts = [panel.frame[0] for panel in row_panels]
        if lefts != sorted(lefts):
            fail(f"row {row_number} panels must move left-to-right in reading_order")
        if len(row_panels) > 1:
            common_top = max(panel.frame[1] for panel in row_panels)
            common_bottom = min(panel.frame[3] for panel in row_panels)
            if common_top >= common_bottom:
                fail(f"row {row_number} panels must share a visible vertical band")
        row_top = min(panel.frame[1] for panel in row_panels)
        if schema_version == 1 and row_number > 1 and row_top < previous_bottom:
            fail(f"row {row_number} starts above the preceding row's bottom edge")
        previous_bottom = max(panel.frame[3] for panel in row_panels)


def resolve_font(
    manifest: dict[str, Any],
    base: Path,
    requested_font: str | None,
    required_text: str,
) -> tuple[str | None, bytes | None, str | None, int, tuple[int, int, int, int]]:
    lettering = require_mapping(manifest.get("lettering", {}), "lettering")
    reject_unknown_keys(lettering, LETTERING_KEYS, "lettering")
    face_index = require_int(lettering.get("face_index", 0), "lettering.face_index")
    color = parse_color(lettering.get("color", "#1f1f1d"), "lettering.color")
    if not required_text:
        return None, None, None, face_index, color

    if requested_font:
        candidates = [requested_font]
    else:
        candidates = require_list(lettering.get("font_candidates"), "lettering.font_candidates")
        if not candidates:
            fail("lettering.font_candidates must not be empty when a bubble contains text")
    checked: list[str] = []
    for index, raw in enumerate(candidates):
        original, candidate = resolve_path(raw, base, f"lettering.font_candidates[{index}]")
        if not candidate.is_file():
            checked.append(f"{original} (missing)")
            continue
        try:
            font_bytes = candidate.read_bytes()
            font = ImageFont.truetype(io.BytesIO(font_bytes), 32, index=face_index)
        except (OSError, ValueError) as error:
            checked.append(f"{original} (cannot snapshot/load: {error})")
            continue
        missing = missing_glyphs(font, required_text)
        if missing:
            codepoints = ", ".join(f"U+{ord(character):04X}" for character in missing)
            checked.append(f"{original} (missing glyphs: {codepoints})")
            continue
        font_sha256 = hashlib.sha256(font_bytes).hexdigest()
        return candidate.name, font_bytes, font_sha256, face_index, color
    fail("no configured CJK font exists; checked: " + ", ".join(checked))


def validate_bubbles(
    manifest: dict[str, Any],
    panel_by_id: dict[str, PanelSpec],
    schema_version: int,
) -> tuple[dict[str, Any], ...]:
    raw_bubbles = require_list(manifest.get("bubbles", []), "bubbles")
    validated: list[dict[str, Any]] = []
    ids: set[str] = set()
    for index, item in enumerate(raw_bubbles):
        bubble = require_mapping(item, f"bubbles[{index}]")
        prefix = f"bubbles[{index}]"
        reject_unknown_keys(bubble, BUBBLE_KEYS, prefix)
        bubble_id = require_string(bubble.get("id"), f"{prefix}.id")
        if bubble_id in ids:
            fail(f"duplicate bubble id: {bubble_id!r}")
        ids.add(bubble_id)
        if schema_version < 2 and "allow_overlap_with" in bubble:
            fail(f"{prefix}.allow_overlap_with requires schema_version 2")
        allow_overlap_with = require_string_list(
            bubble.get("allow_overlap_with", []),
            f"{prefix}.allow_overlap_with",
        )
        if bubble_id in allow_overlap_with:
            fail(f"{prefix}.allow_overlap_with may not contain its own bubble id")
        panel_id = require_string(bubble.get("panel"), f"{prefix}.panel")
        if panel_id not in panel_by_id:
            fail(f"{prefix}.panel refers to unknown panel id {panel_id!r}")
        target_panel = panel_by_id[panel_id]
        panel_frame = target_panel.frame
        advanced_target = target_panel.clip_polygon is not None or target_panel.rotation_degrees != 0.0
        reading_order = require_int(bubble.get("reading_order"), f"{prefix}.reading_order", 1)
        speaker = require_string(bubble.get("speaker"), f"{prefix}.speaker")
        speaker_anchor = require_point(bubble.get("speaker_anchor"), f"{prefix}.speaker_anchor")
        if advanced_target:
            anchor_inside = point_in_polygon(
                (float(speaker_anchor[0]), float(speaker_anchor[1])),
                target_panel.final_polygon,
            )
        else:
            anchor_inside = point_inside(speaker_anchor, panel_frame)
        if not anchor_inside:
            fail(f"{prefix}.speaker_anchor must remain inside panel {panel_id!r}")
        shape = bubble.get("shape", "ellipse")
        if shape not in ("ellipse", "rounded_rect"):
            fail(f"{prefix}.shape must be 'ellipse' or 'rounded_rect'")
        bbox = require_bbox(bubble.get("bbox"), f"{prefix}.bbox")
        if advanced_target:
            bbox_inside_panel = polygon_contains_bbox(target_panel.final_polygon, bbox)
        else:
            bbox_inside_panel = inside(bbox, panel_frame)
        if not bbox_inside_panel:
            fail(f"{prefix}.bbox must remain inside panel {panel_id!r}")
        safe_region = require_bbox(bubble.get("safe_region"), f"{prefix}.safe_region")
        if advanced_target:
            safe_inside_panel = polygon_contains_bbox(target_panel.final_polygon, safe_region)
        else:
            safe_inside_panel = inside(safe_region, panel_frame)
        if not safe_inside_panel:
            fail(f"{prefix}.safe_region must remain inside panel {panel_id!r}")
        if not inside(bbox, safe_region):
            fail(f"{prefix}.bbox must remain inside its approved safe_region")
        radius = require_int(bubble.get("corner_radius", 20), f"{prefix}.corner_radius")
        if shape == "rounded_rect" and radius * 2 > min(bbox[2] - bbox[0], bbox[3] - bbox[1]):
            fail(f"{prefix}.corner_radius is too large for bbox")
        stroke_width = require_int(bubble.get("stroke_width", 3), f"{prefix}.stroke_width", 1)
        minimum_dimension = min(bbox[2] - bbox[0], bbox[3] - bbox[1])
        stroke_limit = min(MAX_BUBBLE_STROKE_WIDTH, max(1, (minimum_dimension - 1) // 2))
        if stroke_width > stroke_limit:
            fail(f"{prefix}.stroke_width may not exceed {stroke_limit} for this bubble")
        fill = parse_color(bubble.get("fill", "#fffdf7"), f"{prefix}.fill")
        stroke = parse_color(bubble.get("stroke", "#1f1f1d"), f"{prefix}.stroke")
        tail_value = bubble.get("tail", [])
        if isinstance(tail_value, list):
            tail_items = require_list(tail_value, f"{prefix}.tail")
            tail_points_label = f"{prefix}.tail"
            tail_style = "pointed"
            tail_tip_trim = 0
        elif isinstance(tail_value, dict):
            if schema_version < 2:
                fail(f"{prefix}.tail soft-rounded object requires schema_version 2")
            tail_object = require_mapping(tail_value, f"{prefix}.tail")
            reject_unknown_keys(
                tail_object,
                frozenset({"style", "points", "tip_trim"}),
                f"{prefix}.tail",
            )
            if set(tail_object) != {"style", "points", "tip_trim"}:
                fail(f"{prefix}.tail soft-rounded object requires style, points, and tip_trim")
            tail_style = require_string(tail_object.get("style"), f"{prefix}.tail.style")
            if tail_style != "soft-rounded":
                fail(f"{prefix}.tail.style must be 'soft-rounded'")
            tail_tip_trim = require_int(tail_object.get("tip_trim"), f"{prefix}.tail.tip_trim")
            tail_items = require_list(tail_object.get("points"), f"{prefix}.tail.points")
            tail_points_label = f"{prefix}.tail.points"
        else:
            fail(f"{prefix}.tail must be an array or a soft-rounded tail object")
        if tail_items and len(tail_items) != 3:
            fail(f"{tail_points_label} must be empty or contain exactly 3 points")
        tail = tuple(
            require_point(point, f"{tail_points_label}[{point_index}]")
            for point_index, point in enumerate(tail_items)
        )
        for point in tail:
            if not point_inside(point, safe_region):
                fail(f"{tail_points_label} point {list(point)} must remain inside its approved safe_region")
        validate_bubble_tail_topology(
            shape,
            bbox,
            radius,
            tail,
            stroke_width,
            tail_points_label,
            tail_style,
            tail_tip_trim,
        )

        collision_margin = (stroke_width + 1) // 2 + 2
        bubble_visual_bbox = expand_box(bbox, collision_margin)
        if not inside(bubble_visual_bbox, safe_region):
            fail(
                f"{prefix}.bbox needs a {collision_margin}px stroke/filter margin inside safe_region"
            )
        tail_visual_bbox = expand_box(points_bbox(tail), collision_margin) if tail else None
        if tail_visual_bbox is not None and not inside(tail_visual_bbox, safe_region):
            fail(
                f"{prefix}.tail needs a {collision_margin}px stroke/filter margin inside safe_region"
            )

        if schema_version >= 2:
            safe_polygon = bbox_polygon(safe_region)
            for other_panel in panel_by_id.values():
                if other_panel.panel_id == panel_id or other_panel.z_index <= target_panel.z_index:
                    continue
                if polygons_overlap(other_panel.final_polygon, safe_polygon):
                    fail(
                        f"{prefix}.safe_region is covered by higher-z panel "
                        f"{other_panel.panel_id!r}; move the bubble or revise panel overlap"
                    )
                if point_in_polygon(
                    (float(speaker_anchor[0]), float(speaker_anchor[1])),
                    other_panel.final_polygon,
                    include_boundary=False,
                ):
                    fail(
                        f"{prefix}.speaker_anchor is covered by higher-z panel "
                        f"{other_panel.panel_id!r}"
                    )

        protected_panels = panel_by_id.values() if schema_version >= 2 else (target_panel,)
        for protected_panel in protected_panels:
            for region_id, protected_bbox in protected_panel.protected_action_regions:
                if intersects(bubble_visual_bbox, protected_bbox):
                    owner_note = (
                        ""
                        if protected_panel.panel_id == panel_id
                        else f" in panel {protected_panel.panel_id!r}"
                    )
                    fail(
                        f"{prefix}.bbox intersects protected action region {region_id!r}{owner_note}"
                    )
                if tail_visual_bbox is not None and intersects(tail_visual_bbox, protected_bbox):
                    owner_note = (
                        ""
                        if protected_panel.panel_id == panel_id
                        else f" in panel {protected_panel.panel_id!r}"
                    )
                    fail(
                        f"{prefix}.tail visual bounding box intersects protected action region "
                        f"{region_id!r}{owner_note}; move the tail or narrow the approved safe_region"
                    )

        text_value = bubble.get("text")
        text: dict[str, Any] | None = None
        if text_value is not None:
            source_text = require_mapping(text_value, f"{prefix}.text")
            reject_unknown_keys(source_text, BUBBLE_TEXT_KEYS, f"{prefix}.text")
            if source_text.get("language") != "zh-Hans":
                fail(f"{prefix}.text.language must be 'zh-Hans'")
            exact = require_inline_text(source_text.get("exact"), f"{prefix}.text.exact")
            lines_raw = require_list(source_text.get("lines"), f"{prefix}.text.lines")
            lines = [
                require_inline_text(line, f"{prefix}.text.lines[{line_index}]")
                for line_index, line in enumerate(lines_raw)
            ]
            if "".join(lines) != exact:
                fail(f"{prefix}.text.lines do not reconstruct the exact locked string")
            text_box = require_bbox(source_text.get("bbox"), f"{prefix}.text.bbox")
            if not inside(text_box, bbox):
                fail(f"{prefix}.text.bbox must remain inside the bubble bbox")
            font_size = require_int(source_text.get("font_size"), f"{prefix}.text.font_size", 1)
            font_limit = min(512, max(text_box[2] - text_box[0], text_box[3] - text_box[1]))
            if font_size > font_limit:
                fail(f"{prefix}.text.font_size may not exceed {font_limit} for its text bbox")
            text = {
                "language": "zh-Hans",
                "exact": exact,
                "lines": lines,
                "bbox": text_box,
                "font_size": font_size,
                "line_gap": require_int(source_text.get("line_gap", 4), f"{prefix}.text.line_gap"),
                "align": source_text.get("align", "center"),
            }
            if text["align"] not in ("left", "center", "right"):
                fail(f"{prefix}.text.align must be left, center, or right")
        validated.append(
            {
                "id": bubble_id,
                "panel": panel_id,
                "reading_order": reading_order,
                "speaker": speaker,
                "speaker_anchor": speaker_anchor,
                "shape": shape,
                "bbox": bbox,
                "safe_region": safe_region,
                "corner_radius": radius,
                "stroke_width": stroke_width,
                "fill": fill,
                "stroke": stroke,
                "tail": tail,
                "tail_style": tail_style,
                "tail_tip_trim": tail_tip_trim,
                "text": text,
                "allow_overlap_with": allow_overlap_with,
                "_visual_bbox": bubble_visual_bbox,
                "_tail_visual_bbox": tail_visual_bbox,
            }
        )
    orders = [bubble["reading_order"] for bubble in validated]
    if sorted(orders) != list(range(1, len(validated) + 1)):
        fail(f"bubble reading_order values must be unique and consecutive 1..{len(validated)}")
    if schema_version >= 2:
        bubble_by_id = {bubble["id"]: bubble for bubble in validated}
        for bubble in validated:
            unknown = [
                bubble_id
                for bubble_id in bubble["allow_overlap_with"]
                if bubble_id not in bubble_by_id
            ]
            if unknown:
                fail(
                    f"bubble {bubble['id']!r}.allow_overlap_with contains unknown bubble ids: "
                    + ", ".join(repr(bubble_id) for bubble_id in unknown)
                )
        for first_index, first in enumerate(validated):
            first_components = [first["_visual_bbox"]]
            if first["_tail_visual_bbox"] is not None:
                first_components.append(first["_tail_visual_bbox"])
            for second in validated[first_index + 1 :]:
                second_components = [second["_visual_bbox"]]
                if second["_tail_visual_bbox"] is not None:
                    second_components.append(second["_tail_visual_bbox"])
                if not any(
                    intersects(first_component, second_component)
                    for first_component in first_components
                    for second_component in second_components
                ):
                    continue
                if (
                    second["id"] not in first["allow_overlap_with"]
                    or first["id"] not in second["allow_overlap_with"]
                ):
                    fail(
                        f"bubble visual bounds overlap without mutual allow_overlap_with: "
                        f"{first['id']!r} and {second['id']!r}"
                    )
                for text_owner, other, other_components in (
                    (first, second, second_components),
                    (second, first, first_components),
                ):
                    if text_owner["text"] is None:
                        continue
                    if any(
                        intersects(text_owner["text"]["bbox"], component)
                        for component in other_components
                    ):
                        fail(
                            f"bubble {other['id']!r} covers locked text bbox in "
                            f"bubble {text_owner['id']!r}; text coverage cannot be allowed"
                        )
    return tuple(sorted(validated, key=lambda bubble: bubble["reading_order"]))


def validate_manifest(
    manifest_path: Path,
    requested_font: str | None,
    output_override: str | None,
    ledger_override: str | None,
) -> ValidatedManifest:
    manifest_path = manifest_path.expanduser().resolve()
    manifest, manifest_hash = load_json(manifest_path)
    reject_unknown_keys(manifest, MANIFEST_KEYS, "manifest")
    schema_version = manifest.get("schema_version")
    if isinstance(schema_version, bool) or schema_version not in (1, 2):
        fail("schema_version must be 1 or 2")
    base = manifest_path.parent
    stages = require_mapping(manifest.get("artifact_stages"), "artifact_stages")
    reject_unknown_keys(stages, ARTIFACT_STAGE_KEYS, "artifact_stages")
    input_stage = require_string(stages.get("panel_inputs"), "artifact_stages.panel_inputs")
    composition_stage = require_string(stages.get("composition"), "artifact_stages.composition")
    stage_pair = (input_stage, composition_stage)
    allowed_stage_pairs = {
        ("unlettered-panel", "unlettered-page"),
        ("page-native-unlettered", "page-native-unlettered"),
    }
    if stage_pair not in allowed_stage_pairs:
        fail(
            "artifact_stages must be either unlettered-panel -> unlettered-page "
            "or page-native-unlettered -> page-native-unlettered"
        )
    canvas = require_mapping(manifest.get("canvas"), "canvas")
    reject_unknown_keys(canvas, CANVAS_KEYS, "canvas")
    canvas_size = require_pair(canvas.get("size"), "canvas.size")
    if max(canvas_size) > MAX_CANVAS_EDGE:
        fail(f"canvas.size may not exceed {MAX_CANVAS_EDGE} pixels on either edge")
    if canvas_size[0] * canvas_size[1] > MAX_CANVAS_PIXELS:
        fail(f"canvas.size may not exceed {MAX_CANVAS_PIXELS:,} total pixels with 4x overlays")
    background = parse_color(canvas.get("background", "#f4efe6"), "canvas.background")
    paper_matte = validate_paper_matte(canvas, schema_version)
    canvas_box = (0, 0, canvas_size[0], canvas_size[1])

    panel_items = require_list(manifest.get("panels"), "panels")
    panel_list: list[PanelSpec] = []
    total_source_bytes = 0
    for index, item in enumerate(panel_items):
        panel = validate_panel(item, index, base, canvas_box, schema_version)
        total_source_bytes += len(panel.source_bytes)
        if total_source_bytes > MAX_TOTAL_SOURCE_BYTES:
            fail(f"panel source bytes exceed the {MAX_TOTAL_SOURCE_BYTES:,}-byte per-run limit")
        panel_list.append(panel)
    panels = tuple(panel_list)
    if input_stage == "page-native-unlettered":
        if len(panels) != 1:
            fail("page-native lettering requires exactly one full-canvas source")
        page_source = panels[0]
        full_canvas = (0, 0, canvas_size[0], canvas_size[1])
        if page_source.source_size != canvas_size:
            fail("page-native lettering source size must exactly match canvas.size")
        if page_source.source_crop != full_canvas or page_source.frame != full_canvas:
            fail("page-native lettering source_crop and frame must cover the exact full canvas")
        if (
            page_source.reading_order != 1
            or page_source.row != 1
            or page_source.column != 1
            or page_source.corner_radius != 0
            or page_source.border_width != 0
            or page_source.clip_polygon is not None
            or page_source.rotation_degrees != 0
            or page_source.z_index != 0
            or page_source.allow_overlap_with
        ):
            fail(
                "page-native lettering source must be one borderless, unrotated, "
                "unclipped full-canvas panel at reading_order/row/column 1"
            )
    validate_panel_flow(panels, schema_version)
    panel_by_id = {panel.panel_id: panel for panel in panels}
    bubbles = validate_bubbles(manifest, panel_by_id, schema_version)
    required_text = "".join(
        bubble["text"]["exact"] for bubble in bubbles if bubble["text"] is not None
    )
    font_name, font_bytes, font_sha256, face_index, font_color = resolve_font(
        manifest,
        base,
        requested_font,
        required_text,
    )

    output = require_mapping(manifest.get("output"), "output")
    reject_unknown_keys(output, OUTPUT_KEYS, "output")
    output_stage = require_string(output.get("stage"), "output.stage")
    expected_output_stage = "lettered-final" if bubbles else "unlettered-page"
    if input_stage == "page-native-unlettered" and not bubbles:
        fail("page-native lettering requires at least one approved bubble")
    if output_stage != expected_output_stage:
        fail(
            f"output.stage must be {expected_output_stage!r} when bubbles "
            f"{'are' if bubbles else 'are not'} rendered"
        )
    image_raw = output_override if output_override else output.get("image")
    ledger_raw = ledger_override if ledger_override else output.get("ledger")
    _, output_path = resolve_path(image_raw, base, "output.image")
    _, ledger_path = resolve_path(ledger_raw, base, "output.ledger")
    unlettered_path: Path | None = None
    if bubbles:
        _, unlettered_path = resolve_path(output.get("unlettered_image"), base, "output.unlettered_image")
    if output_path.suffix.lower() != ".png":
        fail("output.image must use a .png extension")
    if unlettered_path is not None and unlettered_path.suffix.lower() != ".png":
        fail("output.unlettered_image must use a .png extension")
    if ledger_path.suffix.lower() != ".json":
        fail("output.ledger must use a .json extension")
    output_paths = [output_path, ledger_path]
    if unlettered_path is not None:
        output_paths.append(unlettered_path)
    source_paths = {panel.source_path for panel in panels}
    for index, path in enumerate(output_paths):
        for other in output_paths[index + 1 :]:
            if paths_alias(path, other):
                fail(f"output paths alias the same file: {path} and {other}")
        if paths_alias(path, manifest_path):
            fail(f"output path may not overwrite the manifest: {path}")
        for source_path in source_paths:
            if paths_alias(path, source_path):
                fail(f"output path may not overwrite or alias a source panel: {path}")
        if not path.parent.is_dir():
            fail(f"output parent directory does not exist: {path.parent}")

    return ValidatedManifest(
        manifest_path=manifest_path,
        manifest_sha256=manifest_hash,
        schema_version=schema_version,
        raw=manifest,
        canvas_size=canvas_size,
        background=background,
        paper_matte=paper_matte,
        panels=panels,
        bubbles=bubbles,
        font_name=font_name,
        font_bytes=font_bytes,
        font_sha256=font_sha256,
        font_face_index=face_index,
        font_color=font_color,
        input_stage=input_stage,
        composition_stage=composition_stage,
        output_stage=output_stage,
        unlettered_path=unlettered_path,
        output_path=output_path,
        ledger_path=ledger_path,
    )


def scale_box(box: tuple[int, int, int, int], scale: int) -> tuple[int, int, int, int]:
    return tuple(value * scale for value in box)  # type: ignore[return-value]


def scale_draw_box(box: tuple[int, int, int, int], scale: int) -> tuple[int, int, int, int]:
    return box[0] * scale, box[1] * scale, box[2] * scale - 1, box[3] * scale - 1


def scale_point(point: tuple[int, int], scale: int) -> tuple[int, int]:
    return point[0] * scale, point[1] * scale


def render_paper_matte(
    size: tuple[int, int],
    background: tuple[int, int, int, int],
    matte: PaperMatteSpec | None,
) -> Image.Image:
    if matte is None:
        return Image.new("RGBA", size, background)
    state = matte.seed
    span = matte.grain_strength * 2 + 1
    tile_pixels: list[tuple[int, int, int]] = []
    for _ in range(matte.tile_size * matte.tile_size):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        delta = int(state % span) - matte.grain_strength
        tile_pixels.append(
            tuple(max(0, min(255, channel + delta)) for channel in background[:3])  # type: ignore[arg-type]
        )
    tile = Image.new("RGB", (matte.tile_size, matte.tile_size))
    tile.putdata(tile_pixels)
    page = Image.new("RGB", size)
    for top in range(0, size[1], matte.tile_size):
        for left in range(0, size[0], matte.tile_size):
            page.paste(tile, (left, top))
    return page.convert("RGBA")


def local_polygon_points(panel: PanelSpec, size: tuple[int, int]) -> list[tuple[int, int]]:
    if panel.clip_polygon is None:
        return [(0, 0), (size[0] - 1, 0), (size[0] - 1, size[1] - 1), (0, size[1] - 1)]
    return [
        (
            max(0, min(size[0] - 1, point[0] - panel.frame[0])),
            max(0, min(size[1] - 1, point[1] - panel.frame[1])),
        )
        for point in panel.clip_polygon
    ]


def render_advanced_panel(page: Image.Image, panel: PanelSpec) -> None:
    with Image.open(io.BytesIO(panel.source_bytes)) as source:
        source.load()
        crop = source.convert("RGBA").crop(panel.source_crop)
    size = (panel.frame[2] - panel.frame[0], panel.frame[3] - panel.frame[1])
    rendered = crop.resize(size, resample=Image.Resampling.LANCZOS, reducing_gap=3.0)
    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    polygon = local_polygon_points(panel, size)
    if panel.clip_polygon is not None:
        mask_draw.polygon(polygon, fill=255)
    elif panel.corner_radius:
        mask_draw.rounded_rectangle(
            (0, 0, size[0] - 1, size[1] - 1),
            radius=panel.corner_radius,
            fill=255,
        )
    else:
        mask_draw.rectangle((0, 0, size[0] - 1, size[1] - 1), fill=255)
    rendered.putalpha(ImageChops.multiply(rendered.getchannel("A"), mask))

    if panel.border_width:
        border_draw = ImageDraw.Draw(rendered)
        if panel.clip_polygon is not None:
            border_draw.line(
                polygon + [polygon[0]],
                fill=panel.border_color,
                width=panel.border_width,
                joint="curve",
            )
        else:
            inset = panel.border_width // 2
            border_draw.rounded_rectangle(
                (inset, inset, size[0] - 1 - inset, size[1] - 1 - inset),
                radius=max(0, panel.corner_radius - inset),
                outline=panel.border_color,
                width=panel.border_width,
            )
        rendered.putalpha(ImageChops.multiply(rendered.getchannel("A"), mask))

    if panel.rotation_degrees:
        rendered = rendered.rotate(
            -panel.rotation_degrees,
            resample=Image.Resampling.BICUBIC,
            expand=True,
        )
        center_x = (panel.frame[0] + panel.frame[2]) / 2.0
        center_y = (panel.frame[1] + panel.frame[3]) / 2.0
        destination = (
            int(round(center_x - rendered.width / 2.0)),
            int(round(center_y - rendered.height / 2.0)),
        )
    else:
        destination = (panel.frame[0], panel.frame[1])
    page.alpha_composite(rendered, dest=destination)


def render_panel(page: Image.Image, panel: PanelSpec) -> None:
    if panel.clip_polygon is not None or panel.rotation_degrees != 0.0:
        render_advanced_panel(page, panel)
        return
    with Image.open(io.BytesIO(panel.source_bytes)) as source:
        source.load()
        crop = source.convert("RGBA").crop(panel.source_crop)
    size = (panel.frame[2] - panel.frame[0], panel.frame[3] - panel.frame[1])
    resized = crop.resize(size, resample=Image.Resampling.LANCZOS, reducing_gap=3.0)
    if panel.corner_radius:
        rounded = Image.new("L", size, 0)
        ImageDraw.Draw(rounded).rounded_rectangle(
            (0, 0, size[0] - 1, size[1] - 1),
            radius=panel.corner_radius,
            fill=255,
        )
        alpha = resized.getchannel("A")
        resized.putalpha(ImageChops.multiply(alpha, rounded))
    page.alpha_composite(resized, dest=(panel.frame[0], panel.frame[1]))
    if panel.border_width:
        draw = ImageDraw.Draw(page)
        inset = panel.border_width // 2
        draw.rounded_rectangle(
            (
                panel.frame[0] + inset,
                panel.frame[1] + inset,
                panel.frame[2] - 1 - inset,
                panel.frame[3] - 1 - inset,
            ),
            radius=max(0, panel.corner_radius - inset),
            outline=panel.border_color,
            width=panel.border_width,
        )


def validate_glyphs(font: ImageFont.FreeTypeFont, exact: str, bubble_id: str) -> None:
    missing = missing_glyphs(font, exact)
    if missing:
        codepoints = ", ".join(f"U+{ord(character):04X}" for character in missing)
        fail(f"bubble {bubble_id!r}: font is missing glyphs {codepoints}")


def render_text(
    draw: ImageDraw.ImageDraw,
    bubble: dict[str, Any],
    font_bytes: bytes,
    face_index: int,
    color: tuple[int, int, int, int],
    scale: int,
) -> list[dict[str, Any]]:
    text = bubble["text"]
    assert text is not None
    font = ImageFont.truetype(
        io.BytesIO(font_bytes),
        text["font_size"] * scale,
        index=face_index,
        layout_engine=ImageFont.Layout.BASIC,
    )
    validate_glyphs(font, text["exact"], bubble["id"])
    box = scale_box(text["bbox"], scale)
    gap = text["line_gap"] * scale
    metrics = [draw.textbbox((0, 0), line, font=font) for line in text["lines"]]
    heights = [metric[3] - metric[1] for metric in metrics]
    total_height = sum(heights) + gap * (len(heights) - 1)
    available_height = box[3] - box[1]
    if total_height > available_height:
        fail(f"bubble {bubble['id']!r}: text is {total_height / scale:.1f}px tall but box is {available_height / scale:.1f}px")
    cursor_y = box[1] + (available_height - total_height) // 2
    rendered: list[dict[str, Any]] = []
    for line, metric, height in zip(text["lines"], metrics, heights):
        width = metric[2] - metric[0]
        if text["align"] == "left":
            ink_left = box[0]
        elif text["align"] == "right":
            ink_left = box[2] - width
        else:
            ink_left = box[0] + ((box[2] - box[0]) - width) // 2
        x = ink_left - metric[0]
        y = cursor_y - metric[1]
        ink = draw.textbbox((x, y), line, font=font)
        if not inside(ink, box):
            fail(
                f"bubble {bubble['id']!r}: line {line!r} ink box "
                f"{[round(value / scale, 2) for value in ink]} exceeds text bbox {list(text['bbox'])}"
            )
        draw.text((x, y), line, font=font, fill=color)
        rendered.append(
            {
                "text": line,
                "ink_bbox_overlay_pixels": list(ink),
            }
        )
        cursor_y += height + gap
    return rendered


def render_bubbles(
    page: Image.Image,
    manifest: ValidatedManifest,
) -> list[dict[str, Any]]:
    if not manifest.bubbles:
        return []
    size = (manifest.canvas_size[0] * OVERLAY_SCALE, manifest.canvas_size[1] * OVERLAY_SCALE)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    records: list[dict[str, Any]] = []
    for bubble in manifest.bubbles:
        origin, _, _, union = bubble_shape_masks(
            bubble["shape"],
            bubble["bbox"],
            bubble["corner_radius"],
            bubble["tail"],
            bubble["stroke_width"],
            bubble["tail_style"],
            bubble["tail_tip_trim"],
        )
        eroded = erode_mask(union, bubble["stroke_width"] * OVERLAY_SCALE)
        stroke_mask = ImageChops.subtract(union, eroded)
        silhouette = Image.new("RGBA", union.size, (0, 0, 0, 0))
        silhouette.paste(bubble["fill"], (0, 0), union)
        silhouette.paste(bubble["stroke"], (0, 0), stroke_mask)
        overlay.alpha_composite(
            silhouette,
            dest=(origin[0] * OVERLAY_SCALE, origin[1] * OVERLAY_SCALE),
        )
        text_records: list[dict[str, Any]] = []
        if bubble["text"] is not None:
            assert manifest.font_bytes is not None
            text_records = render_text(
                draw,
                bubble,
                manifest.font_bytes,
                manifest.font_face_index,
                manifest.font_color,
                OVERLAY_SCALE,
            )
        records.append(
            {
                "id": bubble["id"],
                "panel": bubble["panel"],
                "reading_order": bubble["reading_order"],
                "speaker": bubble["speaker"],
                "speaker_anchor": list(bubble["speaker_anchor"]),
                "shape": bubble["shape"],
                "bbox": list(bubble["bbox"]),
                "safe_region": list(bubble["safe_region"]),
                "allow_overlap_with": list(bubble["allow_overlap_with"]),
                "tail_style": bubble["tail_style"],
                "tail_tip_trim": bubble["tail_tip_trim"],
                "exact": bubble["text"]["exact"] if bubble["text"] is not None else None,
                "codepoints": (
                    [f"U+{ord(character):04X}" for character in bubble["text"]["exact"]]
                    if bubble["text"] is not None
                    else []
                ),
                "lines": text_records,
            }
        )
    overlay = overlay.resize(manifest.canvas_size, resample=Image.Resampling.LANCZOS)
    page.alpha_composite(overlay)
    return records


def runtime_ledger() -> dict[str, Any]:
    raster_libraries: dict[str, str] = {}
    for name in ("freetype2", "libjpeg_turbo", "jpg", "zlib"):
        version = features.version(name)
        if version is not None:
            raster_libraries[name] = str(version)
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "pillow_version": PIL.__version__,
        "raster_libraries": raster_libraries,
    }


def compose(manifest: ValidatedManifest) -> tuple[Image.Image, Image.Image, dict[str, Any]]:
    page = render_paper_matte(manifest.canvas_size, manifest.background, manifest.paper_matte)
    panel_records: list[dict[str, Any]] = []
    render_order = sorted(
        manifest.panels,
        key=lambda value: (value.z_index, value.reading_order),
    )
    for render_index, panel in enumerate(render_order, start=1):
        render_panel(page, panel)
        panel_records.append(
            {
                "id": panel.panel_id,
                "stage": manifest.input_stage,
                "reading_order": panel.reading_order,
                "render_order": render_index,
                "row": panel.row,
                "column": panel.column,
                "z_index": panel.z_index,
                "allow_overlap_with": list(panel.allow_overlap_with),
                "source": panel.source_label,
                "source_sha256": panel.source_sha256,
                "source_size": list(panel.source_size),
                "source_crop": list(panel.source_crop),
                "frame": list(panel.frame),
                "clip_polygon": (
                    [list(point) for point in panel.clip_polygon]
                    if panel.clip_polygon is not None
                    else None
                ),
                "final_polygon": [
                    [round(point[0], 6), round(point[1], 6)]
                    for point in panel.final_polygon
                ],
                "rotation_degrees": panel.rotation_degrees,
                "protected_action_regions": [
                    {"id": region_id, "bbox": list(region_bbox)}
                    for region_id, region_bbox in panel.protected_action_regions
                ],
                "resample": (
                    "Pillow LANCZOS; BICUBIC rotation"
                    if panel.rotation_degrees
                    else "Pillow LANCZOS"
                ),
            }
        )
    panel_records.sort(key=lambda record: record["reading_order"])
    unlettered_page = page.convert("RGB")
    bubble_records = render_bubbles(page, manifest)
    ledger: dict[str, Any] = {
        "schema_version": manifest.schema_version,
        "compositor_version": COMPOSITOR_VERSION,
        "pillow_version": PIL.__version__,
        "runtime": runtime_ledger(),
        "manifest_sha256": manifest.manifest_sha256,
        "input_stage": manifest.input_stage,
        "composition_stage": manifest.composition_stage,
        "output_stage": manifest.output_stage,
        "canvas_size": list(manifest.canvas_size),
        "paper_matte": (
            {
                "algorithm": "tiled-lcg-luminance-v1",
                "seed": manifest.paper_matte.seed,
                "grain_strength": manifest.paper_matte.grain_strength,
                "tile_size": manifest.paper_matte.tile_size,
            }
            if manifest.paper_matte is not None
            else None
        ),
        "overlay_supersample": OVERLAY_SCALE,
        "panels": panel_records,
        "bubbles": bubble_records,
        "font": None,
    }
    if manifest.font_bytes is not None:
        assert manifest.font_name is not None
        assert manifest.font_sha256 is not None
        ledger["font"] = {
            "file": manifest.font_name,
            "face_index": manifest.font_face_index,
            "sha256": manifest.font_sha256,
            "snapshot_bytes": len(manifest.font_bytes),
        }
    return unlettered_page, page.convert("RGB"), ledger


def ledger_path_label(path: Path, manifest_path: Path) -> str:
    try:
        return str(path.relative_to(manifest_path.parent))
    except ValueError:
        return str(path)


def commit_temporary(temporary: Path, path: Path, force: bool) -> None:
    if force:
        os.replace(temporary, path)
        return
    try:
        os.link(temporary, path)
    except FileExistsError:
        fail(f"refusing to overwrite existing output; pass --force: {path}")
    temporary.unlink()


def atomic_save_png(image: Image.Image, path: Path, force: bool) -> str:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        image.save(temporary, format="PNG", compress_level=9, optimize=False)
        output_sha256 = sha256(temporary)
        commit_temporary(temporary, path, force)
        return output_sha256
    finally:
        temporary.unlink(missing_ok=True)


def atomic_write_json(value: dict[str, Any], path: Path, force: bool) -> str:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        output_sha256 = sha256(temporary)
        commit_temporary(temporary, path, force)
        return output_sha256
    finally:
        temporary.unlink(missing_ok=True)


def dry_run_summary(manifest: ValidatedManifest) -> str:
    text_count = sum(1 for bubble in manifest.bubbles if bubble["text"] is not None)
    return (
        f"OK dry-run: canvas={manifest.canvas_size[0]}x{manifest.canvas_size[1]} "
        f"panels={len(manifest.panels)} bubbles={len(manifest.bubbles)} "
        f"zh-Hans_blocks={text_count} stage={manifest.output_stage} output={manifest.output_path}"
    )


def run(args: argparse.Namespace) -> int:
    manifest = validate_manifest(
        Path(args.manifest),
        args.font,
        args.output,
        args.ledger,
    )
    if args.dry_run:
        compose(manifest)
        print(dry_run_summary(manifest))
        return 0
    candidate_outputs = [manifest.output_path, manifest.ledger_path]
    if manifest.unlettered_path is not None:
        candidate_outputs.append(manifest.unlettered_path)
    existing = [path for path in candidate_outputs if path.exists()]
    if existing and not args.force:
        fail("refusing to overwrite existing output; pass --force: " + ", ".join(str(path) for path in existing))
    unlettered_page, final_page, ledger = compose(manifest)
    artifacts: list[dict[str, Any]] = []
    panel_ids = [panel.panel_id for panel in sorted(manifest.panels, key=lambda item: item.reading_order)]
    if manifest.unlettered_path is not None:
        unlettered_sha256 = atomic_save_png(
            unlettered_page,
            manifest.unlettered_path,
            args.force,
        )
        ledger["unlettered_sha256"] = unlettered_sha256
        artifacts.append(
            {
                "stage": manifest.composition_stage,
                "path": ledger_path_label(manifest.unlettered_path, manifest.manifest_path),
                "sha256": unlettered_sha256,
                "derived_from": panel_ids,
            }
        )
    ledger["output_sha256"] = atomic_save_png(final_page, manifest.output_path, args.force)
    artifacts.append(
        {
            "stage": manifest.output_stage,
            "path": ledger_path_label(manifest.output_path, manifest.manifest_path),
            "sha256": ledger["output_sha256"],
            "derived_from": (
                [ledger_path_label(manifest.unlettered_path, manifest.manifest_path)]
                if manifest.unlettered_path is not None
                else panel_ids
            ),
        }
    )
    ledger["artifacts"] = artifacts
    atomic_write_json(ledger, manifest.ledger_path, args.force)
    print(f"wrote {manifest.output_path} sha256={ledger['output_sha256']}")
    print(f"wrote {manifest.ledger_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render exact lettering onto one full page or reconstruct explicitly "
            "accepted comic panels from a validated JSON manifest."
        ),
    )
    parser.add_argument("--manifest", required=True, help="UTF-8 compositor manifest JSON")
    parser.add_argument("--font", help="override the first available manifest CJK font candidate")
    parser.add_argument("--output", help="override output.image")
    parser.add_argument("--ledger", help="override output.ledger")
    parser.add_argument("--dry-run", action="store_true", help="decode and validate all inputs without writing files")
    parser.add_argument("--force", action="store_true", help="replace existing output and ledger")
    return parser


def main() -> int:
    try:
        return run(build_parser().parse_args())
    except ManifestError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"error: filesystem operation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
