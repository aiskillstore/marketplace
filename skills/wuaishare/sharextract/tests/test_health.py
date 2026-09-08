import json
import os
import tempfile
import unittest
from unittest.mock import patch

from sharextract.health import (
    _optional_dependency_available,
    get_adapter_health,
    render_health_markdown,
)


class AdapterHealthTests(unittest.TestCase):
    def test_offline_health_validates_registry_router_and_fixture_corpus(self):
        report = get_adapter_health()
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["summary"]["total"], 33)
        self.assertEqual(report["summary"]["unhealthy"], 0)
        self.assertEqual(report["summary"]["degraded"], 0)
        self.assertEqual(report["fixture_corpus"]["count"], 33)
        self.assertEqual(report["fixture_corpus"]["issues"], [])

        by_name = {item["name"]: item for item in report["adapters"]}
        self.assertEqual(by_name["chatgpt-share"]["stability"], "page_structure")
        self.assertEqual(by_name["rss-atom"]["integrated_in"], "generic-web")
        self.assertEqual(
            by_name["rss-atom"]["checks"][0]["status"],
            "pass",
        )
        self.assertIn(
            by_name["yt-dlp"]["status"],
            {"healthy", "optional_unavailable"},
        )
        self.assertIn(
            by_name["kuaishou-atlas"]["status"],
            {"healthy", "optional_unavailable"},
        )

    def test_playwright_dependency_requires_runtime(self):
        with patch(
            "sharextract.health.importlib.util.find_spec",
            return_value=None,
        ):
            self.assertFalse(
                _optional_dependency_available("playwright-chromium")
            )

        with tempfile.NamedTemporaryFile() as handle:
            with patch(
                "sharextract.health.importlib.util.find_spec",
                return_value=object(),
            ), patch.dict(
                os.environ,
                {"SHAREXTRACT_BROWSER_EXECUTABLE": handle.name},
                clear=False,
            ):
                self.assertTrue(
                    _optional_dependency_available("playwright-chromium")
                )

    def test_atlas_reports_optional_unavailable_when_browser_missing(self):
        with patch(
            "sharextract.health._optional_dependency_available",
            side_effect=lambda name: False
            if name == "playwright-chromium"
            else True,
        ):
            report = get_adapter_health(
                adapter_names=["kuaishou-atlas"]
            )
        self.assertEqual(
            report["adapters"][0]["status"],
            "optional_unavailable",
        )
        dependency_check = next(
            check
            for check in report["adapters"][0]["checks"]
            if check["name"] == "optional_dependency"
        )
        self.assertEqual(
            dependency_check["dependency"],
            "playwright-chromium",
        )
        self.assertEqual(dependency_check["status"], "unavailable")

    def test_health_can_target_one_adapter(self):
        report = get_adapter_health(adapter_names=["x-oembed"])
        self.assertEqual(report["summary"]["total"], 1)
        self.assertEqual(report["adapters"][0]["name"], "x-oembed")
        self.assertEqual(report["adapters"][0]["status"], "healthy")

    def test_unknown_adapter_is_rejected(self):
        with self.assertRaises(ValueError):
            get_adapter_health(adapter_names=["does-not-exist"])

    def test_live_check_uses_core_extract_contract(self):
        fake = type(
            "FakeResult",
            (),
            {
                "platform": "x",
                "extraction_method": "documented_oembed",
                "title": "Example",
                "has_body": True,
            },
        )()
        with patch("sharextract.health.extract", return_value=fake) as mocked:
            report = get_adapter_health(
                live=True,
                adapter_names=["x-oembed"],
            )
        mocked.assert_called_once()
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["adapters"][0]["live"]["status"], "pass")

    def test_live_check_retries_one_transient_exception(self):
        fake = type(
            "FakeResult",
            (),
            {
                "platform": "x",
                "extraction_method": "documented_oembed",
                "title": "Example",
                "has_body": True,
            },
        )()
        with patch(
            "sharextract.health.extract",
            side_effect=[RuntimeError("temporary"), fake],
        ) as mocked:
            report = get_adapter_health(
                live=True,
                adapter_names=["x-oembed"],
            )
        self.assertEqual(mocked.call_count, 2)
        live = report["adapters"][0]["live"]
        self.assertEqual(live["status"], "pass")
        self.assertEqual(live["attempts"], 2)
        self.assertEqual(live["transient_errors"], ["temporary"])

    def test_markdown_renderer_contains_matrix(self):
        report = get_adapter_health(adapter_names=["x-oembed"])
        rendered = render_health_markdown(report)
        self.assertIn("# ShareXtract Adapter Health", rendered)
        self.assertIn("| x-oembed | x | documented | healthy |", rendered)

    def test_report_is_json_serializable(self):
        json.dumps(get_adapter_health(), ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
