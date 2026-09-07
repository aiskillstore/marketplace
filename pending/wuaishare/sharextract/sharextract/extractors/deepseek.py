from __future__ import annotations

import re
import urllib.parse

from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


class DeepSeekShareExtractor(Extractor):
    name = "deepseek-share"
    priority = 10

    def supports(self, url: str) -> bool:
        return self.hostname(url) == "chat.deepseek.com" and "/share/" in urllib.parse.urlsplit(url).path

    def extract(self, url: str) -> ExtractedContent:
        parsed = urllib.parse.urlsplit(url)
        share_id = parsed.path.split("/share/", 1)[1].strip("/").split("/", 1)[0]
        if not share_id:
            raise ExtractorError("DeepSeek share ID is missing.")

        endpoint = "https://chat.deepseek.com/api/v0/share/content?" + urllib.parse.urlencode(
            {"share_id": share_id}
        )
        _, payload = self.client.get_json(endpoint, headers={"Accept": "application/json"})
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        biz = data.get("biz_data", {}) if isinstance(data, dict) else {}
        raw_messages = biz.get("messages", []) if isinstance(biz, dict) else []
        if not isinstance(raw_messages, list) or not raw_messages:
            raise ExtractorError("DeepSeek returned no shared messages.")

        messages: list[Message] = []
        for item in raw_messages:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or "unknown").lower()
            content = item.get("content")
            if isinstance(content, str) and content.strip():
                messages.append(
                    Message(
                        role=role,
                        text=content.strip(),
                        created_at=item.get("inserted_at"),
                    )
                )
        if not messages:
            raise ExtractorError("DeepSeek messages had no extractable text.")

        title = str(biz.get("title") or "").strip()
        if not title or title.lower() == "shared conversation":
            for message in messages:
                if message.role == "assistant":
                    match = re.search(r"(?m)^#\s+(.+?)\s*$", message.text)
                    if match:
                        title = match.group(1).strip()
                        break
        if not title:
            title = "DeepSeek shared conversation"

        markdown = _render_conversation(messages)
        text = "\n\n".join(m.text for m in messages)
        return ExtractedContent(
            source_url=url,
            canonical_url=f"https://chat.deepseek.com/share/{share_id}",
            platform="deepseek",
            kind="conversation",
            extraction_method="first_party_public_json",
            confidence=0.99,
            title=title,
            text=text,
            markdown=markdown,
            messages=messages,
            metadata={
                "share_id": share_id,
                "native_endpoint_kind": "first-party public JSON endpoint",
                "endpoint_documentation": "undocumented",
            },
            warnings=[
                "The DeepSeek JSON route is a first-party public endpoint but is not a documented stable API contract."
            ],
        )


def _render_conversation(messages: list[Message]) -> str:
    chunks: list[str] = []
    for message in messages:
        label = {"user": "User", "assistant": "Assistant", "system": "System"}.get(
            message.role, message.role.title()
        )
        chunks.append(f"## {label}\n\n{message.text}")
    return "\n\n".join(chunks)
