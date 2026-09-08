import unittest

from sharextract.extractors.mastodon import MastodonStatusExtractor
from sharextract.http import HttpResponse


PUBLIC_STATUS = {
    "id": "1234567890",
    "created_at": "2026-09-06T01:02:03.000Z",
    "edited_at": None,
    "in_reply_to_id": None,
    "in_reply_to_account_id": None,
    "sensitive": False,
    "spoiler_text": "Release note",
    "visibility": "public",
    "language": "en",
    "uri": "https://social.example/users/alice/statuses/1234567890",
    "url": "https://social.example/@alice/1234567890",
    "replies_count": 2,
    "reblogs_count": 3,
    "favourites_count": 4,
    "quotes_count": 1,
    "content": '<p>Hello <a href="https://example.com">open web</a>!</p><p>Second line.</p>',
    "text": None,
    "account": {
        "id": "42",
        "username": "alice",
        "acct": "alice",
        "display_name": "Alice Example",
    },
    "media_attachments": [
        {
            "id": "m1",
            "type": "image",
            "url": "https://cdn.example/full.jpg",
            "preview_url": "https://cdn.example/preview.jpg",
            "description": "A sample image",
            "blurhash": "abc",
            "meta": {"original": {"width": 1000, "height": 800}},
        }
    ],
    "mentions": [],
    "tags": [{"name": "fediverse", "url": "https://social.example/tags/fediverse"}],
    "card": None,
    "poll": None,
}


class FakeClient:
    def __init__(self):
        self.urls = []

    def get_json(self, url, headers=None):
        self.urls.append(url)
        return HttpResponse(url=url, content_type="application/json", body=b"{}"), PUBLIC_STATUS


class MastodonExtractorTests(unittest.TestCase):
    def test_extracts_public_status(self):
        client = FakeClient()
        result = MastodonStatusExtractor(client).extract(
            "https://social.example/@alice/1234567890"
        )
        self.assertEqual(result.platform, "mastodon")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(result.extraction_method, "documented_public_mastodon_api")
        self.assertEqual(result.author, "Alice Example")
        self.assertEqual(result.text, "Hello open web!\n\nSecond line.")
        self.assertEqual(result.metadata["tags"], ["fediverse"])
        self.assertEqual(result.media[0]["url"], "https://cdn.example/full.jpg")
        self.assertTrue(client.urls[0].endswith("/api/v1/statuses/1234567890"))

    def test_supports_common_status_urls(self):
        extractor = MastodonStatusExtractor(FakeClient())
        self.assertTrue(extractor.supports("https://social.example/@alice/123"))
        self.assertTrue(
            extractor.supports("https://social.example/users/alice/statuses/123")
        )
        self.assertFalse(extractor.supports("https://social.example/@alice"))


if __name__ == "__main__":
    unittest.main()
