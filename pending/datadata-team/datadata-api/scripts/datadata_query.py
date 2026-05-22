#!/usr/bin/env python3
"""Execute scripts against Datadata and fetch execution results."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def parse_args() -> argparse.Namespace:
    # First pass: extract global options from anywhere in argv so ordering is flexible.
    global_parser = argparse.ArgumentParser(add_help=False)
    global_parser.add_argument(
        "--base-url",
        default=os.environ.get("DATADATA_BASE_URL", "https://www.datadata.com"),
    )
    global_parser.add_argument(
        "--api-key",
        default=os.environ.get("DATADATA_API_KEY") or load_api_key_from_config() or "",
    )
    global_opts, remaining = global_parser.parse_known_args()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=global_opts.base_url)
    parser.add_argument("--api-key", default=global_opts.api_key)
    subparsers = parser.add_subparsers(dest="command", required=True)

    datasource_info_parser = subparsers.add_parser(
        "get-datasource-info", help="Fetch datasource metadata."
    )
    datasource_info_parser.add_argument("--datasource-id", required=True)

    list_tables_parser = subparsers.add_parser(
        "list-tables", help="List tables for a datasource."
    )
    list_tables_parser.add_argument("--datasource-id", required=True)
    list_tables_parser.add_argument("--schema-name")

    describe_table_parser = subparsers.add_parser(
        "describe-table", help="Describe a table for a datasource."
    )
    describe_table_parser.add_argument("--datasource-id", required=True)
    describe_table_parser.add_argument("--schema-name", required=True)
    describe_table_parser.add_argument("--table-name", required=True)

    execute_parser = subparsers.add_parser(
        "execute-adhoc", help="Create an adhoc execution from a script."
    )
    execute_parser.add_argument("--script-type", default="sql")
    execute_parser.add_argument("--query-engine", default="duckdb")
    execute_parser.add_argument(
        "--datasource",
        action="append",
        default=[],
        metavar="DATASOURCE_ID:ATTACH_ALIAS",
        help="Bind a datasource to the adhoc query. Repeat for multiple datasources.",
    )
    execute_parser.add_argument("--script", required=True)

    result_parser = subparsers.add_parser(
        "get-execution-result", help="Fetch a result artifact for an execution."
    )
    result_parser.add_argument("--execution-id", required=True)
    result_parser.add_argument(
        "--format",
        choices=("ndjson", "csv"),
        default="ndjson",
        help="Result format to download for the execution ID.",
    )
    result_parser.add_argument("--output-path")
    result_parser.add_argument(
        "--timeout",
        type=int,
        help="Max seconds to wait for the execution to complete. If exceeded, the backend returns a timeout error.",
    )

    create_table_parser = subparsers.add_parser(
        "create-table", help="Create a new table in a data space."
    )
    create_table_parser.add_argument("--datasource-id", required=True)
    create_table_parser.add_argument("--table-name", required=True)
    create_table_parser.add_argument(
        "--columns",
        required=True,
        help='JSON array: [{"columnName": "...", "columnType": "..."}]',
    )

    insert_rows_parser = subparsers.add_parser(
        "insert-rows", help="Insert rows into a data space table."
    )
    insert_rows_parser.add_argument("--datasource-id", required=True)
    insert_rows_parser.add_argument("--table-name", required=True)
    insert_rows_parser.add_argument(
        "--columns", required=True, help='JSON array of column names: ["col1", "col2"]'
    )
    insert_rows_parser.add_argument(
        "--rows",
        required=True,
        help="JSON 2D array of row data: [[col1, col2], [col1, col2], ...]]",
    )

    describe_data_space_table_parser = subparsers.add_parser(
        "describe-data-space-table",
        help="Describe a table in a data space.",
    )
    describe_data_space_table_parser.add_argument("--datasource-id", required=True)
    describe_data_space_table_parser.add_argument("--table-name", required=True)

    drop_data_space_table_parser = subparsers.add_parser(
        "drop-data-space-table",
        help="Drop a table from a data space.",
    )
    drop_data_space_table_parser.add_argument("--datasource-id", required=True)
    drop_data_space_table_parser.add_argument("--table-name", required=True)

    scan_parser = subparsers.add_parser(
        "scan-datasource", help="Trigger an async schema scan for a datasource."
    )
    scan_parser.add_argument("--datasource-id", required=True)

    whoami_parser = subparsers.add_parser(
        "whoami", help="Fetch current user info and API key metadata."
    )

    search_parser = subparsers.add_parser(
        "search-datasource",
        help="搜索数据源。支持 username:name 精确查找、社区公开搜索（Meilisearch）及私有数据源搜索。",
    )
    search_parser.add_argument(
        "--query",
        required=True,
        help="搜索关键词，支持 username/datasource-name 格式精确查找",
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="每个来源返回的最大结果数（默认 20）",
    )

    # --- Device Flow 两步式子命令（供 Agent 使用）---
    device_start_parser = subparsers.add_parser(
        "device-flow-start",
        help="发起设备授权（非阻塞），输出 JSON 含 verificationUriComplete 后立即退出。",
    )

    device_complete_parser = subparsers.add_parser(
        "device-flow-complete",
        help="轮询完成设备授权，获取 API Key 并保存到配置文件。",
    )
    device_complete_parser.add_argument(
        "--device-code",
        default=None,
        help="device-flow-start 返回的 deviceCode（可选，默认从状态文件自动读取）",
    )
    device_complete_parser.add_argument(
        "--interval", type=int, default=3, help="轮询间隔（秒），默认 3"
    )

    return parser.parse_args(remaining)


def build_url(base_url: str, path: str, query: dict[str, str] | None = None) -> str:
    base = base_url.rstrip("/")
    url = f"{base}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"
    return url


def fetch_datasource_info(base_url: str, api_key: str, datasource_id: str) -> Any:
    return request_json(
        build_url(base_url, f"/api/v1/datasources/{datasource_id}/info"), api_key
    )


def fetch_list_tables(
    base_url: str, api_key: str, datasource_id: str, schema_name: str | None
) -> Any:
    query = {"schemaName": schema_name} if schema_name else None
    return request_json(
        build_url(base_url, f"/api/v1/datasources/{datasource_id}/list-tables", query),
        api_key,
    )


def fetch_describe_table(
    base_url: str, api_key: str, datasource_id: str, schema_name: str, table_name: str
) -> Any:
    query = {
        "schemaName": schema_name,
        "tableName": table_name,
    }
    return request_json(
        build_url(
            base_url, f"/api/v1/datasources/{datasource_id}/describe-table", query
        ),
        api_key,
    )


def fetch_scan_datasource(base_url: str, api_key: str, datasource_id: str) -> Any:
    return request_json(
        build_url(base_url, f"/api/v1/datasources/{datasource_id}/scan"),
        api_key,
        method="POST",
    )


def fetch_create_table(
    base_url: str,
    api_key: str,
    datasource_id: str,
    table_name: str,
    columns: list[dict[str, str]],
) -> Any:
    payload = {
        "tableName": table_name,
        "columns": columns,
    }
    return request_json(
        build_url(base_url, f"/api/v1/data-spaces/{datasource_id}/create-table"),
        api_key,
        method="POST",
        payload=payload,
    )


def fetch_insert_rows(
    base_url: str,
    api_key: str,
    datasource_id: str,
    table_name: str,
    columns: list[str],
    rows: list[list[Any]],
) -> Any:
    payload = {
        "tableName": table_name,
        "columns": columns,
        "rows": rows,
    }
    return request_json(
        build_url(base_url, f"/api/v1/data-spaces/{datasource_id}/insert-rows"),
        api_key,
        method="POST",
        payload=payload,
    )


def fetch_data_space_describe_table(
    base_url: str,
    api_key: str,
    datasource_id: str,
    table_name: str,
) -> Any:
    payload = {"tableName": table_name}
    return request_json(
        build_url(base_url, f"/api/v1/data-spaces/{datasource_id}/describe-table"),
        api_key,
        method="POST",
        payload=payload,
    )


def fetch_data_space_drop_table(
    base_url: str,
    api_key: str,
    datasource_id: str,
    table_name: str,
) -> Any:
    payload = {"tableName": table_name}
    return request_json(
        build_url(base_url, f"/api/v1/data-spaces/{datasource_id}/drop-table"),
        api_key,
        method="POST",
        payload=payload,
    )


def request_json(
    url: str, api_key: str, method: str = "GET", payload: dict[str, Any] | None = None
) -> Any:
    data = None
    headers: dict[str, str] = {"Accept": "application/json"}
    if api_key:
        headers["X-Datadata-Api-key"] = api_key
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            content_type = resp.headers.get("Content-Type", "")
            if not raw:
                return None
            if "application/x-ndjson" in content_type:
                return parse_ndjson(raw)
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def request_text(url: str, api_key: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"X-Datadata-Api-key": api_key, "Accept": "*/*"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def request_bytes(url: str, api_key: str) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={"X-Datadata-Api-key": api_key, "Accept": "*/*"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read(), resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


# --- Device Flow (自动签发 API Key) ---

DEFAULT_DEVICE_PERMISSIONS = [
    "datasources:read",
    "datasources:scan",
    "datasources:replace-file",
    "data-spaces:write",
    "executions:get",
    "queries:execute",
    "queries:execute-adhoc",
]

# 设备授权签发的 API Key 默认过期天数
DEVICE_API_KEY_EXPIRY_DAYS = 90

# API Key 来源追踪（用于过期后自动重签）
_api_key_source: str | None = None  # "flag", "env", "config", "device-flow"


def _get_config_dir() -> str:
    """返回配置目录，支持 Windows / macOS / Linux。

    Windows: %APPDATA%/datadata/datadata-api-skills
    其他:    ~/.config/datadata/datadata-api-skills
    """
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "datadata", "datadata-api-skills")
    else:
        return os.path.join(
            os.path.expanduser("~"), ".config", "datadata", "datadata-api-skills"
        )


API_KEY_CONFIG_DIR = _get_config_dir()
API_KEY_CONFIG_FILE = os.path.join(API_KEY_CONFIG_DIR, "config.json")

# 设备授权进行中的状态文件（防止 Agent 只 start 忘记 complete）
DEVICE_FLOW_STATE_FILE = os.path.join(API_KEY_CONFIG_DIR, "device-flow-pending.json")


def _ensure_config_dir() -> None:
    """确保配置目录存在。Unix 下权限为 0700。"""
    if not os.path.isdir(API_KEY_CONFIG_DIR):
        os.makedirs(API_KEY_CONFIG_DIR, mode=0o700, exist_ok=True)


def load_api_key_from_config() -> str | None:
    """从 config.json 读取持久化的 API Key。返回 None 如果不存在或已过期。"""
    try:
        with open(API_KEY_CONFIG_FILE, "r", encoding="utf-8") as fh:
            config = json.load(fh)
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        return None

    api_key = config.get("apiKey") if isinstance(config, dict) else None
    if not api_key:
        return None

    # 检查是否过期（基于保存时间 + 90 天）
    saved_at_str = config.get("savedAt") if isinstance(config, dict) else None
    if saved_at_str:
        try:
            import datetime as _dt

            saved_at = _dt.datetime.fromisoformat(saved_at_str.replace("Z", "+00:00"))
            age = _dt.datetime.now(_dt.timezone.utc) - saved_at
            if age.days >= DEVICE_API_KEY_EXPIRY_DAYS:
                clear_api_key_config()
                return None
        except (ValueError, TypeError):
            pass  # 无法解析时间，跳过过期检查，仍可使用

    return api_key


def save_api_key_to_config(api_key: str) -> None:
    """将 API Key 持久化到 config.json，记录保存时间。"""
    import datetime as _dt

    _ensure_config_dir()
    config = {
        "apiKey": api_key,
        "savedAt": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(API_KEY_CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")
    # Unix 下设置文件权限 0600
    if sys.platform != "win32":
        os.chmod(API_KEY_CONFIG_FILE, 0o600)


def clear_api_key_config() -> None:
    """删除配置文件（API Key 过期或无效时调用）。"""
    try:
        os.remove(API_KEY_CONFIG_FILE)
    except (FileNotFoundError, PermissionError):
        pass


def save_device_flow_state(device_code: str, expires_in: int, interval: int) -> None:
    """保存设备授权进行中的状态，防止 Agent 忘记完成轮询。"""
    import datetime as _dt

    _ensure_config_dir()
    state = {
        "deviceCode": device_code,
        "expiresIn": expires_in,
        "interval": interval,
        "startedAt": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(DEVICE_FLOW_STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
        fh.write("\n")


def load_device_flow_state() -> dict[str, Any] | None:
    """读取进行中的设备授权状态。返回 None 如果不存在或已过期。"""
    try:
        with open(DEVICE_FLOW_STATE_FILE, "r", encoding="utf-8") as fh:
            state = json.load(fh)
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        return None
    if not isinstance(state, dict) or "deviceCode" not in state:
        return None
    # 检查是否超时
    started_at_str = state.get("startedAt")
    if started_at_str:
        try:
            import datetime as _dt

            started_at = _dt.datetime.fromisoformat(
                started_at_str.replace("Z", "+00:00")
            )
            expires_in = state.get("expiresIn", 600)
            if (
                _dt.datetime.now(_dt.timezone.utc) - started_at
            ).total_seconds() > expires_in:
                clear_device_flow_state()
                return None
        except (ValueError, TypeError):
            pass
    return state


def clear_device_flow_state() -> None:
    """清除设备授权状态文件。"""
    try:
        os.remove(DEVICE_FLOW_STATE_FILE)
    except (FileNotFoundError, PermissionError):
        pass


def get_default_api_key_expiry() -> str:
    """返回默认的 API Key 过期时间（当前时间 + 90 天），ISO 8601 格式。"""
    import datetime

    expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        days=DEVICE_API_KEY_EXPIRY_DAYS
    )
    return expiry.strftime("%Y-%m-%dT%H:%M:%SZ")


def start_device_flow(
    base_url: str,
    name: str,
    permissions: list[str],
    description: str | None = None,
    expires_at: str | None = None,
) -> dict[str, Any]:
    """发起设备授权流程，返回 userCode、deviceCode、verificationUri 等。"""
    payload: dict[str, Any] = {
        "name": name,
        "permissions": permissions,
    }
    if description:
        payload["description"] = description
    if expires_at:
        payload["expiresAt"] = expires_at
    return request_json(
        build_url(base_url, "/api/v1/api-keys/device-flow/code"),
        "",  # 无需 API Key
        method="POST",
        payload=payload,
    )


def poll_device_token(
    base_url: str, device_code: str, expires_in: int, interval: int
) -> dict[str, Any] | None:
    """轮询 /api-keys/device-flow/token 直到授权成功或过期。返回 API Key 信息或 None。"""
    deadline = time.time() + expires_in
    while time.time() < deadline:
        try:
            result = request_json(
                build_url(base_url, "/api/v1/api-keys/device-flow/token"),
                "",  # 无需 API Key
                method="POST",
                payload={"deviceCode": device_code},
            )
            return result
        except RuntimeError as exc:
            err_msg = str(exc)
            if "authorization_pending" in err_msg:
                time.sleep(interval)
                continue
            # invalid_device_code 或其他错误 → 终止
            print(f"设备授权失败: {err_msg}", file=sys.stderr)
            return None
    print("设备授权超时，未在有效期内完成授权。", file=sys.stderr)
    return None


def run_device_flow(base_url: str) -> str | None:
    """执行完整的 device flow，返回 API Key 或 None。成功后将 Key 持久化到 config.json。"""
    import datetime

    name = f"datadata-cli-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    description = "Auto-generated API key for Datadata CLI / Agent Skills"
    expires_at = get_default_api_key_expiry()

    print("未设置 API Key，正在发起设备授权...", file=sys.stderr)
    try:
        flow = start_device_flow(
            base_url, name, DEFAULT_DEVICE_PERMISSIONS, description, expires_at
        )
    except RuntimeError as exc:
        print(f"发起设备授权失败: {exc}", file=sys.stderr)
        return None

    expiry_display = datetime.datetime.now() + datetime.timedelta(
        days=DEVICE_API_KEY_EXPIRY_DAYS
    )
    print(
        f"\n请在浏览器中打开以下链接完成授权：\n\n    {flow['verificationUriComplete']}\n",
        file=sys.stderr,
    )
    print(
        f"授权后将签发有效期 {DEVICE_API_KEY_EXPIRY_DAYS} 天（至 {expiry_display.strftime('%Y-%m-%d')}）的 API Key。",
        file=sys.stderr,
    )
    print("等待授权中（最长 {} 秒）...".format(flow["expiresIn"]), file=sys.stderr)

    result = poll_device_token(
        base_url,
        flow["deviceCode"],
        flow["expiresIn"],
        flow["interval"],
    )
    if result is None:
        return None

    api_key = result.get("key")
    if api_key:
        try:
            save_api_key_to_config(api_key)
            print(
                f"✅ 授权成功！API Key 已保存到 {API_KEY_CONFIG_FILE}", file=sys.stderr
            )
        except OSError as exc:
            print(f"✅ 授权成功！API Key: {api_key}", file=sys.stderr)
            print(f"⚠️  无法保存到配置文件: {exc}", file=sys.stderr)
            print(
                "提示：可通过 export DATADATA_API_KEY='{}' 手动设置。".format(api_key),
                file=sys.stderr,
            )
    return api_key


def run_device_flow_start(args: argparse.Namespace) -> int:
    """发起设备授权（非阻塞），输出 JSON 后立即退出。自动保存状态防止遗忘。"""
    import datetime as _dt

    name = f"datadata-cli-{_dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    description = "Auto-generated API key for Datadata CLI / Agent Skills"
    expires_at = get_default_api_key_expiry()

    try:
        flow = start_device_flow(
            args.base_url, name, DEFAULT_DEVICE_PERMISSIONS, description, expires_at
        )
    except RuntimeError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    # 保存状态，防止 Agent 忘记后续轮询
    save_device_flow_state(
        flow["deviceCode"], flow["expiresIn"], flow.get("interval", 3)
    )

    expiry_display = _dt.datetime.now() + _dt.timedelta(days=DEVICE_API_KEY_EXPIRY_DAYS)
    output = {
        "userCode": flow["userCode"],
        "deviceCode": flow["deviceCode"],
        "verificationUri": flow["verificationUri"],
        "verificationUriComplete": flow["verificationUriComplete"],
        "expiresIn": flow["expiresIn"],
        "interval": flow.get("interval", 3),
        "expiryDisplay": f"{DEVICE_API_KEY_EXPIRY_DAYS} 天（至 {expiry_display.strftime('%Y-%m-%d')}）",
        "nextStep": (
            "用户授权后，运行: python3 scripts/datadata_query.py device-flow-complete"
            " --device-code " + flow["deviceCode"]
        ),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def run_device_flow_complete(args: argparse.Namespace) -> int:
    """轮询完成设备授权，获取 API Key 并保存到配置文件。可自动读取 device-flow-start 保存的状态。"""
    device_code = args.device_code

    # 如果未提供 --device-code，尝试从状态文件恢复
    if not device_code:
        state = load_device_flow_state()
        if state:
            device_code = state["deviceCode"]
            if not args.interval or args.interval == 3:  # 使用默认值说明没传
                args.interval = state.get("interval", 3)
        else:
            print(
                json.dumps(
                    {
                        "error": "no pending device flow found, run device-flow-start first"
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 1

    expires_in = 600
    result = poll_device_token(
        args.base_url,
        device_code,
        expires_in,
        args.interval,
    )
    if result is None:
        clear_device_flow_state()
        print(
            json.dumps(
                {"error": "device flow polling failed or expired"}, ensure_ascii=False
            ),
            file=sys.stderr,
        )
        return 1

    api_key = result.get("key")
    if not api_key:
        clear_device_flow_state()
        print(
            json.dumps(
                {"error": "no api key in response", "response": result},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1

    try:
        save_api_key_to_config(api_key)
        saved_path = API_KEY_CONFIG_FILE
    except OSError:
        saved_path = None

    # 成功后清除状态文件
    clear_device_flow_state()

    output = {
        "key": api_key,
        "name": result.get("name"),
        "permissions": result.get("permissions"),
        "expiresAt": result.get("expiresAt"),
        "savedTo": saved_path,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def parse_ndjson(raw: str) -> list[Any]:
    rows = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def parse_datasource_bindings(values: list[str]) -> list[dict[str, str]]:
    bindings = []
    for raw in values:
        datasource_id, sep, attach_alias = raw.partition(":")
        datasource_id = datasource_id.strip()
        attach_alias = attach_alias.strip()
        if not sep or not datasource_id or not attach_alias:
            raise ValueError(
                f"Invalid --datasource value '{raw}'. Use DATASOURCE_ID:ATTACH_ALIAS."
            )
        bindings.append(
            {
                "datasourceId": datasource_id,
                "attachAlias": attach_alias,
            }
        )
    return bindings


def find_execution_id(payload: Any) -> str | None:
    if isinstance(payload, dict):
        value = payload.get("id")
        if isinstance(value, str) and value:
            return value
        for key in ("executionId", "execution_id"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        for value in payload.values():
            found = find_execution_id(value)
            if found:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = find_execution_id(item)
            if found:
                return found
    return None


def create_execution(
    base_url: str,
    api_key: str,
    script: str,
    script_type: str,
    query_engine: str,
    datasources: list[dict[str, str]],
) -> tuple[str, Any]:
    payload = {
        "script": script,
        "scriptType": script_type,
        "queryEngine": query_engine,
    }
    if datasources:
        payload["datasources"] = datasources
    response = request_json(
        build_url(base_url, "/api/v1/queries/execute-adhoc"),
        api_key,
        method="POST",
        payload=payload,
    )
    execution_id = find_execution_id(response)
    if not execution_id:
        raise RuntimeError(
            "Could not find executionId in create-query response.\n"
            f"Raw response: {json.dumps(response, ensure_ascii=False)}"
        )
    return execution_id, response


def fetch_result_artifact(
    base_url: str, api_key: str, execution_id: str, fmt: str, timeout: int | None = None
) -> tuple[bytes, str]:
    query: dict[str, str] = {"format": fmt}
    if timeout is not None:
        query["timeout"] = str(timeout)
    url = build_url(base_url, f"/api/v1/executions/{execution_id}/result", query)
    if fmt == "csv":
        text = request_text(url, api_key)
        return text.encode("utf-8"), "text/csv"
    return request_bytes(url, api_key)


def default_output_path(execution_id: str, fmt: str, content_type: str) -> str:
    suffix = ".json"
    if fmt == "ndjson" or "application/x-ndjson" in content_type:
        suffix = ".ndjson"
    elif fmt == "csv":
        suffix = ".csv"
    return os.path.join(tempfile.gettempdir(), f"datadata-{execution_id}{suffix}")


def write_artifact(path: str, content: bytes) -> dict[str, Any]:
    with open(path, "wb") as fh:
        fh.write(content)
    return {
        "outputPath": path,
        "bytes": len(content),
    }


def estimate_rows(content: bytes, content_type: str) -> int | None:
    if "application/x-ndjson" not in content_type:
        return None
    return sum(1 for line in content.splitlines() if line.strip())


def require_common_args(args: argparse.Namespace) -> int:
    if not args.base_url:
        print("Missing --base-url or DATADATA_BASE_URL", file=sys.stderr)
        return 2
    if not args.api_key:
        print("Missing --api-key or DATADATA_API_KEY", file=sys.stderr)
        return 2
    return 0


def run_execute_adhoc(args: argparse.Namespace) -> int:
    try:
        datasources = parse_datasource_bindings(args.datasource)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    execution_id, create_response = create_execution(
        args.base_url,
        args.api_key,
        args.script,
        args.script_type,
        args.query_engine,
        datasources,
    )
    print(
        json.dumps(
            {
                "executionId": execution_id,
                "execution": create_response,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def run_get_datasource_info(args: argparse.Namespace) -> int:
    response = fetch_datasource_info(args.base_url, args.api_key, args.datasource_id)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def run_list_tables(args: argparse.Namespace) -> int:
    response = fetch_list_tables(
        args.base_url, args.api_key, args.datasource_id, args.schema_name
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def run_describe_table(args: argparse.Namespace) -> int:
    response = fetch_describe_table(
        args.base_url,
        args.api_key,
        args.datasource_id,
        args.schema_name,
        args.table_name,
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def run_get_execution_result(args: argparse.Namespace) -> int:
    try:
        result = fetch_result_artifact(
            args.base_url, args.api_key, args.execution_id, args.format, args.timeout
        )
    except RuntimeError:
        raise  # 认证错误等让 main() 处理自动重签
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {
                    "executionId": args.execution_id,
                    "fetchError": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    content, content_type = result
    output_path = args.output_path or default_output_path(
        args.execution_id, args.format, content_type
    )
    artifact = write_artifact(output_path, content)
    artifact["contentType"] = content_type or (
        "text/csv" if args.format == "csv" else "application/x-ndjson"
    )
    artifact["format"] = args.format
    row_count = estimate_rows(content, artifact["contentType"])
    if row_count is not None:
        artifact["rowCount"] = row_count
    print(
        json.dumps(
            {
                "executionId": args.execution_id,
                "result": artifact,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def run_create_table(args: argparse.Namespace) -> int:
    try:
        columns = json.loads(args.columns)
    except json.JSONDecodeError as exc:
        print(f"Invalid --columns JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(columns, list):
        print("--columns must be a JSON array", file=sys.stderr)
        return 2
    fetch_create_table(
        args.base_url, args.api_key, args.datasource_id, args.table_name, columns
    )
    print(
        json.dumps(
            {"status": "ok", "tableName": args.table_name}, ensure_ascii=False, indent=2
        )
    )
    return 0


def run_describe_data_space_table(args: argparse.Namespace) -> int:
    response = fetch_data_space_describe_table(
        args.base_url, args.api_key, args.datasource_id, args.table_name
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def run_drop_data_space_table(args: argparse.Namespace) -> int:
    response = fetch_data_space_drop_table(
        args.base_url, args.api_key, args.datasource_id, args.table_name
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "tableName": args.table_name,
                "response": response,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def run_scan_datasource(args: argparse.Namespace) -> int:
    response = fetch_scan_datasource(args.base_url, args.api_key, args.datasource_id)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def fetch_whoami(base_url: str, api_key: str) -> Any:
    return request_json(
        build_url(base_url, "/api/v1/auth/current"),
        api_key,
    )


# --- Datasource Search ---


def search_public_datasource(
    base_url: str,
    query: str,
    filter_str: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """通过 Meilisearch 搜索引擎搜索公开数据源。无需认证。"""
    params: dict[str, str] = {"q": query, "limit": str(limit), "offset": str(offset)}
    if filter_str:
        params["filter"] = filter_str
    url = build_url(base_url, "/api/search-engine/indexes/datasource/search", params)
    return request_json(url, "")


def search_owner_datasource(
    base_url: str,
    api_key: str,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any]:
    """通过私有接口搜索当前用户的数据源（含公开和私有）。需要认证。"""
    params: dict[str, str] = {
        "scope": "owner",
        "sort": "updated_at:desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    if search:
        params["search"] = search
    url = build_url(base_url, "/api/v1/datasources", params)
    return request_json(url, api_key)


def normalize_search_result_from_public(hit: dict[str, Any]) -> dict[str, Any]:
    """将搜索引擎结果标准化为统一格式。"""
    user = hit.get("user", {})
    return {
        "id": hit.get("id", ""),
        "name": hit.get("name", ""),
        "displayName": hit.get("displayName", ""),
        "description": hit.get("description", ""),
        "visibility": hit.get("visibility", "public"),
        "tags": hit.get("tags", []),
        "username": user.get("username", ""),
        "userDisplayName": user.get("displayName", ""),
        "source": "public",
    }


def normalize_search_result_from_owner(item: dict[str, Any]) -> dict[str, Any]:
    """将私有接口结果标准化为统一格式。"""
    user = item.get("user", {})
    return {
        "id": item.get("id", ""),
        "name": item.get("name", ""),
        "displayName": item.get("displayName", ""),
        "description": item.get("description", ""),
        "visibility": item.get("visibility", "public"),
        "tags": item.get("tags", []),
        "type": item.get("type", ""),
        "username": user.get("username", ""),
        "userDisplayName": user.get("displayName", ""),
        "source": "private",
    }


def _parse_username_name(query: str) -> tuple[str | None, str]:
    """解析 username/datasource-name 格式。

    返回 (username | None, name)。若无斜杠则 username 为 None。
    """
    if "/" in query:
        parts = query.split("/", 1)
        username = parts[0].strip()
        name = parts[1].strip()
        if username and name:
            return username, name
    return None, query


def _get_current_username(base_url: str, api_key: str) -> str | None:
    """通过 whoami 获取当前用户名。失败时返回 None。"""
    try:
        whoami = fetch_whoami(base_url, api_key)
        return whoami.get("user", {}).get("username")
    except RuntimeError:
        return None


def run_whoami(args: argparse.Namespace) -> int:
    response = fetch_whoami(args.base_url, args.api_key)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def run_insert_rows(args: argparse.Namespace) -> int:
    try:
        columns = json.loads(args.columns)
        rows = json.loads(args.rows)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(columns, list) or not isinstance(rows, list):
        print(
            "--columns must be a JSON array and --rows must be a JSON 2D array",
            file=sys.stderr,
        )
        return 2
    response = fetch_insert_rows(
        args.base_url, args.api_key, args.datasource_id, args.table_name, columns, rows
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "tableName": args.table_name,
                "inserted": len(rows),
                "response": response,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _detect_api_key_source(args: argparse.Namespace) -> str | None:
    """检测当前 API Key 的来源。"""
    if not args.api_key:
        return None
    # --api-key 通过命令行显式传入
    cli_key = _get_cli_api_key()
    if cli_key and cli_key == args.api_key:
        return "flag"
    # 环境变量
    env_key = os.environ.get("DATADATA_API_KEY")
    if env_key and env_key == args.api_key:
        return "env"
    # 配置文件（忽略过期检查，仅做值匹配）
    config_key = _load_config_key_raw()
    if config_key and config_key == args.api_key:
        return "config"
    return "device-flow"


def _get_cli_api_key() -> str | None:
    """检查 sys.argv 中是否显式传入了 --api-key。"""
    try:
        idx = sys.argv.index("--api-key")
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    except ValueError:
        pass
    return None


def _load_config_key_raw() -> str | None:
    """读取配置文件中的 apiKey（不做过期检查）。"""
    try:
        with open(API_KEY_CONFIG_FILE, "r", encoding="utf-8") as fh:
            config = json.load(fh)
            return config.get("apiKey") if isinstance(config, dict) else None
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        return None


def _is_auth_error(exc: Exception) -> bool:
    """判断异常是否为 API Key 认证错误（401 或 Key 无效的 403）。

    403 "permission denied"（操作他人资源等正常权限拒绝）不算认证错误，
    只有 401 或 403 中明确提示 Key 不存在/无效的才算。
    """
    msg = str(exc)
    if "HTTP 401" in msg:
        return True
    if "HTTP 403" in msg:
        # 403 且 body 中明确提示 Key 相关问题时才认为是 Key 失效
        key_related = (
            "api key not exists" in msg.lower()
            or "api key" in msg.lower()
            and "expired" in msg.lower()
        )
        return key_related
    return False


def run_search_datasource(args: argparse.Namespace) -> int:
    """搜索数据源，统一处理三种搜索方式。

    1. username/datasource-name 精确格式：
       - username 匹配当前用户 → 通过私有接口搜索
       - username 不匹配 → 通过搜索引擎 + user.username 过滤
    2. 普通关键词 → 同时搜索公开（搜索引擎）和私有（owner 接口）
    """
    query = args.query.strip()
    base_url = args.base_url

    username, name = _parse_username_name(query)
    results: list[dict[str, Any]] = []
    sources: list[str] = []

    if username is not None:
        # 精确格式：username/datasource-name
        current_user = None
        if args.api_key:
            current_user = _get_current_username(base_url, args.api_key)

        if current_user and current_user == username and args.api_key:
            # 匹配当前用户 → 通过私有接口搜索
            try:
                owner_result = search_owner_datasource(
                    base_url, args.api_key, search=name, limit=args.limit
                )
                items = owner_result.get("data", [])
                for item in items:
                    results.append(normalize_search_result_from_owner(item))
                sources.append("private")
            except RuntimeError as exc:
                print(
                    f"私有数据源搜索失败: {exc}",
                    file=sys.stderr,
                )
        else:
            # 非当前用户 → 通过搜索引擎 + user.username 过滤
            filter_str = f"user.username = {username}"
            try:
                public_result = search_public_datasource(
                    base_url, query=name, filter_str=filter_str, limit=args.limit
                )
                for hit in public_result.get("hits", []):
                    results.append(normalize_search_result_from_public(hit))
                sources.append("public")
            except RuntimeError as exc:
                print(
                    f"公开数据源搜索失败: {exc}",
                    file=sys.stderr,
                )
    else:
        # 普通关键词搜索：始终同时搜索公开和私有
        # 1. 搜索引擎搜索公开数据源
        try:
            public_result = search_public_datasource(
                base_url, query=query, limit=args.limit
            )
            for hit in public_result.get("hits", []):
                results.append(normalize_search_result_from_public(hit))
            sources.append("public")
        except RuntimeError as exc:
            print(
                f"公开数据源搜索失败: {exc}",
                file=sys.stderr,
            )

        # 2. 私有接口搜索当前用户的数据源
        if not args.api_key:
            print(
                "私有数据源搜索需要 API Key，已跳过。请先配置认证。",
                file=sys.stderr,
            )
        else:
            try:
                owner_result = search_owner_datasource(
                    base_url, args.api_key, search=query, limit=args.limit
                )
                items = owner_result.get("data", [])
                for item in items:
                    item_normalized = normalize_search_result_from_owner(item)
                    # 去重：如果 public 结果中已有同 ID，跳过
                    existing_ids = {r["id"] for r in results}
                    if item_normalized["id"] not in existing_ids:
                        results.append(item_normalized)
                sources.append("private")
            except RuntimeError as exc:
                print(
                    f"私有数据源搜索失败: {exc}",
                    file=sys.stderr,
                )

    # 添加序号
    for i, r in enumerate(results, 1):
        r["index"] = i

    output = {
        "query": query,
        "sources": sources,
        "resultCount": len(results),
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    global _api_key_source

    args = parse_args()

    # base-url 是必须的
    if not args.base_url:
        print("Missing --base-url or DATADATA_BASE_URL", file=sys.stderr)
        return 2

    # device-flow 和 search-datasource（可仅公开搜索）子命令不需要 API Key，直接分发
    if args.command in (
        "device-flow-start",
        "device-flow-complete",
        "search-datasource",
    ):
        return _dispatch(args)

    # 如果未提供 API Key，打印两步式设备授权指引后退出
    if not args.api_key:
        print(
            "未找到 API Key。请通过设备授权获取：\n"
            "\n"
            "  步骤 1: python3 scripts/datadata_query.py device-flow-start\n"
            "  步骤 2: 在浏览器中打开输出的链接并授权\n"
            "  步骤 3: python3 scripts/datadata_query.py device-flow-complete\n"
            "\n"
            "授权后 API Key 自动保存，重新运行原命令即可。\n"
            "\n"
            "或手动设置：\n"
            "  1. 登录 https://www.datadata.com\n"
            "  2. 头像 → Settings → 左侧 'API Keys' → 创建新 Key\n"
            "  3. 权限勾选: queries:execute-adhoc, executions:get, datasources:read, datasources:scan, data-spaces:write\n"
            "  4. export DATADATA_API_KEY='<key>' 或通过 --api-key 传入",
            file=sys.stderr,
        )
        return 2

    # 首次检测来源
    if _api_key_source is None:
        _api_key_source = _detect_api_key_source(args)

    # 执行命令，遇到 Key 认证错误且来自 config 时自动清除过期配置
    try:
        return _dispatch(args)
    except RuntimeError as exc:
        if _is_auth_error(exc) and _api_key_source == "config":
            print(
                json.dumps(
                    {"error": "api_key_expired", "detail": str(exc)}, ensure_ascii=False
                ),
                file=sys.stderr,
            )
            clear_api_key_config()
            return 2
        # 其他错误 → 输出简洁 JSON，不打印堆栈
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


def _dispatch(args: argparse.Namespace) -> int:
    """根据子命令分发到对应的处理函数。"""
    if args.command == "get-datasource-info":
        return run_get_datasource_info(args)
    if args.command == "list-tables":
        return run_list_tables(args)
    if args.command == "describe-table":
        return run_describe_table(args)
    if args.command == "execute-adhoc":
        return run_execute_adhoc(args)
    if args.command == "get-execution-result":
        return run_get_execution_result(args)
    if args.command == "create-table":
        return run_create_table(args)
    if args.command == "describe-data-space-table":
        return run_describe_data_space_table(args)
    if args.command == "drop-data-space-table":
        return run_drop_data_space_table(args)
    if args.command == "insert-rows":
        return run_insert_rows(args)
    if args.command == "scan-datasource":
        return run_scan_datasource(args)
    if args.command == "whoami":
        return run_whoami(args)
    if args.command == "search-datasource":
        return run_search_datasource(args)
    if args.command == "device-flow-start":
        return run_device_flow_start(args)
    if args.command == "device-flow-complete":
        return run_device_flow_complete(args)
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
