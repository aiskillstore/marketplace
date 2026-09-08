import unittest
from unittest.mock import patch

from sharextract.extractors.grok import GrokShareExtractor
from sharextract.http import FetchError, HttpResponse


SHARE_ID = "bGVnYWN5_57a569b2-d8d9-43be-b345-b60e756b8c63"
PAYLOAD = {
    "data": {
        "grokShare": {
            "items": [
                {
                    "sender": "User",
                    "message": "What do you see in this graph grokky?",
                    "deepsearch_headers": [],
                },
                {
                    "sender": "Agent",
                    "message": "I see a benchmark chart.",
                    "deepsearch_headers": [{"header": "", "steps": []}],
                },
            ]
        }
    }
}


class DirectClient:
    timeout = 20.0

    def get_json(self, url, headers=None):
        return HttpResponse(
            url=url,
            content_type="application/json",
            body=b"{}",
        ), PAYLOAD


class BlockedClient:
    timeout = 20.0

    def get_json(self, url, headers=None):
        raise FetchError("GET failed: HTTP 403 Cloudflare challenge")


class GrokExtractorTests(unittest.TestCase):
    def test_extracts_direct_public_json_when_available(self):
        result = GrokShareExtractor(DirectClient()).extract(
            f"https://grok.com/share/{SHARE_ID}"
        )
        self.assertEqual(result.platform, "grok")
        self.assertEqual(
            result.extraction_method,
            "first_party_undocumented_public_json",
        )
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])
        self.assertEqual(result.messages[1].text, "I see a benchmark chart.")
        self.assertEqual(result.metadata["share_id"], SHARE_ID)
        self.assertFalse(result.metadata["browser_public_only"])

    def test_falls_back_to_anonymous_x_browser_transport(self):
        extractor = GrokShareExtractor(BlockedClient())
        with patch.object(extractor, "_extract_via_x_browser", return_value=PAYLOAD):
            result = extractor.extract(f"https://grok.com/share/{SHARE_ID}")
        self.assertEqual(
            result.extraction_method,
            "public_browser_first_party_graphql",
        )
        self.assertTrue(result.metadata["browser_public_only"])
        self.assertEqual(len(result.messages), 2)

    def test_supports_grok_and_x_share_urls(self):
        extractor = GrokShareExtractor(DirectClient())
        self.assertTrue(extractor.supports(f"https://grok.com/share/{SHARE_ID}"))
        self.assertTrue(extractor.supports(f"https://x.com/i/grok/share/{SHARE_ID}"))
        self.assertTrue(
            extractor.supports(f"https://twitter.com/i/grok/share/{SHARE_ID}")
        )
        self.assertFalse(extractor.supports("https://grok.com/"))

    def test_canonicalizes_x_input_to_grok_share(self):
        result = GrokShareExtractor(DirectClient()).extract(
            f"https://x.com/i/grok/share/{SHARE_ID}"
        )
        self.assertEqual(
            result.canonical_url,
            f"https://grok.com/share/{SHARE_ID}",
        )


if __name__ == "__main__":
    unittest.main()
