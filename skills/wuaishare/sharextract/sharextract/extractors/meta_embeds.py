from __future__ import annotations

import re
import urllib.parse
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError
from .generic import _PageParser


_META_PAGE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.8",
}

_THREADS_HOSTS = {
    "threads.com",
    "www.threads.com",
    "threads.net",
    "www.threads.net",
}
_INSTAGRAM_HOSTS = {
    "instagram.com",
    "www.instagram.com",
}
_FACEBOOK_HOSTS = {
    "facebook.com",
    "www.facebook.com",
    "m.facebook.com",
    "web.facebook.com",
}

_THREADS_POST_RE = re.compile(
    r"^/@(?P<username>[A-Za-z0-9._]+)/post/(?P<code>[A-Za-z0-9_-]+)/?$"
)
_THREADS_SHORT_RE = re.compile(r"^/t/(?P<code>[A-Za-z0-9_-]+)/?$")
_INSTAGRAM_POST_RE = re.compile(
    r"^/(?:[A-Za-z0-9._]+/)?(?P<route>p|reel)/"
    r"(?P<code>[A-Za-z0-9_-]+)/?$",
    re.IGNORECASE,
)
_FACEBOOK_POST_RE = re.compile(
    r"^/(?P<username>[^/]+)/posts/"
    r"(?:(?P<slug>[^/]+)/)?(?P<post_id>[^/]+)/?$",
    re.IGNORECASE,
)
_IG_DESCRIPTION_RE = re.compile(
    r"^(?P<likes>[\d.,]+(?:[KMB])?)\s+likes?,\s+"
    r"(?P<comments>[\d.,]+(?:[KMB])?)\s+comments?\s+-\s+"
    r"(?P<username>[A-Za-z0-9._]+)\s+on\s+"
    r"(?P<date>[^:]+):\s+[\"“](?P<caption>.*)[\"”]\.?\s*$",
    re.IGNORECASE | re.DOTALL,
)
_INSTAGRAM_TITLE_AUTHOR_RE = re.compile(
    r"\(@(?P<username>[A-Za-z0-9._]+)\)"
)
_THREADS_TITLE_AUTHOR_RE = re.compile(
    r"\(@(?P<username>[A-Za-z0-9._]+)\)"
)


class ThreadsPostExtractor(Extractor):
    name = "threads-post"
    priority = 38

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        return host in _THREADS_HOSTS and bool(
            _THREADS_POST_RE.fullmatch(parsed.path)
            or _THREADS_SHORT_RE.fullmatch(parsed.path)
        )

    def extract(self, url: str) -> ExtractedContent:
        requested_username, code = _threads_identity(url)
        response, parser = _read_public_meta_page(self.client, url)
        text = _first(
            parser.meta.get("og:description"),
            parser.meta.get("description"),
            parser.meta.get("twitter:description"),
        )
        og_title = _first(
            parser.meta.get("og:title"),
            parser.meta.get("twitter:title"),
        )
        username = requested_username or _username_from_title(
            og_title,
            _THREADS_TITLE_AUTHOR_RE,
        )
        if not text:
            raise ExtractorError(
                "Threads public page returned no readable Open Graph post text."
            )

        canonical = f"https://www.threads.com/t/{code}/"
        html, oembed, oembed_warning = _best_effort_oembed(
            self.client,
            "https://graph.threads.com/oembed",
            canonical,
        )

        warnings = [
            "Threads Open Graph image is not exported as post media because "
            "the public page can use the account profile image for text posts."
        ]
        if oembed_warning:
            warnings.append(oembed_warning)

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="threads",
            kind="social_post",
            extraction_method="standard_open_graph_threads_post",
            confidence=0.98,
            title=_title_from_text(text),
            author=username,
            text=text,
            markdown=text,
            html=html,
            metadata={
                "shortcode": code,
                "username": username,
                "declared_url": _first(
                    parser.meta.get("og:url"),
                    _declared_canonical(parser, response.url),
                ),
                "og_type": parser.meta.get("og:type", ""),
                "og_preview_image_url": _first(
                    parser.meta.get("og:image"),
                    parser.meta.get("twitter:image"),
                ),
                "oembed": oembed,
                "tokenless_oembed_documented": True,
                "uses_access_token": False,
                "uses_browser": False,
                "post_media_exported": False,
                "endpoint_documentation": (
                    "standard_open_graph_plus_meta_tokenless_oembed"
                ),
            },
            warnings=warnings,
        )


class InstagramPostExtractor(Extractor):
    name = "instagram-post"
    priority = 39

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        return (
            (parsed.hostname or "").lower() in _INSTAGRAM_HOSTS
            and _INSTAGRAM_POST_RE.fullmatch(parsed.path) is not None
        )

    def extract(self, url: str) -> ExtractedContent:
        input_route, code = _instagram_identity(url)
        response, parser = _read_public_meta_page(self.client, url)

        description = _first(
            parser.meta.get("og:description"),
            parser.meta.get("description"),
            parser.meta.get("twitter:description"),
        )
        og_title = _first(
            parser.meta.get("og:title"),
            parser.meta.get("twitter:title"),
        )
        declared_url = _first(
            parser.meta.get("og:url"),
            _declared_canonical(parser, response.url),
        )
        declared_code = _instagram_shortcode(declared_url)
        declared_mismatch = bool(
            declared_code
            and declared_code != code
        )

        parsed_description = _parse_instagram_description(description)
        username = str(parsed_description.get("username") or "")
        if not username:
            username = _username_from_title(
                _first(
                    parser.meta.get("twitter:title"),
                    parser.meta.get("og:title"),
                ),
                _INSTAGRAM_TITLE_AUTHOR_RE,
            )
        caption = str(parsed_description.get("caption") or "").strip()
        if not caption:
            caption = _caption_from_instagram_title(og_title) or description

        og_type = parser.meta.get("og:type", "").lower()
        declared_route = _instagram_route(declared_url)
        route = input_route
        if not declared_mismatch and declared_route in {"p", "reel"}:
            route = declared_route
        if og_type.startswith("video"):
            route = "reel"
        canonical = f"https://www.instagram.com/{route}/{code}/"

        image_url = _first(
            parser.meta.get("og:image"),
            parser.meta.get("twitter:image"),
            parser.meta.get("twitter:image:src"),
        )
        media: list[dict[str, Any]] = []
        if image_url:
            if route == "reel" or og_type.startswith("video"):
                media.append(
                    {
                        "type": "video",
                        "url": canonical,
                        "thumbnail_url": image_url,
                    }
                )
            else:
                media.append(
                    {
                        "type": "image",
                        "url": image_url,
                    }
                )

        html, oembed, oembed_warning = _best_effort_oembed(
            self.client,
            "https://graph.facebook.com/instagram_oembed",
            canonical,
        )
        warnings = []
        if declared_mismatch:
            warnings.append(
                "Instagram declared URL contains a different shortcode; "
                "ShareXtract keeps the requested shortcode as stable identity."
            )
        if oembed_warning:
            warnings.append(oembed_warning)

        if not caption and not og_title:
            raise ExtractorError(
                "Instagram public page returned no readable Open Graph post content."
            )

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="instagram",
            kind="social_post",
            extraction_method="standard_open_graph_instagram_post",
            confidence=0.98,
            title=_title_from_text(caption or og_title),
            author=username,
            text=caption or description or og_title,
            markdown=caption or description or og_title,
            html=html,
            media=media,
            metadata={
                "shortcode": code,
                "route": route,
                "username": username,
                "likes_display": parsed_description.get("likes_display", ""),
                "comments_display": parsed_description.get(
                    "comments_display",
                    "",
                ),
                "published_date_display": parsed_description.get(
                    "published_date_display",
                    "",
                ),
                "og_type": parser.meta.get("og:type", ""),
                "declared_url": declared_url,
                "declared_shortcode": declared_code or "",
                "declared_shortcode_mismatch": declared_mismatch,
                "oembed": oembed,
                "tokenless_oembed_documented": True,
                "uses_access_token": False,
                "uses_browser": False,
                "stream_urls_exported": False,
                "endpoint_documentation": (
                    "standard_open_graph_plus_meta_tokenless_oembed"
                ),
            },
            warnings=warnings,
        )


class FacebookPostExtractor(Extractor):
    name = "facebook-post"
    priority = 40

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        return (
            (parsed.hostname or "").lower() in _FACEBOOK_HOSTS
            and _FACEBOOK_POST_RE.fullmatch(parsed.path) is not None
        )

    def extract(self, url: str) -> ExtractedContent:
        username, post_id = _facebook_identity(url)
        response, parser = _read_public_meta_page(self.client, url)

        author = _first(
            parser.meta.get("og:title"),
            parser.meta.get("twitter:title"),
        )
        text = _first(
            parser.meta.get("og:description"),
            parser.meta.get("twitter:description"),
            parser.meta.get("description"),
        )
        if not text:
            raise ExtractorError(
                "Facebook public page returned no readable Open Graph post text."
            )

        canonical = (
            f"https://www.facebook.com/{username}/posts/{post_id}/"
        )
        declared_url = _first(
            parser.meta.get("og:url"),
            _declared_canonical(parser, response.url),
        )
        declared_post_id = _facebook_post_id(declared_url)
        declared_mismatch = bool(
            declared_post_id
            and declared_post_id != post_id
        )

        og_type = parser.meta.get("og:type", "").lower()
        image_url = _first(
            parser.meta.get("og:image"),
            parser.meta.get("twitter:image"),
        )
        media: list[dict[str, Any]] = []
        if image_url:
            if og_type.startswith("video"):
                media.append(
                    {
                        "type": "video",
                        "url": canonical,
                        "thumbnail_url": image_url,
                    }
                )
            else:
                media.append(
                    {
                        "type": "image",
                        "url": image_url,
                    }
                )

        html, oembed, oembed_warning = _best_effort_oembed(
            self.client,
            "https://graph.facebook.com/oembed_post",
            canonical,
        )
        warnings = []
        if declared_mismatch:
            warnings.append(
                "Facebook declared canonical uses a different post identifier; "
                "ShareXtract keeps the requested public post identifier as identity "
                "and records the declared URL separately."
            )
        if oembed_warning:
            warnings.append(oembed_warning)

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="facebook",
            kind="social_post",
            extraction_method="standard_open_graph_facebook_post",
            confidence=0.96,
            title=_title_from_text(text),
            author=author,
            text=text,
            markdown=text,
            html=html,
            media=media,
            metadata={
                "username": username,
                "post_id": post_id,
                "og_type": parser.meta.get("og:type", ""),
                "declared_url": declared_url,
                "declared_post_id": declared_post_id or "",
                "declared_post_id_mismatch": declared_mismatch,
                "oembed": oembed,
                "tokenless_oembed_documented": True,
                "uses_access_token": False,
                "uses_browser": False,
                "stream_urls_exported": False,
                "endpoint_documentation": (
                    "standard_open_graph_plus_meta_tokenless_oembed"
                ),
            },
            warnings=warnings,
        )


def _read_public_meta_page(client, url: str):
    response = client.get_text(
        url,
        headers=_META_PAGE_HEADERS,
    )
    if "text/html" not in response.content_type.lower():
        raise ExtractorError("Meta public post page did not return HTML.")
    parser = _PageParser()
    try:
        parser.feed(response.text)
        parser.close()
    except Exception as exc:
        raise ExtractorError(
            f"Meta public post HTML could not be parsed: {exc}"
        ) from exc
    return response, parser


def _best_effort_oembed(
    client,
    endpoint: str,
    target_url: str,
) -> tuple[str, dict[str, Any], str]:
    request_url = endpoint + "?" + urllib.parse.urlencode(
        {"url": target_url}
    )
    try:
        _, payload = client.get_json(
            request_url,
            headers={"Accept": "application/json"},
        )
    except Exception as exc:
        return "", {
            "status": "error",
            "endpoint": endpoint,
            "error": str(exc),
        }, (
            "Meta tokenless oEmbed enhancement was unavailable; "
            "standard public Open Graph content was preserved."
        )

    if not isinstance(payload, dict):
        return "", {
            "status": "invalid",
            "endpoint": endpoint,
        }, (
            "Meta tokenless oEmbed returned an unexpected payload; "
            "standard public Open Graph content was preserved."
        )

    html = str(payload.get("html") or "")
    public = {
        key: value
        for key, value in payload.items()
        if key != "html"
    }
    public["status"] = "ok"
    public["endpoint"] = endpoint
    return html, public, ""


def _threads_identity(url: str) -> tuple[str, str]:
    path = urllib.parse.urlsplit(url).path
    match = _THREADS_POST_RE.fullmatch(path)
    if match:
        return match.group("username"), match.group("code")
    match = _THREADS_SHORT_RE.fullmatch(path)
    if match:
        return "", match.group("code")
    raise ExtractorError("Threads URL is not a supported public post URL.")


def _instagram_identity(url: str) -> tuple[str, str]:
    match = _INSTAGRAM_POST_RE.fullmatch(
        urllib.parse.urlsplit(url).path
    )
    if not match:
        raise ExtractorError(
            "Instagram URL is not a supported public post/reel URL."
        )
    return match.group("route").lower(), match.group("code")


def _instagram_shortcode(url: str) -> str | None:
    if not url:
        return None
    match = _INSTAGRAM_POST_RE.fullmatch(
        urllib.parse.urlsplit(url).path
    )
    return match.group("code") if match else None


def _instagram_route(url: str) -> str | None:
    if not url:
        return None
    match = _INSTAGRAM_POST_RE.fullmatch(
        urllib.parse.urlsplit(url).path
    )
    return match.group("route").lower() if match else None


def _facebook_identity(url: str) -> tuple[str, str]:
    match = _FACEBOOK_POST_RE.fullmatch(
        urllib.parse.urlsplit(url).path
    )
    if not match:
        raise ExtractorError(
            "Facebook URL is not a supported public post URL."
        )
    return match.group("username"), match.group("post_id")


def _facebook_post_id(url: str) -> str | None:
    if not url:
        return None
    match = _FACEBOOK_POST_RE.fullmatch(
        urllib.parse.urlsplit(url).path
    )
    return match.group("post_id") if match else None


def _parse_instagram_description(value: str) -> dict[str, str]:
    match = _IG_DESCRIPTION_RE.fullmatch(
        str(value or "").strip()
    )
    if not match:
        return {}
    return {
        "likes_display": match.group("likes"),
        "comments_display": match.group("comments"),
        "username": match.group("username"),
        "published_date_display": match.group("date").strip(),
        "caption": match.group("caption").strip(),
    }


def _caption_from_instagram_title(value: str) -> str:
    match = re.search(
        r'on Instagram:\s*["“](.*)["”]\s*$',
        value or "",
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def _username_from_title(
    value: str,
    pattern: re.Pattern[str],
) -> str:
    match = pattern.search(value or "")
    return match.group("username") if match else ""


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
