import importlib.util
import unittest
from unittest.mock import patch

from sharextract.models import ExtractedContent


def fake_result():
    return ExtractedContent(
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


@unittest.skipIf(importlib.util.find_spec("mcp") is None, "mcp extra not installed")
class McpServerTests(unittest.TestCase):
    def test_impl_returns_same_core_contract(self):
        from sharextract.mcp_server import extract_public_url_impl

        with patch("sharextract.mcp_server.extract", return_value=fake_result()):
            result = extract_public_url_impl("https://example.com/a")
        self.assertEqual(result["title"], "Example")
        self.assertEqual(result["text"], "Body")


@unittest.skipIf(importlib.util.find_spec("mcp") is None, "mcp extra not installed")
class McpProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_in_memory_client_lists_and_calls_tools(self):
        from mcp import Client
        from sharextract.mcp_server import mcp

        async with Client(mcp, raise_exceptions=True) as client:
            listed = await client.list_tools()
            names = {tool.name for tool in listed.tools}
            self.assertIn("extract_public_url", names)
            self.assertIn("list_sharextract_capabilities", names)
            self.assertIn("get_sharextract_adapter_health", names)

            caps = await client.call_tool("list_sharextract_capabilities", {})
            self.assertFalse(caps.is_error)
            self.assertIn("extractors", caps.structured_content)

            with patch(
                "sharextract.mcp_server.get_adapter_health",
                return_value={
                    "status": "ok",
                    "summary": {"total": 1},
                    "fixture_corpus": {"count": 1},
                    "adapters": [{"name": "x-oembed", "status": "healthy"}],
                },
            ):
                health = await client.call_tool(
                    "get_sharextract_adapter_health",
                    {"adapter_names": ["x-oembed"]},
                )
            self.assertFalse(health.is_error)
            self.assertEqual(
                health.structured_content["adapters"][0]["name"],
                "x-oembed",
            )

            with patch("sharextract.mcp_server.extract", return_value=fake_result()):
                extracted = await client.call_tool(
                    "extract_public_url",
                    {"url": "https://example.com/a"},
                )
            self.assertFalse(extracted.is_error)
            self.assertEqual(extracted.structured_content["title"], "Example")
            self.assertEqual(extracted.structured_content["text"], "Body")


if __name__ == "__main__":
    unittest.main()
