import contextlib
import importlib.util
import io
import json
import os
import pathlib
import re
import sys
import tempfile
import threading
import unittest
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse


ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "seoul-weather-risk" / "scripts" / "seoul_weather_risk.py"
SPEC = importlib.util.spec_from_file_location("seoul_weather_risk", MODULE_PATH)
seoul_weather_risk = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = seoul_weather_risk
SPEC.loader.exec_module(seoul_weather_risk)


PRODUCT_ID = "weather_place_risk_window"
PRODUCT_IDS = sorted(seoul_weather_risk.EXACT_PRODUCT_IDS)


def bundle(product_ids=PRODUCT_IDS):
    return {
        "bundle_id": "seoul-weather-risk",
        "registration_ready": True,
        "products": [
            {"product_id": product_id, "publication_id": "publication-1", "registration_ready": True, "blockers": []}
            for product_id in product_ids
        ],
    }


def detail(product_id=PRODUCT_ID):
    return {
        "bundle_id": "seoul-weather-risk",
        "product_id": product_id,
        "publication_id": "publication-1",
        "registration_ready": True,
        "blockers": [],
        "metadata": {
            "columns": [
                {"name": "place_id", "type": "string"},
                {"name": "forecast_at", "type": "string"},
                {"name": "risk_labels", "type": "string"},
            ]
        },
    }


def data(product_id=PRODUCT_ID, limit=100):
    return {
        "bundle_id": "seoul-weather-risk",
        "product_id": product_id,
        "publication_id": "publication-1",
        "row_count": 1,
        "limit": limit,
        "has_more": False,
        "next_cursor": None,
        "rows": [{"place_id": "place-a", "forecast_at": "2026-08-05T09:00:00+09:00", "risk_labels": "폭염후보"}],
    }


class MockApi:
    def __init__(self):
        self.responses = {}
        self.requests = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self.handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def handler(self):
        api = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                query = parse_qs(parsed.query)
                api.requests.append({"path": parsed.path, "query": query, "authorization": self.headers.get("Authorization")})
                entry = api.responses.get(parsed.path, (404, "application/problem+json", {"code": "unknown_product", "detail": "not found"}, {}))
                status, content_type, body, headers = entry(query) if callable(entry) else entry
                encoded = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                for name, value in headers.items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, *_args):
                return

        return Handler

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.server.server_port}/"

    def start(self):
        self.thread.start()
        return self

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()


class QueryWindowClipTests(unittest.TestCase):
    def test_window_sort_key_normalizes_iso_and_timezone_suffix(self):
        self.assertEqual(
            seoul_weather_risk._window_sort_key("2026-08-24T17:00:00+09:00"),
            "2026-08-24 17:00:00",
        )
        self.assertEqual(
            seoul_weather_risk._window_sort_key("2026-08-24 17:00:00"),
            "2026-08-24 17:00:00",
        )

    def test_intersect_query_window_clips_to_overlap(self):
        self.assertEqual(
            seoul_weather_risk._intersect_query_window(
                "2026-08-24 00:00:00",
                "2026-08-24 23:59:59",
                "2026-08-24 17:00:00",
                "2026-08-27 00:00:00",
            ),
            ("2026-08-24 17:00:00", "2026-08-24 23:59:59"),
        )

    def test_intersect_query_window_returns_none_when_ranges_do_not_overlap(self):
        self.assertIsNone(
            seoul_weather_risk._intersect_query_window(
                "2026-08-11 00:00:00",
                "2026-08-17 23:59:59",
                "2026-08-24 17:00:00",
                "2026-08-27 00:00:00",
            )
        )


class ApiClientTests(unittest.TestCase):
    def setUp(self):
        self.api = MockApi().start()
        self.proxy_base_url_env = "KSKILL_PROXY_BASE_URL"
        self.previous = {name: os.environ.get(name) for name in (self.proxy_base_url_env, "KSKILL_SEOUL_WEATHER_RISK_API_KEY")}
        os.environ[self.proxy_base_url_env] = self.api.base_url
        os.environ["KSKILL_SEOUL_WEATHER_RISK_API_KEY"] = "legacy-user-key-must-not-be-used"
        self.api.responses = {
            "/v1/ask-seoul/weather-risk/bundle": (200, "application/json", bundle(), {}),
            "/v1/ask-seoul/weather-risk/product": (200, "application/json", detail(), {}),
            "/v1/ask-seoul/weather-risk/data": (200, "application/json", data(), {}),
        }

    def tearDown(self):
        self.api.close()
        for name, value in self.previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_query_uses_narrow_proxy_paths_without_user_bearer_auth(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = seoul_weather_risk.run([
                "query", "--product-id", PRODUCT_ID, "--filter", "place_id=place-a",
                "--from", "2026-08-01", "--to", "2026-08-05", "--limit", "100", "--cursor", "cursor-1",
            ])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["row_count"], 1)
        self.assertEqual([request["path"] for request in self.api.requests], [
            "/v1/ask-seoul/weather-risk/bundle",
            "/v1/ask-seoul/weather-risk/product",
            "/v1/ask-seoul/weather-risk/data",
        ])
        query = self.api.requests[-1]["query"]
        self.assertEqual(query, {
            "place_id": ["place-a"],
            "from": ["2026-08-01 00:00:00"],
            "to": ["2026-08-05 23:59:59"],
            "limit": ["100"],
            "cursor": ["cursor-1"],
        })
        self.assertTrue(all(request["authorization"] is None for request in self.api.requests))

    def test_fast_query_uses_only_data_route_without_metadata_round_trips(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = seoul_weather_risk.run([
                "query", "--fast", "--product-id", PRODUCT_ID,
                "--admin-dong", "잠실본동", "--from", "2026-08-05", "--to", "2026-08-05", "--limit", "100",
            ])

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["row_count"], 1)
        self.assertEqual([request["path"] for request in self.api.requests], [
            "/v1/ask-seoul/weather-risk/data",
        ])
        self.assertEqual(self.api.requests[0]["query"], {
            "place_id": ["seoul_admd_1171065000"],
            "from": ["2026-08-05 00:00:00"],
            "to": ["2026-08-05 23:59:59"],
            "limit": ["100"],
        })
        self.assertIsNone(self.api.requests[0]["authorization"])

    def test_local_direct_settings_are_ignored_and_hosted_proxy_remains_the_only_route(self):
        with patch.dict(os.environ, {
            "KSKILL_LOCAL_DIRECT": "1",
            "ASK_SEOUL_SKILL_API_BASE_URL": self.api.base_url,
            "MARKETPLACE_API_KEY": "legacy-marketplace-key-must-not-be-used",
        }, clear=False):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = seoul_weather_risk.run(["catalog"])

        self.assertEqual(code, 0)
        self.assertEqual([request["path"] for request in self.api.requests], [
            "/v1/ask-seoul/weather-risk/bundle",
        ])
        self.assertIsNone(self.api.requests[0]["authorization"])
        self.assertNotIn("legacy-marketplace-key-must-not-be-used", stdout.getvalue())

    def test_query_keeps_explicit_datetime_bounds_unchanged(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = seoul_weather_risk.run([
                "query", "--product-id", PRODUCT_ID, "--filter", "place_id=place-a",
                "--from", "2026-08-01 09:00:00", "--to", "2026-08-01 18:00:00", "--limit", "100",
            ])

        self.assertEqual(code, 0)
        self.assertEqual(self.api.requests[-1]["query"], {
            "place_id": ["place-a"],
            "from": ["2026-08-01 09:00:00"],
            "to": ["2026-08-01 18:00:00"],
            "limit": ["100"],
        })

    def test_query_clips_calendar_day_to_available_window(self):
        def data_response(query):
            if query.get("from") == ["2026-08-24 00:00:00"] and query.get("to") == ["2026-08-24 23:59:59"]:
                return (422, "application/problem+json", {
                    "title": "query window unavailable",
                    "status": 422,
                    "detail": {
                        "requested_from_at": "2026-08-24 00:00:00",
                        "requested_to_at": "2026-08-24 23:59:59",
                        "available_from_at": "2026-08-24 17:00:00",
                        "available_to_at": "2026-08-27 00:00:00",
                        "publication_id": "publication-1",
                    },
                }, {})
            if query.get("from") == ["2026-08-24 17:00:00"] and query.get("to") == ["2026-08-24 23:59:59"]:
                return (200, "application/json", data(), {})
            return (500, "application/json", {"error": "unexpected query"}, {})

        self.api.responses["/v1/ask-seoul/weather-risk/data"] = data_response
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = seoul_weather_risk.run([
                "query", "--fast", "--product-id", PRODUCT_ID,
                "--admin-dong", "잠실본동", "--from", "2026-08-24", "--to", "2026-08-24", "--limit", "100",
            ])

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["row_count"], 1)
        self.assertEqual([request["path"] for request in self.api.requests], [
            "/v1/ask-seoul/weather-risk/data",
            "/v1/ask-seoul/weather-risk/data",
        ])
        self.assertEqual(self.api.requests[0]["query"]["from"], ["2026-08-24 00:00:00"])
        self.assertEqual(self.api.requests[0]["query"]["to"], ["2026-08-24 23:59:59"])
        self.assertEqual(self.api.requests[1]["query"], {
            "place_id": ["seoul_admd_1171065000"],
            "from": ["2026-08-24 17:00:00"],
            "to": ["2026-08-24 23:59:59"],
            "limit": ["100"],
        })

    def test_query_window_without_overlap_fails_with_available_bounds(self):
        self.api.responses["/v1/ask-seoul/weather-risk/data"] = (
            422,
            "application/problem+json",
            {
                "title": "query window unavailable",
                "status": 422,
                "request_id": "req-window",
                "detail": {
                    "requested_from_at": "2026-08-11 00:00:00",
                    "requested_to_at": "2026-08-17 23:59:59",
                    "available_from_at": "2026-08-24 17:00:00",
                    "available_to_at": "2026-08-27 00:00:00",
                    "publication_id": "publication-1",
                },
            },
            {},
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run([
                "query", "--fast", "--product-id", PRODUCT_ID,
                "--admin-dong", "잠실본동", "--from", "2026-08-11", "--to", "2026-08-17",
            ])

        error = json.loads(stderr.getvalue())["error"]
        self.assertEqual(code, 2)
        self.assertEqual(error["code"], "query_window_unavailable")
        self.assertIn("겹치지 않습니다", error["message"])
        self.assertEqual(error["details"]["available_from_at"], "2026-08-24 17:00:00")
        self.assertEqual(error["details"]["available_to_at"], "2026-08-27 00:00:00")
        self.assertEqual(error["details"]["request_id"], "req-window")
        self.assertEqual(len(self.api.requests), 1)

    def test_query_window_problem_without_available_bounds_does_not_retry(self):
        self.api.responses["/v1/ask-seoul/weather-risk/data"] = (
            422,
            "application/problem+json",
            {"title": "query window unavailable", "detail": "safe problem detail", "code": "query_window_unavailable"},
            {},
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run([
                "query", "--fast", "--product-id", PRODUCT_ID,
                "--admin-dong", "잠실본동", "--from", "2026-08-24", "--to", "2026-08-24",
            ])

        error = json.loads(stderr.getvalue())["error"]
        self.assertEqual(code, 2)
        self.assertEqual(error["code"], "query_window_unavailable")
        self.assertEqual(error["message"], "safe problem detail")
        self.assertEqual(len(self.api.requests), 1)

    def test_paged_query_does_not_retry_unavailable_window(self):
        self.api.responses["/v1/ask-seoul/weather-risk/data"] = (
            422,
            "application/problem+json",
            {
                "title": "query window unavailable",
                "status": 422,
                "detail": {
                    "requested_from_at": "2026-08-24 00:00:00",
                    "requested_to_at": "2026-08-24 23:59:59",
                    "available_from_at": "2026-08-24 17:00:00",
                    "available_to_at": "2026-08-27 00:00:00",
                },
            },
            {},
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run([
                "query", "--fast", "--product-id", PRODUCT_ID,
                "--admin-dong", "잠실본동", "--from", "2026-08-24", "--to", "2026-08-24",
                "--cursor", "cursor-1",
            ])

        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "query_window_unavailable")
        self.assertEqual(len(self.api.requests), 1)

    def test_query_maps_admin_dong_to_place_id_before_proxy_request(self):
        self.api.responses["/v1/ask-seoul/weather-risk/data"] = (
            200, "application/json", data(limit=1), {},
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = seoul_weather_risk.run([
                "query", "--product-id", PRODUCT_ID,
                "--admin-dong", "잠실본동", "--limit", "1",
            ])

        self.assertEqual(code, 0)
        query = self.api.requests[-1]["query"]
        self.assertEqual(query, {
            "place_id": ["seoul_admd_1171065000"],
            "limit": ["1"],
        })
        self.assertNotIn("admin_dong", query)
        self.assertNotIn("gu", query)

    def test_query_rejects_gu_without_admin_dong(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run([
                "query", "--product-id", PRODUCT_ID, "--gu", "송파구",
            ])

        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "invalid_location_input")
        self.assertEqual(len(self.api.requests), 2)

    def test_query_rejects_admin_dong_with_place_id_filter(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run([
                "query", "--product-id", PRODUCT_ID,
                "--admin-dong", "잠실본동", "--filter", "place_id=place-a",
            ])

        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "conflicting_location_input")
        self.assertEqual(len(self.api.requests), 2)

    def test_bundle_single_product_drift_fails_closed(self):
        self.api.responses["/v1/ask-seoul/weather-risk/bundle"] = (200, "application/json", bundle([]), {})
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run(["catalog"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "response_contract_invalid")

    def test_malformed_success_response_fails_closed(self):
        self.api.responses["/v1/ask-seoul/weather-risk/bundle"] = (200, "application/json", b"not-json", {})
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run(["catalog"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "malformed_response")

    def test_http_problem_statuses_are_typed_and_preserve_safe_details(self):
        endpoint = "/v1/ask-seoul/weather-risk/bundle"
        cases = {
            401: "api_key_missing",
            403: "api_key_forbidden",
            404: "unknown_product",
            409: "cursor_expired",
            429: "rate_limited",
            503: "product_not_ready",
        }
        for status, expected_code in cases.items():
            with self.subTest(status=status):
                headers = {"Retry-After": "60"} if status == 429 else {}
                self.api.responses[endpoint] = (status, "application/problem+json", {
                    "title": "API failure", "detail": "safe problem detail", "code": expected_code,
                    "request_id": "req-1", "product_id": PRODUCT_ID,
                }, headers)
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    code = seoul_weather_risk.run(["catalog"])
                error = json.loads(stderr.getvalue())["error"]
                self.assertEqual(code, 2)
                self.assertEqual(error["code"], expected_code)
                self.assertEqual(error["details"]["status"], status)
                self.assertEqual(error["details"]["request_id"], "req-1")
                if status == 429:
                    self.assertEqual(error["details"]["retry_after"], "60")

    def test_disabled_proxy_never_echoes_legacy_user_credentials(self):
        os.environ[self.proxy_base_url_env] = "off"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run(["preflight"])
        self.assertEqual(code, 2)
        self.assertNotIn("legacy-user-key-must-not-be-used", stderr.getvalue())
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "proxy_disabled")

    def test_non_https_base_url_is_rejected_except_loopback_mock(self):
        with self.assertRaisesRegex(seoul_weather_risk.SkillError, "HTTPS"):
            seoul_weather_risk._api_config({
                self.proxy_base_url_env: "http://example.test",
            })
        config = seoul_weather_risk._api_config({
            self.proxy_base_url_env: self.api.base_url,
        })
        self.assertFalse(config.base_url.endswith("/"))
        with self.assertRaisesRegex(seoul_weather_risk.SkillError, "origin"):
            seoul_weather_risk._api_config({
                self.proxy_base_url_env: "https://api.example.test/untrusted-path",
            })

    def test_redirect_is_not_followed_through_proxy_client(self):
        endpoint = "/v1/ask-seoul/weather-risk/bundle"
        self.api.responses[endpoint] = (302, "application/problem+json", {"detail": "redirect blocked"}, {
            "Location": f"{self.api.base_url}redirect-target",
        })
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = seoul_weather_risk.run(["catalog"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "api_error")
        self.assertEqual([request["path"] for request in self.api.requests], [endpoint])


class LocationMappingTests(unittest.TestCase):
    def test_admin_dong_reference_has_expected_version_and_unique_place_ids(self):
        mapping_path = ROOT / "seoul-weather-risk" / "references" / "admin-dong-place-map.json"
        payload = json.loads(mapping_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["mapping_version"], "kma_admin_dong_grid_20260325")
        self.assertEqual(len(payload["locations"]), 427)
        self.assertEqual(len({row["place_id"] for row in payload["locations"]}), 427)
        self.assertEqual(
            sorted(row["gu"] for row in payload["locations"] if row["admin_dong"] == "신사동"),
            ["강남구", "관악구"],
        )

    def test_resolve_admin_dong_returns_canonical_place_id(self):
        resolved = seoul_weather_risk._resolve_admin_dong("  잠실본동  ")

        self.assertEqual(resolved, {
            "admin_dong": "잠실본동",
            "gu": "송파구",
            "place_id": "seoul_admd_1171065000",
        })

    def test_resolve_admin_dong_normalizes_unicode_nfc(self):
        resolved = seoul_weather_risk._resolve_admin_dong(unicodedata.normalize("NFD", "잠실본동"))

        self.assertEqual(resolved["place_id"], "seoul_admd_1171065000")

    def test_resolve_admin_dong_normalizes_internal_whitespace(self):
        resolved = seoul_weather_risk._resolve_admin_dong(unicodedata.normalize("NFD", "  잠실 본동  "))

        self.assertEqual(resolved, {
            "admin_dong": "잠실본동",
            "gu": "송파구",
            "place_id": "seoul_admd_1171065000",
        })

    def test_resolve_admin_dong_recognizes_map_derived_je_alias(self):
        resolved = seoul_weather_risk._resolve_admin_dong("성수2가3동")

        self.assertEqual(resolved, {
            "admin_dong": "성수2가제3동",
            "gu": "성동구",
            "place_id": "seoul_admd_1120069000",
        })

    def test_resolve_admin_dong_resolves_every_map_derived_je_variant_with_gu(self):
        _version, locations = seoul_weather_risk._load_location_mapping()
        je_rows = [row for row in locations if "제" in row["admin_dong"]]

        self.assertTrue(je_rows)
        for row in je_rows:
            with self.subTest(row=row):
                alias = re.sub(r"제(?=\d)", "", row["admin_dong"])
                self.assertEqual(seoul_weather_risk._resolve_admin_dong(alias, row["gu"]), row)

    def test_resolve_admin_dong_does_not_omit_non_numeric_je(self):
        self.assertEqual(
            seoul_weather_risk._resolve_admin_dong("제기동", "동대문구")["place_id"],
            "seoul_admd_1123054500",
        )

        with self.assertRaises(seoul_weather_risk.SkillError) as raised:
            seoul_weather_risk._resolve_admin_dong("기동", "동대문구")
        self.assertEqual(raised.exception.code, "unknown_admin_dong")

    def test_resolve_admin_dong_accepts_numeric_punctuation_aliases(self):
        expected = "seoul_admd_1111061500"

        self.assertEqual(
            seoul_weather_risk._resolve_admin_dong("종로1.2.3.4가동")["place_id"],
            expected,
        )
        self.assertEqual(
            seoul_weather_risk._resolve_admin_dong("종로1·2·3·4가동")["place_id"],
            expected,
        )
        self.assertEqual(
            seoul_weather_risk._resolve_admin_dong("종로1234가동")["place_id"],
            expected,
        )

    def test_resolve_admin_dong_resolves_every_dot_variant_with_gu(self):
        _version, locations = seoul_weather_risk._load_location_mapping()
        dotted_rows = [row for row in locations if "." in row["admin_dong"]]

        self.assertTrue(dotted_rows)
        for row in dotted_rows:
            with self.subTest(row=row, variant="canonical"):
                self.assertEqual(seoul_weather_risk._resolve_admin_dong(row["admin_dong"], row["gu"]), row)
            with self.subTest(row=row, variant="middle_dot"):
                self.assertEqual(seoul_weather_risk._resolve_admin_dong(row["admin_dong"].replace(".", "·"), row["gu"]), row)
            with self.subTest(row=row, variant="omitted_dot"):
                self.assertEqual(seoul_weather_risk._resolve_admin_dong(row["admin_dong"].replace(".", ""), row["gu"]), row)

    def test_alias_keys_generate_combined_je_and_punctuation_variants(self):
        _version, locations = seoul_weather_risk._load_location_mapping()
        row = next(row for row in locations if row["admin_dong"] == "면목제3.8동")

        aliases = seoul_weather_risk._alias_keys(row["admin_dong"])
        self.assertTrue({"면목3·8동", "면목38동"}.issubset(aliases))

    def test_resolve_admin_dong_resolves_every_generated_map_alias_with_gu(self):
        _version, locations = seoul_weather_risk._load_location_mapping()
        checked_aliases = 0
        for row in locations:
            for alias in seoul_weather_risk._alias_keys(row["admin_dong"]):
                if alias == row["admin_dong"]:
                    continue
                with self.subTest(row=row, alias=alias):
                    self.assertEqual(seoul_weather_risk._resolve_admin_dong(alias, row["gu"]), row)
                checked_aliases += 1

        self.assertGreater(checked_aliases, 0)

    def test_location_indexes_retain_colliding_aliases_and_resolve_exact_first(self):
        alias_source = {"admin_dong": "예제1동", "gu": "가구", "place_id": "seoul_admd_0000000001"}
        canonical_match = {"admin_dong": "예1동", "gu": "나구", "place_id": "seoul_admd_0000000002"}
        locations = [alias_source, canonical_match]

        canonical_index, alias_index = seoul_weather_risk._location_indexes(locations)
        self.assertEqual(canonical_index["예1동"], [canonical_match])
        self.assertEqual(alias_index["예1동"], locations)

        with patch.object(seoul_weather_risk, "_load_location_mapping", return_value=("test", locations)):
            self.assertEqual(seoul_weather_risk._resolve_admin_dong("예1동"), canonical_match)

            with self.assertRaises(seoul_weather_risk.SkillError) as raised:
                seoul_weather_risk._resolve_admin_dong("예 1동")
            self.assertEqual(raised.exception.code, "ambiguous_admin_dong")
            self.assertEqual(raised.exception.details["candidates"], locations)
            self.assertEqual(seoul_weather_risk._resolve_admin_dong("예 1동", "가구"), alias_source)

    def test_resolve_admin_dong_requires_gu_for_duplicate_name(self):
        with self.assertRaises(seoul_weather_risk.SkillError) as raised:
            seoul_weather_risk._resolve_admin_dong("신사동")

        self.assertEqual(raised.exception.code, "ambiguous_admin_dong")
        self.assertEqual(raised.exception.details["candidates"], [
            {"admin_dong": "신사동", "gu": "강남구", "place_id": "seoul_admd_1168051000"},
            {"admin_dong": "신사동", "gu": "관악구", "place_id": "seoul_admd_1162068500"},
        ])

    def test_resolve_admin_dong_uses_gu_to_disambiguate(self):
        resolved = seoul_weather_risk._resolve_admin_dong("신사동", "강남구")

        self.assertEqual(resolved["place_id"], "seoul_admd_1168051000")

    def test_resolve_admin_dong_rejects_unknown_or_broad_dong_and_gu(self):
        with self.assertRaises(seoul_weather_risk.SkillError) as unknown_dong:
            seoul_weather_risk._resolve_admin_dong("없는동")
        self.assertEqual(unknown_dong.exception.code, "unknown_admin_dong")

        for admin_dong in ("성수동", "종로"):
            with self.subTest(admin_dong=admin_dong):
                with self.assertRaises(seoul_weather_risk.SkillError) as broad_dong:
                    seoul_weather_risk._resolve_admin_dong(admin_dong)
                self.assertEqual(broad_dong.exception.code, "unknown_admin_dong")

        with self.assertRaises(seoul_weather_risk.SkillError) as unknown_gu:
            seoul_weather_risk._resolve_admin_dong("잠실본동", "없는구")
        self.assertEqual(unknown_gu.exception.code, "unknown_gu")

        with self.assertRaises(seoul_weather_risk.SkillError) as wrong_gu:
            seoul_weather_risk._resolve_admin_dong("잠실본동", "강남구")
        self.assertEqual(wrong_gu.exception.code, "unknown_admin_dong")

    def test_load_location_mapping_rejects_invalid_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid_path = pathlib.Path(directory) / "mapping.json"
            invalid_path.write_text(json.dumps({
                "mapping_version": "wrong-version",
                "locations": [],
            }), encoding="utf-8")

            with self.assertRaises(seoul_weather_risk.SkillError) as raised:
                seoul_weather_risk._load_location_mapping(invalid_path)

        self.assertEqual(raised.exception.code, "location_mapping_invalid")


class CliTests(unittest.TestCase):
    def test_preflight_is_user_secret_free_and_offline(self):
        proxy_base_url_env = "KSKILL_PROXY_BASE_URL"
        previous = {name: os.environ.get(name) for name in (proxy_base_url_env, "KSKILL_SEOUL_WEATHER_RISK_API_KEY")}
        self.addCleanup(lambda: [os.environ.pop(name, None) if value is None else os.environ.__setitem__(name, value) for name, value in previous.items()])
        os.environ[proxy_base_url_env] = "https://proxy.example.test/"
        os.environ["KSKILL_SEOUL_WEATHER_RISK_API_KEY"] = "legacy-user-key-must-not-be-used"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = seoul_weather_risk.run(["preflight"])
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["mode"], "hosted_proxy")
        self.assertFalse(payload["live_network"])
        self.assertTrue(payload["proxy_base_url_configured"])
        self.assertEqual(set(payload), {"status", "mode", "live_network", "proxy_base_url_configured"})
        self.assertNotIn("legacy-user-key-must-not-be-used", stdout.getvalue())

    def test_parser_has_no_credential_or_base_url_option(self):
        parser = seoul_weather_risk._parser()
        option_strings = {option for action in parser._actions for option in action.option_strings}
        self.assertFalse(any("key" in option.lower() or "url" in option.lower() for option in option_strings))


if __name__ == "__main__":
    unittest.main()
