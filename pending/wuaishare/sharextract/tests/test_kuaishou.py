import json
import unittest

from sharextract.extractors.base import ExtractorError
from sharextract.extractors.kuaishou import (
    KuaishouVideoExtractor,
    _extract_apollo_state,
)
from sharextract.http import HttpResponse


PHOTO_ID = "3x2cvn2u7fq8k8s"
AUTHOR_ID = "3xk4476piuucxxk"


def make_page(*, include_state=True):
    detail_key = (
        '$ROOT_QUERY.visionVideoDetail('
        '{"page":"detail","photoId":"' + PHOTO_ID + '"})'
    )
    tag0 = detail_key + ".tags.0"
    tag1 = detail_key + ".tags.1"
    state = {
        "defaultClient": {
            "VisionVideoDetailAuthor:unrelated": {
                "id": "unrelated",
                "name": "错误作者",
            },
            detail_key: {
                "status": 1,
                "type": 1,
                "author": {
                    "type": "id",
                    "generated": False,
                    "id": f"VisionVideoDetailAuthor:{AUTHOR_ID}",
                    "typename": "VisionVideoDetailAuthor",
                },
                "photo": {
                    "type": "id",
                    "generated": False,
                    "id": f"VisionVideoDetailPhoto:{PHOTO_ID}",
                    "typename": "VisionVideoDetailPhoto",
                },
                "tags": [
                    {
                        "type": "id",
                        "generated": True,
                        "id": tag0,
                        "typename": "VisionVideoDetailTags",
                    },
                    {
                        "type": "id",
                        "generated": True,
                        "id": tag1,
                        "typename": "VisionVideoDetailTags",
                    },
                ],
            },
            f"VisionVideoDetailAuthor:{AUTHOR_ID}": {
                "id": AUTHOR_ID,
                "name": "糖豆姐姐🔥",
                "headerUrl": "http://p5.example/avatar.jpg",
                "verifiedDetail": None,
            },
            f"VisionVideoDetailPhoto:{PHOTO_ID}": {
                "id": PHOTO_ID,
                "duration": 7186,
                "caption": "#微胖女人最可爱",
                "likeCount": "3.4万",
                "realLikeCount": 33769,
                "coverUrl": "http://p4.example/cover.jpg",
                "photoUrl": "https://video.example/should-not-export.mp4",
                "timestamp": 1762252555103,
                "viewCount": "77.4万",
                "videoRatio": 0.5625,
                "stereoType": 0,
                "manifest": {
                    "json": {
                        "representation": [
                            {
                                "url": (
                                    "https://cdn.example/"
                                    "should-not-export-manifest.mp4"
                                )
                            }
                        ]
                    }
                },
                "videoResource": {
                    "json": {
                        "h264": {
                            "representation": [
                                {
                                    "url": (
                                        "https://cdn.example/"
                                        "should-not-export-resource.mp4"
                                    )
                                }
                            ]
                        }
                    }
                },
            },
            tag0: {
                "type": "1",
                "name": "微胖女人是极品",
            },
            tag1: {
                "type": "1",
                "name": "微胖女人最可爱",
            },
        },
        "clients": {},
    }
    if not include_state:
        return "<html><body>empty</body></html>"
    return (
        "<html><body><script>window.__APOLLO_STATE__="
        + json.dumps(state, ensure_ascii=False)
        + ";</script></body></html>"
    )


class FakeClient:
    def __init__(self, *, resolved=None, include_state=True):
        self.resolved = resolved
        self.include_state = include_state
        self.resolve_calls = []
        self.get_calls = []

    def resolve(self, url, headers=None):
        self.resolve_calls.append((url, headers))
        return self.resolved or (
            "https://m.chenzhongtech.com/fw/photo/"
            f"{PHOTO_ID}?photoId={PHOTO_ID}&shareToken=tracking"
        )

    def get_text(self, url, headers=None):
        self.get_calls.append((url, headers))
        final = url
        if "v.kuaishou.com" in url or "/f/" in url:
            final = self.resolved or (
                "https://www.kuaishou.com/short-video/"
                f"{PHOTO_ID}?photoId={PHOTO_ID}&shareToken=tracking"
                "&shareId=public-share"
            )
        return HttpResponse(
            url=final,
            content_type="text/html; charset=utf-8",
            body=make_page(include_state=self.include_state).encode(),
        )


class KuaishouExtractorTests(unittest.TestCase):
    def test_extracts_referenced_apollo_video_metadata_only(self):
        client = FakeClient()
        result = KuaishouVideoExtractor(client).extract(
            f"https://www.kuaishou.com/short-video/{PHOTO_ID}"
        )
        self.assertEqual(result.platform, "kuaishou")
        self.assertEqual(result.kind, "video")
        self.assertEqual(
            result.extraction_method,
            "first_party_public_apollo_ssr",
        )
        self.assertEqual(result.title, "#微胖女人最可爱")
        self.assertEqual(result.author, "糖豆姐姐🔥")
        self.assertEqual(
            result.canonical_url,
            f"https://www.kuaishou.com/short-video/{PHOTO_ID}",
        )
        self.assertEqual(result.metadata["stats"]["like_count"], 33769)
        self.assertEqual(
            result.metadata["stats"]["view_count_display"],
            "77.4万",
        )
        self.assertEqual(result.metadata["duration_seconds"], 7.186)
        self.assertEqual(result.metadata["tags"][0]["name"], "微胖女人是极品")
        self.assertEqual(
            result.metadata["author"]["avatar_url"],
            "https://p5.example/avatar.jpg",
        )
        self.assertEqual(
            result.media[0]["thumbnail_url"],
            "https://p4.example/cover.jpg",
        )
        self.assertEqual(result.media[0]["duration_seconds"], 7.186)
        self.assertFalse(result.metadata["stream_urls_exported"])
        self.assertFalse(result.metadata["uses_device_cookie"])
        self.assertFalse(result.metadata["uses_graphql_api"])
        self.assertIn("Chrome/", client.get_calls[0][1]["User-Agent"])

        serialized = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn("should-not-export", serialized)
        self.assertNotIn(".mp4", serialized)

    def test_short_link_resolves_only_to_find_photo_id(self):
        client = FakeClient()
        result = KuaishouVideoExtractor(client).extract(
            "https://v.kuaishou.com/example"
        )
        self.assertEqual(len(client.resolve_calls), 0)
        self.assertEqual(len(client.get_calls), 1)
        self.assertEqual(result.metadata["photo_id"], PHOTO_ID)
        self.assertEqual(
            client.get_calls[0][0],
            "https://v.kuaishou.com/example",
        )
        self.assertNotIn("shareToken", result.canonical_url)
        serialized = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn("shareToken", serialized)
        self.assertTrue(result.metadata["public_share_context_consumed"])

    def test_supports_direct_legacy_and_share_url_shapes(self):
        extractor = KuaishouVideoExtractor(FakeClient())
        for url in [
            f"https://www.kuaishou.com/short-video/{PHOTO_ID}",
            f"https://kuaishou.cn/short-video/{PHOTO_ID}",
            f"https://m.gifshow.com/fw/photo/{PHOTO_ID}",
            f"https://m.chenzhongtech.com/fw/photo/{PHOTO_ID}",
            "https://v.kuaishou.com/example",
            "https://www.kuaishou.com/f/example",
        ]:
            self.assertTrue(extractor.supports(url), url)
        self.assertFalse(
            extractor.supports("https://www.kuaishou.com/profile/test")
        )

    def test_missing_apollo_state_fails_cleanly(self):
        extractor = KuaishouVideoExtractor(
            FakeClient(include_state=False)
        )
        with self.assertRaisesRegex(ExtractorError, "APOLLO_STATE"):
            extractor.extract(
                f"https://www.kuaishou.com/short-video/{PHOTO_ID}"
            )

    def test_apollo_parser_reads_embedded_json(self):
        state = _extract_apollo_state(make_page())
        self.assertIn("defaultClient", state)


if __name__ == "__main__":
    unittest.main()
