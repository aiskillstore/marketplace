#!/usr/bin/env python3
"""Generate a reviewer-oriented operation manual Markdown draft."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from common import ensure_dir, read_json


def humanize_feature(name: str) -> str:
    raw = Path(name).stem if "/" in name else name
    raw = re.sub(r"[-_]+", " ", raw).strip()
    mapping = {
        "login": "软件登录",
        "register": "用户注册",
        "auth": "用户认证",
        "home": "首页",
        "index": "首页",
        "dashboard": "数据看板",
        "project": "项目管理",
        "projects": "项目管理",
        "projectsettings": "项目设置",
        "projectssettings": "项目设置",
        "setting": "系统设置",
        "settings": "系统设置",
        "asset": "资源管理",
        "assets": "资源管理",
        "user": "用户管理",
        "users": "用户管理",
        "billing": "费用管理",
        "agentstatusbar": "智能体状态展示",
        "messagebubble": "消息展示",
        "chatpanel": "对话面板",
        "chatinput": "对话输入",
        "assetpanel": "资源面板",
    }
    key = raw.lower().replace(" ", "")
    return mapping.get(key, raw.title() if raw else "核心功能")


def feature_list(analysis: dict[str, Any]) -> list[str]:
    candidates = analysis.get("feature_candidates") or []
    pages = (analysis.get("source", {}).get("categorized_files") or {}).get("page", [])
    stop = {"providers", "globals", "layout", "page", "index", "loading", "error", "app"}
    names: list[str] = []
    for item in candidates + pages:
        title = humanize_feature(item)
        item_key = Path(str(item)).stem.lower()
        if title and title not in names and title.lower() not in stop and item_key not in stop:
            names.append(title)
    return names[:10] or ["首页", "核心业务操作", "数据查看", "系统设置"]


def join_items(items: list[str], limit: int = 4) -> str:
    values = [str(item) for item in items if str(item).strip()]
    if not values:
        return "业务用户"
    return "、".join(values[:limit])


def feature_summary(feature: str, detail: str, software_name: str) -> str:
    clean_detail = normalize_detail(feature, detail)
    category = module_category(feature, clean_detail)
    second = {
        "auth": "该功能让系统能够识别当前使用者，并把用户带入可继续操作的页面。",
        "entry": "该功能帮助用户快速了解当前可办理事项，并进入后续业务页面。",
        "query": "用户可以通过查看、搜索或筛选信息，找到需要继续处理的数据。",
        "form": "用户可以按页面要求录入或修改信息，并在提交后获得保存结果。",
        "workflow": "用户可以查看处理进度、确认关键结果，并根据页面提示继续推进。",
        "resource": "用户可以集中查看、保存和复用相关资料，减少重复查找。",
        "report": "用户可以查看汇总结果，了解业务数据或处理情况的变化。",
        "settings": "用户可以维护基础配置，使软件按实际管理要求运行。",
        "creation": "用户可以输入要求、查看生成结果，并对结果进行确认或调整。",
        "general": "用户可以在页面中完成对应操作，并看到清楚的结果反馈。",
    }
    return f"{feature}主要用于{clean_detail.rstrip('。')}。{second.get(category, second['general'])}"


def plain_manual_text(text: str) -> str:
    value = text
    replacements = {
        "多 Agent": "多智能体",
        "多 agent": "多智能体",
        "业务逻辑": "使用过程",
        "前端页面": "软件页面",
        "前端": "界面",
        "后端服务": "系统服务",
        "后端": "系统服务",
        "接口": "数据通道",
        "组件": "页面组成部分",
        "路由": "页面入口",
        "状态管理": "状态记录",
        "数据持久化": "数据保存",
        "异步任务": "后台处理任务",
        "任务队列": "任务处理服务",
        "模型": "智能服务",
        "调度中心": "协调中心",
        "结构化依据": "后续说明",
        "高成本生成": "耗时较长的内容生成",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"(?<![A-Za-z])Agent(?![A-Za-z])", "智能体", value)
    value = re.sub(r"(?<![A-Za-z])agent(?![A-Za-z])", "智能体", value)
    value = re.sub(r"\b[A-Za-z]+\.js\b", "相关界面技术", value)
    value = re.sub(r"\bReact\b|\bVue\b|\bVite\b|\bNext\b|\bNext\.js\b|\bFastAPI\b|\bLangGraph\b|\bCelery\b|\bSSE\b", "相关软件能力", value)
    value = re.sub(r"相关软件能力、相关软件能力", "相关软件能力", value)
    return value


def plain_feature_name(name: str) -> str:
    value = plain_manual_text(str(name))
    value = value.replace("Chat", "对话")
    return value.strip() or "核心功能"


def normalize_detail(feature: str, detail: str) -> str:
    value = plain_manual_text(detail or "").strip()
    value = re.sub(rf"^{re.escape(feature)}[：:，, ]*", "", value)
    value = re.sub(rf"^{re.escape(feature)}(模块|功能)?用于", "", value)
    value = re.sub(rf"^{re.escape(feature)}主要用于", "", value)
    value = re.sub(rf"^用户使用{re.escape(feature)}时，可以", "", value)
    value = re.sub(rf"^进入{re.escape(feature)}后，用户可以", "", value)
    value = re.sub(rf"^在{re.escape(feature)}中，用户可以", "", value)
    value = re.sub(rf"^用户通过{re.escape(feature)}可以", "", value)
    value = re.sub(rf"^在{re.escape(feature)}环节，用户可以", "", value)
    value = re.sub(rf"^通过{re.escape(feature)}，用户可以", "", value)
    value = value.strip("。；; ，,")
    if not value or value == feature:
        value = "支撑软件中的相关业务处理，帮助用户完成信息查看、内容填写、结果确认或资料维护"
    return value + ("。" if not value.endswith("。") else "")


def module_category(feature: str, detail: str) -> str:
    text = f"{feature} {detail}"
    rules = [
        ("auth", ("登录", "注册", "认证", "账号", "密码", "权限")),
        ("entry", ("首页", "概览", "工作台", "看板", "导航")),
        ("query", ("查询", "搜索", "筛选", "检索", "列表", "查看")),
        ("form", ("新增", "编辑", "填写", "录入", "提交", "表单", "创建", "申请")),
        ("workflow", ("流程", "审批", "审核", "确认", "任务", "工单", "进度", "状态", "处理")),
        ("resource", ("文件", "文档", "资料", "素材", "资源", "资产", "附件", "导入", "导出")),
        ("report", ("报表", "统计", "分析", "图表", "汇总", "报告")),
        ("settings", ("设置", "配置", "参数", "角色", "组织", "用户管理")),
        ("creation", ("生成", "创作", "对话", "内容", "文本", "图片", "音频", "视频")),
    ]
    for category, keys in rules:
        if any(key in text for key in keys):
            return category
    return "general"


CATEGORY_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "auth": {
        "usage": "用户进入该页面后，先按照页面要求填写身份信息，再提交验证。验证通过后，软件会进入可使用的业务页面；验证失败时，页面会给出相应提示。",
        "steps": ["打开软件访问地址或登录入口。", "填写页面要求的账号、密码、验证码或其他身份信息。", "点击登录、确认或提交按钮。", "根据页面提示进入首页，或修改信息后重新提交。"],
        "result": "完成该操作后，软件会确认当前使用者身份，并展示其可以继续使用的功能入口。",
    },
    "entry": {
        "usage": "该页面通常用于集中展示软件名称、导航入口、待处理事项和常用功能。用户可先从这里判断当前需要进入哪个模块。",
        "steps": ["打开软件并进入首页或工作台。", "查看页面中的导航、列表、提示信息和常用入口。", "选择需要办理或查看的事项。", "点击对应入口进入后续功能页面。"],
        "result": "完成该操作后，用户会进入所选功能，并继续查看、填写或处理具体业务内容。",
    },
    "query": {
        "usage": "用户进入页面后，可以通过列表、筛选条件或搜索框查找目标信息。页面会把符合条件的内容展示出来，便于继续查看详情或进行后续处理。",
        "steps": ["进入对应查询或列表页面。", "输入关键词，或选择时间、分类、状态等筛选条件。", "查看页面返回的列表或详情内容。", "选择需要继续处理的数据，进入详情、编辑或确认页面。"],
        "result": "完成该操作后，用户可以定位到目标数据，并根据页面提供的入口继续查看或办理。",
    },
    "form": {
        "usage": "用户根据页面中的输入框、选择项和提示内容填写信息。提交前可检查内容是否完整，提交后软件会保存或返回处理结果。",
        "steps": ["进入新增、编辑或填报页面。", "按照页面要求填写名称、说明、分类、时间或其他业务信息。", "检查必填项和页面提示，确认内容无误后提交。", "查看保存结果，根据需要继续修改或返回列表。"],
        "result": "完成该操作后，页面会显示保存状态，相关信息会进入后续查询、处理或管理流程。",
    },
    "workflow": {
        "usage": "该功能用于让用户了解事项当前处于哪个阶段，并在需要时进行确认、修改、提交或继续处理。页面通常会显示状态、进度和下一步入口。",
        "steps": ["进入对应事项或任务页面。", "查看当前状态、已完成内容和待处理事项。", "根据页面提示进行确认、修改、提交或继续处理。", "处理完成后查看状态变化和页面反馈。"],
        "result": "完成该操作后，事项状态会更新，用户可以继续办理下一步，或返回列表查看整体进展。",
    },
    "resource": {
        "usage": "该功能用于集中管理业务资料。用户可以查看已有资料，上传或选择需要使用的内容，也可以把处理结果保存下来供后续复用。",
        "steps": ["进入资料、文件或资源管理页面。", "查看已有资料列表，或选择上传、导入、下载等操作。", "选择需要查看、使用或维护的资料。", "保存处理结果，并返回当前业务页面继续使用。"],
        "result": "完成该操作后，相关资料会被集中保存，用户后续可以继续查找、复用或维护。",
    },
    "report": {
        "usage": "用户可通过该功能查看汇总结果、统计信息或分析内容。页面一般以列表、数字、图形或说明文字展示处理情况。",
        "steps": ["进入统计、报表或分析页面。", "选择需要查看的时间范围、对象或分类。", "查看页面展示的统计结果和说明内容。", "根据需要导出、保存或返回其他页面继续处理。"],
        "result": "完成该操作后，用户可以了解业务数据或处理结果的整体情况，并据此进行后续管理。",
    },
    "settings": {
        "usage": "该功能用于维护软件运行时需要的基础信息。用户可按照管理要求调整配置项，并通过保存操作让设置生效。",
        "steps": ["进入设置、配置或管理页面。", "查看当前参数、角色、权限或基础资料。", "根据实际需要修改配置内容。", "保存设置并查看页面反馈。"],
        "result": "完成该操作后，相关配置会按用户保存的内容生效，后续页面会按新的设置继续运行。",
    },
    "creation": {
        "usage": "用户在该功能中输入要求、选择资料或指定条件，软件根据输入内容生成或整理结果。用户可查看结果，并决定保存、修改或重新处理。",
        "steps": ["进入生成、创作或内容处理页面。", "输入处理要求，或选择需要作为依据的资料。", "提交处理请求，并等待页面显示结果。", "检查结果是否符合预期，选择保存、修改或重新处理。"],
        "result": "完成该操作后，软件会展示生成或整理后的内容，用户可以继续用于后续业务环节。",
    },
    "general": {
        "usage": "用户进入页面后，先查看当前信息，再根据页面提供的按钮、输入框或列表完成操作。处理完成后，软件会返回结果或提示。",
        "steps": ["进入对应功能页面。", "查看页面展示的信息和可操作入口。", "按照业务需要填写、选择、提交或确认。", "查看页面反馈，并决定继续处理或返回上一页面。"],
        "result": "完成该操作后，页面会展示当前处理结果，相关信息也会按业务要求保留。",
    },
}


def module_blueprint(feature: str, detail: str) -> dict[str, Any]:
    return CATEGORY_BLUEPRINTS[module_category(feature, detail)]


def build_module(feature: str, raw_feature: str, detail: str) -> dict[str, Any]:
    detail = normalize_detail(feature, detail)
    blueprint = module_blueprint(feature, detail)
    purpose = f"{feature}主要用于{detail}"
    usage = blueprint["usage"].format(feature=feature)
    return {
        "feature": feature,
        "raw_feature": raw_feature,
        "purpose": purpose,
        "usage": usage,
        "steps": list(blueprint["steps"]),
        "result": blueprint["result"].format(feature=feature),
        "screenshot": f"【截图预留：请在此处插入“{feature}”页面或操作结果截图。】",
    }


TECHNICAL_TERMS = [
    "技术实现",
    "代码",
    "框架",
    "接口封装",
    "状态管理",
    "异步任务",
    "任务队列",
    "数据持久化",
    "业务逻辑",
    "React",
    "Next.js",
    "FastAPI",
    "LangGraph",
    "Celery",
]

TEMPLATE_MARKERS = [
    "重要功能之一",
    "通过清晰的页面入口、信息展示和结果反馈",
    "对应操作环节",
    "审核时可重点查看",
    "按照页面提示填写内容、选择资料、确认方案或点击提交按钮",
    "系统处理完成后显示结果或提示信息",
    "帮助用户用户",
    "帮助用户系统",
    "主要用于在",
    "项目管理或资产中心项目管理",
]

AI_TONE_MARKERS = [
    "旨在",
    "赋能",
    "一站式",
    "智能化",
    "高效便捷",
    "显著提升",
    "强大能力",
    "丰富功能",
    "极大地",
    "全方位",
    "多维度",
    "闭环",
    "降本增效",
    "优化体验",
    "提升效率",
]


def manual_quality_issues(text: str, module_count: int) -> list[str]:
    issues: list[str] = []
    for term in TECHNICAL_TERMS:
        if term in text:
            issues.append(f"存在偏技术表达：{term}")
    for marker in TEMPLATE_MARKERS:
        if marker in text:
            issues.append(f"存在模板化表达：{marker}")
    for marker in AI_TONE_MARKERS:
        if marker in text:
            issues.append(f"存在疑似 AI 味/空泛表达：{marker}")
    if text.count("【截图预留：") < module_count:
        issues.append("截图预留数量少于核心模块数量")
    sections = re.split(r"^###\s+\d+\.\s+", text, flags=re.M)[1:]
    for section in sections:
        title = section.splitlines()[0].strip() if section.splitlines() else "未命名模块"
        body = "\n".join(section.splitlines()[1:])
        if len(body) < 360:
            issues.append(f"模块内容偏薄：{title}")
        if body.count("操作步骤：") != 1:
            issues.append(f"模块操作步骤结构异常：{title}")
    step_lines = [line.strip() for line in text.splitlines() if re.match(r"^\d+\.\s+", line.strip())]
    for line in sorted({line for line in step_lines if step_lines.count(line) > 2}):
        issues.append(f"操作步骤重复过多：{line[:40]}")
    return issues


def make_unique_steps(modules: list[dict[str, Any]]) -> None:
    seen: dict[str, int] = {}
    for module in modules:
        adjusted = []
        for step in module["steps"]:
            count = seen.get(step, 0)
            seen[step] = count + 1
            if count and "页面" in step:
                adjusted.append(step.replace("页面", f"{module['feature']}页面", 1) if count >= 2 else step)
            elif count:
                adjusted.append(f"{module['feature']}：{step}" if count >= 2 else step)
            else:
                adjusted.append(step)
        module["steps"] = adjusted


def expand_modules(modules: list[dict[str, Any]], operation_flow: list[str]) -> None:
    bridge_templates = [
        "这一页可接续“{prev}”形成的内容，继续办理当前业务事项。",
        "在流程上，它会沿用“{prev}”中已经确认的信息，帮助用户进入下一步处理。",
        "用户通常会在完成“{prev}”后进入本环节，并继续查看新的处理结果。",
        "本环节会承接“{prev}”留下的资料，使前后操作保持连贯。",
    ]
    next_templates = [
        "确认后，用户可转入“{next}”继续处理。",
        "该结果确认后，后续可进入“{next}”继续完善。",
        "用户完成检查后，可以打开“{next}”推进后续工作。",
        "保存当前结果后，软件会支持用户继续前往“{next}”。",
    ]
    for index, module in enumerate(modules):
        if index == 0:
            module["usage"] += " 这一步通常是用户进入具体业务的起点，后续页面会围绕当前选择或填写的信息继续展开。"
        elif index == 1:
            module["usage"] += " 它通常承接前一环节的信息，帮助用户把事项推进到更具体的处理页面。"
        elif index == 2:
            module["usage"] += " 这一环节会把前面已经确认的内容进一步细化，便于审核人员理解软件的实际使用路径。"
        if index and modules[index - 1]["feature"] != module["feature"]:
            template = bridge_templates[(index - 1) % len(bridge_templates)]
            module["purpose"] += template.format(prev=modules[index - 1]["feature"])
        if index + 1 < len(modules):
            template = next_templates[index % len(next_templates)]
            module["result"] += template.format(next=modules[index + 1]["feature"])


def rewrite_module_intro(module: dict[str, Any]) -> None:
    feature = module["feature"]
    prefix = f"{feature}主要用于"
    if not module["purpose"].startswith(prefix):
        return
    rest = module["purpose"][len(prefix) :]
    category = module_category(feature, module["purpose"])
    intros = {
        "auth": f"用户使用{feature}时，可以",
        "entry": f"进入{feature}后，用户可以",
        "query": f"在{feature}中，用户可以",
        "form": f"用户通过{feature}可以",
        "workflow": f"在{feature}环节，用户可以",
        "resource": f"通过{feature}，用户可以",
        "report": f"在{feature}中，用户可以",
        "settings": f"通过{feature}，用户可以",
        "creation": f"使用{feature}时，用户可以",
        "general": f"在{feature}中，用户可以",
    }
    module["purpose"] = f"{intros.get(category, intros['general'])}{rest}"


def repair_remaining_issues(modules: list[dict[str, Any]], issues: list[str]) -> None:
    for module in modules:
        if any(module["feature"] in issue and "偏薄" in issue for issue in issues):
            module["usage"] += " 页面中的文字、列表或卡片应围绕该模块的核心事项展开，使审核人员能够看到用户从进入页面到获得结果的完整路径。"
            module["result"] += " 若用户需要继续修改，软件会保留当前项目内容，便于返回前序环节重新调整。"
        module["purpose"] = plain_manual_text(module["purpose"])
        module["usage"] = plain_manual_text(module["usage"])
        module["result"] = plain_manual_text(module["result"])
        module["purpose"] = module["purpose"].replace("主要用于在", "主要用于")
    make_unique_steps(modules)


def de_template_modules(modules: list[dict[str, Any]]) -> None:
    for module in modules:
        rewrite_module_intro(module)
        module["purpose"] = module["purpose"].replace("从项目实际功能看，用户", "从项目实际功能看，用户")
        module["purpose"] = module["purpose"].replace("从项目实际功能看，系统", "从项目实际功能看，软件")
        module["usage"] = module["usage"].replace("用户可以", "用户可")
        module["result"] = module["result"].replace("操作完成后，", "完成该环节后，")
    make_unique_steps(modules)


def clean_field(value: str, default: str) -> str:
    text = plain_manual_text(str(value or "")).strip()
    if not text or text == "待用户确认":
        return default
    return text + ("。" if not text.endswith(("。", "！", "？")) else "")


def feature_phrase(modules: list[dict[str, Any]], limit: int = 5) -> str:
    names = [module["feature"] for module in modules if module.get("feature")]
    return "、".join(names[:limit]) if names else "主要业务处理"


def render_manual(
    software_name: str,
    version: str,
    industry: str,
    users: list[str],
    positioning: str,
    core_value: str,
    modules: list[dict[str, Any]],
    operation_flow: list[str],
    manual_sections: list[Any] | None = None,
) -> str:
    industry_text = "相关业务" if not industry or industry == "待用户确认" else industry
    user_text = join_items([user for user in users if user != "待用户确认"]) or "实际使用人员"
    positioning_text = clean_field(positioning, f"{software_name}是一款根据项目资料整理的软件系统。")
    core_value_text = clean_field(core_value, "提升业务办理效率，统一管理相关信息，并降低重复操作成本。")
    functions_text = feature_phrase(modules)
    flow = operation_flow or [
        "打开软件访问地址，进入系统首页。",
        "根据业务需要选择对应功能模块。",
        "在功能页面中查看、录入或维护相关数据。",
        "提交操作后，根据系统反馈确认处理结果。",
        "完成操作后返回首页或切换至其他模块。",
    ]
    if manual_sections:
        lines = [f"# {software_name}", ""]
        modules_rendered = False
        flow_rendered = False
        for index, section in enumerate(manual_sections, start=1):
            if isinstance(section, dict):
                title = str(section.get("title") or f"章节 {index}").strip()
                paragraphs = [plain_manual_text(str(item)).strip() for item in section.get("paragraphs") or [] if str(item).strip()]
                include_overview = bool(section.get("include_feature_overview"))
                include_modules = bool(section.get("include_operation_modules"))
                include_flow = bool(section.get("include_operation_flow"))
            else:
                title = str(section).strip() or f"章节 {index}"
                paragraphs = []
                include_overview = include_modules = include_flow = False
            lines.extend([f"## {title}", ""])
            if paragraphs:
                for paragraph in paragraphs:
                    lines.extend([paragraph, ""])
            elif index == 1:
                lines.extend(
                    [
                        f"{software_name} {version}是一款面向{industry_text}场景的软件系统。{positioning_text}",
                        "",
                        f"软件围绕{functions_text}等功能组织页面，为{user_text}提供操作入口和结果反馈。",
                        "",
                    ]
                )
            if include_overview:
                for i, module in enumerate(modules[:8], start=1):
                    lines.extend([f"{i}. {module['feature']}：{feature_summary(module['feature'], module['purpose'], software_name)}", ""])
            if include_modules:
                append_modules(lines, modules)
                modules_rendered = True
            if include_flow:
                append_flow(lines, software_name, flow)
                flow_rendered = True
        if not modules_rendered:
            lines.extend(["## 功能操作说明", ""])
            append_modules(lines, modules)
        if not flow_rendered:
            append_flow(lines, software_name, flow)
        append_stop(lines)
        return "\n".join(lines)
    lines = [
        f"# {software_name}",
        "",
        "## 一、软件概述",
        "",
        f"{software_name} {version}是一款面向{industry_text}场景的软件系统。{positioning_text}",
        "",
        f"软件围绕{functions_text}等功能组织页面，为{user_text}提供清晰的操作入口和结果反馈。用户进入系统后，可以按照页面提示完成查看、填写、处理、确认或维护等操作。",
        "",
        f"本软件的核心价值在于{core_value_text}",
        "",
        "本操作手册面向软件著作权审核场景，重点说明软件用途、功能入口、操作方式和处理结果，尽量使用普通读者能够理解的语言。",
        "",
        "## 二、适用对象与运行环境",
        "",
        f"本软件适用于{user_text}在{industry_text}场景下开展日常业务处理。不同使用单位可以根据实际管理要求，为相关人员配置访问入口、使用权限和运行环境。",
        "",
        "| 项目 | 最低要求 | 推荐要求 |",
        "| --- | --- | --- |",
        "| 操作系统 | Windows 10、macOS 或 Linux | Windows 10/11、macOS 或 Linux |",
        "| 浏览器 | Chrome、Edge、Safari 等现代浏览器 | Chrome 或 Edge 最新稳定版 |",
        "| 网络连接 | 可访问系统服务地址 | 稳定的局域网或互联网连接 |",
        "| 显示器分辨率 | 1280x768 | 1920x1080 |",
        "",
        f"以上环境用于保证{software_name}能够正常打开页面、提交操作和展示结果。若部署方式或运行环境与实际项目不同，应在申请表信息中按实际情况填写。",
        "",
        "## 三、进入软件",
        "",
        f"用户打开{software_name}访问地址后，系统会展示登录页、首页或主工作界面。若软件启用了账号认证，用户需要按照页面要求输入账号、密码、验证码或其他身份信息；验证通过后进入可使用页面，验证失败时按照页面提示重新填写。",
        "",
        "若当前项目没有独立登录模块，用户可直接进入首页或主要业务页面。首页通常用于展示导航、功能入口、待处理事项或常用操作，帮助用户快速进入下一步业务。",
        "",
        "## 四、主要功能概览",
        "",
        f"{software_name}的功能概览根据项目资料和页面入口整理。各功能之间可以独立使用，也可以按照实际业务流程连续使用。",
        "",
    ]
    for i, module in enumerate(modules[:5], start=1):
        lines.extend([f"{i}. {module['feature']}：{feature_summary(module['feature'], module['purpose'], software_name)}", ""])
    lines.extend(
        [
            "",
            "## 五、功能操作说明",
            "",
        ]
    )
    for i, module in enumerate(modules, start=1):
        lines.extend(
            [
                f"### {i}. {module['feature']}",
                "",
                module["purpose"],
                "",
                module["usage"],
                "",
                "操作步骤：",
                "",
                *[f"{step_no}. {step}" for step_no, step in enumerate(module["steps"], start=1)],
                "",
                module["result"],
                "",
                module["screenshot"],
                "",
            ]
        )
    lines.extend(
        [
            "## 六、典型使用流程",
            "",
            f"{software_name}的典型使用流程会根据项目功能和业务资料整理。审核人员可通过该流程理解用户从进入系统到完成事项的大致顺序。",
            "",
            *[f"{i}. {plain_manual_text(item)}" for i, item in enumerate(flow, start=1)],
            "",
            "## 七、使用注意事项",
            "",
            "使用软件时应保证运行环境、浏览器版本和网络连接正常。若页面数据加载失败，可检查服务地址、网络状态或重新刷新页面；若任务处理时间较长，应等待系统返回处理状态，避免重复提交相同任务。",
            "",
            "生成草稿时应先检查章节是否完整、说明是否通顺、截图预留位置是否清楚；若某一模块与实际软件功能不一致，应在 Markdown 草稿整体确认前统一修订。",
            "",
        ]
    )
    append_stop(lines)
    return "\n".join(lines)


def append_modules(lines: list[str], modules: list[dict[str, Any]]) -> None:
    for i, module in enumerate(modules, start=1):
        lines.extend(
            [
                f"### {i}. {module['feature']}",
                "",
                module["purpose"],
                "",
                module["usage"],
                "",
                "操作步骤：",
                "",
                *[f"{step_no}. {step}" for step_no, step in enumerate(module["steps"], start=1)],
                "",
                module["result"],
                "",
                module["screenshot"],
                "",
            ]
        )


def append_flow(lines: list[str], software_name: str, flow: list[str]) -> None:
    lines.extend(
        [
            "## 典型使用流程",
            "",
            f"{software_name}的典型使用流程按照项目业务资料整理，审核人员可通过该流程理解主要功能之间的衔接关系。",
            "",
            *[f"{i}. {plain_manual_text(item)}" for i, item in enumerate(flow, start=1)],
            "",
        ]
    )


def append_stop(lines: list[str]) -> None:
    lines.extend(
        [
            "```text",
            "STOP_FOR_USER",
            "NEXT_ACTION: 请一次性确认完整操作手册草稿是否符合真实业务；必要时先统一修改段落内容，再运行 confirm_stage.py --stage markdown。",
            "```",
            "",
        ]
    )


def build_manual_text(
    analysis: dict[str, Any],
    software_name: str,
    version: str,
    business: dict[str, Any] | None = None,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    features = (business.get("business_features") if business else None) or feature_list(analysis)
    feature_details = (business.get("business_feature_details") if business else {}) or {}
    feature_pairs = [(plain_feature_name(feature), feature) for feature in features]
    positioning = plain_manual_text(business.get("product_positioning") if business else f"{software_name} {version}是一款基于项目实际功能整理的软件系统。")
    core_value = plain_manual_text(business.get("core_value") if business else "系统通过清晰的软件界面为用户提供主要业务入口，支持用户完成信息查看、业务处理、数据维护和结果反馈等操作。")
    users = business.get("target_users") if business else ["业务用户"]
    operation_flow = business.get("operation_flow") if business else []
    manual_sections = business.get("manual_sections") if business else []
    industry = business.get("industry") if business else "业务应用"
    if positioning.rstrip("。") == software_name.rstrip("。"):
        positioning = "软件围绕项目资料中体现的业务场景提供操作能力。"
    elif not positioning.endswith("。"):
        positioning += "。"
    modules = [
        build_module(feature, raw_feature, feature_details.get(raw_feature) or f"{feature}模块用于处理{feature}相关业务。")
        for feature, raw_feature in feature_pairs
    ]
    records: list[dict[str, Any]] = []

    text = render_manual(software_name, version, industry, users, positioning, core_value, modules, operation_flow, manual_sections)
    records.append({"round": 1, "action": "初稿生成", "issues": manual_quality_issues(text, len(modules))})

    expand_modules(modules, operation_flow)
    text = render_manual(software_name, version, industry, users, positioning, core_value, modules, operation_flow, manual_sections)
    records.append({"round": 2, "action": "按项目流程扩写模块说明", "issues": manual_quality_issues(text, len(modules))})

    de_template_modules(modules)
    text = render_manual(software_name, version, industry, users, positioning, core_value, modules, operation_flow, manual_sections)
    records.append({"round": 3, "action": "去除制式表达和 AI 味，并复核截图预留", "issues": manual_quality_issues(text, len(modules))})

    for round_no in range(4, 7):
        issues = records[-1]["issues"]
        if not issues:
            break
        repair_remaining_issues(modules, issues)
        text = render_manual(software_name, version, industry, users, positioning, core_value, modules, operation_flow, manual_sections)
        records.append(
            {
                "round": round_no,
                "action": "根据自检问题继续补写和修正",
                "issues": manual_quality_issues(text, len(modules)),
            }
        )
    return text, records, modules


def write_review_records(out_dir: Path, records: list[dict[str, Any]], modules: list[dict[str, Any]]) -> None:
    (out_dir / "操作手册自检记录.json").write_text(
        json.dumps({"rounds": records, "module_count": len(modules)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = ["# 操作手册自检记录", ""]
    for record in records:
        lines.extend([f"## 第 {record['round']} 轮：{record['action']}", ""])
        if record["issues"]:
            lines.extend(f"- {issue}" for issue in record["issues"])
        else:
            lines.append("- 未发现需继续修正的问题")
        lines.append("")
    lines.extend(["## 模块清单", ""])
    lines.extend(f"- {module['feature']}" for module in modules)
    (out_dir / "操作手册自检记录.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manual(path: Path, analysis: dict[str, Any], software_name: str, version: str, business: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    text, records, modules = build_manual_text(analysis, software_name, version, business)
    path.write_text(text, encoding="utf-8")
    write_review_records(path.parent, records, modules)
    return records


def require_confirmed_business(business: dict[str, Any] | None) -> None:
    if business is None:
        raise SystemExit(
            "STOP_FOR_USER\n"
            "NEXT_ACTION: 操作手册必须基于已确认的业务理解生成。请先生成并确认 草稿/业务理解.md。"
        )
    if business.get("confirmation_required") and not business.get("user_confirmed"):
        raise SystemExit(
            "STOP_FOR_USER\n"
            "NEXT_ACTION: 业务理解尚未确认。请先确认 草稿/业务理解.md，"
            "再运行 `python3 scripts/confirm_stage.py --workdir 软件著作权申请资料 --stage business --note \"<用户确认内容>\"`。"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--software-name", required=True)
    parser.add_argument("--version", default="V1.0")
    parser.add_argument("--business-context", help="Business context JSON generated before manual drafting")
    parser.add_argument("--out-dir", default="软件著作权申请资料/草稿")
    args = parser.parse_args()

    analysis = read_json(Path(args.analysis))
    business = read_json(Path(args.business_context)) if args.business_context else None
    require_confirmed_business(business)
    out_dir = ensure_dir(Path(args.out_dir))
    out_path = out_dir / "操作手册.md"
    records = write_manual(out_path, analysis, args.software_name, args.version, business)
    print(f"OK manual draft: {out_path}")
    print(f"OK manual self-review: {out_dir / '操作手册自检记录.md'}")
    for record in records:
        print(f"Review round {record['round']}: {record['action']} issues={len(record['issues'])}")
    print("STOP_FOR_USER")
    print("NEXT_ACTION: 请一次性确认完整操作手册草稿是否符合真实业务；必要时先统一修改段落内容，再运行 confirm_stage.py --stage markdown。")


if __name__ == "__main__":
    main()
