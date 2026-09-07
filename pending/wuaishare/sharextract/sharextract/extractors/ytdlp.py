from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from urllib.parse import urlsplit

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_MEDIA_HOST_SUFFIXES = (
    "youtube.com",
    "youtu.be",
    "vimeo.com",
    "tiktok.com",
    "instagram.com",
    "x.com",
    "twitter.com",
    "bilibili.com",
    "b23.tv",
    "soundcloud.com",
    "twitch.tv",
    "facebook.com",
)


class YtDlpExtractor(Extractor):
    name = "yt-dlp"
    priority = 60

    def supports(self, url: str) -> bool:
        if shutil.which("yt-dlp") is None:
            return False
        host = (urlsplit(url).hostname or "").lower()
        return any(host == suffix or host.endswith("." + suffix) for suffix in _MEDIA_HOST_SUFFIXES)

    def extract(self, url: str) -> ExtractedContent:
        command = [
            "yt-dlp",
            "--dump-single-json",
            "--skip-download",
            "--no-playlist",
            "--no-warnings",
            url,
        ]
        try:
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=45,
            )
            payload = json.loads(completed.stdout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            raise ExtractorError(f"yt-dlp metadata extraction failed: {exc}") from exc

        description = str(payload.get("description") or "").strip()
        title = str(payload.get("title") or "").strip()
        uploader = str(payload.get("uploader") or payload.get("channel") or "").strip()
        webpage_url = str(payload.get("webpage_url") or url)
        media: list[dict] = []
        thumbnail = payload.get("thumbnail")
        if thumbnail:
            media.append({"type": "thumbnail", "url": thumbnail})
        timestamp = payload.get("timestamp")
        published_at = None
        if isinstance(timestamp, (int, float)):
            published_at = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()

        platform = str(payload.get("extractor_key") or payload.get("extractor") or "media").lower()
        return ExtractedContent(
            source_url=url,
            canonical_url=webpage_url,
            platform=platform,
            kind="media",
            extraction_method="yt_dlp_metadata",
            confidence=0.94,
            title=title,
            author=uploader,
            text=description,
            markdown=description,
            media=media,
            metadata={
                "id": payload.get("id"),
                "duration": payload.get("duration"),
                "published_at": published_at,
                "view_count": payload.get("view_count"),
                "like_count": payload.get("like_count"),
                "comment_count": payload.get("comment_count"),
                "extractor": payload.get("extractor"),
                "webpage_url": webpage_url,
            },
            warnings=[
                "yt-dlp is used in metadata-only mode; ShareXtract does not download media by default."
            ],
        )
