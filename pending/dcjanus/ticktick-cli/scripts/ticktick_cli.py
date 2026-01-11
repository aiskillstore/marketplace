#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "httpx>=0.28.1",
#     "typer>=0.20.1",
#     "pydantic>=2.12.5",
#     "rich>=14.2.0",
# ]
# ///

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import typer
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

AUTH_URL = "https://ticktick-oauth.dcjanus.workers.dev/authorize"
ENV_BASE_URL = "TICKTICK_BASE_URL"
ENV_TIMEOUT = "TICKTICK_TIMEOUT"
ENV_TOKEN = "TICKTICK_TOKEN"
# 该脚本主要提供给 AI Agent 调用，人类 CLI 使用只是顺带支持。
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ticktick_api_client import (  # noqa: E402
    DEFAULT_BASE_URL,
    ChecklistItem,
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate,
    TicktickApiClient,
    TicktickApiError,
)

app = typer.Typer(no_args_is_help=True)
project_app = typer.Typer(no_args_is_help=True, help="项目相关操作。")
task_app = typer.Typer(no_args_is_help=True, help="任务相关操作。")
console = Console()


class ApiError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AppState(BaseModel):
    token: str | None
    base_url: str
    timeout: str
    json_output: bool


def get_client(ctx: typer.Context) -> TicktickApiClient:
    state = ctx.obj
    if not isinstance(state, AppState):
        raise ApiError("Client config not initialized.")
    token = state.token
    if not token:
        raise ApiError(
            "缺少 token。请先访问 "
            f"{AUTH_URL} 授权，"
            f"然后通过 --token 或环境变量 {ENV_TOKEN} 传入。"
        )
    base_url = state.base_url
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


@app.callback()
def main(
    ctx: typer.Context,
    token: str | None = typer.Option(
        None,
        "--token",
        envvar=ENV_TOKEN,
        help="OAuth token.",
    ),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL,
        "--base-url",
        envvar=ENV_BASE_URL,
        help="API base URL.",
    ),
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
        token=token,
        base_url=base_url,
        timeout=timeout,
        json_output=json_output,
    )


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


app.add_typer(project_app, name="project")
app.add_typer(task_app, name="task")


def run() -> None:
    try:
        app()
    except (ApiError, TicktickApiError) as exc:
        if exc.status_code:
            console.print(f"[red]Error:[/red] {exc} (status {exc.status_code})")
        else:
            console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    run()
