#!/usr/bin/env python
"""CLI for local text signals, provenance, and social-media reception analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from c2pa_verify import verify_c2pa
from evidence import assess_origin, assess_practical, render_markdown
from local_text_detector import analyze_local_text
from local_model import LocalModelError, admit as admit_local_model, predict as predict_local_model
from media_security import (
    DEFAULT_MAX_BYTES,
    MediaSecurityError,
    validate_external_selection,
    validate_media_file,
)
from providers import ProviderError, analyze_image_hive
from reception_schema import ReceptionValidationError, validate_reception
from redaction import safe_provider_error
from style_signals import analyze_style_patterns


PLATFORMS = {"x", "reddit", "linkedin", "instagram", "tiktok", "threads", "web", "unknown"}
LANGUAGES = {"en", "zh", "mixed", "other", "unknown"}
PURPOSES = {"inform", "discuss", "persuade", "promote", "support", "unknown"}
OBSERVATION_TYPES = {"platform_ai_label", "author_disclosure", "other"}


class CaseValidationError(ValueError):
    """Raised when case.json violates the public input contract."""


def _load_json(path: Path) -> Any:
    if not path.is_file():
        raise CaseValidationError(f"JSON file does not exist: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CaseValidationError(f"Invalid JSON in {path.name}: {error.msg}") from error


def _valid_public_url(value: Any) -> bool:
    if value in (None, ""):
        return True
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _valid_iso8601(value: Any, *, nullable: bool = False) -> bool:
    if nullable and value in (None, ""):
        return True
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate_case(value: Any) -> dict:
    """Validate the case input and local-media boundary."""

    if not isinstance(value, dict):
        raise CaseValidationError("case must be a JSON object")
    if value.get("schema_version") != "1.0":
        raise CaseValidationError("schema_version must be 1.0")

    source = value.get("source")
    if not isinstance(source, dict):
        raise CaseValidationError("source must be an object")
    if source.get("public") is not True:
        raise CaseValidationError("source.public must be true")
    if source.get("platform") not in PLATFORMS:
        raise CaseValidationError("source.platform is invalid")
    if not _valid_public_url(source.get("url")):
        raise CaseValidationError("source.url must be a public http(s) URL or null")
    if not _valid_iso8601(source.get("captured_at")):
        raise CaseValidationError("source.captured_at must be an ISO-8601 timestamp")
    if not _valid_iso8601(source.get("published_at"), nullable=True):
        raise CaseValidationError("source.published_at must be ISO-8601 or null")
    if source.get("author") is not None and not isinstance(source.get("author"), str):
        raise CaseValidationError("source.author must be a string or null")

    content = value.get("content")
    if not isinstance(content, dict):
        raise CaseValidationError("content must be an object")
    text = content.get("text")
    if text is not None and not isinstance(text, str):
        raise CaseValidationError("content.text must be a string or null")
    if content.get("language") not in LANGUAGES:
        raise CaseValidationError("content.language is invalid")

    images = content.get("images")
    if not isinstance(images, list):
        raise CaseValidationError("content.images must be a list")
    seen_ids: set[str] = set()
    for index, image in enumerate(images):
        path = f"content.images[{index}]"
        if not isinstance(image, dict):
            raise CaseValidationError(f"{path} must be an object")
        image_id = image.get("id")
        if not isinstance(image_id, str) or not image_id.strip():
            raise CaseValidationError(f"{path}.id must be a non-empty string")
        if image_id in seen_ids:
            raise CaseValidationError(f"duplicate image id: {image_id}")
        seen_ids.add(image_id)
        media_path = image.get("path")
        if not isinstance(media_path, str):
            raise CaseValidationError(f"{path}.path must be a string")
        local_path = Path(media_path)
        if not local_path.is_absolute():
            raise CaseValidationError(f"{path}.path must be an absolute local file")
        if not _valid_public_url(image.get("source_url")):
            raise CaseValidationError(f"{path}.source_url must be http(s) or null")
        alt_text = image.get("alt_text")
        if alt_text is not None and not isinstance(alt_text, str):
            raise CaseValidationError(f"{path}.alt_text must be a string or null")

    if not (isinstance(text, str) and text.strip()) and not images:
        raise CaseValidationError("case must contain text or at least one local image")

    observations = value.get("observations")
    if not isinstance(observations, list):
        raise CaseValidationError("observations must be a list")
    for index, observation in enumerate(observations):
        path = f"observations[{index}]"
        if not isinstance(observation, dict):
            raise CaseValidationError(f"{path} must be an object")
        if observation.get("type") not in OBSERVATION_TYPES:
            raise CaseValidationError(f"{path}.type is invalid")
        if not isinstance(observation.get("value"), str) or not observation["value"].strip():
            raise CaseValidationError(f"{path}.value must be a non-empty string")
        if not _valid_public_url(observation.get("source_url")):
            raise CaseValidationError(f"{path}.source_url must be http(s) or null")
        if observation.get("assertion") not in {None, "confirmed", "denied", "quoted", "discussed", "uncertain"}:
            raise CaseValidationError(f"{path}.assertion is invalid")
        scope = observation.get("scope")
        if scope is not None and (not isinstance(scope, str) or not scope.strip()):
            raise CaseValidationError(f"{path}.scope must be a non-empty string or null")
        valid_observation_scopes = {"post", *seen_ids}
        if isinstance(text, str) and text.strip():
            valid_observation_scopes.add("text")
        if scope is not None and scope not in valid_observation_scopes:
            raise CaseValidationError(f"{path}.scope must be post, text, or a known image id")

    if value.get("declared_purpose") not in PURPOSES:
        raise CaseValidationError("declared_purpose is invalid")
    return value


def _collect_sources(case: dict) -> list[str]:
    candidates = [case.get("source", {}).get("url")]
    candidates.extend(
        observation.get("source_url") for observation in case.get("observations", [])
    )
    candidates.extend(
        image.get("source_url") for image in case.get("content", {}).get("images", [])
    )
    return list(dict.fromkeys(source for source in candidates if isinstance(source, str) and source))


def _provider_error(error: ProviderError, secrets: list[str]) -> dict:
    return safe_provider_error(error.provider, error.category, error, secrets)


def _detector_coverage(
    case: dict,
    *,
    external_authorized: bool,
    selected_assets: list[dict],
    provider_signals: list[dict],
    provider_errors: list[dict],
) -> dict:
    text_present = bool(str(case.get("content", {}).get("text") or "").strip())

    hive_completed = sum(1 for item in provider_signals if item.get("provider") == "hive")
    hive_errors = [item for item in provider_errors if item.get("provider") == "hive"]
    if not selected_assets:
        hive_status = "not_run_no_assets_selected" if case.get("content", {}).get("images") else "not_applicable"
    elif hive_completed == len(selected_assets):
        hive_status = "completed"
    elif not external_authorized:
        hive_status = "not_run_no_consent"
    elif any(item.get("category") == "missing_key" for item in hive_errors):
        hive_status = "not_run_missing_key"
    elif hive_completed:
        hive_status = "partial"
    else:
        hive_status = "failed"

    return {
        "local_text": {
            "status": "completed" if text_present else "not_applicable",
            "text_present": text_present,
            "external_transmission": False,
        },
        "hive": {
            "status": hive_status,
            "selected_images": len(selected_assets),
            "completed_images": hive_completed,
        },
    }


def analyze(
    case: dict,
    reception: dict,
    *,
    allow_external: bool,
    external_image_ids: list[str],
    media_root: Path,
    max_media_bytes: int,
    max_images: int,
    text_model: dict | None = None,
    text_model_evaluation: dict | None = None,
) -> dict:
    """Run local text/provenance checks and optional Hive image analysis."""

    images = case["content"]["images"]
    c2pa_results: list[dict] = []
    provider_signals: list[dict] = []
    provider_errors: list[dict] = []
    local_model_assessment: dict = {"status": "not_configured"}
    asset_summaries: list[dict] = []
    paths_by_id: dict[str, str] = {}

    for image in images:
        summary = validate_media_file(
            image["path"],
            allowed_root=media_root,
            max_bytes=max_media_bytes,
            asset_id=image["id"],
        )
        asset_summaries.append(summary)
        paths_by_id[image["id"]] = image["path"]
        # Only the digest crosses into the report-generating evidence layer.
        image["sha256"] = summary["sha256"]

    selected_assets = validate_external_selection(asset_summaries, external_image_ids)
    if len(selected_assets) > max_images:
        raise MediaSecurityError("explicit external image selection exceeds --max-images")
    if selected_assets and not allow_external:
        raise MediaSecurityError("--external-image requires --allow-external consent")

    # Local provenance verification always covers every validated image.  The
    # upload cap must not silently reduce local C2PA coverage.
    for image in images:
        c2pa_results.append(
            {
                "scope": image["id"],
                "result": verify_c2pa(image["path"]),
            }
        )

    if allow_external and selected_assets:
        hive_key = os.environ.get("HIVE_API_KEY", "")
        secrets = [hive_key]

        for asset in selected_assets:
            try:
                fresh = validate_media_file(
                    paths_by_id[asset["asset_id"]],
                    allowed_root=media_root,
                    max_bytes=max_media_bytes,
                    asset_id=asset["asset_id"],
                )
                if fresh != asset:
                    raise MediaSecurityError("media changed after consent selection")
                signal = analyze_image_hive(
                    paths_by_id[asset["asset_id"]],
                    hive_key,
                    media_type=asset["media_type"],
                )
                signal["scope"] = asset["asset_id"]
                provider_signals.append(signal)
            except ProviderError as error:
                provider_errors.append(_provider_error(error, secrets))
            except Exception as error:
                provider_errors.append(
                    safe_provider_error("hive", "unexpected", type(error).__name__, secrets)
                )

    if text_model is not None or text_model_evaluation is not None:
        if text_model is None or text_model_evaluation is None:
            raise LocalModelError("--text-model and --text-model-evaluation must be supplied together")
        language = case["content"].get("language", "unknown")
        admit_local_model(text_model, text_model_evaluation, language)
        local_model_assessment = predict_local_model(
            text_model, str(case["content"].get("text") or "")
        )
        local_model_assessment.update(
            {
                "status": "evaluation_metadata_passed",
                "trusted_for_origin": False,
                "origin_effect": "none",
                "limitation": (
                    "The local evaluation file is not a cryptographic attestation; "
                    "this baseline remains research-only and cannot change origin_assessment."
                ),
            }
        )

    origin = assess_origin(case, provider_signals, c2pa_results)
    style_patterns = analyze_style_patterns(
        case["content"].get("text"),
        case["content"].get("language", "unknown"),
        platform=case["source"].get("platform", "unknown"),
        declared_purpose=case.get("declared_purpose", "unknown"),
    )
    local_text = analyze_local_text(
        case["content"].get("text"),
        case["content"].get("language", "unknown"),
        style_assessment=style_patterns,
    )
    practical = assess_practical(origin, style_patterns, local_text)
    detector_coverage = _detector_coverage(
        case,
        external_authorized=allow_external,
        selected_assets=selected_assets,
        provider_signals=provider_signals,
        provider_errors=provider_errors,
    )
    if images and not selected_assets:
        origin["limitations"].append(
            "No image was explicitly selected for external analysis; Hive was not called."
        )
    if provider_errors:
        origin["limitations"].append("One or more configured provider checks did not complete.")

    return {
        "schema_version": "1.0",
        "practical_assessment": practical,
        "origin_assessment": origin,
        "local_text_assessment": local_text,
        "local_model_research_assessment": local_model_assessment,
        "style_pattern_assessment": style_patterns,
        "detector_coverage": detector_coverage,
        "external_processing": {
            "provider": "hive",
            "authorized": bool(allow_external and selected_assets),
            "selected_assets": selected_assets,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "paths_retained": False,
        },
        "reproducibility": {
            "content_sha256": hashlib.sha256(
                json.dumps(
                    {
                        "text": case.get("content", {}).get("text"),
                        "language": case.get("content", {}).get("language"),
                        "assets": asset_summaries,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest(),
            "local_text_method": local_text.get("method"),
        },
        "human_reception": reception,
        "sources": _collect_sources(case),
        "provider_errors": provider_errors,
    }


def _write_report(report: dict, output_dir: Path, output_format: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_format in {"json", "both"}:
        (output_dir / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if output_format in {"markdown", "both"}:
        (output_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze social-media AI-origin evidence and blind Human Reception."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze", help="Analyze one public-content case")
    analyze_parser.add_argument("--input", required=True, type=Path, help="Path to case.json")
    analyze_parser.add_argument(
        "--reception", required=True, type=Path, help="Path to blind reception.json"
    )
    analyze_parser.add_argument(
        "--output-dir", required=True, type=Path, help="Directory for report files"
    )
    analyze_parser.add_argument(
        "--format",
        choices=("json", "markdown", "both"),
        default="both",
        help="Output format",
    )
    analyze_parser.add_argument(
        "--allow-external",
        action="store_true",
        help="Consent gate for sending only explicitly selected images to Hive",
    )
    analyze_parser.add_argument(
        "--external-image",
        action="append",
        default=[],
        metavar="IMAGE_ID",
        help="Image ID authorized for Hive upload; repeat once per image",
    )
    analyze_parser.add_argument(
        "--media-root",
        type=Path,
        help="Absolute directory containing allowed local media; defaults to case.json directory",
    )
    analyze_parser.add_argument(
        "--max-media-bytes",
        type=int,
        default=DEFAULT_MAX_BYTES,
        help="Maximum bytes per validated image, default 20 MiB",
    )
    analyze_parser.add_argument(
        "--max-images",
        type=int,
        default=4,
        help="Maximum explicitly selected images to upload; local C2PA still covers all images",
    )
    analyze_parser.add_argument(
        "--text-model",
        type=Path,
        help="Optional fingerprinted local model artifact",
    )
    analyze_parser.add_argument(
        "--text-model-evaluation",
        type=Path,
        help="Matching locked-blind passing evaluation report",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "analyze":
        parser.error("unknown command")
    if args.max_images < 1:
        parser.error("--max-images must be at least 1")
    if args.max_media_bytes < 1:
        parser.error("--max-media-bytes must be at least 1")

    try:
        case = validate_case(_load_json(args.input))
        reception = validate_reception(_load_json(args.reception), case)
        text_model = _load_json(args.text_model) if args.text_model else None
        text_model_evaluation = (
            _load_json(args.text_model_evaluation) if args.text_model_evaluation else None
        )
        report = analyze(
            case,
            reception,
            allow_external=args.allow_external,
            external_image_ids=args.external_image,
            media_root=args.media_root or args.input.resolve().parent,
            max_media_bytes=args.max_media_bytes,
            max_images=args.max_images,
            text_model=text_model,
            text_model_evaluation=text_model_evaluation,
        )
        _write_report(report, args.output_dir, args.format)
    except (CaseValidationError, ReceptionValidationError, MediaSecurityError, LocalModelError) as error:
        print(f"validation error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"filesystem error: {type(error).__name__}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
