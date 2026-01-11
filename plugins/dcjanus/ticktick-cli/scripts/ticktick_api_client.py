from __future__ import annotations

from typing import Any, Iterable

import httpx
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
    status: int | None = Field(default=None, description="子任务状态（0 未完成，1 已完成）。")
    completedTime: str | int | None = Field(default=None, description="子任务完成时间。")
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
    priority: int | None = Field(default=None, description="任务优先级。")
    status: int | None = Field(default=None, description="任务状态。")
    completedTime: str | None = Field(default=None, description="任务完成时间。")
    sortOrder: int | None = Field(default=None, description="任务排序值。")
    items: list[ChecklistItem] | None = Field(default=None, description="子任务列表。")


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


class TicktickApiClient:
    """Dida365 Open API 客户端封装。"""
    def __init__(
        self,
        token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 30.0,
        session: httpx.Client | None = None,
        user_agent: str | None = None,
    ) -> None:
        """初始化 API 客户端。"""
        self.config = ApiConfig(
            base_url=base_url,
            token=token,
            timeout_seconds=timeout_seconds,
            user_agent=user_agent or "ticktick-cli/0.1",
        )
        self.session = session or httpx.Client()

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
        params: dict[str, str] | None = None,
        payload: dict[str, Any] | list[Any] | None = None,
    ) -> httpx.Response:
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
        params: dict[str, str] | None = None,
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

def main() -> None:
    print("Hello from ticktick_api_client.py!")


if __name__ == "__main__":
    main()
