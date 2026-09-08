import json
import unittest

from sharextract.extractors.gemini import GeminiShareExtractor
from sharextract.http import HttpResponse


def rpc_response(share_id="abc123xyz") -> str:
    turn = [
        ["conv_1", "resp_1"],
        None,
        [["\u200bHello Gemini"], 1, None, 1, "model_1", 0],
        [
            [["resp_candidate", ["Hello human"], None]],
            None,
            None,
            "resp_candidate",
        ],
        [1760000000, 500000000],
    ]
    root = [
        None,
        [turn],
        [True, "Synthetic Gemini Chat", None, None, None, None, None, [1, "model_1", "Thinking"], True],
        share_id,
        [1760000100, 0],
        None,
        "=s1200",
    ]
    nested = json.dumps([root, None, False], separators=(",", ":"))
    outer = json.dumps([["wrb.fr", "ujx1Bf", nested, None, None, None, "generic"]], separators=(",", ":"))
    return ")]}'\n\n" + str(len(outer)) + "\n" + outer + "\n"


class FakeClient:
    def __init__(self):
        self.posts = []
        self.resolved = []

    def post_form(self, url, fields, headers=None):
        self.posts.append((url, fields, headers))
        return HttpResponse(
            url=url,
            content_type="application/json; charset=utf-8",
            body=rpc_response().encode(),
        )

    def resolve(self, url, headers=None):
        self.resolved.append(url)
        return "https://gemini.google.com/share/abc123xyz?skid=synthetic"


class GeminiExtractorTests(unittest.TestCase):
    def test_extracts_public_share_rpc(self):
        client = FakeClient()
        result = GeminiShareExtractor(client).extract(
            "https://gemini.google.com/share/abc123xyz"
        )
        self.assertEqual(result.platform, "gemini")
        self.assertEqual(result.kind, "conversation")
        self.assertEqual(result.extraction_method, "first_party_undocumented_public_rpc")
        self.assertEqual(result.title, "Synthetic Gemini Chat")
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])
        self.assertEqual(result.messages[0].text, "Hello Gemini")
        self.assertEqual(result.messages[1].text, "Hello human")
        self.assertEqual(result.metadata["share_id"], "abc123xyz")
        self.assertEqual(result.metadata["model_label"], "Thinking")
        self.assertIn("rpcids=ujx1Bf", client.posts[0][0])
        self.assertIn("abc123xyz", client.posts[0][1]["f.req"])

    def test_extracts_legacy_gco_short_link_without_browser(self):
        client = FakeClient()
        result = GeminiShareExtractor(client).extract(
            "https://g.co/gemini/share/abc123xyz"
        )
        self.assertEqual(result.metadata["share_id"], "abc123xyz")
        self.assertEqual(
            result.extraction_method,
            "first_party_undocumented_public_rpc",
        )
        self.assertEqual(client.resolved, [])

    def test_supports_legacy_and_new_short_links(self):
        extractor = GeminiShareExtractor(FakeClient())
        self.assertTrue(extractor.supports("https://g.co/gemini/share/abc123xyz"))
        self.assertTrue(extractor.supports("https://gemini.google.com/share/abc123xyz"))
        self.assertTrue(extractor.supports("https://share.gemini.google/OoM7BNqBmJuO"))
        self.assertFalse(extractor.supports("https://gemini.google.com/app"))

    def test_resolves_new_short_link_to_canonical_share_id(self):
        client = FakeClient()
        result = GeminiShareExtractor(client).extract(
            "https://share.gemini.google/OoM7BNqBmJuO"
        )
        self.assertEqual(result.canonical_url, "https://gemini.google.com/share/abc123xyz")
        self.assertEqual(client.resolved, ["https://share.gemini.google/OoM7BNqBmJuO"])


if __name__ == "__main__":
    unittest.main()
