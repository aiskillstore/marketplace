from __future__ import annotations

import html
import json
import re
import urllib.parse
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_INITIAL_DATA_RE = re.compile(
    r'<script[^>]+id=["\']js-initialData["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
_INITIAL_PROPS_MARKER = "window.g_initialProps = "
_ID_RE = re.compile(r"^\d{5,32}$")
_BLOCK_TAGS = {
    "p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "blockquote", "pre", "figcaption", "br",
}
_IGNORE_TAGS = {"script", "style", "noscript", "template", "svg"}


class _RichHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.media: list[dict[str, Any]] = []
        self._ignore_depth = 0
        self._seen_media: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        attr = {
            str(key).lower(): str(value)
            for key, value in attrs
            if key and value is not None
        }
        if tag in _IGNORE_TAGS:
            self._ignore_depth += 1
            return
        if self._ignore_depth:
            return
        if tag in _BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "img":
            url = (
                attr.get("data-original")
                or attr.get("src")
                or attr.get("data-actualsrc")
                or ""
            ).strip()
            if url.startswith("//"):
                url = "https:" + url
            if url.startswith(("http://", "https://")) and url not in self._seen_media:
                self._seen_media.add(url)
                item: dict[str, Any] = {"type": "image", "url": html.unescape(url)}
                alt = attr.get("alt", "").strip()
                if alt:
                    item["alt"] = alt
                width = _int_value(attr.get("data-rawwidth") or attr.get("width"))
                height = _int_value(attr.get("data-rawheight") or attr.get("height"))
                if width is not None:
                    item["width"] = width
                if height is not None:
                    item["height"] = height
                self.media.append(item)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _IGNORE_TAGS and self._ignore_depth:
            self._ignore_depth -= 1
            return
        if self._ignore_depth:
            return
        if tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._ignore_depth:
            return
        if data:
            self.parts.append(data)

    @property
    def text(self) -> str:
        joined = html.unescape("".join(self.parts))
        lines = [
            re.sub(r"[ \t\f\v]+", " ", line).strip()
            for line in joined.splitlines()
        ]
        result: list[str] = []
        previous_blank = False
        for line in lines:
            if not line:
                if result and not previous_blank:
                    result.append("")
                previous_blank = True
                continue
            result.append(line)
            previous_blank = False
        return "\n".join(result).strip()


class _SanitizingHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self._ignore_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in _IGNORE_TAGS:
            self._ignore_depth += 1
            return
        if self._ignore_depth:
            return
        rendered = []
        for key, value in attrs:
            if not key:
                continue
            key_l = str(key).lower()
            if key_l.startswith("on") or key_l == "style":
                continue
            if value is None:
                rendered.append(str(key))
            else:
                value_s = str(value)
                if key_l in {"href", "src", "data-original", "data-actualsrc"}:
                    if not _safe_rich_url(value_s):
                        continue
                rendered.append(
                    f'{key}="{html.escape(value_s, quote=True)}"'
                )
        suffix = (" " + " ".join(rendered)) if rendered else ""
        self.parts.append(f"<{tag}{suffix}>")

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)
        if not self._ignore_depth and tag.lower() not in _IGNORE_TAGS:
            self.parts.append(f"</{tag.lower()}>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _IGNORE_TAGS and self._ignore_depth:
            self._ignore_depth -= 1
            return
        if self._ignore_depth:
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self._ignore_depth:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if not self._ignore_depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self._ignore_depth:
            self.parts.append(f"&#{name};")

    @property
    def html(self) -> str:
        return "".join(self.parts).strip()


class ZhihuAnswerExtractor(Extractor):
    """Extract public Zhihu answers from the anonymous Tardis SSR reader."""

    name = "zhihu-answer"
    priority = 35

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = self.hostname(url)
        parts = [part for part in parsed.path.split("/") if part]

        if host in {"zhihu.com", "www.zhihu.com"}:
            if (
                len(parts) >= 4
                and parts[0] == "question"
                and parts[2] == "answer"
                and _ID_RE.fullmatch(parts[1])
                and _ID_RE.fullmatch(parts[3])
            ):
                return True
            if (
                len(parts) >= 4
                and parts[:3] == ["tardis", "zm", "ans"]
                and _ID_RE.fullmatch(parts[3])
            ):
                return True
        return False

    def extract(self, url: str) -> ExtractedContent:
        question_id, answer_id = self._ids(url)
        endpoint = f"https://www.zhihu.com/tardis/zm/ans/{answer_id}"
        response = self.client.get_text(
            endpoint,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
        )
        props = _extract_initial_props(response.text)
        render = props.get("renderHtml")
        if not isinstance(render, dict) or render.get("type") != "ans":
            raise ExtractorError(
                "Zhihu public Tardis answer page did not contain readable SSR data."
            )

        actual_question = str(render.get("question_token") or question_id or "").strip()
        if actual_question and not _ID_RE.fullmatch(actual_question):
            actual_question = question_id or ""
        if not actual_question:
            raise ExtractorError("Zhihu answer did not expose its question ID.")

        content_html = str(render.get("content") or "")
        text, sanitized_html, media = _normalize_rich_html(content_html)
        if not text:
            raise ExtractorError("Zhihu public answer contained no readable text.")

        author = render.get("author")
        author = author if isinstance(author, dict) else {}
        created = _timestamp(render.get("created"))
        canonical = (
            f"https://www.zhihu.com/question/{actual_question}/answer/{answer_id}"
        )

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="zhihu",
            kind="answer",
            extraction_method="first_party_public_tardis_ssr_json",
            confidence=0.98,
            title=str(render.get("title") or "").strip(),
            author=str(author.get("name") or "").strip(),
            text=text,
            markdown=text,
            html=sanitized_html,
            media=media,
            metadata={
                "answer_id": answer_id,
                "question_id": actual_question,
                "question_description": _rich_text(str(render.get("desc") or "")),
                "created_at": created,
                "author": {
                    "name": author.get("name"),
                    "headline": author.get("info"),
                    "avatar_url": author.get("logo"),
                },
                "stats": {
                    "voteup_count": render.get("upvoted_count"),
                    "comment_count": render.get("comment_count"),
                    "favorite_count": render.get("favorites"),
                    "question_answer_count": render.get("answer_count"),
                },
                "public_reader_url": endpoint,
                "endpoint_documentation": "undocumented",
                "requires_login": False,
                "uses_private_signature": False,
            },
            warnings=[
                "Zhihu answer content was read from the anonymous first-party "
                "Tardis SSR reader. This public page structure is undocumented "
                "and may change."
            ],
        )

    def _ids(self, url: str) -> tuple[str, str]:
        parsed = urllib.parse.urlsplit(url)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
        if (
            len(parts) >= 4
            and parts[0] == "question"
            and parts[2] == "answer"
            and _ID_RE.fullmatch(parts[1])
            and _ID_RE.fullmatch(parts[3])
        ):
            return parts[1], parts[3]
        if (
            len(parts) >= 4
            and parts[:3] == ["tardis", "zm", "ans"]
            and _ID_RE.fullmatch(parts[3])
        ):
            return "", parts[3]
        raise ExtractorError("Unsupported Zhihu answer URL.")


class ZhihuArticleExtractor(Extractor):
    """Extract public Zhihu Zhuanlan articles from embedded first-party state."""

    name = "zhihu-article"
    priority = 36

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = self.hostname(url)
        parts = [part for part in parsed.path.split("/") if part]

        if host in {"zhuanlan.zhihu.com"}:
            return (
                len(parts) >= 2
                and parts[0] == "p"
                and bool(_ID_RE.fullmatch(parts[1]))
            )
        if host in {"zhihu.com", "www.zhihu.com"}:
            return (
                len(parts) >= 4
                and parts[:3] == ["tardis", "zm", "art"]
                and bool(_ID_RE.fullmatch(parts[3]))
            )
        return False

    def extract(self, url: str) -> ExtractedContent:
        article_id = self._article_id(url)
        canonical = f"https://zhuanlan.zhihu.com/p/{article_id}"
        warnings: list[str] = []

        try:
            response = self.client.get_text(
                canonical,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                },
            )
            article = _extract_article_entity(response.text, article_id)
        except Exception as exc:
            article = None
            warnings.append(
                "Zhihu Zhuanlan hydration route was unavailable; "
                f"falling back to the public Tardis reader ({exc})."
            )

        if isinstance(article, dict):
            result = _article_result_from_entity(
                source_url=url,
                canonical=canonical,
                article_id=article_id,
                article=article,
                warnings=warnings,
            )
            if result is not None:
                return result

        endpoint = f"https://www.zhihu.com/tardis/zm/art/{article_id}"
        response = self.client.get_text(
            endpoint,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
        )
        props = _extract_initial_props(response.text)
        render = props.get("renderHtml")
        if not isinstance(render, dict) or render.get("type") != "art":
            raise ExtractorError(
                "Zhihu public article routes returned no readable structured data."
            )
        content_html = str(render.get("content") or "")
        text, sanitized_html, media = _normalize_rich_html(content_html)
        if not text:
            raise ExtractorError("Zhihu public article contained no readable text.")

        author = render.get("author")
        author = author if isinstance(author, dict) else {}
        image = str(render.get("img") or "").strip()
        if image and not any(item.get("url") == image for item in media):
            media.insert(0, {"type": "image", "url": image})

        warnings.append(
            "Zhihu article used the anonymous first-party Tardis SSR reader "
            "because the richer Zhuanlan hydration entity was unavailable."
        )
        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="zhihu",
            kind="article",
            extraction_method="first_party_public_tardis_ssr_json",
            confidence=0.94,
            title=str(render.get("title") or "").strip(),
            author=str(author.get("name") or "").strip(),
            text=text,
            markdown=text,
            html=sanitized_html,
            media=media,
            metadata={
                "article_id": article_id,
                "created_or_updated_at": _timestamp(render.get("created")),
                "author": {
                    "name": author.get("name"),
                    "headline": author.get("info"),
                    "avatar_url": author.get("logo"),
                },
                "stats": {
                    "voteup_count": render.get("upvoted_count"),
                    "comment_count": render.get("comment_count"),
                    "favorite_count": render.get("favorites"),
                },
                "public_reader_url": endpoint,
                "endpoint_documentation": "undocumented",
                "requires_login": False,
                "uses_private_signature": False,
            },
            warnings=warnings,
        )

    def _article_id(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
        if (
            self.hostname(url) == "zhuanlan.zhihu.com"
            and len(parts) >= 2
            and parts[0] == "p"
            and _ID_RE.fullmatch(parts[1])
        ):
            return parts[1]
        if (
            self.hostname(url) in {"zhihu.com", "www.zhihu.com"}
            and len(parts) >= 4
            and parts[:3] == ["tardis", "zm", "art"]
            and _ID_RE.fullmatch(parts[3])
        ):
            return parts[3]
        raise ExtractorError("Unsupported Zhihu article URL.")


def _extract_initial_props(page_html: str) -> dict[str, Any]:
    pos = page_html.find(_INITIAL_PROPS_MARKER)
    if pos < 0:
        raise ExtractorError("Zhihu public Tardis SSR data was not found.")
    raw = page_html[pos + len(_INITIAL_PROPS_MARKER) :]
    try:
        value, _ = json.JSONDecoder().raw_decode(raw)
    except json.JSONDecodeError as exc:
        raise ExtractorError("Zhihu public Tardis SSR JSON was invalid.") from exc
    if not isinstance(value, dict):
        raise ExtractorError("Zhihu public Tardis SSR data was not an object.")
    return value


def _extract_article_entity(
    page_html: str,
    article_id: str,
) -> dict[str, Any] | None:
    match = _INITIAL_DATA_RE.search(page_html)
    if not match:
        return None
    try:
        payload = json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    state = payload.get("initialState")
    if not isinstance(state, dict):
        return None
    entities = state.get("entities")
    if not isinstance(entities, dict):
        return None
    articles = entities.get("articles")
    if not isinstance(articles, dict):
        return None
    value = articles.get(article_id)
    return value if isinstance(value, dict) else None


def _article_result_from_entity(
    *,
    source_url: str,
    canonical: str,
    article_id: str,
    article: dict[str, Any],
    warnings: list[str],
) -> ExtractedContent | None:
    content_html = str(article.get("content") or "")
    text, sanitized_html, media = _normalize_rich_html(content_html)
    if not text:
        return None

    author = article.get("author")
    author = author if isinstance(author, dict) else {}
    image = str(article.get("imageUrl") or "").strip()
    if image and not any(item.get("url") == image for item in media):
        media.insert(0, {"type": "image", "url": image})

    topics: list[dict[str, Any]] = []
    raw_topics = article.get("topics")
    if isinstance(raw_topics, list):
        for topic in raw_topics:
            if not isinstance(topic, dict):
                continue
            topics.append(
                {
                    "id": topic.get("id"),
                    "name": topic.get("name"),
                    "url": topic.get("url"),
                }
            )

    return ExtractedContent(
        source_url=source_url,
        canonical_url=canonical,
        platform="zhihu",
        kind="article",
        extraction_method="first_party_embedded_initial_state",
        confidence=0.99,
        title=str(article.get("title") or "").strip(),
        author=str(author.get("name") or "").strip(),
        text=text,
        markdown=text,
        html=sanitized_html,
        media=media,
        metadata={
            "article_id": article_id,
            "created_at": _timestamp(article.get("created")),
            "updated_at": _timestamp(article.get("updated")),
            "excerpt": _rich_text(str(article.get("excerpt") or "")),
            "author": {
                "id": author.get("id"),
                "name": author.get("name"),
                "headline": author.get("headline"),
                "url_token": author.get("urlToken"),
                "url": _absolute_zhihu_url(author.get("url")),
                "avatar_url": author.get("avatarUrl"),
            },
            "topics": topics,
            "stats": {
                "voteup_count": article.get("voteupCount"),
                "comment_count": article.get("commentCount"),
                "favorite_count": article.get("favlistsCount"),
                "liked_count": article.get("likedCount"),
            },
            "endpoint_documentation": "undocumented",
            "requires_login": False,
            "uses_private_signature": False,
        },
        warnings=warnings
        + [
            "Zhihu article content was read from first-party hydration data "
            "embedded in the anonymous public Zhuanlan page. This structure is "
            "undocumented and may change."
        ],
    )


def _normalize_rich_html(
    value: str,
) -> tuple[str, str, list[dict[str, Any]]]:
    text_parser = _RichHTMLParser()
    sanitizer = _SanitizingHTMLParser()
    try:
        text_parser.feed(value)
        text_parser.close()
        sanitizer.feed(value)
        sanitizer.close()
    except Exception as exc:
        raise ExtractorError(f"Zhihu rich-text parsing failed: {exc}") from exc
    return text_parser.text, sanitizer.html, text_parser.media


def _rich_text(value: str) -> str:
    parser = _RichHTMLParser()
    try:
        parser.feed(value)
        parser.close()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html.unescape(value)).strip()
    return parser.text


def _timestamp(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(float(value), timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _safe_rich_url(value: str) -> bool:
    token = html.unescape(value).strip()
    if not token:
        return False
    parsed = urllib.parse.urlsplit(token)
    if parsed.scheme:
        return parsed.scheme.lower() in {"http", "https"}
    return not token.lower().startswith(("javascript:", "data:", "vbscript:"))


def _absolute_zhihu_url(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    if value.startswith("//"):
        return "https:" + value
    if value.startswith("/"):
        return "https://www.zhihu.com" + value
    return value


def _int_value(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
