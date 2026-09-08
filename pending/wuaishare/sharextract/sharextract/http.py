from __future__ import annotations

import http.client
import ipaddress
import json
import os
import socket
import ssl
import urllib.parse
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


def _trusted_proxy_enabled() -> bool:
    return os.environ.get("SHAREXTRACT_TRUST_PROXY", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def validate_public_url(url: str, *, resolve_dns: bool | None = None) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeURL("Only http:// and https:// URLs are supported.")
    if not parsed.hostname:
        raise UnsafeURL("URL has no hostname.")

    host = parsed.hostname.strip().rstrip(".")
    lowered = host.lower()
    if (
        lowered in {"localhost", "localhost.localdomain"}
        or lowered.endswith(".localhost")
        or lowered.endswith(".local")
    ):
        raise UnsafeURL("Localhost/local-network hostnames are blocked.")

    literal_ip = _parse_ip(host)
    if literal_ip is not None:
        _reject_non_public_ip(literal_ip)
        return url

    if resolve_dns is None:
        resolve_dns = True

    if not resolve_dns:
        if not _trusted_proxy_enabled():
            raise UnsafeURL(
                "Skipping local DNS validation requires SHAREXTRACT_TRUST_PROXY=1 "
                "and a trusted outbound proxy."
            )
        return url

    _resolve_public_endpoints(
        host,
        parsed.port or (443 if parsed.scheme == "https" else 80),
    )
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


def _resolve_public_endpoints(
    host: str,
    port: int,
) -> list[tuple[int, int, int, tuple]]:
    """Resolve once and return only public TCP endpoints.

    The returned socket addresses are later used directly for the connection so
    DNS cannot be resolved a second time between validation and connect.
    """

    try:
        addresses = socket.getaddrinfo(
            host,
            port,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise UnsafeURL(f"Could not resolve host: {host}") from exc

    endpoints: list[tuple[int, int, int, tuple]] = []
    seen: set[tuple[int, str, int]] = set()
    for family, socktype, proto, _canonname, sockaddr in addresses:
        ip = ipaddress.ip_address(sockaddr[0])
        _reject_non_public_ip(ip)
        key = (family, str(ip), int(sockaddr[1]))
        if key in seen:
            continue
        seen.add(key)
        endpoints.append((family, socktype, proto, sockaddr))

    if not endpoints:
        raise UnsafeURL(f"Host resolved to no usable public TCP endpoints: {host}")
    return endpoints


def _connect_public_socket(host: str, port: int, timeout: float) -> socket.socket:
    endpoints = _resolve_public_endpoints(host, port)
    last_error: OSError | None = None

    for family, socktype, proto, sockaddr in endpoints:
        sock = socket.socket(family, socktype, proto)
        sock.settimeout(timeout)
        try:
            sock.connect(sockaddr)
            peer_ip = ipaddress.ip_address(sock.getpeername()[0])
            _reject_non_public_ip(peer_ip)
            return sock
        except UnsafeURL:
            sock.close()
            raise
        except OSError as exc:
            last_error = exc
            sock.close()

    if last_error is not None:
        raise FetchError(f"Could not connect to public endpoint for {host}: {last_error}")
    raise FetchError(f"Could not connect to public endpoint for {host}.")


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def connect(self) -> None:
        self.sock = _connect_public_socket(self.host, self.port, self.timeout)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def connect(self) -> None:
        raw_sock = _connect_public_socket(self.host, self.port, self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw_sock, server_hostname=self.host)
            peer_ip = ipaddress.ip_address(self.sock.getpeername()[0])
            _reject_non_public_ip(peer_ip)
        except Exception:
            raw_sock.close()
            raise


class SafeHttpClient:
    def __init__(
        self,
        *,
        timeout: float = 20.0,
        max_bytes: int = 8 * 1024 * 1024,
        max_redirects: int = 5,
        user_agent: str = f"ShareXtract/{__version__} (+https://github.com/wuaishare/sharextract)",
    ) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects
        self.user_agent = user_agent

    def _request_once(
        self,
        url: str,
        *,
        method: str,
        headers: dict[str, str],
        data: bytes | None,
    ) -> tuple[int, str, str | None, str, bytes]:
        validate_public_url(url)
        parsed = urllib.parse.urlsplit(url)
        assert parsed.hostname is not None

        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if parsed.scheme == "https":
            connection: http.client.HTTPConnection = _PinnedHTTPSConnection(
                parsed.hostname,
                port,
                timeout=self.timeout,
                context=ssl.create_default_context(),
            )
        else:
            connection = _PinnedHTTPConnection(
                parsed.hostname,
                port,
                timeout=self.timeout,
            )

        target = urllib.parse.urlunsplit(
            ("", "", parsed.path or "/", parsed.query, "")
        )
        try:
            connection.request(method, target, body=data, headers=headers)
            response = connection.getresponse()
            body = response.read(self.max_bytes + 1)
            if len(body) > self.max_bytes:
                raise FetchError(f"Response exceeded {self.max_bytes} bytes.")
            return (
                response.status,
                response.reason or "",
                response.getheader("Location"),
                response.getheader("Content-Type", ""),
                body,
            )
        except FetchError:
            raise
        except (
            OSError,
            ssl.SSLError,
            http.client.HTTPException,
            TimeoutError,
        ) as exc:
            raise FetchError(f"{method} failed for {url}: {exc}") from exc
        finally:
            connection.close()

    def _request(
        self,
        url: str,
        *,
        method: str,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
    ) -> HttpResponse:
        current_url = validate_public_url(url)
        current_method = method.upper()
        current_data = data
        request_headers = {"User-Agent": self.user_agent, "Accept": "*/*"}
        if headers:
            request_headers.update(headers)

        for redirect_index in range(self.max_redirects + 1):
            status, reason, location, content_type, body = self._request_once(
                current_url,
                method=current_method,
                headers=request_headers,
                data=current_data,
            )

            if status in {301, 302, 303, 307, 308} and location:
                if redirect_index >= self.max_redirects:
                    raise FetchError(
                        f"{method} exceeded {self.max_redirects} redirects for {url}."
                    )
                next_url = urllib.parse.urljoin(current_url, location)
                validate_public_url(next_url)

                if status == 303 or (
                    status in {301, 302}
                    and current_method not in {"GET", "HEAD"}
                ):
                    current_method = "GET"
                    current_data = None
                    request_headers = dict(request_headers)
                    request_headers.pop("Content-Type", None)
                    request_headers.pop("Content-Length", None)

                current_url = next_url
                continue

            if status >= 400:
                raise FetchError(
                    f"{current_method} failed for {current_url}: HTTP {status} {reason}".rstrip()
                )

            return HttpResponse(
                url=current_url,
                content_type=content_type,
                body=body,
            )

        raise FetchError(f"{method} failed for {url}: redirect handling exhausted.")

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
        return self._request(url, method="GET", headers=headers).url

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        return self.get(url, headers=headers)

    def get_json(self, url: str, headers: dict[str, str] | None = None):
        response = self.get(url, headers=headers)
        try:
            return response, json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise FetchError(
                f"Expected JSON from {url}, got {response.content_type or 'unknown type'}."
            ) from exc
