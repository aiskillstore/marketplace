import unittest

from sharextract.extractors.kimi import KimiShareExtractor
from sharextract.http import HttpResponse


SHARE_ID = "d43fjiqebk48hc9l79v0"


class FakeClient:
    def post_json(self, url, payload, headers=None):
        data = {
            "share": {
                "id": SHARE_ID,
                "chat": {"id": "chat-1", "name": "Synthetic Kimi Share"},
                "creator": {"name": "Alice", "avatarUrl": "https://example.com/a.png"},
                "messages": [
                    {
                        "id": "u1",
                        "role": "user",
                        "childrenMessageIds": ["a1"],
                        "status": "MESSAGE_STATUS_COMPLETED",
                        "createTime": "2026-01-01T00:00:00Z",
                        "blocks": [{"id": "0_0", "text": {"content": "Hello Kimi"}}],
                        "refs": {},
                    },
                    {
                        "id": "a1",
                        "parentId": "u1",
                        "role": "assistant",
                        "status": "MESSAGE_STATUS_COMPLETED",
                        "createTime": "2026-01-01T00:00:01Z",
                        "blocks": [
                            {"id": "1_0", "search": {"queries": ["public search"]}},
                            {"id": "1_1", "text": {"content": "Hello human"}},
                            {"id": "1_2", "thinking": {"content": "do not export"}},
                        ],
                        "refs": {},
                    },
                ],
            }
        }
        return HttpResponse(url=url, content_type="application/json", body=b"{}"), data


class KimiExtractorTests(unittest.TestCase):
    def test_extracts_public_share_json(self):
        result = KimiShareExtractor(FakeClient()).extract(
            f"https://www.kimi.com/share/{SHARE_ID}"
        )
        self.assertEqual(result.platform, "kimi")
        self.assertEqual(
            result.extraction_method,
            "first_party_undocumented_public_json",
        )
        self.assertEqual(result.title, "Synthetic Kimi Share")
        self.assertEqual(result.author, "Alice")
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])
        self.assertEqual(result.messages[0].text, "Hello Kimi")
        self.assertEqual(result.messages[1].text, "Hello human")
        self.assertNotIn("do not export", result.text)
        self.assertFalse(result.metadata["reasoning_exported"])

    def test_supports_locale_and_plain_share_urls(self):
        extractor = KimiShareExtractor(FakeClient())
        self.assertTrue(extractor.supports(f"https://kimi.com/share/{SHARE_ID}"))
        self.assertTrue(extractor.supports(f"https://www.kimi.com/share/en/{SHARE_ID}?ra=1"))
        self.assertFalse(extractor.supports("https://www.kimi.com/"))

    def test_canonicalizes_locale_share_url(self):
        result = KimiShareExtractor(FakeClient()).extract(
            f"https://www.kimi.com/share/zh/{SHARE_ID}?sharetype=link"
        )
        self.assertEqual(
            result.canonical_url,
            f"https://www.kimi.com/share/{SHARE_ID}",
        )


if __name__ == "__main__":
    unittest.main()
