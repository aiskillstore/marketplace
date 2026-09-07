import json
import unittest
from unittest.mock import patch

from sharextract.extractors.base import ExtractorError
from sharextract.extractors.kuaishou import (
    KuaishouAtlasExtractor,
    _KuaishouAtlasDomParser,
)


PHOTO_ID = "3xt75sfvujxqejc"
DIRECT_URL = (
    f"https://c.kuaishou.com/fw/photo/{PHOTO_ID}"
    f"?photoId={PHOTO_ID}&shareMethod=PICTURE&subBiz=PHOTO"
)


SNAPSHOT_HTML = """
<div class="player">
  <div class="player-wrapper">
    <div class="long-image-container disable-touch">
      <img src="//p5.a.yximgs.com/ufile/atlas/example_1.jpg">
      <img src="//p5.a.yximgs.com/ufile/atlas/example_2.jpg">
      <img src="//p5.a.yximgs.com/ufile/atlas/example_2.jpg">
    </div>
  </div>
  <div class="body">
    <div class="tag-text"><div class="title-0">泪痕的作品原声</div></div>
    <div data-log-action="AUTHOR_NICKNAME_BUTTON">
      <div>@</div><div>困困兔</div>
    </div>
    <div data-log-action="PHOTO_DESCRIPTION_TEXT">
      <span class="text txt">那些费尽心思对你好的瞬间</span>
      <span class="text txt">我没想过回报</span>
      <span class="text txt">只想你开心</span>
      <span class="topic txt">#小众情头</span>
      <span class="topic txt">#优质情头</span>
      <span class="topic txt">#情头</span>
    </div>
    <img class="avatar-image"
      src="https://p5-pro.a.yximgs.com/uhead/avatar.jpg">
    <div data-log-action="PHOTO_LIKE_BUTTON"><div>11.4万</div></div>
    <div data-log-action="COMMENT_BUTTON">
      <div>4578</div>
      <div class="comment-action-panel" style="display:none">
        <img src="https://emoji.example/hidden.png">
        <img src="https://emoji.example/hidden-2.png">
      </div>
    </div>
    <div data-log-action="COLLECT_BUTTON"><div>5.3万</div></div>
    <video src="https://video.example/should-not-export.mp4"></video>
    <audio src="https://audio.example/should-not-export.m4a"></audio>
  </div>
</div>
"""


class DummyClient:
    timeout = 20.0


def fake_snapshot(url, **kwargs):
    return {
        "url": DIRECT_URL,
        "title": "快手",
        "text": "rendered",
        "html": SNAPSHOT_HTML,
    }


class KuaishouAtlasExtractorTests(unittest.TestCase):
    def test_extracts_public_rendered_atlas_dom(self):
        with patch(
            "sharextract.extractors.kuaishou.fetch_public_rendered_snapshot",
            side_effect=fake_snapshot,
        ) as browser:
            result = KuaishouAtlasExtractor(DummyClient()).extract(DIRECT_URL)

        self.assertEqual(result.platform, "kuaishou")
        self.assertEqual(result.kind, "image_post")
        self.assertEqual(
            result.extraction_method,
            "public_browser_rendered_atlas_dom",
        )
        self.assertEqual(result.author, "困困兔")
        self.assertEqual(
            result.text,
            "那些费尽心思对你好的瞬间 我没想过回报 "
            "只想你开心 #小众情头 #优质情头 #情头",
        )
        self.assertEqual(
            result.canonical_url,
            f"https://c.kuaishou.com/fw/photo/{PHOTO_ID}",
        )
        self.assertEqual(result.metadata["image_count"], 2)
        self.assertEqual(
            result.metadata["stats"],
            {
                "like_count_display": "11.4万",
                "comment_count_display": "4578",
                "collection_count_display": "5.3万",
            },
        )
        self.assertEqual(
            result.metadata["topics"],
            ["#小众情头", "#优质情头", "#情头"],
        )
        self.assertEqual(result.metadata["music_title"], "泪痕的作品原声")
        self.assertEqual(
            result.metadata["author"]["avatar_url"],
            "https://p5-pro.a.yximgs.com/uhead/avatar.jpg",
        )
        self.assertEqual(
            [m["url"] for m in result.media],
            [
                "https://p5.a.yximgs.com/ufile/atlas/example_1.jpg",
                "https://p5.a.yximgs.com/ufile/atlas/example_2.jpg",
            ],
        )
        self.assertTrue(result.metadata["public_browser_execution"])
        self.assertFalse(result.metadata["imports_device_cookie"])
        self.assertFalse(result.metadata["persists_browser_state"])
        self.assertFalse(result.metadata["private_api_replayed"])
        self.assertFalse(result.metadata["private_signature_generated"])
        self.assertFalse(result.metadata["stream_urls_exported"])

        serialized = json.dumps(result.to_dict(), ensure_ascii=False)
        self.assertNotIn(".mp4", serialized)
        self.assertNotIn(".m4a", serialized)
        self.assertNotIn("__NS_hxfalcon", serialized)
        browser.assert_called_once()
        kwargs = browser.call_args.kwargs
        self.assertEqual(
            kwargs["root_selector"],
            ".swiper-slide-active .player",
        )
        self.assertEqual(kwargs["locale"], "zh-CN")

    def test_parser_scopes_topics_actions_and_atlas_images(self):
        parser = _KuaishouAtlasDomParser()
        parser.feed(SNAPSHOT_HTML)
        parser.close()
        self.assertEqual(parser.values["author"].replace(" ", ""), "@困困兔")
        self.assertEqual(len(parser.atlas_images), 3)
        self.assertEqual(
            parser.topics,
            ["#小众情头", "#优质情头", "#情头"],
        )

    def test_missing_atlas_images_is_rejected(self):
        empty = {
            "url": DIRECT_URL,
            "title": "快手",
            "text": "@someone video",
            "html": '<div data-log-action="AUTHOR_NICKNAME_BUTTON">@someone</div>',
        }
        with patch(
            "sharextract.extractors.kuaishou.fetch_public_rendered_snapshot",
            return_value=empty,
        ):
            with self.assertRaisesRegex(ExtractorError, "no atlas images"):
                KuaishouAtlasExtractor(DummyClient()).extract(DIRECT_URL)

    def test_supports_picture_share_and_short_links_without_overmatching(self):
        extractor = KuaishouAtlasExtractor(DummyClient())
        for url in [
            DIRECT_URL,
            "https://v.kuaishou.com/example",
            "https://v.kuaishou.cn/example",
            "https://www.kuaishou.com/f/example",
        ]:
            self.assertTrue(extractor.supports(url), url)
        self.assertFalse(
            extractor.supports(
                f"https://c.kuaishou.com/fw/photo/{PHOTO_ID}"
                f"?photoId={PHOTO_ID}&shareMethod=TOKEN&subBiz=BROWSE_VIDEO"
            )
        )
        self.assertFalse(
            extractor.supports("https://www.kuaishou.com/profile/example")
        )


if __name__ == "__main__":
    unittest.main()
