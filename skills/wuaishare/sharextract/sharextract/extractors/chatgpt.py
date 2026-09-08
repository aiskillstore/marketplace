from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any

from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


_SHARE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,256}$")
_STREAM_RE = re.compile(
    r'streamController\.enqueue\((".*?")\);</script>',
    re.DOTALL,
)


class ChatGPTShareExtractor(Extractor):
    """Extract public ChatGPT share pages without account/session state."""

    name = "chatgpt-share"
    priority = 20

    def supports(self, url: str) -> bool:
        host = self.hostname(url)
        if host not in {"chatgpt.com", "chat.openai.com"}:
            return False
        parsed = urllib.parse.urlsplit(url)
        parts = [part for part in parsed.path.split("/") if part]
        return len(parts) >= 2 and parts[0] in {"share", "s"} and bool(parts[1])

    def extract(self, url: str) -> ExtractedContent:
        share_type, share_id = self._share_ref(url)
        canonical = f"https://chatgpt.com/{share_type}/{share_id}"
        page_error = ""

        try:
            response = self.client.get_text(
                canonical,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
            parsed = _parse_turbo_stream(response.text)
            if parsed is not None:
                title, messages = parsed
                if messages:
                    return self._result(
                        source_url=url,
                        canonical_url=response.url,
                        share_type=share_type,
                        share_id=share_id,
                        title=title,
                        messages=messages,
                        method="first_party_embedded_turbo_stream",
                        confidence=0.98,
                        warnings=[
                            "ChatGPT public content was decoded from the first-party React Router "
                            "turbo-stream embedded in the public page. This serialization is "
                            "provider-owned but undocumented and may change."
                        ],
                    )
                page_error = "public turbo-stream contained no extractable user/assistant messages"
            else:
                page_error = "public turbo-stream payload was not found"
        except Exception as exc:
            page_error = str(exc)

        if share_type == "share":
            endpoint = (
                "https://chatgpt.com/backend-api/share/"
                + urllib.parse.quote(share_id, safe="")
            )
            try:
                _, payload = self.client.get_json(
                    endpoint,
                    headers={"Accept": "application/json"},
                )
                if isinstance(payload, dict):
                    messages = _messages_from_legacy_payload(payload)
                    if messages:
                        title = (
                            str(payload.get("title") or "").strip()
                            or "ChatGPT shared conversation"
                        )
                        return self._result(
                            source_url=url,
                            canonical_url=canonical,
                            share_type=share_type,
                            share_id=share_id,
                            title=title,
                            messages=messages,
                            method="first_party_undocumented_json",
                            confidence=0.9,
                            warnings=[
                                "ChatGPT's legacy /backend-api/share route is an "
                                "undocumented implementation detail."
                            ],
                        )
            except Exception as exc:
                legacy_error = str(exc)
            else:
                legacy_error = "legacy share endpoint returned no readable messages"
            raise ExtractorError(
                "ChatGPT public share could not be decoded. "
                f"Page route: {page_error}. Legacy JSON route: {legacy_error}."
            )

        raise ExtractorError(
            "ChatGPT public shared content could not be decoded from the page. "
            f"{page_error}"
        )

    def _share_ref(self, url: str) -> tuple[str, str]:
        parsed = urllib.parse.urlsplit(url)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[0] not in {"share", "s"}:
            raise ExtractorError("Unsupported ChatGPT share URL.")
        share_type = parts[0]
        share_id = parts[1].strip()
        if not _SHARE_ID_RE.fullmatch(share_id):
            raise ExtractorError("ChatGPT share ID is malformed.")
        return share_type, share_id

    def _result(
        self,
        *,
        source_url: str,
        canonical_url: str,
        share_type: str,
        share_id: str,
        title: str,
        messages: list[Message],
        method: str,
        confidence: float,
        warnings: list[str],
    ) -> ExtractedContent:
        return ExtractedContent(
            source_url=source_url,
            canonical_url=canonical_url,
            platform="chatgpt",
            kind="conversation" if share_type == "share" else "shared_content",
            extraction_method=method,
            confidence=confidence,
            title=title or (
                "ChatGPT shared conversation"
                if share_type == "share"
                else "ChatGPT shared content"
            ),
            text="\n\n".join(message.text for message in messages),
            markdown=_render_conversation(messages),
            messages=messages,
            metadata={
                "share_id": share_id,
                "share_type": share_type,
                "endpoint_documentation": "undocumented",
                "reasoning_exported": False,
            },
            warnings=warnings,
        )


def _parse_turbo_stream(page_html: str) -> tuple[str, list[Message]] | None:
    for raw in _STREAM_RE.findall(page_html):
        try:
            pool = json.loads(json.loads(raw))
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        if not isinstance(pool, list) or not pool:
            continue

        data = _hydrate_pool(pool, 0)
        raw_messages = _conversation_messages(data)
        if raw_messages is None:
            continue

        messages = [
            message
            for item in raw_messages
            if (message := _normalize_message(item)) is not None
        ]
        title = _find_key(data, "title")
        return (
            title.strip() if isinstance(title, str) else "",
            messages,
        )
    return None


def _hydrate_pool(pool: list[Any], index: Any, depth: int = 0) -> Any:
    if (
        depth > 100
        or not isinstance(index, int)
        or index < 0
        or index >= len(pool)
    ):
        return None

    value = pool[index]
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for encoded_key, child_index in value.items():
            if not (
                isinstance(encoded_key, str)
                and encoded_key.startswith("_")
                and encoded_key[1:].isdigit()
            ):
                continue
            key_index = int(encoded_key[1:])
            key = pool[key_index] if 0 <= key_index < len(pool) else None
            if isinstance(key, str):
                result[key] = _hydrate_pool(pool, child_index, depth + 1)
        return result

    if isinstance(value, list):
        # React Router turbo-stream uses string-leading arrays for typed markers
        # such as promise/date references rather than ordinary JSON arrays.
        if value and isinstance(value[0], str):
            return None
        return [_hydrate_pool(pool, child, depth + 1) for child in value]

    return value


def _find_key(value: Any, key: str, depth: int = 0) -> Any:
    if depth > 40:
        return None
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = _find_key(child, key, depth + 1)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_key(child, key, depth + 1)
            if found is not None:
                return found
    return None


def _conversation_messages(data: Any) -> list[Any] | None:
    linear = _find_key(data, "linear_conversation")
    if isinstance(linear, list):
        return [
            node.get("message") if isinstance(node, dict) else None
            for node in linear
        ]

    messages = _find_key(data, "messages")
    if isinstance(messages, list):
        return list(messages)

    return None


def _messages_from_legacy_payload(payload: dict[str, Any]) -> list[Message]:
    direct = payload.get("messages")
    if isinstance(direct, list):
        result = [_normalize_message(item) for item in direct]
        return [message for message in result if message is not None]

    mapping = payload.get("mapping")
    if not isinstance(mapping, dict):
        return []

    current = payload.get("current_node")
    ordered_nodes: list[dict[str, Any]] = []
    seen: set[str] = set()

    if isinstance(current, str) and current in mapping:
        cursor: str | None = current
        while cursor and cursor not in seen and cursor in mapping:
            seen.add(cursor)
            node = mapping.get(cursor)
            if not isinstance(node, dict):
                break
            ordered_nodes.append(node)
            parent = node.get("parent")
            cursor = parent if isinstance(parent, str) else None
        ordered_nodes.reverse()
    else:
        ordered_nodes = [
            node for node in mapping.values() if isinstance(node, dict)
        ]
        ordered_nodes.sort(
            key=lambda node: (
                _message_create_time(node.get("message")),
                str(node.get("id") or ""),
            )
        )

    result: list[Message] = []
    for node in ordered_nodes:
        normalized = _normalize_message(node.get("message"))
        if normalized is not None:
            result.append(normalized)
    return result


def _message_create_time(message: Any) -> float:
    if not isinstance(message, dict):
        return 0.0
    value = message.get("create_time")
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _normalize_message(message: Any) -> Message | None:
    if not isinstance(message, dict):
        return None

    author = message.get("author")
    role = ""
    author_name = None
    if isinstance(author, dict):
        role = str(author.get("role") or "")
        author_name = str(author.get("name") or "").strip() or None
    role = (role or str(message.get("role") or "unknown")).lower()

    # Public shares may contain system/tool/developer nodes in their serialized
    # graph. They are implementation context, not part of the public dialogue
    # contract ShareXtract exports.
    if role not in {"user", "assistant"}:
        return None

    content = message.get("content")
    parts: list[str] = []
    if isinstance(content, dict):
        raw_parts = content.get("parts")
        if isinstance(raw_parts, list):
            for part in raw_parts:
                if isinstance(part, str) and part.strip():
                    parts.append(part.strip())
                elif isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
        elif isinstance(content.get("text"), str):
            parts = [content["text"].strip()]
    elif isinstance(content, str) and content.strip():
        parts = [content.strip()]

    if not parts:
        return None

    text = "\n\n".join(_clean_text(part) for part in parts if part)
    if not text.strip():
        return None

    return Message(
        role=role,
        author=author_name,
        text=text.strip(),
        created_at=message.get("create_time"),
    )


def _clean_text(value: str) -> str:
    # Some newer /s/ payloads serialize visible entity labels as private-use
    # marker + JSON tuple + marker. Preserve the visible label, not the marker.
    pattern = re.compile(r"\ue200entity\ue202(\[.*?\])\ue201")

    def replace(match: re.Match[str]) -> str:
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            return ""
        if isinstance(payload, list):
            for item in reversed(payload):
                if isinstance(item, str) and item.strip():
                    return item.strip()
        return ""

    return pattern.sub(replace, value)


def _render_conversation(messages: list[Message]) -> str:
    chunks: list[str] = []
    for message in messages:
        label = "User" if message.role == "user" else "ChatGPT"
        chunks.append(f"## {label}\n\n{message.text}")
    return "\n\n".join(chunks)
