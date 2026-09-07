from __future__ import annotations

import re
import urllib.parse
from html.parser import HTMLParser
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError
from .generic import _PageParser


_LINKEDIN_HOSTS = {
    "linkedin.com",
    "www.linkedin.com",
}
_ACTIVITY_RE = re.compile(
    r"activity-(?P<activity_id>\d+)(?:-[A-Za-z0-9_-]+)?",
    re.IGNORECASE,
)
_FEED_ACTIVITY_RE = re.compile(
    r"^/(?:embed/)?feed/update/urn:li:activity:(?P<activity_id>\d+)/?$",
    re.IGNORECASE,
)


class LinkedInPostExtractor(Extractor):
    """Extract an embeddable public LinkedIn post from LinkedIn's public embed."""

    name = "linkedin-post"
    priority = 41

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        if (parsed.hostname or "").lower() not in _LINKEDIN_HOSTS:
            return False
        return _activity_id(url) is not None

    def extract(self, url: str) -> ExtractedContent:
        activity_id = _activity_id(url)
        if not activity_id:
            raise ExtractorError(
                "LinkedIn URL does not contain a supported public activity ID."
            )

        canonical = (
            "https://www.linkedin.com/feed/update/"
            f"urn:li:activity:{activity_id}"
        )
        embed_url = (
            "https://www.linkedin.com/embed/feed/update/"
            f"urn:li:activity:{activity_id}"
        )
        response = self.client.get_text(
            embed_url,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.8",
            },
        )
        if "text/html" not in response.content_type.lower():
            raise ExtractorError(
                "LinkedIn public embed did not return HTML."
            )

        dom = _LinkedInEmbedParser()
        og = _PageParser()
        try:
            dom.feed(response.text)
            dom.close()
            og.feed(response.text)
            og.close()
        except Exception as exc:
            raise ExtractorError(
                f"LinkedIn public embed HTML could not be parsed: {exc}"
            ) from exc

        if dom.activity_id and dom.activity_id != activity_id:
            raise ExtractorError(
                "LinkedIn embed activity identity did not match the requested activity."
            )

        text = _clean_text(dom.values.get("commentary", ""))
        author = _clean_text(dom.values.get("author", ""))
        if not text:
            text = _strip_linkedin_og_suffix(
                _first(
                    og.meta.get("og:description"),
                    og.meta.get("description"),
                    og.meta.get("twitter:description"),
                )
            )
        if not text and not author:
            raise ExtractorError(
                "LinkedIn public embed returned no usable post content."
            )

        media = [
            {
                "type": "image",
                "url": image_url,
                **({"alt": alt} if alt else {}),
            }
            for image_url, alt in _dedupe_images(dom.post_images)
        ]

        attachment = {
            key: value
            for key, value in {
                "url": dom.attachment_url,
                "title": _clean_text(
                    dom.values.get("attachment_title", "")
                ),
                "subtitle": _clean_text(
                    dom.values.get("attachment_subtitle", "")
                ),
                "thumbnail_url": dom.attachment_thumbnail_url,
            }.items()
            if value
        }

        preview_image = _first(
            og.meta.get("og:image"),
            og.meta.get("twitter:image"),
        )
        title = _title_from_text(text)
        if not title:
            title = _first(
                og.meta.get("og:title"),
                " ".join(og.title_parts).strip(),
            )

        author_url = _strip_tracking_query(dom.author_url)
        author_type = (
            "organization"
            if "/company/" in author_url
            else "member"
            if "/in/" in author_url
            else ""
        )

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="linkedin",
            kind="social_post",
            extraction_method="public_linkedin_embed",
            confidence=0.98,
            title=title,
            author=author,
            text=text,
            markdown=text,
            media=media,
            metadata={
                "activity_id": activity_id,
                "activity_urn": f"urn:li:activity:{activity_id}",
                "embed_url": embed_url,
                "author": {
                    key: value
                    for key, value in {
                        "name": author,
                        "url": author_url,
                        "type": author_type,
                        "followers_display": _clean_text(
                            dom.values.get("followers", "")
                        ),
                    }.items()
                    if value
                },
                "published_display": _clean_text(
                    dom.values.get("time", "")
                ),
                "stats": {
                    "reactions": dom.reactions_count,
                    "comments": dom.comments_count,
                    "reactions_display": _clean_text(
                        dom.values.get("reactions_display", "")
                    ),
                    "comments_display": _clean_text(
                        dom.values.get("comments_display", "")
                    ),
                },
                "attachment": attachment,
                "preview_image_url": preview_image,
                "declared_url": _first(
                    og.meta.get("og:url"),
                    _declared_canonical(og, response.url),
                ),
                "public_embed_documented": True,
                "requires_login": False,
                "uses_oauth": False,
                "uses_access_token": False,
                "uses_browser": False,
                "comments_exported": False,
                "endpoint_documentation": (
                    "linkedin_public_embed_product_surface"
                ),
            },
            warnings=[
                "LinkedIn public posts are extracted from the anonymous public "
                "embed representation available for posts whose visibility allows "
                "off-LinkedIn embedding.",
                "Only images explicitly present in the embed's feed-images content "
                "are exported as post media. Profile images, logos and generic Open "
                "Graph previews are kept out of media.",
                "LinkedIn comments are not exported by this adapter; only the public "
                "comment count exposed by the embed is normalized.",
            ],
        )


class _LinkedInEmbedParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.stack: list[dict[str, Any]] = []
        self.captures: list[dict[str, Any]] = []
        self.values: dict[str, str] = {}
        self.activity_id = ""
        self.author_url = ""
        self.reactions_count: int | None = None
        self.comments_count: int | None = None
        self.post_images: list[tuple[str, str]] = []
        self.attachment_url = ""
        self.attachment_thumbnail_url = ""

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        is_void = tag in {
            "area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr",
        }
        attr = {
            str(key): str(value)
            for key, value in attrs
            if key and value is not None
        }
        if not is_void:
            self.depth += 1
            self.stack.append({
                "tag": tag,
                "depth": self.depth,
                "test_id": attr.get("data-test-id", ""),
            })

        if tag == "article":
            urn = attr.get("data-activity-urn", "")
            match = re.fullmatch(
                r"urn:li:activity:(\d+)",
                urn,
                flags=re.IGNORECASE,
            )
            if match:
                self.activity_id = match.group(1)

        tracking = attr.get("data-tracking-control-name", "")
        test_id = attr.get("data-test-id", "")

        if tracking == "public_post_embed_feed-actor-name":
            self.author_url = attr.get("href", "")
            if not is_void:
                self._capture("author")

        if test_id == "main-feed-activity-embed-card__commentary":
            if not is_void:
                self._capture("commentary")

        if test_id == "social-actions__reactions":
            self.reactions_count = _int_or_none(
                attr.get("data-num-reactions")
            )
            if not is_void:
                self._capture("reactions_display")

        if test_id == "social-actions__comments":
            self.comments_count = _int_or_none(
                attr.get("data-num-comments")
            )
            if not is_void:
                self._capture("comments_display")

        if tag == "time" and not is_void and "time" not in self.values:
            self._capture("time")

        if test_id == "article-content":
            self.attachment_url = _strip_tracking_query(
                attr.get("href", "")
            )

        if test_id == "article-content__title" and not is_void:
            self._capture("attachment_title")

        if test_id == "article-content__subtitle" and not is_void:
            self._capture("attachment_subtitle")

        if tag == "img":
            src = attr.get("data-delayed-url", "") or attr.get("src", "")
            alt = _clean_text(attr.get("alt", ""))
            if src and self._inside("feed-images-content__list-item"):
                self.post_images.append((src, alt))
            elif src and self._inside("article-content"):
                self.attachment_thumbnail_url = src

        if (
            tag == "p"
            and not is_void
            and self._inside(
                "main-feed-activity-embed-card__entity-lockup"
            )
        ):
            self._capture("__entity_paragraph__")

    def handle_data(self, data: str) -> None:
        if not data:
            return
        for capture in self.captures:
            capture["parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {
            "area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr",
        }:
            return

        remaining: list[dict[str, Any]] = []
        for capture in self.captures:
            if capture["depth"] == self.depth:
                value = _clean_text("".join(capture["parts"]))
                key = capture["key"]
                if key == "__entity_paragraph__":
                    if (
                        value
                        and "followers" in value.lower()
                        and "followers" not in self.values
                    ):
                        self.values["followers"] = value
                elif value and key not in self.values:
                    self.values[key] = value
            else:
                remaining.append(capture)
        self.captures = remaining

        if self.stack and self.stack[-1]["depth"] == self.depth:
            self.stack.pop()
        self.depth = max(0, self.depth - 1)

    def _capture(self, key: str) -> None:
        self.captures.append({
            "key": key,
            "depth": self.depth,
            "parts": [],
        })

    def _inside(self, test_id: str) -> bool:
        return any(
            item.get("test_id") == test_id
            for item in self.stack
        )


def _activity_id(url: str) -> str | None:
    parsed = urllib.parse.urlsplit(url)
    match = _FEED_ACTIVITY_RE.fullmatch(parsed.path)
    if match:
        return match.group("activity_id")
    if "/posts/" in parsed.path:
        match = _ACTIVITY_RE.search(parsed.path)
        if match:
            return match.group("activity_id")
    return None


def _int_or_none(value: Any) -> int | None:
    try:
        result = int(str(value or "").strip())
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None


def _clean_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_linkedin_og_suffix(value: str) -> str:
    text = _clean_text(value)
    return re.sub(
        r"\s*\|\s*\d[\d,]*\s+comments?\s+on\s+LinkedIn\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()


def _strip_tracking_query(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        return url
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            "",
            "",
        )
    )


def _declared_canonical(
    parser: _PageParser,
    base_url: str,
) -> str:
    for link in parser.links:
        rel = str(link.get("rel") or "").lower()
        href = str(link.get("href") or "").strip()
        if "canonical" in rel and href:
            return urllib.parse.urljoin(base_url, href)
    return ""


def _first(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _title_from_text(value: str) -> str:
    first = next(
        (
            line.strip()
            for line in str(value or "").splitlines()
            if line.strip()
        ),
        "",
    )
    if len(first) <= 100:
        return first
    return first[:97].rstrip() + "..."


def _dedupe_images(
    values: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for url, alt in values:
        token = str(url or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        result.append((token, alt))
    return result
