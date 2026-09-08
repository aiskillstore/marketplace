from __future__ import annotations

import html
import json
import re
import urllib.parse
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
    "AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"
)
_MOBILE_HEADERS = {
    "User-Agent": _MOBILE_UA,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
_ID_RE = re.compile(r"^\d{10,32}$")
_SSR_MARKER = "window._SSR_DATA = "
_DURATION_RE = re.compile(
    r"^PT(?:(?P<hours>\d+(?:\.\d+)?)H)?"
    r"(?:(?P<minutes>\d+(?:\.\d+)?)M)?"
    r"(?:(?P<seconds>\d+(?:\.\d+)?)S)?$"
)


class _JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capture = False
        self._parts: list[str] = []
        self.documents: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "script":
            return
        attr = {
            str(key).lower(): str(value)
            for key, value in attrs
            if key and value is not None
        }
        self._capture = attr.get("type", "").lower() == "application/ld+json"
        if self._capture:
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "script" or not self._capture:
            return
        self._capture = False
        raw = "".join(self._parts).strip()
        self._parts = []
        if not raw:
            return
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            return
        if isinstance(value, dict):
            self.documents.append(value)
        elif isinstance(value, list):
            self.documents.extend(
                item for item in value if isinstance(item, dict)
            )


class DouyinVideoExtractor(Extractor):
    """Extract public Douyin video metadata from the anonymous Jingxuan SSR reader."""

    name = "douyin-video"
    priority = 38

    def supports(self, url: str) -> bool:
        host = self.hostname(url)
        if host == "v.douyin.com":
            return bool([part for part in urllib.parse.urlsplit(url).path.split("/") if part])
        return self._video_id_from_url(url) is not None

    def extract(self, url: str) -> ExtractedContent:
        video_id = self._video_id_from_url(url)
        resolved_url = url
        if video_id is None and self.hostname(url) == "v.douyin.com":
            resolved_url = self.client.resolve(url, headers=_MOBILE_HEADERS)
            video_id = self._video_id_from_url(resolved_url)
        if video_id is None:
            raise ExtractorError("Unsupported Douyin video URL.")

        reader_url = f"https://jingxuan.douyin.com/m/video/{video_id}"
        response = self.client.get_text(reader_url, headers=_MOBILE_HEADERS)
        result = _extract_ssr_result(response.text, video_id)
        jsonld = _extract_video_jsonld(response.text)

        if result is not None:
            return _from_ssr(
                source_url=url,
                resolved_url=resolved_url,
                reader_url=reader_url,
                video_id=video_id,
                result=result,
                jsonld=jsonld,
            )
        if jsonld is not None:
            return _from_jsonld(
                source_url=url,
                resolved_url=resolved_url,
                reader_url=reader_url,
                video_id=video_id,
                value=jsonld,
            )
        raise ExtractorError(
            "Douyin public Jingxuan reader returned no readable video metadata."
        )

    def _video_id_from_url(self, url: str) -> str | None:
        parsed = urllib.parse.urlsplit(url)
        host = self.hostname(url)
        parts = [
            urllib.parse.unquote(part)
            for part in parsed.path.split("/")
            if part
        ]
        candidate: str | None = None

        if host in {"douyin.com", "www.douyin.com"}:
            if len(parts) >= 2 and parts[0] == "video":
                candidate = parts[1]
            elif len(parts) >= 3 and parts[:2] == ["share", "video"]:
                candidate = parts[2]
        elif host in {"m.douyin.com", "www.iesdouyin.com", "iesdouyin.com"}:
            if len(parts) >= 3 and parts[:2] == ["share", "video"]:
                candidate = parts[2]
        elif host == "jingxuan.douyin.com":
            if len(parts) >= 3 and parts[:2] == ["m", "video"]:
                candidate = parts[2]

        if candidate and _ID_RE.fullmatch(candidate):
            return candidate
        return None


def _extract_ssr_result(
    page_html: str,
    expected_video_id: str,
) -> dict[str, Any] | None:
    pos = page_html.find(_SSR_MARKER)
    if pos < 0:
        return None
    raw = page_html[pos + len(_SSR_MARKER) :]
    try:
        payload, _ = json.JSONDecoder().raw_decode(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None

    data = payload.get("data")
    data = data if isinstance(data, dict) else {}
    state = data.get("storeState")
    state = state if isinstance(state, dict) else {}
    detail = state.get("detail")
    detail = detail if isinstance(detail, dict) else {}
    video_data = detail.get("videoData")
    video_data = video_data if isinstance(video_data, dict) else {}
    result = video_data.get("result")
    if not isinstance(result, dict):
        return None

    gid = str(result.get("gid") or "").strip()
    if gid and gid != expected_video_id:
        return None
    if not str(result.get("title") or result.get("abstract") or "").strip():
        return None
    return result


def _extract_video_jsonld(page_html: str) -> dict[str, Any] | None:
    parser = _JsonLdParser()
    try:
        parser.feed(page_html)
        parser.close()
    except Exception:
        return None
    for doc in parser.documents:
        kind = doc.get("@type")
        if kind == "VideoObject":
            return doc
        if isinstance(kind, list) and "VideoObject" in kind:
            return doc
    return None


def _from_ssr(
    *,
    source_url: str,
    resolved_url: str,
    reader_url: str,
    video_id: str,
    result: dict[str, Any],
    jsonld: dict[str, Any] | None,
) -> ExtractedContent:
    title = str(result.get("title") or "").strip()
    text = str(result.get("abstract") or title).strip()
    user = result.get("media_user")
    user = user if isinstance(user, dict) else {}
    author = str(user.get("screen_name") or "").strip()
    cover = str(result.get("cover_image_url") or "").strip()

    duration = _duration_from_video_model(result.get("video_model"))
    if duration is None and jsonld is not None:
        duration = _parse_iso_duration(jsonld.get("duration"))

    media: list[dict[str, Any]] = [
        {
            "type": "video",
            "url": f"https://www.douyin.com/video/{video_id}",
        }
    ]
    if cover:
        media[0]["thumbnail_url"] = cover
    if duration is not None:
        media[0]["duration_seconds"] = duration

    return ExtractedContent(
        source_url=source_url,
        canonical_url=f"https://www.douyin.com/video/{video_id}",
        platform="douyin",
        kind="video",
        extraction_method="first_party_public_jingxuan_ssr_json",
        confidence=0.98,
        title=title,
        author=author,
        text=text,
        markdown=text,
        media=media,
        metadata={
            "video_id": video_id,
            "gid": str(result.get("gid") or video_id),
            "internal_video_id": str(result.get("video_id") or ""),
            "published_at": _timestamp(result.get("publish_time")),
            "duration_seconds": duration,
            "is_vertical": result.get("is_vertical"),
            "author": {
                "id": str(user.get("id") or ""),
                "screen_name": user.get("screen_name"),
                "followers_count": user.get("follower_count"),
                "video_count": user.get("video_count"),
                "avatar_url": user.get("avatar_url"),
            },
            "stats": {
                "play_count": result.get("play_count"),
                "digg_count": result.get("digg_count"),
            },
            "resolved_source_url": resolved_url,
            "public_reader_url": reader_url,
            "endpoint_documentation": "undocumented",
            "requires_login": False,
            "uses_private_signature": False,
            "metadata_only": True,
            "stream_urls_exported": False,
        },
        warnings=[
            "Douyin metadata was read from the anonymous first-party Jingxuan "
            "SSR reader. This frontend structure is undocumented and may change.",
            "ShareXtract intentionally excludes temporary playback/download URLs "
            "embedded in the page and returns metadata only.",
        ],
    )


def _from_jsonld(
    *,
    source_url: str,
    resolved_url: str,
    reader_url: str,
    video_id: str,
    value: dict[str, Any],
) -> ExtractedContent:
    title = str(value.get("name") or "").strip()
    text = str(value.get("description") or title).strip()
    author_value = value.get("author")
    author_value = author_value if isinstance(author_value, dict) else {}
    author = str(author_value.get("name") or "").strip()

    thumbnails = value.get("thumbnailUrl")
    if isinstance(thumbnails, str):
        thumbnail = thumbnails.strip()
    elif isinstance(thumbnails, list):
        thumbnail = next(
            (str(item).strip() for item in thumbnails if str(item).strip()),
            "",
        )
    else:
        thumbnail = ""

    duration = _parse_iso_duration(value.get("duration"))
    media: list[dict[str, Any]] = [
        {
            "type": "video",
            "url": f"https://www.douyin.com/video/{video_id}",
        }
    ]
    if thumbnail:
        media[0]["thumbnail_url"] = thumbnail
    if duration is not None:
        media[0]["duration_seconds"] = duration

    interaction = value.get("interactionStatistic")
    interaction = interaction if isinstance(interaction, dict) else {}

    return ExtractedContent(
        source_url=source_url,
        canonical_url=f"https://www.douyin.com/video/{video_id}",
        platform="douyin",
        kind="video",
        extraction_method="first_party_public_jingxuan_jsonld",
        confidence=0.92,
        title=title,
        author=author,
        text=text,
        markdown=text,
        media=media,
        metadata={
            "video_id": video_id,
            "published_at": value.get("uploadDate"),
            "duration_seconds": duration,
            "author": {
                "screen_name": author,
            },
            "stats": {
                "play_count": interaction.get("userInteractionCount"),
            },
            "resolved_source_url": resolved_url,
            "public_reader_url": reader_url,
            "endpoint_documentation": "standard_markup_on_undocumented_reader",
            "requires_login": False,
            "uses_private_signature": False,
            "metadata_only": True,
            "stream_urls_exported": False,
        },
        warnings=[
            "Douyin metadata fell back to schema.org VideoObject embedded in the "
            "anonymous first-party Jingxuan reader.",
            "ShareXtract returns metadata only and does not expose playback or "
            "download stream URLs.",
        ],
    )


def _duration_from_video_model(value: Any) -> float | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    duration = parsed.get("video_duration")
    if isinstance(duration, (int, float)):
        return float(duration)
    return None


def _parse_iso_duration(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    match = _DURATION_RE.fullmatch(value.strip())
    if not match:
        return None
    hours = float(match.group("hours") or 0)
    minutes = float(match.group("minutes") or 0)
    seconds = float(match.group("seconds") or 0)
    return hours * 3600 + minutes * 60 + seconds


def _timestamp(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(float(value), timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None
