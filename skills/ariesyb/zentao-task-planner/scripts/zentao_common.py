"""本技能内置的禅道工具。"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

try:
    from chinese_calendar import is_workday
except ModuleNotFoundError:
    def is_workday(day: datetime) -> bool:
        """缺少节假日库时，退化为周一到周五视为工作日。"""
        return day.weekday() < 5

TASK_PLAN_HEADER = "人员姓名\t需求编号\t任务名称（功能点）\t任务类型\t预计工时（小时）\t预计开始\t预计结束"
TASK_PLAN_HEADER_PREFIX = ["人员姓名", "需求编号", "任务名称（功能点）"]
WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

TASK_TYPE_DICT = {
    "需求": "requirementDocking",
    "市场/用户调研": "marketUserResearch",
    "产品方案设计": "productSolutionDesign",
    "产品方案评审": "productSolutionReview",
    "研发项目立项": "rdProjectInitiation",
    "研发项目管理": "rdProjectManagement",
    "需求分析": "requirementAnalysis",
    "通用需求": "commonRequirement",
    "UI设计": "uiDesign",
    "技术预研": "technicalPreResearch",
    "需求/UI评审": "requirementUiReview",
    "架构设计": "architectureDesign",
    "概要设计": "outlineDesign",
    "通用研发": "commonDevelop",
    "详细设计": "detailedDesign",
    "冒烟用例": "smokeTestCases",
    "测试用例": "testCases",
    "研发设计评审": "rdDesignReview",
    "前端编码": "frontendCoding",
    "后端编码": "backendCoding",
    "联调": "jointDebugging",
    "代码走查": "codeReview",
    "自测/单元测试": "selfTestingUnitTesting",
    "研发成果演示": "rdAchievementDemo",
    "UI走查": "uiReview",
    "产品验收": "productAcceptance",
    "版本提测": "versionTestSubmission",
    "测试用例评审": "testCaseReview",
    "通用测试": "commonTest",
    "测试准入检查": "testAccessCheck",
    "产品功能测试": "productFunctionTesting",
    "回归测试": "regressionTesting",
    "集成测试": "integrationTesting",
    "自动化测试": "automatedTesting",
    "安全测试": "securityTesting",
    "性能测试": "performanceTesting",
    "测试报告": "testReport",
    "生产问题复现": "productionIssueReproduction",
    "项目升级支持": "projectUpgradeSupport",
    "生产问题处理": "productionIssueHandling",
    "生产问题复盘": "productionIssueReview",
    "研发项目结项复盘": "rdProjectClosureReview",
    "质量体系建设": "qualitySystemConstruction",
    "质量审计稽查": "qualityAuditInspection",
    "质量统计度量": "qualityQualityMetrics",
    "质量问题整改": "qualityIssueRectification",
    "通用支持": "commonSupport",
    "售前支持": "preSalesSupport",
    "项目测试与演示支持": "projectTestingDemoSupport",
    "项目文档编写": "projectDocumentWriting",
    "生产安全加固": "productionSecurityReinforcement",
    "生产性能优化": "productionPerformanceOptimization",
    "项目其他支持": "projectOtherSupport",
    "培训": "training",
    "请假": "leaveApplication",
    "其他": "other",
    "内容运营": "contentOperation",
    "数据审核": "dataAudit",
    "通用运营": "commonOperation",
    "客服": "customService",
}


def strip_html_tags(html_text: str) -> str:
    """去掉 HTML 标签并压缩空白。"""
    if not html_text:
        return ""
    text = re.sub(r"<[^>]+>", "", html_text)
    return re.sub(r"\s+", " ", text).strip()


def read_text_input_with_stdin(text: Optional[str], file_path: Optional[str]) -> str:
    """从参数、文件或标准输入读取文本。"""
    if text and file_path:
        raise ValueError("不能同时提供文本和文件")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if text:
        return text

    import sys

    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("缺少输入文本")


def read_json_input(raw_json: Optional[str], file_path: Optional[str]) -> Dict[str, str]:
    """从文本或文件读取 JSON 对象。"""
    if raw_json and file_path:
        raise ValueError("不能同时提供 JSON 文本和 JSON 文件")
    if file_path:
        return json.loads(Path(file_path).read_text(encoding="utf-8"))
    if raw_json:
        return json.loads(raw_json)
    return {}


def print_json(data: Dict[str, Any]) -> None:
    """稳定格式输出 JSON。"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def load_skill_env(env_file: Optional[str] = None) -> None:
    """优先加载技能目录内的 .env。"""
    candidates: List[Path] = []
    if env_file:
        candidates.append(Path(env_file).resolve())
    else:
        candidates.append(Path(__file__).resolve().parents[1] / ".env")

    for candidate in candidates:
        if candidate.exists():
            load_dotenv(candidate, override=False)


@dataclass
class ZentaoConfig:
    base_url: str
    account: str
    password: str

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "ZentaoConfig":
        load_skill_env(env_file=env_file)

        base_url = os.getenv("ZENTAO_BASE_URL", "").strip()
        account = os.getenv("ZENTAO_ACCOUNT", "").strip()
        password = os.getenv("ZENTAO_PASSWORD", "").strip()

        missing = [
            name
            for name, value in (
                ("ZENTAO_BASE_URL", base_url),
                ("ZENTAO_ACCOUNT", account),
                ("ZENTAO_PASSWORD", password),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"缺少环境变量: {', '.join(missing)}")

        return cls(
            base_url=base_url.rstrip("/") + "/",
            account=account,
            password=password,
        )


@dataclass
class TaskPlanRow:
    line_num: int
    chinese_name: str
    assigned_to: str
    story_id: int
    task_name: str
    task_type_cn: str
    task_type: str
    estimate: float
    est_started: str
    deadline: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_date_string(value: str) -> str:
    """把日期统一成 YYYY-MM-DD。"""
    text = value.strip().replace("/", "-")
    parsed = datetime.strptime(text, "%Y-%m-%d")
    return parsed.strftime("%Y-%m-%d")


def get_current_date() -> Dict[str, Any]:
    """获取当前日期、星期和是否工作日。"""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "weekday": WEEKDAY_NAMES[now.weekday()],
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "today_is_workday": is_workday(now),
    }


def get_next_workdays(week_type: Literal["current", "next"] = "next") -> Dict[str, Any]:
    """获取当前或下一段连续工作日。"""
    workdays: List[Dict[str, Any]] = []
    current_date = datetime.now()
    today_is_workday = is_workday(current_date)

    if week_type == "current":
        date_to_check = current_date
        if not today_is_workday:
            date_to_check += timedelta(days=1)
            while not is_workday(date_to_check):
                date_to_check += timedelta(days=1)
    else:
        date_to_check = current_date + timedelta(days=1)
        if today_is_workday:
            while is_workday(date_to_check):
                date_to_check += timedelta(days=1)
        while not is_workday(date_to_check):
            date_to_check += timedelta(days=1)

    while is_workday(date_to_check):
        workdays.append(
            {
                "date": date_to_check.strftime("%Y-%m-%d"),
                "weekday": WEEKDAY_NAMES[date_to_check.weekday()],
                "is_workday": True,
            }
        )
        date_to_check += timedelta(days=1)

    return {
        "today": get_current_date(),
        "today_is_workday": today_is_workday,
        "workdays": workdays,
        "week_type": week_type,
    }


def resolve_assigned_to(
    chinese_name: str,
    username_mapping: Dict[str, str],
    user_list: Dict[str, str],
) -> str:
    """把中文姓名解析成禅道用户名。"""
    explicit = username_mapping.get(chinese_name)
    if explicit:
        return explicit

    matched_usernames = [
        username
        for username, display_name in user_list.items()
        if str(display_name).strip() == chinese_name
    ]
    if len(matched_usernames) == 1:
        return matched_usernames[0]
    if len(matched_usernames) > 1:
        raise ValueError(f'用户名"{chinese_name}"匹配到多个禅道账号，请提供显式映射')
    raise ValueError(f'用户名"{chinese_name}"未在映射表或禅道用户列表中找到')


def parse_task_plan_text(
    text_data: str,
    username_mapping: Optional[Dict[str, str]],
    user_list: Dict[str, str],
    task_type_map: Dict[str, str],
) -> Tuple[List[TaskPlanRow], List[str]]:
    """解析标准化任务表。"""
    username_mapping = username_mapping or {}
    rows: List[TaskPlanRow] = []
    errors: List[str] = []

    for line_num, raw_line in enumerate(text_data.splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue

        parts = [part.strip() for part in line.split("\t")]
        if parts[:3] == TASK_PLAN_HEADER_PREFIX:
            continue
        if len(parts) != 7:
            errors.append(f"第{line_num}行: 数据格式错误，需要严格的 7 列制表符数据")
            continue

        chinese_name, story_id_str, task_name, task_type_cn, estimate_str, est_started, deadline = parts

        try:
            assigned_to = resolve_assigned_to(chinese_name, username_mapping, user_list)
        except ValueError as exc:
            errors.append(f"第{line_num}行: {exc}")
            continue

        try:
            story_id = int(story_id_str)
        except ValueError:
            errors.append(f'第{line_num}行: 需求ID"{story_id_str}"格式错误')
            continue

        task_type = task_type_map.get(task_type_cn)
        if not task_type:
            errors.append(f'第{line_num}行: 任务类型"{task_type_cn}"无效或未标准化')
            continue

        try:
            estimate = float(estimate_str)
            if estimate <= 0:
                raise ValueError
        except ValueError:
            errors.append(f'第{line_num}行: 预估工时"{estimate_str}"格式错误')
            continue

        try:
            normalized_started = normalize_date_string(est_started)
            normalized_deadline = normalize_date_string(deadline)
        except ValueError:
            errors.append(f"第{line_num}行: 日期格式错误，应为 YYYY-MM-DD 或 YYYY/MM/DD")
            continue

        if normalized_deadline < normalized_started:
            errors.append(f"第{line_num}行: 结束日期不能早于开始日期")
            continue

        if not task_name:
            errors.append(f"第{line_num}行: 任务名称不能为空")
            continue

        rows.append(
            TaskPlanRow(
                line_num=line_num,
                chinese_name=chinese_name,
                assigned_to=assigned_to,
                story_id=story_id,
                task_name=task_name,
                task_type_cn=task_type_cn,
                task_type=task_type,
                estimate=estimate,
                est_started=normalized_started,
                deadline=normalized_deadline,
            )
        )

    return rows, errors


class ZentaoClient:
    """供技能脚本使用的独立禅道 HTTP 客户端。"""

    def __init__(self, config: ZentaoConfig) -> None:
        self.base_url = config.base_url
        self.account = config.account
        self.password = config.password
        self.session = requests.Session()
        self.session_id: Optional[str] = None
        self.is_logged_in = False

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "ZentaoClient":
        return cls(ZentaoConfig.from_env(env_file=env_file))

    def login(self) -> bool:
        url = f"{self.base_url}user-login.json"
        response = self.session.post(
            url,
            params={"account": self.account, "password": self.password},
        )

        if response.status_code != 200:
            return False

        response_data = response.json()
        if response_data.get("status") != "success":
            return False

        self.session_id = response.cookies.get("zentaosid")
        self.is_logged_in = bool(self.session_id)
        return self.is_logged_in

    def ensure_logged_in(self) -> None:
        if not self.is_logged_in or not self.session_id:
            raise ValueError("请先登录禅道")

    def _parse_response_data(self, response: requests.Response) -> Dict[str, Any]:
        if response.status_code != 200:
            raise ValueError(f"请求失败，状态码: {response.status_code}")

        outer_data = response.json()
        if outer_data.get("status") != "success":
            raise ValueError(f"API返回失败: {outer_data.get('reason', '未知错误')}")

        data_str = outer_data.get("data", "{}")
        try:
            return json.loads(data_str)
        except json.JSONDecodeError as exc:
            raise ValueError(f"解析响应数据失败: {exc}") from exc

    def get_story_detail(self, story_id: int) -> Dict[str, Any]:
        self.ensure_logged_in()
        response = self.session.post(f"{self.base_url}story-view-{story_id}.json")
        data = self._parse_response_data(response)
        return data.get("story", {})

    def get_user_list(self) -> Dict[str, str]:
        self.ensure_logged_in()
        response = self.session.post(f"{self.base_url}my-managecontacts.json")
        data = self._parse_response_data(response)
        return data.get("users", {})

    def get_my_tasks(self, view: str = "active") -> Dict[str, Any]:
        self.ensure_logged_in()
        endpoint_map = {
            "active": "my-task.json",
            "assignedTo": "my-task-assignedTo.json",
            "finishedBy": "my-task-finishedBy.json",
            "closedBy": "my-task-closedBy.json",
        }
        if view not in endpoint_map:
            raise ValueError(f"不支持的任务视图: {view}")
        response = self.session.post(f"{self.base_url}{endpoint_map[view]}")
        return self._parse_response_data(response)

    def get_doing_projects(self) -> List[Dict[str, Any]]:
        self.ensure_logged_in()
        response = self.session.post(f"{self.base_url}project-all-doing-order_desc-0.json")
        data = self._parse_response_data(response)
        return data.get("projectStats", [])

    def get_task_types(self, project_id: Optional[int] = None) -> Dict[str, str]:
        self.ensure_logged_in()

        resolved_project_id = project_id
        if not resolved_project_id:
            projects = self.get_doing_projects()
            if not projects:
                raise ValueError("无法获取进行中的项目以解析任务类型")
            resolved_project_id = int(projects[0]["id"])

        url = f"{self.base_url}task-create-{resolved_project_id}-0-0.html"
        response = self.session.get(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
                "Referer": f"{self.base_url}my-task.html",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        if response.status_code != 200:
            raise RuntimeError(f"获取创建任务页面失败，状态码: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        type_select = soup.find("select", {"name": "type"})
        if not type_select:
            raise ValueError("无法在页面中找到任务类型选择元素")

        task_types: Dict[str, str] = {}
        for option in type_select.find_all("option"):
            value = option.get("value")
            text = option.get_text(strip=True)
            if value and text:
                task_types[text] = value

        if not task_types:
            raise ValueError("未能解析到任何任务类型")
        return task_types

    def get_task_detail(self, task_id: int) -> Dict[str, Any]:
        self.ensure_logged_in()
        response = self.session.post(f"{self.base_url}task-view-{task_id}.json")
        data = self._parse_response_data(response)
        return data.get("task", {})

    @staticmethod
    def _format_hour_value(value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")

    @staticmethod
    def _is_finished_task_detail(task_detail: Dict[str, Any]) -> bool:
        status = str(task_detail.get("status", "")).strip().lower()
        if status in {"done", "closed"}:
            return True
        finished_by = str(task_detail.get("finishedBy", "")).strip()
        finished_date = str(task_detail.get("finishedDate", "")).strip()
        return bool(finished_by) and finished_by != "0" and not finished_date.startswith("0000-00-00")

    @staticmethod
    def _extract_submit_error(response_text: str) -> str:
        if not response_text:
            return "提交后任务状态和工时都没有变化"

        patterns = [
            r"alert\(['\"](.+?)['\"]\)",
            r'"message"\s*:\s*"(.+?)"',
            r'"reason"\s*:\s*"(.+?)"',
            r"<div[^>]*class=['\"][^'\"]*alert[^'\"]*['\"][^>]*>(.*?)</div>",
            r"<td[^>]*class=['\"][^'\"]*message[^'\"]*['\"][^>]*>(.*?)</td>",
        ]
        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
            if match:
                message = strip_html_tags(match.group(1)).strip()
                if message:
                    return message

        plain_text = strip_html_tags(response_text).strip()
        return plain_text[:200] if plain_text else "提交后任务状态和工时都没有变化"

    @staticmethod
    def _extract_form_data(response_text: str) -> Dict[str, str]:
        soup = BeautifulSoup(response_text, "html.parser")
        form = soup.find("form")
        if not form:
            return {}

        form_data: Dict[str, str] = {}
        for field in form.find_all(["input", "textarea", "select"]):
            name = field.get("name")
            if not name:
                continue

            tag_name = field.name.lower()
            field_type = str(field.get("type", "")).lower()
            if tag_name == "input":
                if field_type in {"checkbox", "radio"} and not field.has_attr("checked"):
                    continue
                form_data[name] = field.get("value", "")
            elif tag_name == "textarea":
                form_data[name] = field.get_text()
            elif tag_name == "select":
                selected_option = field.find("option", selected=True) or field.find("option")
                form_data[name] = selected_option.get("value", "") if selected_option else ""
        return form_data

    @staticmethod
    def _extract_form_field_names(response_text: str) -> List[str]:
        soup = BeautifulSoup(response_text, "html.parser")
        field_names: List[str] = []
        for field in soup.find_all(["input", "textarea", "select"]):
            name = field.get("name")
            if name:
                field_names.append(name)
        return field_names

    @classmethod
    def _build_finish_consumed_updates(
        cls,
        form_data: Dict[str, str],
        consumed: Optional[float],
    ) -> Dict[str, str]:
        if consumed is None:
            return {}

        consumed_value = cls._format_hour_value(consumed)
        updates: Dict[str, str] = {}
        candidate_keys = [key for key in form_data if "consumed" in key.lower()]

        if "consumed" in form_data:
            updates["consumed"] = consumed_value
        for key in candidate_keys:
            updates[key] = consumed_value
        if not updates:
            updates["consumed"] = consumed_value
        return updates

    def create_task_from_story(
        self,
        story_id: int,
        task_type: str,
        task_name: str,
        assigned_to: str,
        estimate: float,
        priority: int = 3,
        est_started: Optional[str] = None,
        deadline: Optional[str] = None,
    ) -> Dict[str, Any]:
        self.ensure_logged_in()
        story_detail = self.get_story_detail(story_id)
        if not story_detail:
            raise ValueError(f"无法获取需求 {story_id} 的详情")

        module_id = story_detail.get("module")
        if not module_id:
            raise ValueError(f"无法从需求 {story_id} 的详情中获取模块ID")

        try:
            module_id = int(module_id)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"模块ID格式错误: {module_id}") from exc

        projects = story_detail.get("projects", {})
        if not projects:
            raise ValueError("无法从需求详情中获取项目ID")

        project_id = list(projects.keys())[0]
        try:
            project_id = int(project_id)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"项目ID格式错误: {project_id}") from exc

        description = strip_html_tags(story_detail.get("spec", ""))
        return self._create_task(
            project_id=project_id,
            story_id=story_id,
            module_id=module_id,
            task_type=task_type,
            name=task_name,
            description=description,
            assigned_to=assigned_to,
            estimate=estimate,
            priority=priority,
            est_started=est_started,
            deadline=deadline,
        )

    def _create_task(
        self,
        project_id: int,
        story_id: int,
        module_id: int,
        task_type: str,
        name: str,
        description: str,
        assigned_to: str,
        estimate: float,
        priority: int = 3,
        est_started: Optional[str] = None,
        deadline: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}task-create-{project_id}-{story_id}-{module_id}.html"
        today = datetime.now().strftime("%Y-%m-%d")
        if not est_started:
            est_started = today
        if not deadline:
            deadline = today

        data = {
            "functionEstimates": "{}",
            "project": str(project_id),
            "story": str(story_id),
            "module[]": str(module_id),
            "type": task_type,
            "estimate": self._format_hour_value(estimate),
            "estStarted": est_started,
            "deadline": deadline,
            "assignedTo[]": assigned_to,
            "name": strip_html_tags(name),
            "desc": strip_html_tags(description),
            "pri": str(priority),
            "storyEstimate": "0",
            "storyPri": "1",
            "color": "",
            "labels[]": "",
            "files[]": "",
            "mailto[]": "",
            "after": "continueAdding",
            "uid": str(uuid.uuid4()),
            "team[]": "",
            "teamEstimate[]": "",
            "functionMapping": "{}",
        }

        response = self.session.post(
            url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Origin": self.base_url.rstrip("/"),
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
            },
            data=data,
        )

        if response.status_code != 200:
            raise RuntimeError(f"创建任务请求失败，状态码: {response.status_code}")

        return {
            "success": True,
            "response_excerpt": strip_html_tags(response.text)[:200],
        }

    def close_task(self, task_id: int, comment: str = "") -> bool:
        self.ensure_logged_in()
        url = f"{self.base_url}task-close-{task_id}.html?onlybody=yes"
        response = self.session.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"获取关闭任务页面失败，状态码: {response.status_code}")

        uid_match = re.search(r"var kuid = '([a-f0-9]+)';", response.text)
        if uid_match:
            uid = uid_match.group(1)
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            uid_input = soup.find("input", {"id": "uid", "name": "uid"})
            if not uid_input:
                raise ValueError(f"无法提取uid参数，任务ID: {task_id}")
            uid = uid_input.get("value")

        submit = self.session.post(
            url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": url,
                "Origin": self.base_url.rstrip("/"),
                "Connection": "keep-alive",
            },
            data={"comment": comment, "uid": uid},
        )
        return submit.status_code == 200

    def finish_task(
        self,
        task_id: int,
        consumed: Optional[float] = None,
        left: float = 0,
        comment: str = "",
    ) -> bool:
        self.ensure_logged_in()
        before_detail = self.get_task_detail(task_id)

        url = f"{self.base_url}task-finish-{task_id}.html?onlybody=yes"
        response = self.session.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"获取完成任务页面失败，状态码: {response.status_code}")

        post_data = self._extract_form_data(response.text)
        uid_match = re.search(r"var kuid = '([a-f0-9]+)';", response.text)
        if uid_match:
            uid = uid_match.group(1)
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            uid_input = soup.find("input", {"id": "uid", "name": "uid"})
            if not uid_input:
                raise ValueError(f"无法提取uid参数，任务ID: {task_id}")
            uid = uid_input.get("value")

        post_data["left"] = self._format_hour_value(left)
        post_data["comment"] = comment
        post_data["uid"] = uid
        post_data.update(self._build_finish_consumed_updates(post_data, consumed))

        submit = self.session.post(
            url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": url,
                "Origin": self.base_url.rstrip("/"),
                "Connection": "keep-alive",
            },
            data=post_data,
        )
        if submit.status_code != 200:
            raise RuntimeError(f"完成任务请求失败，状态码: {submit.status_code}")

        after_detail = self.get_task_detail(task_id)
        if self._is_finished_task_detail(after_detail):
            return True

        before_consumed = self._parse_float_value(before_detail.get("consumed"))
        after_consumed = self._parse_float_value(after_detail.get("consumed"))
        after_left = self._parse_float_value(after_detail.get("left"))

        if consumed is not None and after_consumed >= before_consumed + consumed and after_left == float(left):
            return True
        if consumed is None and after_left == float(left):
            return True

        field_names = self._extract_form_field_names(submit.text)
        consumed_fields = [name for name in field_names if "consumed" in name.lower()]
        debug_suffix = ""
        if consumed_fields:
            debug_suffix = f"；页面工时字段: {', '.join(consumed_fields)}"
        raise RuntimeError(f"{self._extract_submit_error(submit.text)}{debug_suffix}")

    @staticmethod
    def _normalize_task_list(tasks: Any) -> List[Dict[str, Any]]:
        if isinstance(tasks, list):
            return tasks
        if isinstance(tasks, dict):
            return list(tasks.values())
        return []

    @staticmethod
    def _parse_date_value(value: Any) -> Optional[date]:
        if value is None:
            return None
        text = str(value).strip()
        if not text or text.startswith("0000-00-00"):
            return None
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_float_value(value: Any, default: float = 0.0) -> float:
        if value is None:
            return default
        try:
            return float(str(value).strip())
        except (TypeError, ValueError):
            return default

    @classmethod
    def is_task_closed(cls, task: Dict[str, Any]) -> bool:
        status = str(task.get("status", "")).strip().lower()
        if status == "closed":
            return True
        return cls._parse_date_value(task.get("closedDate")) is not None

    @classmethod
    def filter_tasks_by_date(
        cls,
        tasks: Any,
        start_date: str,
        end_date: Optional[str] = None,
        date_field: str = "range",
        statuses: Optional[Iterable[str]] = None,
        exclude_closed: bool = True,
    ) -> List[Dict[str, Any]]:
        normalized_tasks = cls._normalize_task_list(tasks)
        start = cls._parse_date_value(start_date)
        end = cls._parse_date_value(end_date or start_date)
        if not start or not end:
            raise ValueError("开始日期或结束日期格式错误")
        if end < start:
            raise ValueError("结束日期不能早于开始日期")

        allowed_statuses = {status.strip() for status in statuses or () if status}
        matched: List[Dict[str, Any]] = []

        for task in normalized_tasks:
            if exclude_closed and cls.is_task_closed(task):
                continue
            if allowed_statuses and str(task.get("status", "")).strip() not in allowed_statuses:
                continue

            est_started = cls._parse_date_value(task.get("estStarted"))
            deadline = cls._parse_date_value(task.get("deadline"))

            if date_field == "estStarted":
                if est_started and start <= est_started <= end:
                    matched.append(task)
                continue
            if date_field == "deadline":
                if deadline and start <= deadline <= end:
                    matched.append(task)
                continue

            if est_started and deadline and est_started <= end and deadline >= start:
                matched.append(task)
        return matched

    @classmethod
    def calculate_finish_consumed(cls, task: Dict[str, Any]) -> float:
        estimate = cls._parse_float_value(task.get("estimate"))
        consumed = cls._parse_float_value(task.get("consumed"))
        return max(estimate - consumed, 0.0)

    def auto_finish_tasks_by_date(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        date_field: str = "range",
        statuses: Optional[Iterable[str]] = None,
        comment: str = "按预估工时自动完成任务",
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        self.ensure_logged_in()

        statuses = tuple(statuses or ("wait", "doing", "pause"))
        tasks_data = self.get_my_tasks()
        task_list = self._normalize_task_list(tasks_data.get("tasks", []))
        matched_tasks = self.filter_tasks_by_date(
            task_list,
            start_date=start_date,
            end_date=end_date,
            date_field=date_field,
            statuses=statuses,
            exclude_closed=True,
        )

        results: List[Dict[str, Any]] = []
        success_count = 0
        skipped_count = 0
        failed_count = 0

        for task in matched_tasks:
            task_id = task.get("id")
            estimate = self._parse_float_value(task.get("estimate"))
            current_consumed = self._parse_float_value(task.get("consumed"))
            finish_consumed = self.calculate_finish_consumed(task)

            if estimate <= 0:
                results.append(
                    {
                        "task_id": task_id,
                        "task_name": task.get("name"),
                        "status": "skipped",
                        "reason": "预估工时为空或小于等于0，无法按预估工时自动完成",
                    }
                )
                skipped_count += 1
                continue

            result_item = {
                "task_id": task_id,
                "task_name": task.get("name"),
                "matched_by": date_field,
                "estimate": estimate,
                "current_consumed": current_consumed,
                "finish_consumed": finish_consumed,
                "left": 0,
            }

            if dry_run:
                result_item["status"] = "planned"
                results.append(result_item)
                continue

            try:
                success = self.finish_task(
                    task_id=task_id,
                    consumed=finish_consumed if finish_consumed > 0 else None,
                    left=0,
                    comment=comment,
                )
                result_item["status"] = "success" if success else "failed"
                results.append(result_item)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as exc:  # noqa: BLE001
                result_item["status"] = "failed"
                result_item["reason"] = str(exc)
                results.append(result_item)
                failed_count += 1

        return {
            "start_date": start_date,
            "end_date": end_date or start_date,
            "date_field": date_field,
            "dry_run": dry_run,
            "matched_count": len(matched_tasks),
            "success_count": success_count,
            "skipped_count": skipped_count,
            "failed_count": failed_count,
            "results": results,
        }

    def list_closable_finished_tasks(self) -> List[Dict[str, Any]]:
        self.ensure_logged_in()
        tasks = self.get_my_tasks()
        task_list = self._normalize_task_list(tasks.get("tasks", []))
        return [
            task
            for task in task_list
            if str(task.get("status", "")).strip() == "done"
            and not self.is_task_closed(task)
        ]

    def close_finished_tasks(self, comment: str = "", execute: bool = False) -> Dict[str, Any]:
        matched_tasks = self.list_closable_finished_tasks()
        if not execute:
            return {"matched_count": len(matched_tasks), "tasks": matched_tasks}

        results: List[Dict[str, Any]] = []
        success_count = 0
        failed_count = 0

        for task in matched_tasks:
            task_id = task.get("id")
            try:
                success = self.close_task(task_id=task_id, comment=comment)
                results.append(
                    {
                        "task_id": task_id,
                        "task_name": task.get("name"),
                        "success": success,
                    }
                )
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "task_id": task_id,
                        "task_name": task.get("name"),
                        "success": False,
                        "error": str(exc),
                    }
                )
                failed_count += 1

        return {
            "matched_count": len(matched_tasks),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results,
        }

    def batch_create_tasks_from_text(
        self,
        text_data: str,
        username_mapping: Optional[Dict[str, str]] = None,
        execute_create: bool = False,
    ) -> Dict[str, Any]:
        self.ensure_logged_in()
        username_mapping = username_mapping or {}

        user_list = self.get_user_list()
        try:
            task_type_map = self.get_task_types()
            task_type_source = "dynamic"
        except Exception as exc:  # noqa: BLE001
            task_type_map = TASK_TYPE_DICT.copy()
            task_type_source = f"static-fallback: {exc}"

        tasks_to_create, validation_errors = parse_task_plan_text(
            text_data=text_data,
            username_mapping=username_mapping,
            user_list=user_list,
            task_type_map=task_type_map,
        )

        validated_tasks: List[TaskPlanRow] = []
        for task in tasks_to_create:
            story_detail = self.get_story_detail(task.story_id)
            if not story_detail:
                validation_errors.append(
                    f"第{task.line_num}行: 需求ID {task.story_id} 不存在或无法获取详情"
                )
                continue
            validated_tasks.append(task)

        if validation_errors:
            return {
                "validation_passed": False,
                "task_type_source": task_type_source,
                "validation_errors": validation_errors,
                "tasks_to_create": [task.to_dict() for task in validated_tasks],
                "create_results": [],
            }

        if not execute_create:
            return {
                "validation_passed": True,
                "task_type_source": task_type_source,
                "validation_errors": [],
                "tasks_to_create": [task.to_dict() for task in validated_tasks],
                "create_results": [],
            }

        create_results: List[Dict[str, Any]] = []
        for task in validated_tasks:
            try:
                result = self.create_task_from_story(
                    story_id=task.story_id,
                    task_type=task.task_type,
                    task_name=task.task_name,
                    assigned_to=task.assigned_to,
                    estimate=task.estimate,
                    priority=3,
                    est_started=task.est_started,
                    deadline=task.deadline,
                )
                create_results.append(
                    {
                        "line_num": task.line_num,
                        "task_name": task.task_name,
                        "story_id": task.story_id,
                        "assigned_to": task.assigned_to,
                        "success": True,
                        "result": result,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                create_results.append(
                    {
                        "line_num": task.line_num,
                        "task_name": task.task_name,
                        "story_id": task.story_id,
                        "assigned_to": task.assigned_to,
                        "success": False,
                        "error": str(exc),
                    }
                )

        return {
            "validation_passed": True,
            "task_type_source": task_type_source,
            "validation_errors": [],
            "tasks_to_create": [task.to_dict() for task in validated_tasks],
            "create_results": create_results,
        }
