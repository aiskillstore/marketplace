from __future__ import annotations

import re
import urllib.parse
from html.parser import HTMLParser
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


class _FirstParagraphParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts: list[str] = []
        self.done = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if self.done:
            return
        if tag.lower() == "p":
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self.done:
            return
        if tag.lower() == "p" and self.depth:
            self.depth -= 1
            if self.depth == 0:
                self.done = True

    def handle_data(self, data: str) -> None:
        if self.depth and not self.done:
            self.parts.append(data)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()


class _OEmbedExtractor(Extractor):
    platform = ""
    kind = ""
    endpoint = ""
    priority = 30

    def endpoint_for(self, url: str) -> str:
        raise NotImplementedError

    def extract(self, url: str) -> ExtractedContent:
        endpoint = self.endpoint_for(url)
        _, payload = self.client.get_json(
            endpoint,
            headers={"Accept": "application/json"},
        )
        if not isinstance(payload, dict):
            raise ExtractorError(f"{self.platform} oEmbed did not return an object.")

        canonical = str(payload.get("url") or "").strip() or url
        author = str(payload.get("author_name") or "").strip()
        title = str(payload.get("title") or "").strip()
        html = str(payload.get("html") or "")

        text = ""
        if self.platform == "x":
            text = _first_paragraph(html)
            if not title:
                title = _title_from_text(text)
        else:
            description = payload.get("description")
            if isinstance(description, str) and description.strip():
                text = description.strip()
            elif title:
                text = title

        if not title and not text and not html:
            raise ExtractorError(f"{self.platform} oEmbed returned no usable metadata.")

        media: list[dict[str, Any]] = []
        if self.kind == "video":
            item: dict[str, Any] = {
                "type": "video",
                "url": canonical,
            }
            thumbnail = payload.get("thumbnail_url")
            if isinstance(thumbnail, str) and thumbnail:
                item["thumbnail_url"] = thumbnail
            for key, target in (
                ("width", "width"),
                ("height", "height"),
                ("duration", "duration_seconds"),
            ):
                value = payload.get(key)
                if isinstance(value, (int, float)):
                    item[target] = value
            media.append(item)

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform=self.platform,
            kind=self.kind,
            extraction_method="documented_oembed",
            confidence=0.99,
            title=title,
            author=author,
            text=text,
            markdown=text,
            html=html,
            media=media,
            metadata={
                "oembed": {
                    key: value
                    for key, value in payload.items()
                    if key != "html"
                },
                "endpoint_documentation": "documented",
            },
        )


class XPostOEmbedExtractor(_OEmbedExtractor):
    name = "x-oembed"
    platform = "x"
    kind = "social_post"
    priority = 31

    def supports(self, url: str) -> bool:
        host = self.hostname(url)
        if host not in {
            "x.com",
            "www.x.com",
            "twitter.com",
            "www.twitter.com",
            "mobile.twitter.com",
        }:
            return False
        path = urllib.parse.urlsplit(url).path
        return bool(re.fullmatch(r"/[^/]+/status/\d+/?", path))

    def endpoint_for(self, url: str) -> str:
        return "https://publish.x.com/oembed?" + urllib.parse.urlencode(
            {
                "url": url,
                "omit_script": "1",
            }
        )


class YouTubeOEmbedExtractor(_OEmbedExtractor):
    name = "youtube-oembed"
    platform = "youtube"
    kind = "video"
    priority = 32

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        if host in {"youtu.be", "www.youtu.be"}:
            return bool([part for part in parsed.path.split("/") if part])
        if host not in {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "music.youtube.com",
        }:
            return False
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.path == "/watch":
            return bool(urllib.parse.parse_qs(parsed.query).get("v"))
        return len(parts) >= 2 and parts[0] in {"shorts", "live", "embed"}

    def endpoint_for(self, url: str) -> str:
        return "https://www.youtube.com/oembed?" + urllib.parse.urlencode(
            {
                "url": url,
                "format": "json",
            }
        )


class TikTokOEmbedExtractor(_OEmbedExtractor):
    name = "tiktok-oembed"
    platform = "tiktok"
    kind = "video"
    priority = 34

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        if host not in {
            "tiktok.com",
            "www.tiktok.com",
            "m.tiktok.com",
        }:
            return False
        parts = [part for part in parsed.path.split("/") if part]
        return (
            len(parts) >= 3
            and parts[0].startswith("@")
            and parts[1] == "video"
            and parts[2].isdigit()
        )

    def endpoint_for(self, url: str) -> str:
        return "https://www.tiktok.com/oembed?" + urllib.parse.urlencode(
            {"url": url}
        )


class VimeoOEmbedExtractor(_OEmbedExtractor):
    name = "vimeo-oembed"
    platform = "vimeo"
    kind = "video"
    priority = 33

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        if host not in {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}:
            return False
        return any(part.isdigit() for part in parsed.path.split("/") if part)

    def endpoint_for(self, url: str) -> str:
        return "https://vimeo.com/api/oembed.json?" + urllib.parse.urlencode(
            {"url": url}
        )


def _first_paragraph(value: str) -> str:
    if not value:
        return ""
    parser = _FirstParagraphParser()
    try:
        parser.feed(value)
        parser.close()
    except Exception:
        return ""
    return parser.text


def _title_from_text(value: str) -> str:
    first = next((line.strip() for line in value.splitlines() if line.strip()), "")
    if len(first) <= 100:
        return first
    return first[:97].rstrip() + "..."
