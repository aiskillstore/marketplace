from __future__ import annotations

import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_VIDEO_ID_RE = re.compile(r"^(BV[A-Za-z0-9]+|av\d+)$", re.IGNORECASE)


class BilibiliVideoExtractor(Extractor):
    """Extract public Bilibili video metadata from the first-party view JSON."""

    name = "bilibili-video"
    priority = 34

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        if self.hostname(url) not in {
            "bilibili.com",
            "www.bilibili.com",
            "m.bilibili.com",
        }:
            return False
        parts = [part for part in parsed.path.split("/") if part]
        return (
            len(parts) >= 2
            and parts[0] == "video"
            and bool(_VIDEO_ID_RE.fullmatch(parts[1]))
        )

    def extract(self, url: str) -> ExtractedContent:
        video_id = self._video_id(url)
        if video_id.lower().startswith("bv"):
            query = {"bvid": video_id}
        else:
            query = {"aid": video_id[2:]}

        endpoint = (
            "https://api.bilibili.com/x/web-interface/view?"
            + urllib.parse.urlencode(query)
        )
        _, payload = self.client.get_json(
            endpoint,
            headers={
                "Accept": "application/json",
                "Referer": "https://www.bilibili.com/",
            },
        )
        if not isinstance(payload, dict):
            raise ExtractorError("Bilibili view endpoint returned invalid JSON.")
        if payload.get("code") != 0:
            raise ExtractorError(
                "Bilibili view endpoint rejected the public video: "
                + str(payload.get("message") or payload.get("code"))
            )

        data = payload.get("data")
        if not isinstance(data, dict):
            raise ExtractorError("Bilibili view endpoint returned no video data.")

        bvid = str(data.get("bvid") or "").strip()
        aid = data.get("aid")
        canonical_id = bvid or (f"av{aid}" if aid else video_id)
        canonical = f"https://www.bilibili.com/video/{canonical_id}"

        title = str(data.get("title") or "").strip()
        description = str(data.get("desc") or "").strip()
        owner = data.get("owner")
        owner = owner if isinstance(owner, dict) else {}
        author = str(owner.get("name") or "").strip()

        picture = _https_url(data.get("pic"))
        duration = data.get("duration")
        media: list[dict[str, Any]] = [
            {
                "type": "video",
                "url": canonical,
                "thumbnail_url": picture,
                "duration_seconds": duration
                if isinstance(duration, (int, float))
                else None,
            }
        ]

        pages = []
        raw_pages = data.get("pages")
        if isinstance(raw_pages, list):
            for page in raw_pages:
                if not isinstance(page, dict):
                    continue
                pages.append(
                    {
                        "cid": page.get("cid"),
                        "page": page.get("page"),
                        "part": page.get("part"),
                        "duration": page.get("duration"),
                        "dimension": page.get("dimension")
                        if isinstance(page.get("dimension"), dict)
                        else {},
                    }
                )

        stat = data.get("stat")
        stat = stat if isinstance(stat, dict) else {}
        rights = data.get("rights")
        rights = rights if isinstance(rights, dict) else {}

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="bilibili",
            kind="video",
            extraction_method="first_party_undocumented_public_json",
            confidence=0.99,
            title=title,
            author=author,
            text=description or title,
            markdown=description or title,
            media=media,
            metadata={
                "bvid": bvid,
                "aid": aid,
                "cid": data.get("cid"),
                "published_at": _timestamp(data.get("pubdate")),
                "created_at": _timestamp(data.get("ctime")),
                "duration_seconds": duration,
                "owner": {
                    "mid": owner.get("mid"),
                    "name": owner.get("name"),
                    "face": _https_url(owner.get("face")),
                },
                "stats": {
                    key: stat.get(key)
                    for key in (
                        "view",
                        "danmaku",
                        "reply",
                        "favorite",
                        "coin",
                        "share",
                        "like",
                    )
                    if key in stat
                },
                "rights": {
                    key: rights.get(key)
                    for key in (
                        "download",
                        "no_reprint",
                        "is_cooperation",
                        "pay",
                        "ugc_pay",
                    )
                    if key in rights
                },
                "pages": pages,
                "endpoint_documentation": "undocumented",
            },
            warnings=[
                "Bilibili metadata was read from the first-party public "
                "/x/web-interface/view JSON route, which is provider-owned but "
                "not treated as a documented external API contract."
            ],
        )

    def _video_id(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[0] != "video":
            raise ExtractorError("Unsupported Bilibili video URL.")
        video_id = parts[1].strip()
        if not _VIDEO_ID_RE.fullmatch(video_id):
            raise ExtractorError("Bilibili video ID is malformed.")
        if video_id.lower().startswith("bv"):
            return "BV" + video_id[2:]
        return "av" + video_id[2:]


def _timestamp(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(float(value), timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _https_url(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    if value.startswith("http://"):
        return "https://" + value[len("http://") :]
    if value.startswith("//"):
        return "https:" + value
    return value
