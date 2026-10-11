#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""Offline runtime regressions. Run: uv run skills/geo-sleuth/tests/test_runtime.py"""
from __future__ import annotations

import asyncio
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import _net
import _browser
import baidu_pano
import doctor
import gsv
import osm
import poi
import revimg


class NetworkTests(unittest.TestCase):
    def test_route_precedence(self):
        with patch.dict(os.environ, {"GEO_PROXY": "http://localhost:8123"}, clear=True):
            self.assertEqual(_net.resolve_proxy(), "http://localhost:8123")
            self.assertEqual(_net.resolve_proxy("http://localhost:8234"), "http://localhost:8234")
            self.assertIsNone(_net.resolve_proxy("direct"))
            self.assertIsNone(_net.resolve_proxy(""))
        with patch.dict(os.environ, {"HTTPS_PROXY": "http://localhost:9999"}, clear=True):
            self.assertIsNone(_net.resolve_proxy())

    @unittest.skipUnless(shutil.which("curl"), "curl required")
    def test_curl_reaches_direct_and_explicit_proxy_despite_ambient_settings(self):
        paths = []
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                paths.append(self.path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")
            def log_message(self, *args):
                pass
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with patch.dict(os.environ, {"HTTP_PROXY": "http://127.0.0.1:1", "http_proxy": "http://127.0.0.1:1",
                                         "ALL_PROXY": "http://127.0.0.1:1", "NO_PROXY": "*", "GEO_PROXY": "http://127.0.0.1:1"}):
                self.assertEqual(_net.fetch_bytes(base + "/direct", "direct"), b"ok")
                self.assertEqual(_net.fetch_bytes("http://example.invalid/proxied", base), b"ok")
            self.assertEqual(paths, ["/direct", "http://example.invalid/proxied"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_model_route_overrides_ambient_variables(self):
        with patch.dict(os.environ, {"GEO_PROXY": "http://chosen:8080", "https_proxy": "http://old:8080", "NO_PROXY": "*"}, clear=True):
            _net.model_proxy_env()
            self.assertEqual(os.environ["HTTPS_PROXY"], "http://chosen:8080")
            self.assertNotIn("https_proxy", os.environ)
            self.assertNotIn("NO_PROXY", os.environ)
            _net.model_proxy_env("direct")
            self.assertNotIn("HTTPS_PROXY", os.environ)
            self.assertEqual(os.environ["NO_PROXY"], "*")

    def test_baidu_near_forwards_proxy(self):
        with patch.object(baidu_pano, "fetch_bytes", return_value=b'{"content":null}') as fetch:
            self.assertIsNone(baidu_pano.near(35, 110, proxy="http://chosen:8080"))
            self.assertEqual(fetch.call_args.args[1], "http://chosen:8080")

    def test_all_poi_sources_forward_proxy(self):
        with patch.object(poi, "_curl", return_value='{}') as fetch:
            poi.search_so("school", None, 2, "direct")
            self.assertEqual(fetch.call_args.kwargs["proxy"], "direct")
            poi.search_sug("school", "http://chosen:8080")
            self.assertEqual(fetch.call_args.kwargs["proxy"], "http://chosen:8080")
        with patch.object(poi, "_curl", return_value='[]') as fetch:
            poi.search_osm("school", None, 2, "http://chosen:8080", "us")
            self.assertEqual(fetch.call_args.kwargs["proxy"], "http://chosen:8080")

    def test_intake_forwards_route_to_both_engines(self):
        import intake
        from PIL import Image
        commands = []
        def run(cmd, **kwargs):
            commands.append(cmd)
            return 0, "", ""
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            photo = root / "photo.jpg"
            Image.new("RGB", (100, 100), "white").save(photo)
            # Preparation writes files used by intake; run the actual small local helpers.
            original = intake._run
            def local_or_search(cmd, **kwargs):
                if any(str(part).endswith("revimg.py") for part in cmd):
                    return run(cmd, **kwargs)
                return original([sys.executable, *cmd[2:]], **kwargs)
            with patch.object(intake, "_run", side_effect=local_or_search), patch.object(sys, "argv", ["intake.py", str(photo), "--out-dir", str(root / "out"), "--no-ocr", "--max-variants", "1", "--proxy", "direct"]):
                intake.main()
            self.assertEqual(len(commands), 2)
            for cmd in commands:
                self.assertEqual(cmd[cmd.index("--proxy") + 1], "direct")
            self.assertEqual({cmd[cmd.index("--engines") + 1] for cmd in commands}, {"baidu", "yandex"})


class BrowserTests(unittest.IsolatedAsyncioTestCase):
    async def test_chromium_fallback_uses_same_route(self):
        browser = object()
        launch = AsyncMock(side_effect=[RuntimeError("Chrome absent"), browser])
        p = SimpleNamespace(chromium=SimpleNamespace(launch=launch))
        actual, label = await _browser.launch_browser(p, "socks5h://localhost:8123")
        self.assertIs(actual, browser)
        self.assertEqual(label, "Playwright Chromium")
        for call in launch.call_args_list:
            self.assertEqual(call.kwargs["proxy"]["server"], "socks5://localhost:8123")
        self.assertEqual(launch.call_args_list[0].kwargs["channel"], "chrome")
        self.assertNotIn("channel", launch.call_args_list[1].kwargs)

    async def test_explicit_direct_overrides_saved_browser_proxy(self):
        launch = AsyncMock(return_value=object())
        p = SimpleNamespace(chromium=SimpleNamespace(launch=launch))
        with patch.dict(os.environ, {"GEO_PROXY": "http://old:8080"}):
            await _browser.launch_browser(p, "direct")
        self.assertNotIn("proxy", launch.call_args.kwargs)
        self.assertIn("--no-proxy-server", launch.call_args.kwargs["args"])

    async def test_both_browsers_missing_gives_install_fix(self):
        p = SimpleNamespace(chromium=SimpleNamespace(launch=AsyncMock(side_effect=RuntimeError("missing"))))
        with self.assertRaisesRegex(RuntimeError, "uvx playwright install chromium"):
            await _browser.launch_browser(p, "direct")

    async def test_reverse_search_all_engines_get_selected_route(self):
        browser = SimpleNamespace(new_context=AsyncMock(), close=AsyncMock())
        manager = AsyncMock()
        manager.__aenter__.return_value = object()
        # Avoid requiring Playwright in this offline test's environment.
        fake = SimpleNamespace(async_playwright=lambda: manager)
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, {"playwright.async_api": fake}), patch.object(revimg, "launch_browser", AsyncMock(return_value=(browser, "test"))) as launch, patch.object(revimg, "_text", AsyncMock(return_value={"links": []})), patch.object(revimg, "_baidu", AsyncMock(return_value={"links": []})) as baidu, patch.object(revimg, "_yandex", AsyncMock(return_value={"links": []})):
            await revimg.run([Path("photo.jpg")], ["baidu", "yandex"], Path(folder), "direct", ["school"], ["bing"])
            self.assertEqual(launch.await_count, 3)
            self.assertTrue(all(call.args[1] == "direct" for call in launch.await_args_list))
            self.assertEqual(baidu.await_args.args[-1], "direct")


class DoctorTests(unittest.TestCase):
    def test_probe_distinguishes_transport_failure_and_service_block(self):
        for returncode, stdout, status in [(0, "200", "PASS"), (0, "429", "WARN"), (7, "000", "FAIL")]:
            with self.subTest(status=status), patch.object(doctor.subprocess, "run", return_value=SimpleNamespace(returncode=returncode, stdout=stdout)):
                row = doctor.probe(("service", "https://example.invalid"), "direct")
                self.assertEqual(row["status"], status)

    def test_local_checks_do_not_probe_network_or_print_proxy_credentials(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(doctor, "browser_check", AsyncMock(return_value=doctor.check("browser", "PASS", "ready"))), patch.object(doctor, "probe") as probe, patch.dict(os.environ, {"GEO_PROXY": "http://user:secret@localhost:8080"}):
            report = doctor.diagnose(False, None)
            probe.assert_not_called()
            self.assertTrue(report["ok"])
            self.assertNotIn("secret", json.dumps(report))
            self.assertEqual(report["connection"], "configured proxy")


QH = '[out:json][timeout:180];(area["name"="青海省"];area["name:zh"="青海省"];area["name:zh-Hans"="青海省"];)->.searchArea;nwr["power"="line"](area.searchArea);out geom tags;'
LINE = {"type": "way", "id": 1, "geometry": [{"lat": 37.7, "lon": 95.3}, {"lat": 37.8, "lon": 95.4}], "tags": {"power": "line"}}


def count(n):
    return {"elements": [{"type": "count", "tags": {"total": str(n)}}]}


class OverpassMirrorTests(unittest.TestCase):
    """One mirror answered a whole-province --area query with a clean empty result while others had thousands of lines; it got cached."""

    def run_with(self, replies, ql=QH):
        calls = []

        def post(ep, q, proxy, timeout):
            calls.append(ep)
            return replies(ep, q)

        with tempfile.TemporaryDirectory() as d, patch.object(osm, "_post", side_effect=post), patch.object(osm.time, "sleep"):
            data = osm.run(ql, None, Path(d))
            cached = list(Path(d).glob("*.json"))
        return data, calls, cached

    def test_empty_from_one_mirror_is_checked_on_another(self):
        data, calls, cached = self.run_with(lambda ep, q: ({"elements": []} if ep == osm.ENDPOINTS[0] else {"elements": [LINE]}, ""))
        self.assertEqual(len(data["elements"]), 1)
        self.assertEqual(calls, osm.ENDPOINTS[:2])
        self.assertEqual(len(cached), 1)

    def test_empty_confirmed_by_two_mirrors_is_cached(self):
        data, calls, cached = self.run_with(lambda ep, q: ({"elements": []}, ""))
        self.assertEqual(data["elements"], [])
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(cached), 1)

    def test_unconfirmed_empty_is_returned_but_not_cached(self):
        data, calls, cached = self.run_with(lambda ep, q: ({"elements": []}, "") if ep == osm.ENDPOINTS[0] else (None, "503"))
        self.assertEqual(data["elements"], [])
        self.assertEqual(cached, [])
        self.assertEqual(len(calls), len(osm.ENDPOINTS))           # one round, no retry sleeps

    def test_zero_area_count_needs_a_second_mirror(self):
        ql = '[out:json][timeout:120];(area["name"="青海省"];)->.a;.a out count;'
        data, _, _ = self.run_with(lambda ep, q: (count(0) if ep == osm.ENDPOINTS[0] else count(1), ""), ql)
        self.assertEqual(data["elements"][0]["tags"]["total"], "1")

    def test_bbox_empty_is_trusted(self):
        ql = '[out:json][timeout:180];nwr["power"="line"](37.6,95.2,37.8,95.4);out geom tags;'
        _, calls, cached = self.run_with(lambda ep, q: ({"elements": []}, ""), ql)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(cached), 1)

    def test_failure_names_every_mirror(self):
        replies = {osm.ENDPOINTS[0]: (None, "HTTP 406: Not Acceptable"), osm.ENDPOINTS[1]: (None, "HTTP 500: Internal Server Error"),
                   osm.ENDPOINTS[2]: (None, "HTTP 504: server too busy")}
        with self.assertRaises(SystemExit) as cm:
            self.run_with(lambda ep, q: replies[ep])
        for code in ("406", "500", "504"):
            self.assertIn(code, str(cm.exception))

    def test_error_remark_not_cached(self):
        def replies(ep, q):
            if ep == osm.ENDPOINTS[0]:
                return {"elements": [], "remark": "runtime error: Query timed out"}, ""
            return {"elements": [LINE]}, ""
        data, _, cached = self.run_with(replies)
        self.assertEqual(len(data["elements"]), 1)
        self.assertEqual(len(cached), 1)


class StreetViewTests(unittest.TestCase):
    def test_lookup_replies(self):
        ok = json.dumps([[0], [[1], [2, "Z4kP7jsHKunVOqfsg_khyw"], None, [None, None, [["168 W 60th Ave"], ["Vancouver"]]], None,
                               [[None, [[None, None, 49.21598, -123.10927], None, [90.4]], None, [[]], None, None, None, None, []]],
                               [None] * 7 + [[2024, 5]]]])
        cases = {
            ok: "Z4kP7jsHKunVOqfsg_khyw",
            '[[5,"generic","Search returned no images."]]': None,
        }
        for reply, want in cases.items():
            with patch.object(gsv, "_curl", return_value=reply.encode()):
                res = gsv.near(49.2161, -123.1093, 50, None)
                self.assertEqual(res and res["id"], want)
        ok_res = None
        with patch.object(gsv, "_curl", return_value=ok.encode()):
            ok_res = gsv.near(49.2161, -123.1093, 50, None)
        self.assertEqual(ok_res["date"], "2024-05")
        for bad in ('[[5,"generic","GeoPhotoService.SingleImageSearch is decommissioned and turned down."]]',
                    '[3,"Invalid JSON payload received."]', "<html>blocked</html>", ""):
            with patch.object(gsv, "_curl", return_value=bad.encode()), self.assertRaises(gsv.ServiceError):
                gsv.near(49.2161, -123.1093, 50, None)


if __name__ == "__main__":
    unittest.main()
