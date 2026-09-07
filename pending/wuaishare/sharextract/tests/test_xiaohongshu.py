import json
import unittest

from sharextract.extractors.base import ExtractorError
from sharextract.extractors.xiaohongshu import (
    XiaohongshuNoteExtractor,
    _extract_initial_state,
)
from sharextract.http import HttpResponse


NOTE_ID = "6a6075370000000011011d01"
TOKEN = "PUBLIC-SHARE-TOKEN="


def make_page():
    note = {
        "xsecToken": "do-not-export-note-token",
        "noteId": NOTE_ID,
        "user": {
            "userId": "5a6818284eacab58e0dec26c",
            "nickname": "毛小星Ryan",
            "avatar": "http://sns-avatar.example/avatar.jpg",
            "xsecToken": "do-not-export-user-token",
        },
        "interactInfo": {
            "collectedCount": "2811",
            "commentCount": "141",
            "shareCount": "1047",
            "likedCount": "1.1万",
            "niceCount": "",
        },
        "imageList": [
            {
                "fileId": "cover-id",
                "urlDefault": "http://sns-webpic.example/cover.jpg",
                "height": 1685,
                "width": 1263,
            }
        ],
        "video": {
            "media": {
                "video": {
                    "duration": 132,
                },
                "stream": {
                    "h264": [
                        {
                            "masterUrl": "http://video.example/should-not-export.mp4",
                        }
                    ]
                },
                "videoId": 138028871631567170,
            },
            "capa": {"duration": 131},
            "mediaV2": json.dumps(
                {
                    "subtitles": {
                        "zh-CN": [
                            {
                                "url": "https://subtitle.example/should-not-export.srt",
                            }
                        ]
                    }
                }
            ),
        },
        "tagList": [
            {"id": "tag1", "name": "护肤", "type": "topic"},
            {"id": "tag2", "name": "变美", "type": "topic"},
        ],
        "time": 1784798127000,
        "type": "video",
        "title": "年轻必看！卡戴珊太后变年轻，全靠AI？",
        "desc": "#护肤[话题]# #变美[话题]#",
        "lastUpdateTime": 1786516097000,
        "ipLocation": "上海",
        "shareInfo": {"unShare": False},
    }
    state = {
        "global": {
            "example": None,
            "literal": "undefined stays inside strings",
        },
        "note": {
            "firstNoteId": NOTE_ID,
            "noteDetailMap": {
                NOTE_ID: {
                    "currentTime": 1788681896836,
                    "note": note,
                }
            },
        },
    }
    raw = json.dumps(state, ensure_ascii=False)
    raw = raw.replace('"example": null', '"example": undefined')
    return (
        "<html><body><script>window.__INITIAL_STATE__="
        + raw
        + "</script></body></html>"
    )


class FakeClient:
    def __init__(self, *, resolved=None, expired=False):
        self.resolved = resolved
        self.expired = expired
        self.resolve_calls = []
        self.get_calls = []

    def resolve(self, url, headers=None):
        self.resolve_calls.append((url, headers))
        return self.resolved or (
            f"https://www.xiaohongshu.com/discovery/item/{NOTE_ID}"
            f"?xsec_token={TOKEN}&xsec_source=app_share&share_id=tracking"
        )

    def get_text(self, url, headers=None):
        self.get_calls.append((url, headers))
        final = (
            "https://www.xiaohongshu.com/404/sec_example"
            if self.expired
            else url
        )
        return HttpResponse(
            url=final,
            content_type="text/html; charset=utf-8",
            body=make_page().encode(),
        )


class XiaohongshuExtractorTests(unittest.TestCase):
    def test_extracts_public_tokenized_ssr_without_stream_urls(self):
        url = (
            f"https://www.xiaohongshu.com/explore/{NOTE_ID}"
            f"?xsec_token={TOKEN}&xsec_source=pc_share&shareRedId=tracking"
        )
        result = XiaohongshuNoteExtractor(FakeClient()).extract(url)

        self.assertEqual(result.platform, "xiaohongshu")
        self.assertEqual(result.kind, "note")
        self.assertEqual(
            result.extraction_method,
            "first_party_public_ssr_initial_state",
        )
        self.assertEqual(result.title, "年轻必看！卡戴珊太后变年轻，全靠AI？")
        self.assertEqual(result.author, "毛小星Ryan")
        self.assertEqual(result.metadata["note_type"], "video")
        self.assertEqual(result.metadata["video"]["duration_seconds"], 131.0)
        self.assertEqual(result.metadata["stats"]["liked_count"], "1.1万")
        self.assertEqual(result.metadata["tags"][0]["name"], "护肤")
        self.assertEqual(
            result.media[0]["url"],
            result.canonical_url,
        )
        self.assertEqual(result.media[0]["duration_seconds"], 131.0)
        self.assertEqual(
            result.media[0]["thumbnail_url"],
            "https://sns-webpic.example/cover.jpg",
        )
        self.assertTrue(
            result.canonical_url.startswith(
                f"https://www.xiaohongshu.com/explore/{NOTE_ID}?"
            )
        )
        self.assertIn("xsec_token=PUBLIC-SHARE-TOKEN%3D", result.canonical_url)
        self.assertNotIn("shareRedId", result.canonical_url)

        serialized = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn("should-not-export.mp4", serialized)
        self.assertNotIn("should-not-export.srt", serialized)
        self.assertNotIn("do-not-export-user-token", serialized)
        self.assertNotIn("do-not-export-note-token", serialized)
        self.assertFalse(result.metadata["stream_urls_exported"])
        self.assertFalse(result.metadata["token_generated_by_sharextract"])

    def test_short_link_resolves_and_consumes_existing_public_token(self):
        client = FakeClient()
        result = XiaohongshuNoteExtractor(client).extract(
            "https://xhslink.cn/o/example"
        )
        self.assertEqual(len(client.resolve_calls), 1)
        self.assertEqual(len(client.get_calls), 1)
        self.assertEqual(result.metadata["xsec_source"], "app_share")
        self.assertTrue(result.metadata["public_share_token_consumed"])

    def test_bare_note_url_is_rejected_without_generating_token(self):
        client = FakeClient()
        extractor = XiaohongshuNoteExtractor(client)
        with self.assertRaisesRegex(ExtractorError, "no current xsec_token"):
            extractor.extract(
                f"https://www.xiaohongshu.com/explore/{NOTE_ID}"
            )
        self.assertEqual(client.get_calls, [])
        self.assertEqual(client.resolve_calls, [])

    def test_expired_share_redirect_is_reported(self):
        client = FakeClient(expired=True)
        extractor = XiaohongshuNoteExtractor(client)
        with self.assertRaisesRegex(ExtractorError, "expired"):
            extractor.extract(
                f"https://www.xiaohongshu.com/explore/{NOTE_ID}"
                f"?xsec_token={TOKEN}&xsec_source=pc_share"
            )

    def test_initial_state_parser_replaces_only_bare_undefined(self):
        state = _extract_initial_state(make_page())
        self.assertIsNone(state["global"]["example"])
        self.assertEqual(
            state["global"]["literal"],
            "undefined stays inside strings",
        )

    def test_supports_note_shapes_and_official_short_links(self):
        extractor = XiaohongshuNoteExtractor(FakeClient())
        self.assertTrue(
            extractor.supports(
                f"https://www.xiaohongshu.com/explore/{NOTE_ID}"
            )
        )
        self.assertTrue(
            extractor.supports(
                f"https://www.xiaohongshu.com/discovery/item/{NOTE_ID}"
            )
        )
        self.assertTrue(extractor.supports("https://xhslink.cn/o/example"))
        self.assertTrue(extractor.supports("http://xhslink.com/o/example"))
        self.assertFalse(
            extractor.supports(
                "https://www.xiaohongshu.com/user/profile/123"
            )
        )


if __name__ == "__main__":
    unittest.main()
