import unittest

from sharextract.extractors.qwen import QwenShareExtractor
from sharextract.http import HttpResponse


SHARE_ID = "97d45748-645d-407e-8191-87bd996f8901"


class FakeClient:
    def get_json(self, url, headers=None):
        payload = {
            "success": True,
            "data": {
                "id": SHARE_ID,
                "share_id": SHARE_ID,
                "title": "Synthetic Qwen Share",
                "created_at": "2026-05-18T00:00:00Z",
                "updated_at": "2026-05-18T00:01:00Z",
                "models": ["qwen-test"],
                "chat": {
                    "messages": [
                        {
                            "id": "u1",
                            "role": "user",
                            "content": "Hello Qwen",
                            "timestamp": 1779122900,
                            "parentId": None,
                            "childrenIds": ["a1"],
                            "files": [],
                        },
                        {
                            "id": "a1",
                            "role": "assistant",
                            "content": "",
                            "timestamp": 1779123123,
                            "parentId": "u1",
                            "childrenIds": [],
                            "model": "qwen-test",
                            "modelName": "Qwen Test",
                            "reasoning_content": "private reasoning should not be exported",
                            "content_list": [
                                {
                                    "phase": "thinking_summary",
                                    "content": "thinking summary should not be exported",
                                    "status": "finished",
                                },
                                {
                                    "phase": "answer",
                                    "content": "Hello human",
                                    "status": "finished",
                                },
                            ],
                        },
                    ]
                },
            },
        }
        return HttpResponse(url=url, content_type="application/json", body=b"{}"), payload


class QwenExtractorTests(unittest.TestCase):
    def test_extracts_public_share_json_and_ignores_reasoning(self):
        result = QwenShareExtractor(FakeClient()).extract(
            f"https://chat.qwen.ai/s/{SHARE_ID}"
        )
        self.assertEqual(result.platform, "qwen")
        self.assertEqual(
            result.extraction_method,
            "first_party_undocumented_public_json",
        )
        self.assertEqual(result.title, "Synthetic Qwen Share")
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])
        self.assertEqual(result.messages[0].text, "Hello Qwen")
        self.assertEqual(result.messages[1].text, "Hello human")
        self.assertNotIn("private reasoning", result.text)
        self.assertNotIn("thinking summary", result.text)
        self.assertFalse(result.metadata["reasoning_exported"])

    def test_supports_qwen_share_urls(self):
        extractor = QwenShareExtractor(FakeClient())
        self.assertTrue(extractor.supports(f"https://chat.qwen.ai/s/{SHARE_ID}"))
        self.assertFalse(extractor.supports("https://chat.qwen.ai/"))
        self.assertFalse(extractor.supports("https://example.com/s/test"))


if __name__ == "__main__":
    unittest.main()
