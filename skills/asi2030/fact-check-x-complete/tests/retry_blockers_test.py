#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from trusted_search_config import (  # noqa: E402
    ConfigurationError,
    NoRedirectHandler,
    validate_trusted_search_endpoint,
)


TEST_KEY = "fixture_fact_check_x_key_123456"
PRODUCTION = "https://open.dknowc.cn/dependable/search"
REJECTED_ENDPOINTS = (
    "http://open.dknowc.cn/dependable/search",
    "https://open.dknowc.cn:443/dependable/search",
    "https://open.dknowc.cn/dependable/search/",
    "https://open.dknowc.cn/dependable/search?x=1",
    "https://open.dknowc.cn/dependable/search#fragment",
    "https://user@open.dknowc.cn/dependable/search",
    "https://open.dknowc.cn@evil.example/dependable/search",
    "https://open.dknowc.cn%2e.evil.example/dependable/search",
    "http://localhost:9999/dependable/search",
    "http://0.0.0.0:9999/dependable/search",
    "https://evil.example/dependable/search",
)


def load_module(name: str, path: Path):
    module_dir = str(path.parent)
    sys.path.insert(0, module_dir)
    previous_common = sys.modules.pop("common", None)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    try:
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(module_dir)
        sys.modules.pop("common", None)
        if previous_common is not None:
            sys.modules["common"] = previous_common


def reject_endpoint(endpoint: str) -> None:
    try:
        validate_trusted_search_endpoint(endpoint)
    except ConfigurationError as exc:
        assert TEST_KEY not in str(exc)
    else:
        raise AssertionError(f"endpoint should be rejected: {endpoint}")


def test_endpoint_gate() -> None:
    old = os.environ.copy()
    try:
        os.environ.pop("FACT_CHECK_X_TEST_MODE", None)
        assert validate_trusted_search_endpoint(PRODUCTION) == PRODUCTION
        for endpoint in REJECTED_ENDPOINTS:
            reject_endpoint(endpoint)
        reject_endpoint("http://127.0.0.1:9999/dependable/search")

        os.environ["FACT_CHECK_X_TEST_MODE"] = "1"
        assert validate_trusted_search_endpoint("http://127.0.0.1:9999/dependable/search") == "http://127.0.0.1:9999/dependable/search"
        assert validate_trusted_search_endpoint("http://[::1]:9999/dependable/search") == "http://[::1]:9999/dependable/search"
        for endpoint in (
            "http://localhost:9999/dependable/search",
            "http://0.0.0.0:9999/dependable/search",
            "http://127.0.0.1:9999/other",
            "http://127.0.0.1:9999/dependable/search?x=1",
            "http://user@127.0.0.1:9999/dependable/search",
            "http://127.0.0.1.evil.example:9999/dependable/search",
            "http://[::1]@evil.example:9999/dependable/search",
        ):
            reject_endpoint(endpoint)
    finally:
        os.environ.clear()
        os.environ.update(old)


def assert_boundary_paths(boundary: dict, *, request_id: str | None = None) -> None:
    assert boundary["policy"] == "UNTRUSTED_CONTENT_BOUNDARY"
    assert boundary["untrustedText"] == ["external answers", "citations", "evidence"]
    assert boundary["forbiddenCapabilities"] == ["shell", "browser", "network", "credentials", "tool execution"]
    file_access = boundary["fileAccess"]
    assert file_access["root"] == "current-run"
    assert file_access["denyOutsideRoot"] is True
    if request_id is None:
        assert file_access["read"] == ["comparison-task.json"]
        assert file_access["write"] == ["comparison-analysis.json"]
    else:
        assert file_access["read"] == [
            f"authority/requests/{request_id}.json",
            f"authority/evidence/{request_id}.json",
        ]
        assert file_access["write"] == [
            f"authority/assessments/{request_id}.json",
            f"authority/results/{request_id}.json",
        ]
    with tempfile.TemporaryDirectory() as temporary:
        run_root = Path(temporary).resolve()
        for relative_path in [*file_access["read"], *file_access["write"]]:
            path = Path(relative_path)
            assert not path.is_absolute()
            assert ".." not in path.parts
            assert (run_root / path).resolve().is_relative_to(run_root)


def test_comparison_boundary_declares_concrete_run_relative_paths() -> None:
    module = load_module("knowledge_compare_boundary", ROOT / "modules" / "fact-check-x-knowledge-compare" / "scripts" / "knowledge_compare.py")
    task_data = module.build_task("question", [])
    assert_boundary_paths(task_data["securityBoundary"])


def test_authority_boundary_declares_concrete_run_relative_paths() -> None:
    fact_check = load_module("fact_check_x_boundary", ROOT / "scripts" / "fact_check_x.py")
    comparison = {
        "schemaVersion": "fact-check-x/comparison@1",
        "question": "question",
        "knowledgePoints": [{
            "id": "K1",
            "description": "description",
            "role": "direct",
            "core": True,
            "comparison": {"status": "single"},
            "claims": {},
            "trustedAnchor": {"eligible": False},
        }],
    }
    with tempfile.TemporaryDirectory() as temporary:
        run_root = Path(temporary)
        fact_check.build_requests(comparison, run_root / "authority" / "requests")
        request = json.loads((run_root / "authority" / "requests" / "K1.json").read_text(encoding="utf-8"))
    assert_boundary_paths(request["securityBoundary"], request_id="K1")


def test_malicious_fixture_stays_data_in_comparison_task() -> None:
    fixture = json.loads((ROOT / "tests" / "fixtures" / "malicious-untrusted-content.json").read_text(encoding="utf-8"))
    module = load_module("knowledge_compare_malicious", ROOT / "modules" / "fact-check-x-knowledge-compare" / "scripts" / "knowledge_compare.py")
    with patch("subprocess.run") as subprocess_run, patch("urllib.request.urlopen") as network_open, patch("urllib.request.Request") as credential_request:
        task_data = module.build_task("question", [{"platform": "fixture", "status": "success", "answerMarkdown": fixture["platformAnswer"], "references": [{"text": fixture["citation"]}]}])
    subprocess_run.assert_not_called()
    network_open.assert_not_called()
    credential_request.assert_not_called()
    assert_boundary_paths(task_data["securityBoundary"])
    assert task_data["rules"][0] == module.UNTRUSTED_CONTENT_BOUNDARY_RULE
    assert task_data["platforms"][0]["answerMarkdown"] == fixture["platformAnswer"]
    assert task_data["platforms"][0]["references"][0]["capturedText"] == fixture["citation"]


def test_malicious_fixture_stays_data_in_authority_request_and_evidence() -> None:
    fixture = json.loads((ROOT / "tests" / "fixtures" / "malicious-untrusted-content.json").read_text(encoding="utf-8"))
    fact_check = load_module("fact_check_x_malicious", ROOT / "scripts" / "fact_check_x.py")
    authority = load_module("authority_verify_malicious", ROOT / "modules" / "fact-check-x-authoritative-verify" / "scripts" / "authority_verify.py")
    comparison = {"schemaVersion": "fact-check-x/comparison@1", "question": "question", "knowledgePoints": [{"id": "K1", "description": fixture["platformAnswer"], "role": "direct", "core": True, "comparison": {"status": "single"}, "claims": {"fixture": {"covered": True, "claim": fixture["citation"]}}, "trustedAnchor": {"eligible": False}}]}
    with tempfile.TemporaryDirectory() as temporary, patch("subprocess.run") as subprocess_run, patch("urllib.request.urlopen") as network_open, patch("urllib.request.Request") as credential_request:
        run_root = Path(temporary)
        fact_check.build_requests(comparison, run_root / "authority" / "requests")
        request = json.loads((run_root / "authority" / "requests" / "K1.json").read_text(encoding="utf-8"))
        evidence = authority.acquire(request, fixture=[{"title": "fixture", "url": "https://evil.example/collect", "body": fixture["evidence"]}])
    subprocess_run.assert_not_called()
    network_open.assert_not_called()
    credential_request.assert_not_called()
    assert_boundary_paths(request["securityBoundary"], request_id="K1")
    assert evidence["securityBoundary"] == request["securityBoundary"]
    assert request["knowledgePoint"]["description"] == fixture["platformAnswer"]
    assert request["claims"]["fixture"]["claim"] == fixture["citation"]
    assert evidence["evidence"][0]["body"] == fixture["evidence"]
    assert evidence["evidence"][0]["url"] == "https://evil.example/collect"


def test_authority_rejects_external_endpoint_before_credentialed_request() -> None:
    authority = load_module("authority_verify_rejected_endpoint", ROOT / "modules" / "fact-check-x-authoritative-verify" / "scripts" / "authority_verify.py")
    old = os.environ.copy()
    try:
        os.environ["TRUSTED_SEARCH_KEY"] = TEST_KEY
        os.environ["FACTCHECK_TRUSTED_SEARCH_URL"] = "https://evil.example/dependable/search"
        with patch.object(authority.urllib.request, "Request") as credential_request, patch.object(authority, "open_no_redirect") as network_open, patch.object(authority.urllib.request, "build_opener") as network_opener:
            try:
                authority.trusted_search("question", "", 1)
            except authority.SkillError as exc:
                assert TEST_KEY not in str(exc)
            else:
                raise AssertionError("external endpoint must be rejected")
        credential_request.assert_not_called()
        network_open.assert_not_called()
        network_opener.assert_not_called()
    finally:
        os.environ.clear()
        os.environ.update(old)


def test_no_redirect_handler_refuses_redirect_request() -> None:
    assert NoRedirectHandler().redirect_request(MagicMock(), MagicMock(), 302, "redirect", MagicMock(), "https://evil.example/") is None


def test_redirects_fail_closed_without_forwarding_key() -> None:
    import trusted_search_config as config

    class RedirectingOpener:
        def __init__(self):
            self.requests = []

        def open(self, request, timeout):
            self.requests.append(request)
            raise urllib.error.HTTPError(request.full_url, 302, "redirect", {}, None)

    opener = RedirectingOpener()
    with patch.object(config.urllib.request, "build_opener", return_value=opener):
        try:
            config.open_no_redirect(config.urllib.request.Request(PRODUCTION, headers={"api-key": TEST_KEY}), timeout=1, context=config.trusted_search_ssl_context())
        except urllib.error.HTTPError as exc:
            assert exc.code == 302
            assert TEST_KEY not in str(exc)
        else:
            raise AssertionError("redirect must be rejected")
    assert len(opener.requests) == 1
    assert opener.requests[0].full_url == PRODUCTION
    assert opener.requests[0].get_header("Api-key") == TEST_KEY


def main() -> int:
    test_endpoint_gate()
    test_comparison_boundary_declares_concrete_run_relative_paths()
    test_authority_boundary_declares_concrete_run_relative_paths()
    test_malicious_fixture_stays_data_in_comparison_task()
    test_malicious_fixture_stays_data_in_authority_request_and_evidence()
    test_authority_rejects_external_endpoint_before_credentialed_request()
    test_no_redirect_handler_refuses_redirect_request()
    test_redirects_fail_closed_without_forwarding_key()
    print("PASS retry endpoint gate, redirects, and untrusted-content boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
