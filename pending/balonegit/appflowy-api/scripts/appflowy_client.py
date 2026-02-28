from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class AppFlowyError(RuntimeError):
    def __init__(self, message: str, status: Optional[int] = None, response: Any = None):
        super().__init__(message)
        self.status = status
        self.response = response


def now_millis() -> int:
    return int(time.time() * 1000)


def new_device_id() -> str:
    return str(uuid.uuid4())


def load_env(path: Optional[str | Path] = None) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not path:
        return env
    env_path = Path(path)
    if not env_path.exists():
        raise AppFlowyError(f".env file not found: {env_path}")
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        env[key.strip()] = value
    return env


@dataclass
class AppFlowyClient:
    base_url: Optional[str]
    gotrue_url: Optional[str]
    client_version: str
    device_id: str

    @classmethod
    def from_env(
        cls,
        env_path: Optional[str | Path] = None,
        base_url: Optional[str] = None,
        gotrue_url: Optional[str] = None,
        client_version: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> "AppFlowyClient":
        env = load_env(env_path)
        resolved_base = (base_url or os.environ.get("APPFLOWY_BASE_URL") or env.get("APPFLOWY_BASE_URL"))
        resolved_gotrue = (
            gotrue_url
            or os.environ.get("API_EXTERNAL_URL")
            or os.environ.get("APPFLOWY_GOTRUE_BASE_URL")
            or env.get("API_EXTERNAL_URL")
            or env.get("APPFLOWY_GOTRUE_BASE_URL")
            or ""
        )
        if resolved_base:
            resolved_base = resolved_base.rstrip("/")
        if resolved_gotrue:
            resolved_gotrue = resolved_gotrue.rstrip("/")
        if not resolved_gotrue:
            resolved_gotrue = None
        resolved_version = (
            client_version
            or os.environ.get("APPFLOWY_CLIENT_VERSION")
            or env.get("APPFLOWY_CLIENT_VERSION")
            or "0.12.3"
        )
        resolved_device = (
            device_id
            or os.environ.get("APPFLOWY_DEVICE_ID")
            or env.get("APPFLOWY_DEVICE_ID")
            or new_device_id()
        )
        return cls(
            base_url=resolved_base,
            gotrue_url=resolved_gotrue,
            client_version=resolved_version,
            device_id=resolved_device,
        )

    def _default_headers(self, token: Optional[str]) -> Dict[str, str]:
        headers = {
            "client-version": self.client_version,
            "client-timestamp": str(now_millis()),
            "device-id": self.device_id,
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _require_base_url(self) -> str:
        if not self.base_url:
            raise AppFlowyError(
                "APPFLOWY_BASE_URL not configured. Provide --base-url, use --config, set APPFLOWY_BASE_URL, or pass --env <path>."
            )
        return self.base_url

    def _require_gotrue_url(self) -> str:
        if not self.gotrue_url:
            raise AppFlowyError(
                "GoTrue base URL not configured. Provide --gotrue-url, use --config, set API_EXTERNAL_URL/APPFLOWY_GOTRUE_BASE_URL, or pass --env <path>."
            )
        return self.gotrue_url

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        timeout: int = 10,
    ) -> Any:
        if params:
            query = urlencode(params, doseq=True)
            url = f"{url}?{query}"
        headers = self._default_headers(token)
        data = None
        if json_body is not None:
            data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
            headers["Accept-Charset"] = "utf-8"
        req = Request(url, data=data, method=method.upper(), headers=headers)
        try:
            with urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                status = getattr(resp, "status", None)
        except HTTPError as exc:
            body = exc.read()
            status = exc.code
            raise AppFlowyError(f"HTTP {status} for {url}", status=status, response=body) from exc
        except URLError as exc:
            raise AppFlowyError(f"Request failed for {url}: {exc}") from exc

        if not body:
            return None
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return body.decode("utf-8", errors="replace")

        if isinstance(payload, dict):
            if payload.get("success") is False or "error" in payload:
                raise AppFlowyError("AppFlowy API error", status=status, response=payload)
        return payload

    def login_password(self, email: str, password: str) -> Dict[str, Any]:
        base = self._require_gotrue_url()
        url = f"{base}/token"
        return self._request_json(
            "POST",
            url,
            params={"grant_type": "password"},
            json_body={"email": email, "password": password},
            token=None,
        )

    def list_workspaces(self, token: str) -> Any:
        base = self._require_base_url()
        return self._request_json("GET", f"{base}/api/workspace", token=token)

    def search(self, token: str, workspace_id: str, query: str) -> Any:
        base = self._require_base_url()
        return self._request_json(
            "GET",
            f"{base}/api/search/{workspace_id}",
            token=token,
            params={"query": query},
        )

    def list_databases(self, token: str, workspace_id: str) -> Any:
        base = self._require_base_url()
        return self._request_json(
            "GET",
            f"{base}/api/workspace/{workspace_id}/database",
            token=token,
        )

    def create_page_view(self, token: str, workspace_id: str, payload: Dict[str, Any]) -> Any:
        base = self._require_base_url()
        return self._request_json(
            "POST",
            f"{base}/api/workspace/{workspace_id}/page-view",
            token=token,
            json_body=payload,
        )

    def append_block(self, token: str, workspace_id: str, view_id: str, payload: Dict[str, Any]) -> Any:
        base = self._require_base_url()
        return self._request_json(
            "POST",
            f"{base}/api/workspace/{workspace_id}/page-view/{view_id}/append-block",
            token=token,
            json_body=payload,
        )

    def add_database_field(
        self, token: str, workspace_id: str, database_id: str, payload: Dict[str, Any]
    ) -> Any:
        base = self._require_base_url()
        return self._request_json(
            "POST",
            f"{base}/api/workspace/{workspace_id}/database/{database_id}/fields",
            token=token,
            json_body=payload,
        )

    def upsert_row(
        self, token: str, workspace_id: str, database_id: str, payload: Dict[str, Any]
    ) -> Any:
        base = self._require_base_url()
        return self._request_json(
            "POST",
            f"{base}/api/workspace/{workspace_id}/database/{database_id}/row",
            token=token,
            json_body=payload,
        )

    def get_row_detail(
        self, token: str, workspace_id: str, database_id: str, ids: Iterable[str]
    ) -> Any:
        base = self._require_base_url()
        ids_param = ",".join(ids)
        return self._request_json(
            "GET",
            f"{base}/api/workspace/{workspace_id}/database/{database_id}/row/detail",
            token=token,
            params={"ids": ids_param},
        )
