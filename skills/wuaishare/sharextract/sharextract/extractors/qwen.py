from __future__ import annotations

import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


_SHARE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,256}$")


class QwenShareExtractor(Extractor):
    """Extract public Qwen chat shares through the first-party share JSON API."""

    name = "qwen-share"
    priority = 24

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        if self.hostname(url) != "chat.qwen.ai":
            return False
        parts = [part for part in parsed.path.split("/") if part]
        return len(parts) >= 2 and parts[0] == "s" and bool(parts[1])

    def extract(self, url: str) -> ExtractedContent:
        share_id = self._share_id(url)
        endpoint = (
            "https://chat.qwen.ai/api/v2/chats/share/"
            + urllib.parse.quote(share_id, safe="")
        )
        _, payload = self.client.get_json(
            endpoint,
            headers={
                "Accept": "application/json",
                "Referer": "https://chat.qwen.ai/",
            },
        )

        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            raise ExtractorError("Qwen share endpoint returned invalid JSON.")

        returned_id = str(data.get("share_id") or data.get("id") or "").strip()
        if returned_id and returned_id != share_id:
            raise ExtractorError("Qwen share ID did not match the requested share.")

        chat = data.get("chat")
        if not isinstance(chat, dict):
            raise ExtractorError("Qwen share did not contain chat data.")

        raw_messages = chat.get("messages")
        if not isinstance(raw_messages, list) or not raw_messages:
            history = chat.get("history")
            if isinstance(history, dict):
                mapping = history.get("messages")
                if isinstance(mapping, dict):
                    raw_messages = list(mapping.values())

        if not isinstance(raw_messages, list) or not raw_messages:
            raise ExtractorError("Qwen public share returned no messages.")

        messages: list[Message] = []
        message_metadata: list[dict[str, Any]] = []
        media: list[dict[str, Any]] = []
        seen_media: set[str] = set()

        for item in raw_messages:
            if not isinstance(item, dict):
                continue

            role = str(item.get("role") or "unknown").lower().strip()
            text = _public_message_text(item)
            attachments = _public_files(item.get("files"))

            if text or attachments:
                messages.append(
                    Message(
                        role=role,
                        text=text,
                        created_at=_timestamp(item.get("timestamp")),
                        attachments=attachments,
                    )
                )

            metadata = {
                "id": item.get("id"),
                "role": role,
                "parent_id": item.get("parentId"),
                "children_ids": item.get("childrenIds")
                if isinstance(item.get("childrenIds"), list)
                else [],
                "timestamp": _timestamp(item.get("timestamp")),
                "models": item.get("models")
                if isinstance(item.get("models"), list)
                else [],
                "model": item.get("model"),
                "model_name": item.get("modelName"),
                "chat_type": item.get("chat_type"),
                "sub_chat_type": item.get("sub_chat_type"),
            }
            message_metadata.append(metadata)

            for attachment in attachments:
                for candidate in _media_from_attachment(attachment):
                    media_url = candidate["url"]
                    if media_url not in seen_media:
                        seen_media.add(media_url)
                        media.append(candidate)

        if not messages:
            raise ExtractorError("Qwen messages had no extractable public content.")

        title = str(data.get("title") or "").strip() or "Qwen shared conversation"
        models = data.get("models")
        if not isinstance(models, list):
            models = chat.get("models") if isinstance(chat.get("models"), list) else []

        return ExtractedContent(
            source_url=url,
            canonical_url=f"https://chat.qwen.ai/s/{share_id}",
            platform="qwen",
            kind="conversation",
            extraction_method="first_party_undocumented_public_json",
            confidence=0.99,
            title=title,
            text="\n\n".join(message.text for message in messages if message.text),
            markdown=_render_conversation(messages),
            messages=messages,
            media=media,
            metadata={
                "share_id": share_id,
                "chat_id": data.get("id"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "chat_type": data.get("chat_type"),
                "models": models,
                "current_id": data.get("currentId"),
                "current_response_ids": data.get("currentResponseIds")
                if isinstance(data.get("currentResponseIds"), list)
                else [],
                "messages": message_metadata,
                "endpoint_documentation": "undocumented",
                "reasoning_exported": False,
            },
            warnings=[
                "Qwen's public share JSON route is first-party and anonymous but undocumented. "
                "Internal reasoning/thinking fields are intentionally not exported."
            ],
        )

    def _share_id(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[0] != "s":
            raise ExtractorError("Unsupported Qwen share URL.")
        share_id = parts[1].strip()
        if not _SHARE_ID_RE.fullmatch(share_id):
            raise ExtractorError("Qwen share ID is malformed.")
        return share_id


def _public_message_text(item: dict[str, Any]) -> str:
    direct = item.get("content")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    content_list = item.get("content_list")
    if not isinstance(content_list, list):
        return ""

    parts: list[str] = []
    for block in content_list:
        if not isinstance(block, dict):
            continue
        phase = str(block.get("phase") or "").lower().strip()
        if phase != "answer":
            continue
        content = block.get("content")
        if isinstance(content, str) and content.strip():
            parts.append(content.strip())

    return "\n\n".join(_dedupe(parts))


def _public_files(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            result.append(dict(item))
        elif isinstance(item, str) and item.strip():
            result.append({"value": item.strip()})
    return result


def _media_from_attachment(value: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for key in ("url", "file_url", "download_url", "preview_url", "thumbnail_url"):
        candidate = value.get(key)
        if not isinstance(candidate, str) or not candidate.startswith(("http://", "https://")):
            continue
        lowered = candidate.lower()
        if re.search(r"\.(?:png|jpe?g|webp|gif)(?:[?#]|$)", lowered):
            kind = "image"
        elif re.search(r"\.(?:mp4|webm|mov)(?:[?#]|$)", lowered):
            kind = "video"
        else:
            kind = "file"
        result.append({"type": kind, "url": candidate})
    return result


def _timestamp(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(float(value), timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _render_conversation(messages: list[Message]) -> str:
    chunks: list[str] = []
    for message in messages:
        label = {
            "user": "User",
            "assistant": "Qwen",
            "system": "System",
        }.get(message.role, message.role.title())
        if message.text:
            chunks.append(f"## {label}\n\n{message.text}")
        elif message.attachments:
            chunks.append(f"## {label}\n\n[Attachment-only message]")
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
