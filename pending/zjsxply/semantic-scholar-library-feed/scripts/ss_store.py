#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen

SEMANTIC_SCHOLAR_ORIGIN = "https://www.semanticscholar.org"
GRAPH_API_ORIGIN = "https://api.semanticscholar.org"
DEFAULT_COOKIE_DIR = Path.home() / ".auth"
DEFAULT_COOKIE_PATH = DEFAULT_COOKIE_DIR / "semantic-scholar.cookies.json"
DEFAULT_COOKIE_HEADER_PATH = DEFAULT_COOKIE_DIR / "semantic-scholar.cookie-header.txt"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 60
REQUIRED_COOKIE_NAMES = ("sid", "s2")
DATA_PATTERN = re.compile(r"var DATA = '([^']+)'")


@dataclass
class HttpResponse:
    status: int
    url: str
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json_body(self) -> Any:
        if not self.body:
            return None
        return json.loads(self.text)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_cookie_path(cookie_path: str | Path | None = None) -> Path:
    if cookie_path is None:
        return DEFAULT_COOKIE_PATH
    return Path(cookie_path).expanduser().resolve()


def header_path_for_cookie_path(cookie_path: str | Path | None = None) -> Path:
    path = normalize_cookie_path(cookie_path)
    if path == DEFAULT_COOKIE_PATH:
        return DEFAULT_COOKIE_HEADER_PATH

    name = path.name
    if name.endswith(".cookies.json"):
        header_name = name[: -len(".cookies.json")] + ".cookie-header.txt"
    elif name.endswith(".json"):
        header_name = name[:-len(".json")] + ".cookie-header.txt"
    else:
        header_name = name + ".cookie-header.txt"
    return path.with_name(header_name)


def ensure_cookie_dir(path: str | Path = DEFAULT_COOKIE_DIR) -> Path:
    cookie_dir = Path(path).expanduser().resolve()
    cookie_dir.mkdir(parents=True, exist_ok=True)
    return cookie_dir


def mask_secret(value: str, keep: int = 4) -> str:
    if len(value) <= keep * 2:
        return "*" * len(value)
    return f"{value[:keep]}...{value[-keep:]}"


def filter_semantic_scholar_cookies(cookies: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for cookie in cookies:
        name = str(cookie.get("name", "")).strip()
        domain = str(cookie.get("domain", "")).lower()
        if not name:
            continue
        if "semanticscholar.org" not in domain and domain not in {"", "localhost"}:
            continue
        filtered.append(cookie)
    return filtered


def cookie_is_expired(cookie: dict[str, Any], now_ts: float | None = None) -> bool:
    expires = cookie.get("expires")
    if expires in (None, "", -1):
        return False
    try:
        expires_value = float(expires)
    except (TypeError, ValueError):
        return False
    if expires_value <= 0:
        return False
    if now_ts is None:
        now_ts = datetime.now(timezone.utc).timestamp()
    return expires_value <= now_ts


def cookie_header_from_cookies(cookies: Iterable[dict[str, Any]]) -> str:
    pairs: list[str] = []
    seen: set[str] = set()
    for cookie in cookies:
        name = str(cookie.get("name", "")).strip()
        if not name or cookie_is_expired(cookie) or name in seen:
            continue
        value = str(cookie.get("value", ""))
        pairs.append(f"{name}={value}")
        seen.add(name)
    return "; ".join(pairs)


def parse_cookie_header(header: str, domain: str = ".semanticscholar.org") -> list[dict[str, Any]]:
    cookies: list[dict[str, Any]] = []
    for part in header.split(";"):
        chunk = part.strip()
        if not chunk or "=" not in chunk:
            continue
        name, value = chunk.split("=", 1)
        cookies.append(
            {
                "name": name.strip(),
                "value": value.strip(),
                "domain": domain,
                "path": "/",
                "secure": True,
                "httpOnly": False,
                "sameSite": "Lax",
            }
        )
    return cookies


def build_cookie_bundle(
    cookies: Iterable[dict[str, Any]],
    *,
    source: str,
    user_agent: str = DEFAULT_USER_AGENT,
    note: str | None = None,
) -> dict[str, Any]:
    normalized = filter_semantic_scholar_cookies(cookies)
    bundle = {
        "source": source,
        "origin": SEMANTIC_SCHOLAR_ORIGIN,
        "updatedAt": now_utc_iso(),
        "userAgent": user_agent,
        "cookieNames": sorted(
            {str(cookie.get("name", "")).strip() for cookie in normalized if cookie.get("name")}
        ),
        "cookieHeader": cookie_header_from_cookies(normalized),
        "cookies": normalized,
    }
    if note:
        bundle["note"] = note
    return bundle


def save_cookie_bundle(
    bundle: dict[str, Any],
    cookie_path: str | Path | None = None,
) -> tuple[Path, Path]:
    path = normalize_cookie_path(cookie_path)
    ensure_cookie_dir(path.parent)
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n")
    header_path = header_path_for_cookie_path(path)
    header = str(bundle.get("cookieHeader", "")).strip()
    header_path.write_text(f"{header}\n")
    return path, header_path


def load_cookie_bundle(cookie_path: str | Path | None = None) -> dict[str, Any]:
    path = normalize_cookie_path(cookie_path)
    if not path.exists():
        raise FileNotFoundError(f"Cookie file not found: {path}")
    bundle = json.loads(path.read_text())
    if not isinstance(bundle, dict):
        raise ValueError(f"Cookie bundle is not a JSON object: {path}")
    return bundle


def cookie_header_from_bundle(bundle: dict[str, Any]) -> str:
    header = str(bundle.get("cookieHeader", "")).strip()
    if header:
        return header
    cookies = bundle.get("cookies") or []
    if not isinstance(cookies, list):
        raise ValueError("Cookie bundle field 'cookies' must be a list.")
    return cookie_header_from_cookies(cookies)


def missing_required_cookies(bundle: dict[str, Any]) -> list[str]:
    names = {str(name) for name in bundle.get("cookieNames") or []}
    if not names and isinstance(bundle.get("cookies"), list):
        names = {
            str(cookie.get("name", "")).strip()
            for cookie in bundle["cookies"]
            if isinstance(cookie, dict) and cookie.get("name")
        }
    return [name for name in REQUIRED_COOKIE_NAMES if name not in names]


def build_auth_headers(
    bundle: dict[str, Any] | None = None,
    *,
    accept: str,
    referer: str | None = None,
    content_type: str | None = None,
) -> dict[str, str]:
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": accept,
    }
    if bundle is not None:
        headers["Cookie"] = cookie_header_from_bundle(bundle)
        user_agent = str(bundle.get("userAgent", "")).strip()
        if user_agent:
            headers["User-Agent"] = user_agent
    if referer:
        headers["Referer"] = referer
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | list[Any] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> HttpResponse:
    payload = None
    request_headers = dict(headers or {})
    if json_body is not None:
        payload = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    request_headers.setdefault("User-Agent", DEFAULT_USER_AGENT)
    req = Request(url, data=payload, headers=request_headers, method=method.upper())
    try:
        with urlopen(req, timeout=timeout) as response:
            return HttpResponse(
                status=response.status,
                url=response.geturl(),
                headers=dict(response.headers.items()),
                body=response.read(),
            )
    except HTTPError as exc:
        return HttpResponse(
            status=exc.code,
            url=exc.geturl(),
            headers=dict(exc.headers.items()),
            body=exc.read(),
        )
    except URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def require_ok(response: HttpResponse, context: str) -> HttpResponse:
    if 200 <= response.status < 300:
        return response
    snippet = response.text.replace("\n", " ").strip()[:400]
    raise RuntimeError(f"{context} failed with HTTP {response.status}: {snippet}")


def fetch_html(
    url: str,
    bundle: dict[str, Any],
    *,
    referer: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    response = request(
        url,
        headers=build_auth_headers(bundle, accept="text/html,application/xhtml+xml", referer=referer),
        timeout=timeout,
    )
    require_ok(response, f"Fetching HTML from {url}")
    return response.text


def fetch_json(
    url: str,
    bundle: dict[str, Any] | None = None,
    *,
    method: str = "GET",
    referer: str | None = None,
    json_body: dict[str, Any] | list[Any] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    response = request(
        url,
        method=method,
        headers=build_auth_headers(
            bundle,
            accept="application/json, text/plain, */*",
            referer=referer,
        ),
        json_body=json_body,
        timeout=timeout,
    )
    require_ok(response, f"Fetching JSON from {url}")
    return response.json_body()


def extract_data_blob(html: str) -> str:
    match = DATA_PATTERN.search(html)
    if not match:
        raise RuntimeError("Could not find `var DATA = '...'` in HTML.")
    return match.group(1)


def decode_var_data(blob: str) -> Any:
    padding = (-len(blob)) % 4
    decoded = base64.b64decode(blob + ("=" * padding)).decode("utf-8")
    return json.loads(unquote(decoded))


def decode_ssr_data_from_html(html: str) -> Any:
    return decode_var_data(extract_data_blob(html))


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def list_snapshot_names(value: Any) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for item in iter_dicts(value):
        for key in ("requestType", "requestName", "operationName"):
            name = item.get(key)
            if isinstance(name, str) and name and name not in seen:
                seen.add(name)
                names.append(name)
    return names


def find_snapshot(value: Any, *names: str) -> dict[str, Any] | None:
    wanted = set(names)
    for item in iter_dicts(value):
        for key in ("requestType", "requestName", "operationName"):
            name = item.get(key)
            if name in wanted:
                return item
    return None


def parse_query(path_or_url: str) -> dict[str, list[str]]:
    return parse_qs(urlparse(path_or_url).query)


def parse_folder_ids(path_or_url: str) -> list[str]:
    params = parse_query(path_or_url)
    folder_ids: list[str] = []
    for raw in params.get("folderIds", []):
        for item in raw.split(","):
            value = item.strip()
            if value:
                folder_ids.append(value)
    return folder_ids


def parse_window_utc(path_or_url: str) -> str | None:
    values = parse_query(path_or_url).get("windowUTC", [])
    if not values:
        return None
    value = values[0].strip()
    return value or None


def count_papers(days: Iterable[dict[str, Any]]) -> int:
    total = 0
    for day in days:
        papers = day.get("papers") if isinstance(day, dict) else None
        if isinstance(papers, list):
            total += len(papers)
    return total
