from __future__ import annotations

import html
import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_NOTE_ID_RE = re.compile(r"^[0-9a-fA-F]{24}$")
_INITIAL_STATE_MARKERS = (
    "window.__INITIAL_STATE__=",
    "window.__INITIAL_STATE__ = ",
)
_PAGE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
_SHORT_HOSTS = {
    "xhslink.com",
    "www.xhslink.com",
    "xhslink.cn",
    "www.xhslink.cn",
}


class XiaohongshuNoteExtractor(Extractor):
    """Extract public Xiaohongshu notes from tokenized anonymous SSR pages."""

    name = "xiaohongshu-note"
    priority = 39

    def supports(self, url: str) -> bool:
        host = self.hostname(url)
        if host in _SHORT_HOSTS:
            return bool(
                [
                    part
                    for part in urllib.parse.urlsplit(url).path.split("/")
                    if part
                ]
            )
        return self._note_id_from_url(url) is not None

    def extract(self, url: str) -> ExtractedContent:
        resolved = url
        if self.hostname(url) in _SHORT_HOSTS:
            resolved = self.client.resolve(url, headers=_PAGE_HEADERS)

        note_id = self._note_id_from_url(resolved)
        if note_id is None:
            raise ExtractorError(
                "Xiaohongshu share link did not resolve to a supported public note URL."
            )

        query = urllib.parse.parse_qs(
            urllib.parse.urlsplit(resolved).query,
            keep_blank_values=True,
        )
        token = _first(query.get("xsec_token"))
        source = _first(query.get("xsec_source"))
        if not token:
            raise ExtractorError(
                "Xiaohongshu public note URL has no current xsec_token. "
                "Use the platform's current Share / Copy Link URL. "
                "ShareXtract does not generate or refresh Xiaohongshu tokens."
            )

        canonical = _canonical_tokenized_url(
            resolved,
            note_id=note_id,
            token=token,
            source=source,
        )
        response = self.client.get_text(canonical, headers=_PAGE_HEADERS)
        final_path = urllib.parse.urlsplit(response.url).path
        if final_path.startswith("/404"):
            raise ExtractorError(
                "Xiaohongshu public share token is expired, unavailable, or the "
                "note is no longer anonymously readable. Use a fresh official share link."
            )

        state = _extract_initial_state(response.text)
        note = _extract_note(state, note_id)
        if note is None:
            raise ExtractorError(
                "Xiaohongshu public SSR page contained no readable note data. "
                "The share token may have expired or the frontend structure may have changed."
            )

        return _normalize_note(
            source_url=url,
            canonical_url=canonical,
            note_id=note_id,
            xsec_source=source,
            note=note,
        )

    def _note_id_from_url(self, url: str) -> str | None:
        parsed = urllib.parse.urlsplit(url)
        host = self.hostname(url)
        if host not in {
            "xiaohongshu.com",
            "www.xiaohongshu.com",
        }:
            return None
        parts = [
            urllib.parse.unquote(part)
            for part in parsed.path.split("/")
            if part
        ]
        candidate: str | None = None
        if len(parts) >= 2 and parts[0] == "explore":
            candidate = parts[1]
        elif (
            len(parts) >= 3
            and parts[:2] == ["discovery", "item"]
        ):
            candidate = parts[2]
        if candidate and _NOTE_ID_RE.fullmatch(candidate):
            return candidate.lower()
        return None


def _extract_initial_state(page_html: str) -> dict[str, Any]:
    raw = ""
    for marker in _INITIAL_STATE_MARKERS:
        pos = page_html.find(marker)
        if pos >= 0:
            raw = page_html[pos + len(marker) :]
            break
    if not raw:
        raise ExtractorError(
            "Xiaohongshu public page did not contain window.__INITIAL_STATE__."
        )

    normalized = _replace_bare_undefined(raw)
    try:
        value, _ = json.JSONDecoder().raw_decode(normalized)
    except json.JSONDecodeError as exc:
        raise ExtractorError(
            "Xiaohongshu public initial-state data was not readable JSON."
        ) from exc
    if not isinstance(value, dict):
        raise ExtractorError(
            "Xiaohongshu public initial-state data was not an object."
        )
    return value


def _replace_bare_undefined(value: str) -> str:
    """Replace JavaScript bare undefined tokens outside strings with JSON null."""
    out: list[str] = []
    index = 0
    in_string = False
    escaped = False

    while index < len(value):
        char = value[index]
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            out.append(char)
            index += 1
            continue

        if value.startswith("undefined", index):
            before = value[index - 1] if index else ""
            after_index = index + len("undefined")
            after = value[after_index] if after_index < len(value) else ""
            if not _identifier_char(before) and not _identifier_char(after):
                out.append("null")
                index = after_index
                continue

        out.append(char)
        index += 1

    return "".join(out)


def _identifier_char(value: str) -> bool:
    return bool(value) and (value.isalnum() or value in {"_", "$"})


def _extract_note(
    state: dict[str, Any],
    note_id: str,
) -> dict[str, Any] | None:
    note_state = state.get("note")
    if not isinstance(note_state, dict):
        return None
    detail_map = note_state.get("noteDetailMap")
    if not isinstance(detail_map, dict):
        return None

    entry = detail_map.get(note_id)
    if not isinstance(entry, dict):
        for candidate in detail_map.values():
            if not isinstance(candidate, dict):
                continue
            item = candidate.get("note")
            if (
                isinstance(item, dict)
                and str(item.get("noteId") or "").lower() == note_id
            ):
                entry = candidate
                break
    if not isinstance(entry, dict):
        return None

    note = entry.get("note")
    if not isinstance(note, dict):
        return None
    actual_id = str(note.get("noteId") or "").lower()
    if actual_id and actual_id != note_id:
        return None
    return note


def _normalize_note(
    *,
    source_url: str,
    canonical_url: str,
    note_id: str,
    xsec_source: str,
    note: dict[str, Any],
) -> ExtractedContent:
    title = str(note.get("title") or "").strip()
    description = str(note.get("desc") or "").strip()
    text = description or title
    user = note.get("user")
    user = user if isinstance(user, dict) else {}
    author = str(user.get("nickname") or user.get("nickName") or "").strip()
    note_type = str(note.get("type") or "normal").strip().lower()

    image_media = _image_media(note.get("imageList"))
    video_meta = _video_metadata(note.get("video"))
    media: list[dict[str, Any]] = []

    if note_type == "video" or video_meta:
        item: dict[str, Any] = {
            "type": "video",
            "url": canonical_url,
        }
        if video_meta.get("duration_seconds") is not None:
            item["duration_seconds"] = video_meta["duration_seconds"]
        if image_media:
            item["thumbnail_url"] = image_media[0]["url"]
        media.append(item)

    media.extend(image_media)

    tags = _tags(note.get("tagList"))
    interact = note.get("interactInfo")
    interact = interact if isinstance(interact, dict) else {}

    return ExtractedContent(
        source_url=source_url,
        canonical_url=canonical_url,
        platform="xiaohongshu",
        kind="note",
        extraction_method="first_party_public_ssr_initial_state",
        confidence=0.98,
        title=title,
        author=author,
        text=text,
        markdown=_markdown(title, description, tags),
        media=media,
        metadata={
            "note_id": note_id,
            "note_type": note_type,
            "created_at": _timestamp_ms(note.get("time")),
            "updated_at": _timestamp_ms(note.get("lastUpdateTime")),
            "ip_location": note.get("ipLocation"),
            "author": {
                "id": str(user.get("userId") or ""),
                "nickname": user.get("nickname") or user.get("nickName"),
                "avatar_url": _https_url(user.get("avatar")),
            },
            "stats": {
                "liked_count": interact.get("likedCount"),
                "collected_count": interact.get("collectedCount"),
                "comment_count": interact.get("commentCount"),
                "share_count": interact.get("shareCount"),
                "nice_count": interact.get("niceCount"),
            },
            "tags": tags,
            "video": {
                "duration_seconds": video_meta.get("duration_seconds"),
                "video_id": video_meta.get("video_id"),
            }
            if video_meta
            else None,
            "xsec_source": xsec_source or None,
            "public_share_token_consumed": True,
            "token_generated_by_sharextract": False,
            "requires_login": False,
            "uses_private_signature": False,
            "stream_urls_exported": False,
            "endpoint_documentation": "undocumented_public_ssr",
        },
        warnings=[
            "Xiaohongshu note content was read from first-party SSR initial state "
            "using the current public share token supplied by the share URL. "
            "This frontend structure is undocumented and may change.",
            "Xiaohongshu xsec_token values are transient. If this URL stops working, "
            "use a fresh official Share / Copy Link URL; ShareXtract will not generate "
            "or refresh the token.",
        ]
        + (
            [
                "Temporary video/subtitle stream URLs embedded in the public note "
                "state are intentionally not exported."
            ]
            if video_meta
            else []
        ),
    )


def _image_media(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    seen: set[str] = set()

    for image in value:
        if not isinstance(image, dict):
            continue
        url = str(
            image.get("urlDefault")
            or image.get("urlPre")
            or image.get("url")
            or ""
        ).strip()

        if not url:
            info = image.get("infoList")
            if isinstance(info, list):
                preferred: list[str] = []
                fallback: list[str] = []
                for item in info:
                    if not isinstance(item, dict):
                        continue
                    candidate = str(item.get("url") or "").strip()
                    if not candidate:
                        continue
                    if item.get("imageScene") == "WB_DFT":
                        preferred.append(candidate)
                    else:
                        fallback.append(candidate)
                url = next(iter(preferred or fallback), "")

        url = _https_url(url) or ""
        if not url or url in seen:
            continue
        seen.add(url)

        item: dict[str, Any] = {
            "type": "image",
            "url": url,
        }
        if image.get("fileId"):
            item["id"] = str(image["fileId"])
        width = _int_value(image.get("width"))
        height = _int_value(image.get("height"))
        if width is not None:
            item["width"] = width
        if height is not None:
            item["height"] = height
        result.append(item)

    return result


def _video_metadata(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}

    duration: float | None = None
    capa = value.get("capa")
    if isinstance(capa, dict):
        candidate = capa.get("duration")
        if isinstance(candidate, (int, float)):
            duration = float(candidate)

    media = value.get("media")
    media = media if isinstance(media, dict) else {}
    video = media.get("video")
    video = video if isinstance(video, dict) else {}
    if duration is None:
        candidate = video.get("duration")
        if isinstance(candidate, (int, float)):
            duration = float(candidate)

    video_id = value.get("videoId") or media.get("videoId") or video.get("videoId")
    if video_id is None:
        video_id = media.get("video_id") or video.get("video_id")

    result: dict[str, Any] = {}
    if duration is not None:
        result["duration_seconds"] = duration
    if video_id is not None:
        result["video_id"] = str(video_id)
    return result


def _tags(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        result.append(
            {
                "id": str(item.get("id") or ""),
                "name": name,
                "type": item.get("type"),
            }
        )
    return result


def _canonical_tokenized_url(
    resolved_url: str,
    *,
    note_id: str,
    token: str,
    source: str,
) -> str:
    parsed = urllib.parse.urlsplit(resolved_url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 3 and parts[:2] == ["discovery", "item"]:
        path = f"/discovery/item/{note_id}"
    else:
        path = f"/explore/{note_id}"
    query: list[tuple[str, str]] = [("xsec_token", token)]
    if source:
        query.append(("xsec_source", source))
    return urllib.parse.urlunsplit(
        (
            "https",
            "www.xiaohongshu.com",
            path,
            urllib.parse.urlencode(query),
            "",
        )
    )


def _markdown(
    title: str,
    description: str,
    tags: list[dict[str, Any]],
) -> str:
    parts: list[str] = []
    if title:
        parts.append(f"# {title}")
    if description:
        parts.append(description)
    if tags:
        names = [
            f"#{item['name']}"
            for item in tags
            if str(item.get("name") or "").strip()
        ]
        if names:
            parts.append(" ".join(names))
    return "\n\n".join(parts).strip()


def _timestamp_ms(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(
            float(value) / 1000.0,
            timezone.utc,
        ).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _https_url(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    token = html.unescape(value).strip()
    if token.startswith("//"):
        return "https:" + token
    if token.startswith("http://"):
        return "https://" + token[len("http://") :]
    if token.startswith("https://"):
        return token
    return None


def _int_value(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _first(values: Any) -> str:
    if isinstance(values, list) and values:
        return str(values[0] or "").strip()
    return ""
