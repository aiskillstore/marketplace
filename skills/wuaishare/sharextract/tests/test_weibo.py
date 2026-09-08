import unittest

from sharextract.extractors.weibo import WeiboStatusExtractor
from sharextract.http import FetchError, HttpResponse


BID = "JhPnDoE7y"


class FakeClient:
    def __init__(self, *, long=False, extend_ok=True):
        self.long = long
        self.extend_ok = extend_ok
        self.calls = []

    def get_json(self, url, headers=None):
        self.calls.append((url, headers))
        if "/statuses/show" in url:
            return (
                HttpResponse(
                    url=url,
                    content_type="application/json",
                    body=b"{}",
                ),
                {
                    "ok": 1,
                    "data": {
                        "id": "4542490855874100",
                        "mid": "4542490855874100",
                        "bid": BID,
                        "created_at": "Thu Aug 27 11:07:58 +0800 2020",
                        "text": "短文本<br />第二行<a href='/n/test'>@测试</a>",
                        "source": "微博 weibo.com",
                        "isLongText": self.long,
                        "reposts_count": 5,
                        "comments_count": 6,
                        "attitudes_count": 7,
                        "favorites_count": 8,
                        "pics": [
                            {
                                "pid": "pic1",
                                "url": "https://wx.example/small.jpg",
                                "large": {
                                    "url": "https://wx.example/large.jpg",
                                    "geo": {"width": "1200", "height": "800"},
                                },
                            }
                        ],
                        "page_info": {
                            "page_pic": {"url": "https://wx.example/poster.jpg"},
                            "media_info": {
                                "stream_url_hd": "https://video.example/a.mp4",
                                "duration": 12.5,
                            },
                            "page_url": "https://weibo.com/tv/show/test",
                            "page_title": "视频",
                        },
                        "user": {
                            "id": 2016713117,
                            "screen_name": "微博客服",
                            "description": "客服",
                            "avatar_hd": "https://wx.example/avatar.jpg",
                            "verified": True,
                            "verified_reason": "微博客服",
                            "followers_count_str": "1.65亿",
                            "statuses_count": 100,
                        },
                        "retweeted_status": {
                            "id": "111",
                            "mid": "111",
                            "bid": "AbCdE123",
                            "created_at": "Wed Aug 26 10:00:00 +0800 2020",
                            "text": "原微博<br />正文",
                            "reposts_count": 1,
                            "comments_count": 2,
                            "attitudes_count": 3,
                            "user": {
                                "id": 123,
                                "screen_name": "原作者",
                                "avatar_hd": "https://wx.example/o.jpg",
                            },
                            "pics": [],
                        },
                    },
                },
            )

        if "/statuses/extend" in url:
            if not self.extend_ok:
                raise FetchError("temporary")
            return (
                HttpResponse(
                    url=url,
                    content_type="application/json",
                    body=b"{}",
                ),
                {
                    "ok": 1,
                    "data": {
                        "longTextContent": "完整长文<br />第二行",
                    },
                },
            )
        raise AssertionError(url)


class WeiboExtractorTests(unittest.TestCase):
    def test_extracts_public_mobile_json_and_media(self):
        client = FakeClient()
        result = WeiboStatusExtractor(client).extract(
            f"https://weibo.com/2016713117/{BID}"
        )
        self.assertEqual(result.platform, "weibo")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(
            result.extraction_method,
            "first_party_public_mobile_json",
        )
        self.assertEqual(result.author, "微博客服")
        self.assertEqual(result.text, "短文本\n第二行@测试")
        self.assertEqual(
            result.canonical_url,
            f"https://weibo.com/2016713117/{BID}",
        )
        self.assertEqual(result.metadata["stats"]["comment_count"], 6)
        self.assertEqual(result.metadata["author"]["followers_count"], "1.65亿")
        self.assertEqual(result.media[0]["url"], "https://wx.example/large.jpg")
        self.assertTrue(any(x["type"] == "video" for x in result.media))
        self.assertEqual(
            result.metadata["retweeted_status"]["author"]["screen_name"],
            "原作者",
        )
        self.assertIn("转发自 @原作者", result.markdown)
        self.assertEqual(len(client.calls), 1)
        headers = client.calls[0][1]
        self.assertEqual(headers["MWeibo-Pwa"], "1")
        self.assertEqual(headers["X-Requested-With"], "XMLHttpRequest")

    def test_long_text_calls_extend_only_when_needed(self):
        client = FakeClient(long=True)
        result = WeiboStatusExtractor(client).extract(
            f"https://m.weibo.cn/detail/{BID}"
        )
        self.assertEqual(
            result.extraction_method,
            "first_party_public_mobile_json_plus_extend",
        )
        self.assertEqual(result.text, "完整长文\n第二行")
        self.assertEqual(len(client.calls), 2)
        self.assertIn("/statuses/extend", client.calls[1][0])

    def test_long_text_falls_back_when_extend_unavailable(self):
        client = FakeClient(long=True, extend_ok=False)
        result = WeiboStatusExtractor(client).extract(
            f"https://m.weibo.cn/status/{BID}"
        )
        self.assertEqual(
            result.extraction_method,
            "first_party_public_mobile_json",
        )
        self.assertEqual(result.text, "短文本\n第二行@测试")
        self.assertTrue(any("long text" in x for x in result.warnings))

    def test_supports_desktop_and_mobile_status_shapes(self):
        extractor = WeiboStatusExtractor(FakeClient())
        self.assertTrue(
            extractor.supports(f"https://weibo.com/2016713117/{BID}")
        )
        self.assertTrue(
            extractor.supports(f"https://www.weibo.com/status/{BID}")
        )
        self.assertTrue(
            extractor.supports(f"https://m.weibo.cn/detail/{BID}")
        )
        self.assertTrue(
            extractor.supports(f"https://m.weibo.cn/status/{BID}")
        )
        self.assertFalse(extractor.supports("https://weibo.com/u/2016713117"))
        self.assertFalse(extractor.supports("https://m.weibo.cn/"))


if __name__ == "__main__":
    unittest.main()
