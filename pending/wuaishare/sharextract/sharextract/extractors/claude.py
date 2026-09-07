from __future__ import annotations

import re
import urllib.parse
from typing import Any

from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


_SHARE_ID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


class ClaudeShareExtractor(Extractor):
    """Extract public Claude snapshots through Claude's first-party JSON endpoint."""

    name = "claude-share"
    priority = 20

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        if self.hostname(url) != "claude.ai":
            return False
        parts = [part for part in parsed.path.split("/") if part]
        return len(parts) >= 2 and parts[0] == "share" and bool(parts[1])

    def extract(self, url: str) -> ExtractedContent:
        share_id = self._share_id(url)
        endpoint = f"https://claude.ai/api/chat_snapshots/{share_id}"
        _, payload = self.client.get_json(
            endpoint,
            headers={
                "Accept": "application/json",
                "Referer": "https://claude.ai/",
            },
        )
        if not isinstance(payload, dict):
            raise ExtractorError("Claude snapshot endpoint returned invalid JSON.")

        returned_id = str(payload.get("uuid") or "").strip()
        if returned_id and returned_id.lower() != share_id.lower():
            raise ExtractorError("Claude snapshot ID did not match the requested share.")

        if payload.get("is_public") is False:
            raise ExtractorError("Claude snapshot is not public.")

        raw_messages = payload.get("chat_messages")
        if not isinstance(raw_messages, list) or not raw_messages:
            raise ExtractorError("Claude public snapshot returned no messages.")

        messages: list[Message] = []
        message_metadata: list[dict[str, Any]] = []
        media: list[dict[str, Any]] = []
        seen_media: set[str] = set()

        for item in raw_messages:
            if not isinstance(item, dict):
                continue

            sender = str(item.get("sender") or "").lower().strip()
            role = {
                "human": "user",
                "user": "user",
                "assistant": "assistant",
                "system": "system",
            }.get(sender, sender or "unknown")

            text = _message_text(item)
            attachments = _message_attachments(item)

            if text or attachments:
                messages.append(
                    Message(
                        role=role,
                        text=text,
                        created_at=item.get("created_at"),
                        attachments=attachments,
                    )
                )

            message_metadata.append(
                {
                    "uuid": item.get("uuid"),
                    "index": item.get("index"),
                    "sender": sender,
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "parent_message_uuid": item.get("parent_message_uuid"),
                    "stop_reason": item.get("stop_reason"),
                    "truncated": item.get("truncated"),
                    "input_mode": item.get("input_mode"),
                    "file_count": item.get("file_count"),
                    "image_count": item.get("image_count"),
                    "compaction_summary": item.get("compaction_summary"),
                }
            )

            for media_item in _media_from_value(attachments):
                media_url = media_item["url"]
                if media_url not in seen_media:
                    seen_media.add(media_url)
                    media.append(media_item)

        if not messages:
            raise ExtractorError("Claude messages had no extractable content.")

        title = str(payload.get("snapshot_name") or "").strip()
        if not title:
            title = "Claude shared conversation"

        creator = payload.get("creator")
        creator = creator if isinstance(creator, dict) else {}
        author = (
            str(payload.get("created_by") or "").strip()
            or str(creator.get("full_name") or "").strip()
        )

        working_documents = payload.get("working_documents")
        if not isinstance(working_documents, list):
            working_documents = []

        return ExtractedContent(
            source_url=url,
            canonical_url=f"https://claude.ai/share/{share_id}",
            platform="claude",
            kind="conversation",
            extraction_method="first_party_undocumented_public_json",
            confidence=0.99,
            title=title,
            author=author,
            text="\n\n".join(message.text for message in messages if message.text),
            markdown=_render_conversation(messages),
            messages=messages,
            media=media,
            metadata={
                "share_id": share_id,
                "conversation_uuid": payload.get("conversation_uuid"),
                "created_at": payload.get("created_at"),
                "updated_at": payload.get("updated_at"),
                "created_by": payload.get("created_by"),
                "creator_uuid": creator.get("uuid"),
                "project_uuid": payload.get("project_uuid"),
                "is_public": payload.get("is_public"),
                "up_to_date": payload.get("up_to_date"),
                "messages": message_metadata,
                "working_documents": working_documents,
                "endpoint_documentation": "undocumented",
            },
            warnings=[
                "Claude's chat_snapshots route is a first-party anonymous public JSON endpoint, "
                "but it is an undocumented frontend implementation detail and may change."
            ],
        )

    def _share_id(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[0] != "share":
            raise ExtractorError("Unsupported Claude share URL.")
        share_id = urllib.parse.unquote(parts[1]).strip()
        if not _SHARE_ID_RE.fullmatch(share_id):
            raise ExtractorError("Claude share ID is malformed.")
        return share_id


def _message_text(item: dict[str, Any]) -> str:
    text = item.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()

    content = item.get("content")
    chunks: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, str):
            value = node.strip()
            if value:
                chunks.append(value)
            return
        if isinstance(node, list):
            for child in node:
                visit(child)
            return
        if not isinstance(node, dict):
            return

        node_type = str(node.get("type") or "").lower()
        for key in ("text", "thinking", "content"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                prefix = "Thinking: " if key == "thinking" or node_type == "thinking" else ""
                chunks.append(prefix + value.strip())
                return
        if "input" in node:
            visit(node.get("input"))

    visit(content)
    return "\n\n".join(_dedupe_strings(chunks))


def _message_attachments(item: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for key in ("attachments", "files"):
        value = item.get(key)
        if not isinstance(value, list):
            continue
        for entry in value:
            if isinstance(entry, dict):
                normalized = dict(entry)
                normalized.setdefault("source_field", key)
                result.append(normalized)
            elif isinstance(entry, str) and entry.strip():
                result.append({"source_field": key, "value": entry.strip()})
    return result


def _media_from_value(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def visit(node: Any) -> None:
        if isinstance(node, list):
            for child in node:
                visit(child)
            return
        if isinstance(node, dict):
            for key, child in node.items():
                if isinstance(child, str) and child.startswith(("http://", "https://")):
                    lowered = child.lower()
                    key_lower = str(key).lower()
                    if (
                        any(token in key_lower for token in ("url", "preview", "thumbnail"))
                        or re.search(r"\.(?:png|jpe?g|webp|gif|mp4|webm|pdf)(?:[?#]|$)", lowered)
                    ):
                        media_type = "image" if re.search(r"\.(?:png|jpe?g|webp|gif)(?:[?#]|$)", lowered) else "file"
                        found.append({"type": media_type, "url": child})
                else:
                    visit(child)

    visit(value)
    return found


def _render_conversation(messages: list[Message]) -> str:
    chunks: list[str] = []
    for message in messages:
        label = {
            "user": "User",
            "assistant": "Claude",
            "system": "System",
        }.get(message.role, message.role.title())
        body = message.text.strip()
        if body:
            chunks.append(f"## {label}\n\n{body}")
        elif message.attachments:
            chunks.append(f"## {label}\n\n[Attachment-only message]")
    return "\n\n".join(chunks)


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
