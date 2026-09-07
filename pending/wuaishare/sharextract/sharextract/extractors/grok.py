from __future__ import annotations

import re
import urllib.parse
from typing import Any

from sharextract.browser import (
    BrowserFetchError,
    BrowserUnavailable,
    fetch_public_json_response,
)
from sharextract.http import FetchError
from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,256}$")


class GrokShareExtractor(Extractor):
    """Extract public Grok shares without importing account/session state."""

    name = "grok-share"
    priority = 27

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = self.hostname(url)
        parts = [part for part in parsed.path.split("/") if part]
        if host == "grok.com":
            return len(parts) >= 2 and parts[0] == "share"
        if host in {"x.com", "twitter.com"}:
            return len(parts) >= 4 and parts[:3] == ["i", "grok", "share"]
        return False

    def extract(self, url: str) -> ExtractedContent:
        share_id = self._share_id(url)
        payload: Any | None = None
        method = ""
        confidence = 0.0
        warnings: list[str] = []

        endpoint = (
            "https://grok.com/rest/app-chat/share_links_data/"
            + urllib.parse.quote(share_id, safe="")
        )
        try:
            _, direct_payload = self.client.get_json(
                endpoint,
                headers={
                    "Accept": "application/json",
                    "Referer": "https://grok.com/",
                },
            )
            if _find_items(direct_payload):
                payload = direct_payload
                method = "first_party_undocumented_public_json"
                confidence = 0.98
        except FetchError as exc:
            warnings.append(
                "Grok's direct public share-data route was unavailable to the standard "
                f"HTTP client ({exc}); trying the anonymous X public-page transport."
            )

        if payload is None:
            x_url = f"https://x.com/i/grok/share/{share_id}"
            try:
                payload = self._extract_via_x_browser(x_url)
            except BrowserUnavailable as exc:
                raise ExtractorError(str(exc)) from exc
            except BrowserFetchError as exc:
                raise ExtractorError(str(exc)) from exc
            method = "public_browser_first_party_graphql"
            confidence = 0.94
            warnings.append(
                "Grok data was read from the first-party GrokShare GraphQL response generated "
                "by an anonymous public X page. No account cookies or imported session state were used."
            )

        items = _find_items(payload)
        if not items:
            raise ExtractorError("Grok public share returned no readable conversation items.")

        messages, item_metadata = _normalize_items(items)
        if not messages:
            raise ExtractorError("Grok public share items had no extractable messages.")

        return ExtractedContent(
            source_url=url,
            canonical_url=f"https://grok.com/share/{share_id}",
            platform="grok",
            kind="conversation",
            extraction_method=method,
            confidence=confidence,
            title=_title_from_messages(messages),
            text="\n\n".join(message.text for message in messages),
            markdown=_render_conversation(messages),
            messages=messages,
            metadata={
                "share_id": share_id,
                "items": item_metadata,
                "endpoint_documentation": "undocumented",
                "browser_public_only": method == "public_browser_first_party_graphql",
            },
            warnings=warnings,
        )

    def _extract_via_x_browser(self, url: str) -> Any:
        return fetch_public_json_response(
            url,
            response_matcher=lambda response_url: (
                "api.x.com/graphql/" in response_url
                and "/GrokShare?" in response_url
            ),
            timeout=getattr(self.client, "timeout", 20.0),
        )

    def _share_id(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        host = self.hostname(url)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]

        if host == "grok.com" and len(parts) >= 2 and parts[0] == "share":
            share_id = parts[1]
        elif (
            host in {"x.com", "twitter.com"}
            and len(parts) >= 4
            and parts[:3] == ["i", "grok", "share"]
        ):
            share_id = parts[3]
        else:
            raise ExtractorError("Unsupported Grok share URL.")

        if not _ID_RE.fullmatch(share_id):
            raise ExtractorError("Grok share ID is malformed.")
        return share_id


def _find_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        items = value.get("items")
        if isinstance(items, list):
            normalized = [item for item in items if isinstance(item, dict)]
            if normalized and any(
                "message" in item and "sender" in item for item in normalized
            ):
                return normalized
        for child in value.values():
            found = _find_items(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_items(child)
            if found:
                return found
    return []


def _normalize_items(
    items: list[dict[str, Any]],
) -> tuple[list[Message], list[dict[str, Any]]]:
    messages: list[Message] = []
    metadata: list[dict[str, Any]] = []

    for index, item in enumerate(items):
        text = item.get("message")
        if not isinstance(text, str) or not text.strip():
            continue
        sender = str(item.get("sender") or "").strip()
        role = {
            "user": "user",
            "human": "user",
            "agent": "assistant",
            "assistant": "assistant",
            "grok": "assistant",
            "system": "system",
        }.get(sender.lower(), sender.lower() or "unknown")

        messages.append(Message(role=role, text=text.strip()))
        metadata.append(
            {
                "index": index,
                "sender": sender,
                "deepsearch_headers": item.get("deepsearch_headers")
                if isinstance(item.get("deepsearch_headers"), list)
                else [],
            }
        )

    return messages, metadata


def _title_from_messages(messages: list[Message]) -> str:
    for message in messages:
        if message.role != "user":
            continue
        first = next(
            (line.strip() for line in message.text.splitlines() if line.strip()),
            "",
        )
        if first:
            return first if len(first) <= 100 else first[:97].rstrip() + "..."
    return "Grok shared conversation"


def _render_conversation(messages: list[Message]) -> str:
    chunks: list[str] = []
    for message in messages:
        label = {
            "user": "User",
            "assistant": "Grok",
            "system": "System",
        }.get(message.role, message.role.title())
        chunks.append(f"## {label}\n\n{message.text}")
    return "\n\n".join(chunks)
