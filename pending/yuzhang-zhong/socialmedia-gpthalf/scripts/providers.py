"""Optional Hive adapter with normalized, minimal responses."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable


HIVE_ENDPOINT = "https://api.thehive.ai/api/v2/task/sync"


class ProviderError(RuntimeError):
    """An expected provider failure safe for normalization."""

    def __init__(self, provider: str, category: str, message: str):
        super().__init__(message)
        self.provider = provider
        self.category = category


def _requests_module():
    try:
        import requests
    except Exception as error:
        raise ProviderError("runtime", "dependency", "requests is not installed") from error
    return requests


def _http_category(status_code: int) -> str:
    if status_code in {401, 403}:
        return "authentication"
    if status_code == 429:
        return "rate_limited"
    if status_code >= 500:
        return "service_unavailable"
    return "request_rejected"


def _find_classes(value: Any) -> list[dict]:
    findings: list[dict] = []
    if isinstance(value, dict):
        if (
            isinstance(value.get("class"), str)
            and isinstance(value.get("score"), (int, float))
            and not isinstance(value.get("score"), bool)
        ):
            findings.append({"class": value["class"], "score": float(value["score"])})
        for child in value.values():
            findings.extend(_find_classes(child))
    elif isinstance(value, list):
        for child in value:
            findings.extend(_find_classes(child))
    return findings


def _has_c2pa(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if "c2pa" in key.casefold() and child not in (None, "", [], {}):
                return True
            if _has_c2pa(child):
                return True
    elif isinstance(value, list):
        return any(_has_c2pa(child) for child in value)
    return False


def _hive_model_version(payload: dict) -> str:
    try:
        return str(payload["status"][0]["response"]["input"].get("model_version", "unknown"))
    except (KeyError, IndexError, TypeError, AttributeError):
        return "unknown"


def analyze_image_hive(
    image_path: str | Path,
    api_key: str,
    *,
    media_type: str | None = None,
    session: Any = None,
    timeout: int = 30,
    max_attempts: int = 2,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    """Upload a local image to Hive and normalize generation classes."""

    if not api_key:
        raise ProviderError("hive", "missing_key", "HIVE_API_KEY is not configured")
    path = Path(image_path)
    if not path.is_absolute() or not path.is_file():
        raise ProviderError("hive", "invalid_input", "image path must be an existing absolute file")

    requests = _requests_module()
    client = session or requests
    mime_type = media_type or "application/octet-stream"
    if mime_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise ProviderError("hive", "invalid_input", "validated image media_type is required")
    upload_name = {
        "image/jpeg": "asset.jpg",
        "image/png": "asset.png",
        "image/webp": "asset.webp",
        "image/gif": "asset.gif",
    }[mime_type]
    last_response = None
    for attempt in range(max_attempts):
        try:
            with path.open("rb") as handle:
                response = client.post(
                    HIVE_ENDPOINT,
                    headers={"authorization": f"token {api_key}", "accept": "application/json"},
                    files={"media": (upload_name, handle, mime_type)},
                    timeout=timeout,
                )
        except Exception as error:
            if attempt + 1 < max_attempts:
                sleep(0.2 * (attempt + 1))
                continue
            raise ProviderError("hive", "network", type(error).__name__) from error
        last_response = response
        if response.status_code < 400:
            break
        if response.status_code not in {429} and response.status_code < 500:
            break
        if attempt + 1 < max_attempts:
            sleep(0.2 * (attempt + 1))

    status = int(getattr(last_response, "status_code", 0))
    if status >= 400:
        raise ProviderError("hive", _http_category(status), f"HTTP {status}")
    try:
        payload = last_response.json()
    except Exception as error:
        raise ProviderError("hive", "schema", "response was not valid JSON") from error
    if not isinstance(payload, dict):
        raise ProviderError("hive", "schema", "response must be a JSON object")

    model_version = _hive_model_version(payload)
    if model_version == "unknown":
        raise ProviderError("hive", "schema", "response omitted the model version")

    classes = _find_classes(payload)
    if not classes:
        raise ProviderError("hive", "schema", "response contained no classification scores")
    by_name: dict[str, float] = {}
    for item in classes:
        name = str(item["class"]).casefold()
        by_name[name] = max(by_name.get(name, 0.0), float(item["score"]))

    ai_score = by_name.get("ai_generated")
    not_ai_score = by_name.get("not_ai_generated")
    if ai_score is None and not_ai_score is None:
        raise ProviderError("hive", "schema", "generation classes were missing")
    if any(score is not None and not 0.0 <= score <= 1.0 for score in (ai_score, not_ai_score)):
        raise ProviderError("hive", "schema", "generation score was outside [0, 1]")

    excluded = {
        "ai_generated",
        "not_ai_generated",
        "deepfake",
        "none",
        "inconclusive",
        "inconclusive_video",
    }
    source_candidates = [
        (name, score) for name, score in by_name.items() if name not in excluded
    ]
    source_name, source_score = (
        max(source_candidates, key=lambda item: item[1])
        if source_candidates
        else (None, None)
    )

    return {
        "provider": "hive",
        "modality": "image",
        "scope": None,
        "ai_generated_score": ai_score,
        "not_ai_generated_score": not_ai_score,
        "source_class": source_name,
        "source_score": source_score,
        "deepfake_score": by_name.get("deepfake"),
        "c2pa_metadata_present": _has_c2pa(payload),
        "model_version": model_version,
    }
