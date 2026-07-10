#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "httpxyz>=0.31.2",
#     "typer>=0.26.8",
#     "pydantic>=2.13.4",
#     "rich>=15.0.0",
# ]
# ///

from __future__ import annotations

import json
import sys
from enum import Enum
from pathlib import Path
from typing import Any

import typer
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

ENV_TIMEOUT = "TICKTICK_TIMEOUT"
# 该脚本主要提供给 AI Agent 调用，人类 CLI 使用只是顺带支持。
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ticktick_api_client import (  # noqa: E402
    DEFAULT_BASE_URL,
    ChecklistItem,
    ProjectCreate,
    ProjectUpdate,
    TaskCompletedFilter,
    TaskCreate,
    TaskFilter,
    TaskMove,
    TaskUpdate,
    TicktickApiClient,
    TicktickApiError,
)
from ticktick_auth import (  # noqa: E402
    ENV_TOKEN_FILE,
    AuthError,
    default_token_file,
    load_token_payload,
    login,
    remove_stored_token,
    token_expiry_info,
)

app = typer.Typer(no_args_is_help=True)
auth_app = typer.Typer(no_args_is_help=True, help="认证相关操作。")
project_app = typer.Typer(no_args_is_help=True, help="项目相关操作。")
task_app = typer.Typer(no_args_is_help=True, help="任务相关操作。")
focus_app = typer.Typer(no_args_is_help=True, help="专注记录相关操作。")
habit_app = typer.Typer(no_args_is_help=True, help="习惯相关操作。")
console = Console()


class ApiError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AppState(BaseModel):
    timeout: str
    json_output: bool


class TicktickRegion(str, Enum):
    dida365 = "dida365"
    ticktick = "ticktick"


def api_base_url_for_region(region: TicktickRegion) -> str:
    if region is TicktickRegion.ticktick:
        return "https://api.ticktick.com/open/v1"
    return DEFAULT_BASE_URL


def region_for_api_base_url(base_url: str) -> str:
    return "ticktick" if "api.ticktick.com" in base_url.lower() else "dida365"


def resolve_auth(ctx: typer.Context) -> tuple[str, str, str, dict[str, Any] | None]:
    state = ctx.obj
    if not isinstance(state, AppState):
        raise ApiError("Client config not initialized.")
    payload = load_token_payload()
    if payload is None:
        raise ApiError(
            "缺少本地 token。请先运行 `./scripts/ticktick_cli.py auth login`。"
        )
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise ApiError(f"Invalid token file payload: {default_token_file()}")
    base_url = payload.get("base_url")
    if not isinstance(base_url, str) or not base_url:
        base_url = DEFAULT_BASE_URL
    return token, base_url, region_for_api_base_url(base_url), payload


def get_client(ctx: typer.Context) -> TicktickApiClient:
    state = ctx.obj
    if not isinstance(state, AppState):
        raise ApiError("Client config not initialized.")
    token, base_url, _, _ = resolve_auth(ctx)
    timeout_raw = state.timeout
    timeout_seconds = parse_timeout(str(timeout_raw))
    if timeout_seconds <= 0:
        raise ApiError("Timeout must be greater than 0.")
    return TicktickApiClient(
        token=token,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )


def render_payload(payload: Any) -> None:
    if isinstance(payload, list):
        data = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in payload
        ]
        console.print_json(data=data)
        return
    if hasattr(payload, "model_dump"):
        console.print_json(data=payload.model_dump())
        return
    console.print_json(data=payload)


def render_table(title: str, columns: list[str], rows: list[list[str]]) -> None:
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def render_kv_table(title: str, data: dict[str, Any]) -> None:
    rows = [[key, "" if value is None else str(value)] for key, value in data.items()]
    render_table(title, ["field", "value"], rows)


def render_project_list(projects: list[Any]) -> None:
    rows = []
    for project in projects:
        data = project.model_dump() if hasattr(project, "model_dump") else project
        rows.append(
            [
                str(data.get("id", "")),
                str(data.get("name", "")),
                str(data.get("color", "")),
                str(data.get("closed", "")),
                str(data.get("groupId", "")),
                str(data.get("viewMode", "")),
                str(data.get("kind", "")),
                str(data.get("sortOrder", "")),
            ]
        )
    render_table(
        "Projects",
        ["id", "name", "color", "closed", "groupId", "viewMode", "kind", "sortOrder"],
        rows,
    )


def render_task_list(tasks: list[Any]) -> None:
    rows = []
    for task in tasks:
        data = task.model_dump() if hasattr(task, "model_dump") else task
        rows.append(
            [
                str(data.get("id", "")),
                str(data.get("title", "")),
                str(data.get("status", "")),
                str(data.get("priority", "")),
                str(data.get("dueDate", "")),
                str(data.get("projectId", "")),
            ]
        )
    render_table(
        "Tasks",
        ["id", "title", "status", "priority", "dueDate", "projectId"],
        rows,
    )


def render_columns_list(columns: list[Any]) -> None:
    rows = []
    for column in columns:
        data = column.model_dump() if hasattr(column, "model_dump") else column
        rows.append(
            [
                str(data.get("id", "")),
                str(data.get("name", "")),
                str(data.get("sortOrder", "")),
            ]
        )
    render_table("Columns", ["id", "name", "sortOrder"], rows)


def parse_timeout(raw: str) -> float:
    value = raw.strip().lower()
    if not value:
        raise ApiError("Timeout cannot be empty.")
    multipliers = [
        ("seconds", 1),
        ("second", 1),
        ("secs", 1),
        ("sec", 1),
        ("s", 1),
        ("minutes", 60),
        ("minute", 60),
        ("mins", 60),
        ("min", 60),
        ("m", 60),
        ("hours", 3600),
        ("hour", 3600),
        ("hrs", 3600),
        ("hr", 3600),
        ("h", 3600),
    ]
    for unit, multiplier in multipliers:
        if value.endswith(unit):
            number = value[: -len(unit)].strip()
            try:
                return float(number) * multiplier
            except ValueError as exc:
                raise ApiError(f"Invalid timeout: {raw}") from exc
    try:
        return float(value)
    except ValueError as exc:
        raise ApiError(f"Invalid timeout: {raw}") from exc


def parse_checklist_items(
    item: list[str] | None,
    item_json: str | None,
) -> list[ChecklistItem] | None:
    if item and item_json:
        raise ApiError("Use --item or --item-json, not both.")
    if item_json:
        raw = item_json
        if raw.startswith("@"):
            path = Path(raw[1:]).expanduser()
            try:
                raw = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise ApiError(f"Failed to read items JSON: {path}") from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ApiError("Invalid JSON for --item-json.") from exc
        if not isinstance(payload, list):
            raise ApiError("--item-json must be a JSON array.")
        items: list[ChecklistItem] = []
        for entry in payload:
            if isinstance(entry, str):
                items.append(ChecklistItem(title=entry))
                continue
            if not isinstance(entry, dict):
                raise ApiError("Each item in --item-json must be an object or string.")
            items.append(ChecklistItem.model_validate(entry))
        return items or None
    if item:
        return [ChecklistItem(title=item_title) for item_title in item]
    return None


def parse_json_object(raw: str, option_name: str) -> dict[str, Any]:
    if raw.startswith("@"):
        path = Path(raw[1:]).expanduser()
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ApiError(f"Failed to read JSON payload: {path}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ApiError(f"Invalid JSON for {option_name}.") from exc
    if not isinstance(payload, dict):
        raise ApiError(f"{option_name} must be a JSON object.")
    return payload


def parse_json_list(raw: str, option_name: str) -> list[Any]:
    if raw.startswith("@"):
        path = Path(raw[1:]).expanduser()
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ApiError(f"Failed to read JSON payload: {path}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ApiError(f"Invalid JSON for {option_name}.") from exc
    if not isinstance(payload, list):
        raise ApiError(f"{option_name} must be a JSON array.")
    return payload


def compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


@app.callback()
def main(
    ctx: typer.Context,
    timeout: str = typer.Option(
        "30s",
        "--timeout",
        envvar=ENV_TIMEOUT,
        help="Request timeout (e.g. 20s, 1m).",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="输出 JSON 格式。",
    ),
) -> None:
    if ctx.resilient_parsing:
        return
    ctx.obj = AppState(
        timeout=timeout,
        json_output=json_output,
    )


@auth_app.command("login", help="使用官方 Dynamic OAuth 完成本地登录。")
def auth_login(
    ctx: typer.Context,
    region: TicktickRegion = typer.Option(
        TicktickRegion.dida365,
        "--region",
        help="账号区域：dida365 为中国区，ticktick 为国际版。",
    ),
    open_browser: bool = typer.Option(
        False,
        "--open",
        help="自动打开浏览器授权页。",
    ),
    timeout_seconds: int = typer.Option(
        300,
        "--timeout-seconds",
        min=30,
        help="等待浏览器授权回调的秒数；默认 5 分钟，请尽快完成登录。",
    ),
) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        raise ApiError("Client config not initialized.")
    base_url = api_base_url_for_region(region)
    path = login(
        base_url=base_url,
        open_browser=open_browser,
        timeout_seconds=timeout_seconds,
    )
    console.print(f"Saved token to {path}")
    payload = load_token_payload(base_url)
    if payload is not None:
        expiry = token_expiry_info(payload)
        if expiry["expires_at"]:
            console.print(f"Token expires at {expiry['expires_at']}")


@auth_app.command("doctor", help="检查当前认证配置是否可用。")
def auth_doctor(ctx: typer.Context) -> None:
    state = ctx.obj
    if not isinstance(state, AppState):
        raise ApiError("Client config not initialized.")
    token_source = str(default_token_file())
    try:
        token, base_url, region, token_payload = resolve_auth(ctx)
    except ApiError as exc:
        raise ApiError(
            "No token found. Run `./scripts/ticktick_cli.py auth login`, "
            f"or set {ENV_TOKEN_FILE}."
        ) from exc
    client = TicktickApiClient(
        token=token,
        base_url=base_url,
        timeout_seconds=parse_timeout(state.timeout),
    )
    projects = client.list_projects()
    payload = {
        "ok": True,
        "region": region,
        "base_url": base_url,
        "token_source": token_source,
        "project_count": len(projects),
    }
    if token_payload is not None:
        payload.update(token_expiry_info(token_payload))
    if state.json_output:
        render_payload(payload)
        return
    render_kv_table("Auth", payload)


@auth_app.command("logout", help="删除本地保存的 OAuth token。")
def auth_logout() -> None:
    removed = remove_stored_token()
    console.print("Removed stored token." if removed else "No stored token found.")


@project_app.command("list", help="列出当前账号的项目。")
def project_list(ctx: typer.Context) -> None:
    client = get_client(ctx)
    projects = client.list_projects()
    if ctx.obj.json_output:
        render_payload(projects)
        return
    render_project_list(projects)


@project_app.command("get", help="根据项目 ID 获取项目详情。")
def project_get(
    ctx: typer.Context,
    project_id: str = typer.Option(..., "--project-id"),
) -> None:
    client = get_client(ctx)
    project = client.get_project(project_id)
    if ctx.obj.json_output:
        render_payload(project)
        return
    render_kv_table("Project", project.model_dump())


@project_app.command("data", help="获取项目详情（包含未完成任务与列）。")
def project_data(
    ctx: typer.Context,
    project_id: str = typer.Option(..., "--project-id"),
) -> None:
    client = get_client(ctx)
    data = client.get_project_data(project_id)
    if ctx.obj.json_output:
        render_payload(data)
        return
    project = data.project.model_dump() if data.project else {}
    render_kv_table("Project", project)
    render_task_list(data.tasks or [])
    render_columns_list(data.columns or [])


@project_app.command("create", help="创建项目。")
def project_create(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name"),
    color: str | None = typer.Option(None, "--color"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
    view_mode: str | None = typer.Option(None, "--view-mode"),
    kind: str | None = typer.Option(None, "--kind"),
) -> None:
    client = get_client(ctx)
    project = client.create_project(
        ProjectCreate(
            name=name,
            color=color,
            sortOrder=sort_order,
            viewMode=view_mode,
            kind=kind,
        )
    )
    if ctx.obj.json_output:
        render_payload(project)
        return
    render_kv_table("Project", project.model_dump())


@project_app.command("update", help="更新项目。")
def project_update(
    ctx: typer.Context,
    project_id: str = typer.Option(..., "--project-id"),
    name: str | None = typer.Option(None, "--name"),
    color: str | None = typer.Option(None, "--color"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
    view_mode: str | None = typer.Option(None, "--view-mode"),
    kind: str | None = typer.Option(None, "--kind"),
) -> None:
    if not any([name, color, sort_order, view_mode, kind]):
        raise ApiError("No update fields provided.")
    client = get_client(ctx)
    project = client.update_project(
        project_id,
        ProjectUpdate(
            name=name,
            color=color,
            sortOrder=sort_order,
            viewMode=view_mode,
            kind=kind,
        ),
    )
    if ctx.obj.json_output:
        render_payload(project)
        return
    render_kv_table("Project", project.model_dump())


@project_app.command("delete", help="删除项目。")
def project_delete(
    ctx: typer.Context,
    project_id: str = typer.Option(..., "--project-id"),
) -> None:
    client = get_client(ctx)
    client.delete_project(project_id)
    console.print("OK")


@task_app.command("get", help="根据项目 ID 与任务 ID 获取任务。")
def task_get(
    ctx: typer.Context,
    project_id: str = typer.Option(..., "--project-id"),
    task_id: str = typer.Option(..., "--task-id"),
) -> None:
    client = get_client(ctx)
    task = client.get_task(project_id, task_id)
    if ctx.obj.json_output:
        render_payload(task)
        return
    render_kv_table("Task", task.model_dump())


@task_app.command("create", help="创建任务。")
def task_create(
    ctx: typer.Context,
    title: str = typer.Option(..., "--title"),
    project_id: str = typer.Option(..., "--project-id"),
    content: str | None = typer.Option(None, "--content"),
    desc: str | None = typer.Option(None, "--desc"),
    is_all_day: bool | None = typer.Option(None, "--all-day"),
    start_date: str | None = typer.Option(None, "--start-date"),
    due_date: str | None = typer.Option(None, "--due-date"),
    time_zone: str | None = typer.Option(None, "--time-zone"),
    reminder: list[str] | None = typer.Option(None, "--reminder"),
    tag: list[str] | None = typer.Option(None, "--tag"),
    repeat_flag: str | None = typer.Option(None, "--repeat"),
    priority: int | None = typer.Option(None, "--priority"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
    item: list[str] | None = typer.Option(None, "--item"),
    item_json: str | None = typer.Option(
        None,
        "--item-json",
        help="JSON array string or @path to JSON file for checklist items.",
    ),
) -> None:
    client = get_client(ctx)
    items = parse_checklist_items(item, item_json)
    task = client.create_task(
        TaskCreate(
            title=title,
            projectId=project_id,
            content=content,
            desc=desc,
            isAllDay=is_all_day,
            startDate=start_date,
            dueDate=due_date,
            timeZone=time_zone,
            reminders=reminder or None,
            tags=tag or None,
            repeatFlag=repeat_flag,
            priority=priority,
            sortOrder=sort_order,
            items=items or None,
        )
    )
    if ctx.obj.json_output:
        render_payload(task)
        return
    render_kv_table("Task", task.model_dump())


@task_app.command("update", help="更新任务。")
def task_update(
    ctx: typer.Context,
    task_id: str = typer.Option(..., "--task-id"),
    project_id: str = typer.Option(..., "--project-id"),
    title: str | None = typer.Option(None, "--title"),
    content: str | None = typer.Option(None, "--content"),
    desc: str | None = typer.Option(None, "--desc"),
    is_all_day: bool | None = typer.Option(None, "--all-day"),
    start_date: str | None = typer.Option(None, "--start-date"),
    due_date: str | None = typer.Option(None, "--due-date"),
    time_zone: str | None = typer.Option(None, "--time-zone"),
    reminder: list[str] | None = typer.Option(None, "--reminder"),
    tag: list[str] | None = typer.Option(None, "--tag"),
    repeat_flag: str | None = typer.Option(None, "--repeat"),
    priority: int | None = typer.Option(None, "--priority"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
    item: list[str] | None = typer.Option(None, "--item"),
    item_json: str | None = typer.Option(
        None,
        "--item-json",
        help="JSON array string or @path to JSON file for checklist items.",
    ),
) -> None:
    if not any(
        [
            title,
            content,
            desc,
            is_all_day is not None,
            start_date,
            due_date,
            time_zone,
            reminder,
            tag,
            repeat_flag,
            priority,
            sort_order,
            item,
            item_json,
        ]
    ):
        raise ApiError("No update fields provided.")
    client = get_client(ctx)
    items = parse_checklist_items(item, item_json)
    task = client.update_task(
        task_id,
        TaskUpdate(
            id=task_id,
            projectId=project_id,
            title=title,
            content=content,
            desc=desc,
            isAllDay=is_all_day,
            startDate=start_date,
            dueDate=due_date,
            timeZone=time_zone,
            reminders=reminder or None,
            tags=tag or None,
            repeatFlag=repeat_flag,
            priority=priority,
            sortOrder=sort_order,
            items=items or None,
        ),
    )
    if ctx.obj.json_output:
        render_payload(task)
        return
    render_kv_table("Task", task.model_dump())


@task_app.command("complete", help="完成指定任务。")
def task_complete(
    ctx: typer.Context,
    project_id: str = typer.Option(..., "--project-id"),
    task_id: str = typer.Option(..., "--task-id"),
) -> None:
    client = get_client(ctx)
    client.complete_task(project_id, task_id)
    console.print("OK")


@task_app.command("delete", help="删除任务。")
def task_delete(
    ctx: typer.Context,
    project_id: str = typer.Option(..., "--project-id"),
    task_id: str = typer.Option(..., "--task-id"),
) -> None:
    client = get_client(ctx)
    client.delete_task(project_id, task_id)
    console.print("OK")


@task_app.command("move", help="移动任务到另一个项目。")
def task_move(
    ctx: typer.Context,
    from_project_id: str | None = typer.Option(None, "--from-project-id"),
    to_project_id: str | None = typer.Option(None, "--to-project-id"),
    task_id: str | None = typer.Option(None, "--task-id"),
    move_json: str | None = typer.Option(
        None,
        "--move-json",
        help="JSON array string or @path for task move operations.",
    ),
) -> None:
    if move_json:
        if any([from_project_id, to_project_id, task_id]):
            raise ApiError("Use --move-json or explicit move fields, not both.")
        moves = [
            TaskMove.model_validate(entry)
            for entry in parse_json_list(move_json, "--move-json")
        ]
    else:
        if not all([from_project_id, to_project_id, task_id]):
            raise ApiError("Provide --from-project-id, --to-project-id, and --task-id.")
        moves = [
            TaskMove(
                fromProjectId=str(from_project_id),
                toProjectId=str(to_project_id),
                taskId=str(task_id),
            )
        ]
    result = get_client(ctx).move_tasks(moves)
    if ctx.obj.json_output:
        render_payload(result)
        return
    render_payload(result)


@task_app.command("completed", help="查询已完成任务。")
def task_completed(
    ctx: typer.Context,
    project_id: list[str] | None = typer.Option(None, "--project-id"),
    start_date: str | None = typer.Option(None, "--start-date"),
    end_date: str | None = typer.Option(None, "--end-date"),
) -> None:
    if not any([project_id, start_date, end_date]):
        raise ApiError("Provide at least one completed-task filter.")
    tasks = get_client(ctx).list_completed_tasks(
        TaskCompletedFilter(
            projectIds=project_id or None,
            startDate=start_date,
            endDate=end_date,
        )
    )
    if ctx.obj.json_output:
        render_payload(tasks)
        return
    render_task_list(tasks)


@task_app.command("filter", help="按项目、时间、标签、优先级或状态过滤任务。")
def task_filter(
    ctx: typer.Context,
    project_id: list[str] | None = typer.Option(None, "--project-id"),
    start_date: str | None = typer.Option(None, "--start-date"),
    end_date: str | None = typer.Option(None, "--end-date"),
    priority: list[int] | None = typer.Option(None, "--priority"),
    tag: list[str] | None = typer.Option(None, "--tag"),
    status: list[int] | None = typer.Option(None, "--status"),
) -> None:
    if not any([project_id, start_date, end_date, priority, tag, status]):
        raise ApiError("Provide at least one task filter.")
    tasks = get_client(ctx).filter_tasks(
        TaskFilter(
            projectIds=project_id or None,
            startDate=start_date,
            endDate=end_date,
            priority=priority or None,
            tag=tag or None,
            status=status or None,
        )
    )
    if ctx.obj.json_output:
        render_payload(tasks)
        return
    render_task_list(tasks)


@focus_app.command("get", help="获取单条专注记录。")
def focus_get(
    ctx: typer.Context,
    focus_id: str = typer.Option(..., "--focus-id"),
    focus_type: int = typer.Option(..., "--type", help="Pomodoro=0, Timing=1."),
) -> None:
    focus = get_client(ctx).get_focus(focus_id, focus_type)
    if ctx.obj.json_output:
        render_payload(focus)
        return
    render_kv_table("Focus", focus.model_dump())


@focus_app.command("list", help="按时间范围列出专注记录。")
def focus_list(
    ctx: typer.Context,
    from_time: str = typer.Option(..., "--from"),
    to_time: str = typer.Option(..., "--to"),
    focus_type: int = typer.Option(..., "--type", help="Pomodoro=0, Timing=1."),
) -> None:
    focuses = get_client(ctx).list_focuses(from_time, to_time, focus_type)
    render_payload(focuses)


@focus_app.command("delete", help="删除专注记录。")
def focus_delete(
    ctx: typer.Context,
    focus_id: str = typer.Option(..., "--focus-id"),
    focus_type: int = typer.Option(..., "--type", help="Pomodoro=0, Timing=1."),
) -> None:
    focus = get_client(ctx).delete_focus(focus_id, focus_type)
    if ctx.obj.json_output:
        render_payload(focus)
        return
    render_kv_table("Focus", focus.model_dump())


def habit_payload_from_options(
    payload_json: str | None,
    name: str | None,
    icon_res: str | None,
    color: str | None,
    sort_order: int | None,
    status: int | None,
    encouragement: str | None,
    habit_type: str | None,
    goal: float | None,
    step: float | None,
    unit: str | None,
    repeat_rule: str | None,
    reminder: list[str] | None,
    record_enable: bool | None,
    section_id: str | None,
    target_days: int | None,
    target_start_date: int | None,
    completed_cycles: int | None,
    ex_date: list[str] | None,
    style: int | None,
) -> dict[str, Any]:
    payload = parse_json_object(payload_json, "--payload-json") if payload_json else {}
    payload.update(
        compact_payload(
            {
                "name": name,
                "iconRes": icon_res,
                "color": color,
                "sortOrder": sort_order,
                "status": status,
                "encouragement": encouragement,
                "type": habit_type,
                "goal": goal,
                "step": step,
                "unit": unit,
                "repeatRule": repeat_rule,
                "reminders": reminder or None,
                "recordEnable": record_enable,
                "sectionId": section_id,
                "targetDays": target_days,
                "targetStartDate": target_start_date,
                "completedCycles": completed_cycles,
                "exDates": ex_date or None,
                "style": style,
            }
        )
    )
    return payload


@habit_app.command("list", help="列出全部习惯。")
def habit_list(ctx: typer.Context) -> None:
    habits = get_client(ctx).list_habits()
    render_payload(habits)


@habit_app.command("get", help="获取习惯详情。")
def habit_get(
    ctx: typer.Context,
    habit_id: str = typer.Option(..., "--habit-id"),
) -> None:
    habit = get_client(ctx).get_habit(habit_id)
    if ctx.obj.json_output:
        render_payload(habit)
        return
    render_kv_table("Habit", habit.model_dump())


@habit_app.command("create", help="创建习惯。")
def habit_create(
    ctx: typer.Context,
    name: str | None = typer.Option(None, "--name"),
    icon_res: str | None = typer.Option(None, "--icon-res"),
    color: str | None = typer.Option(None, "--color"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
    status: int | None = typer.Option(None, "--status"),
    encouragement: str | None = typer.Option(None, "--encouragement"),
    habit_type: str | None = typer.Option(None, "--type"),
    goal: float | None = typer.Option(None, "--goal"),
    step: float | None = typer.Option(None, "--step"),
    unit: str | None = typer.Option(None, "--unit"),
    repeat_rule: str | None = typer.Option(None, "--repeat-rule"),
    reminder: list[str] | None = typer.Option(None, "--reminder"),
    record_enable: bool | None = typer.Option(
        None, "--record-enable/--no-record-enable"
    ),
    section_id: str | None = typer.Option(None, "--section-id"),
    target_days: int | None = typer.Option(None, "--target-days"),
    target_start_date: int | None = typer.Option(None, "--target-start-date"),
    completed_cycles: int | None = typer.Option(None, "--completed-cycles"),
    ex_date: list[str] | None = typer.Option(None, "--ex-date"),
    style: int | None = typer.Option(None, "--style"),
    payload_json: str | None = typer.Option(
        None,
        "--payload-json",
        help="JSON object string or @path for full habit payload.",
    ),
) -> None:
    payload = habit_payload_from_options(
        payload_json,
        name,
        icon_res,
        color,
        sort_order,
        status,
        encouragement,
        habit_type,
        goal,
        step,
        unit,
        repeat_rule,
        reminder,
        record_enable,
        section_id,
        target_days,
        target_start_date,
        completed_cycles,
        ex_date,
        style,
    )
    if not payload.get("name"):
        raise ApiError("Habit name is required.")
    habit = get_client(ctx).create_habit(payload)
    if ctx.obj.json_output:
        render_payload(habit)
        return
    render_kv_table("Habit", habit.model_dump())


@habit_app.command("update", help="更新习惯。")
def habit_update(
    ctx: typer.Context,
    habit_id: str = typer.Option(..., "--habit-id"),
    name: str | None = typer.Option(None, "--name"),
    icon_res: str | None = typer.Option(None, "--icon-res"),
    color: str | None = typer.Option(None, "--color"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
    status: int | None = typer.Option(None, "--status"),
    encouragement: str | None = typer.Option(None, "--encouragement"),
    habit_type: str | None = typer.Option(None, "--type"),
    goal: float | None = typer.Option(None, "--goal"),
    step: float | None = typer.Option(None, "--step"),
    unit: str | None = typer.Option(None, "--unit"),
    repeat_rule: str | None = typer.Option(None, "--repeat-rule"),
    reminder: list[str] | None = typer.Option(None, "--reminder"),
    record_enable: bool | None = typer.Option(
        None, "--record-enable/--no-record-enable"
    ),
    section_id: str | None = typer.Option(None, "--section-id"),
    target_days: int | None = typer.Option(None, "--target-days"),
    target_start_date: int | None = typer.Option(None, "--target-start-date"),
    completed_cycles: int | None = typer.Option(None, "--completed-cycles"),
    ex_date: list[str] | None = typer.Option(None, "--ex-date"),
    style: int | None = typer.Option(None, "--style"),
    payload_json: str | None = typer.Option(
        None,
        "--payload-json",
        help="JSON object string or @path for full habit payload.",
    ),
) -> None:
    payload = habit_payload_from_options(
        payload_json,
        name,
        icon_res,
        color,
        sort_order,
        status,
        encouragement,
        habit_type,
        goal,
        step,
        unit,
        repeat_rule,
        reminder,
        record_enable,
        section_id,
        target_days,
        target_start_date,
        completed_cycles,
        ex_date,
        style,
    )
    if not payload:
        raise ApiError("No update fields provided.")
    habit = get_client(ctx).update_habit(habit_id, payload)
    if ctx.obj.json_output:
        render_payload(habit)
        return
    render_kv_table("Habit", habit.model_dump())


@habit_app.command("checkin", help="创建或更新习惯打卡。")
def habit_checkin(
    ctx: typer.Context,
    habit_id: str = typer.Option(..., "--habit-id"),
    stamp: int | None = typer.Option(None, "--stamp"),
    time: str | None = typer.Option(None, "--time"),
    op_time: str | None = typer.Option(None, "--op-time"),
    value: float | None = typer.Option(None, "--value"),
    goal: float | None = typer.Option(None, "--goal"),
    status: int | None = typer.Option(None, "--status"),
    payload_json: str | None = typer.Option(
        None,
        "--payload-json",
        help="JSON object string or @path for full check-in payload.",
    ),
) -> None:
    payload = parse_json_object(payload_json, "--payload-json") if payload_json else {}
    payload.update(
        compact_payload(
            {
                "stamp": stamp,
                "time": time,
                "opTime": op_time,
                "value": value,
                "goal": goal,
                "status": status,
            }
        )
    )
    if "stamp" not in payload:
        raise ApiError("Check-in stamp is required.")
    checkin = get_client(ctx).checkin_habit(habit_id, payload)
    render_payload(checkin)


@habit_app.command("checkins", help="查询习惯打卡记录。")
def habit_checkins(
    ctx: typer.Context,
    habit_id: list[str] = typer.Option(..., "--habit-id"),
    from_stamp: int = typer.Option(..., "--from"),
    to_stamp: int = typer.Option(..., "--to"),
) -> None:
    checkins = get_client(ctx).list_habit_checkins(habit_id, from_stamp, to_stamp)
    render_payload(checkins)


app.add_typer(auth_app, name="auth")
app.add_typer(project_app, name="project")
app.add_typer(task_app, name="task")
app.add_typer(focus_app, name="focus")
app.add_typer(habit_app, name="habit")


def run() -> None:
    try:
        app()
    except (ApiError, AuthError, TicktickApiError) as exc:
        status_code = getattr(exc, "status_code", None)
        if status_code:
            console.print(f"[red]Error:[/red] {exc} (status {status_code})")
        else:
            console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    run()
