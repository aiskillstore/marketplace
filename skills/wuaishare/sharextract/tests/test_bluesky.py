import unittest

from sharextract.extractors.bluesky import BlueskyPostExtractor
from sharextract.http import HttpResponse


class FakeClient:
    def __init__(self):
        self.urls = []

    def get_json(self, url, headers=None):
        self.urls.append(url)
        if "resolveHandle" in url:
            return HttpResponse(url=url, content_type="application/json", body=b"{}"), {
                "did": "did:plc:example"
            }

        payload = {
            "thread": {
                "$type": "app.bsky.feed.defs#threadViewPost",
                "post": {
                    "uri": "at://did:plc:example/app.bsky.feed.post/abc123",
                    "cid": "bafytest",
                    "author": {
                        "did": "did:plc:example",
                        "handle": "alice.example",
                        "displayName": "Alice",
                    },
                    "record": {
                        "$type": "app.bsky.feed.post",
                        "text": "Hello from the open social web.",
                        "createdAt": "2026-09-06T01:02:03.000Z",
                        "langs": ["en"],
                        "reply": {
                            "root": {"uri": "at://did:plc:root/app.bsky.feed.post/root"},
                            "parent": {"uri": "at://did:plc:parent/app.bsky.feed.post/parent"},
                        },
                    },
                    "indexedAt": "2026-09-06T01:02:04.000Z",
                    "likeCount": 12,
                    "replyCount": 2,
                    "repostCount": 3,
                    "quoteCount": 1,
                    "embed": {
                        "$type": "app.bsky.embed.images#view",
                        "images": [
                            {
                                "thumb": "https://cdn.example/thumb.jpg",
                                "fullsize": "https://cdn.example/full.jpg",
                                "alt": "Example image",
                                "aspectRatio": {"width": 1200, "height": 630},
                            }
                        ],
                    },
                }
            }
        }
        return HttpResponse(url=url, content_type="application/json", body=b"{}"), payload


class BlueskyExtractorTests(unittest.TestCase):
    def test_extracts_public_post_via_atproto(self):
        client = FakeClient()
        result = BlueskyPostExtractor(client).extract(
            "https://bsky.app/profile/alice.example/post/abc123"
        )
        self.assertEqual(result.platform, "bluesky")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(result.extraction_method, "documented_public_atproto_api")
        self.assertEqual(result.author, "Alice")
        self.assertEqual(result.text, "Hello from the open social web.")
        self.assertEqual(result.metadata["did"], "did:plc:example")
        self.assertEqual(result.metadata["reply_parent_uri"], "at://did:plc:parent/app.bsky.feed.post/parent")
        self.assertEqual(result.media[0]["url"], "https://cdn.example/full.jpg")
        self.assertTrue(any("resolveHandle" in url for url in client.urls))
        self.assertTrue(any("getPostThread" in url for url in client.urls))

    def test_direct_did_skips_handle_resolution(self):
        client = FakeClient()
        result = BlueskyPostExtractor(client).extract(
            "https://bsky.app/profile/did:plc:example/post/abc123"
        )
        self.assertEqual(result.metadata["did"], "did:plc:example")
        self.assertFalse(any("resolveHandle" in url for url in client.urls))

    def test_supports_only_post_urls(self):
        extractor = BlueskyPostExtractor(FakeClient())
        self.assertTrue(
            extractor.supports("https://bsky.app/profile/alice.example/post/abc123")
        )
        self.assertFalse(extractor.supports("https://bsky.app/profile/alice.example"))
        self.assertFalse(extractor.supports("https://example.com/profile/alice/post/abc"))


if __name__ == "__main__":
    unittest.main()
