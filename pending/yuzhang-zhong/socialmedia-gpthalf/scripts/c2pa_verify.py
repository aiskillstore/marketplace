"""Local, best-effort C2PA verification with minimal retained metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


GENERATED_TYPES = {"trainedalgorithmicmedia"}
GENERATIVE_EDIT_TYPES = {
    "compositewithtrainedalgorithmicmedia",
    "compositedwithtrainedalgorithmicmedia",  # legacy C2PA guidance spelling
}
ALGORITHMIC_NON_GENERATIVE_TYPES = {
    "algorithmicallyenhanced",
    "algorithmicmedia",
}


def _collect_statuses(value: Any) -> list[dict]:
    statuses: list[dict] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "validation_status" and isinstance(child, list):
                for item in child:
                    if isinstance(item, dict):
                        statuses.append(
                            {
                                "code": str(item.get("code") or ""),
                                "explanation": str(item.get("explanation") or "")[:300],
                            }
                        )
            else:
                statuses.extend(_collect_statuses(child))
    elif isinstance(value, list):
        for child in value:
            statuses.extend(_collect_statuses(child))
    return statuses


def _source_type_tokens(value: Any) -> set[str]:
    """Extract exact controlled-vocabulary identifiers from common JSON forms."""

    rendered: list[str] = []
    if isinstance(value, str):
        rendered.append(value)
    elif isinstance(value, dict):
        for key in ("uri", "url", "id", "identifier", "value", "literal", "qcode"):
            child = value.get(key)
            if isinstance(child, str):
                rendered.append(child)
    elif isinstance(value, list):
        for child in value:
            rendered.extend(_source_type_tokens(child))

    tokens: set[str] = set()
    for item in rendered:
        leaf = re.split(r"[/#:]+", item.strip())[-1]
        normalized = re.sub(r"[^a-z0-9]", "", leaf.casefold())
        if normalized:
            tokens.add(normalized)
    return tokens


def _classify_source_type(token: str) -> str:
    if token in GENERATED_TYPES:
        return "generated"
    if token in GENERATIVE_EDIT_TYPES:
        return "generative_edit"
    if token in ALGORITHMIC_NON_GENERATIVE_TYPES:
        return "non_generative_algorithmic"
    return "unknown"


TRUSTED_ASSERTION_LABELS = {
    "c2pametadata",
    "stdsiptcphotometadata",
}


def _trusted_assertion_label(label: str) -> bool:
    return label in TRUSTED_ASSERTION_LABELS or bool(
        re.fullmatch(r"c2paactions(?:v\d+)?", label)
    )


def _append_source_types(findings: list[dict], value: Any, path: str) -> None:
    for token in sorted(_source_type_tokens(value)):
        findings.append(
            {
                "manifest_path": path,
                "source_type": token,
                "category": _classify_source_type(token),
            }
        )


def _collect_source_assertions(value: Any, path: str = "$") -> list[dict]:
    """Read only standardized, asset-level assertion fields.

    Trust never propagates recursively: an extension object or ingredient may
    itself contain a field called digitalSourceType, but that does not scope it
    to the active asset.
    """

    findings: list[dict] = []
    if not isinstance(value, dict):
        return findings
    assertions = value.get("assertions")
    if not isinstance(assertions, list):
        return findings
    for index, assertion in enumerate(assertions):
        if not isinstance(assertion, dict):
            continue
        assertion_path = f"{path}.assertions[{index}]"
        label = re.sub(r"[^a-z0-9]", "", str(assertion.get("label") or "").casefold())
        data = assertion.get("data")
        if not isinstance(data, dict) or "ingredient" in label:
            continue
        if re.fullmatch(r"c2paactions(?:v\d+)?", label):
            actions = data.get("actions")
            if not isinstance(actions, list):
                continue
            for action_index, action in enumerate(actions):
                if not isinstance(action, dict):
                    continue
                for key in ("digitalSourceType", "digital_source_type"):
                    if key in action:
                        _append_source_types(
                            findings,
                            action[key],
                            f"{assertion_path}.data.actions[{action_index}].{key}",
                        )
        elif label in TRUSTED_ASSERTION_LABELS:
            for key in ("digitalSourceType", "digital_source_type"):
                if key in data:
                    _append_source_types(
                        findings, data[key], f"{assertion_path}.data.{key}"
                    )
    return findings


def _safe_reader_error(error: Exception, asset_path: Path) -> str:
    message = str(error)
    resolved = asset_path.resolve()
    candidates = {
        str(asset_path), str(resolved), asset_path.as_posix(), resolved.as_posix(),
        "\\\\?\\" + str(resolved), asset_path.name,
    }
    for candidate in sorted(candidates, key=len, reverse=True):
        if candidate:
            message = re.sub(re.escape(candidate), "[LOCAL_MEDIA]", message, flags=re.IGNORECASE)
    message = re.sub(
        r"(?i)(?:[a-z]:[\\/]|\\\\\?\\)[^\"\r\n,;]*",
        "[LOCAL_PATH]",
        message,
    )
    message = re.sub(
        r"(?<![:/])/(?!/)(?:[^/\s]+/)+[^\s,;]*",
        "[LOCAL_PATH]",
        message,
    )
    return message[:500]


def verify_c2pa(path: str | Path) -> dict:
    """Read a local asset and return a normalized provenance result."""

    asset_path = Path(path)
    base = {
        "status": "unavailable",
        "present": False,
        "valid": False,
        "ai_generated": False,
        "generative_involvement": False,
        "provenance_categories": [],
        "active_manifest": None,
        "claim_generator": None,
        "validation_status": [],
        "digital_source_assertions": [],
    }

    if not asset_path.is_absolute():
        return {**base, "error": "media path must be absolute"}
    if not asset_path.is_file():
        return {**base, "error": "media file does not exist"}

    try:
        from c2pa import Reader
    except Exception:
        return {**base, "error": "c2pa-python is not installed or failed to load"}

    try:
        with Reader(str(asset_path)) as reader:
            manifest_store = json.loads(reader.json())
    except Exception as error:
        message = str(error).casefold()
        if "manifest" in message and ("not found" in message or "no " in message):
            return {**base, "status": "absent", "error": None}
        return {
            **base,
            "status": "invalid",
            "error": "C2PA reader failed to parse or validate the local asset.",
        }

    active_id = manifest_store.get("active_manifest")
    manifests = manifest_store.get("manifests") or {}
    if not active_id or active_id not in manifests:
        return {**base, "status": "absent", "error": None}

    active = manifests.get(active_id) or {}
    statuses = _collect_statuses(manifest_store)
    for status in statuses:
        status["explanation"] = _safe_reader_error(
            RuntimeError(status.get("explanation") or ""), asset_path
        )
    assertions = _collect_source_assertions(active)
    categories = sorted({item["category"] for item in assertions})
    valid = not statuses
    generated = "generated" in categories
    generative_edit = "generative_edit" in categories

    return {
        **base,
        "status": "verified" if valid else "invalid",
        "present": True,
        "valid": valid,
        "ai_generated": bool(valid and generated),
        "generative_involvement": bool(valid and (generated or generative_edit)),
        "provenance_categories": categories,
        "active_manifest": str(active_id),
        "claim_generator": str(active.get("claim_generator") or "")[:300] or None,
        "validation_status": statuses,
        "digital_source_assertions": assertions,
        "error": None,
    }
