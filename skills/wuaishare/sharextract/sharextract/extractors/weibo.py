from __future__ import annotations

import html
import re
import urllib.parse
from datetime import datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import Any

from sharextract.http import FetchError
from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_BID_RE = re.compile(r"^[A-Za-z0-9]{5,32}$")
_MOBILE_HEADERS = {
    "Accept": "application/json,text/plain,*/*",
    "MWeibo-Pwa": "1",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://m.weibo.cn/",
}
_BLOCK_TAGS = {"br", "p", "div", "li", "blockquote"}


class _WeiboTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_startendtag(self, tag: str, attrs) -> None:
        if tag.lower() in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _BLOCK_TAGS and tag != "br":
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    @property
    def text(self) -> str:
        value = html.unescape("".join(self.parts))
        value = re.sub(r"\n+", "\n", value)
        lines = [
            re.sub(r"[ \t\f\v]+", " ", line).strip()
            for line in value.splitlines()
        ]
        return "\n".join(line for line in lines if line).strip()


class WeiboStatusExtractor(Extractor):
    """Extract one public Weibo status through the anonymous mobile PWA JSON route."""

    name = "weibo-status"
    priority = 37

    def supports(self, url: str) -> bool:
        return self._bid(url, strict=False) is not None

    def extract(self, url: str) -> ExtractedContent:
        bid = self._bid(url, strict=True)
        endpoint = (
            "https://m.weibo.cn/statuses/show?id="
            + urllib.parse.quote(bid, safe="")
        )
        _, payload = self.client.get_json(endpoint, headers=_MOBILE_HEADERS)
        if not isinstance(payload, dict):
            raise ExtractorError("Weibo public status route returned a non-object payload.")
        if payload.get("ok") != 1:
            raise ExtractorError(
                "Weibo public status route did not return an anonymously readable status."
            )
        status = payload.get("data")
        if not isinstance(status, dict):
            raise ExtractorError("Weibo public status payload contained no data object.")

        actual_bid = str(status.get("bid") or bid).strip()
        if not _BID_RE.fullmatch(actual_bid):
            actual_bid = bid

        body_html = str(status.get("text") or "")
        method = "first_party_public_mobile_json"
        warnings: list[str] = []

        if status.get("isLongText") is True:
            extended = self._read_extended(actual_bid)
            if extended:
                body_html = extended
                method = "first_party_public_mobile_json_plus_extend"
            else:
                warnings.append(
                    "Weibo marked this status as long text, but the public extend route "
                    "did not return readable longTextContent; the status/show text was used."
                )

        text = _html_to_text(body_html)
        if not text:
            raise ExtractorError("Weibo public status contained no readable text.")

        user = status.get("user")
        user = user if isinstance(user, dict) else {}
        author = str(user.get("screen_name") or "").strip()

        media = _collect_media(status)
        retweeted = status.get("retweeted_status")
        retweeted_meta = (
            _normalize_retweeted_status(retweeted)
            if isinstance(retweeted, dict)
            else None
        )

        canonical = _canonical_url(status, actual_bid)
        created_at = _parse_weibo_time(status.get("created_at"))

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="weibo",
            kind="social_post",
            extraction_method=method,
            confidence=0.99,
            title=_title(author, text),
            author=author,
            text=text,
            markdown=_render_markdown(author, text, retweeted_meta),
            html=body_html,
            media=media,
            metadata={
                "status_id": str(status.get("id") or status.get("mid") or ""),
                "mid": str(status.get("mid") or status.get("id") or ""),
                "bid": actual_bid,
                "created_at": created_at,
                "source": _html_to_text(str(status.get("source") or "")),
                "is_long_text": bool(status.get("isLongText")),
                "author": _normalize_user(user),
                "stats": {
                    "repost_count": status.get("reposts_count"),
                    "comment_count": status.get("comments_count"),
                    "attitude_count": status.get("attitudes_count"),
                    "favorite_count": status.get("favorites_count"),
                },
                "retweeted_status": retweeted_meta,
                "public_status_endpoint": endpoint,
                "endpoint_documentation": "undocumented",
                "requires_login": False,
                "uses_account_cookies": False,
            },
            warnings=warnings
            + [
                "Weibo status content was read from the anonymous first-party "
                "mobile PWA JSON route. This public frontend route is undocumented "
                "and may change."
            ],
        )

    def _read_extended(self, bid: str) -> str:
        endpoint = (
            "https://m.weibo.cn/statuses/extend?id="
            + urllib.parse.quote(bid, safe="")
        )
        try:
            _, payload = self.client.get_json(endpoint, headers=_MOBILE_HEADERS)
        except FetchError:
            return ""
        if not isinstance(payload, dict) or payload.get("ok") != 1:
            return ""
        data = payload.get("data")
        if not isinstance(data, dict):
            return ""
        content = data.get("longTextContent")
        return str(content or "").strip()

    def _bid(self, url: str, *, strict: bool) -> str | None:
        parsed = urllib.parse.urlsplit(url)
        host = self.hostname(url)
        parts = [
            urllib.parse.unquote(part)
            for part in parsed.path.split("/")
            if part
        ]
        bid: str | None = None

        if host in {"weibo.com", "www.weibo.com"}:
            if len(parts) >= 2 and parts[0] == "status":
                bid = parts[1]
            elif (
                len(parts) >= 2
                and parts[0].lower()
                not in {
                    "u",
                    "n",
                    "profile",
                    "tv",
                    "ajax",
                    "search",
                    "hot",
                    "newlogin",
                    "login",
                    "signup",
                }
            ):
                bid = parts[1]
        elif host == "m.weibo.cn":
            if len(parts) >= 2 and parts[0] in {"detail", "status"}:
                bid = parts[1]

        if isinstance(bid, str):
            bid = bid.split("?", 1)[0].strip()
        if bid and _BID_RE.fullmatch(bid):
            return bid
        if strict:
            raise ExtractorError("Unsupported Weibo status URL.")
        return None


def _html_to_text(value: str) -> str:
    parser = _WeiboTextParser()
    try:
        parser.feed(value)
        parser.close()
        return parser.text
    except Exception:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(value))).strip()


def _collect_media(status: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    pics = status.get("pics")
    if isinstance(pics, list):
        for pic in pics:
            if not isinstance(pic, dict):
                continue
            large = pic.get("large")
            large = large if isinstance(large, dict) else {}
            url = str(large.get("url") or pic.get("url") or "").strip()
            if not url:
                continue
            url = _absolute_url(url)
            key = ("image", url)
            if key in seen:
                continue
            seen.add(key)
            item: dict[str, Any] = {
                "type": "image",
                "url": url,
            }
            pid = pic.get("pid")
            if pid:
                item["id"] = str(pid)
            geo = large.get("geo")
            geo = geo if isinstance(geo, dict) else pic.get("geo")
            if isinstance(geo, dict):
                width = _int_value(geo.get("width"))
                height = _int_value(geo.get("height"))
                if width is not None:
                    item["width"] = width
                if height is not None:
                    item["height"] = height
            result.append(item)

    page_info = status.get("page_info")
    if isinstance(page_info, dict):
        page_pic = page_info.get("page_pic")
        if isinstance(page_pic, dict):
            poster = str(
                page_pic.get("url")
                or page_pic.get("url_ori")
                or page_pic.get("url_default")
                or ""
            ).strip()
            if poster:
                poster = _absolute_url(poster)
                key = ("image", poster)
                if key not in seen:
                    seen.add(key)
                    result.append(
                        {
                            "type": "image",
                            "url": poster,
                            "role": "poster",
                        }
                    )

        media_info = page_info.get("media_info")
        if isinstance(media_info, dict):
            video_url = str(
                media_info.get("stream_url_hd")
                or media_info.get("stream_url")
                or media_info.get("h5_url")
                or ""
            ).strip()
            if video_url:
                video_url = _absolute_url(video_url)
                key = ("video", video_url)
                if key not in seen:
                    seen.add(key)
                    item = {
                        "type": "video",
                        "url": video_url,
                    }
                    duration = media_info.get("duration")
                    if isinstance(duration, (int, float)):
                        item["duration_seconds"] = duration
                    result.append(item)

        page_url = str(page_info.get("page_url") or "").strip()
        if page_url:
            page_url = _absolute_url(page_url)
            key = ("link", page_url)
            if key not in seen:
                seen.add(key)
                result.append(
                    {
                        "type": "link",
                        "url": page_url,
                        "title": str(page_info.get("page_title") or "").strip(),
                    }
                )

    return result


def _normalize_retweeted_status(status: dict[str, Any]) -> dict[str, Any]:
    user = status.get("user")
    user = user if isinstance(user, dict) else {}
    bid = str(status.get("bid") or "").strip()
    return {
        "id": str(status.get("id") or status.get("mid") or ""),
        "mid": str(status.get("mid") or status.get("id") or ""),
        "bid": bid,
        "canonical_url": _canonical_url(status, bid) if bid else None,
        "created_at": _parse_weibo_time(status.get("created_at")),
        "author": _normalize_user(user),
        "text": _html_to_text(str(status.get("text") or "")),
        "media": _collect_media(status),
        "stats": {
            "repost_count": status.get("reposts_count"),
            "comment_count": status.get("comments_count"),
            "attitude_count": status.get("attitudes_count"),
        },
    }


def _normalize_user(user: dict[str, Any]) -> dict[str, Any]:
    uid = user.get("id")
    uid_s = str(uid) if uid is not None else ""
    profile = str(user.get("profile_url") or "").strip()
    if profile:
        profile = _absolute_url(profile)
    elif uid_s:
        profile = f"https://weibo.com/u/{uid_s}"

    return {
        "id": uid_s,
        "screen_name": user.get("screen_name"),
        "description": user.get("description"),
        "profile_url": profile or None,
        "avatar_url": user.get("avatar_hd") or user.get("profile_image_url"),
        "verified": user.get("verified"),
        "verified_reason": user.get("verified_reason"),
        "followers_count": user.get("followers_count_str") or user.get("followers_count"),
        "statuses_count": user.get("statuses_count"),
    }


def _canonical_url(status: dict[str, Any], bid: str) -> str:
    user = status.get("user")
    user = user if isinstance(user, dict) else {}
    uid = user.get("id")
    if uid and bid:
        return f"https://weibo.com/{uid}/{bid}"
    if bid:
        return f"https://m.weibo.cn/detail/{bid}"
    mid = str(status.get("id") or status.get("mid") or "").strip()
    return f"https://m.weibo.cn/detail/{mid}" if mid else "https://weibo.com/"


def _parse_weibo_time(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    token = value.strip()
    try:
        dt = parsedate_to_datetime(token)
    except (TypeError, ValueError):
        dt = None
    if dt is None:
        try:
            dt = datetime.strptime(token, "%a %b %d %H:%M:%S %z %Y")
        except ValueError:
            return token
    return dt.isoformat()


def _title(author: str, text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    excerpt = compact[:80].rstrip()
    if len(compact) > 80:
        excerpt += "…"
    if author and excerpt:
        return f"{author}：{excerpt}"
    return excerpt or author or "Weibo post"


def _render_markdown(
    author: str,
    text: str,
    retweeted: dict[str, Any] | None,
) -> str:
    lines = [text.strip()]
    if retweeted and retweeted.get("text"):
        ret_author = retweeted.get("author")
        ret_author = ret_author if isinstance(ret_author, dict) else {}
        name = str(ret_author.get("screen_name") or "").strip()
        prefix = f"@{name}: " if name else ""
        lines.extend(["", f"> 转发自 {prefix}{retweeted['text']}"])
    return "\n".join(lines).strip()


def _absolute_url(value: str) -> str:
    token = html.unescape(value).strip()
    if token.startswith("//"):
        return "https:" + token
    if token.startswith("/"):
        return "https://m.weibo.cn" + token
    return token


def _int_value(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
