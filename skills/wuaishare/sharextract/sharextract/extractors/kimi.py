from __future__ import annotations

import re
import urllib.parse
from typing import Any

from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


_SHARE_ID_RE = re.compile(r"^[A-Za-z0-9-]{6,128}$")


class KimiShareExtractor(Extractor):
    """Extract public Kimi chat shares through the first-party share JSON API."""

    name = "kimi-share"
    priority = 23

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        if self.hostname(url) not in {"kimi.com", "www.kimi.com"}:
            return False
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[0] != "share":
            return False
        return bool(parts[-1])

    def extract(self, url: str) -> ExtractedContent:
        share_id = self._share_id(url)
        endpoint = (
            "https://www.kimi.com/apiv2/"
            "kimi.gateway.chat.v1.ChatService/GetChatShare"
        )
        _, payload = self.client.post_json(
            endpoint,
            {"share_id": share_id},
            headers={
                "Accept": "application/json",
                "Referer": f"https://www.kimi.com/share/{share_id}",
            },
        )

        share = payload.get("share") if isinstance(payload, dict) else None
        if not isinstance(share, dict):
            raise ExtractorError("Kimi share endpoint returned invalid JSON.")

        returned_id = str(share.get("id") or "").strip()
        if returned_id and returned_id != share_id:
            raise ExtractorError("Kimi share ID did not match the requested share.")

        raw_messages = share.get("messages")
        if not isinstance(raw_messages, list) or not raw_messages:
            raise ExtractorError("Kimi public share returned no messages.")

        ordered = _order_messages(
            [item for item in raw_messages if isinstance(item, dict)]
        )
        messages: list[Message] = []
        message_metadata: list[dict[str, Any]] = []
        media: list[dict[str, Any]] = []
        seen_media: set[str] = set()

        for item in ordered:
            role = str(item.get("role") or "unknown").lower().strip()
            text = _public_message_text(item)
            if text:
                messages.append(
                    Message(
                        role=role,
                        text=text,
                        created_at=item.get("createTime"),
                    )
                )

            block_types = _block_types(item.get("blocks"))
            message_metadata.append(
                {
                    "id": item.get("id"),
                    "role": role,
                    "parent_id": item.get("parentId"),
                    "children_message_ids": item.get("childrenMessageIds")
                    if isinstance(item.get("childrenMessageIds"), list)
                    else [],
                    "created_at": item.get("createTime"),
                    "status": item.get("status"),
                    "scenario": item.get("scenario"),
                    "block_types": block_types,
                    "refs": item.get("refs")
                    if isinstance(item.get("refs"), dict)
                    else {},
                }
            )

            for candidate in _public_media(item.get("blocks")):
                media_url = candidate["url"]
                if media_url not in seen_media:
                    seen_media.add(media_url)
                    media.append(candidate)

        if not messages:
            raise ExtractorError("Kimi messages had no extractable public text.")

        chat = share.get("chat")
        chat = chat if isinstance(chat, dict) else {}
        creator = share.get("creator")
        creator = creator if isinstance(creator, dict) else {}

        title = str(chat.get("name") or "").strip() or "Kimi shared conversation"
        author = str(creator.get("name") or "").strip()

        return ExtractedContent(
            source_url=url,
            canonical_url=f"https://www.kimi.com/share/{share_id}",
            platform="kimi",
            kind="conversation",
            extraction_method="first_party_undocumented_public_json",
            confidence=0.99,
            title=title,
            author=author,
            text="\n\n".join(message.text for message in messages),
            markdown=_render_conversation(messages),
            messages=messages,
            media=media,
            metadata={
                "share_id": share_id,
                "chat_id": chat.get("id"),
                "creator": {
                    "name": creator.get("name"),
                    "avatar_url": creator.get("avatarUrl"),
                },
                "messages": message_metadata,
                "share_url": share.get("url"),
                "endpoint_documentation": "undocumented",
                "reasoning_exported": False,
            },
            warnings=[
                "Kimi's GetChatShare route is a first-party anonymous public JSON endpoint "
                "but is not a documented external API contract. Internal reasoning fields, "
                "if present, are not exported."
            ],
        )

    def _share_id(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[0] != "share":
            raise ExtractorError("Unsupported Kimi share URL.")

        if len(parts) >= 3 and re.fullmatch(r"[A-Za-z]{2}", parts[1]):
            share_id = parts[2]
        else:
            share_id = parts[1]

        if not _SHARE_ID_RE.fullmatch(share_id):
            raise ExtractorError("Kimi share ID is malformed.")
        return share_id


def _public_message_text(item: dict[str, Any]) -> str:
    blocks = item.get("blocks")
    if not isinstance(blocks, list):
        return ""

    parts: list[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        text = block.get("text")
        if isinstance(text, dict):
            content = text.get("content")
            if isinstance(content, str) and content.strip():
                parts.append(content.strip())
        elif isinstance(text, str) and text.strip():
            parts.append(text.strip())

    return "\n\n".join(_dedupe(parts))


def _order_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not messages:
        return []

    mapping = {
        str(item.get("id")): item
        for item in messages
        if item.get("id") is not None
    }
    roots = [
        item
        for item in messages
        if not item.get("parentId") or str(item.get("parentId")) not in mapping
    ]
    roots.sort(key=lambda item: str(item.get("createTime") or ""))

    ordered: list[dict[str, Any]] = []
    seen: set[str] = set()

    def walk(item: dict[str, Any]) -> None:
        item_id = str(item.get("id") or "")
        if item_id and item_id in seen:
            return
        if item_id:
            seen.add(item_id)
        ordered.append(item)

        children = item.get("childrenMessageIds")
        if isinstance(children, list):
            for child_id in children:
                child = mapping.get(str(child_id))
                if child is not None:
                    walk(child)

    for root in roots:
        walk(root)

    for item in messages:
        item_id = str(item.get("id") or "")
        if not item_id or item_id not in seen:
            walk(item)

    return ordered


def _block_types(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for block in value:
        if not isinstance(block, dict):
            continue
        for key in block:
            if key == "id":
                continue
            if key not in result:
                result.append(key)
    return result


def _public_media(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def visit(node: Any) -> None:
        if isinstance(node, list):
            for child in node:
                visit(child)
            return
        if not isinstance(node, dict):
            return

        for key, child in node.items():
            key_lower = str(key).lower()
            if isinstance(child, str) and child.startswith(("http://", "https://")):
                lowered = child.lower()
                if any(token in key_lower for token in ("url", "src", "image", "video", "cover")):
                    if re.search(r"\.(?:png|jpe?g|webp|gif)(?:[?#]|$)", lowered):
                        kind = "image"
                    elif re.search(r"\.(?:mp4|webm|mov)(?:[?#]|$)", lowered):
                        kind = "video"
                    else:
                        kind = "external"
                    found.append({"type": kind, "url": child})
            elif key_lower not in {"thinking", "reasoning", "chain_of_thought"}:
                visit(child)

    visit(value)
    return found


def _render_conversation(messages: list[Message]) -> str:
    chunks: list[str] = []
    for message in messages:
        label = {
            "user": "User",
            "assistant": "Kimi",
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
