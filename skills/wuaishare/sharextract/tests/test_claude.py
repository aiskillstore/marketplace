import unittest

from sharextract.extractors.claude import ClaudeShareExtractor
from sharextract.http import HttpResponse


SHARE_ID = "b76ffb8c-8a9d-43fb-b02d-0990e2e2fc7c"


class FakeClient:
    def __init__(self, payload=None):
        self.payload = payload or {
            "uuid": SHARE_ID,
            "conversation_uuid": "7a9b58a6-0903-4964-8207-cbe44de743ff",
            "created_at": "2026-02-04T07:49:09.020776Z",
            "updated_at": "2026-02-04T07:49:09.020776Z",
            "snapshot_name": "Synthetic Claude Snapshot",
            "created_by": "Alice",
            "creator": {"uuid": "creator-1", "full_name": "Alice"},
            "project_uuid": None,
            "is_public": True,
            "up_to_date": False,
            "working_documents": [],
            "chat_messages": [
                {
                    "uuid": "m1",
                    "sender": "human",
                    "text": "Hello Claude",
                    "created_at": "2026-02-04T07:43:37Z",
                    "updated_at": "2026-02-04T07:43:37Z",
                    "index": 0,
                    "attachments": [],
                    "files": [],
                },
                {
                    "uuid": "m2",
                    "sender": "assistant",
                    "text": "Hello human",
                    "created_at": "2026-02-04T07:45:54Z",
                    "updated_at": "2026-02-04T07:45:54Z",
                    "index": 1,
                    "stop_reason": "stop_sequence",
                    "attachments": [
                        {
                            "file_name": "example.png",
                            "url": "https://cdn.example/example.png",
                        }
                    ],
                    "files": [],
                },
            ],
        }
        self.urls = []

    def get_json(self, url, headers=None):
        self.urls.append(url)
        return (
            HttpResponse(
                url=url,
                content_type="application/json",
                body=b"{}",
            ),
            self.payload,
        )


class ClaudeExtractorTests(unittest.TestCase):
    def test_extracts_public_snapshot_json(self):
        client = FakeClient()
        result = ClaudeShareExtractor(client).extract(
            f"https://claude.ai/share/{SHARE_ID}"
        )
        self.assertEqual(result.platform, "claude")
        self.assertEqual(result.kind, "conversation")
        self.assertEqual(
            result.extraction_method,
            "first_party_undocumented_public_json",
        )
        self.assertEqual(result.title, "Synthetic Claude Snapshot")
        self.assertEqual(result.author, "Alice")
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])
        self.assertEqual(result.messages[0].text, "Hello Claude")
        self.assertEqual(result.messages[1].text, "Hello human")
        self.assertEqual(result.metadata["share_id"], SHARE_ID)
        self.assertEqual(result.media[0]["url"], "https://cdn.example/example.png")
        self.assertTrue(
            client.urls[0].endswith(f"/api/chat_snapshots/{SHARE_ID}")
        )

    def test_rejects_nonpublic_snapshot(self):
        payload = FakeClient().payload
        payload = dict(payload, is_public=False)
        with self.assertRaises(Exception):
            ClaudeShareExtractor(FakeClient(payload)).extract(
                f"https://claude.ai/share/{SHARE_ID}"
            )

    def test_supports_only_public_share_shape(self):
        extractor = ClaudeShareExtractor(FakeClient())
        self.assertTrue(
            extractor.supports(f"https://claude.ai/share/{SHARE_ID}")
        )
        self.assertFalse(extractor.supports("https://claude.ai/new"))
        self.assertFalse(extractor.supports("https://example.com/share/x"))


if __name__ == "__main__":
    unittest.main()
