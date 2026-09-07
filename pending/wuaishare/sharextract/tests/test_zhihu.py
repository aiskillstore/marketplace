import html
import json
import unittest

from sharextract.extractors.zhihu import (
    ZhihuAnswerExtractor,
    ZhihuArticleExtractor,
)
from sharextract.http import FetchError, HttpResponse


ANSWER_ID = "1993418784334177262"
QUESTION_ID = "19550225"
ARTICLE_ID = "2062463440527136754"


class AnswerClient:
    def get_text(self, url, headers=None):
        self.url = url
        payload = {
            "renderHtml": {
                "title": "如何正确使用知乎？",
                "desc": "<p>问题说明</p>",
                "content": (
                    "<script>fetch('tracking')</script>"
                    "<p>第一段 <b>回答</b>。</p>"
                    '<figure><img src="https://pic.example/a.jpg" '
                    'data-rawwidth="1200" data-rawheight="800"></figure>'
                    "<p>第二段。</p>""<a href=\"javascript:alert(1)\" onclick=\"bad()\">不安全链接</a>"
                ),
                "type": "ans",
                "created": 1768048419,
                "author": {
                    "name": "聂飞琼",
                    "logo": "https://pic.example/avatar.jpg",
                    "info": "此心即宇宙",
                },
                "upvoted_count": 22,
                "comment_count": 6,
                "favorites": 14,
                "answer_count": 1505,
                "question_token": QUESTION_ID,
            }
        }
        body = (
            "<html><body><script>"
            "window.g_initialProps = "
            + json.dumps(payload, ensure_ascii=False)
            + ";</script></body></html>"
        )
        return HttpResponse(
            url=url,
            content_type="text/html; charset=utf-8",
            body=body.encode(),
        )


class ArticleClient:
    def __init__(self, hydration=True):
        self.hydration = hydration
        self.urls = []

    def get_text(self, url, headers=None):
        self.urls.append(url)
        if "zhuanlan.zhihu.com" in url and self.hydration:
            article = {
                "id": ARTICLE_ID,
                "title": "公开文章",
                "content": (
                    "<p>文章 <strong>正文</strong>。</p>"
                    '<img data-original="https://pic.example/full.jpg" '
                    'data-rawwidth="1000" data-rawheight="600">'
                ),
                "excerpt": "<p>摘要</p>",
                "created": 1784509890,
                "updated": 1784687528,
                "commentCount": 11,
                "voteupCount": 211,
                "favlistsCount": 7,
                "likedCount": 3,
                "imageUrl": "https://pic.example/cover.jpg",
                "author": {
                    "id": "author-id",
                    "name": "王善应",
                    "headline": "作者简介",
                    "urlToken": "bajuexuanyuan",
                    "url": "/people/bajuexuanyuan",
                    "avatarUrl": "https://pic.example/avatar.jpg",
                },
                "topics": [
                    {
                        "id": "19870638",
                        "name": "内容营销",
                        "url": "https://www.zhihu.com/api/v4/topics/19870638",
                    }
                ],
                "type": "article",
            }
            payload = {
                "initialState": {
                    "entities": {
                        "articles": {ARTICLE_ID: article}
                    }
                }
            }
            encoded = html.escape(
                json.dumps(payload, ensure_ascii=False),
                quote=False,
            )
            body = (
                '<html><script id="js-initialData" type="text/json">'
                + encoded
                + "</script></html>"
            )
            return HttpResponse(
                url=url,
                content_type="text/html; charset=utf-8",
                body=body.encode(),
            )

        if "zhuanlan.zhihu.com" in url and not self.hydration:
            raise FetchError("zhuanlan unavailable")

        payload = {
            "renderHtml": {
                "title": "公开文章 fallback",
                "content": "<p>Fallback 正文。</p>",
                "type": "art",
                "created": 1784687528,
                "author": {
                    "name": "王善应",
                    "logo": "https://pic.example/avatar.jpg",
                    "info": "作者简介",
                },
                "img": "https://pic.example/cover.jpg",
                "upvoted_count": 211,
                "comment_count": 11,
                "favorites": 7,
            }
        }
        body = (
            "<html><script>window.g_initialProps = "
            + json.dumps(payload, ensure_ascii=False)
            + ";</script></html>"
        )
        return HttpResponse(
            url=url,
            content_type="text/html; charset=utf-8",
            body=body.encode(),
        )


class ZhihuExtractorTests(unittest.TestCase):
    def test_answer_uses_public_tardis_reader_and_sanitizes_tracking(self):
        client = AnswerClient()
        result = ZhihuAnswerExtractor(client).extract(
            f"https://www.zhihu.com/question/{QUESTION_ID}/answer/{ANSWER_ID}"
        )
        self.assertEqual(
            client.url,
            f"https://www.zhihu.com/tardis/zm/ans/{ANSWER_ID}",
        )
        self.assertEqual(result.platform, "zhihu")
        self.assertEqual(result.kind, "answer")
        self.assertEqual(
            result.extraction_method,
            "first_party_public_tardis_ssr_json",
        )
        self.assertEqual(result.title, "如何正确使用知乎？")
        self.assertEqual(result.author, "聂飞琼")
        self.assertIn("第一段 回答。", result.text)
        self.assertNotIn("tracking", result.text)
        self.assertNotIn("<script", result.html)
        self.assertNotIn("javascript:", result.html)
        self.assertNotIn("onclick=", result.html)
        self.assertEqual(result.media[0]["url"], "https://pic.example/a.jpg")
        self.assertEqual(result.metadata["stats"]["voteup_count"], 22)
        self.assertFalse(result.metadata["requires_login"])
        self.assertFalse(result.metadata["uses_private_signature"])

    def test_article_uses_embedded_public_initial_state(self):
        result = ZhihuArticleExtractor(ArticleClient()).extract(
            f"https://zhuanlan.zhihu.com/p/{ARTICLE_ID}"
        )
        self.assertEqual(result.platform, "zhihu")
        self.assertEqual(result.kind, "article")
        self.assertEqual(
            result.extraction_method,
            "first_party_embedded_initial_state",
        )
        self.assertEqual(result.title, "公开文章")
        self.assertEqual(result.author, "王善应")
        self.assertEqual(result.text, "文章 正文。")
        self.assertEqual(result.metadata["topics"][0]["name"], "内容营销")
        self.assertEqual(
            result.metadata["author"]["url"],
            "https://www.zhihu.com/people/bajuexuanyuan",
        )
        self.assertEqual(result.media[0]["url"], "https://pic.example/cover.jpg")
        self.assertEqual(result.media[1]["url"], "https://pic.example/full.jpg")

    def test_article_falls_back_to_public_tardis_reader(self):
        client = ArticleClient(hydration=False)
        result = ZhihuArticleExtractor(client).extract(
            f"https://zhuanlan.zhihu.com/p/{ARTICLE_ID}"
        )
        self.assertEqual(
            result.extraction_method,
            "first_party_public_tardis_ssr_json",
        )
        self.assertEqual(result.title, "公开文章 fallback")
        self.assertIn("Fallback 正文。", result.text)
        self.assertTrue(any("falling back" in w for w in result.warnings))

    def test_supports_public_answer_and_article_shapes(self):
        answer = ZhihuAnswerExtractor(AnswerClient())
        article = ZhihuArticleExtractor(ArticleClient())
        self.assertTrue(
            answer.supports(
                f"https://www.zhihu.com/question/{QUESTION_ID}/answer/{ANSWER_ID}"
            )
        )
        self.assertTrue(
            answer.supports(
                f"https://www.zhihu.com/tardis/zm/ans/{ANSWER_ID}"
            )
        )
        self.assertFalse(answer.supports("https://www.zhihu.com/question/123"))
        self.assertTrue(
            article.supports(f"https://zhuanlan.zhihu.com/p/{ARTICLE_ID}")
        )
        self.assertTrue(
            article.supports(
                f"https://www.zhihu.com/tardis/zm/art/{ARTICLE_ID}"
            )
        )
        self.assertFalse(article.supports("https://www.zhihu.com/people/test"))


if __name__ == "__main__":
    unittest.main()
