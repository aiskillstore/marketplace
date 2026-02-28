import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from appflowy_client import AppFlowyClient, AppFlowyError, load_env


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise AppFlowyError(f"Config file not found: {cfg_path}")
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def _pick(*values):
    for value in values:
        if value:
            return value
    return None


def build_client(args) -> AppFlowyClient:
    cfg = load_config(getattr(args, "config", None))
    env_path = getattr(args, "env", None)
    env_file = {}
    if env_path:
        env_file = load_env(env_path)
    base_url = _pick(
        getattr(args, "base_url", None),
        cfg.get("base_url") or cfg.get("APPFLOWY_BASE_URL"),
        os.environ.get("APPFLOWY_BASE_URL"),
        env_file.get("APPFLOWY_BASE_URL") if env_file else None,
    )
    gotrue_url = _pick(
        getattr(args, "gotrue_url", None),
        cfg.get("gotrue_url") or cfg.get("API_EXTERNAL_URL") or cfg.get("APPFLOWY_GOTRUE_BASE_URL"),
        os.environ.get("API_EXTERNAL_URL"),
        os.environ.get("APPFLOWY_GOTRUE_BASE_URL"),
        env_file.get("API_EXTERNAL_URL") if env_file else None,
        env_file.get("APPFLOWY_GOTRUE_BASE_URL") if env_file else None,
    )
    client_version = _pick(
        getattr(args, "client_version", None),
        cfg.get("client_version") or cfg.get("APPFLOWY_CLIENT_VERSION"),
        os.environ.get("APPFLOWY_CLIENT_VERSION"),
        env_file.get("APPFLOWY_CLIENT_VERSION") if env_file else None,
    )
    device_id = _pick(
        getattr(args, "device_id", None),
        cfg.get("device_id") or cfg.get("APPFLOWY_DEVICE_ID"),
        os.environ.get("APPFLOWY_DEVICE_ID"),
        env_file.get("APPFLOWY_DEVICE_ID") if env_file else None,
    )
    return AppFlowyClient.from_env(
        env_path=None,
        base_url=base_url,
        gotrue_url=gotrue_url,
        client_version=client_version,
        device_id=device_id,
    )


def resolve_token(args, client: AppFlowyClient) -> str:
    if args.token:
        return args.token
    if args.email and args.password:
        resp = client.login_password(args.email, args.password)
        token = resp.get("access_token") or resp.get("token")
        if not token:
            raise AppFlowyError("No access_token in GoTrue response", response=resp)
        return token
    raise AppFlowyError("Missing token or email/password for authentication")


def load_json_payload(payload: Optional[str], payload_file: Optional[str]) -> Dict[str, Any]:
    if payload and payload_file:
        raise AppFlowyError("Provide only one of --payload or --payload-file")
    if payload_file:
        text = Path(payload_file).read_text(encoding="utf-8")
        return json.loads(text)
    if payload:
        return json.loads(payload)
    raise AppFlowyError("Missing JSON payload")


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=True))
