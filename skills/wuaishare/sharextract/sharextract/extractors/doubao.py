from __future__ import annotations

import html
import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


_ROUTER_PATTERNS = (
    re.compile(
        r'data-script-src="modern-run-router-data-fn"\s+data-fn-args="(.*?)"\s+nonce="',
        re.DOTALL,
    ),
    re.compile(
        r'data-script-src="modern-run-window-fn"\s+data-fn-name="mergeLoaderData"\s+'
        r'data-fn-args="(.*?)"\s+nonce="',
        re.DOTALL,
    ),
)


class DoubaoShareExtractor(Extractor):
    """Extract public Doubao thread/share snapshots from embedded router JSON."""

    name = "doubao-share"
    priority = 22

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        if self.hostname(url) not in {"doubao.com", "www.doubao.com"}:
            return False
        parts = [part for part in parsed.path.split("/") if part]
        return len(parts) >= 2 and parts[0] in {"thread", "share"} and bool(parts[1])

    def extract(self, url: str) -> ExtractedContent:
        share_token = self._share_token(url)
        response = self.client.get(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
        )

        payload = _extract_router_payload(response.text)
        data = _find_share_data(payload)
        if not isinstance(data, dict):
            raise ExtractorError("Doubao public page did not contain share snapshot data.")

        share_info = data.get("share_info")
        share_info = share_info if isinstance(share_info, dict) else {}
        snapshot = data.get("message_snapshot")
        snapshot = snapshot if isinstance(snapshot, dict) else {}
        raw_messages = snapshot.get("message_list")

        if not isinstance(raw_messages, list) or not raw_messages:
            raise ExtractorError("Doubao public share returned no messages.")

        raw_messages = [item for item in raw_messages if isinstance(item, dict)]
        raw_messages.sort(key=lambda item: _sort_index(item.get("index")))

        messages: list[Message] = []
        message_metadata: list[dict[str, Any]] = []
        media: list[dict[str, Any]] = []
        seen_media: set[str] = set()

        for item in raw_messages:
            role = _role(item.get("user_type"))
            text_parts: list[str] = []

            blocks = item.get("content_block")
            if isinstance(blocks, list):
                for block in blocks:
                    if not isinstance(block, dict):
                        continue
                    public_block = _decode_public_block(block)
                    if not isinstance(public_block, dict):
                        continue

                    block_text = _text_from_block(public_block)
                    if block_text:
                        text_parts.append(block_text)

                    for candidate in _media_from_block(public_block):
                        url_value = candidate.get("url")
                        if isinstance(url_value, str) and url_value and url_value not in seen_media:
                            seen_media.add(url_value)
                            media.append(candidate)

            if not text_parts:
                fallback = _text_from_message_content(item.get("content"))
                if fallback:
                    text_parts.append(fallback)

            text = "\n\n".join(_dedupe(text_parts))
            if text:
                messages.append(Message(role=role, text=text))

            message_metadata.append(
                {
                    "message_id": item.get("message_id"),
                    "role": role,
                    "user_type": item.get("user_type"),
                    "index": item.get("index"),
                    "reply_id": item.get("reply_id"),
                    "section_id": item.get("section_id"),
                    "status": item.get("status"),
                    "content_type": item.get("content_type"),
                }
            )

        if not messages:
            raise ExtractorError("Doubao messages had no extractable public text.")

        user = share_info.get("user")
        user = user if isinstance(user, dict) else {}
        bot = share_info.get("bot")
        bot = bot if isinstance(bot, dict) else {}

        title = str(share_info.get("share_name") or "").strip()
        if not title:
            title = _title_from_messages(messages) or "Doubao shared conversation"

        canonical = _canonical_url(response.url, share_token)
        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="doubao",
            kind="conversation",
            extraction_method="first_party_embedded_router_json",
            confidence=0.98,
            title=title,
            author=str(user.get("nick_name") or "").strip(),
            text="\n\n".join(message.text for message in messages),
            markdown=_render_conversation(messages, str(bot.get("name") or "豆包")),
            messages=messages,
            media=media,
            metadata={
                "share_token": share_token,
                "share_id": share_info.get("share_id"),
                "share_status": share_info.get("share_status"),
                "share_time": _timestamp_ms(share_info.get("share_time")),
                "share_biz_type": share_info.get("share_biz_type"),
                "author": {
                    "name": user.get("nick_name"),
                    "avatar_url": _avatar_url(user.get("image")),
                },
                "bot": {
                    "name": bot.get("name"),
                    "bot_id": bot.get("bot_id"),
                    "bot_type": bot.get("bot_type"),
                },
                "messages": message_metadata,
                "endpoint_documentation": "undocumented",
                "reasoning_exported": False,
            },
            warnings=[
                "Doubao public share data is read from first-party router JSON embedded in "
                "the public HTML page. The page structure is undocumented and may change. "
                "Internal reasoning/thinking fields are not exported."
            ],
        )

    def _share_token(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[0] not in {"thread", "share"}:
            raise ExtractorError("Unsupported Doubao share URL.")
        token = parts[1].strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{6,256}", token):
            raise ExtractorError("Doubao share token is malformed.")
        return token


def _extract_router_payload(page_html: str) -> Any:
    for pattern in _ROUTER_PATTERNS:
        match = pattern.search(page_html)
        if not match:
            continue
        blob = html.unescape(match.group(1))
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            continue
    raise ExtractorError("Doubao public page router JSON was not found or was invalid.")


def _find_share_data(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if isinstance(value.get("message_snapshot"), dict):
            return value
        data = value.get("data")
        if isinstance(data, dict) and isinstance(data.get("message_snapshot"), dict):
            return data
        for child in value.values():
            found = _find_share_data(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            if (
                isinstance(child, dict)
                and isinstance(child.get("routerDataFnArgs"), list)
                and child["routerDataFnArgs"]
            ):
                raw = child["routerDataFnArgs"][0]
                if isinstance(raw, str):
                    try:
                        parsed = json.loads(raw)
                    except json.JSONDecodeError:
                        parsed = None
                    found = _find_share_data(parsed)
                    if found is not None:
                        return found
            found = _find_share_data(child)
            if found is not None:
                return found
    return None


def _decode_public_block(block: dict[str, Any]) -> dict[str, Any] | None:
    raw = block.get("content_v2")
    if raw in (None, ""):
        raw = block.get("content")

    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _text_from_block(block: dict[str, Any]) -> str:
    text_block = block.get("text_block")
    if isinstance(text_block, dict):
        text = text_block.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()

    text = block.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    return ""


def _text_from_message_content(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value.strip()
        if isinstance(parsed, dict):
            return _text_from_block(parsed)
    elif isinstance(value, dict):
        return _text_from_block(value)
    return ""


def _media_from_block(block: dict[str, Any]) -> list[dict[str, Any]]:
    creation_block = block.get("creation_block")
    if not isinstance(creation_block, dict):
        return []

    creations = creation_block.get("creations")
    if not isinstance(creations, list):
        return []

    result: list[dict[str, Any]] = []
    for creation in creations:
        if not isinstance(creation, dict):
            continue

        image = creation.get("image")
        if isinstance(image, dict):
            selected = _first_media_variant(
                image,
                ("image_ori", "image_preview", "image_thumb"),
            )
            if selected:
                result.append(
                    {
                        "type": "image",
                        "url": selected["url"],
                        "width": selected.get("width"),
                        "height": selected.get("height"),
                        "creation_id": creation.get("id"),
                    }
                )

        video = creation.get("video")
        if isinstance(video, dict):
            video_url = _first_url(
                video,
                ("url", "play_url", "video_url", "download_url"),
            )
            if video_url:
                result.append(
                    {
                        "type": "video",
                        "url": video_url,
                        "thumbnail_url": _first_url(
                            video,
                            ("poster_url", "cover_url", "thumbnail_url"),
                        ),
                        "creation_id": creation.get("id"),
                    }
                )

    return result


def _first_media_variant(
    value: dict[str, Any],
    keys: tuple[str, ...],
) -> dict[str, Any] | None:
    for key in keys:
        item = value.get(key)
        if isinstance(item, dict):
            url = item.get("url")
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                return {
                    "url": html.unescape(url),
                    "width": item.get("width"),
                    "height": item.get("height"),
                }
        elif isinstance(item, str) and item.startswith(("http://", "https://")):
            return {"url": html.unescape(item)}
    return None


def _first_url(value: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        item = value.get(key)
        if isinstance(item, str) and item.startswith(("http://", "https://")):
            return html.unescape(item)
        if isinstance(item, dict):
            url = item.get("url")
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                return html.unescape(url)
    return None


def _avatar_url(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    for key in ("origin_url", "tiny_url"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            return candidate
    return None


def _role(value: Any) -> str:
    if value == 1 or str(value).lower() in {"user", "human"}:
        return "user"
    if value == 2 or str(value).lower() in {"assistant", "agent", "bot"}:
        return "assistant"
    return "unknown"


def _sort_index(value: Any) -> tuple[int, str]:
    if isinstance(value, int):
        return (0, str(value).zfill(20))
    return (1, str(value or ""))


def _timestamp_ms(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(float(value) / 1000.0, timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _title_from_messages(messages: list[Message]) -> str:
    for message in messages:
        if message.role != "user":
            continue
        first = next((line.strip() for line in message.text.splitlines() if line.strip()), "")
        if first:
            return first if len(first) <= 100 else first[:97].rstrip() + "..."
    return ""


def _canonical_url(response_url: str, token: str) -> str:
    parsed = urllib.parse.urlsplit(response_url)
    host = parsed.hostname or "www.doubao.com"
    scheme = parsed.scheme or "https"
    return f"{scheme}://{host}/thread/{token}"


def _render_conversation(messages: list[Message], assistant_name: str) -> str:
    chunks: list[str] = []
    for message in messages:
        label = {
            "user": "User",
            "assistant": assistant_name or "Doubao",
            "system": "System",
        }.get(message.role, message.role.title())
        chunks.append(f"## {label}\n\n{message.text}")
    return "\n\n".join(chunks)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
