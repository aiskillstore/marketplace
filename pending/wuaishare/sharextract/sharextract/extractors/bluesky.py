from __future__ import annotations

import re
import urllib.parse
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_POST_PATH_RE = re.compile(r"^/profile/([^/]+)/post/([^/?#]+)/*$")


class BlueskyPostExtractor(Extractor):
    """Extract public Bluesky posts through documented AT Protocol APIs."""

    name = "bluesky-atproto"
    priority = 30

    def supports(self, url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        return (
            self.hostname(url) == "bsky.app"
            and _POST_PATH_RE.match(parsed.path) is not None
        )

    def extract(self, url: str) -> ExtractedContent:
        parsed = urllib.parse.urlsplit(url)
        match = _POST_PATH_RE.match(parsed.path)
        if not match:
            raise ExtractorError("Unsupported Bluesky post URL.")

        actor = urllib.parse.unquote(match.group(1))
        rkey = urllib.parse.unquote(match.group(2))
        did = actor if actor.startswith("did:") else self._resolve_handle(actor)
        at_uri = f"at://{did}/app.bsky.feed.post/{rkey}"

        endpoint = (
            "https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread?"
            + urllib.parse.urlencode(
                {
                    "uri": at_uri,
                    "depth": 0,
                    "parentHeight": 0,
                }
            )
        )
        _, payload = self.client.get_json(
            endpoint, headers={"Accept": "application/json"}
        )
        if not isinstance(payload, dict):
            raise ExtractorError("Bluesky AppView returned an invalid response.")

        thread = payload.get("thread")
        if not isinstance(thread, dict):
            raise ExtractorError("Bluesky response did not contain a post thread.")

        post = thread.get("post")
        if not isinstance(post, dict):
            raise ExtractorError("Bluesky thread did not contain a readable post.")

        record = post.get("record")
        if not isinstance(record, dict):
            raise ExtractorError("Bluesky post record is missing.")

        text = str(record.get("text") or "").strip()
        author_view = post.get("author")
        author_view = author_view if isinstance(author_view, dict) else {}
        handle = str(author_view.get("handle") or actor).strip()
        display_name = str(author_view.get("displayName") or "").strip()
        author = display_name or handle

        canonical_actor = handle or did
        canonical_url = (
            "https://bsky.app/profile/"
            + urllib.parse.quote(canonical_actor, safe=":.@")
            + "/post/"
            + urllib.parse.quote(rkey, safe="")
        )

        media = _collect_embed_media(post.get("embed"))
        metadata: dict[str, Any] = {
            "uri": post.get("uri") or at_uri,
            "cid": post.get("cid"),
            "did": author_view.get("did") or did,
            "handle": handle,
            "display_name": display_name,
            "created_at": record.get("createdAt"),
            "indexed_at": post.get("indexedAt"),
            "langs": record.get("langs") if isinstance(record.get("langs"), list) else [],
            "like_count": post.get("likeCount"),
            "reply_count": post.get("replyCount"),
            "repost_count": post.get("repostCount"),
            "quote_count": post.get("quoteCount"),
            "facets": record.get("facets") if isinstance(record.get("facets"), list) else [],
        }

        reply = record.get("reply")
        if isinstance(reply, dict):
            metadata["reply_root_uri"] = _strong_ref_uri(reply.get("root"))
            metadata["reply_parent_uri"] = _strong_ref_uri(reply.get("parent"))

        quote = _extract_quoted_record(post.get("embed"))
        if quote:
            metadata["quoted_post"] = quote

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical_url,
            platform="bluesky",
            kind="social_post",
            extraction_method="documented_public_atproto_api",
            confidence=0.99,
            title=_post_title(handle, text),
            author=author,
            text=text,
            markdown=text,
            media=media,
            metadata=metadata,
        )

    def _resolve_handle(self, handle: str) -> str:
        endpoint = (
            "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?"
            + urllib.parse.urlencode({"handle": handle})
        )
        _, payload = self.client.get_json(
            endpoint, headers={"Accept": "application/json"}
        )
        if not isinstance(payload, dict):
            raise ExtractorError("AT Protocol handle resolver returned invalid data.")
        did = str(payload.get("did") or "").strip()
        if not did.startswith("did:"):
            raise ExtractorError(f"Could not resolve Bluesky handle: {handle}")
        return did


def _strong_ref_uri(value: Any) -> str | None:
    if isinstance(value, dict):
        uri = value.get("uri")
        if isinstance(uri, str) and uri:
            return uri
    return None


def _post_title(handle: str, text: str) -> str:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if len(first_line) > 96:
        first_line = first_line[:93].rstrip() + "..."
    if first_line:
        return f"@{handle}: {first_line}"
    return f"@{handle} on Bluesky"


def _collect_embed_media(embed: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(kind: str, url: Any, **extra: Any) -> None:
        if not isinstance(url, str) or not url or url in seen:
            return
        seen.add(url)
        item: dict[str, Any] = {"type": kind, "url": url}
        item.update({key: value for key, value in extra.items() if value not in (None, "")})
        items.append(item)

    def visit(node: Any) -> None:
        if not isinstance(node, dict):
            return
        node_type = str(node.get("$type") or "")

        images = node.get("images")
        if isinstance(images, list):
            for image in images:
                if not isinstance(image, dict):
                    continue
                add(
                    "image",
                    image.get("fullsize") or image.get("thumb"),
                    thumbnail_url=image.get("thumb"),
                    alt=image.get("alt"),
                    aspect_ratio=image.get("aspectRatio"),
                )

        external = node.get("external")
        if isinstance(external, dict):
            add(
                "external",
                external.get("uri"),
                title=external.get("title"),
                description=external.get("description"),
                thumbnail_url=external.get("thumb"),
            )

        playlist = node.get("playlist")
        if isinstance(playlist, str):
            add(
                "video_playlist",
                playlist,
                thumbnail_url=node.get("thumbnail"),
                alt=node.get("alt"),
                aspect_ratio=node.get("aspectRatio"),
            )

        media = node.get("media")
        if isinstance(media, dict):
            visit(media)

        record = node.get("record")
        if isinstance(record, dict) and node_type.endswith("recordWithMedia#view"):
            visit(record)

    visit(embed)
    return items


def _extract_quoted_record(embed: Any) -> dict[str, Any] | None:
    if not isinstance(embed, dict):
        return None

    record = embed.get("record")
    if not isinstance(record, dict):
        return None

    if isinstance(record.get("record"), dict):
        record = record["record"]

    uri = record.get("uri")
    author = record.get("author")
    value = record.get("value")

    result: dict[str, Any] = {}
    if isinstance(uri, str):
        result["uri"] = uri
    if isinstance(author, dict):
        result["author"] = {
            "did": author.get("did"),
            "handle": author.get("handle"),
            "display_name": author.get("displayName"),
        }
    if isinstance(value, dict):
        result["text"] = value.get("text")
        result["created_at"] = value.get("createdAt")

    return result or None
