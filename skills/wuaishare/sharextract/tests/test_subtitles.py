import unittest

from sharextract.extractors.base import ExtractorError
from sharextract.extractors.generic import GenericWebExtractor
from sharextract.http import HttpResponse


class FakeClient:
    def __init__(self, body: str, content_type: str, final_url: str):
        self.body = body
        self.content_type = content_type
        self.final_url = final_url

    def get_text(self, url, headers=None):
        return HttpResponse(
            url=self.final_url,
            content_type=self.content_type,
            body=self.body.encode("utf-8"),
        )

    def get_json(self, url, headers=None):
        raise AssertionError("subtitle tests must not make a second JSON request")


WEBVTT = """WEBVTT

NOTE internal note
not transcript text

STYLE
::cue { color: lime; }

intro
00:00:01.000 --> 00:00:04.340 align:start
<v Alice>Tools for <b>evaluating</b> web accessibility.

00:04.640 --> 00:10.880
There are software programs
and online services.
"""

SRT = """1
00:00:01,000 --> 00:00:03,250
Hello <i>world</i>.

2
00:00:04,500 --> 00:00:06,000
Second line
continues here.
"""

TTML = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xml:lang="en">
  <head>
    <metadata><ttm:title>Example TTML</ttm:title></metadata>
  </head>
  <body>
    <div>
      <p xml:id="p1" begin="1.5s" end="3.25s">Hello TTML.</p>
      <p xml:id="p2" begin="4s" dur="2s">Second cue.</p>
    </div>
  </body>
</tt>
"""

HTML_TRACKS = """<!doctype html>
<html>
<head><title>Video page</title></head>
<body>
<main><p>A public page with caption tracks.</p></main>
<video controls>
  <track kind="captions" src="/captions/en.vtt" srclang="en" label="English" default>
  <track kind="subtitles" src="fr.vtt" srclang="fr" label="Français">
  <track kind="chapters" src="chapters.vtt" srclang="en">
</video>
</body>
</html>
"""


class TimedTextTests(unittest.TestCase):
    def test_webvtt_normalizes_cues_speaker_and_settings(self):
        result = GenericWebExtractor(
            FakeClient(
                WEBVTT,
                "text/vtt; charset=utf-8",
                "https://example.com/media/tools.en.vtt",
            )
        ).extract("https://example.com/media/tools.en.vtt")

        self.assertEqual(result.platform, "timed-text")
        self.assertEqual(result.kind, "transcript")
        self.assertEqual(result.extraction_method, "standard_webvtt")
        self.assertEqual(result.title, "tools")
        transcript = result.metadata["transcript"]
        self.assertEqual(transcript["format"], "webvtt")
        self.assertEqual(transcript["language"], "en")
        self.assertEqual(transcript["language_source"], "url_filename")
        self.assertEqual(transcript["cue_count"], 2)
        self.assertEqual(transcript["duration_seconds"], 10.88)
        self.assertEqual(transcript["cues"][0]["id"], "intro")
        self.assertEqual(transcript["cues"][0]["speaker"], "Alice")
        self.assertEqual(
            transcript["cues"][0]["settings"],
            "align:start",
        )
        self.assertEqual(
            transcript["cues"][0]["text"],
            "Tools for evaluating web accessibility.",
        )
        self.assertNotIn("internal note", result.text)
        self.assertNotIn("color: lime", result.text)

    def test_srt_normalizes_comma_timestamps_and_markup(self):
        result = GenericWebExtractor(
            FakeClient(
                SRT,
                "application/x-subrip",
                "https://example.com/subtitles/demo.srt",
            )
        ).extract("https://example.com/subtitles/demo.srt")

        self.assertEqual(result.extraction_method, "standard_srt")
        transcript = result.metadata["transcript"]
        self.assertEqual(transcript["cue_count"], 2)
        self.assertEqual(transcript["cues"][0]["start"], "00:00:01.000")
        self.assertEqual(transcript["cues"][0]["end"], "00:00:03.250")
        self.assertEqual(transcript["cues"][0]["text"], "Hello world.")
        self.assertEqual(
            transcript["cues"][1]["text"],
            "Second line continues here.",
        )

    def test_ttml_normalizes_clock_and_duration_timing(self):
        result = GenericWebExtractor(
            FakeClient(
                TTML,
                "application/ttml+xml",
                "https://example.com/captions/example.ttml",
            )
        ).extract("https://example.com/captions/example.ttml")

        self.assertEqual(result.extraction_method, "standard_ttml")
        self.assertEqual(result.title, "Example TTML")
        transcript = result.metadata["transcript"]
        self.assertEqual(transcript["language"], "en")
        self.assertEqual(transcript["cue_count"], 2)
        self.assertEqual(transcript["cues"][0]["start_seconds"], 1.5)
        self.assertEqual(transcript["cues"][0]["end_seconds"], 3.25)
        self.assertEqual(transcript["cues"][1]["end_seconds"], 6.0)
        self.assertEqual(transcript["duration_seconds"], 6.0)

    def test_html_discovers_caption_subtitle_tracks_without_fetching_them(self):
        result = GenericWebExtractor(
            FakeClient(
                HTML_TRACKS,
                "text/html; charset=utf-8",
                "https://example.com/video/page.html",
            )
        ).extract("https://example.com/video/page.html")

        self.assertEqual(
            result.metadata["subtitle_tracks"],
            [
                {
                    "kind": "captions",
                    "url": "https://example.com/captions/en.vtt",
                    "language": "en",
                    "label": "English",
                    "default": True,
                },
                {
                    "kind": "subtitles",
                    "url": "https://example.com/video/fr.vtt",
                    "language": "fr",
                    "label": "Français",
                    "default": False,
                },
            ],
        )

    def test_ttml_dtd_or_entity_is_rejected(self):
        malicious = """<?xml version="1.0"?>
<!DOCTYPE tt [<!ENTITY local SYSTEM "file:///etc/passwd">]>
<tt xmlns="http://www.w3.org/ns/ttml"><body><p begin="0s" end="1s">&local;</p></body></tt>
"""
        extractor = GenericWebExtractor(
            FakeClient(
                malicious,
                "application/ttml+xml",
                "https://example.com/captions/bad.ttml",
            )
        )
        with self.assertRaises(ExtractorError):
            extractor.extract("https://example.com/captions/bad.ttml")


if __name__ == "__main__":
    unittest.main()
