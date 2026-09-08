import json
import unittest

from sharextract.extractors.generic import GenericWebExtractor
from sharextract.http import HttpResponse


HTML = """<!doctype html>
<html>
<head>
<title>Fallback title</title>
<meta property="og:title" content="Example Article">
<meta name="author" content="Ada Example">
<meta property="og:image" content="/cover.jpg">
<link rel="canonical" href="https://example.com/canonical">
<link rel="alternate" type="application/json+oembed" href="/oembed?id=1">
<script type="application/ld+json">
{"@type":"Article","headline":"LD title","datePublished":"2026-09-06"}
</script>
</head>
<body>
<nav>Noise navigation</nav>
<main>
<h1>Example Article</h1>
<p>This is the first paragraph with enough useful content to be included.</p>
<p>This is the second paragraph and it contains more readable article text.</p>
<p>This is the third paragraph so the main content passes the preferred threshold for article extraction.</p>
</main>
<footer>Noise footer</footer>
</body>
</html>"""


class FakeClient:
    def get_text(self, url, headers=None):
        return HttpResponse(
            url="https://example.com/a",
            content_type="text/html; charset=utf-8",
            body=HTML.encode(),
        )

    def get_json(self, url, headers=None):
        payload = {
            "type": "rich",
            "title": "oEmbed title",
            "author_name": "oEmbed author",
            "html": "<blockquote>embed</blockquote>",
            "thumbnail_url": "https://example.com/thumb.jpg",
        }
        return HttpResponse(url=url, content_type="application/json", body=b"{}"), payload


class GenericExtractorTests(unittest.TestCase):
    def test_structured_html_and_oembed(self):
        result = GenericWebExtractor(FakeClient()).extract("https://example.com/a")
        self.assertEqual(result.title, "oEmbed title")
        self.assertEqual(result.author, "oEmbed author")
        self.assertEqual(result.canonical_url, "https://example.com/canonical")
        self.assertNotIn("Noise navigation", result.text)
        self.assertNotIn("Noise footer", result.text)
        self.assertIn("first paragraph", result.text)
        self.assertEqual(result.kind, "embed")
        self.assertTrue(any(item["url"].endswith("thumb.jpg") for item in result.media))

    def test_public_json_document(self):
        class JsonClient(FakeClient):
            def get_text(self, url, headers=None):
                body = json.dumps({"title": "JSON title", "content": "JSON body"}).encode()
                return HttpResponse(url=url, content_type="application/json", body=body)

        result = GenericWebExtractor(JsonClient()).extract("https://example.com/data")
        self.assertEqual(result.kind, "structured_data")
        self.assertEqual(result.title, "JSON title")
        self.assertEqual(result.text, "JSON body")


if __name__ == "__main__":
    unittest.main()
