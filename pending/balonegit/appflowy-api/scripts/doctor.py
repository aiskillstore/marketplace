import argparse
import json
import sys
from typing import Any, Dict, List

import os

from _common import build_client, load_config, print_json, resolve_token
from appflowy_client import AppFlowyError


def _check(name: str, fn) -> Dict[str, Any]:
    try:
        result = fn()
        return {"name": name, "ok": True, "result": result}
    except Exception as exc:  # pylint: disable=broad-except
        return {"name": name, "ok": False, "error": str(exc)}


def _extract_version(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in (
            "version",
            "appflowy_version",
            "appflowy_cloud_version",
            "appflowyCloudVersion",
        ):
            if key in payload and payload[key]:
                return str(payload[key])
        data = payload.get("data")
        if isinstance(data, dict):
            for key in (
                "version",
                "appflowy_version",
                "appflowy_cloud_version",
                "appflowyCloudVersion",
            ):
                if key in data and data[key]:
                    return str(data[key])
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="AppFlowy API self-check.")
    parser.add_argument("--config", default=None, help="Path to config JSON (optional).")
    parser.add_argument("--env", default=None, help="Path to .env file (optional, opt-in).")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--gotrue-url", default=None)
    parser.add_argument("--client-version", default=None)
    parser.add_argument("--expected-version", default=None, help="Expected AppFlowy Cloud version.")
    parser.add_argument("--device-id", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--check-gotrue", action="store_true")
    parser.add_argument("--check-appflowy", action="store_true")
    parser.add_argument("--check-workspace", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    client = build_client(args)
    checks: List[Dict[str, Any]] = []
    warnings: List[str] = []

    def want(name: str) -> bool:
        if args.check_gotrue or args.check_appflowy or args.check_workspace:
            return {
                "gotrue": args.check_gotrue,
                "appflowy": args.check_appflowy,
                "workspace": args.check_workspace,
            }[name]
        return True

    if want("gotrue"):
        checks.append(
            _check(
                "gotrue_health",
                lambda: client._request_json(
                    "GET",
                    f"{client._require_gotrue_url()}/health",
                    token=None,
                    timeout=args.timeout,
                ),
            )
        )

    token = None
    if args.token or (args.email and args.password):
        try:
            token = resolve_token(args, client)
        except AppFlowyError as exc:
            checks.append({"name": "auth", "ok": False, "error": str(exc)})

    appflowy_health = None
    if want("appflowy"):
        checks.append(
            _check(
                "appflowy_health",
                lambda: client._request_json(
                    "GET",
                    f"{client._require_base_url()}/api/health",
                    token=None,
                    timeout=args.timeout,
                ),
            )
        )
        if checks[-1]["ok"]:
            appflowy_health = checks[-1]["result"]

    if want("workspace") and token:
        checks.append(
            _check(
                "list_workspaces",
                lambda: client.list_workspaces(token),
            )
        )

    expected_version = (
        args.expected_version
        or cfg.get("expected_appflowy_version")
        or cfg.get("expected_version")
        or os.environ.get("APPFLOWY_EXPECTED_VERSION")
    )
    if expected_version and appflowy_health:
        server_version = _extract_version(appflowy_health)
        if server_version and server_version != expected_version:
            warnings.append(
                f"AppFlowy version mismatch: expected {expected_version}, got {server_version}. Skill may be incompatible."
            )
        if not server_version:
            warnings.append(
                "Unable to detect AppFlowy version from /api/health response. Skill may be incompatible."
            )

    ok = all(c.get("ok") for c in checks) if checks else False
    output = {"ok": ok, "checks": checks, "warnings": warnings}
    print_json(output)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
