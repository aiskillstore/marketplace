from __future__ import annotations

import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


_RPC_ID = "ujx1Bf"
_CANONICAL_HOST = "gemini.google.com"


class GeminiShareExtractor(Extractor):
    """Extract public Gemini share snapshots through Gemini's public share RPC."""

    name = "gemini-share"
    priority = 25

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        path = parsed.path.rstrip("/")
        if host == "gemini.google.com":
            return path.startswith("/share/") and len(path.split("/")) >= 3
        if host == "g.co":
            return path.startswith("/gemini/share/") and len(path.split("/")) >= 4
        if host == "share.gemini.google":
            return bool(path.strip("/"))
        return False

    def extract(self, url: str) -> ExtractedContent:
        share_id, canonical_url = self._resolve_share_id(url)

        inner_request = json.dumps(
            [None, share_id, [4]],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        f_req = json.dumps(
            [[[_RPC_ID, inner_request, None, "generic"]]],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        query = urllib.parse.urlencode(
            {
                "rpcids": _RPC_ID,
                "source-path": f"/share/{share_id}",
                "hl": "en-US",
                "rt": "c",
            }
        )
        endpoint = f"https://{_CANONICAL_HOST}/_/BardChatUi/data/batchexecute?{query}"
        response = self.client.post_form(
            endpoint,
            {"f.req": f_req},
            headers={
                "Accept": "application/json",
                "X-Same-Domain": "1",
                "Referer": f"https://{_CANONICAL_HOST}/",
            },
        )

        payload = _decode_batchexecute(response.text)
        root = _conversation_root(payload)
        messages, turn_metadata, media = _extract_turns(root)

        if not messages:
            raise ExtractorError("Gemini public share returned no readable messages.")

        title = _safe_string(_nested(root, 2, 1)) or "Gemini shared conversation"
        returned_share_id = _safe_string(_nested(root, 3))
        if returned_share_id and returned_share_id != share_id:
            raise ExtractorError("Gemini share response ID did not match the requested share.")

        published_at = _timestamp(_nested(root, 4))
        model_info = _nested(root, 2, 7)
        model_label = _safe_string(_nested(model_info, 2))
        model_id = _safe_string(_nested(model_info, 1))

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical_url,
            platform="gemini",
            kind="conversation",
            extraction_method="first_party_undocumented_public_rpc",
            confidence=0.97,
            title=title,
            text="\n\n".join(message.text for message in messages),
            markdown=_render_conversation(messages),
            messages=messages,
            media=media,
            metadata={
                "share_id": share_id,
                "published_at": published_at,
                "model_id": model_id,
                "model_label": model_label,
                "turns": turn_metadata,
                "rpc_id": _RPC_ID,
                "endpoint_documentation": "undocumented",
            },
            warnings=[
                "Gemini's public share RPC is first-party and unauthenticated, "
                "but it is an undocumented frontend implementation detail and may change."
            ],
        )

    def _resolve_share_id(self, url: str) -> tuple[str, str]:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        parts = [part for part in parsed.path.split("/") if part]

        if host == _CANONICAL_HOST and len(parts) >= 2 and parts[0] == "share":
            share_id = parts[1]
        elif host == "g.co" and len(parts) >= 3 and parts[0:2] == ["gemini", "share"]:
            share_id = parts[2]
        elif host == "share.gemini.google":
            resolved = self.client.resolve(
                url,
                headers={"Accept": "text/html", "Referer": f"https://{_CANONICAL_HOST}/"},
            )
            resolved_parsed = urllib.parse.urlsplit(resolved)
            resolved_parts = [part for part in resolved_parsed.path.split("/") if part]
            if (
                (resolved_parsed.hostname or "").lower() != _CANONICAL_HOST
                or len(resolved_parts) < 2
                or resolved_parts[0] != "share"
            ):
                raise ExtractorError("Gemini short link did not resolve to a public share page.")
            share_id = resolved_parts[1]
        else:
            raise ExtractorError("Unsupported Gemini share URL.")

        if not re.fullmatch(r"[A-Za-z0-9_-]{6,128}", share_id):
            raise ExtractorError("Gemini share ID is malformed.")
        return share_id, f"https://{_CANONICAL_HOST}/share/{share_id}"


def _decode_batchexecute(text: str) -> Any:
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("[["):
            continue
        try:
            outer = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(outer, list):
            continue
        for row in outer:
            if (
                isinstance(row, list)
                and len(row) >= 3
                and row[0] == "wrb.fr"
                and row[1] == _RPC_ID
                and isinstance(row[2], str)
            ):
                try:
                    return json.loads(row[2])
                except json.JSONDecodeError as exc:
                    raise ExtractorError("Gemini share RPC contained invalid nested JSON.") from exc
    raise ExtractorError("Gemini share RPC response did not contain the expected payload.")


def _conversation_root(payload: Any) -> list[Any]:
    root = _nested(payload, 0)
    if not isinstance(root, list) or len(root) < 4:
        raise ExtractorError("Gemini public share payload shape is unsupported.")
    if not isinstance(_nested(root, 1), list):
        raise ExtractorError("Gemini public share payload contained no turns.")
    return root


def _extract_turns(root: list[Any]) -> tuple[list[Message], list[dict[str, Any]], list[dict[str, Any]]]:
    messages: list[Message] = []
    turn_metadata: list[dict[str, Any]] = []
    media: list[dict[str, Any]] = []
    seen_media: set[str] = set()

    turns = _nested(root, 1)
    if not isinstance(turns, list):
        return messages, turn_metadata, media

    for turn_index, turn in enumerate(turns):
        if not isinstance(turn, list):
            continue

        ids = _nested(turn, 0)
        conversation_id = _safe_string(_nested(ids, 0))
        response_id = _safe_string(_nested(ids, 1))
        created_at = _timestamp(_nested(turn, 4))

        prompt = _nested(turn, 2)
        user_text = _join_text_parts(_nested(prompt, 0))
        if user_text:
            messages.append(
                Message(
                    role="user",
                    text=_clean_text(user_text),
                    created_at=created_at,
                )
            )

        response = _nested(turn, 3)
        assistant_text = _assistant_text(response)
        if assistant_text:
            messages.append(
                Message(
                    role="assistant",
                    text=_clean_text(assistant_text),
                    created_at=created_at,
                )
            )

        turn_metadata.append(
            {
                "index": turn_index,
                "conversation_id": conversation_id,
                "response_id": response_id,
                "created_at": created_at,
            }
        )

        for item in _media_from_value(turn):
            url = item["url"]
            if url not in seen_media:
                seen_media.add(url)
                media.append(item)

    return messages, turn_metadata, media


def _assistant_text(response: Any) -> str:
    candidates = _nested(response, 0)
    if not isinstance(candidates, list):
        return ""
    for candidate in candidates:
        if not isinstance(candidate, list):
            continue
        parts = _nested(candidate, 1)
        value = _join_text_parts(parts)
        if value:
            return value
    return ""


def _join_text_parts(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if not isinstance(value, list):
        return ""
    parts: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            parts.append(item.strip())
    return "\n\n".join(parts)


def _clean_text(value: str) -> str:
    return value.replace("\u200b", "").strip()


def _timestamp(value: Any) -> str | None:
    if not isinstance(value, list) or not value:
        return None
    seconds = value[0]
    nanos = value[1] if len(value) > 1 else 0
    if not isinstance(seconds, (int, float)):
        return None
    try:
        moment = float(seconds) + (float(nanos) / 1_000_000_000 if isinstance(nanos, (int, float)) else 0)
        return datetime.fromtimestamp(moment, timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _media_from_value(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def visit(node: Any) -> None:
        if isinstance(node, list):
            for child in node:
                visit(child)
            return
        if isinstance(node, dict):
            for child in node.values():
                visit(child)
            return
        if not isinstance(node, str) or not node.startswith(("http://", "https://")):
            return
        lowered = node.lower()
        if "googleusercontent.com" in lowered or re.search(r"\.(?:png|jpe?g|webp|gif)(?:[?#]|$)", lowered):
            found.append({"type": "image", "url": node})
        elif re.search(r"\.(?:mp4|webm)(?:[?#]|$)", lowered):
            found.append({"type": "video", "url": node})

    visit(value)
    return found


def _render_conversation(messages: list[Message]) -> str:
    chunks: list[str] = []
    for message in messages:
        label = "User" if message.role == "user" else "Gemini"
        chunks.append(f"## {label}\n\n{message.text}")
    return "\n\n".join(chunks)


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _nested(value: Any, *indexes: int) -> Any:
    current = value
    for index in indexes:
        if not isinstance(current, list) or index < 0 or index >= len(current):
            return None
        current = current[index]
    return current
