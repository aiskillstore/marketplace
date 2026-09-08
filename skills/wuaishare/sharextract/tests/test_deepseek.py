import unittest

from sharextract.extractors.deepseek import DeepSeekShareExtractor
from sharextract.http import HttpResponse


class FakeClient:
    def get_json(self, url, headers=None):
        payload = {
            "data": {
                "biz_data": {
                    "title": "Shared Conversation",
                    "messages": [
                        {"role": "USER", "content": "写一篇文章", "inserted_at": 1},
                        {
                            "role": "ASSISTANT",
                            "content": "# 测试标题\n\n这是正文。",
                            "inserted_at": 2,
                        },
                    ],
                }
            }
        }
        return HttpResponse(url=url, content_type="application/json", body=b"{}"), payload


class DeepSeekExtractorTests(unittest.TestCase):
    def test_extracts_messages_and_title(self):
        extractor = DeepSeekShareExtractor(FakeClient())
        result = extractor.extract("https://chat.deepseek.com/share/abc123")
        self.assertEqual(result.platform, "deepseek")
        self.assertEqual(result.kind, "conversation")
        self.assertEqual(result.title, "测试标题")
        self.assertEqual(len(result.messages), 2)
        self.assertIn("这是正文", result.markdown)
        self.assertEqual(result.metadata["share_id"], "abc123")


if __name__ == "__main__":
    unittest.main()
