import html
import json
import unittest

from sharextract.extractors.douyin import DouyinVideoExtractor
from sharextract.http import HttpResponse


VIDEO_ID = "7660369906369629476"


def make_ssr_html(*, include_ssr=True):
    result = {
        "title": "2026年",
        "publish_time": 1783568860,
        "cover_image_url": "https://p3.example/cover.jpeg",
        "abstract": "2026年#基本医保参保人数同比增长超400万",
        "play_count": 966,
        "digg_count": 11,
        "tag": 0,
        "media_user": {
            "id": 1381458385312408,
            "follower_count": "4490",
            "screen_name": "经济参考报",
            "video_count": "14009",
            "avatar_url": "https://p26.example/avatar.jpeg",
        },
        "gid": VIDEO_ID,
        "video_model": json.dumps(
            {
                "status": 10,
                "video_duration": 7.615,
                "video_id": "v0300example",
                "video_list": [
                    {
                        "main_url": "https://video.example/should-not-export.mp4",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        "is_vertical": True,
        "video_id": "v0300example",
    }
    ssr = {
        "data": {
            "storeState": {
                "detail": {
                    "videoData": {
                        "result": result,
                    }
                }
            }
        }
    }
    ld = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": "2026年",
        "description": "2026年",
        "thumbnailUrl": ["https://p3.example/ld.jpeg"],
        "uploadDate": "2026-07-09T03:47:40.000Z",
        "duration": "PT7.615S",
        "interactionStatistic": {
            "@type": "InteractionCounter",
            "userInteractionCount": 966,
        },
        "author": {"@type": "Person", "name": "经济参考报"},
    }
    parts = [
        "<html><head>",
        '<script type="application/ld+json">',
        json.dumps(ld, ensure_ascii=False),
        "</script></head><body>",
    ]
    if include_ssr:
        parts.extend(
            [
                "<script>window._SSR_DATA = ",
                json.dumps(ssr, ensure_ascii=False),
                "</script>",
            ]
        )
    parts.append("</body></html>")
    return "".join(parts)


class FakeClient:
    def __init__(self, *, include_ssr=True, resolved=None):
        self.include_ssr = include_ssr
        self.resolved = resolved
        self.get_calls = []
        self.resolve_calls = []

    def get_text(self, url, headers=None):
        self.get_calls.append((url, headers))
        return HttpResponse(
            url=url,
            content_type="text/html; charset=utf-8",
            body=make_ssr_html(include_ssr=self.include_ssr).encode(),
        )

    def resolve(self, url, headers=None):
        self.resolve_calls.append((url, headers))
        return (
            self.resolved
            or f"https://www.iesdouyin.com/share/video/{VIDEO_ID}/?from_ssr=1"
        )


class DouyinExtractorTests(unittest.TestCase):
    def test_extracts_public_jingxuan_ssr_metadata_only(self):
        client = FakeClient()
        result = DouyinVideoExtractor(client).extract(
            f"https://www.douyin.com/video/{VIDEO_ID}"
        )
        self.assertEqual(result.platform, "douyin")
        self.assertEqual(result.kind, "video")
        self.assertEqual(
            result.extraction_method,
            "first_party_public_jingxuan_ssr_json",
        )
        self.assertEqual(result.title, "2026年")
        self.assertEqual(result.author, "经济参考报")
        self.assertEqual(
            result.canonical_url,
            f"https://www.douyin.com/video/{VIDEO_ID}",
        )
        self.assertEqual(result.metadata["stats"]["play_count"], 966)
        self.assertEqual(result.metadata["stats"]["digg_count"], 11)
        self.assertEqual(result.metadata["duration_seconds"], 7.615)
        self.assertEqual(result.media[0]["duration_seconds"], 7.615)
        self.assertEqual(
            result.media[0]["thumbnail_url"],
            "https://p3.example/cover.jpeg",
        )
        serialized = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn("should-not-export.mp4", serialized)
        self.assertFalse(result.metadata["stream_urls_exported"])
        self.assertEqual(len(client.get_calls), 1)
        self.assertIn(
            "jingxuan.douyin.com/m/video",
            client.get_calls[0][0],
        )
        self.assertIn("iPhone", client.get_calls[0][1]["User-Agent"])

    def test_jsonld_is_safe_metadata_fallback(self):
        result = DouyinVideoExtractor(
            FakeClient(include_ssr=False)
        ).extract(
            f"https://jingxuan.douyin.com/m/video/{VIDEO_ID}"
        )
        self.assertEqual(
            result.extraction_method,
            "first_party_public_jingxuan_jsonld",
        )
        self.assertEqual(result.title, "2026年")
        self.assertEqual(result.author, "经济参考报")
        self.assertEqual(result.metadata["duration_seconds"], 7.615)
        self.assertEqual(result.metadata["stats"]["play_count"], 966)

    def test_short_link_resolves_only_to_find_video_id(self):
        client = FakeClient()
        result = DouyinVideoExtractor(client).extract(
            "https://v.douyin.com/example/"
        )
        self.assertEqual(len(client.resolve_calls), 1)
        self.assertEqual(result.metadata["video_id"], VIDEO_ID)
        self.assertEqual(
            result.canonical_url,
            f"https://www.douyin.com/video/{VIDEO_ID}",
        )

    def test_supports_direct_share_reader_and_short_urls(self):
        extractor = DouyinVideoExtractor(FakeClient())
        for url in [
            f"https://www.douyin.com/video/{VIDEO_ID}",
            f"https://www.douyin.com/share/video/{VIDEO_ID}",
            f"https://m.douyin.com/share/video/{VIDEO_ID}",
            f"https://www.iesdouyin.com/share/video/{VIDEO_ID}/",
            f"https://jingxuan.douyin.com/m/video/{VIDEO_ID}",
            "https://v.douyin.com/abc123/",
        ]:
            self.assertTrue(extractor.supports(url), url)
        self.assertFalse(extractor.supports("https://www.douyin.com/user/test"))
        self.assertFalse(extractor.supports("https://jingxuan.douyin.com/"))


if __name__ == "__main__":
    unittest.main()
