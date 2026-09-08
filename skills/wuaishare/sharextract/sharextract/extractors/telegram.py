from __future__ import annotations

import re
import urllib.parse
from html.parser import HTMLParser
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_TELEGRAM_HOSTS = {
    "t.me",
    "www.t.me",
    "telegram.me",
    "www.telegram.me",
}
_POST_RE = re.compile(r"^/(?P<channel>[A-Za-z0-9_]+)/(?P<message_id>\d+)/?$")


class TelegramPostExtractor(Extractor):
    """Extract public Telegram channel/group posts through the official Post Widget."""

    name = "telegram-post"
    priority = 36

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        return host in _TELEGRAM_HOSTS and _POST_RE.fullmatch(parsed.path) is not None

    def extract(self, url: str) -> ExtractedContent:
        canonical, channel, message_id = _canonical_post_url(url)
        widget_url = canonical + "?embed=1&mode=tme"
        response = self.client.get_text(
            widget_url,
            headers={
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        if "text/html" not in response.content_type.lower():
            raise ExtractorError("Telegram Post Widget did not return HTML.")

        parser = _TelegramWidgetParser()
        try:
            parser.feed(response.text)
            parser.close()
        except Exception as exc:
            raise ExtractorError(
                f"Telegram Post Widget HTML could not be parsed: {exc}"
            ) from exc

        text = _clean_text(parser.values.get("text", ""))
        author = _clean_text(parser.values.get("author", ""))
        if not text and not author:
            raise ExtractorError(
                "Telegram Post Widget returned no public message content."
            )

        media: list[dict[str, Any]] = []
        for image_url in _dedupe(parser.photo_urls):
            media.append(
                {
                    "type": "image",
                    "url": image_url,
                }
            )

        title = _title_from_text(text)
        if not title:
            title = f"Telegram post by {author or '@' + channel}"

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="telegram",
            kind="social_post",
            extraction_method="documented_telegram_post_widget",
            confidence=0.99,
            title=title,
            author=author,
            text=text,
            markdown=text,
            media=media,
            metadata={
                "channel": channel,
                "message_id": message_id,
                "author_url": parser.author_url,
                "published_at": parser.published_at,
                "views_display": _clean_text(
                    parser.values.get("views", "")
                ),
                "verified": parser.verified,
                "reactions": parser.reactions,
                "link_preview": {
                    key: value
                    for key, value in {
                        "url": parser.link_preview_url,
                        "site_name": _clean_text(
                            parser.values.get("preview_site", "")
                        ),
                        "title": _clean_text(
                            parser.values.get("preview_title", "")
                        ),
                        "description": _clean_text(
                            parser.values.get("preview_description", "")
                        ),
                    }.items()
                    if value
                },
                "endpoint_documentation": "official_telegram_post_widget",
                "requires_login": False,
                "uses_bot_token": False,
                "uses_browser": False,
                "stream_urls_exported": False,
            },
            warnings=[
                "Telegram public post content is read from the official anonymous "
                "Post Widget HTML documented by Telegram.",
                "Temporary audio/video playback stream URLs, widget auth/upload "
                "API parameters, and account state are not exported.",
            ],
        )


class _TelegramWidgetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.captures: list[dict[str, Any]] = []
        self.values: dict[str, str] = {}
        self.photo_urls: list[str] = []
        self.reactions: list[dict[str, Any]] = []
        self.author_url = ""
        self.published_at = ""
        self.verified = False
        self.link_preview_url = ""

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        is_void = tag in {
            "area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr",
        }
        if not is_void:
            self.depth += 1

        attr = {
            str(key): str(value)
            for key, value in attrs
            if key and value is not None
        }
        classes = set(attr.get("class", "").split())

        key = None
        if "tgme_widget_message_owner_name" in classes:
            key = "author"
            self.author_url = _absolute_tme(attr.get("href", ""))
        elif "tgme_widget_message_text" in classes:
            key = "text"
        elif "tgme_widget_message_views" in classes:
            key = "views"
        elif "link_preview_site_name" in classes:
            key = "preview_site"
        elif "link_preview_title" in classes:
            key = "preview_title"
        elif "link_preview_description" in classes:
            key = "preview_description"

        if key and not is_void:
            self.captures.append(
                {
                    "key": key,
                    "depth": self.depth,
                    "parts": [],
                }
            )

        if "tgme_widget_message_link_preview" in classes:
            self.link_preview_url = attr.get("href", "")

        if "verified-icon" in classes:
            self.verified = True

        if "tgme_widget_message_photo_wrap" in classes:
            image_url = _css_background_url(attr.get("style", ""))
            if image_url:
                self.photo_urls.append(image_url)

        if "tgme_reaction" in classes and not is_void:
            self.captures.append(
                {
                    "key": "__reaction__",
                    "depth": self.depth,
                    "parts": [],
                    "paid": "tgme_reaction_paid" in classes,
                }
            )

        if tag == "time" and attr.get("datetime"):
            self.published_at = attr["datetime"]

        if tag == "br":
            for capture in self.captures:
                if capture["key"] == "text":
                    capture["parts"].append("\n")

    def handle_data(self, data: str) -> None:
        if not data:
            return
        for capture in self.captures:
            capture["parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {
            "area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr",
        }:
            return

        remaining: list[dict[str, Any]] = []
        for capture in self.captures:
            if capture["depth"] == self.depth:
                value = _clean_text("".join(capture["parts"]))
                if capture["key"] == "__reaction__":
                    if value:
                        self.reactions.append(
                            _reaction(value, paid=bool(capture.get("paid")))
                        )
                elif value and capture["key"] not in self.values:
                    self.values[capture["key"]] = value
            else:
                remaining.append(capture)
        self.captures = remaining
        self.depth = max(0, self.depth - 1)


def _canonical_post_url(url: str) -> tuple[str, str, str]:
    parsed = urllib.parse.urlsplit(url)
    match = _POST_RE.fullmatch(parsed.path)
    if match is None:
        raise ExtractorError("Telegram URL is not a supported public post URL.")
    channel = match.group("channel")
    message_id = match.group("message_id")
    return f"https://t.me/{channel}/{message_id}", channel, message_id


def _absolute_tme(value: str) -> str:
    if value.startswith("//"):
        return "https:" + value
    return value


def _css_background_url(style: str) -> str:
    match = re.search(
        r"background-image\s*:\s*url\((['\"]?)(.*?)\1\)",
        style or "",
        flags=re.IGNORECASE,
    )
    if not match:
        return ""
    return _absolute_tme(match.group(2).strip())


def _reaction(value: str, *, paid: bool) -> dict[str, Any]:
    token = _clean_text(value)
    match = re.match(r"^(.*?)([\d][\d.,]*(?:[KMB])?)$", token, re.IGNORECASE)
    if match:
        label = match.group(1).strip()
        count = match.group(2)
    else:
        label = ""
        count = token
    result: dict[str, Any] = {
        "count_display": count,
        "paid": paid,
    }
    if label:
        result["label"] = label
    return result


def _clean_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _title_from_text(value: str) -> str:
    first = next(
        (line.strip() for line in value.splitlines() if line.strip()),
        "",
    )
    if len(first) <= 100:
        return first
    return first[:97].rstrip() + "..."


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        token = str(value or "").strip()
        if token and token not in seen:
            seen.add(token)
            result.append(token)
    return result
