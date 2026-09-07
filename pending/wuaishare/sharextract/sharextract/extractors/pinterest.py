from __future__ import annotations

import re
import urllib.parse
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError
from .generic import _PageParser


_PIN_RE = re.compile(
    r"^/pin/(?:[^/]*--)?(?P<pin_id>\d+)/?$",
    re.IGNORECASE,
)


class PinterestPinExtractor(Extractor):
    """Extract a public Pinterest Pin from standard Open Graph metadata."""

    name = "pinterest-pin"
    priority = 37

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        return _is_pinterest_host(host) and _PIN_RE.fullmatch(parsed.path) is not None

    def extract(self, url: str) -> ExtractedContent:
        pin_id = _pin_id(url)
        if not pin_id:
            raise ExtractorError("Pinterest URL is not a supported public Pin URL.")

        response = self.client.get_text(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.8",
            },
        )
        if "text/html" not in response.content_type.lower():
            raise ExtractorError("Pinterest public Pin page did not return HTML.")

        parser = _PageParser()
        try:
            parser.feed(response.text)
            parser.close()
        except Exception as exc:
            raise ExtractorError(
                f"Pinterest public Pin HTML could not be parsed: {exc}"
            ) from exc

        og_type = parser.meta.get("og:type", "").strip().lower()
        title = _first(
            parser.meta.get("og:title"),
            parser.meta.get("twitter:title"),
            " ".join(parser.title_parts).strip(),
        )
        description = _first(
            parser.meta.get("description"),
            parser.meta.get("og:description"),
            parser.meta.get("twitter:description"),
        )
        image_url = _first(
            parser.meta.get("og:image"),
            parser.meta.get("twitter:image:src"),
            parser.meta.get("twitter:image"),
        )

        if og_type and og_type != "pinterestapp:pin":
            raise ExtractorError(
                f"Pinterest page is not a validated Pin surface: og:type={og_type!r}."
            )
        if not title and not description and not image_url:
            raise ExtractorError(
                "Pinterest public Pin page returned no usable Open Graph metadata."
            )

        canonical = f"https://www.pinterest.com/pin/{pin_id}/"
        declared_canonical = _declared_canonical(parser, response.url)
        declared_pin_id = _pin_id(declared_canonical) if declared_canonical else None
        declared_mismatch = bool(
            declared_pin_id
            and declared_pin_id != pin_id
        )
        media: list[dict[str, Any]] = []
        if image_url:
            item: dict[str, Any] = {
                "type": "image",
                "url": image_url,
            }
            width = _int_value(parser.meta.get("og:image:width"))
            height = _int_value(parser.meta.get("og:image:height"))
            if width is not None:
                item["width"] = width
            if height is not None:
                item["height"] = height
            media.append(item)

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="pinterest",
            kind="image_post",
            extraction_method="standard_open_graph_pinterest_pin",
            confidence=0.97,
            title=title,
            text=description or title,
            markdown=description or title,
            media=media,
            metadata={
                "pin_id": pin_id,
                "description": description,
                "updated_at": parser.meta.get("og:updated_time", ""),
                "site_name": parser.meta.get("og:site_name", ""),
                "og_type": parser.meta.get("og:type", ""),
                "declared_canonical_url": declared_canonical,
                "declared_canonical_pin_id": declared_pin_id or "",
                "declared_og_url": parser.meta.get("og:url", ""),
                "declared_canonical_mismatch": declared_mismatch,
                "source_link": parser.meta.get("og:see_also", ""),
                "public_pin_widget_documented": True,
                "uses_internal_pws_state": False,
                "uses_api_token": False,
                "uses_browser": False,
                "endpoint_documentation": (
                    "standard_open_graph_on_documented_public_pin_surface"
                ),
            },
            warnings=[
                "Pinterest Pin metadata is read only from standard Open Graph "
                "fields already present in the anonymous public Pin HTML.",
                "Pinterest may declare a canonical/og:url pointing at a different "
                "Pin ID with different content. ShareXtract therefore keeps the "
                "requested Pin ID as canonical identity and records Pinterest's "
                "declared canonical separately."
                if declared_mismatch
                else "Pinterest declared canonical metadata matches the requested "
                "Pin identity.",
                "ShareXtract does not parse Pinterest internal PWS state, call "
                "undocumented pidgets endpoints, require API tokens, or use a browser.",
            ],
        )


def _declared_canonical(parser: _PageParser, base_url: str) -> str:
    for link in parser.links:
        rel = str(link.get("rel") or "").lower()
        href = str(link.get("href") or "").strip()
        if "canonical" in rel and href:
            return urllib.parse.urljoin(base_url, href)
    return ""


def _is_pinterest_host(host: str) -> bool:
    host = host.lower().strip(".")
    return host == "pinterest.com" or host.endswith(".pinterest.com")


def _pin_id(url: str) -> str | None:
    match = _PIN_RE.fullmatch(urllib.parse.urlsplit(url).path)
    return match.group("pin_id") if match else None


def _first(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _int_value(value: Any) -> int | None:
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None
