import json
import unittest

from sharextract.extractors.telegram import TelegramPostExtractor
from sharextract.http import HttpResponse


POST = "https://t.me/durov/43"

HTML = """<!doctype html>
<html><body>
<div class="tgme_widget_message">
  <div class="tgme_widget_message_author accent_color">
    <a class="tgme_widget_message_owner_name" href="https://t.me/durov">
      <span>Pavel Durov</span>
    </a>
    <a class="tgme_widget_message_owner_labels" href="https://t.me/durov">
      <i class="verified-icon">✔</i>
    </a>
  </div>
  <a class="tgme_widget_message_photo_wrap"
     href="https://t.me/durov/43"
     style="background-image:url('https://cdn1.telesco.pe/file/example.jpg')">
    <div class="tgme_widget_message_photo"></div>
  </a>
  <div class="tgme_widget_message_text js-message_text">
    This October we are working on new features for
    <a href="https://t.me/telegram">@telegram</a><br>
    from a castle in Umbria, Italy.
  </div>
  <a class="tgme_widget_message_link_preview" href="https://telegram.org/">
    <div class="link_preview_site_name">Telegram</div>
    <div class="link_preview_title">Telegram News</div>
    <div class="link_preview_description">Public preview</div>
  </a>
  <div class="tgme_widget_message_reactions">
    <span class="tgme_reaction tgme_reaction_paid">48</span>
    <span class="tgme_reaction"><i><b>👍</b></i>2.03K</span>
    <span class="tgme_reaction"><i><b>❤</b></i>837</span>
  </div>
  <div class="tgme_widget_message_info">
    <span class="tgme_widget_message_views">870K</span>
    <a class="tgme_widget_message_date" href="https://t.me/durov/43">
      <time datetime="2016-10-09T18:53:49+00:00">Oct 9, 2016</time>
    </a>
  </div>
</div>
<script>
TWidgetAuth.init({"api_url":"https://t.me/api/method?api_hash=secret"});
</script>
</body></html>
"""


class FakeClient:
    timeout = 20.0

    def __init__(self):
        self.calls = []

    def get_text(self, url, headers=None):
        self.calls.append((url, headers))
        return HttpResponse(
            url=url,
            content_type="text/html; charset=utf-8",
            body=HTML.encode(),
        )


class TelegramExtractorTests(unittest.TestCase):
    def test_extracts_official_post_widget(self):
        client = FakeClient()
        result = TelegramPostExtractor(client).extract(POST)

        self.assertEqual(result.platform, "telegram")
        self.assertEqual(result.kind, "social_post")
        self.assertEqual(
            result.extraction_method,
            "documented_telegram_post_widget",
        )
        self.assertEqual(result.author, "Pavel Durov")
        self.assertEqual(
            result.canonical_url,
            POST,
        )
        self.assertIn("This October", result.text)
        self.assertIn("from a castle", result.text)
        self.assertEqual(
            result.metadata["published_at"],
            "2016-10-09T18:53:49+00:00",
        )
        self.assertEqual(result.metadata["views_display"], "870K")
        self.assertTrue(result.metadata["verified"])
        self.assertEqual(
            result.metadata["author_url"],
            "https://t.me/durov",
        )
        self.assertEqual(
            result.metadata["link_preview"],
            {
                "url": "https://telegram.org/",
                "site_name": "Telegram",
                "title": "Telegram News",
                "description": "Public preview",
            },
        )
        self.assertEqual(
            result.metadata["reactions"],
            [
                {"count_display": "48", "paid": True},
                {"count_display": "2.03K", "paid": False, "label": "👍"},
                {"count_display": "837", "paid": False, "label": "❤"},
            ],
        )
        self.assertEqual(
            result.media,
            [
                {
                    "type": "image",
                    "url": "https://cdn1.telesco.pe/file/example.jpg",
                }
            ],
        )
        self.assertFalse(result.metadata["requires_login"])
        self.assertFalse(result.metadata["uses_bot_token"])
        self.assertFalse(result.metadata["uses_browser"])
        self.assertFalse(result.metadata["stream_urls_exported"])
        self.assertEqual(
            client.calls[0][0],
            POST + "?embed=1&mode=tme",
        )

        serialized = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn("api_hash=secret", serialized)
        self.assertNotIn("/api/method", serialized)

    def test_text_only_widget_is_supported(self):
        text_only = HTML.replace(
            """  <a class="tgme_widget_message_photo_wrap"
     href="https://t.me/durov/43"
     style="background-image:url('https://cdn1.telesco.pe/file/example.jpg')">
    <div class="tgme_widget_message_photo"></div>
  </a>
""",
            "",
        )
        client = FakeClient()
        client.get_text = lambda url, headers=None: HttpResponse(
            url=url,
            content_type="text/html; charset=utf-8",
            body=text_only.encode(),
        )
        result = TelegramPostExtractor(client).extract(POST)
        self.assertEqual(result.media, [])
        self.assertTrue(result.text)

    def test_canonicalizes_supported_hosts(self):
        extractor = TelegramPostExtractor(FakeClient())
        for url in [
            "https://t.me/telegram/83",
            "https://www.t.me/telegram/83?single",
            "https://telegram.me/telegram/83",
            "https://www.telegram.me/telegram/83",
        ]:
            self.assertTrue(extractor.supports(url), url)
        result = extractor.extract("https://telegram.me/durov/43")
        self.assertEqual(result.canonical_url, POST)

    def test_rejects_non_post_urls(self):
        extractor = TelegramPostExtractor(FakeClient())
        for url in [
            "https://t.me/telegram",
            "https://t.me/+invitehash",
            "https://t.me/s/telegram",
            "https://example.com/telegram/83",
        ]:
            self.assertFalse(extractor.supports(url), url)


if __name__ == "__main__":
    unittest.main()
