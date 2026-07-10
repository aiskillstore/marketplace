from __future__ import annotations

from typing import Any, Iterable

import httpxyz
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

DEFAULT_BASE_URL = "https://api.dida365.com/open/v1"


class ApiModel(BaseModel):
    """通用 API 数据模型基类，允许额外字段以兼容文档不完整的情况。"""

    model_config = ConfigDict(extra="allow")


class ApiConfig(ApiModel):
    """API 连接与认证配置。"""

    base_url: AnyHttpUrl = Field(
        default=DEFAULT_BASE_URL,
        description="Open API 基础地址。",
    )
    token: str = Field(description="OAuth access token。")
    timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        description="请求超时时间（秒）。",
    )
    user_agent: str = Field(
        default="ticktick-cli/0.1",
        description="请求 User-Agent 标识。",
    )


class TicktickApiError(RuntimeError):
    """API 请求失败时抛出的异常。"""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ChecklistItem(ApiModel):
    """子任务（清单项）模型。"""

    id: str | None = Field(default=None, description="子任务标识。")
    title: str | None = Field(default=None, description="子任务标题。")
    status: int | None = Field(
        default=None, description="子任务状态（0 未完成，1 已完成）。"
    )
    completedTime: str | int | None = Field(
        default=None, description="子任务完成时间。"
    )
    isAllDay: bool | None = Field(default=None, description="是否为全天任务。")
    sortOrder: int | None = Field(default=None, description="子任务排序值。")
    startDate: str | int | None = Field(default=None, description="子任务开始时间。")
    timeZone: str | None = Field(default=None, description="子任务时区。")


class Task(ApiModel):
    """任务模型。"""

    id: str | None = Field(default=None, description="任务标识。")
    projectId: str | None = Field(default=None, description="项目标识。")
    title: str | None = Field(default=None, description="任务标题。")
    content: str | None = Field(default=None, description="任务内容。")
    desc: str | None = Field(default=None, description="任务描述（清单说明）。")
    isAllDay: bool | None = Field(default=None, description="是否为全天任务。")
    startDate: str | None = Field(default=None, description="任务开始时间。")
    dueDate: str | None = Field(default=None, description="任务截止时间。")
    timeZone: str | None = Field(default=None, description="任务时区。")
    repeatFlag: str | None = Field(default=None, description="任务重复规则。")
    reminders: list[str] | None = Field(default=None, description="提醒列表。")
    tags: list[str] | None = Field(default=None, description="标签列表。")
    priority: int | None = Field(default=None, description="任务优先级。")
    status: int | None = Field(default=None, description="任务状态。")
    completedTime: str | None = Field(default=None, description="任务完成时间。")
    sortOrder: int | None = Field(default=None, description="任务排序值。")
    items: list[ChecklistItem] | None = Field(default=None, description="子任务列表。")
    kind: str | None = Field(default=None, description="任务类型。")


class TaskCreate(ApiModel):
    """创建任务的请求体。"""

    title: str = Field(description="任务标题。")
    projectId: str = Field(description="项目标识。")
    content: str | None = Field(default=None, description="任务内容。")
    desc: str | None = Field(default=None, description="任务描述（清单说明）。")
    isAllDay: bool | None = Field(default=None, description="是否为全天任务。")
    startDate: str | None = Field(default=None, description="任务开始时间。")
    dueDate: str | None = Field(default=None, description="任务截止时间。")
    timeZone: str | None = Field(default=None, description="任务时区。")
    reminders: list[str] | None = Field(default=None, description="提醒列表。")
    tags: list[str] | None = Field(default=None, description="标签列表。")
    repeatFlag: str | None = Field(default=None, description="任务重复规则。")
    priority: int | None = Field(default=None, description="任务优先级。")
    sortOrder: int | None = Field(default=None, description="任务排序值。")
    items: list[ChecklistItem] | None = Field(default=None, description="子任务列表。")


class TaskUpdate(ApiModel):
    """更新任务的请求体。"""

    id: str = Field(description="任务标识。")
    projectId: str = Field(description="项目标识。")
    title: str | None = Field(default=None, description="任务标题。")
    content: str | None = Field(default=None, description="任务内容。")
    desc: str | None = Field(default=None, description="任务描述（清单说明）。")
    isAllDay: bool | None = Field(default=None, description="是否为全天任务。")
    startDate: str | None = Field(default=None, description="任务开始时间。")
    dueDate: str | None = Field(default=None, description="任务截止时间。")
    timeZone: str | None = Field(default=None, description="任务时区。")
    reminders: list[str] | None = Field(default=None, description="提醒列表。")
    tags: list[str] | None = Field(default=None, description="标签列表。")
    repeatFlag: str | None = Field(default=None, description="任务重复规则。")
    priority: int | None = Field(default=None, description="任务优先级。")
    sortOrder: int | None = Field(default=None, description="任务排序值。")
    items: list[ChecklistItem] | None = Field(default=None, description="子任务列表。")


class Project(ApiModel):
    """项目模型。"""

    id: str | None = Field(default=None, description="项目标识。")
    name: str | None = Field(default=None, description="项目名称。")
    color: str | None = Field(default=None, description="项目颜色。")
    closed: bool | None = Field(default=None, description="是否已关闭。")
    groupId: str | None = Field(default=None, description="项目分组标识。")
    viewMode: str | None = Field(default=None, description="视图模式。")
    permission: str | None = Field(default=None, description="权限信息。")
    kind: str | None = Field(default=None, description="项目类型。")
    sortOrder: int | None = Field(default=None, description="排序值。")


class ProjectCreate(ApiModel):
    """创建项目的请求体。"""

    name: str = Field(description="项目名称。")
    color: str | None = Field(default=None, description="项目颜色。")
    sortOrder: int | None = Field(default=None, description="项目排序值。")
    viewMode: str | None = Field(default=None, description="视图模式。")
    kind: str | None = Field(default=None, description="项目类型。")


class ProjectUpdate(ApiModel):
    """更新项目的请求体。"""

    name: str | None = Field(default=None, description="项目名称。")
    color: str | None = Field(default=None, description="项目颜色。")
    sortOrder: int | None = Field(default=None, description="项目排序值。")
    viewMode: str | None = Field(default=None, description="视图模式。")
    kind: str | None = Field(default=None, description="项目类型。")


class Column(ApiModel):
    """项目看板列模型。"""

    id: str | None = Field(default=None, description="列标识。")
    projectId: str | None = Field(default=None, description="所属项目标识。")
    name: str | None = Field(default=None, description="列名称。")
    sortOrder: int | None = Field(default=None, description="列排序值。")


class ProjectData(ApiModel):
    """项目详情数据（含任务与列）。"""

    project: Project | None = Field(default=None, description="项目信息。")
    tasks: list[Task] | None = Field(default=None, description="项目未完成任务列表。")
    columns: list[Column] | None = Field(default=None, description="项目列信息。")


class TaskMove(ApiModel):
    """移动任务请求项。"""

    fromProjectId: str = Field(description="源项目标识。")
    toProjectId: str = Field(description="目标项目标识。")
    taskId: str = Field(description="任务标识。")


class TaskMoveResult(ApiModel):
    """移动任务结果。"""

    id: str | None = Field(default=None, description="任务标识。")
    etag: str | None = Field(default=None, description="实体标签。")


class TaskCompletedFilter(ApiModel):
    """查询已完成任务的过滤条件。"""

    projectIds: list[str] | None = Field(default=None, description="项目标识列表。")
    startDate: str | None = Field(default=None, description="完成时间起点。")
    endDate: str | None = Field(default=None, description="完成时间终点。")


class TaskFilter(ApiModel):
    """任务过滤条件。"""

    projectIds: list[str] | None = Field(default=None, description="项目标识列表。")
    startDate: str | None = Field(default=None, description="开始时间起点。")
    endDate: str | None = Field(default=None, description="开始时间终点。")
    priority: list[int] | None = Field(default=None, description="优先级列表。")
    tag: list[str] | None = Field(default=None, description="标签列表。")
    status: list[int] | None = Field(default=None, description="状态列表。")


class OpenPomodoroTaskBrief(ApiModel):
    """专注记录关联任务摘要。"""

    taskId: str | None = Field(default=None, description="任务标识。")
    title: str | None = Field(default=None, description="任务标题。")
    habitId: str | None = Field(default=None, description="习惯标识。")
    timerId: str | None = Field(default=None, description="计时器标识。")
    timerName: str | None = Field(default=None, description="计时器名称。")
    startTime: str | None = Field(default=None, description="开始时间。")
    endTime: str | None = Field(default=None, description="结束时间。")


class OpenFocus(ApiModel):
    """专注记录。"""

    id: str | None = Field(default=None, description="专注记录标识。")
    userId: int | None = Field(default=None, description="用户标识。")
    type: int | None = Field(default=None, description="专注类型。")
    taskId: str | None = Field(default=None, description="任务标识。")
    note: str | None = Field(default=None, description="备注。")
    tasks: list[OpenPomodoroTaskBrief] | None = Field(
        default=None, description="关联任务摘要。"
    )
    status: int | None = Field(default=None, description="状态。")
    startTime: str | None = Field(default=None, description="开始时间。")
    endTime: str | None = Field(default=None, description="结束时间。")
    duration: int | None = Field(default=None, description="持续时间。")


class OpenHabit(ApiModel):
    """习惯。"""

    id: str | None = Field(default=None, description="习惯标识。")
    name: str | None = Field(default=None, description="习惯名称。")
    iconRes: str | None = Field(default=None, description="图标资源。")
    color: str | None = Field(default=None, description="颜色。")
    sortOrder: int | None = Field(default=None, description="排序值。")
    status: int | None = Field(default=None, description="状态。")
    encouragement: str | None = Field(default=None, description="鼓励语。")
    totalCheckIns: int | None = Field(default=None, description="总打卡数。")
    type: str | None = Field(default=None, description="习惯类型。")
    goal: float | None = Field(default=None, description="目标值。")
    step: float | None = Field(default=None, description="步进值。")
    unit: str | None = Field(default=None, description="单位。")
    repeatRule: str | None = Field(default=None, description="重复规则。")
    reminders: list[str] | None = Field(default=None, description="提醒列表。")
    recordEnable: bool | None = Field(default=None, description="是否开启记录。")
    sectionId: str | None = Field(default=None, description="分组标识。")
    targetDays: int | None = Field(default=None, description="目标天数。")
    targetStartDate: int | None = Field(default=None, description="目标开始日期。")
    completedCycles: int | None = Field(default=None, description="完成周期数。")
    exDates: list[str] | None = Field(default=None, description="排除日期。")
    style: int | None = Field(default=None, description="样式。")


class OpenHabitCheckinData(ApiModel):
    """习惯打卡项。"""

    id: str | None = Field(default=None, description="打卡项标识。")
    stamp: int | None = Field(default=None, description="日期戳。")
    time: str | None = Field(default=None, description="打卡时间。")
    opTime: str | None = Field(default=None, description="操作时间。")
    value: float | None = Field(default=None, description="打卡值。")
    goal: float | None = Field(default=None, description="目标值。")
    status: int | None = Field(default=None, description="状态。")


class OpenHabitCheckin(ApiModel):
    """习惯打卡文档。"""

    id: str | None = Field(default=None, description="打卡文档标识。")
    habitId: str | None = Field(default=None, description="习惯标识。")
    createdTime: str | None = Field(default=None, description="创建时间。")
    modifiedTime: str | None = Field(default=None, description="修改时间。")
    etag: str | None = Field(default=None, description="实体标签。")
    year: int | None = Field(default=None, description="年份。")
    checkins: list[OpenHabitCheckinData] | None = Field(
        default=None, description="打卡项列表。"
    )


class TicktickApiClient:
    """Dida365 Open API 客户端封装。"""

    def __init__(
        self,
        token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 30.0,
        session: httpxyz.Client | None = None,
        user_agent: str | None = None,
    ) -> None:
        """初始化 API 客户端。"""
        self.config = ApiConfig(
            base_url=base_url,
            token=token,
            timeout_seconds=timeout_seconds,
            user_agent=user_agent or "ticktick-cli/0.1",
        )
        self.session = session or httpxyz.Client()

    def _headers(self) -> dict[str, str]:
        """构建请求头。"""
        return {
            "Authorization": f"Bearer {self.config.token}",
            "Accept": "application/json",
            "User-Agent": self.config.user_agent,
        }

    def _url(self, path: str) -> str:
        """拼接完整请求 URL。"""
        base_url = str(self.config.base_url)
        return f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | list[Any] | None = None,
    ) -> httpxyz.Response:
        """发起原始 HTTP 请求并返回响应对象。"""
        return self.session.request(
            method=method.upper(),
            url=self._url(path),
            params=params,
            json=payload,
            headers=self._headers(),
            timeout=self.config.timeout_seconds,
        )

    def _request_json(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """发起请求并解析 JSON（或原始文本）。"""
        response = self._request(method, path, params=params, payload=payload)
        if response.status_code >= 400:
            raise TicktickApiError(
                f"Request failed: {response.status_code} {response.text}",
                response.status_code,
            )
        if not response.content:
            return None
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    def _parse_list(self, model: type[ApiModel], items: Iterable[Any]) -> list[Any]:
        """将列表响应解析为模型列表。"""
        return [model.model_validate(item) for item in items]

    def list_projects(self) -> list[Project]:
        """获取当前用户的项目列表。"""
        payload = self._request_json("GET", "project")
        return self._parse_list(Project, payload or [])

    def get_project(self, project_id: str) -> Project:
        """根据项目 ID 获取项目信息。"""
        payload = self._request_json("GET", f"project/{project_id}")
        return Project.model_validate(payload)

    def get_project_data(self, project_id: str) -> ProjectData:
        """获取项目详情（包含任务与列）。"""
        payload = self._request_json("GET", f"project/{project_id}/data")
        return ProjectData.model_validate(payload)

    def create_project(self, project: ProjectCreate) -> Project:
        """创建项目并返回创建结果。"""
        payload = self._request_json("POST", "project", payload=project.model_dump())
        return Project.model_validate(payload)

    def update_project(self, project_id: str, project: ProjectUpdate) -> Project:
        """更新项目并返回更新结果。"""
        payload = self._request_json(
            "POST",
            f"project/{project_id}",
            payload=project.model_dump(exclude_none=True),
        )
        return Project.model_validate(payload)

    def delete_project(self, project_id: str) -> None:
        """删除指定项目。"""
        self._request_json("DELETE", f"project/{project_id}")

    def get_task(self, project_id: str, task_id: str) -> Task:
        """根据项目 ID 与任务 ID 获取任务。"""
        payload = self._request_json("GET", f"project/{project_id}/task/{task_id}")
        return Task.model_validate(payload)

    def create_task(self, task: TaskCreate) -> Task:
        """创建任务并返回创建结果。"""
        payload = self._request_json("POST", "task", payload=task.model_dump())
        return Task.model_validate(payload)

    def update_task(self, task_id: str, task: TaskUpdate) -> Task:
        """更新任务并返回更新结果。"""
        payload = self._request_json(
            "POST",
            f"task/{task_id}",
            payload=task.model_dump(exclude_none=True),
        )
        return Task.model_validate(payload)

    def complete_task(self, project_id: str, task_id: str) -> None:
        """完成指定任务。"""
        self._request_json("POST", f"project/{project_id}/task/{task_id}/complete")

    def delete_task(self, project_id: str, task_id: str) -> None:
        """删除指定任务。"""
        self._request_json("DELETE", f"project/{project_id}/task/{task_id}")

    def move_tasks(self, moves: list[TaskMove]) -> list[TaskMoveResult]:
        """移动一个或多个任务。"""
        payload = self._request_json(
            "POST",
            "task/move",
            payload=[move.model_dump() for move in moves],
        )
        return self._parse_list(TaskMoveResult, payload or [])

    def list_completed_tasks(self, filters: TaskCompletedFilter) -> list[Task]:
        """按完成时间查询已完成任务。"""
        payload = self._request_json(
            "POST",
            "task/completed",
            payload=filters.model_dump(exclude_none=True),
        )
        return self._parse_list(Task, payload or [])

    def filter_tasks(self, filters: TaskFilter) -> list[Task]:
        """按条件过滤任务。"""
        payload = self._request_json(
            "POST",
            "task/filter",
            payload=filters.model_dump(exclude_none=True),
        )
        return self._parse_list(Task, payload or [])

    def get_focus(self, focus_id: str, focus_type: int) -> OpenFocus:
        """获取专注记录。"""
        payload = self._request_json(
            "GET",
            f"focus/{focus_id}",
            params={"type": focus_type},
        )
        return OpenFocus.model_validate(payload)

    def list_focuses(
        self, from_time: str, to_time: str, focus_type: int
    ) -> list[OpenFocus]:
        """按时间范围获取专注记录。"""
        payload = self._request_json(
            "GET",
            "focus",
            params={"from": from_time, "to": to_time, "type": focus_type},
        )
        return self._parse_list(OpenFocus, payload or [])

    def delete_focus(self, focus_id: str, focus_type: int) -> OpenFocus:
        """删除专注记录。"""
        payload = self._request_json(
            "DELETE",
            f"focus/{focus_id}",
            params={"type": focus_type},
        )
        return OpenFocus.model_validate(payload)

    def list_habits(self) -> list[OpenHabit]:
        """获取全部习惯。"""
        payload = self._request_json("GET", "habit")
        return self._parse_list(OpenHabit, payload or [])

    def get_habit(self, habit_id: str) -> OpenHabit:
        """获取习惯详情。"""
        payload = self._request_json("GET", f"habit/{habit_id}")
        return OpenHabit.model_validate(payload)

    def create_habit(self, payload: dict[str, Any]) -> OpenHabit:
        """创建习惯。"""
        response = self._request_json("POST", "habit", payload=payload)
        return OpenHabit.model_validate(response)

    def update_habit(self, habit_id: str, payload: dict[str, Any]) -> OpenHabit:
        """更新习惯。"""
        response = self._request_json("POST", f"habit/{habit_id}", payload=payload)
        return OpenHabit.model_validate(response)

    def checkin_habit(self, habit_id: str, payload: dict[str, Any]) -> OpenHabitCheckin:
        """创建或更新习惯打卡。"""
        response = self._request_json(
            "POST",
            f"habit/{habit_id}/checkin",
            payload=payload,
        )
        return OpenHabitCheckin.model_validate(response)

    def list_habit_checkins(
        self, habit_ids: list[str], from_stamp: int, to_stamp: int
    ) -> list[OpenHabitCheckin]:
        """查询习惯打卡记录。"""
        payload = self._request_json(
            "GET",
            "habit/checkins",
            params={
                "habitIds": ",".join(habit_ids),
                "from": from_stamp,
                "to": to_stamp,
            },
        )
        return self._parse_list(OpenHabitCheckin, payload or [])


def main() -> None:
    print("Hello from ticktick_api_client.py!")


if __name__ == "__main__":
    main()
