from __future__ import annotations

import importlib.util
import shutil
from typing import Any

from .registry import adapter_registry


def _extractor_capabilities() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in adapter_registry():
        public = {
            "name": item["name"],
            "platform": item["platform"],
            "kind": item["kind"],
            "provenance": item["provenance"],
            "built_in": item["built_in"],
            "priority": item["priority"],
            "stability": item["stability"],
            "fixture_count": len(item.get("fixture_ids") or []),
            "verification": item.get("verification") or {},
        }
        if item.get("integrated_in"):
            public["integrated_in"] = item["integrated_in"]
        dependency = item.get("optional_dependency")
        if dependency == "yt-dlp":
            public["available"] = shutil.which("yt-dlp") is not None
        result.append(public)
    return result


def get_capabilities() -> dict[str, Any]:
    """Return machine-readable extraction and optional-runtime capabilities."""
    return {
        "strategies": ["auto", "native", "media", "web"],
        "extractors": _extractor_capabilities(),
        "optional_dependencies": {
            "trafilatura": importlib.util.find_spec("trafilatura") is not None,
            "yt_dlp": shutil.which("yt-dlp") is not None,
            "mcp": importlib.util.find_spec("mcp") is not None,
            "fastapi": importlib.util.find_spec("fastapi") is not None,
            "playwright": importlib.util.find_spec("playwright") is not None,
        },
        "health": {
            "adapter_registry": True,
            "contract_fixture_corpus": True,
            "offline_validation": True,
            "optional_live_verification": True,
        },
        "security_boundary": {
            "public_http_only": True,
            "blocks_literal_private_ips": True,
            "blocks_localhost": True,
            "revalidates_redirects": True,
            "bounded_response_bytes": True,
            "bypasses_authentication": False,
            "solves_captchas": False,
            "bypasses_paywalls_or_waf": False,
            "imports_browser_session_state": False,
        },
    }
