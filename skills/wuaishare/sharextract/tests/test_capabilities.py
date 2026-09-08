import unittest

from sharextract.capabilities import get_capabilities


class CapabilitiesTests(unittest.TestCase):
    def test_reports_core_routes_and_security_boundary(self):
        data = get_capabilities()
        names = {item["name"] for item in data["extractors"]}
        self.assertIn("deepseek-share", names)
        self.assertIn("chatgpt-share", names)
        self.assertIn("bluesky-atproto", names)
        self.assertIn("x-oembed", names)
        self.assertIn("youtube-oembed", names)
        self.assertIn("vimeo-oembed", names)
        self.assertIn("bilibili-video", names)
        self.assertIn("rss-atom", names)
        self.assertIn("zhihu-answer", names)
        self.assertIn("zhihu-article", names)
        self.assertIn("weibo-status", names)
        self.assertIn("tiktok-oembed", names)
        self.assertIn("douyin-video", names)
        self.assertIn("xiaohongshu-note", names)
        self.assertIn("kuaishou-video", names)
        self.assertIn("kuaishou-atlas", names)
        self.assertIn("reddit-oembed", names)
        self.assertIn("telegram-post", names)
        self.assertIn("pinterest-pin", names)
        self.assertIn("threads-post", names)
        self.assertIn("instagram-post", names)
        self.assertIn("facebook-post", names)
        self.assertIn("linkedin-post", names)
        self.assertIn("generic-web", names)
        self.assertFalse(data["security_boundary"]["bypasses_authentication"])


if __name__ == "__main__":
    unittest.main()
