import json
import unittest

from sharextract.extractors.reddit import RedditPostExtractor
from sharextract.http import HttpResponse


POST = (
    "https://www.reddit.com/r/redditdev/comments/"
    "1txd5mm/reddit_json_endpoints_returning_403/"
)
COMMENT = POST + "opv6zof/"


OEMBED = {
    "author_name": "MrMRUU",
    "html": (
        '<blockquote class="reddit-embed-bq">'
        '<a href="' + POST + '">Reddit .json endpoints returning 403</a>'
        "</blockquote>"
    ),
    "provider_name": "reddit",
    "provider_url": "https://www.reddit.com",
    "title": "Reddit .json endpoints returning 403",
    "type": "rich",
    "height": 316,
}


ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Reddit .json endpoints returning 403 : redditdev</title>
  <updated>2026-06-05T08:21:13+00:00</updated>
  <id>/r/redditdev/comments/1txd5mm/example.rss</id>
  <link rel="self" href="https://www.reddit.com/r/redditdev/comments/1txd5mm/example.rss"/>
  <entry>
    <title>Reddit .json endpoints returning 403</title>
    <author><name>/u/MrMRUU</name></author>
    <updated>2026-06-05T06:46:20+00:00</updated>
    <link rel="alternate" href="https://www.reddit.com/r/redditdev/comments/1txd5mm/reddit_json_endpoints_returning_403/"/>
    <content type="html">&lt;p&gt;Trying to fetch public Reddit data using the .json endpoints.&lt;/p&gt;
      &lt;p&gt;submitted by /u/MrMRUU [link] [comments]&lt;/p&gt;
    </content>
  </entry>
  <entry>
    <title>/u/TourStrong8443 on Reddit .json endpoints returning 403</title>
    <author><name>/u/TourStrong8443</name></author>
    <updated>2026-06-05T08:21:13+00:00</updated>
    <link rel="alternate" href="https://www.reddit.com/r/redditdev/comments/1txd5mm/reddit_json_endpoints_returning_403/opv6zof/"/>
    <content type="html">&lt;p&gt;A while back Reddit updated their API usage policies.&lt;/p&gt;</content>
  </entry>
</feed>
"""


class FakeClient:
    def __init__(self, *, rss_error=None):
        self.rss_error = rss_error
        self.json_calls = []
        self.text_calls = []

    def get_json(self, url, headers=None):
        self.json_calls.append((url, headers))
        return (
            HttpResponse(
                url=url,
                content_type="application/json",
                body=json.dumps(OEMBED).encode(),
            ),
            OEMBED,
        )

    def get_text(self, url, headers=None):
        self.text_calls.append((url, headers))
        if self.rss_error is not None:
            raise self.rss_error
        return HttpResponse(
            url=url,
            content_type="application/atom+xml; charset=UTF-8",
            body=ATOM.encode(),
        )


class RedditExtractorTests(unittest.TestCase):
    def test_extracts_documented_oembed_and_atom_thread(self):
        client = FakeClient()
        result = RedditPostExtractor(client).extract(POST)

        self.assertEqual(result.platform, "reddit")
        self.assertEqual(result.kind, "discussion_thread")
        self.assertEqual(
            result.extraction_method,
            "documented_reddit_oembed",
        )
        self.assertEqual(
            result.title,
            "Reddit .json endpoints returning 403",
        )
        self.assertEqual(result.author, "MrMRUU")
        self.assertEqual(
            result.text,
            "Trying to fetch public Reddit data using the .json endpoints.",
        )
        self.assertEqual(result.canonical_url, POST)
        self.assertEqual(len(result.messages), 1)
        self.assertEqual(result.messages[0].role, "comment")
        self.assertEqual(
            result.messages[0].author,
            "TourStrong8443",
        )
        self.assertEqual(
            result.messages[0].text,
            "A while back Reddit updated their API usage policies.",
        )
        self.assertEqual(
            result.messages[0].created_at,
            "2026-06-05T08:21:13+00:00",
        )
        self.assertEqual(
            result.metadata["thread_rss"]["status"],
            "ok",
        )
        self.assertEqual(
            result.metadata["thread_rss"]["comment_count"],
            1,
        )
        self.assertFalse(result.metadata["uses_json_endpoint"])
        self.assertFalse(result.metadata["uses_oauth"])
        self.assertFalse(result.metadata["uses_browser"])
        self.assertIn(
            "https%3A%2F%2Fwww.reddit.com%2Fr%2Fredditdev",
            client.json_calls[0][0],
        )
        self.assertEqual(client.text_calls[0][0], POST.rstrip("/") + ".rss")

    def test_rss_failure_preserves_oembed_result(self):
        client = FakeClient(rss_error=RuntimeError("429 Too Many Requests"))
        result = RedditPostExtractor(client).extract(POST)
        self.assertEqual(
            result.extraction_method,
            "documented_reddit_oembed",
        )
        self.assertEqual(result.text, result.title)
        self.assertEqual(result.messages, [])
        self.assertEqual(
            result.metadata["thread_rss"]["status"],
            "error",
        )
        self.assertIn("429", result.metadata["thread_rss"]["error"])
        self.assertTrue(result.warnings)

    def test_comment_permalink_canonicalizes_to_thread(self):
        result = RedditPostExtractor(FakeClient()).extract(COMMENT)
        self.assertEqual(result.canonical_url, POST)
        self.assertEqual(result.metadata["post_id"], "1txd5mm")

    def test_supports_only_reddit_thread_shapes(self):
        extractor = RedditPostExtractor(FakeClient())
        for url in [
            POST,
            COMMENT,
            POST.replace("www.reddit.com", "reddit.com"),
            POST.replace("www.reddit.com", "m.reddit.com"),
        ]:
            self.assertTrue(extractor.supports(url), url)
        for url in [
            "https://www.reddit.com/r/redditdev/",
            "https://old.reddit.com/r/redditdev/comments/1txd5mm/example/",
            "https://example.com/r/redditdev/comments/1txd5mm/example/",
        ]:
            self.assertFalse(extractor.supports(url), url)


if __name__ == "__main__":
    unittest.main()
