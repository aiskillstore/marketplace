import unittest

from sharextract.http import SafeHttpClient
from sharextract.router import _extractors_for_strategy


class RouterTests(unittest.TestCase):
    def test_auto_orders_native_before_media_and_web(self):
        extractors = _extractors_for_strategy("auto", SafeHttpClient())
        names = [x.name for x in extractors]
        self.assertEqual(names[-2:], ["yt-dlp", "generic-web"])
        native_priorities = [x.priority for x in extractors[:-2]]
        self.assertEqual(native_priorities, sorted(native_priorities))
        for native_name in (
            "doubao-share",
            "x-oembed",
            "youtube-oembed",
            "vimeo-oembed",
            "bilibili-video",
        ):
            self.assertLess(names.index(native_name), names.index("yt-dlp"))

    def test_web_strategy_is_generic_only(self):
        names = [x.name for x in _extractors_for_strategy("web", SafeHttpClient())]
        self.assertEqual(names, ["generic-web"])


if __name__ == "__main__":
    unittest.main()
