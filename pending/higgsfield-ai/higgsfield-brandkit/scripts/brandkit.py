#!/usr/bin/env python3
"""Deterministic Brandkit operations for a local agent workspace.

This script deliberately uses only the Python standard library plus the
ImageMagick and librsvg CLIs installed by the user. It owns
Brandkit's approval ledger, editable HTML review boards, and
geometry-preserving SVG/PNG logo exports. Files remain in the user's project.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import socket
import ssl
import subprocess
import tempfile
from typing import Any
import unicodedata
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener


MAX_SVG_BYTES = 256 * 1024
MAX_SVG_ELEMENTS = 500
MAX_REDIRECTS = 3
COMMAND_TIMEOUT_SECONDS = 60
HEX_RE = re.compile(r"^#[0-9a-f]{6}$", re.IGNORECASE)
SVG_ROOT_RE = re.compile(r"<svg\b([^>]*)>([\s\S]*)</svg>", re.IGNORECASE)
VIEWBOX_RE = re.compile(
    r"""\bviewBox\s*=\s*["']\s*
    (-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+
    (\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*["']""",
    re.IGNORECASE | re.VERBOSE,
)
COLOR_TOKEN = r"(?:#[0-9a-f]{3,8}|rgba?\([^)]*\)|black|white)"
PAINT_ATTRIBUTE_RE = re.compile(
    rf"""(\b(?:fill|stroke|stop-color|flood-color|lighting-color|color)\s*=\s*["'])({COLOR_TOKEN})(["'])""",
    re.IGNORECASE,
)
RECT_RE = re.compile(r"<rect\b[^>]*?/?>", re.IGNORECASE)
PATH_RE = re.compile(r"<path\b[^>]*?/?>", re.IGNORECASE)
STYLE_PAINT_RE = re.compile(
    rf"""((?:^|[;{{"']\s*)(?:fill|stroke|stop-color|flood-color|lighting-color|color)\s*:\s*)({COLOR_TOKEN})""",
    re.IGNORECASE,
)
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def tls_context() -> ssl.SSLContext:
    """Use OpenSSL defaults, then common OS CA bundles when Python lacks one."""
    context = ssl.create_default_context()
    if ssl.get_default_verify_paths().cafile:
        return context
    for candidate in (
        Path("/etc/ssl/cert.pem"),
        Path("/etc/ssl/certs/ca-certificates.crt"),
        Path("/etc/pki/tls/certs/ca-bundle.crt"),
    ):
        if candidate.is_file():
            context.load_verify_locations(cafile=str(candidate))
            break
    return context


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("input JSON must be an object")
    return value


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    result = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return (result[:60] or "brandkit")


def normalize_hex(value: str) -> str:
    normalized = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", normalized):
        normalized = "#" + "".join(character * 2 for character in normalized[1:])
    if not HEX_RE.fullmatch(normalized):
        raise RuntimeError(f"expected #RRGGBB color, got '{value}'")
    return normalized


def empty_state() -> dict[str, Any]:
    return {
        "brandbookElements": [],
        "essentialKitApproved": False,
        "version": 0,
    }


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_state()
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Brandkit state is not a JSON object")
    # One-way compatibility with the first script-only draft. New writes use
    # the exact former brandkit_handoff snapshot keys.
    if "brandbookElements" not in value and "brandbook_elements" in value:
        value["brandbookElements"] = value.pop("brandbook_elements")
    if "visualAxes" not in value and "visual_axes" in value:
        value["visualAxes"] = value.pop("visual_axes")
    value.pop("state_version", None)
    value.pop("essential_kit_approved", None)
    value.setdefault("brandbookElements", [])
    value.setdefault("version", 0)
    value["essentialKitApproved"] = all(
        value.get(slot) for slot in ("logo", "palette", "typography")
    )
    return value


def write_state(path: Path, state: dict[str, Any]) -> None:
    state["essentialKitApproved"] = all(
        state.get(slot) for slot in ("logo", "palette", "typography")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def state_status(state: dict[str, Any]) -> dict[str, Any]:
    axes = state.get("visualAxes")
    return {
        "brandbook_element_keys": [
            item.get("key")
            for item in state.get("brandbookElements", [])
            if isinstance(item, dict)
        ],
        "approved_slots": {
            slot: bool(state.get(slot)) for slot in ("logo", "palette", "typography")
        },
        "complete_kit": state.get("essentialKitApproved", False),
        "essential_kit": state.get("essentialKitApproved", False),
        "locked_slots": {
            slot: (
                state[slot].get("origin")
                if isinstance(state.get(slot), dict)
                else None
            )
            for slot in ("logo", "palette", "typography")
        },
        "logo_revision": state.get("logo", {}).get("revision"),
        "palette_revision": state.get("palette", {}).get("revision"),
        "typography_revision": state.get("typography", {}).get("revision"),
        "visual_axes": (
            {
                "familiar_experimental": axes.get("familiarExperimental"),
                "geometric_organic": axes.get("geometricOrganic"),
                "restrained_expressive": axes.get("restrainedExpressive"),
            }
            if isinstance(axes, dict)
            else None
        ),
        "version": state.get("version", 0),
    }


def require_object(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise RuntimeError(f"input requires object field '{key}'")
    return value


def next_revision(current: Any) -> int:
    if isinstance(current, dict) and isinstance(current.get("revision"), int):
        return current["revision"] + 1
    return 1


def normalize_font(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError("typography choices must be objects")
    family = str(value.get("family", "")).strip()
    source = str(value.get("source", "")).strip()
    if not family or not source:
        raise RuntimeError("typography choices require family and source")
    style = value.get("style", "normal")
    weight = value.get("weight", 400)
    if style not in {"normal", "italic"}:
        raise RuntimeError("font style must be normal or italic")
    if not isinstance(weight, int) or not 100 <= weight <= 900:
        raise RuntimeError("font weight must be an integer from 100 to 900")
    return {
        "family": family,
        "source": source,
        "style": style,
        "weight": weight,
    }


def normalize_asset(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError("Brandkit asset must be an object")
    asset_id = str(value.get("id", "")).strip()
    asset_path = str(value.get("path") or value.get("file") or "").strip()
    asset_url = str(value.get("url", "")).strip()
    if not asset_id and not asset_path and not asset_url:
        raise RuntimeError("Brandkit asset requires id, path, or url")
    result: dict[str, Any] = {}
    if asset_id:
        result["id"] = asset_id
    if asset_path:
        result["path"] = str(Path(asset_path).expanduser().resolve())
    if asset_url:
        result["url"] = asset_url
    for key in ("type",):
        if key in value and str(value[key]).strip():
            result[key] = value[key]
    return result


def normalize_slot(value: dict[str, Any], slot: str) -> dict[str, Any]:
    if slot == "logo":
        result = {
            "asset": normalize_asset(value.get("asset")),
            "name": str(value.get("name", "")).strip(),
        }
        if not result["name"]:
            raise RuntimeError("logo.name is required")
        if "geometry_fingerprint" in value:
            result["geometryFingerprint"] = value["geometry_fingerprint"]
        elif "geometryFingerprint" in value:
            result["geometryFingerprint"] = value["geometryFingerprint"]
        if "variants" in value:
            variants = require_object(value, "variants")
            result["variants"] = {
                "black": normalize_asset(variants.get("black")),
                "white": normalize_asset(variants.get("white")),
            }
        return result
    if slot == "palette":
        colors = value.get("colors")
        if not isinstance(colors, list) or not 2 <= len(colors) <= 12:
            raise RuntimeError("palette.colors must contain 2 to 12 colors")
        normalized_colors = []
        for item in colors:
            if not isinstance(item, dict):
                raise RuntimeError("palette colors must be objects")
            normalized_colors.append(
                {
                    "hex": normalize_hex(str(item.get("hex", ""))),
                    "name": str(item.get("name", "")).strip(),
                    **(
                        {"role": item["role"]}
                        if str(item.get("role", "")).strip()
                        else {}
                    ),
                }
            )
            if not normalized_colors[-1]["name"]:
                raise RuntimeError("palette color names are required")
        gradients = value.get("gradients", [])
        if not isinstance(gradients, list) or len(gradients) > 8:
            raise RuntimeError("palette.gradients must contain at most eight entries")
        normalized_gradients = []
        for gradient in gradients:
            if not isinstance(gradient, dict):
                raise RuntimeError("palette gradients must be objects")
            stops = gradient.get("stops")
            if not isinstance(stops, list) or not 2 <= len(stops) <= 6:
                raise RuntimeError("gradient stops must contain 2 to 6 colors")
            normalized_gradients.append(
                {
                    "name": str(gradient.get("name", "")).strip(),
                    "stops": [normalize_hex(str(stop)) for stop in stops],
                }
            )
            if not normalized_gradients[-1]["name"]:
                raise RuntimeError("gradient names are required")
        return {"colors": normalized_colors, "gradients": normalized_gradients}
    if slot == "typography":
        links = value.get("font_links", value.get("fontLinks", []))
        if not isinstance(links, list) or len(links) > 4:
            raise RuntimeError("typography font links must contain at most four URLs")
        return {
            "body": normalize_font(value.get("body")),
            "display": normalize_font(value.get("display")),
            "fontLinks": links,
            **(
                {"specimen": normalize_asset(value["specimen"])}
                if "specimen" in value
                else {}
            ),
        }
    raise RuntimeError(f"unsupported Brandkit slot: {slot}")


def dependency_key(slot: str) -> str:
    return f"{slot}Revision"


def invalidate_brandbook(
    state: dict[str, Any], slots: tuple[str, ...] = ("logo", "palette", "typography")
) -> list[str]:
    elements = state.get("brandbookElements", [])
    affected = [
        item
        for item in elements
        if isinstance(item, dict)
        and isinstance(item.get("dependencies"), dict)
        and any(dependency_key(slot) in item["dependencies"] for slot in slots)
    ]
    state["brandbookElements"] = [item for item in elements if item not in affected]
    return [str(item.get("key")) for item in affected]


def save_slot(
    state: dict[str, Any], payload: dict[str, Any], slot: str, authoritative: bool
) -> tuple[list[str], str | None]:
    current = state.get(slot)
    if (
        not authoritative
        and isinstance(current, dict)
        and current.get("origin") == "user_supplied"
    ):
        raise RuntimeError(
            f"approve_{slot} cannot replace the user-supplied official {slot}"
        )
    summary_key = "source_summary" if authoritative else "approval_summary"
    summary = str(payload.get(summary_key, "")).strip()
    if not summary:
        raise RuntimeError(f"input requires {summary_key}")
    value = normalize_slot(dict(require_object(payload, slot)), slot)
    value["approvalSummary"] = summary
    value["origin"] = "user_supplied" if authoritative else "brandkit_generated"
    value["revision"] = next_revision(current)
    invalidated = invalidate_brandbook(state, (slot,))
    invalidated_logo = None
    if slot == "palette":
        current_logo = state.get("logo")
        if (
            isinstance(current_logo, dict)
            and current_logo.get("origin") == "brandkit_generated"
        ):
            invalidated_logo = str(current_logo.get("name") or "generated logo")
            invalidated.extend(invalidate_brandbook(state, ("logo",)))
            state.pop("logo", None)
    if slot == "logo" and not authoritative:
        palette_revision = state.get("palette", {}).get("revision")
        if isinstance(palette_revision, int):
            value["paletteRevision"] = palette_revision
    state[slot] = value
    return sorted(set(invalidated)), invalidated_logo


def run_state(args: argparse.Namespace) -> dict[str, Any]:
    state_path = args.state_file.resolve()
    state = read_state(state_path)
    payload = load_json(args.input)
    action = args.action
    invalidated: list[str] = []

    if action == "get_status":
        return state_status(state)
    if action in {"get_logo", "get_palette", "get_typography"}:
        slot = action.removeprefix("get_")
        return {slot: state.get(slot)}
    if action == "get_visual_axes":
        axes = state.get("visualAxes")
        return {
            "visual_axes": (
                {
                    "familiar_experimental": axes.get("familiarExperimental"),
                    "geometric_organic": axes.get("geometricOrganic"),
                    "restrained_expressive": axes.get("restrainedExpressive"),
                }
                if isinstance(axes, dict)
                else None
            )
        }
    if action == "get_essential_kit":
        return {
            "approved_slots": {
                slot: bool(state.get(slot))
                for slot in ("logo", "palette", "typography")
            },
            "complete": state.get("essentialKitApproved", False),
            "logo": state.get("logo"),
            "palette": state.get("palette"),
            "typography": state.get("typography"),
            "visual_axes": state.get("visualAxes"),
            "version": state["version"],
            "approved": state.get("essentialKitApproved", False),
        }
    if action == "list_brandbook_elements":
        return {
            "elements": [
                {
                    key: item.get(key)
                    for key in ("key", "kind", "name", "revision")
                }
                for item in state.get("brandbookElements", [])
                if isinstance(item, dict)
            ]
        }
    if action == "get_brandbook_element":
        key = str(payload.get("key", "")).strip()
        item = next(
            (
                candidate
                for candidate in state.get("brandbookElements", [])
                if candidate.get("key") == key
            ),
            None,
        )
        return {"element": item}

    if action == "clear":
        state = {**empty_state(), "version": int(state.get("version", 0)) + 1}
        result: dict[str, Any] = {"cleared": True, "version": state["version"]}
    elif action == "set_visual_axes":
        axes = require_object(payload, "visual_axes")
        required = {
            "familiar_experimental",
            "geometric_organic",
            "restrained_expressive",
        }
        if set(axes) != required or any(
            not isinstance(value, (int, float)) or not 0 <= value <= 100
            for value in axes.values()
        ):
            raise RuntimeError(
                "visual_axes must contain exactly three numeric values from 0 to 100"
            )
        invalidated = invalidate_brandbook(state)
        state["visualAxes"] = {
            "familiarExperimental": axes["familiar_experimental"],
            "geometricOrganic": axes["geometric_organic"],
            "restrainedExpressive": axes["restrained_expressive"],
        }
        state["version"] = int(state.get("version", 0)) + 1
        result = {
            "invalidated_brandbook_elements": invalidated,
            "saved": "visual_axes",
            "version": state["version"],
        }
    elif action.startswith("lock_authoritative_"):
        slot = action.removeprefix("lock_authoritative_")
        invalidated, invalidated_logo = save_slot(
            state, payload, slot, True
        )
        state["version"] = int(state.get("version", 0)) + 1
        result = {
            "invalidated_brandbook_elements": invalidated,
            **(
                {"invalidated_generated_logo": invalidated_logo}
                if slot == "palette"
                else {}
            ),
            "revision": state[slot]["revision"],
            "saved": f"authoritative_{slot}",
            "version": state["version"],
        }
    elif action.startswith("approve_") and action in {
        "approve_logo",
        "approve_palette",
        "approve_typography",
    }:
        slot = action.removeprefix("approve_")
        invalidated, invalidated_logo = save_slot(
            state, payload, slot, False
        )
        state["version"] = int(state.get("version", 0)) + 1
        write_state(state_path, state)
        result = {
            "complete_kit": state["essentialKitApproved"],
            "invalidated_brandbook_elements": invalidated,
            **(
                {"invalidated_generated_logo": invalidated_logo}
                if slot == "palette"
                else {}
            ),
            "revision": state[slot]["revision"],
            "saved": slot,
            "version": state["version"],
        }
        return {**result, "state_snapshot": state}
    elif action == "approve_brandbook_element":
        raw_item = require_object(payload, "brandbook_element")
        item = {
            "asset": normalize_asset(raw_item.get("asset")),
            "key": str(raw_item.get("key", "")).strip(),
            "kind": str(raw_item.get("kind", "")).strip(),
            "name": str(raw_item.get("name", "")).strip(),
        }
        required_slots = payload.get(
            "required_slots", ["logo", "palette", "typography"]
        )
        if not isinstance(required_slots, list) or not required_slots or any(
            slot not in {"logo", "palette", "typography"}
            for slot in required_slots
        ):
            raise RuntimeError("required_slots must list the exact approved dependencies")
        missing = [slot for slot in required_slots if not state.get(slot)]
        if missing:
            raise RuntimeError("unapproved required slots: " + ", ".join(missing))
        key = item["key"]
        if not key:
            raise RuntimeError("brandbook_element.key is required")
        if not item["kind"] or not item["name"]:
            raise RuntimeError("brandbook_element.kind and name are required")
        current = next(
            (
                candidate
                for candidate in state.get("brandbookElements", [])
                if candidate.get("key") == key
            ),
            None,
        )
        item["revision"] = next_revision(current)
        approval_summary = str(payload.get("approval_summary", "")).strip()
        if not approval_summary:
            raise RuntimeError("input requires approval_summary")
        item["approvalSummary"] = approval_summary
        item["dependencies"] = {
            dependency_key(slot): state[slot]["revision"] for slot in required_slots
        }
        state["brandbookElements"] = [
            candidate
            for candidate in state.get("brandbookElements", [])
            if candidate.get("key") != key
        ] + [item]
        state["version"] = int(state.get("version", 0)) + 1
        result = {
            "key": key,
            "revision": item["revision"],
            "saved": "brandbook_element",
            "version": state["version"],
        }
    elif action == "remove_brandbook_element":
        key = str(payload.get("key", "")).strip()
        state["brandbookElements"] = [
            candidate
            for candidate in state.get("brandbookElements", [])
            if candidate.get("key") != key
        ]
        state["version"] = int(state.get("version", 0)) + 1
        result = {"removed": key, "version": state["version"]}
    else:
        raise RuntimeError(f"unsupported Brandkit state action: {action}")

    write_state(state_path, state)
    return {**result, "state_snapshot": state}


def assert_public_host(hostname: str) -> None:
    try:
        answers = socket.getaddrinfo(hostname, None)
    except socket.gaierror as error:
        raise RuntimeError(f"cannot resolve SVG host '{hostname}'") from error
    addresses = {answer[4][0] for answer in answers}
    if not addresses:
        raise RuntimeError(f"cannot resolve SVG host '{hostname}'")
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%", 1)[0])
        if not ip.is_global:
            raise RuntimeError(f"SVG host resolves to a non-public address: {address}")


def safe_fetch_svg(url: str) -> str:
    opener = build_opener(NoRedirect, HTTPSHandler(context=tls_context()))
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        parsed = urlparse(current)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username:
            raise RuntimeError("SVG URL must use https with a public host")
        assert_public_host(parsed.hostname)
        request = Request(
            current,
            headers={"Accept": "image/svg+xml", "User-Agent": "higgsfield-brandkit/1"},
        )
        try:
            response = opener.open(request, timeout=20)
        except HTTPError as error:
            if error.code in {301, 302, 303, 307, 308}:
                location = error.headers.get("Location")
                if not location:
                    raise RuntimeError("SVG redirect is missing Location") from error
                current = urljoin(current, location)
                continue
            raise RuntimeError(f"SVG download failed with HTTP {error.code}") from error
        content_type = response.headers.get_content_type()
        data = response.read(MAX_SVG_BYTES + 1)
        if len(data) > MAX_SVG_BYTES:
            raise RuntimeError(f"SVG exceeds {MAX_SVG_BYTES} bytes")
        if content_type not in {"image/svg+xml", "text/plain", "application/octet-stream"}:
            raise RuntimeError(f"SVG URL returned unsupported content type '{content_type}'")
        return data.decode("utf-8")
    raise RuntimeError("SVG URL redirected too many times")


def read_svg(source: str) -> str:
    stripped = source.strip()
    if stripped.startswith("<svg"):
        svg = stripped
    elif stripped.startswith("https://"):
        svg = safe_fetch_svg(stripped)
    else:
        path = Path(stripped).resolve()
        data = path.read_bytes()
        if len(data) > MAX_SVG_BYTES:
            raise RuntimeError(f"SVG exceeds {MAX_SVG_BYTES} bytes")
        svg = data.decode("utf-8")
    validate_svg(svg)
    return svg.strip()


def validate_svg(svg: str) -> tuple[str, str, tuple[float, float, float, float]]:
    if len(svg.encode("utf-8")) > MAX_SVG_BYTES:
        raise RuntimeError(f"SVG exceeds {MAX_SVG_BYTES} bytes")
    if re.search(r"<!DOCTYPE|<!ENTITY", svg, re.IGNORECASE):
        raise RuntimeError("SVG doctypes and entities are not allowed")
    if re.search(
        r"<(?:script|foreignObject|iframe|object|embed|image)\b",
        svg,
        re.IGNORECASE,
    ):
        raise RuntimeError("SVG active or embedded content is not allowed")
    if re.search(r"\son[a-z]+\s*=", svg, re.IGNORECASE):
        raise RuntimeError("SVG event handlers are not allowed")
    if re.search(r"(?:href|xlink:href)\s*=\s*[\"'](?!#)[^\"']+", svg, re.IGNORECASE):
        raise RuntimeError("SVG external references are not allowed")
    if re.search(r"url\(\s*[\"']?(?:https?:|data:|file:)|@import", svg, re.IGNORECASE):
        raise RuntimeError("SVG external CSS resources are not allowed")
    if len(re.findall(r"<[a-z][^>]*>", svg, re.IGNORECASE)) > MAX_SVG_ELEMENTS:
        raise RuntimeError(f"SVG exceeds {MAX_SVG_ELEMENTS} elements")
    root = SVG_ROOT_RE.search(svg)
    if not root:
        raise RuntimeError("expected a complete <svg> document")
    viewbox = VIEWBOX_RE.search(root.group(1))
    if not viewbox:
        raise RuntimeError("SVG must declare a numeric viewBox")
    values = tuple(float(value) for value in viewbox.groups())
    if values[2] <= 0 or values[3] <= 0 or values[2] > 10000 or values[3] > 10000:
        raise RuntimeError("SVG viewBox is invalid or too large")
    return root.group(1), root.group(2), values


def color_channel(value: str) -> int:
    stripped = value.strip()
    parsed = float(stripped.removesuffix("%"))
    scaled = parsed * 2.55 if stripped.endswith("%") else parsed
    return max(0, min(255, round(scaled)))


def alpha_channel(value: str | None) -> float | None:
    if value is None:
        return None
    stripped = value.strip()
    parsed = float(stripped.removesuffix("%"))
    scaled = parsed / 100 if stripped.endswith("%") else parsed
    return max(0, min(1, scaled))


def parse_paint(value: str) -> tuple[str, float | None]:
    normalized = value.strip().lower()
    if normalized == "black":
        return "#000000", None
    if normalized == "white":
        return "#ffffff", None
    if normalized.startswith("#"):
        raw = normalized[1:]
        if len(raw) in {3, 4}:
            raw = "".join(character * 2 for character in raw)
        if len(raw) not in {6, 8}:
            raise RuntimeError(f"unsupported hex color '{value}'")
        alpha = int(raw[6:8], 16) / 255 if len(raw) == 8 else None
        return f"#{raw[:6]}", alpha
    functional = re.fullmatch(r"rgba?\((.*)\)", normalized)
    if not functional:
        raise RuntimeError(f"unsupported SVG color '{value}'")
    parts = [
        part
        for part in re.sub(r"/", " ", functional.group(1)).replace(",", " ").split()
        if part
    ]
    if len(parts) not in {3, 4}:
        raise RuntimeError(f"unsupported SVG color '{value}'")
    channels = [color_channel(part) for part in parts[:3]]
    alpha = alpha_channel(parts[3] if len(parts) == 4 else None)
    return "#" + "".join(f"{channel:02x}" for channel in channels), alpha


def replacement_paint(target: str, alpha: float | None) -> str:
    normalized = normalize_hex(target)
    if alpha is None or alpha >= 1:
        return normalized
    integer = int(normalized[1:], 16)
    red = integer // 65536 % 256
    green = integer // 256 % 256
    blue = integer % 256
    alpha_text = f"{alpha:.4f}".rstrip("0").rstrip(".")
    return f"rgba({red},{green},{blue},{alpha_text})"


def color_distance(first: str, second: str) -> float:
    left = int(normalize_hex(first)[1:], 16)
    right = int(normalize_hex(second)[1:], 16)
    left_channels = (left // 65536 % 256, left // 256 % 256, left % 256)
    right_channels = (right // 65536 % 256, right // 256 % 256, right % 256)
    return sum(
        (left_channel - right_channel) ** 2
        for left_channel, right_channel in zip(left_channels, right_channels)
    ) ** 0.5


def ordered_paint_colors(svg: str) -> list[str]:
    colors: list[str] = []
    for pattern in (PAINT_ATTRIBUTE_RE, STYLE_PAINT_RE):
        for match in pattern.finditer(svg):
            parsed, _ = parse_paint(match.group(2))
            if parsed not in colors:
                colors.append(parsed)
    return colors


def nearest_paint(colors: list[str], requested: str) -> tuple[str, float] | None:
    if not colors:
        return None
    return min(
        ((candidate, color_distance(candidate, requested)) for candidate in colors),
        key=lambda item: item[1],
    )


def recolor_svg(
    svg: str, replacements: list[dict[str, str]]
) -> tuple[str, int, list[str]]:
    colors = ordered_paint_colors(svg)
    mapping: dict[str, str] = {}
    for item in replacements:
        source = normalize_hex(str(item.get("from", "")))
        target = normalize_hex(str(item.get("to", "")))
        nearest = nearest_paint(colors, source)
        if nearest and nearest[1] <= 32:
            mapping[nearest[0]] = target
    changed = 0
    unmatched: set[str] = set()

    def replace_value(value: str) -> str:
        nonlocal changed
        source, alpha = parse_paint(value)
        target = mapping.get(source)
        if target is None:
            unmatched.add(source)
            return value
        changed += 1
        return replacement_paint(target, alpha)

    def replace_attribute(match: re.Match[str]) -> str:
        return match.group(1) + replace_value(match.group(2)) + match.group(3)

    result = PAINT_ATTRIBUTE_RE.sub(replace_attribute, svg)

    def replace_style(match: re.Match[str]) -> str:
        return match.group(1) + replace_value(match.group(2).strip())

    result = re.sub(
        r"""(\bstyle\s*=\s*["'])([^"']*)(["'])""",
        lambda outer: outer.group(1)
        + STYLE_PAINT_RE.sub(replace_style, outer.group(2))
        + outer.group(3),
        result,
        flags=re.IGNORECASE,
    )
    return result, changed, sorted(unmatched)


def geometry_fingerprint(svg: str) -> str:
    neutral = PAINT_ATTRIBUTE_RE.sub(
        lambda match: (
            match.group(1)
            + replacement_paint("#000000", parse_paint(match.group(2))[1])
            + match.group(3)
        ),
        svg,
    )
    neutral = re.sub(
        r"""(\bstyle\s*=\s*["'])([^"']*)(["'])""",
        lambda outer: outer.group(1)
        + STYLE_PAINT_RE.sub(
            lambda match: (
                match.group(1)
                + replacement_paint("#000000", parse_paint(match.group(2))[1])
            ),
            outer.group(2),
        )
        + outer.group(3),
        neutral,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(r"\s+", " ", neutral).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def source_colors(svg: str) -> list[str]:
    return ordered_paint_colors(svg)


def run_logo_inspect(args: argparse.Namespace) -> dict[str, Any]:
    original = read_svg(args.source)
    canonical, background_removed = strip_full_canvas_background(original)
    return {
        "background_removed": background_removed,
        "geometry_fingerprint": geometry_fingerprint(canonical),
        "source_colors": source_colors(canonical),
    }


def monochrome_svg(svg: str, target: str) -> tuple[str, int]:
    colors = ordered_paint_colors(svg)
    if not colors:
        raise RuntimeError("approved SVG has no exact color tokens to monochromize")
    output, changed, _ = recolor_svg(
        svg, [{"from": source, "to": target} for source in colors]
    )
    return output, changed


def tonal_monochrome_svg(
    svg: str, mode: str, primary_color: str | None
) -> tuple[str, int, str, str]:
    colors = ordered_paint_colors(svg)
    if not colors:
        raise RuntimeError("approved SVG has no exact color tokens to monochromize")
    nearest = nearest_paint(colors, primary_color) if primary_color else None
    primary = nearest[0] if nearest else colors[0]
    main = "#000000" if mode == "black" else "#ffffff"
    detail = "#707070" if mode == "black" else "#b8b8b8"
    output, changed, _ = recolor_svg(
        svg,
        [
            {"from": source, "to": main if source == primary else detail}
            for source in colors
        ],
    )
    return output, changed, detail, primary


def attribute_value(markup: str, name: str) -> str | None:
    match = re.search(
        rf"""\b{re.escape(name)}\s*=\s*["']([^"']+)["']""",
        markup,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def matches_dimension(
    value: str | None, expected: float, default_value: float | None = None
) -> bool:
    if value is None:
        return default_value is not None and abs(default_value - expected) < 0.01
    if value.strip() == "100%":
        return True
    try:
        return abs(float(value) - expected) < 0.01
    except ValueError:
        return False


def make_element_transparent(element: str) -> str:
    if re.search(r"""\bfill\s*=\s*["'][^"']*["']""", element, re.IGNORECASE):
        return re.sub(
            r"""\bfill\s*=\s*["'][^"']*["']""",
            'fill="none"',
            element,
            count=1,
            flags=re.IGNORECASE,
        )
    if re.search(r"""\bstyle\s*=\s*["'][^"']*\bfill\s*:""", element, re.IGNORECASE):
        return re.sub(
            r"""(\bstyle\s*=\s*["'][^"']*?)\bfill\s*:\s*[^;"']+""",
            r"\1fill:none",
            element,
            count=1,
            flags=re.IGNORECASE,
        )
    return re.sub(r"\s*/?>$", lambda match: f' fill="none"{match.group(0)}', element)


def path_bounds(markup: str) -> tuple[float, float, float, float, bool] | None:
    """Bounds for the restricted M/L/H/V/Z path subset Recraft uses for backgrounds."""
    data = attribute_value(markup, "d")
    if not data:
        return None
    tokens = re.findall(
        r"[a-z]|[-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?",
        data,
        re.IGNORECASE,
    )
    command = ""
    index = 0
    x = y = start_x = start_y = 0.0
    closed = False
    points: list[tuple[float, float]] = []

    def number() -> float | None:
        nonlocal index
        if index >= len(tokens) or re.fullmatch(r"[a-z]", tokens[index], re.IGNORECASE):
            return None
        value = float(tokens[index])
        index += 1
        return value

    while index < len(tokens):
        if re.fullmatch(r"[a-z]", tokens[index], re.IGNORECASE):
            command = tokens[index]
            index += 1
        if not command:
            return None
        if command.lower() == "z":
            x, y = start_x, start_y
            points.append((x, y))
            closed = True
            command = ""
            continue
        if command not in {"m", "M", "l", "L", "h", "H", "v", "V"}:
            return None
        relative = command.islower()
        if command.lower() in {"m", "l"}:
            next_x = number()
            next_y = number()
            if next_x is None or next_y is None:
                return None
            x = x + next_x if relative else next_x
            y = y + next_y if relative else next_y
            if command.lower() == "m":
                start_x, start_y = x, y
                command = "l" if relative else "L"
        else:
            value = number()
            if value is None:
                return None
            if command.lower() == "h":
                x = x + value if relative else value
            else:
                y = y + value if relative else value
        points.append((x, y))
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys), closed


def full_canvas_path(
    markup: str, viewbox: tuple[float, float, float, float]
) -> bool:
    bounds = path_bounds(markup)
    if not bounds or not bounds[4]:
        return False
    min_x, min_y, max_x, max_y, _ = bounds
    x, y, width, height = viewbox
    return (
        abs(min_x - x) < 0.01
        and abs(min_y - y) < 0.01
        and abs(max_x - (x + width)) < 0.01
        and abs(max_y - (y + height)) < 0.01
    )


def strip_full_canvas_background(svg: str) -> tuple[str, bool]:
    _, _, viewbox = validate_svg(svg)
    x, y, width, height = viewbox
    for match in RECT_RE.finditer(svg):
        rect = match.group(0)
        if (
            matches_dimension(attribute_value(rect, "x"), x, 0)
            and matches_dimension(attribute_value(rect, "y"), y, 0)
            and matches_dimension(attribute_value(rect, "width"), width)
            and matches_dimension(attribute_value(rect, "height"), height)
        ):
            return svg.replace(rect, make_element_transparent(rect), 1), True
    for match in PATH_RE.finditer(svg):
        background = match.group(0)
        if full_canvas_path(background, viewbox):
            return svg.replace(
                background, make_element_transparent(background), 1
            ), True
    return svg, False


def write_logo_pair(
    output_dir: Path, stem: str, suffix: str, svg: str
) -> dict[str, Any]:
    image_magick = shutil.which("magick") or shutil.which("convert")
    rsvg_convert = shutil.which("rsvg-convert")
    if not image_magick:
        raise RuntimeError("ImageMagick is unavailable in the local environment")
    if not rsvg_convert:
        raise RuntimeError("rsvg-convert is unavailable in the local environment")
    svg_path = output_dir / f"{stem}{suffix}.svg"
    png_path = output_dir / f"{stem}{suffix}-2048.png"
    svg_path.write_text(svg + "\n", encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="brandkit-logo-") as directory:
        raster = Path(directory) / "raster.png"
        subprocess.run(
            [
                rsvg_convert,
                "--format",
                "png",
                "--width",
                "2048",
                "--height",
                "2048",
                "--keep-aspect-ratio",
                "--output",
                str(raster),
                str(svg_path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
        subprocess.run(
            [
                image_magick,
                "-background",
                "none",
                str(raster),
                "-resize",
                "2048x2048",
                "-gravity",
                "center",
                "-extent",
                "2048x2048",
                str(png_path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    return {
        "png": str(png_path.resolve()),
        "svg": str(svg_path.resolve()),
    }


def run_logo(args: argparse.Namespace) -> dict[str, Any]:
    payload = load_json(args.input)
    source = str(payload.get("logo_svg", "")).strip()
    name = str(payload.get("name", "brandkit-logo"))
    if not source:
        raise RuntimeError("input requires logo_svg")
    svg, background_removed = strip_full_canvas_background(read_svg(source))
    before = geometry_fingerprint(svg)
    replacements_value = payload.get("replacements", [])
    if not isinstance(replacements_value, list):
        raise RuntimeError("replacements must be an array")
    replacements: list[dict[str, str]] = []
    for item in replacements_value:
        if not isinstance(item, dict):
            raise RuntimeError("each replacement must be an object")
        replacements.append(
            {
                "from": normalize_hex(str(item.get("from", ""))),
                "to": normalize_hex(str(item.get("to", ""))),
            }
        )
    color_svg, changed, unmatched = (
        recolor_svg(svg, replacements) if replacements else (svg, 0, [])
    )
    if replacements and changed == 0:
        raise RuntimeError(
            "no requested source colors matched; available source colors: "
            + ", ".join(source_colors(svg))
        )
    if geometry_fingerprint(color_svg) != before:
        raise RuntimeError("logo export changed SVG geometry")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = slug(name)
    variants: dict[str, Any] = {
        "color": write_logo_pair(output_dir, stem, "", color_svg)
    }
    monochrome_tokens: dict[str, int] = {}
    monochrome_details: dict[str, str] = {}
    primary_sources: dict[str, str] = {}
    if payload.get("include_monochrome") is True:
        primary_color = (
            normalize_hex(str(payload["primary_color"]))
            if payload.get("primary_color")
            else None
        )
        if primary_color:
            replacement = next(
                (
                    item["to"]
                    for item in replacements
                    if item["from"] == primary_color
                ),
                None,
            )
            primary_color = replacement or primary_color
        black_svg, black_changed, black_detail, black_primary = tonal_monochrome_svg(
            color_svg, "black", primary_color
        )
        white_svg, white_changed, white_detail, white_primary = tonal_monochrome_svg(
            color_svg, "white", primary_color
        )
        variants["black"] = write_logo_pair(output_dir, stem, "-black", black_svg)
        variants["white"] = write_logo_pair(output_dir, stem, "-white", white_svg)
        monochrome_tokens = {
            "black": black_changed,
            "white": white_changed,
        }
        monochrome_details = {
            "black": black_detail,
            "white": white_detail,
        }
        primary_sources = {
            "black": black_primary,
            "white": white_primary,
        }
    single_changed: int | None = None
    if payload.get("single_color"):
        target = normalize_hex(str(payload["single_color"]))
        single_svg, single_changed = monochrome_svg(color_svg, target)
        variants["single_color"] = {
            **write_logo_pair(output_dir, stem, "-single-color", single_svg),
            "color": target,
        }
    for variant in variants.values():
        if geometry_fingerprint(Path(variant["svg"]).read_text(encoding="utf-8")) != before:
            raise RuntimeError("logo export changed SVG geometry")
    files = [
        path
        for variant in variants.values()
        for path in (variant["svg"], variant["png"])
    ]
    return {
        "action": "export",
        "available_source_colors": source_colors(svg),
        "background_removed": background_removed,
        "changed_color_tokens": changed,
        "delivery": payload.get("delivery", "internal"),
        "files": files,
        "geometry_fingerprint": before,
        "internal_assets": files,
        **(
            {
                "monochrome_color_tokens": monochrome_tokens,
                "monochrome_detail_colors": monochrome_details,
                "primary_source_colors": primary_sources,
            }
            if monochrome_tokens
            else {}
        ),
        "png_size": {"height": 2048, "width": 2048},
        **(
            {"single_color_tokens": single_changed}
            if single_changed is not None
            else {}
        ),
        "unmatched_colors": unmatched,
        "variants": variants,
    }


def font_css(font: dict[str, Any], default_family: str) -> tuple[str, str]:
    family = str(font.get("family", default_family))
    source = str(font.get("source", ""))
    weight = int(font.get("weight", 400))
    if source.startswith("google:"):
        google_family = source.removeprefix("google:").strip() or family
        encoded = google_family.replace(" ", "+")
        css = (
            '@import url("https://fonts.googleapis.com/css2?family='
            f"{html.escape(encoded)}:wght@{weight}&display=swap\");"
        )
    elif source.startswith("https://"):
        css = (
            "@font-face{font-family:"
            + json.dumps(family)
            + ";src:url("
            + json.dumps(source)
            + f");font-weight:{weight};font-style:normal;font-display:swap}}"
        )
    elif source:
        path = Path(source).expanduser().resolve()
        if path.is_file():
            css = (
                "@font-face{font-family:"
                + json.dumps(family)
                + ";src:url("
                + json.dumps(path.as_uri())
                + f");font-weight:{weight};font-style:normal;font-display:swap}}"
            )
        else:
            css = ""
    else:
        css = ""
    return css, family


def logo_markup(source: str | None) -> str:
    if not source:
        return ""
    svg = read_svg(source)
    attributes, body, viewbox = validate_svg(svg)
    del attributes
    box = " ".join(f"{value:g}" for value in viewbox)
    return (
        f'<svg class="logo" viewBox="{box}" aria-label="Selected logo">'
        + body
        + "</svg>"
    )


def build_review_html(review: dict[str, Any]) -> str:
    stage = str(review.get("stage", ""))
    if stage not in {"palette", "typography", "essential"}:
        raise RuntimeError("review.stage must be palette, typography, or essential")
    name = str(review.get("name", "")).strip()
    premise = str(review.get("premise", "")).strip()
    if not name or not premise:
        raise RuntimeError("review requires name and premise")
    background = normalize_hex(str(review.get("background_color", "")))
    text = normalize_hex(str(review.get("text_color", "")))
    if background == text:
        raise RuntimeError(f"review '{name}' text and background colors must differ")
    palette = review.get("palette", [])
    if not isinstance(palette, list) or len(palette) > 8:
        raise RuntimeError("review.palette must contain at most eight entries")
    swatches = "".join(
        '<li><span style="background:'
        + normalize_hex(str(item["hex"]))
        + '"></span><strong>'
        + html.escape(str(item["name"]))
        + "</strong><code>"
        + normalize_hex(str(item["hex"])).upper()
        + "</code></li>"
        for item in palette
        if isinstance(item, dict) and "hex" in item and "name" in item
    )
    ideas = "".join(
        "<li>" + html.escape(str(idea)) + "</li>"
        for idea in review.get("logo_ideas", [])
    )
    display_css, display_family = font_css(
        review.get("display_font", {}), "Arial"
    )
    body_css, body_family = font_css(review.get("body_font", {}), "Arial")
    display_stack = json.dumps(display_family) + ",sans-serif"
    body_stack = json.dumps(body_family) + ",sans-serif"
    logo = logo_markup(review.get("logo_svg"))
    overview = ""
    if swatches or logo or ideas:
        overview = '<div class="layout">'
        if swatches:
            overview += f"<section><h2>Palette</h2><ul class=\"swatches\">{swatches}</ul></section>"
        if logo or ideas:
            overview += f"<aside>{logo}"
            if ideas:
                overview += f"<h2>Logo ideas</h2><ul class=\"ideas\">{ideas}</ul>"
            overview += "</aside>"
        overview += "</div>"
    specimen = ""
    if stage != "palette":
        headline = html.escape(str(review.get("headline", "")))
        body = html.escape(str(review.get("body", "")))
        if not headline or not body:
            raise RuntimeError(f"{stage} review '{name}' requires headline and body")
        specimen = (
            '<section class="specimen"><div class="eyebrow">'
            + html.escape(display_family)
            + " + "
            + html.escape(body_family)
            + f'</div><p class="headline">{headline}</p><p class="body-copy">{body}</p></section>'
        )
    note = {
        "palette": "Editable palette draft. Colors and logo directions remain changeable until selection.",
        "typography": "Editable typography draft. This type pair remains changeable until selection.",
        "essential": "Combined presentation of the separately approved logo, palette, and typography.",
    }[stage]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(name)} — Brandkit draft</title>
<style>{display_css}
{body_css}
:root{{--bg:{background};--text:{text}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:{body_stack}}}
main{{max-width:1000px;margin:auto;padding:36px}}.eyebrow{{font:600 11px/1 sans-serif;letter-spacing:.13em;text-transform:uppercase}}
h1{{margin:9px 0 6px;font:700 38px/1.05 {display_stack}}}.premise{{max-width:700px;margin:0;font-size:16px;line-height:1.45}}
.layout{{display:grid;grid-template-columns:1.45fr .85fr;gap:28px;margin-top:28px}}.layout h2{{margin:0 0 12px;font-size:18px}}
.logo{{width:100%;max-height:180px;object-fit:contain}}.swatches{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:0;list-style:none}}
.swatches li{{display:grid;gap:5px}}.swatches span{{display:block;height:64px;border:1px solid color-mix(in srgb,var(--text) 18%,transparent)}}code{{font-size:11px}}
.specimen{{margin-top:28px;padding-top:22px}}.headline{{margin:8px 0 0;color:var(--text);font:700 52px/1.05 {display_stack}}}
.body-copy{{max-width:760px;margin:14px 0 0;font:400 18px/1.4 {body_stack}}}.ideas{{margin:0;padding-left:18px}}.ideas li+li{{margin-top:6px}}
.note{{margin:28px 0 0;font-size:12px;opacity:.7}}@media(max-width:800px){{main{{padding:24px}}.layout{{grid-template-columns:1fr}}.swatches{{grid-template-columns:repeat(2,1fr)}}.headline{{font-size:40px}}}}
</style></head><body><main><div class="eyebrow">{html.escape(stage)} review</div>
<h1>{html.escape(name)}</h1><p class="premise">{html.escape(premise)}</p>
{overview}{specimen}<p class="note">{html.escape(note)}</p></main></body></html>"""


def run_preview(args: argparse.Namespace) -> dict[str, Any]:
    payload = load_json(args.input)
    reviews = payload.get("reviews")
    if not isinstance(reviews, list) or not 1 <= len(reviews) <= 3:
        raise RuntimeError("input requires one to three reviews")
    typography_pairs: set[str] = set()
    for review in reviews:
        if not isinstance(review, dict):
            raise RuntimeError("each review must be an object")
        stage = review.get("stage")
        palette = review.get("palette", [])
        keywords = review.get("keywords")
        logo_ideas = review.get("logo_ideas", [])
        if not isinstance(keywords, list) or not 1 <= len(keywords) <= 5:
            raise RuntimeError("each review requires one to five keywords")
        if not isinstance(palette, list) or len(palette) > 8:
            raise RuntimeError("review.palette must contain at most eight entries")
        if stage == "palette":
            if not 2 <= len(palette) <= 8 or not isinstance(
                logo_ideas, list
            ) or not 2 <= len(logo_ideas) <= 3:
                raise RuntimeError(
                    f"palette review '{review.get('name', '')}' requires 2-8 palette colors and 2-3 logo_ideas"
                )
        elif stage == "typography":
            if not all(
                review.get(key)
                for key in ("display_font", "body_font", "headline", "body")
            ):
                raise RuntimeError(
                    f"typography review '{review.get('name', '')}' requires display_font, body_font, headline, and body"
                )
            pair = "|".join(
                sorted(
                    str(review[key].get("family", "")).strip().lower()
                    for key in ("display_font", "body_font")
                )
            )
            if pair in typography_pairs:
                raise RuntimeError(
                    f"duplicate typography pair in '{review.get('name', '')}'"
                )
            typography_pairs.add(pair)
        elif stage == "essential":
            if not (
                all(
                    review.get(key)
                    for key in (
                        "display_font",
                        "body_font",
                        "logo_svg",
                        "headline",
                        "body",
                    )
                )
                and len(palette) >= 2
            ):
                raise RuntimeError(
                    f"essential review '{review.get('name', '')}' requires logo, palette, display/body fonts, headline, and body"
                )
        else:
            raise RuntimeError("review.stage must be palette, typography, or essential")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for index, review in enumerate(reviews, start=1):
        path = output_dir / f"brandkit-review-{index}-{slug(str(review.get('name', 'option')))}.html"
        path.write_text(build_review_html(review), encoding="utf-8")
        files.append(
            {
                "file": str(path),
                "name": review.get("name"),
                "stage": review.get("stage"),
            }
        )
    return {
        "files": files,
        "next": "Screenshot each HTML board per references/inline-widgets.md, then show the local PNG previews with editable HTML paths.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    state = commands.add_parser("state")
    state.add_argument("--action", required=True)
    state.add_argument("--input", type=Path)
    state.add_argument("--state-file", type=Path, default=Path("brandkit/state.json"))

    preview = commands.add_parser("preview")
    preview.add_argument("--input", required=True, type=Path)
    preview.add_argument("--output-dir", type=Path, default=Path("brandkit/reviews"))

    logo = commands.add_parser("logo-export")
    logo.add_argument("--input", required=True, type=Path)
    logo.add_argument("--output-dir", type=Path, default=Path("brandkit/logo"))
    inspect_logo = commands.add_parser("logo-inspect")
    inspect_logo.add_argument("--source", required=True)
    brandbook = commands.add_parser("brandbook-build")
    brandbook.add_argument("--input", required=True, type=Path)
    brandbook.add_argument(
        "--state-file", type=Path, default=Path("brandkit/state.json")
    )
    brandbook.add_argument(
        "--output-dir", type=Path, default=Path("brandkit/brandbook")
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "state":
        result = run_state(args)
    elif args.command == "preview":
        result = run_preview(args)
    elif args.command == "brandbook-build":
        from build_brandbook import build

        result = build(args)
    elif args.command == "logo-inspect":
        result = run_logo_inspect(args)
    else:
        result = run_logo(args)
    print(compact(result))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        detail = (error.stdout or "").strip()
        print(detail or str(error), file=os.sys.stderr)
        raise SystemExit(1) from error
    except Exception as error:
        print(str(error), file=os.sys.stderr)
        raise SystemExit(1) from error
