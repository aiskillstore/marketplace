from __future__ import annotations

import re
import urllib.parse
from typing import Any

from sharextract.feeds import try_extract_syndication_feed
from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


_REDDIT_HOSTS = {
    "reddit.com",
    "www.reddit.com",
    "m.reddit.com",
}
_THREAD_RE = re.compile(
    r"^/r/(?P<subreddit>[^/]+)/comments/(?P<post_id>[a-z0-9]+)/"
    r"(?P<slug>[^/]+)(?:/(?P<comment_id>[a-z0-9]+))?/?$",
    re.IGNORECASE,
)


class RedditPostExtractor(Extractor):
    """Extract public Reddit posts through documented oEmbed + optional Atom RSS."""

    name = "reddit-oembed"
    priority = 35

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        if host not in _REDDIT_HOSTS:
            return False
        return _THREAD_RE.fullmatch(parsed.path) is not None

    def extract(self, url: str) -> ExtractedContent:
        canonical, subreddit, post_id = _canonical_thread_url(url)
        endpoint = "https://www.reddit.com/oembed?" + urllib.parse.urlencode(
            {"url": canonical}
        )
        _, payload = self.client.get_json(
            endpoint,
            headers={
                "Accept": "application/json",
            },
        )
        if not isinstance(payload, dict):
            raise ExtractorError("Reddit oEmbed did not return an object.")

        title = str(payload.get("title") or "").strip()
        author = _clean_author(payload.get("author_name"))
        embed_html = str(payload.get("html") or "")
        if not title and not author and not embed_html:
            raise ExtractorError("Reddit oEmbed returned no usable metadata.")

        post_text = title
        comments: list[Message] = []
        thread_entries: list[dict[str, Any]] = []
        rss_status = "unavailable"
        rss_error = ""
        rss_url = canonical.rstrip("/") + ".rss"

        try:
            response = self.client.get_text(
                rss_url,
                headers={
                    "Accept": (
                        "application/atom+xml,application/xml;q=0.9,"
                        "*/*;q=0.5"
                    ),
                },
            )
            feed = try_extract_syndication_feed(
                rss_url,
                response.url,
                response.content_type,
                response.text,
            )
            if (
                feed is not None
                and feed.extraction_method == "standard_atom"
                and isinstance(feed.metadata.get("feed"), dict)
            ):
                raw_entries = feed.metadata["feed"].get("entries")
                if isinstance(raw_entries, list):
                    thread_entries = [
                        entry
                        for entry in raw_entries
                        if isinstance(entry, dict)
                    ]
                if thread_entries:
                    first = thread_entries[0]
                    if _same_reddit_thread(
                        str(first.get("url") or ""),
                        subreddit,
                        post_id,
                    ):
                        candidate = _strip_reddit_feed_footer(
                            str(first.get("text") or "")
                        )
                        if candidate:
                            post_text = candidate
                        if not title:
                            title = str(first.get("title") or "").strip()
                        if not author:
                            author = _clean_author(first.get("author"))

                    comments = _messages_from_entries(
                        thread_entries[1:],
                        subreddit=subreddit,
                        post_id=post_id,
                    )
                    rss_status = "ok"
                else:
                    rss_status = "empty"
            else:
                rss_status = "not_atom"
        except Exception as exc:
            rss_status = "error"
            rss_error = str(exc)

        if not post_text:
            post_text = title

        metadata: dict[str, Any] = {
            "subreddit": subreddit,
            "post_id": post_id,
            "oembed": {
                key: value
                for key, value in payload.items()
                if key != "html"
            },
            "endpoint_documentation": "documented_reddit_oembed",
            "thread_rss": {
                "url": rss_url,
                "status": rss_status,
                "standard": "Atom",
                "entry_count": len(thread_entries),
                "comment_count": len(comments),
            },
            "requires_login": False,
            "uses_oauth": False,
            "uses_json_endpoint": False,
            "uses_browser": False,
        }
        if rss_error:
            metadata["thread_rss"]["error"] = rss_error

        warnings = []
        if rss_status != "ok":
            warnings.append(
                "Reddit Atom thread RSS was unavailable for this request; "
                "the documented public oEmbed result was preserved."
            )

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="reddit",
            kind="discussion_thread",
            extraction_method="documented_reddit_oembed",
            confidence=0.99,
            title=title,
            author=author,
            text=post_text,
            markdown=post_text,
            html=embed_html,
            messages=comments,
            metadata=metadata,
            warnings=warnings,
        )


def _canonical_thread_url(url: str) -> tuple[str, str, str]:
    parsed = urllib.parse.urlsplit(url)
    match = _THREAD_RE.fullmatch(parsed.path)
    if match is None:
        raise ExtractorError("Reddit URL is not a supported public thread URL.")
    subreddit = match.group("subreddit")
    post_id = match.group("post_id").lower()
    slug = match.group("slug")
    canonical = (
        f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/{slug}/"
    )
    return canonical, subreddit, post_id


def _clean_author(value: Any) -> str:
    token = str(value or "").strip()
    token = re.sub(r"^/?u/", "", token, flags=re.IGNORECASE)
    return token


def _same_reddit_thread(
    url: str,
    subreddit: str,
    post_id: str,
) -> bool:
    try:
        canonical, entry_subreddit, entry_post_id = _canonical_thread_url(url)
    except Exception:
        return False
    return (
        bool(canonical)
        and entry_subreddit.lower() == subreddit.lower()
        and entry_post_id.lower() == post_id.lower()
    )


def _messages_from_entries(
    entries: list[dict[str, Any]],
    *,
    subreddit: str,
    post_id: str,
) -> list[Message]:
    messages: list[Message] = []
    for entry in entries:
        url = str(entry.get("url") or "")
        if not _same_reddit_thread(url, subreddit, post_id):
            continue
        text = str(entry.get("text") or "").strip()
        if not text:
            continue
        messages.append(
            Message(
                role="comment",
                text=text,
                author=_clean_author(entry.get("author")) or None,
                created_at=(
                    entry.get("updated_at")
                    or entry.get("published_at")
                    or None
                ),
                attachments=[
                    {"url": url}
                ] if url else [],
            )
        )
    return messages


def _strip_reddit_feed_footer(value: str) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    # Reddit's Atom post entry appends a generated attribution/action footer.
    text = re.sub(
        r"\s+submitted by\s+/u/[^\s]+\s+\[link\]\s+\[comments\]\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return text.strip()
