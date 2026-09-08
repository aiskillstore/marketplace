from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin

from sharextract.models import ExtractedContent

from .extractors.base import ExtractorError


_XML_CONTENT_TYPES = (
    "application/rss+xml",
    "application/atom+xml",
    "application/xml",
    "text/xml",
    "application/rdf+xml",
)


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._ignore_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self._ignore_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self._ignore_depth:
            self._ignore_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignore_depth:
            return
        self.parts.append(data)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()


def try_extract_syndication_feed(
    source_url: str,
    final_url: str,
    content_type: str,
    raw: str,
) -> ExtractedContent | None:
    """Return a normalized RSS/Atom result when *raw* is a public feed."""
    if not _looks_xmlish(content_type, raw):
        return None

    prefix = raw[:8192].lower()
    if "<!doctype" in prefix or "<!entity" in prefix:
        raise ExtractorError(
            "XML feed contains a DTD/entity declaration and was rejected."
        )

    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None

    root_name = _local_name(root.tag).lower()
    if root_name == "rss":
        return _extract_rss(source_url, final_url, root)
    if root_name == "feed":
        return _extract_atom(source_url, final_url, root)
    if root_name == "rdf":
        return _extract_rdf_rss(source_url, final_url, root)
    return None


def _looks_xmlish(content_type: str, raw: str) -> bool:
    ctype = (content_type or "").lower()
    if any(token in ctype for token in _XML_CONTENT_TYPES):
        return True
    stripped = raw.lstrip()[:200].lower()
    return stripped.startswith(
        ("<?xml", "<rss", "<feed", "<rdf:rdf", "<rdf")
    )


def _extract_rss(
    source_url: str,
    final_url: str,
    root: ET.Element,
) -> ExtractedContent:
    channel = _child(root, "channel")
    if channel is None:
        raise ExtractorError("RSS feed did not contain a channel element.")

    title = _text(channel, "title")
    home_url = _text(channel, "link")
    description = _html_text(_text(channel, "description"))
    author = _first(
        _text(channel, "managingEditor"),
        _text(channel, "webMaster"),
        _text_ns(channel, "creator"),
    )
    updated = _normalize_date(
        _first(
            _text(channel, "lastBuildDate"),
            _text(channel, "pubDate"),
        )
    )

    entries = [
        _rss_item(item, final_url)
        for item in _children(channel, "item")
    ]
    entries = [entry for entry in entries if entry]

    feed_url = urljoin(
        final_url,
        _atom_self_link(channel) or final_url,
    )
    home_url = urljoin(final_url, home_url) if home_url else ""
    media = _feed_media(entries)
    return _build_result(
        source_url=source_url,
        final_url=final_url,
        platform="rss",
        method="standard_rss",
        title=title,
        author=author,
        description=description,
        home_url=home_url,
        feed_url=feed_url,
        updated=updated,
        language=_text(channel, "language"),
        entries=entries,
        media=media,
        metadata_extra={
            "generator": _text(channel, "generator"),
            "copyright": _text(channel, "copyright"),
        },
    )


def _extract_rdf_rss(
    source_url: str,
    final_url: str,
    root: ET.Element,
) -> ExtractedContent:
    channel = next(
        (child for child in list(root) if _local_name(child.tag) == "channel"),
        None,
    )
    if channel is None:
        raise ExtractorError("RSS 1.0 feed did not contain a channel element.")

    entries = [
        _rss_item(item, final_url)
        for item in list(root)
        if _local_name(item.tag) == "item"
    ]
    entries = [entry for entry in entries if entry]
    return _build_result(
        source_url=source_url,
        final_url=final_url,
        platform="rss",
        method="standard_rss",
        title=_text(channel, "title"),
        author=_text_ns(channel, "creator"),
        description=_html_text(_text(channel, "description")),
        home_url=_text(channel, "link"),
        feed_url=final_url,
        updated=_normalize_date(_text_ns(channel, "date")),
        language=_text_ns(channel, "language"),
        entries=entries,
        media=_feed_media(entries),
        metadata_extra={"rss_version": "1.0"},
    )


def _rss_item(item: ET.Element, base_url: str) -> dict[str, Any]:
    link = _text(item, "link")
    guid = _text(item, "guid")
    title = _text(item, "title")
    description = _html_text(_text(item, "description"))
    content = _html_text(_text_ns(item, "encoded"))
    author = _first(
        _text_ns(item, "creator"),
        _text(item, "author"),
    )
    published = _normalize_date(
        _first(
            _text(item, "pubDate"),
            _text_ns(item, "date"),
        )
    )
    categories = [
        value
        for element in _children(item, "category")
        if (value := _element_text(element))
    ]
    media = _rss_enclosures(item, base_url)

    if not any((title, link, guid, description, content)):
        return {}
    return {
        "id": guid or link,
        "title": title,
        "url": urljoin(base_url, link) if link else "",
        "author": author,
        "published_at": published,
        "updated_at": "",
        "summary": description,
        "text": content or description,
        "categories": categories,
        "media": media,
    }


def _extract_atom(
    source_url: str,
    final_url: str,
    root: ET.Element,
) -> ExtractedContent:
    title = _text(root, "title")
    subtitle = _html_text(_text(root, "subtitle"))
    author = _atom_author(root)
    home_url = _atom_link(root, "alternate")
    home_url = urljoin(final_url, home_url) if home_url else ""
    feed_url = urljoin(
        final_url,
        _atom_link(root, "self") or final_url,
    )
    updated = _normalize_date(_text(root, "updated"))

    entries = [
        _atom_entry(entry, final_url)
        for entry in _children(root, "entry")
    ]
    entries = [entry for entry in entries if entry]
    return _build_result(
        source_url=source_url,
        final_url=final_url,
        platform="atom",
        method="standard_atom",
        title=title,
        author=author,
        description=subtitle,
        home_url=home_url,
        feed_url=feed_url,
        updated=updated,
        language=_xml_lang(root),
        entries=entries,
        media=_feed_media(entries),
        metadata_extra={
            "id": _text(root, "id"),
            "rights": _text(root, "rights"),
        },
    )


def _atom_entry(entry: ET.Element, base_url: str) -> dict[str, Any]:
    title = _html_text(_text(entry, "title"))
    link = _atom_link(entry, "alternate")
    entry_id = _text(entry, "id")
    author = _atom_author(entry)
    published = _normalize_date(
        _first(
            _text(entry, "published"),
            _text(entry, "issued"),
        )
    )
    updated = _normalize_date(_text(entry, "updated"))
    summary = _html_text(_text(entry, "summary"))
    content = _html_text(_text(entry, "content"))
    categories = []
    for category in _children(entry, "category"):
        term = category.attrib.get("term") or _element_text(category)
        if term:
            categories.append(term)

    media: list[dict[str, Any]] = []
    for link_element in _children(entry, "link"):
        if (link_element.attrib.get("rel") or "").lower() != "enclosure":
            continue
        href = link_element.attrib.get("href")
        if not href:
            continue
        item: dict[str, Any] = {
            "type": _media_type(link_element.attrib.get("type")),
            "url": urljoin(base_url, href),
        }
        if link_element.attrib.get("type"):
            item["mime_type"] = link_element.attrib["type"]
        length = _int_value(link_element.attrib.get("length"))
        if length is not None:
            item["length_bytes"] = length
        media.append(item)

    if not any((title, link, entry_id, summary, content)):
        return {}
    return {
        "id": entry_id or link,
        "title": title,
        "url": urljoin(base_url, link) if link else "",
        "author": author,
        "published_at": published,
        "updated_at": updated,
        "summary": summary,
        "text": content or summary,
        "categories": categories,
        "media": media,
    }


def _build_result(
    *,
    source_url: str,
    final_url: str,
    platform: str,
    method: str,
    title: str,
    author: str,
    description: str,
    home_url: str,
    feed_url: str,
    updated: str,
    language: str,
    entries: list[dict[str, Any]],
    media: list[dict[str, Any]],
    metadata_extra: dict[str, Any],
) -> ExtractedContent:
    text = _render_feed_text(description, entries)
    metadata = {
        "feed": {
            "title": title,
            "home_url": home_url,
            "feed_url": feed_url,
            "description": description,
            "author": author,
            "updated_at": updated,
            "language": language,
            "entry_count": len(entries),
            "entries": entries,
        },
        "standard": "RSS" if platform == "rss" else "Atom",
        **{
            key: value
            for key, value in metadata_extra.items()
            if value not in ("", None)
        },
    }
    return ExtractedContent(
        source_url=source_url,
        canonical_url=feed_url or final_url,
        platform=platform,
        kind="feed",
        extraction_method=method,
        confidence=0.99,
        title=title,
        author=author,
        text=text,
        markdown=_render_feed_markdown(title, description, entries),
        media=media,
        metadata=metadata,
    )


def _render_feed_text(
    description: str,
    entries: list[dict[str, Any]],
) -> str:
    chunks = [description] if description else []
    for entry in entries:
        title = str(entry.get("title") or "").strip()
        body = str(
            entry.get("text")
            or entry.get("summary")
            or ""
        ).strip()
        if title and body:
            chunks.append(f"{title}\n{body}")
        elif title or body:
            chunks.append(title or body)
    return "\n\n".join(chunks)


def _render_feed_markdown(
    title: str,
    description: str,
    entries: list[dict[str, Any]],
) -> str:
    chunks: list[str] = []
    if title:
        chunks.append(f"# {title}")
    if description:
        chunks.append(description)

    for entry in entries:
        entry_title = str(entry.get("title") or "").strip() or "Untitled"
        entry_url = str(entry.get("url") or "").strip()
        heading = (
            f"## [{entry_title}]({entry_url})"
            if entry_url
            else f"## {entry_title}"
        )
        parts = [heading]
        meta = []
        if entry.get("author"):
            meta.append(str(entry["author"]))
        if entry.get("published_at") or entry.get("updated_at"):
            meta.append(
                str(entry.get("published_at") or entry.get("updated_at"))
            )
        if meta:
            parts.append(" · ".join(meta))
        body = str(
            entry.get("text")
            or entry.get("summary")
            or ""
        ).strip()
        if body:
            parts.append(body)
        chunks.append("\n\n".join(parts))

    return "\n\n".join(chunks)


def _feed_media(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    media: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        for item in entry.get("media") or []:
            if not isinstance(item, dict):
                continue
            url = item.get("url")
            if not isinstance(url, str) or not url or url in seen:
                continue
            seen.add(url)
            enriched = dict(item)
            enriched["entry_index"] = index
            if entry.get("title"):
                enriched["entry_title"] = entry["title"]
            media.append(enriched)
    return media


def _rss_enclosures(item: ET.Element, base_url: str) -> list[dict[str, Any]]:
    media: list[dict[str, Any]] = []
    seen: set[str] = set()

    for enclosure in _children(item, "enclosure"):
        url = enclosure.attrib.get("url")
        if not url:
            continue
        full = urljoin(base_url, html.unescape(url))
        if full in seen:
            continue
        seen.add(full)
        value: dict[str, Any] = {
            "type": _media_type(enclosure.attrib.get("type")),
            "url": full,
        }
        mime = enclosure.attrib.get("type")
        if mime:
            value["mime_type"] = mime
        length = _int_value(enclosure.attrib.get("length"))
        if length is not None:
            value["length_bytes"] = length
        media.append(value)

    # Media RSS: content/thumbnail commonly expose public media references.
    for element in item.iter():
        name = _local_name(element.tag).lower()
        namespace = _namespace(element.tag)
        if name not in {"content", "thumbnail"}:
            continue
        if "search.yahoo.com/mrss" not in namespace:
            continue
        url = element.attrib.get("url")
        if not url:
            continue
        full = urljoin(base_url, html.unescape(url))
        if full in seen:
            continue
        seen.add(full)
        media.append(
            {
                "type": (
                    "thumbnail"
                    if name == "thumbnail"
                    else _media_type(element.attrib.get("type"))
                ),
                "url": full,
                **(
                    {"mime_type": element.attrib["type"]}
                    if element.attrib.get("type")
                    else {}
                ),
            }
        )
    return media


def _atom_author(element: ET.Element) -> str:
    author = _child(element, "author")
    if author is None:
        return ""
    return _first(
        _text(author, "name"),
        _text(author, "email"),
        _element_text(author),
    )


def _atom_link(element: ET.Element, rel: str) -> str:
    fallback = ""
    for link in _children(element, "link"):
        href = (link.attrib.get("href") or "").strip()
        if not href:
            continue
        link_rel = (link.attrib.get("rel") or "alternate").lower()
        if not fallback:
            fallback = href
        if link_rel == rel:
            return href
    return fallback if rel == "alternate" else ""


def _atom_self_link(element: ET.Element) -> str:
    for link in element.iter():
        if _local_name(link.tag) != "link":
            continue
        if (link.attrib.get("rel") or "").lower() != "self":
            continue
        href = (link.attrib.get("href") or "").strip()
        if href:
            return href
    return ""


def _child(element: ET.Element, local_name: str) -> ET.Element | None:
    return next(
        (
            child
            for child in list(element)
            if _local_name(child.tag) == local_name
        ),
        None,
    )


def _children(element: ET.Element, local_name: str) -> list[ET.Element]:
    return [
        child
        for child in list(element)
        if _local_name(child.tag) == local_name
    ]


def _text(element: ET.Element, local_name: str) -> str:
    child = _child(element, local_name)
    return _element_text(child) if child is not None else ""


def _text_ns(element: ET.Element, local_name: str) -> str:
    for child in list(element):
        if _local_name(child.tag) == local_name:
            value = _element_text(child)
            if value:
                return value
    return ""


def _element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def _html_text(value: str) -> str:
    if not value:
        return ""
    parser = _TextHTMLParser()
    try:
        parser.feed(html.unescape(value))
        parser.close()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html.unescape(value)).strip()
    return parser.text


def _normalize_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""

    try:
        dt = parsedate_to_datetime(value)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        pass

    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except ValueError:
        return value


def _xml_lang(element: ET.Element) -> str:
    return (
        element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
        or element.attrib.get("lang")
        or ""
    )


def _namespace(tag: str) -> str:
    if isinstance(tag, str) and tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return ""


def _local_name(tag: Any) -> str:
    if not isinstance(tag, str):
        return ""
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    if ":" in tag:
        return tag.rsplit(":", 1)[1]
    return tag


def _media_type(mime_type: Any) -> str:
    mime = str(mime_type or "").lower()
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("audio/"):
        return "audio"
    if mime.startswith("video/"):
        return "video"
    return "enclosure"


def _int_value(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _first(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""
