from __future__ import annotations

import re
import urllib.parse
from html.parser import HTMLParser
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_PUBLIC_PATHS = (
    re.compile(r"^/@[^/]+/([^/?#]+)/?$"),
    re.compile(r"^/users/[^/]+/statuses/([^/?#]+)/?$"),
)


class MastodonStatusExtractor(Extractor):
    """Extract public Mastodon-compatible statuses through the documented REST API."""

    name = "mastodon-public-api"
    priority = 40

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False
        path = urllib.parse.unquote(parsed.path)
        return any(pattern.match(path) for pattern in _PUBLIC_PATHS)

    def extract(self, url: str) -> ExtractedContent:
        parsed = urllib.parse.urlsplit(url)
        path = urllib.parse.unquote(parsed.path)
        status_id = _status_id_from_path(path)
        if not status_id:
            raise ExtractorError("Unsupported Mastodon status URL.")

        origin = urllib.parse.urlunsplit(
            (parsed.scheme, parsed.netloc, "", "", "")
        ).rstrip("/")
        endpoint = (
            origin
            + "/api/v1/statuses/"
            + urllib.parse.quote(status_id, safe="")
        )
        _, payload = self.client.get_json(
            endpoint,
            headers={"Accept": "application/json"},
        )
        if not _looks_like_status(payload):
            raise ExtractorError("The instance did not return a Mastodon-compatible Status.")

        status = payload
        visibility = str(status.get("visibility") or "").lower()
        if visibility in {"private", "direct"}:
            raise ExtractorError("The returned status is not public.")

        boosted = status.get("reblog")
        content_status = boosted if isinstance(boosted, dict) else status
        if not _looks_like_status(content_status):
            content_status = status

        account = content_status.get("account")
        account = account if isinstance(account, dict) else {}
        acct = str(account.get("acct") or account.get("username") or "").strip()
        display_name = _strip_html(str(account.get("display_name") or "")).strip()
        author = display_name or acct

        plain_text = _plain_status_text(content_status)
        content_warning = _strip_html(
            str(content_status.get("spoiler_text") or "")
        ).strip()
        markdown = plain_text
        if content_warning:
            markdown = f"Content warning: {content_warning}\n\n{plain_text}".strip()

        canonical_url = str(content_status.get("url") or status.get("url") or url)
        media = _collect_media(content_status)

        metadata: dict[str, Any] = {
            "id": content_status.get("id"),
            "uri": content_status.get("uri"),
            "visibility": content_status.get("visibility"),
            "sensitive": content_status.get("sensitive"),
            "content_warning": content_warning,
            "created_at": content_status.get("created_at"),
            "edited_at": content_status.get("edited_at"),
            "language": content_status.get("language"),
            "account_id": account.get("id"),
            "acct": acct,
            "username": account.get("username"),
            "display_name": display_name,
            "replies_count": content_status.get("replies_count"),
            "reblogs_count": content_status.get("reblogs_count"),
            "favourites_count": content_status.get("favourites_count"),
            "quotes_count": content_status.get("quotes_count"),
            "in_reply_to_id": content_status.get("in_reply_to_id"),
            "in_reply_to_account_id": content_status.get("in_reply_to_account_id"),
            "tags": _tag_names(content_status.get("tags")),
            "mentions": _mentions(content_status.get("mentions")),
        }

        poll = _normalize_poll(content_status.get("poll"))
        if poll:
            metadata["poll"] = poll

        quote = _normalize_quote(content_status.get("quote"))
        if quote:
            metadata["quote"] = quote

        if isinstance(boosted, dict):
            booster = status.get("account")
            booster = booster if isinstance(booster, dict) else {}
            metadata["boosted_by"] = {
                "id": booster.get("id"),
                "acct": booster.get("acct") or booster.get("username"),
                "display_name": _strip_html(
                    str(booster.get("display_name") or "")
                ).strip(),
                "status_id": status.get("id"),
                "status_url": status.get("url"),
            }

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical_url,
            platform="mastodon",
            kind="social_post",
            extraction_method="documented_public_mastodon_api",
            confidence=0.98,
            title=_status_title(acct, plain_text, content_warning),
            author=author,
            text=plain_text,
            markdown=markdown,
            media=media,
            metadata=metadata,
        )


def _status_id_from_path(path: str) -> str | None:
    for pattern in _PUBLIC_PATHS:
        match = pattern.match(path)
        if match:
            value = urllib.parse.unquote(match.group(1)).strip()
            return value or None
    return None


def _looks_like_status(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("id"), str)
        and isinstance(value.get("account"), dict)
        and ("content" in value or "text" in value)
    )


def _plain_status_text(status: dict[str, Any]) -> str:
    raw_text = status.get("text")
    if isinstance(raw_text, str) and raw_text.strip():
        return raw_text.strip()

    content = status.get("content")
    if isinstance(content, str):
        return _strip_html(content).strip()
    return ""


class _HTMLText(HTMLParser):
    _BREAK_TAGS = {"p", "br", "div", "li", "blockquote", "pre"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in self._BREAK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._BREAK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)


def _strip_html(value: str) -> str:
    if not value:
        return ""
    parser = _HTMLText()
    try:
        parser.feed(value)
        parser.close()
        text = "".join(parser.parts)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", value)
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _collect_media(status: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    attachments = status.get("media_attachments")
    if isinstance(attachments, list):
        for attachment in attachments:
            if not isinstance(attachment, dict):
                continue
            url = attachment.get("url") or attachment.get("remote_url")
            if not isinstance(url, str) or not url or url in seen:
                continue
            seen.add(url)
            items.append(
                {
                    "type": str(attachment.get("type") or "media"),
                    "url": url,
                    "preview_url": attachment.get("preview_url"),
                    "description": attachment.get("description"),
                    "blurhash": attachment.get("blurhash"),
                    "meta": attachment.get("meta"),
                }
            )

    card = status.get("card")
    if isinstance(card, dict):
        url = card.get("url")
        if isinstance(url, str) and url and url not in seen:
            seen.add(url)
            items.append(
                {
                    "type": "external",
                    "url": url,
                    "title": card.get("title"),
                    "description": card.get("description"),
                    "thumbnail_url": card.get("image"),
                    "provider_name": card.get("provider_name"),
                }
            )

    return items


def _normalize_poll(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    options = value.get("options")
    normalized_options: list[dict[str, Any]] = []
    if isinstance(options, list):
        for option in options:
            if isinstance(option, dict):
                normalized_options.append(
                    {
                        "title": option.get("title"),
                        "votes_count": option.get("votes_count"),
                    }
                )
    return {
        "id": value.get("id"),
        "expires_at": value.get("expires_at"),
        "expired": value.get("expired"),
        "multiple": value.get("multiple"),
        "votes_count": value.get("votes_count"),
        "voters_count": value.get("voters_count"),
        "options": normalized_options,
    }


def _normalize_quote(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    result: dict[str, Any] = {}
    for key in ("state", "quoted_status_id"):
        if key in value:
            result[key] = value.get(key)
    quoted = value.get("quoted_status")
    if isinstance(quoted, dict):
        result["quoted_status"] = {
            "id": quoted.get("id"),
            "url": quoted.get("url"),
            "uri": quoted.get("uri"),
            "text": _plain_status_text(quoted),
        }
    return result or None


def _tag_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        str(item.get("name"))
        for item in value
        if isinstance(item, dict) and item.get("name")
    ]


def _mentions(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "id": item.get("id"),
                "username": item.get("username"),
                "acct": item.get("acct"),
                "url": item.get("url"),
            }
        )
    return result


def _status_title(acct: str, text: str, content_warning: str) -> str:
    seed = content_warning or next(
        (line.strip() for line in text.splitlines() if line.strip()),
        "",
    )
    if len(seed) > 96:
        seed = seed[:93].rstrip() + "..."
    actor = f"@{acct}" if acct else "Mastodon"
    return f"{actor}: {seed}" if seed else f"{actor} status"
