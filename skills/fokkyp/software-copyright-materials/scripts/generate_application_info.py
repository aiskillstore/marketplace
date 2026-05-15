#!/usr/bin/env python3
"""Generate the Markdown draft for application form information."""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
from pathlib import Path
from typing import Any

from common import ensure_dir, read_json, read_text


FIELD_ORDER = [
    "软件全称",
    "版本号",
    "著作权人",
    "开发完成日期",
    "首次发表日期",
    "开发的硬件环境",
    "运行的硬件环境",
    "开发该软件的操作系统",
    "软件开发环境 / 开发工具",
    "该软件的运行平台 / 操作系统",
    "软件运行支撑环境 / 支持软件",
    "编程语言",
    "源程序量",
    "开发目的",
    "面向领域 / 行业",
    "软件的主要功能",
    "技术特点",
    "软件的技术特点选项",
    "页数",
    "软件分类",
]


def summarize_features(analysis: dict[str, Any], software_name: str) -> str:
    features = analysis.get("feature_candidates") or []
    if features:
        readable_features = []
        for feature in features:
            name = humanize_feature(str(feature))
            if name and name not in readable_features:
                readable_features.append(name)
        readable = "、".join(readable_features[:10])
        return f"{software_name}提供{readable}等功能，支持用户通过前端界面完成核心业务操作、信息查看、数据维护和流程处理。"
    readme = (analysis.get("readme_excerpt") or "").strip()
    if readme:
        first = readme.splitlines()[0][:120]
        return f"{software_name}围绕{first}提供信息展示、业务操作和数据管理等功能。"
    return f"{software_name}提供信息展示、业务处理、数据管理和系统配置等功能。"


def humanize_feature(name: str) -> str:
    value = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    value = value.replace("-", " ").replace("_", " ").strip()
    key = value.lower().replace(" ", "")
    mapping = {
        "login": "软件登录",
        "register": "用户注册",
        "auth": "用户认证",
        "home": "首页",
        "dashboard": "数据看板",
        "project": "项目管理",
        "projects": "项目管理",
        "projectsettings": "项目设置",
        "projectssettings": "项目设置",
        "settings": "系统设置",
        "asset": "资源管理",
        "assets": "资源管理",
        "assethub": "资源中心",
        "billing": "费用管理",
        "agentstatusbar": "智能体状态展示",
        "messagebubble": "消息展示",
        "chatpanel": "对话面板",
        "chatinput": "对话输入",
        "assetpanel": "资源面板",
    }
    return mapping.get(key, value.title() if re.search(r"[A-Za-z]", value) else value)


def build_fields(
    analysis: dict[str, Any],
    manifest: dict[str, Any],
    software_name: str,
    version: str,
    answers: dict[str, str],
    business: dict[str, Any] | None = None,
) -> dict[str, str]:
    frameworks = analysis.get("frameworks") or []
    framework_text = "、".join(frameworks) if frameworks else "前端工程化框架"
    language = analysis.get("language") or "待用户确认"
    project = Path(analysis.get("project_root") or ".")
    hardware_hint = current_hardware_environment()
    dev_os_hint = current_operating_system()
    version_hint = version_confirmation_hint(analysis, version)
    software_name_hint = f"待用户确认（建议：{software_name}；请确认最终申报的软件全称）"

    defaults = {
        "软件全称": software_name_hint,
        "版本号": version_hint,
        "著作权人": "待用户确认",
        "开发完成日期": "待用户确认",
        "首次发表日期": "待用户确认",
        "开发的硬件环境": hardware_hint,
        "运行的硬件环境": hardware_hint,
        "开发该软件的操作系统": dev_os_hint,
        "软件开发环境 / 开发工具": infer_ide_name(project),
        "该软件的运行平台 / 操作系统": infer_runtime_os(analysis),
        "软件运行支撑环境 / 支持软件": infer_runtime_support(analysis, project),
        "编程语言": language,
        "源程序量": str(analysis.get("source", {}).get("line_count") or manifest.get("selected_source_line_count") or "待用户确认"),
        "开发目的": business.get("application_purpose") if business else f"建设{software_name}，为用户提供稳定、便捷的信息化操作能力，提升相关业务处理效率。",
        "面向领域 / 行业": business.get("industry") if business else "待用户确认",
        "软件的主要功能": business.get("main_functions") if business else summarize_features(analysis, software_name),
        "技术特点": business.get("technical_characteristics") if business else f"系统采用{framework_text}构建前端界面，结合模块化组件、路由组织、接口封装和状态管理实现业务功能，具备较好的可维护性和扩展性。",
        "软件的技术特点选项": business.get("software_technical_option") if business else "应用软件",
        "页数": str(manifest.get("total_pages") or "待用户确认"),
        "软件分类": business.get("software_category") if business else "应用软件",
    }
    defaults.update({k: v for k, v in answers.items() if v})
    return defaults


def version_numbers(value: str) -> tuple[int, ...]:
    raw = str(value or "").strip()
    raw = raw.lstrip("vV")
    parts = re.findall(r"\d+", raw)
    return tuple(int(part) for part in parts[:3])


def version_less_than_1(value: str) -> bool:
    numbers = version_numbers(value)
    return bool(numbers) and numbers[0] < 1


def normalize_version_label(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    return raw if raw.upper().startswith("V") else f"V{raw}"


def project_version_candidate(analysis: dict[str, Any]) -> str:
    value = str((analysis.get("package") or {}).get("version") or "").strip()
    if value and value.upper() != "V1.0":
        return normalize_version_label(value)
    return ""


def version_confirmation_hint(analysis: dict[str, Any], requested_version: str) -> str:
    project_version = project_version_candidate(analysis)
    requested = normalize_version_label(requested_version or "V1.0")
    if project_version and version_less_than_1(project_version):
        return (
            f"待用户确认（项目版本号为 {project_version}，软著首次提交通常建议从 V1.0 开始；"
            f"请确认填写 V1.0 还是 {project_version}）"
        )
    if not project_version and version_less_than_1(requested):
        return (
            f"待用户确认（当前建议版本号为 {requested}，软著首次提交通常建议从 V1.0 开始；"
            f"请确认填写 V1.0 还是 {requested}）"
        )
    if project_version and project_version != requested:
        return f"待用户确认（项目版本号为 {project_version}，当前建议为 {requested}；请确认最终申报版本号）"
    return f"待用户确认（建议：{requested}；请确认最终申报版本号）"


def format_gb(size: int | None) -> str:
    if not size:
        return ""
    return f"{size / (1024 ** 3):.0f}GB"


def total_memory_bytes() -> int | None:
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        return None


def current_hardware_environment() -> str:
    parts: list[str] = []
    cpu_count = os.cpu_count()
    machine = platform.machine()
    processor = platform.processor()
    if processor and processor != machine and processor.lower() != "arm":
        parts.append(f"CPU {processor}")
    if cpu_count:
        parts.append(f"CPU {cpu_count}核")
    if machine:
        parts.append(f"架构 {machine}")
    memory = format_gb(total_memory_bytes())
    if memory:
        parts.append(f"内存 {memory}")
    try:
        disk = shutil.disk_usage(Path.home())
        disk_total = format_gb(disk.total)
        if disk_total:
            parts.append(f"硬盘 {disk_total}")
    except OSError:
        pass
    if parts:
        return "建议：" + "、".join(parts) + "（可按实际开发/运行设备调整）"
    return "待用户确认（建议填写 CPU、内存、硬盘容量等硬件配置）"


def current_operating_system() -> str:
    system = platform.system()
    if system == "Darwin":
        version = platform.mac_ver()[0]
        label = f"macOS {version}" if version else f"macOS（Darwin {platform.release()}）"
    elif system == "Windows":
        label = f"Windows {platform.release()}"
    elif system == "Linux":
        label = f"Linux {platform.release()}"
    else:
        label = f"{system} {platform.release()}".strip() or "待用户确认"
    return f"建议：{label}（请按实际开发操作系统版本确认）"


def infer_ide_name(project: Path) -> str:
    if (project / ".idea").exists():
        return "建议：WebStorm 或 IntelliJ IDEA（项目存在 .idea 配置，请按实际使用 IDE 确认）"
    if (project / ".vscode").exists():
        return "建议：Visual Studio Code（项目存在 .vscode 配置，请按实际使用 IDE 确认）"
    if list(project.glob("*.code-workspace")):
        return "建议：Visual Studio Code（项目存在工作区配置，请按实际使用 IDE 确认）"
    return "建议：Visual Studio Code（可按实际改为 WebStorm、IntelliJ IDEA、Cursor 等 IDE）"


def infer_runtime_os(analysis: dict[str, Any]) -> str:
    frameworks = set(analysis.get("frameworks") or [])
    deps = set((analysis.get("package") or {}).get("dependency_names") or [])
    if "Electron" in frameworks or "electron" in deps or "Tauri" in frameworks or "@tauri-apps/api" in deps:
        return "建议：Windows 10/11 或 macOS 13及以上版本（请按实际桌面端运行环境确认）"
    if frameworks & {"Vue", "React", "Vite", "Next.js", "Nuxt", "Svelte", "Astro", "Angular"}:
        return "建议：Windows 10/11 或 macOS 13及以上版本（请按实际客户端操作系统确认）"
    return "建议：Windows 10/11 或 macOS 13及以上版本（请按实际运行操作系统版本确认）"


def project_file(project: Path, relative: str) -> Path | None:
    if not relative:
        return None
    path = project / relative
    return path if path.exists() else None


def load_project_package(project: Path, analysis: dict[str, Any]) -> dict[str, Any]:
    package_path = project_file(project, (analysis.get("package") or {}).get("path") or "")
    if package_path:
        try:
            return read_json(package_path)
        except Exception:
            return {}
    return {}


def read_readme(project: Path) -> str:
    for name in ("README.md", "README.zh.md", "readme.md", "Readme.md"):
        path = project / name
        if path.exists():
            try:
                return read_text(path, limit=12000)
            except Exception:
                return ""
    return ""


def extract_requirement_bullets(text: str) -> list[str]:
    wanted = ("python", "node", "docker", "compose", "postgres", "redis", "chrome", "edge", "safari")
    bullets: list[str] = []
    for line in text.splitlines():
        match = re.match(r"\s*[-*]\s+(.+)", line)
        if not match:
            continue
        item = match.group(1).strip()
        if any(key in item.lower() for key in wanted) and item not in bullets:
            bullets.append(item)
    return bullets[:8]


def detect_package_manager(project: Path, package_path: str) -> str:
    base = (project / package_path).parent if package_path else project
    checks = [
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "Yarn"),
        ("bun.lock", "Bun"),
        ("bun.lockb", "Bun"),
        ("package-lock.json", "npm"),
    ]
    for filename, manager in checks:
        if (base / filename).exists() or (project / filename).exists():
            return manager
    return "npm"


def has_support_term(items: list[str], term: str) -> bool:
    return any(term.lower() in item.lower() for item in items)


def infer_runtime_support(analysis: dict[str, Any], project: Path) -> str:
    package_info = load_project_package(project, analysis)
    package_path = (analysis.get("package") or {}).get("path") or ""
    deps = set((analysis.get("package") or {}).get("dependency_names") or [])
    frameworks = set(analysis.get("frameworks") or [])
    support: list[str] = []
    readme_requirements = extract_requirement_bullets(read_readme(project))
    if readme_requirements:
        support.extend(readme_requirements)
    if package_info or deps or frameworks & {"Vue", "React", "Vite", "Next.js", "Nuxt", "Svelte", "Astro", "Angular"}:
        if not has_support_term(support, "node"):
            node_engine = str((package_info.get("engines") or {}).get("node") or "").strip()
            support.append(f"Node.js {node_engine}" if node_engine else "Node.js（按项目 package.json 要求确认版本）")
        support.append(detect_package_manager(project, package_path))
        support.append("Chrome、Edge 或 Safari 等现代浏览器")
    if ((project / "pyproject.toml").exists() or any(project.glob("*/pyproject.toml"))) and not has_support_term(support, "python"):
        support.append("Python（按项目 pyproject.toml 要求确认版本）")
    if ((project / "requirements.txt").exists() or list(project.glob("*/requirements*.txt"))) and not has_support_term(support, "python"):
        support.append("Python 依赖环境")
    if ((project / "docker-compose.yml").exists() or (project / "docker-compose.yaml").exists() or list(project.glob("docker-compose*.yml"))) and not has_support_term(support, "docker"):
        support.append("Docker、Docker Compose")
    compose_text = ""
    for compose in list(project.glob("docker-compose*.yml")) + list(project.glob("docker-compose*.yaml")):
        try:
            compose_text += "\n" + read_text(compose, limit=20000).lower()
        except Exception:
            continue
    if "postgres" in compose_text:
        support.append("PostgreSQL")
    if "redis" in compose_text:
        support.append("Redis")
    unique: list[str] = []
    for item in support:
        clean = str(item).strip().rstrip("；;")
        if clean and clean not in unique:
            unique.append(clean)
    if unique:
        return "建议：" + "、".join(unique) + "（请按实际部署环境确认）"
    return "待用户确认（建议填写项目所需运行时、浏览器、数据库、中间件和外部服务）"


def write_application_md(path: Path, fields: dict[str, str], analysis: dict[str, Any], manifest: dict[str, Any], business: dict[str, Any] | None = None) -> None:
    lines = ["# 申请表信息", ""]
    for field in FIELD_ORDER:
        lines.append(f"➤{field}：{fields.get(field, '待用户确认')}")
    pending = [field for field in FIELD_ORDER if "待用户确认" in fields.get(field, "")]
    lines.extend(
        [
            "",
            "## 环境字段填写口径",
            "",
            "- 软件全称：必须由用户确认；最终正式资料文件名、代码页眉和操作手册中的软件名称均以本字段为准。",
            "- 软件开发环境 / 开发工具：填写 IDE 或编辑器名称，例如 Visual Studio Code、WebStorm、IntelliJ IDEA、Cursor。",
            "- 版本号：必须由用户确认；如果项目版本小于 V1.0，软著首次提交通常建议使用 V1.0，也可按实际项目版本填写，最终以前面“版本号”字段为准。",
            "- 开发该软件的操作系统：填写实际开发电脑的操作系统版本，例如 macOS 14、macOS 15、Windows 10、Windows 11。",
            "- 该软件的运行平台 / 操作系统：填写软件客户端或服务运行所在的操作系统版本，例如 Windows 10/11 或 macOS 13及以上版本。",
            "- 软件运行支撑环境 / 支持软件：填写项目运行所需的软件环境，例如 Node.js、Python、Docker、数据库、浏览器、中间件或外部服务。",
            "- 开发的硬件环境和运行的硬件环境：可使用当前检测到的电脑配置作为建议值，也可按实际开发、部署或审核口径调整。",
            "",
            "## 项目分析摘要",
            "",
            f"- 项目目录：{analysis.get('project_root', '')}",
            f"- 框架：{'、'.join(analysis.get('frameworks') or []) or '未识别'}",
            f"- 源码文件数：{analysis.get('source', {}).get('file_count', 0)}",
            f"- 代码材料页数：{manifest.get('total_pages', 0)}",
            f"- 代码输出模式：{manifest.get('mode', '')}",
            f"- 业务理解：{'已读取 草稿/业务理解.json' if business else '未提供，使用项目分析兜底'}",
            "",
            "## 待确认字段",
            "",
        ]
    )
    if pending:
        lines.extend(f"- {field}" for field in pending)
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "```text",
            "STOP_FOR_USER",
            "NEXT_ACTION: 请补全并确认申请表字段；确认后运行 confirm_stage.py --stage application-fields。",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def require_confirmed_business(business: dict[str, Any] | None) -> None:
    if business is None:
        raise SystemExit(
            "STOP_FOR_USER\n"
            "NEXT_ACTION: 申请表信息必须基于已确认的业务理解生成。请先生成并确认 草稿/业务理解.md。"
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
    parser.add_argument("--code-manifest", required=True)
    parser.add_argument("--software-name", required=True)
    parser.add_argument("--version", default="V1.0")
    parser.add_argument("--answers", help="Optional JSON object with confirmed field values")
    parser.add_argument("--business-context", help="Business context JSON generated before material drafting")
    parser.add_argument("--out-dir", default="软件著作权申请资料/草稿")
    args = parser.parse_args()

    analysis = read_json(Path(args.analysis))
    manifest = read_json(Path(args.code_manifest))
    answers = read_json(Path(args.answers)) if args.answers else {}
    business = read_json(Path(args.business_context)) if args.business_context else None
    require_confirmed_business(business)
    out_dir = ensure_dir(Path(args.out_dir))

    fields = build_fields(analysis, manifest, args.software_name, args.version, answers, business)
    out_path = out_dir / "申请表信息.md"
    write_application_md(out_path, fields, analysis, manifest, business)
    print(f"OK application draft: {out_path}")
    print("STOP_FOR_USER")
    print("NEXT_ACTION: 请补全并确认申请表字段；确认后运行 confirm_stage.py --stage application-fields。")


if __name__ == "__main__":
    main()
