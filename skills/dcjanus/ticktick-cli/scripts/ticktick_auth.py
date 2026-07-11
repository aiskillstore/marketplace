from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from datetime import UTC, date, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any


DEFAULT_SCOPE = "tasks:read tasks:write"
ENV_TOKEN_FILE = "TICKTICK_TOKEN_FILE"


class AuthError(RuntimeError):
    pass


@dataclass(frozen=True)
class AuthEndpoints:
    authorization_endpoint: str
    token_endpoint: str
    registration_endpoint: str


def default_token_file() -> Path:
    configured = os.environ.get(ENV_TOKEN_FILE)
    if configured:
        return Path(configured).expanduser()
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home).expanduser() / "ticktick-cli" / "token.json"
    return Path.home() / ".config" / "ticktick-cli" / "token.json"


def auth_base_url_for_api_base(base_url: str) -> str:
    parsed = urllib.parse.urlparse(base_url)
    host = parsed.netloc.lower()
    if "ticktick.com" in host:
        return "https://ticktick.com"
    return "https://dida365.com"


def load_token_payload(
    base_url: str | None = None, token_file: Path | None = None
) -> dict[str, Any] | None:
    path = token_file or default_token_file()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as exc:
        raise AuthError(f"Failed to read token file: {path}") from exc
    if not isinstance(payload, dict):
        raise AuthError(f"Invalid token file payload: {path}")
    if base_url is not None and payload.get("base_url") != base_url:
        return None
    return payload


def token_expiry_info(
    payload: dict[str, Any], now: int | None = None
) -> dict[str, Any]:
    created_at = payload.get("created_at")
    expires_in = payload.get("expires_in")
    if not isinstance(created_at, (int, float)) or not isinstance(
        expires_in, (int, float)
    ):
        return {
            "expires_at": None,
            "expired": None,
        }
    expires_at_epoch = int(created_at + expires_in)
    current_time = int(time.time()) if now is None else now
    seconds_remaining = expires_at_epoch - current_time
    relative = format_relative_duration(seconds_remaining)
    return {
        "expires_at": (
            f"{datetime.fromtimestamp(expires_at_epoch, UTC).isoformat()} ({relative})"
        ),
        "expired": seconds_remaining <= 0,
    }


def format_relative_duration(seconds: int) -> str:
    abs_seconds = abs(seconds)
    if abs_seconds >= 86400:
        value = abs_seconds // 86400
        unit = "d"
    elif abs_seconds >= 3600:
        value = abs_seconds // 3600
        unit = "h"
    elif abs_seconds >= 60:
        value = abs_seconds // 60
        unit = "m"
    else:
        value = abs_seconds
        unit = "s"
    if seconds < 0:
        return f"expired {value}{unit} ago"
    return f"in {value}{unit}"


def remove_stored_token(token_file: Path | None = None) -> bool:
    path = token_file or default_token_file()
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise AuthError(f"Failed to remove token file: {path}") from exc


def _request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    content_type: str = "application/json",
) -> dict[str, Any]:
    body = None
    if payload is not None:
        if content_type == "application/x-www-form-urlencoded":
            body = urllib.parse.urlencode(payload).encode()
        else:
            body = json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        method=method,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": content_type,
            "User-Agent": "ticktick-cli/0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise AuthError(f"Request failed: {exc.code} {detail}") from exc
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AuthError(f"Invalid JSON response from {url}") from exc
    if not isinstance(parsed, dict):
        raise AuthError(f"Unexpected JSON response from {url}")
    return parsed


def discover_endpoints(auth_base_url: str) -> AuthEndpoints:
    metadata_url = auth_base_url.rstrip("/") + "/.well-known/oauth-authorization-server"
    payload = _request_json("GET", metadata_url)
    try:
        return AuthEndpoints(
            authorization_endpoint=payload["authorization_endpoint"],
            token_endpoint=payload["token_endpoint"],
            registration_endpoint=payload["registration_endpoint"],
        )
    except KeyError as exc:
        raise AuthError(f"Missing OAuth metadata field: {exc}") from exc


def default_client_name() -> str:
    today = date.today().isoformat()
    hostname = socket.gethostname().strip().split(".")[0]
    if not hostname:
        return f"ticktick-cli ({today})"
    return f"ticktick-cli ({hostname}, {today})"


def register_client(
    endpoints: AuthEndpoints, redirect_uri: str, scope: str, client_name: str
) -> str:
    payload = _request_json(
        "POST",
        endpoints.registration_endpoint,
        {
            "client_name": client_name,
            "redirect_uris": [redirect_uri],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
            "scope": scope,
        },
    )
    client_id = payload.get("client_id")
    if not isinstance(client_id, str) or not client_id:
        raise AuthError("Dynamic registration did not return client_id.")
    return client_id


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        self.server.oauth_result = {key: values[0] for key, values in query.items()}  # type: ignore[attr-defined]
        if "error" in query:
            body = callback_page_html("failed")
            status = 400
        else:
            body = callback_page_html("complete")
            status = 200
        body_bytes = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def callback_page_html(status: str) -> str:
    success = status == "complete"
    title_en = "Authorization complete" if success else "Authorization failed"
    title_zh = "授权已完成" if success else "授权失败"
    message_en = (
        "ticktick-cli has received the authorization result. You can close this page."
        if success
        else "ticktick-cli could not complete authorization. You can close this page and retry."
    )
    message_zh = (
        "ticktick-cli 已收到授权结果，可以关闭此页面。"
        if success
        else "ticktick-cli 未能完成授权，可以关闭此页面后重试。"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title_en}</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #1f2937;
      background: #f8fafc;
    }}
    main {{
      width: min(420px, calc(100vw - 32px));
      padding: 28px;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      background: #ffffff;
      box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 22px;
      font-weight: 650;
    }}
    p {{
      margin: 0;
      font-size: 14px;
      line-height: 1.5;
      color: #4b5563;
    }}
  </style>
</head>
<body>
  <main>
    <h1 data-en="{title_en}" data-zh="{title_zh}">{title_en}</h1>
    <p data-en="{message_en}" data-zh="{message_zh}">{message_en}</p>
  </main>
  <script>
    const language = navigator.language || "";
    const locale = language.toLowerCase().startsWith("zh") ? "zh" : "en";
    document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
    document.querySelectorAll("[data-en]").forEach((node) => {{
      node.textContent = node.dataset[locale];
    }});
  </script>
</body>
</html>"""


def exchange_code_for_token(
    endpoints: AuthEndpoints,
    client_id: str,
    code: str,
    redirect_uri: str,
    code_verifier: str,
    scope: str,
) -> dict[str, Any]:
    payload = _request_json(
        "POST",
        endpoints.token_endpoint,
        {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
            "scope": scope,
        },
        content_type="application/x-www-form-urlencoded",
    )
    access_token = payload.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise AuthError("Token endpoint did not return access_token.")
    return payload


def login(
    base_url: str,
    scope: str = DEFAULT_SCOPE,
    open_browser: bool = True,
    timeout_seconds: int = 180,
    token_file: Path | None = None,
    client_name: str | None = None,
) -> Path:
    auth_base_url = auth_base_url_for_api_base(base_url)
    endpoints = discover_endpoints(auth_base_url)
    effective_client_name = client_name or default_client_name()
    callback_server = HTTPServer(("127.0.0.1", 0), OAuthCallbackHandler)
    callback_server.timeout = timeout_seconds
    port = callback_server.server_port
    redirect_uri = f"http://127.0.0.1:{port}/oauth/callback"
    client_id = register_client(
        endpoints,
        redirect_uri,
        scope,
        effective_client_name,
    )
    code_verifier, code_challenge = _pkce_pair()
    state = secrets.token_urlsafe(24)
    authorization_url = (
        endpoints.authorization_endpoint
        + "?"
        + urllib.parse.urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
        )
    )
    if open_browser:
        webbrowser.open(authorization_url)
    print("Open this URL to authorize ticktick-cli:")
    print(authorization_url)
    try:
        callback_server.handle_request()
        result = getattr(callback_server, "oauth_result", None)
    finally:
        callback_server.server_close()
    if not isinstance(result, dict):
        raise AuthError("Timed out waiting for OAuth callback.")
    if result.get("state") != state:
        raise AuthError("OAuth state mismatch.")
    if result.get("error"):
        raise AuthError(f"Authorization failed: {result.get('error')}")
    code = result.get("code")
    if not isinstance(code, str) or not code:
        raise AuthError("OAuth callback did not include authorization code.")
    token_payload = exchange_code_for_token(
        endpoints=endpoints,
        client_id=client_id,
        code=code,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
        scope=scope,
    )
    stored = {
        **token_payload,
        "base_url": base_url,
        "auth_base_url": auth_base_url,
        "client_id": client_id,
        "client_name": effective_client_name,
        "scope": scope,
        "created_at": int(time.time()),
    }
    path = token_file or default_token_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(stored, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    path.chmod(0o600)
    return path
