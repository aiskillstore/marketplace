import json
import unittest

from sharextract.extractors.meta_embeds import (
    FacebookPostExtractor,
    InstagramPostExtractor,
    ThreadsPostExtractor,
)
from sharextract.http import HttpResponse


THREADS = "https://www.threads.com/@threads/post/DWjTI0cgH5O/"
INSTAGRAM = "https://www.instagram.com/p/fA9uwTtkSN/"
FACEBOOK = (
    "https://www.facebook.com/kevinloveofficial/posts/"
    "pfbid0nWhZeiMVjzLHVjzR6QngXeVug8Nw4YxncbbZrquMu72r3HM8a73k55keRWiaWNLTl/"
)


THREADS_HTML = """<html><head>
<meta property="og:type" content="article">
<meta property="og:title" content="Threads (@threads) on Threads">
<meta property="og:description" content="The smell of a fresh box of crayons is undefeated">
<meta property="og:url" content="https://www.threads.com/@threads/post/DWjTI0cgH5O">
<meta property="og:image" content="https://cdninstagram.example/profile.jpg">
<link rel="canonical" href="https://www.threads.com/@threads/post/DWjTI0cgH5O">
</head></html>"""

INSTAGRAM_HTML = """<html><head>
<meta property="og:type" content="video">
<meta property="og:title" content='Diego Moreno Quinteiro on Instagram: "Wii Gato (Lipe Sleep)"'>
<meta property="og:description" content='3,699 likes, 71 comments - diegoquinteiro on June 16, 2015: "Wii Gato (Lipe Sleep)". '>
<meta property="og:image" content="https://cdninstagram.example/post.jpg">
<meta property="og:url" content="https://www.instagram.com/diegoquinteiro/reel/fA9uwTtkSN/">
<link rel="canonical" href="https://www.instagram.com/reel/fA9uwTtkSN/">
</head></html>"""

FACEBOOK_HTML = """<html><head>
<meta property="og:type" content="video.other">
<meta property="og:title" content="Kevin Love">
<meta property="og:description" content="The best thing I ever did was raise my hand and say, I need help.">
<meta property="og:image" content="https://fbcdn.example/post.jpg">
<meta property="og:url" content="https://www.facebook.com/kevinloveofficial/posts/example-slug/1361298268691553/">
<link rel="canonical" href="https://www.facebook.com/kevinloveofficial/posts/example-slug/1361298268691553/">
</head></html>"""


class FakeClient:
    timeout = 20.0

    def __init__(self, page_html, *, oembed_error=None):
        self.page_html = page_html
        self.oembed_error = oembed_error
        self.text_calls = []
        self.json_calls = []

    def get_text(self, url, headers=None):
        self.text_calls.append((url, headers))
        return HttpResponse(
            url=url,
            content_type="text/html; charset=utf-8",
            body=self.page_html.encode(),
        )

    def get_json(self, url, headers=None):
        self.json_calls.append((url, headers))
        if self.oembed_error is not None:
            raise self.oembed_error
        provider = (
            "Threads"
            if "threads.com/oembed" in url
            else "Instagram"
            if "instagram_oembed" in url
            else "Facebook"
        )
        payload = {
            "type": "rich",
            "version": "1.0",
            "provider_name": provider,
            "provider_url": "https://example.invalid/",
            "width": 658,
            "html": f"<blockquote>{provider} embed</blockquote>",
        }
        return (
            HttpResponse(
                url=url,
                content_type="application/json",
                body=json.dumps(payload).encode(),
            ),
            payload,
        )


class MetaEmbedsTests(unittest.TestCase):
    def test_threads_uses_og_text_but_does_not_export_profile_image(self):
        client = FakeClient(THREADS_HTML)
        result = ThreadsPostExtractor(client).extract(THREADS)

        self.assertEqual(result.platform, "threads")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(
            result.extraction_method,
            "standard_open_graph_threads_post",
        )
        self.assertEqual(
            result.canonical_url,
            "https://www.threads.com/t/DWjTI0cgH5O/",
        )
        self.assertEqual(result.author, "threads")
        self.assertEqual(
            result.text,
            "The smell of a fresh box of crayons is undefeated",
        )
        self.assertEqual(result.media, [])
        self.assertEqual(
            result.metadata["og_preview_image_url"],
            "https://cdninstagram.example/profile.jpg",
        )
        self.assertEqual(result.metadata["oembed"]["status"], "ok")
        self.assertTrue(result.html.startswith("<blockquote>"))
        self.assertFalse(result.metadata["uses_access_token"])
        self.assertFalse(result.metadata["uses_browser"])

    def test_threads_short_and_legacy_urls_are_supported(self):
        extractor = ThreadsPostExtractor(FakeClient(THREADS_HTML))
        for url in [
            THREADS,
            "https://www.threads.com/t/DWjTI0cgH5O/",
            "https://www.threads.net/@threads/post/DWjTI0cgH5O",
            "https://threads.net/t/DWjTI0cgH5O/",
        ]:
            self.assertTrue(extractor.supports(url), url)
        self.assertFalse(
            extractor.supports("https://www.threads.com/@threads")
        )

    def test_oembed_failure_preserves_threads_open_graph(self):
        result = ThreadsPostExtractor(
            FakeClient(
                THREADS_HTML,
                oembed_error=RuntimeError("temporary oembed failure"),
            )
        ).extract(THREADS)
        self.assertTrue(result.text)
        self.assertEqual(result.metadata["oembed"]["status"], "error")
        self.assertTrue(result.warnings)

    def test_instagram_parses_caption_stats_and_reel_identity(self):
        client = FakeClient(INSTAGRAM_HTML)
        result = InstagramPostExtractor(client).extract(INSTAGRAM)

        self.assertEqual(result.platform, "instagram")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(
            result.extraction_method,
            "standard_open_graph_instagram_post",
        )
        self.assertEqual(
            result.canonical_url,
            "https://www.instagram.com/reel/fA9uwTtkSN/",
        )
        self.assertEqual(result.author, "diegoquinteiro")
        self.assertEqual(result.text, "Wii Gato (Lipe Sleep)")
        self.assertEqual(result.metadata["likes_display"], "3,699")
        self.assertEqual(result.metadata["comments_display"], "71")
        self.assertEqual(
            result.metadata["published_date_display"],
            "June 16, 2015",
        )
        self.assertFalse(result.metadata["declared_shortcode_mismatch"])
        self.assertEqual(
            result.media,
            [
                {
                    "type": "video",
                    "url": "https://www.instagram.com/reel/fA9uwTtkSN/",
                    "thumbnail_url": "https://cdninstagram.example/post.jpg",
                }
            ],
        )
        self.assertNotIn("access_token", client.json_calls[0][0])

    def test_instagram_shortcode_mismatch_keeps_requested_identity(self):
        bad = INSTAGRAM_HTML.replace(
            "fA9uwTtkSN/",
            "DIFFERENT123/",
        )
        result = InstagramPostExtractor(
            FakeClient(bad)
        ).extract(INSTAGRAM)
        self.assertEqual(
            result.canonical_url,
            "https://www.instagram.com/reel/fA9uwTtkSN/",
        )
        self.assertTrue(result.metadata["declared_shortcode_mismatch"])
        self.assertTrue(result.warnings)

    def test_instagram_supports_post_and_reel_only(self):
        extractor = InstagramPostExtractor(FakeClient(INSTAGRAM_HTML))
        for url in [
            INSTAGRAM,
            "https://instagram.com/reel/fA9uwTtkSN/",
            "https://www.instagram.com/diegoquinteiro/reel/fA9uwTtkSN/",
        ]:
            self.assertTrue(extractor.supports(url), url)
        for url in [
            "https://www.instagram.com/diegoquinteiro/",
            "https://www.instagram.com/stories/diegoquinteiro/123/",
        ]:
            self.assertFalse(extractor.supports(url), url)

    def test_facebook_public_post_uses_og_and_tokenless_oembed(self):
        client = FakeClient(FACEBOOK_HTML)
        result = FacebookPostExtractor(client).extract(FACEBOOK)

        self.assertEqual(result.platform, "facebook")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(
            result.extraction_method,
            "standard_open_graph_facebook_post",
        )
        self.assertEqual(
            result.canonical_url,
            FACEBOOK,
        )
        self.assertEqual(result.author, "Kevin Love")
        self.assertIn("raise my hand", result.text)
        self.assertTrue(result.metadata["declared_post_id_mismatch"])
        self.assertEqual(
            result.metadata["declared_post_id"],
            "1361298268691553",
        )
        self.assertEqual(
            result.media,
            [
                {
                    "type": "video",
                    "url": FACEBOOK,
                    "thumbnail_url": "https://fbcdn.example/post.jpg",
                }
            ],
        )
        self.assertEqual(result.metadata["oembed"]["status"], "ok")
        self.assertNotIn("access_token", client.json_calls[0][0])
        self.assertFalse(result.metadata["uses_access_token"])
        self.assertFalse(result.metadata["uses_browser"])
        self.assertFalse(result.metadata["stream_urls_exported"])

    def test_facebook_supports_documented_post_shape_only(self):
        extractor = FacebookPostExtractor(FakeClient(FACEBOOK_HTML))
        for url in [
            FACEBOOK,
            "https://m.facebook.com/kevinloveofficial/posts/123456/",
            "https://www.facebook.com/kevinloveofficial/posts/slug/123456/",
        ]:
            self.assertTrue(extractor.supports(url), url)
        for url in [
            "https://www.facebook.com/kevinloveofficial/",
            "https://www.facebook.com/reel/123456/",
            "https://example.com/user/posts/123/",
        ]:
            self.assertFalse(extractor.supports(url), url)


if __name__ == "__main__":
    unittest.main()
