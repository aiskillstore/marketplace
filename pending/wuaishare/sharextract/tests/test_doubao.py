import html
import json
import unittest

from sharextract.extractors.doubao import DoubaoShareExtractor
from sharextract.http import HttpResponse


TOKEN = "aef4c7a4c78c2"


class FakeClient:
    def get(self, url, headers=None):
        router = [
            "thread_(token)/page",
            "shareInfo",
            {
                "data": {
                    "share_info": {
                        "share_id": "35082955417775618",
                        "share_name": "画一只狗",
                        "share_status": 2,
                        "share_time": 1767619961000,
                        "user": {"nick_name": "Alice"},
                        "bot": {"name": "豆包", "bot_id": "bot-1", "bot_type": 1},
                    },
                    "message_snapshot": {
                        "message_list": [
                            {
                                "message_id": "u1",
                                "user_type": 1,
                                "index": 1,
                                "reply_id": "0",
                                "status": 1,
                                "content_block": [
                                    {
                                        "content_v2": json.dumps(
                                            {"text_block": {"text": "画一只狗"}},
                                            ensure_ascii=False,
                                        )
                                    }
                                ],
                            },
                            {
                                "message_id": "a1",
                                "user_type": 2,
                                "index": 2,
                                "reply_id": "u1",
                                "status": 1,
                                "content_block": [
                                    {
                                        "content_v2": json.dumps(
                                            {"text_block": {"text": "以下是为你生成的图片："}},
                                            ensure_ascii=False,
                                        )
                                    },
                                    {
                                        "content_v2": json.dumps(
                                            {
                                                "creation_block": {
                                                    "creations": [
                                                        {
                                                            "id": "c1",
                                                            "image": {
                                                                "image_ori": {
                                                                    "url": "https://cdn.example/public.png",
                                                                    "width": 2048,
                                                                    "height": 2048,
                                                                },
                                                                "image_ori_raw": {
                                                                    "url": "https://cdn.example/raw.png"
                                                                },
                                                            },
                                                        }
                                                    ]
                                                }
                                            }
                                        )
                                    },
                                    {
                                        "content_v2": json.dumps(
                                            {"thinking": {"text": "do not export"}}
                                        )
                                    },
                                ],
                            },
                        ]
                    },
                }
            },
        ]
        encoded = html.escape(json.dumps(router, ensure_ascii=False), quote=True)
        page = (
            '<html><body><script data-script-src="modern-run-router-data-fn" '
            f'data-fn-args="{encoded}" nonce="test"></script></body></html>'
        )
        return HttpResponse(url=url, content_type="text/html; charset=utf-8", body=page.encode())


class DoubaoExtractorTests(unittest.TestCase):
    def test_extracts_public_router_snapshot(self):
        result = DoubaoShareExtractor(FakeClient()).extract(
            f"https://www.doubao.com/thread/{TOKEN}"
        )
        self.assertEqual(result.platform, "doubao")
        self.assertEqual(result.extraction_method, "first_party_embedded_router_json")
        self.assertEqual(result.title, "画一只狗")
        self.assertEqual(result.author, "Alice")
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])
        self.assertEqual(result.messages[0].text, "画一只狗")
        self.assertEqual(result.messages[1].text, "以下是为你生成的图片：")
        self.assertEqual(result.media[0]["url"], "https://cdn.example/public.png")
        self.assertNotIn("raw.png", json.dumps(result.to_dict()))
        self.assertFalse(result.metadata["reasoning_exported"])

    def test_supports_thread_and_share_urls(self):
        extractor = DoubaoShareExtractor(FakeClient())
        self.assertTrue(extractor.supports(f"https://doubao.com/thread/{TOKEN}"))
        self.assertTrue(extractor.supports(f"https://www.doubao.com/share/{TOKEN}"))
        self.assertFalse(extractor.supports("https://www.doubao.com/chat/abc"))
        self.assertFalse(extractor.supports("https://example.com/thread/abc"))


if __name__ == "__main__":
    unittest.main()
