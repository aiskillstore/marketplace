from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Message:
    role: str
    text: str
    author: str | None = None
    created_at: str | float | int | None = None
    attachments: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ExtractedContent:
    source_url: str
    canonical_url: str
    platform: str
    kind: str
    extraction_method: str
    confidence: float
    title: str = ""
    author: str = ""
    text: str = ""
    markdown: str = ""
    html: str = ""
    messages: list[Message] = field(default_factory=list)
    media: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    retrieved_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["messages"] = [m.to_dict() for m in self.messages]
        return data

    @property
    def has_body(self) -> bool:
        return bool(self.text.strip() or self.markdown.strip() or self.messages)
