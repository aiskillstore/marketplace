from __future__ import annotations

import ipaddress
import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .version import __version__


class UnsafeURL(ValueError):
    pass


class FetchError(RuntimeError):
    pass


@dataclass(slots=True)
class HttpResponse:
    url: str
    content_type: str
    body: bytes

    @property
    def text(self) -> str:
        charset = "utf-8"
        if "charset=" in self.content_type.lower():
            charset = self.content_type.lower().split("charset=", 1)[1].split(";", 1)[0].strip()
        try:
            return self.body.decode(charset, errors="replace")
        except LookupError:
            return self.body.decode("utf-8", errors="replace")


def validate_public_url(url: str, *, resolve_dns: bool | None = None) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeURL("Only http:// and https:// URLs are supported.")
    if not parsed.hostname:
        raise UnsafeURL("URL has no hostname.")

    host = parsed.hostname.strip().rstrip(".")
    lowered = host.lower()
    if lowered in {"localhost", "localhost.localdomain"} or lowered.endswith(".localhost") or lowered.endswith(".local"):
        raise UnsafeURL("Localhost/local-network hostnames are blocked.")

    literal_ip = _parse_ip(host)
    if literal_ip is not None:
        _reject_non_public_ip(literal_ip)
        return url

    if resolve_dns is None:
        # urllib respects environment and OS proxy settings. With a configured
        # HTTP(S) proxy, local DNS may intentionally return a fake-IP range
        # (for example Clash/Surge 198.18.0.0/15). In that mode the proxy, not
        # this process, resolves the real destination, so pre-resolution would
        # create false positives. Literal private IPs remain blocked above.
        resolve_dns = not _has_proxy_for_url(url)

    if not resolve_dns:
        return url

    try:
        addresses = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise UnsafeURL(f"Could not resolve host: {host}") from exc

    for entry in addresses:
        _reject_non_public_ip(ipaddress.ip_address(entry[4][0]))
    return url


def _parse_ip(host: str):
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return None


def _reject_non_public_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        raise UnsafeURL(f"Non-public destination is blocked: {ip}")


def _has_proxy_for_url(url: str) -> bool:
    scheme = urllib.parse.urlsplit(url).scheme.lower()
    try:
        proxies = urllib.request.getproxies()
    except Exception:
        return False
    return bool(proxies.get(scheme) or proxies.get("all"))


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class SafeHttpClient:
    def __init__(
        self,
        *,
        timeout: float = 20.0,
        max_bytes: int = 8 * 1024 * 1024,
        user_agent: str = f"ShareXtract/{__version__} (+https://github.com/wuaishare/sharextract)",
    ) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.user_agent = user_agent
        self._opener = urllib.request.build_opener(_SafeRedirectHandler())

    def _request(
        self,
        url: str,
        *,
        method: str,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
    ) -> HttpResponse:
        validate_public_url(url)
        request_headers = {"User-Agent": self.user_agent, "Accept": "*/*"}
        if headers:
            request_headers.update(headers)
        req = urllib.request.Request(
            url,
            data=data,
            headers=request_headers,
            method=method,
        )
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                final_url = resp.geturl()
                validate_public_url(final_url)
                body = resp.read(self.max_bytes + 1)
                if len(body) > self.max_bytes:
                    raise FetchError(f"Response exceeded {self.max_bytes} bytes.")
                return HttpResponse(
                    url=final_url,
                    content_type=resp.headers.get("Content-Type", ""),
                    body=body,
                )
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            raise FetchError(f"{method} failed for {url}: {exc}") from exc

    def get(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        return self._request(url, method="GET", headers=headers)

    def post_form(
        self,
        url: str,
        fields: dict[str, str],
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        request_headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        if headers:
            request_headers.update(headers)
        data = urllib.parse.urlencode(fields).encode("utf-8")
        return self._request(
            url,
            method="POST",
            headers=request_headers,
            data=data,
        )

    def post_json(
        self,
        url: str,
        payload,
        headers: dict[str, str] | None = None,
    ):
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if headers:
            request_headers.update(headers)
        data = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        response = self._request(
            url,
            method="POST",
            headers=request_headers,
            data=data,
        )
        try:
            return response, json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise FetchError(
                f"Expected JSON from {url}, got {response.content_type or 'unknown type'}."
            ) from exc

    def resolve(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> str:
        validate_public_url(url)
        request_headers = {"User-Agent": self.user_agent, "Accept": "*/*"}
        if headers:
            request_headers.update(headers)
        req = urllib.request.Request(url, headers=request_headers, method="GET")
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                final_url = resp.geturl()
                validate_public_url(final_url)
                return final_url
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            raise FetchError(f"GET failed for {url}: {exc}") from exc

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        return self.get(url, headers=headers)

    def get_json(self, url: str, headers: dict[str, str] | None = None):
        response = self.get(url, headers=headers)
        try:
            return response, json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise FetchError(f"Expected JSON from {url}, got {response.content_type or 'unknown type'}.") from exc
