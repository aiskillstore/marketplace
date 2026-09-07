import importlib.util
import unittest
from unittest.mock import patch

from sharextract.models import ExtractedContent


@unittest.skipIf(importlib.util.find_spec("fastapi") is None, "service extra not installed")
class HttpApiTests(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from sharextract.http_api import create_app

        self.client = TestClient(create_app())

    def test_health_and_capabilities(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")

        caps = self.client.get("/v1/capabilities")
        self.assertEqual(caps.status_code, 200)
        self.assertIn("extractors", caps.json())

        with patch(
            "sharextract.http_api.get_adapter_health",
            return_value={
                "status": "ok",
                "summary": {"total": 1},
                "fixture_corpus": {"count": 1},
                "adapters": [{"name": "x-oembed", "status": "healthy"}],
            },
        ) as mocked:
            adapter_health = self.client.get(
                "/v1/health/adapters?adapter=x-oembed"
            )
        self.assertEqual(adapter_health.status_code, 200)
        self.assertEqual(adapter_health.json()["status"], "ok")
        self.assertEqual(
            adapter_health.json()["adapters"][0]["name"],
            "x-oembed",
        )
        mocked.assert_called_once()

    def test_extract_uses_core_contract(self):
        fake = ExtractedContent(
            source_url="https://example.com/a",
            canonical_url="https://example.com/a",
            platform="example",
            kind="article",
            extraction_method="test",
            confidence=1.0,
            title="Example",
            text="Body",
            markdown="Body",
        )
        with patch("sharextract.http_api.extract", return_value=fake):
            response = self.client.post(
                "/v1/extract",
                json={"url": "https://example.com/a"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Example")
        self.assertEqual(response.json()["text"], "Body")


if __name__ == "__main__":
    unittest.main()
