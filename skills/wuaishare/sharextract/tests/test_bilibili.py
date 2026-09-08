import unittest

from sharextract.extractors.bilibili import BilibiliVideoExtractor
from sharextract.http import HttpResponse


class FakeClient:
    def get_json(self, url, headers=None):
        payload = {
            "code": 0,
            "message": "OK",
            "data": {
                "bvid": "BV1Xj7N6mEa3",
                "aid": 116794069092246,
                "cid": 123,
                "title": "当一千年后的人类考古2026年",
                "desc": "公开视频简介",
                "pic": "http://i2.hdslb.com/bfs/archive/test.jpg",
                "pubdate": 1782268200,
                "ctime": 1782136328,
                "duration": 145,
                "owner": {
                    "mid": 25329626,
                    "name": "咪克菌",
                    "face": "http://i2.hdslb.com/bfs/face/test.jpg",
                },
                "stat": {
                    "view": 100,
                    "like": 20,
                    "share": 3,
                },
                "rights": {
                    "download": 1,
                    "no_reprint": 1,
                },
                "pages": [
                    {
                        "cid": 123,
                        "page": 1,
                        "part": "正片",
                        "duration": 145,
                        "dimension": {"width": 1920, "height": 1080},
                    }
                ],
            },
        }
        return HttpResponse(
            url=url,
            content_type="application/json",
            body=b"{}",
        ), payload


class BilibiliExtractorTests(unittest.TestCase):
    def test_extracts_public_video_metadata(self):
        result = BilibiliVideoExtractor(FakeClient()).extract(
            "https://www.bilibili.com/video/BV1Xj7N6mEa3"
        )
        self.assertEqual(result.platform, "bilibili")
        self.assertEqual(result.kind, "video")
        self.assertEqual(result.title, "当一千年后的人类考古2026年")
        self.assertEqual(result.author, "咪克菌")
        self.assertEqual(result.text, "公开视频简介")
        self.assertEqual(
            result.media[0]["thumbnail_url"],
            "https://i2.hdslb.com/bfs/archive/test.jpg",
        )
        self.assertEqual(result.metadata["stats"]["view"], 100)
        self.assertEqual(
            result.extraction_method,
            "first_party_undocumented_public_json",
        )

    def test_supports_bv_and_av_video_urls(self):
        extractor = BilibiliVideoExtractor(FakeClient())
        self.assertTrue(
            extractor.supports("https://www.bilibili.com/video/BV1Xj7N6mEa3")
        )
        self.assertTrue(
            extractor.supports("https://www.bilibili.com/video/av116883424609977/")
        )
        self.assertFalse(extractor.supports("https://space.bilibili.com/123"))
        self.assertFalse(extractor.supports("https://example.com/video/BV123"))


if __name__ == "__main__":
    unittest.main()
