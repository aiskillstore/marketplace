from __future__ import annotations

import importlib.util
import json
import os
import shutil
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable

from .http import SafeHttpClient
from .registry import adapter_registry
from .router import _extractors_for_strategy, extract



def _optional_dependency_available(dependency: str) -> bool:
    if dependency == "yt-dlp":
        return shutil.which("yt-dlp") is not None

    if dependency == "playwright-chromium":
        if importlib.util.find_spec("playwright") is None:
            return False

        configured = os.environ.get(
            "SHAREXTRACT_BROWSER_EXECUTABLE",
            "",
        ).strip()
        if configured:
            return Path(configured).is_file()

        configured_cache = os.environ.get(
            "PLAYWRIGHT_BROWSERS_PATH",
            "",
        ).strip()
        if configured_cache and configured_cache != "0":
            roots = [Path(configured_cache).expanduser()]
        else:
            roots = [
                Path.home() / "Library" / "Caches" / "ms-playwright",
                Path.home() / ".cache" / "ms-playwright",
                Path.home() / "AppData" / "Local" / "ms-playwright",
            ]

        patterns = (
            "chromium-*/chrome-*/chrome",
            "chromium-*/chrome-linux/chrome",
            "chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
            "chromium-*/chrome-win/chrome.exe",
            "chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
            "chromium_headless_shell-*/chrome-headless-shell-linux/headless_shell",
            "chromium_headless_shell-*/chrome-headless-shell-win/headless_shell.exe",
        )
        for root in roots:
            if not root.is_dir():
                continue
            for pattern in patterns:
                if any(path.is_file() for path in root.glob(pattern)):
                    return True
        return False

    # Unknown optional runtimes fail closed instead of being reported healthy.
    return False

def get_adapter_health(
    *,
    live: bool = False,
    adapter_names: Iterable[str] | None = None,
    timeout: float = 12.0,
    max_bytes: int = 8 * 1024 * 1024,
) -> dict[str, Any]:
    """Validate adapter registration/fixtures and optionally probe public samples."""
    requested = set(adapter_names or [])
    registry = adapter_registry()
    if requested:
        registry = [item for item in registry if item["name"] in requested]
        missing_requested = sorted(
            requested - {item["name"] for item in registry}
        )
        if missing_requested:
            raise ValueError(
                "Unknown adapter health target(s): "
                + ", ".join(missing_requested)
            )

    client = SafeHttpClient(timeout=timeout, max_bytes=max_bytes)
    router_extractors = _extractors_for_strategy("auto", client)
    router_by_name = {item.name: item for item in router_extractors}

    manifest, fixture_by_id, corpus_issues = _load_fixture_corpus()
    results: list[dict[str, Any]] = []

    for item in registry:
        name = item["name"]
        issues: list[str] = []
        checks: list[dict[str, Any]] = []

        integrated_in = item.get("integrated_in")
        extractor = router_by_name.get(name)
        integration = (
            router_by_name.get(str(integrated_in))
            if integrated_in
            else extractor
        )

        if integration is None:
            issues.append(
                "adapter is not present in the auto router"
                if not integrated_in
                else f"integrated adapter {integrated_in!r} is absent from the auto router"
            )
            checks.append(
                {
                    "name": "router_registration",
                    "status": "fail",
                }
            )
        else:
            checks.append(
                {
                    "name": "router_registration",
                    "status": "pass",
                    "adapter": integration.name,
                }
            )

        if extractor is not None:
            actual_priority = getattr(extractor, "priority", None)
            if actual_priority != item.get("priority"):
                issues.append(
                    f"router priority {actual_priority!r} does not match registry "
                    f"{item.get('priority')!r}"
                )
                checks.append(
                    {
                        "name": "priority",
                        "status": "fail",
                        "actual": actual_priority,
                        "expected": item.get("priority"),
                    }
                )
            else:
                checks.append(
                    {
                        "name": "priority",
                        "status": "pass",
                        "value": actual_priority,
                    }
                )
        elif integrated_in:
            expected_priority = item.get("priority")
            actual_priority = getattr(integration, "priority", None)
            if expected_priority != actual_priority:
                issues.append(
                    f"integration priority {actual_priority!r} does not match registry "
                    f"{expected_priority!r}"
                )
                checks.append(
                    {
                        "name": "priority",
                        "status": "fail",
                        "actual": actual_priority,
                        "expected": expected_priority,
                    }
                )
            else:
                checks.append(
                    {
                        "name": "priority",
                        "status": "pass",
                        "value": actual_priority,
                    }
                )

        fixture_results = []
        for fixture_id in item.get("fixture_ids") or []:
            fixture = fixture_by_id.get(fixture_id)
            fixture_result = _validate_contract_fixture(
                item,
                fixture_id,
                fixture,
                extractor=extractor,
                integration=integration,
            )
            fixture_results.append(fixture_result)
            if fixture_result["status"] != "pass":
                issues.extend(fixture_result.get("issues") or [])

        if not fixture_results:
            issues.append("registry contains no contract fixture IDs")
        checks.append(
            {
                "name": "contract_fixtures",
                "status": (
                    "pass"
                    if fixture_results
                    and all(x["status"] == "pass" for x in fixture_results)
                    else "fail"
                ),
                "fixtures": fixture_results,
            }
        )

        dependency = item.get("optional_dependency")
        dependency_available = (
            _optional_dependency_available(str(dependency))
            if dependency
            else True
        )
        if dependency:
            checks.append(
                {
                    "name": "optional_dependency",
                    "status": "pass" if dependency_available else "unavailable",
                    "dependency": dependency,
                }
            )

        live_result: dict[str, Any] = {
            "status": "not_requested" if not live else "not_configured"
        }
        sample = item.get("live_sample")
        if live and isinstance(sample, dict):
            live_result = _run_live_check(
                item,
                sample,
                timeout=timeout,
                max_bytes=max_bytes,
            )
            if live_result["status"] != "pass":
                issues.append(
                    "live verification failed: "
                    + str(live_result.get("error") or "unexpected result")
                )

        offline_failed = any(
            check["status"] == "fail"
            for check in checks
            if check["name"] != "optional_dependency"
        )
        if issues:
            status = "degraded" if live and not offline_failed else "unhealthy"
        elif dependency and not dependency_available:
            status = "optional_unavailable"
        else:
            status = "healthy"

        results.append(
            {
                "name": name,
                "platform": item["platform"],
                "kind": item["kind"],
                "priority": item["priority"],
                "stability": item["stability"],
                "provenance": item["provenance"],
                "status": status,
                "verification": item.get("verification") or {},
                "expected_methods": item.get("expected_methods") or [],
                "fixture_ids": item.get("fixture_ids") or [],
                "integrated_in": integrated_in,
                "checks": checks,
                "live": live_result,
                "issues": issues,
            }
        )

    statuses = [item["status"] for item in results]
    unhealthy = sum(status == "unhealthy" for status in statuses)
    degraded = sum(status == "degraded" for status in statuses)
    optional_unavailable = sum(
        status == "optional_unavailable" for status in statuses
    )
    healthy = sum(status == "healthy" for status in statuses)

    return {
        "schema_version": 1,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": "offline+live" if live else "offline",
        "status": "ok" if not unhealthy and not degraded and not corpus_issues else "degraded",
        "summary": {
            "total": len(results),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "optional_unavailable": optional_unavailable,
            "live_configured": sum(
                isinstance(item.get("live_sample"), dict)
                for item in registry
            ),
        },
        "fixture_corpus": {
            "schema_version": manifest.get("schema_version"),
            "fixture_type": manifest.get("fixture_type"),
            "count": len(fixture_by_id),
            "issues": corpus_issues,
        },
        "adapters": results,
    }


def render_health_markdown(report: dict[str, Any]) -> str:
    """Render a compact human-readable health matrix from a health report."""
    summary = report.get("summary") or {}
    lines = [
        "# ShareXtract Adapter Health",
        "",
        (
            f"Mode: {report.get('mode', '')} · Status: {report.get('status', '')} · "
            f"Adapters: {summary.get('total', 0)} · Healthy: {summary.get('healthy', 0)} · "
            f"Degraded: {summary.get('degraded', 0)} · Unhealthy: {summary.get('unhealthy', 0)} · "
            f"Optional unavailable: {summary.get('optional_unavailable', 0)}"
        ),
        "",
        "| Adapter | Platform | Stability | Status | Last verified | Live | Fixtures |",
        "| --- | --- | --- | --- | --- | --- | ---: |",
    ]
    for item in report.get("adapters") or []:
        verification = item.get("verification") or {}
        live_result = item.get("live") or {}
        lines.append(
            "| {name} | {platform} | {stability} | {status} | {verified} | {live} | {fixtures} |".format(
                name=item.get("name", ""),
                platform=item.get("platform", ""),
                stability=item.get("stability", ""),
                status=item.get("status", ""),
                verified=verification.get("last_verified_at", ""),
                live=live_result.get("status", ""),
                fixtures=len(item.get("fixture_ids") or []),
            )
        )

    corpus = report.get("fixture_corpus") or {}
    lines.extend(
        [
            "",
            (
                f"Fixture corpus: {corpus.get('fixture_type', '')} · "
                f"{corpus.get('count', 0)} fixture(s)."
            ),
        ]
    )
    if corpus.get("issues"):
        lines.append("")
        lines.append("Corpus issues:")
        for issue in corpus["issues"]:
            lines.append(f"- {issue}")

    return "\n".join(lines)


def _load_fixture_corpus() -> tuple[
    dict[str, Any],
    dict[str, dict[str, Any]],
    list[str],
]:
    root = files("sharextract.fixtures")
    issues: list[str] = []

    try:
        manifest = json.loads(
            root.joinpath("manifest.json").read_text(encoding="utf-8")
        )
    except Exception as exc:
        return {}, {}, [f"fixture manifest could not be read: {exc}"]

    if not isinstance(manifest, dict):
        return {}, {}, ["fixture manifest must be a JSON object"]

    entries = manifest.get("fixtures")
    if not isinstance(entries, list):
        return manifest, {}, ["fixture manifest fixtures must be a list"]

    fixture_by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            issues.append("fixture manifest contains a non-object entry")
            continue
        fixture_id = entry.get("id")
        path = entry.get("path")
        if not isinstance(fixture_id, str) or not fixture_id:
            issues.append("fixture manifest entry is missing id")
            continue
        if fixture_id in fixture_by_id:
            issues.append(f"duplicate fixture id: {fixture_id}")
            continue
        if not isinstance(path, str) or not path:
            issues.append(f"fixture {fixture_id} is missing path")
            continue

        try:
            payload = json.loads(
                root.joinpath(path).read_text(encoding="utf-8")
            )
        except Exception as exc:
            issues.append(f"fixture {fixture_id} could not be read: {exc}")
            continue
        if not isinstance(payload, dict):
            issues.append(f"fixture {fixture_id} must be a JSON object")
            continue
        fixture_by_id[fixture_id] = payload

    return manifest, fixture_by_id, issues


def _validate_contract_fixture(
    registry_item: dict[str, Any],
    fixture_id: str,
    fixture: dict[str, Any] | None,
    *,
    extractor: Any,
    integration: Any,
) -> dict[str, Any]:
    issues: list[str] = []
    if fixture is None:
        return {
            "id": fixture_id,
            "status": "fail",
            "issues": [f"fixture {fixture_id} is absent from packaged corpus"],
        }

    if fixture.get("id") != fixture_id:
        issues.append(f"fixture {fixture_id} id field does not match filename/registry")
    if fixture.get("adapter") != registry_item["name"]:
        issues.append(
            f"fixture {fixture_id} adapter {fixture.get('adapter')!r} does not match "
            f"{registry_item['name']!r}"
        )
    if fixture.get("scope") != "route_contract":
        issues.append(f"fixture {fixture_id} scope must be route_contract")

    expected = fixture.get("expected")
    if not isinstance(expected, dict):
        issues.append(f"fixture {fixture_id} expected must be an object")
        expected = {}

    for key in ("platform", "kind", "priority"):
        if expected.get(key) != registry_item.get(key):
            issues.append(
                f"fixture {fixture_id} expected {key}={expected.get(key)!r} "
                f"does not match registry {registry_item.get(key)!r}"
            )

    fixture_methods = expected.get("methods")
    if (
        not isinstance(fixture_methods, list)
        or fixture_methods != registry_item.get("expected_methods")
    ):
        issues.append(
            f"fixture {fixture_id} methods do not match registry expected_methods"
        )

    input_url = fixture.get("input_url")
    if not isinstance(input_url, str) or not input_url.startswith(
        ("http://", "https://")
    ):
        issues.append(f"fixture {fixture_id} input_url is invalid")
    elif registry_item.get("optional_dependency") == "yt-dlp":
        if shutil.which("yt-dlp") is not None and extractor is not None:
            if bool(extractor.supports(input_url)) is not True:
                issues.append(
                    f"fixture {fixture_id} is not supported by installed yt-dlp adapter"
                )
    elif extractor is not None:
        if bool(extractor.supports(input_url)) is not bool(
            expected.get("supported")
        ):
            issues.append(
                f"fixture {fixture_id} support expectation does not match adapter"
            )
    elif registry_item.get("integrated_in") and integration is not None:
        if not integration.supports(input_url):
            issues.append(
                f"fixture {fixture_id} URL is not supported by integration "
                f"{integration.name}"
            )

    return {
        "id": fixture_id,
        "status": "pass" if not issues else "fail",
        "scope": fixture.get("scope"),
        "synthetic": fixture.get("synthetic"),
        "issues": issues,
    }


def _run_live_check(
    registry_item: dict[str, Any],
    sample: dict[str, Any],
    *,
    timeout: float,
    max_bytes: int,
) -> dict[str, Any]:
    url = sample.get("url")
    if not isinstance(url, str) or not url:
        return {"status": "fail", "error": "live sample URL is missing"}

    errors: list[str] = []
    result = None
    attempts = max(1, int(sample.get("attempts") or 2))
    for attempt in range(1, attempts + 1):
        try:
            result = extract(
                url,
                strategy="auto",
                timeout=timeout,
                max_bytes=max_bytes,
            )
            break
        except Exception as exc:
            errors.append(str(exc))

    if result is None:
        return {
            "status": "fail",
            "url": url,
            "attempts": attempts,
            "errors": errors,
            "error": errors[-1] if errors else "live extraction failed",
        }

    expected_platform = sample.get("platform")
    expected_methods = sample.get("methods")
    if result.platform != expected_platform:
        return {
            "status": "fail",
            "url": url,
            "error": (
                f"platform drift: expected {expected_platform!r}, "
                f"got {result.platform!r}"
            ),
            "actual_method": result.extraction_method,
            "attempts": len(errors) + 1,
        }
    if (
        isinstance(expected_methods, list)
        and result.extraction_method not in expected_methods
    ):
        return {
            "status": "fail",
            "url": url,
            "error": (
                f"method drift: expected one of {expected_methods!r}, "
                f"got {result.extraction_method!r}"
            ),
            "actual_platform": result.platform,
            "attempts": len(errors) + 1,
        }

    return {
        "status": "pass",
        "url": url,
        "platform": result.platform,
        "method": result.extraction_method,
        "title": result.title,
        "has_body": result.has_body,
        "attempts": len(errors) + 1,
        "transient_errors": errors,
    }
