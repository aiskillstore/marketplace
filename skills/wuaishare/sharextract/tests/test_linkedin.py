import json
import unittest

from sharextract.extractors.linkedin import LinkedInPostExtractor
from sharextract.http import HttpResponse


POST = (
    "https://www.linkedin.com/posts/microsoft_"
    "june-activity-7477715981667086336-BV_s"
)
FEED = (
    "https://www.linkedin.com/feed/update/"
    "urn:li:activity:7477715981667086336"
)
EMBED = (
    "https://www.linkedin.com/embed/feed/update/"
    "urn:li:activity:7477715981667086336"
)


HTML = """<!doctype html><html><head>
<meta property="og:title" content="June 2026 | Microsoft | 88 comments">
<meta property="og:description" content="Fallback description | 88 comments on LinkedIn">
<meta property="og:image" content="https://media.licdn.com/preview.jpg">
<meta property="og:url" content="https://www.linkedin.com/feed/update/urn:li:activity:7477715981667086336">
<link rel="canonical" href="https://www.linkedin.com/feed/update/urn:li:activity:7477715981667086336">
</head><body>
<article data-activity-urn="urn:li:activity:7477715981667086336">
  <div data-test-id="main-feed-activity-embed-card__entity-lockup">
    <a href="https://www.linkedin.com/company/microsoft?trk=embed"
       data-tracking-control-name="public_post_embed_feed-actor-name">
      Microsoft
    </a>
    <p>29,035,744 followers</p>
    <time>2mo</time>
  </div>

  <p data-test-id="main-feed-activity-embed-card__commentary">
    The most meaningful breakthroughs happen when technology is built with people in mind.
  </p>

  <ul data-test-id="feed-images-content">
    <li data-test-id="feed-images-content__list-item">
      <img data-delayed-url="https://media.licdn.com/post-image.jpg"
           alt="Post image alt">
    </li>
  </ul>

  <a data-test-id="article-content"
     href="https://www.linkedin.com/pulse/june-microsoft?trk=embed">
    <img data-delayed-url="https://media.licdn.com/article-cover.jpg"
         alt="June 2026">
    <span data-test-id="article-content__title">June 2026</span>
    <span data-test-id="article-content__subtitle">Microsoft on LinkedIn</span>
  </a>

  <a data-test-id="social-actions__reactions"
     data-num-reactions="1071">1,071</a>
  <a data-test-id="social-actions__comments"
     data-num-comments="88">88 Comments</a>
</article>
</body></html>
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


class LinkedInExtractorTests(unittest.TestCase):
    def test_extracts_public_embed_dom(self):
        client = FakeClient()
        result = LinkedInPostExtractor(client).extract(POST)

        self.assertEqual(result.platform, "linkedin")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(
            result.extraction_method,
            "public_linkedin_embed",
        )
        self.assertEqual(result.canonical_url, FEED)
        self.assertEqual(result.author, "Microsoft")
        self.assertEqual(
            result.text,
            "The most meaningful breakthroughs happen when technology is built with people in mind.",
        )
        self.assertEqual(
            result.metadata["activity_id"],
            "7477715981667086336",
        )
        self.assertEqual(
            result.metadata["activity_urn"],
            "urn:li:activity:7477715981667086336",
        )
        self.assertEqual(result.metadata["embed_url"], EMBED)
        self.assertEqual(
            result.metadata["author"],
            {
                "name": "Microsoft",
                "url": "https://www.linkedin.com/company/microsoft",
                "type": "organization",
                "followers_display": "29,035,744 followers",
            },
        )
        self.assertEqual(result.metadata["published_display"], "2mo")
        self.assertEqual(
            result.metadata["stats"],
            {
                "reactions": 1071,
                "comments": 88,
                "reactions_display": "1,071",
                "comments_display": "88 Comments",
            },
        )
        self.assertEqual(
            result.metadata["attachment"],
            {
                "url": "https://www.linkedin.com/pulse/june-microsoft",
                "title": "June 2026",
                "subtitle": "Microsoft on LinkedIn",
                "thumbnail_url": "https://media.licdn.com/article-cover.jpg",
            },
        )
        self.assertEqual(
            result.metadata["preview_image_url"],
            "https://media.licdn.com/preview.jpg",
        )
        self.assertEqual(
            result.media,
            [
                {
                    "type": "image",
                    "url": "https://media.licdn.com/post-image.jpg",
                    "alt": "Post image alt",
                }
            ],
        )
        self.assertFalse(result.metadata["requires_login"])
        self.assertFalse(result.metadata["uses_oauth"])
        self.assertFalse(result.metadata["uses_access_token"])
        self.assertFalse(result.metadata["uses_browser"])
        self.assertFalse(result.metadata["comments_exported"])
        self.assertEqual(client.calls[0][0], EMBED)

    def test_og_description_is_a_fallback_and_suffix_is_removed(self):
        html = HTML.replace(
            """  <p data-test-id="main-feed-activity-embed-card__commentary">
    The most meaningful breakthroughs happen when technology is built with people in mind.
  </p>
""",
            "",
        ).replace(
            'content="Fallback description | 88 comments on LinkedIn"',
            'content="Fallback description | 88 comments on LinkedIn"',
        )
        result = LinkedInPostExtractor(FakeClient(html)).extract(POST)
        self.assertEqual(result.text, "Fallback description")

    def test_activity_identity_mismatch_is_rejected(self):
        bad = HTML.replace(
            'data-activity-urn="urn:li:activity:7477715981667086336"',
            'data-activity-urn="urn:li:activity:1111111111111111111"',
        )
        with self.assertRaisesRegex(Exception, "identity did not match"):
            LinkedInPostExtractor(FakeClient(bad)).extract(POST)

    def test_supports_post_feed_and_embed_shapes(self):
        extractor = LinkedInPostExtractor(FakeClient())
        for url in [
            POST,
            FEED,
            EMBED,
            "https://linkedin.com/posts/example_activity-7477715981667086336-AbCd",
        ]:
            self.assertTrue(extractor.supports(url), url)

        for url in [
            "https://www.linkedin.com/company/microsoft/",
            "https://www.linkedin.com/in/example/",
            "https://www.linkedin.com/posts/example-no-activity-id",
            "https://example.com/posts/example-activity-7477715981667086336-x",
        ]:
            self.assertFalse(extractor.supports(url), url)

    def test_serialized_output_contains_no_credentials_or_comment_bodies(self):
        result = LinkedInPostExtractor(FakeClient()).extract(POST)
        data = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn("Authorization", data)
        self.assertNotIn("access_token=", data)
        self.assertNotIn("li_at", data)
        self.assertNotIn("comment body", data.lower())


if __name__ == "__main__":
    unittest.main()
