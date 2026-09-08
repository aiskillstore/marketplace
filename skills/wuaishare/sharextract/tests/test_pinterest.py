import json
import unittest

from sharextract.extractors.base import ExtractorError
from sharextract.extractors.pinterest import PinterestPinExtractor
from sharextract.http import HttpResponse


PIN = "https://www.pinterest.com/pin/444941638158153317/"

HTML = """<!doctype html>
<html>
<head>
  <title>Fallback title</title>
  <meta property="og:site_name" content="Pinterest">
  <meta property="og:type" content="pinterestapp:pin">
  <meta property="og:title" content="Leaning tower of Pisa">
  <meta property="og:description" content="The leaning tower of Pisa in Italy.">
  <meta property="og:image" content="https://i.pinimg.com/736x/example.jpg">
  <meta property="og:image:width" content="736">
  <meta property="og:image:height" content="490">
  <meta property="og:updated_time" content="2014-04-28T12:40:14.000Z">
  <meta property="og:url" content="https://de.pinterest.com/pin/example--999999999999999999/">
  <link rel="canonical" href="https://de.pinterest.com/pin/example--999999999999999999/">
  <meta property="og:see_also" content="https://example.com/original">
</head>
<body>
  <script id="__PWS_DATA__">{"secret_internal_state": true}</script>
</body>
</html>
"""


class FakeClient:
    timeout = 20.0

    def __init__(self, html=HTML):
        self.html = html
        self.calls = []

    def get_text(self, url, headers=None):
        self.calls.append((url, headers))
        return HttpResponse(
            url=url,
            content_type="text/html; charset=utf-8",
            body=self.html.encode(),
        )


class PinterestExtractorTests(unittest.TestCase):
    def test_extracts_standard_open_graph_pin(self):
        client = FakeClient()
        result = PinterestPinExtractor(client).extract(PIN)

        self.assertEqual(result.platform, "pinterest")
        self.assertEqual(result.kind, "image_post")
        self.assertEqual(
            result.extraction_method,
            "standard_open_graph_pinterest_pin",
        )
        self.assertEqual(result.canonical_url, PIN)
        self.assertEqual(result.title, "Leaning tower of Pisa")
        self.assertEqual(result.text, "The leaning tower of Pisa in Italy.")
        self.assertEqual(result.metadata["pin_id"], "444941638158153317")
        self.assertEqual(
            result.metadata["updated_at"],
            "2014-04-28T12:40:14.000Z",
        )
        self.assertEqual(
            result.metadata["source_link"],
            "https://example.com/original",
        )
        self.assertEqual(
            result.metadata["declared_canonical_url"],
            "https://de.pinterest.com/pin/example--999999999999999999/",
        )
        self.assertEqual(
            result.metadata["declared_canonical_pin_id"],
            "999999999999999999",
        )
        self.assertEqual(
            result.metadata["declared_og_url"],
            "https://de.pinterest.com/pin/example--999999999999999999/",
        )
        self.assertTrue(result.metadata["declared_canonical_mismatch"])
        self.assertTrue(
            any("different Pin ID" in warning for warning in result.warnings)
        )
        self.assertFalse(result.metadata["uses_internal_pws_state"])
        self.assertFalse(result.metadata["uses_api_token"])
        self.assertFalse(result.metadata["uses_browser"])
        self.assertEqual(
            result.media,
            [
                {
                    "type": "image",
                    "url": "https://i.pinimg.com/736x/example.jpg",
                    "width": 736,
                    "height": 490,
                }
            ],
        )

        serialized = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn("secret_internal_state", serialized)
        self.assertNotIn("__PWS_DATA__", serialized)

    def test_supports_localized_subdomains_and_slug_pin_paths(self):
        extractor = PinterestPinExtractor(FakeClient())
        for url in [
            PIN,
            "https://de.pinterest.com/pin/444941638158153317/",
            "https://jp.pinterest.com/pin/example-title--444941638158153317/",
            "https://in.pinterest.com/pin/example-title--444941638158153317/",
        ]:
            self.assertTrue(extractor.supports(url), url)

    def test_rejects_non_pin_and_external_hosts(self):
        extractor = PinterestPinExtractor(FakeClient())
        for url in [
            "https://www.pinterest.com/example/profile/",
            "https://www.pinterest.com/pin/not-a-number/",
            "https://example.com/pin/444941638158153317/",
            "https://pinterest.example/pin/444941638158153317/",
        ]:
            self.assertFalse(extractor.supports(url), url)

    def test_rejects_wrong_og_type(self):
        bad = HTML.replace(
            'content="pinterestapp:pin"',
            'content="article"',
        )
        with self.assertRaisesRegex(ExtractorError, "not a validated Pin"):
            PinterestPinExtractor(FakeClient(bad)).extract(PIN)


if __name__ == "__main__":
    unittest.main()
