import unittest

from sharextract.extractors.oembed import (
    TikTokOEmbedExtractor,
    VimeoOEmbedExtractor,
    XPostOEmbedExtractor,
    YouTubeOEmbedExtractor,
)
from sharextract.http import HttpResponse


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.urls = []

    def get_json(self, url, headers=None):
        self.urls.append(url)
        return HttpResponse(
            url=url,
            content_type="application/json",
            body=b"{}",
        ), self.payload


class OEmbedExtractorTests(unittest.TestCase):
    def test_x_oembed_extracts_visible_post_text(self):
        client = FakeClient(
            {
                "url": "https://x.com/Interior/status/463440424141459456",
                "author_name": "U.S. Department of the Interior",
                "html": (
                    '<blockquote class="twitter-tweet"><p lang="en">'
                    'Sunsets are great <a href="#">#nature</a></p>'
                    '&mdash; U.S. Department of the Interior</blockquote>'
                ),
                "type": "rich",
                "provider_name": "Twitter",
                "version": "1.0",
            }
        )
        result = XPostOEmbedExtractor(client).extract(
            "https://x.com/Interior/status/463440424141459456"
        )
        self.assertEqual(result.platform, "x")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(result.text, "Sunsets are great #nature")
        self.assertEqual(result.author, "U.S. Department of the Interior")
        self.assertEqual(result.extraction_method, "documented_oembed")
        self.assertIn("omit_script=1", client.urls[0])

    def test_youtube_oembed_normalizes_video(self):
        client = FakeClient(
            {
                "title": "Video title",
                "author_name": "Creator",
                "type": "video",
                "thumbnail_url": "https://img.example/thumb.jpg",
                "width": 480,
                "height": 270,
                "html": "<iframe></iframe>",
            }
        )
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = YouTubeOEmbedExtractor(client).extract(url)
        self.assertEqual(result.platform, "youtube")
        self.assertEqual(result.title, "Video title")
        self.assertEqual(result.media[0]["type"], "video")
        self.assertEqual(result.media[0]["thumbnail_url"], "https://img.example/thumb.jpg")

    def test_tiktok_oembed_normalizes_video(self):
        client = FakeClient(
            {
                "version": "1.0",
                "type": "video",
                "title": "Public TikTok caption #example",
                "author_name": "Creator",
                "author_unique_id": "creator",
                "author_url": "https://www.tiktok.com/@creator",
                "thumbnail_url": "https://img.example/tiktok.jpg",
                "thumbnail_width": 576,
                "thumbnail_height": 1024,
                "provider_name": "TikTok",
                "html": "<blockquote></blockquote>",
            }
        )
        url = "https://www.tiktok.com/@creator/video/6718335390845095173"
        result = TikTokOEmbedExtractor(client).extract(url)
        self.assertEqual(result.platform, "tiktok")
        self.assertEqual(result.kind, "video")
        self.assertEqual(result.extraction_method, "documented_oembed")
        self.assertEqual(result.title, "Public TikTok caption #example")
        self.assertEqual(result.text, "Public TikTok caption #example")
        self.assertEqual(result.author, "Creator")
        self.assertEqual(
            result.metadata["oembed"]["author_unique_id"],
            "creator",
        )
        self.assertIn("www.tiktok.com%2F%40creator%2Fvideo", client.urls[0])

    def test_vimeo_oembed_uses_description_and_duration(self):
        client = FakeClient(
            {
                "title": "Inside Vimeo Staff Picks",
                "author_name": "Vimeo",
                "description": "A public Vimeo description.",
                "type": "video",
                "duration": 183,
                "thumbnail_url": "https://img.example/vimeo.jpg",
                "html": "<iframe></iframe>",
            }
        )
        result = VimeoOEmbedExtractor(client).extract(
            "https://vimeo.com/863362136"
        )
        self.assertEqual(result.platform, "vimeo")
        self.assertEqual(result.text, "A public Vimeo description.")
        self.assertEqual(result.media[0]["duration_seconds"], 183)

    def test_url_matchers_are_narrow(self):
        x = XPostOEmbedExtractor(FakeClient({}))
        yt = YouTubeOEmbedExtractor(FakeClient({}))
        tk = TikTokOEmbedExtractor(FakeClient({}))
        vm = VimeoOEmbedExtractor(FakeClient({}))
        self.assertTrue(x.supports("https://x.com/a/status/123"))
        self.assertFalse(x.supports("https://x.com/a"))
        self.assertTrue(yt.supports("https://youtu.be/dQw4w9WgXcQ"))
        self.assertTrue(yt.supports("https://www.youtube.com/shorts/abc"))
        self.assertFalse(yt.supports("https://www.youtube.com/@creator"))
        self.assertTrue(
            tk.supports(
                "https://www.tiktok.com/@scout2015/video/6718335390845095173"
            )
        )
        self.assertFalse(tk.supports("https://www.tiktok.com/@scout2015"))
        self.assertFalse(tk.supports("https://vt.tiktok.com/abc"))
        self.assertTrue(vm.supports("https://vimeo.com/863362136"))
        self.assertFalse(vm.supports("https://vimeo.com/staff"))


if __name__ == "__main__":
    unittest.main()
