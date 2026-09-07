from __future__ import annotations

import importlib.util
import json
import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlsplit

from sharextract.feeds import try_extract_syndication_feed
from sharextract.models import ExtractedContent
from sharextract.subtitles import try_extract_timed_text

from .base import Extractor, ExtractorError


_BLOCK_TAGS = {
    "p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote",
    "pre", "figcaption", "dt", "dd",
}
_IGNORE_TAGS = {"script", "style", "noscript", "svg", "canvas", "template"}
_BOILERPLATE_TAGS = {"nav", "header", "footer", "aside"}


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.meta: dict[str, str] = {}
        self.links: list[dict[str, str]] = []
        self.tracks: list[dict[str, Any]] = []
        self.jsonld: list[Any] = []
        self.article_chunks: list[str] = []
        self.body_chunks: list[str] = []
        self._tag_stack: list[str] = []
        self._ignore_depth = 0
        self._boilerplate_depth = 0
        self._article_depth = 0
        self._in_title = False
        self._current_block_tag: str | None = None
        self._current_block_parts: list[str] = []
        self._jsonld_depth = 0
        self._jsonld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        attr = {str(k).lower(): str(v) for k, v in attrs if k and v is not None}
        self._tag_stack.append(tag)

        if tag in _IGNORE_TAGS:
            self._ignore_depth += 1
        if tag in _BOILERPLATE_TAGS:
            self._boilerplate_depth += 1
        if tag in {"article", "main"}:
            self._article_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = (attr.get("property") or attr.get("name") or attr.get("itemprop") or "").strip().lower()
            value = attr.get("content", "").strip()
            if key and value and key not in self.meta:
                self.meta[key] = value
        if tag == "link":
            rel = attr.get("rel", "").strip().lower()
            href = attr.get("href", "").strip()
            typ = attr.get("type", "").strip().lower()
            if href:
                self.links.append({"rel": rel, "href": href, "type": typ})
        if tag == "track":
            src = attr.get("src", "").strip()
            kind = attr.get("kind", "subtitles").strip().lower()
            if src and kind in {"captions", "subtitles", "descriptions"}:
                self.tracks.append(
                    {
                        "kind": kind,
                        "src": src,
                        "srclang": attr.get("srclang", "").strip(),
                        "label": attr.get("label", "").strip(),
                        "default": any(
                            str(key).lower() == "default"
                            for key, _ in attrs
                        ),
                    }
                )
        if tag == "script" and attr.get("type", "").lower().split(";", 1)[0].strip() == "application/ld+json":
            self._jsonld_depth = 1
            self._jsonld_parts = []
        elif self._jsonld_depth and tag == "script":
            self._jsonld_depth += 1

        if tag in _BLOCK_TAGS and not self._ignore_depth:
            self._flush_block()
            self._current_block_tag = tag
            self._current_block_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _BLOCK_TAGS and self._current_block_tag == tag:
            self._flush_block()

        if tag == "script" and self._jsonld_depth:
            self._jsonld_depth -= 1
            if self._jsonld_depth == 0:
                raw = "".join(self._jsonld_parts).strip()
                if raw:
                    try:
                        self.jsonld.append(json.loads(raw))
                    except json.JSONDecodeError:
                        pass
                self._jsonld_parts = []

        if tag == "title":
            self._in_title = False
        if tag in {"article", "main"} and self._article_depth:
            self._article_depth -= 1
        if tag in _BOILERPLATE_TAGS and self._boilerplate_depth:
            self._boilerplate_depth -= 1
        if tag in _IGNORE_TAGS and self._ignore_depth:
            self._ignore_depth -= 1

        if self._tag_stack:
            if self._tag_stack[-1] == tag:
                self._tag_stack.pop()
            elif tag in self._tag_stack:
                idx = len(self._tag_stack) - 1 - self._tag_stack[::-1].index(tag)
                del self._tag_stack[idx:]

    def handle_data(self, data: str) -> None:
        if self._jsonld_depth:
            self._jsonld_parts.append(data)
            return
        if self._ignore_depth:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        if self._current_block_tag and not self._boilerplate_depth:
            self._current_block_parts.append(text)

    def close(self) -> None:
        self._flush_block()
        super().close()

    def _flush_block(self) -> None:
        if not self._current_block_parts:
            self._current_block_tag = None
            return
        text = " ".join(self._current_block_parts).strip()
        if text:
            self.body_chunks.append(text)
            if self._article_depth:
                self.article_chunks.append(text)
        self._current_block_tag = None
        self._current_block_parts = []


class GenericWebExtractor(Extractor):
    name = "generic-web"
    priority = 1000

    def supports(self, url: str) -> bool:
        return urlsplit(url).scheme in {"http", "https"}

    def extract(self, url: str) -> ExtractedContent:
        response = self.client.get_text(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.7"
            },
        )
        ctype = response.content_type.lower()
        if "json" in ctype or response.text.lstrip().startswith(("{", "[")):
            return _extract_json_document(url, response.url, response.text)

        timed_text_result = try_extract_timed_text(
            url,
            response.url,
            response.content_type,
            response.text,
        )
        if timed_text_result is not None:
            return timed_text_result

        feed_result = try_extract_syndication_feed(
            url,
            response.url,
            response.content_type,
            response.text,
        )
        if feed_result is not None:
            return feed_result

        parser = _PageParser()
        try:
            parser.feed(response.text)
            parser.close()
        except Exception as exc:
            raise ExtractorError(f"HTML parsing failed: {exc}") from exc

        canonical = _canonical_url(parser, response.url)
        oembed = self._read_oembed(parser, response.url)
        jsonld = _flatten_jsonld(parser.jsonld)

        title = _first(
            oembed.get("title"),
            parser.meta.get("og:title"),
            parser.meta.get("twitter:title"),
            _jsonld_value(jsonld, "headline", "name"),
            " ".join(parser.title_parts).strip(),
        )
        author = _first(
            oembed.get("author_name"),
            parser.meta.get("author"),
            _jsonld_author(jsonld),
        )
        description = _first(
            parser.meta.get("description"),
            parser.meta.get("og:description"),
            parser.meta.get("twitter:description"),
            _jsonld_value(jsonld, "description"),
        )

        main_chunks = parser.article_chunks if len(" ".join(parser.article_chunks)) >= 200 else parser.body_chunks
        text = "\n\n".join(_dedupe_chunks(main_chunks)).strip()

        trafilatura_markdown = _try_trafilatura(response.text, response.url)
        markdown = trafilatura_markdown or text
        if not text and trafilatura_markdown:
            text = _markdown_to_plain(trafilatura_markdown)
        if not text:
            text = description

        media = _collect_media(parser, oembed, jsonld, response.url)
        platform = _platform_from_host(urlsplit(response.url).hostname or "")
        method = "html_structured"
        if oembed:
            method = "oembed_plus_html"
        elif jsonld:
            method = "jsonld_plus_html"
        if trafilatura_markdown:
            method += "_trafilatura"

        confidence = 0.88 if text and len(text) >= 300 else 0.72 if text else 0.45
        warnings: list[str] = []
        if not text:
            warnings.append("No substantial readable body was found; metadata may be the only available public content.")

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform=platform,
            kind=_infer_kind(oembed, jsonld, parser.meta),
            extraction_method=method,
            confidence=confidence,
            title=title,
            author=author,
            text=text,
            markdown=markdown,
            html=str(oembed.get("html") or ""),
            media=media,
            metadata={
                "description": description,
                "published_at": _jsonld_value(jsonld, "datePublished", "dateCreated"),
                "modified_at": _jsonld_value(jsonld, "dateModified"),
                "site_name": parser.meta.get("og:site_name", ""),
                "oembed": {k: v for k, v in oembed.items() if k != "html"},
                "jsonld_types": sorted(_jsonld_types(jsonld)),
                "syndication_feeds": _collect_syndication_feeds(
                    parser,
                    response.url,
                ),
                "subtitle_tracks": _collect_subtitle_tracks(
                    parser,
                    response.url,
                ),
            },
            warnings=warnings,
        )

    def _read_oembed(self, parser: _PageParser, base_url: str) -> dict[str, Any]:
        for link in parser.links:
            if "alternate" not in link.get("rel", ""):
                continue
            typ = link.get("type", "")
            if typ not in {"application/json+oembed", "text/json+oembed"}:
                continue
            endpoint = urljoin(base_url, link["href"])
            try:
                _, payload = self.client.get_json(
                    endpoint, headers={"Accept": "application/json"}
                )
            except Exception:
                continue
            if isinstance(payload, dict):
                return payload
        return {}


def _collect_subtitle_tracks(
    parser: _PageParser,
    base_url: str,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for track in parser.tracks:
        src = track.get("src")
        kind = track.get("kind")
        if not isinstance(src, str) or not src:
            continue
        resolved = urljoin(base_url, src)
        key = (str(kind or ""), resolved)
        if key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "kind": str(kind or "subtitles"),
                "url": resolved,
                "language": str(track.get("srclang") or ""),
                "label": str(track.get("label") or ""),
                "default": bool(track.get("default")),
            }
        )
    return result


def _collect_syndication_feeds(
    parser: _PageParser,
    base_url: str,
) -> list[dict[str, str]]:
    supported = {
        "application/rss+xml": "rss",
        "application/atom+xml": "atom",
    }
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for link in parser.links:
        rel_tokens = {
            token.strip().lower()
            for token in link.get("rel", "").split()
            if token.strip()
        }
        if "alternate" not in rel_tokens:
            continue
        feed_type = supported.get(link.get("type", "").lower())
        if not feed_type:
            continue
        href = link.get("href", "").strip()
        if not href:
            continue
        resolved = urljoin(base_url, href)
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append({"type": feed_type, "url": resolved})
    return result


def _extract_json_document(source_url: str, final_url: str, raw: str) -> ExtractedContent:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ExtractorError("Response looked like JSON but was invalid.") from exc

    title = ""
    author = ""
    text = ""
    if isinstance(payload, dict):
        title = str(payload.get("title") or payload.get("name") or "").strip()
        author_value = payload.get("author")
        if isinstance(author_value, str):
            author = author_value.strip()
        for key in ("text", "content", "body", "description", "summary"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                text = value.strip()
                break

    pretty = json.dumps(payload, ensure_ascii=False, indent=2)
    return ExtractedContent(
        source_url=source_url,
        canonical_url=final_url,
        platform=_platform_from_host(urlsplit(final_url).hostname or ""),
        kind="structured_data",
        extraction_method="public_json",
        confidence=0.9 if text else 0.7,
        title=title,
        author=author,
        text=text or pretty,
        markdown=text or "JSON:\n\n" + pretty,
        metadata={"json": payload},
    )


def _canonical_url(parser: _PageParser, final_url: str) -> str:
    for link in parser.links:
        if "canonical" in link.get("rel", "") and link.get("href"):
            return urljoin(final_url, link["href"])
    return parser.meta.get("og:url") or final_url


def _flatten_jsonld(values: list[Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            result.append(node)
            graph = node.get("@graph")
            if isinstance(graph, list):
                for child in graph:
                    visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    for value in values:
        visit(value)
    return result


def _jsonld_value(nodes: list[dict[str, Any]], *keys: str) -> str:
    for node in nodes:
        for key in keys:
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _jsonld_author(nodes: list[dict[str, Any]]) -> str:
    for node in nodes:
        value = node.get("author")
        candidates = value if isinstance(value, list) else [value]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
            if isinstance(candidate, dict):
                name = candidate.get("name")
                if isinstance(name, str) and name.strip():
                    return name.strip()
    return ""


def _jsonld_types(nodes: list[dict[str, Any]]) -> set[str]:
    types: set[str] = set()
    for node in nodes:
        value = node.get("@type")
        if isinstance(value, str):
            types.add(value)
        elif isinstance(value, list):
            types.update(str(item) for item in value if item)
    return types


def _collect_media(
    parser: _PageParser,
    oembed: dict[str, Any],
    jsonld: list[dict[str, Any]],
    base_url: str,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    candidates = [
        ("image", parser.meta.get("og:image")),
        ("image", parser.meta.get("twitter:image")),
        ("thumbnail", oembed.get("thumbnail_url")),
        ("video", parser.meta.get("og:video")),
        ("audio", parser.meta.get("og:audio")),
    ]
    for kind, value in candidates:
        if isinstance(value, str) and value.strip():
            media_url = urljoin(base_url, value.strip())
            if not any(item["url"] == media_url for item in items):
                items.append({"type": kind, "url": media_url})

    for node in jsonld:
        for key, kind in (("image", "image"), ("thumbnailUrl", "thumbnail"), ("contentUrl", "media")):
            value = node.get(key)
            candidates2 = value if isinstance(value, list) else [value]
            for item in candidates2:
                if isinstance(item, dict):
                    item = item.get("url") or item.get("contentUrl")
                if isinstance(item, str) and item.strip():
                    media_url = urljoin(base_url, item.strip())
                    if not any(existing["url"] == media_url for existing in items):
                        items.append({"type": kind, "url": media_url})
    return items


def _infer_kind(
    oembed: dict[str, Any],
    jsonld: list[dict[str, Any]],
    meta: dict[str, str],
) -> str:
    otype = str(oembed.get("type") or "").lower()
    if otype in {"video", "photo", "rich"}:
        return "media" if otype in {"video", "photo"} else "embed"
    types = {item.lower() for item in _jsonld_types(jsonld)}
    if types & {"article", "newsarticle", "blogposting", "report"}:
        return "article"
    if types & {"videoobject", "audioobject", "imageobject"}:
        return "media"
    ogtype = meta.get("og:type", "").lower()
    if ogtype.startswith("article"):
        return "article"
    return "webpage"


def _try_trafilatura(html: str, url: str) -> str:
    if importlib.util.find_spec("trafilatura") is None:
        return ""
    try:
        from trafilatura import extract as trafilatura_extract  # type: ignore

        result = trafilatura_extract(
            html,
            url=url,
            output_format="markdown",
            include_comments=False,
            include_links=True,
            include_images=True,
            include_formatting=True,
        )
        return str(result or "").strip()
    except Exception:
        return ""


def _markdown_to_plain(markdown: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", markdown)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = re.sub(r"[\*_~\x60]+", "", text)
    return text.strip()


def _dedupe_chunks(chunks: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for chunk in chunks:
        normalized = re.sub(r"\s+", " ", chunk).strip()
        if len(normalized) < 2 or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _platform_from_host(host: str) -> str:
    host = host.lower().removeprefix("www.")
    return host.split(".", 1)[0] if host else "web"


def _first(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""
