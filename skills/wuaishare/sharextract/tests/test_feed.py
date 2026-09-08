import unittest

from sharextract.extractors.base import ExtractorError
from sharextract.extractors.generic import GenericWebExtractor
from sharextract.http import HttpResponse


class FakeClient:
    def __init__(self, body: str, content_type: str, final_url: str):
        self.body = body
        self.content_type = content_type
        self.final_url = final_url

    def get_text(self, url, headers=None):
        return HttpResponse(
            url=self.final_url,
            content_type=self.content_type,
            body=self.body.encode("utf-8"),
        )

    def get_json(self, url, headers=None):
        raise AssertionError("Feed tests must not make a second JSON request")


RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
 xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Example News</title>
    <link>https://example.com/news</link>
    <description><![CDATA[<strong>Latest</strong> updates]]></description>
    <lastBuildDate>Fri, 28 Aug 2026 13:56:48 +0000</lastBuildDate>
    <language>en-US</language>
    <item>
      <guid>post-1</guid>
      <title>First post</title>
      <link>/news/first</link>
      <dc:creator>Alice</dc:creator>
      <pubDate>Fri, 28 Aug 2026 12:00:00 +0000</pubDate>
      <description><![CDATA[<p>Short <b>summary</b>.</p>]]></description>
      <content:encoded><![CDATA[
        <p>Full <strong>article</strong> text.</p>
        <script>do-not-export()</script>
      ]]></content:encoded>
      <category>Release</category>
      <enclosure
        url="https://cdn.example.com/audio.mp3"
        type="audio/mpeg"
        length="12345" />
    </item>
  </channel>
</rss>
"""

ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en-US">
  <id>tag:example.com,2026:feed</id>
  <title>Example Commits</title>
  <subtitle>Recent project changes</subtitle>
  <link rel="alternate" type="text/html" href="/commits/main"/>
  <link rel="self" type="application/atom+xml" href="/commits/main.atom"/>
  <updated>2026-09-06T06:07:01Z</updated>
  <author><name>Example Org</name></author>
  <entry>
    <id>tag:example.com,2026:commit-1</id>
    <title>Ship feature</title>
    <link rel="alternate" href="/commit/abc"/>
    <updated>2026-09-06T06:07:01Z</updated>
    <author><name>Bob</name></author>
    <summary type="html">&lt;p&gt;One &lt;b&gt;change&lt;/b&gt;.&lt;/p&gt;</summary>
    <category term="release"/>
    <link
      rel="enclosure"
      href="/assets/demo.mp4"
      type="video/mp4"
      length="9876"/>
  </entry>
</feed>
"""

HTML_DISCOVERY = """<!doctype html>
<html>
<head>
  <title>Example Site</title>
  <link rel="alternate" type="application/rss+xml" href="/feed.xml">
  <link rel="alternate stylesheet" type="application/atom+xml" href="atom.xml">
  <link rel="alternate" type="application/rss+xml" href="/feed.xml">
</head>
<body>
  <main><p>This is a substantial public page body used for feed discovery.</p></main>
</body>
</html>
"""


class FeedExtractorTests(unittest.TestCase):
    def test_rss_20_is_normalized_without_second_request(self):
        extractor = GenericWebExtractor(
            FakeClient(
                RSS,
                "application/rss+xml; charset=UTF-8",
                "https://example.com/feed/",
            )
        )
        result = extractor.extract("https://example.com/feed/")

        self.assertEqual(result.platform, "rss")
        self.assertEqual(result.kind, "feed")
        self.assertEqual(result.extraction_method, "standard_rss")
        self.assertEqual(result.title, "Example News")
        self.assertEqual(
            result.metadata["feed"]["updated_at"],
            "2026-08-28T13:56:48+00:00",
        )
        self.assertEqual(result.metadata["feed"]["entry_count"], 1)

        entry = result.metadata["feed"]["entries"][0]
        self.assertEqual(entry["url"], "https://example.com/news/first")
        self.assertEqual(entry["author"], "Alice")
        self.assertEqual(entry["text"], "Full article text.")
        self.assertNotIn("do-not-export", result.text)
        self.assertEqual(entry["categories"], ["Release"])
        self.assertEqual(entry["media"][0]["type"], "audio")
        self.assertEqual(entry["media"][0]["length_bytes"], 12345)
        self.assertEqual(result.media[0]["entry_title"], "First post")

    def test_atom_is_normalized_and_relative_urls_are_resolved(self):
        extractor = GenericWebExtractor(
            FakeClient(
                ATOM,
                "application/atom+xml; charset=utf-8",
                "https://example.com/repo/commits/main.atom",
            )
        )
        result = extractor.extract(
            "https://example.com/repo/commits/main.atom"
        )

        self.assertEqual(result.platform, "atom")
        self.assertEqual(result.extraction_method, "standard_atom")
        self.assertEqual(
            result.canonical_url,
            "https://example.com/commits/main.atom",
        )
        self.assertEqual(
            result.metadata["feed"]["home_url"],
            "https://example.com/commits/main",
        )
        entry = result.metadata["feed"]["entries"][0]
        self.assertEqual(entry["url"], "https://example.com/commit/abc")
        self.assertEqual(entry["author"], "Bob")
        self.assertEqual(entry["summary"], "One change.")
        self.assertEqual(entry["categories"], ["release"])
        self.assertEqual(
            entry["media"][0]["url"],
            "https://example.com/assets/demo.mp4",
        )
        self.assertEqual(entry["media"][0]["type"], "video")

    def test_html_page_discovers_declared_rss_and_atom_feeds(self):
        extractor = GenericWebExtractor(
            FakeClient(
                HTML_DISCOVERY,
                "text/html; charset=utf-8",
                "https://example.com/blog/index.html",
            )
        )
        result = extractor.extract("https://example.com/blog/index.html")

        self.assertEqual(
            result.metadata["syndication_feeds"],
            [
                {
                    "type": "rss",
                    "url": "https://example.com/feed.xml",
                },
                {
                    "type": "atom",
                    "url": "https://example.com/blog/atom.xml",
                },
            ],
        )

    def test_dtd_or_entity_feed_is_rejected(self):
        malicious = """<?xml version="1.0"?>
<!DOCTYPE rss [
  <!ENTITY local SYSTEM "file:///etc/passwd">
]>
<rss version="2.0"><channel><title>&local;</title></channel></rss>
"""
        extractor = GenericWebExtractor(
            FakeClient(
                malicious,
                "application/rss+xml",
                "https://example.com/feed.xml",
            )
        )
        with self.assertRaises(ExtractorError):
            extractor.extract("https://example.com/feed.xml")


if __name__ == "__main__":
    unittest.main()
