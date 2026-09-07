import json
import unittest

from sharextract.extractors.chatgpt import ChatGPTShareExtractor
from sharextract.http import FetchError, HttpResponse


def encode_turbo(data):
    pool = []

    def add(value):
        index = len(pool)
        pool.append(None)

        if isinstance(value, dict):
            encoded = {}
            for key, child in value.items():
                key_index = add(str(key))
                child_index = add(child)
                encoded[f"_{key_index}"] = child_index
            pool[index] = encoded
            return index

        if isinstance(value, list):
            pool[index] = [add(child) for child in value]
            return index

        pool[index] = value
        return index

    root = add(data)
    assert root == 0
    encoded = json.dumps(json.dumps(pool, ensure_ascii=False))
    return f'<script>streamController.enqueue({encoded});</script>'



class TurboClient:
    def __init__(self, html):
        self.html = html

    def get_text(self, url, headers=None):
        return HttpResponse(
            url=url,
            content_type="text/html; charset=utf-8",
            body=self.html.encode(),
        )

    def get_json(self, url, headers=None):
        raise FetchError("legacy endpoint unavailable")


class LegacyClient:
    def get_text(self, url, headers=None):
        raise FetchError("page parser unavailable")

    def get_json(self, url, headers=None):
        payload = {
            "title": "Legacy share",
            "current_node": "b",
            "mapping": {
                "a": {
                    "id": "a",
                    "parent": None,
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello"]},
                        "create_time": 1,
                    },
                },
                "b": {
                    "id": "b",
                    "parent": "a",
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["World"]},
                        "create_time": 2,
                    },
                },
            },
        }
        return HttpResponse(
            url=url,
            content_type="application/json",
            body=b"{}",
        ), payload


class ChatGPTExtractorTests(unittest.TestCase):
    def test_extracts_full_share_from_turbo_stream(self):
        data = {
            "title": "Shared test",
            "linear_conversation": [
                {
                    "message": {
                        "author": {"role": "system"},
                        "content": {"parts": ["internal"]},
                    }
                },
                {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello"]},
                        "create_time": 1,
                    }
                },
                {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["World"]},
                        "create_time": 2,
                    }
                },
            ],
        }
        extractor = ChatGPTShareExtractor(TurboClient(encode_turbo(data)))
        result = extractor.extract(
            "https://chatgpt.com/share/67a4266c-dbcc-800f-9b92-f0a8a6480e16"
        )
        self.assertEqual(result.title, "Shared test")
        self.assertEqual(
            result.extraction_method,
            "first_party_embedded_turbo_stream",
        )
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])
        self.assertNotIn("internal", result.text)
        self.assertFalse(result.metadata["reasoning_exported"])

    def test_extracts_new_s_share_shape(self):
        data = {
            "title": "Shared output",
            "messages": [
                {
                    "author": {"role": "assistant"},
                    "content": {
                        "parts": [
                            'Hello \ue200entity\ue202["people","Alice"]\ue201'
                        ]
                    },
                }
            ],
        }
        extractor = ChatGPTShareExtractor(TurboClient(encode_turbo(data)))
        result = extractor.extract(
            "https://chatgpt.com/s/t_69b1f761e57c81919921439ae31c0a40"
        )
        self.assertEqual(result.kind, "shared_content")
        self.assertEqual(result.messages[0].text, "Hello Alice")
        self.assertEqual(result.metadata["share_type"], "s")

    def test_legacy_json_remains_a_fallback(self):
        extractor = ChatGPTShareExtractor(LegacyClient())
        result = extractor.extract(
            "https://chatgpt.com/share/67a4266c-dbcc-800f-9b92-f0a8a6480e16"
        )
        self.assertEqual(result.title, "Legacy share")
        self.assertEqual(
            result.extraction_method,
            "first_party_undocumented_json",
        )
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])

    def test_supports_share_and_s_urls_only(self):
        extractor = ChatGPTShareExtractor(TurboClient(""))
        self.assertTrue(
            extractor.supports(
                "https://chatgpt.com/share/67a4266c-dbcc-800f-9b92-f0a8a6480e16"
            )
        )
        self.assertTrue(
            extractor.supports(
                "https://chatgpt.com/s/t_69b1f761e57c81919921439ae31c0a40"
            )
        )
        self.assertFalse(extractor.supports("https://chatgpt.com/c/abc"))
        self.assertFalse(extractor.supports("https://example.com/share/abc"))


if __name__ == "__main__":
    unittest.main()
