#!/usr/bin/env python3
"""Generate README.md and README.zh.md from repo metadata and optional config."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

TEMPLATE_EN = "readme_template_en.md"
TEMPLATE_ZH = "readme_template_zh.md"

DEFAULT_EN_TEMPLATE = """# {{project_name_en}}
{{tagline_en}}

{{badges}}

[中文](README.zh.md)

{{overview_section}}
{{contents_section}}
{{features_section}}
{{components_section}}
{{quickstart_section}}
{{configuration_section}}
{{structure_section}}
{{license_section}}
{{credits_section}}
"""

DEFAULT_ZH_TEMPLATE = """# {{project_name_zh}}
{{tagline_zh}}

{{badges}}

[English](README.md)

{{overview_section}}
{{contents_section}}
{{features_section}}
{{components_section}}
{{quickstart_section}}
{{configuration_section}}
{{structure_section}}
{{license_section}}
{{credits_section}}
"""

DIR_LABELS_EN = {
    "configs": "configs/ - runtime configuration",
    "models": "models/ - trained models",
    "src": "src/ - core source code",
    "docs": "docs/ - documentation",
    "examples": "examples/ - training/testing scripts",
    "static": "static/ - frontend assets",
    "templates": "templates/ - HTML templates",
}

DIR_LABELS_ZH = {
    "configs": "configs/ - 运行配置",
    "models": "models/ - 训练模型",
    "src": "src/ - 核心源码",
    "docs": "docs/ - 文档",
    "examples": "examples/ - 训练/测试脚本",
    "static": "static/ - 前端静态资源",
    "templates": "templates/ - HTML 模板",
}

HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"```[a-zA-Z0-9_-]*\n(.*?)```", re.DOTALL)


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Dict:
    return json.loads(read_text(path))


def extract_section(text: str, titles: List[str]) -> Optional[str]:
    if not text:
        return None
    for title in titles:
        pattern = re.compile(rf"^##\s+{re.escape(title)}\s*$", re.MULTILINE)
        match = pattern.search(text)
        if not match:
            continue
        start = match.end()
        rest = text[start:]
        next_heading = HEADING_RE.search(rest)
        end = start + next_heading.start() if next_heading else len(text)
        section = text[start:end].strip()
        return section if section else None
    return None


def extract_bullets(section_text: Optional[str]) -> List[str]:
    if not section_text:
        return []
    bullets = []
    for line in section_text.splitlines():
        line = line.strip()
        if line.startswith("-"):
            bullets.append(line.lstrip("- ").strip())
    return bullets


def extract_first_paragraph(section_text: Optional[str]) -> Optional[str]:
    if not section_text:
        return None
    parts = [p.strip() for p in section_text.split("\n\n") if p.strip()]
    return parts[0] if parts else None


def extract_code_block(section_text: Optional[str]) -> List[str]:
    if not section_text:
        return []
    match = CODE_BLOCK_RE.search(section_text)
    if not match:
        return []
    block = match.group(1).strip()
    return [line.rstrip() for line in block.splitlines() if line.strip()]


def detect_license_text(license_path: Path) -> Optional[str]:
    if not license_path.exists():
        return None
    text = read_text(license_path)
    if "MIT License" in text:
        return "MIT"
    if "Apache License" in text:
        return "Apache-2.0"
    if "GNU GENERAL PUBLIC LICENSE" in text:
        return "GPL"
    if "BSD" in text:
        return "BSD"
    if "Mozilla Public License" in text:
        return "MPL-2.0"
    return None


def detect_port(app_path: Path) -> Optional[str]:
    if not app_path.exists():
        return None
    text = read_text(app_path)
    match = re.search(r"port\s*=\s*(\d+)", text)
    return match.group(1) if match else None


def collect_top_level_contents(project_root: Path) -> Tuple[List[str], List[str]]:
    en_items: List[str] = []
    zh_items: List[str] = []
    for dirname, label in DIR_LABELS_EN.items():
        if (project_root / dirname).exists():
            en_items.append(label)
    for dirname, label in DIR_LABELS_ZH.items():
        if (project_root / dirname).exists():
            zh_items.append(label)
    return en_items, zh_items


def load_config(config_path: Optional[Path]) -> Dict[str, object]:
    if not config_path:
        return {}
    if not config_path.exists():
        return {}
    if config_path.suffix.lower() != ".json":
        raise ValueError("Config must be JSON (.json).")
    return load_json(config_path)


def make_badges(license_name: Optional[str], python_version: Optional[str]) -> str:
    badges = []
    if license_name:
        badges.append(f"[![License: {license_name}](https://img.shields.io/badge/License-{license_name}-yellow.svg)](LICENSE)")
    if python_version:
        badges.append(f"[![Python {python_version}](https://img.shields.io/badge/python-{python_version}-blue.svg)](https://www.python.org/downloads/)")
    return "\n".join(badges)


def format_bullets(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def format_section(title: str, body: str) -> str:
    if not body.strip():
        return ""
    return f"## {title}\n{body.strip()}\n"


def format_code_block(lines: List[str]) -> str:
    if not lines:
        return ""
    content = "\n".join(lines)
    return f"```bash\n{content}\n```"


def normalize_output(text: str) -> str:
    cleaned = re.sub(r"\n{3,}", "\n\n", text)
    return cleaned.strip() + "\n"


def resolve_project_name(readme_text: Optional[str], config_data: Dict[str, object]) -> Tuple[Optional[str], Optional[str]]:
    name_en = config_data.get("project_name_en")
    name_zh = config_data.get("project_name_zh")
    if name_en or name_zh:
        return name_en, name_zh
    if not readme_text:
        return None, None
    headings = [line.strip("# ").strip() for line in readme_text.splitlines() if line.startswith("# ")]
    for heading in headings:
        if contains_cjk(heading):
            name_zh = name_zh or heading
        else:
            name_en = name_en or heading
    return name_en, name_zh


def resolve_tagline(config_data: Dict[str, object], config_json: Dict[str, object]) -> Tuple[Optional[str], Optional[str]]:
    tag_en = config_data.get("tagline_en")
    tag_zh = config_data.get("tagline_zh")
    if tag_en or tag_zh:
        return tag_en, tag_zh
    system = config_json.get("system", {}) if isinstance(config_json, dict) else {}
    desc = system.get("description") if isinstance(system, dict) else None
    if isinstance(desc, str):
        if contains_cjk(desc):
            tag_zh = desc
        else:
            tag_en = desc
    return tag_en, tag_zh


def resolve_overview(readme_text: Optional[str], config_data: Dict[str, object]) -> Tuple[Optional[str], Optional[str]]:
    overview_en = config_data.get("overview_en")
    overview_zh = config_data.get("overview_zh")
    if overview_en or overview_zh:
        return overview_en, overview_zh
    overview_zh = extract_first_paragraph(extract_section(readme_text or "", ["项目简介"]))
    overview_en = extract_first_paragraph(extract_section(readme_text or "", ["Overview"]))
    return overview_en, overview_zh


def resolve_features(readme_text: Optional[str], config_data: Dict[str, object]) -> Tuple[List[str], List[str]]:
    features_en = config_data.get("features_en") or []
    features_zh = config_data.get("features_zh") or []
    if features_en or features_zh:
        return list(features_en), list(features_zh)
    features_zh = extract_bullets(extract_section(readme_text or "", ["关键能力", "核心能力"]))
    features_en = extract_bullets(extract_section(readme_text or "", ["Key Capabilities", "Features"]))
    return features_en, features_zh


def resolve_components(readme_text: Optional[str], config_data: Dict[str, object]) -> Tuple[List[str], List[str]]:
    components_en = config_data.get("components_en") or []
    components_zh = config_data.get("components_zh") or []
    if components_en or components_zh:
        return list(components_en), list(components_zh)
    components_zh = extract_bullets(extract_section(readme_text or "", ["系统组件", "系统组成"]))
    components_en = extract_bullets(extract_section(readme_text or "", ["System Components", "Components"]))
    return components_en, components_zh


def resolve_quickstart(
    readme_text: Optional[str],
    config_data: Dict[str, object],
    project_root: Path,
    app_port: Optional[str],
) -> Tuple[List[str], List[str]]:
    qs_en = config_data.get("quick_start_en") or []
    qs_zh = config_data.get("quick_start_zh") or []
    if qs_en or qs_zh:
        return list(qs_en), list(qs_zh)

    section_zh = extract_section(readme_text or "", ["快速上手", "快速开始"]) if readme_text else None
    section_en = extract_section(readme_text or "", ["Quick Start", "Getting Started"]) if readme_text else None

    qs_zh = extract_code_block(section_zh)
    qs_en = extract_code_block(section_en)

    if qs_en or qs_zh:
        return qs_en, qs_zh

    steps_en = []
    steps_zh = []
    if (project_root / "requirements.txt").exists():
        steps_en.append("pip install -r requirements.txt")
        steps_zh.append("pip install -r requirements.txt")
    if (project_root / "requirements_ai.txt").exists():
        steps_en.append("pip install -r requirements_ai.txt  # optional")
        steps_zh.append("pip install -r requirements_ai.txt  # 可选")
    if (project_root / "run.py").exists():
        steps_en.append("python3 run.py")
        steps_zh.append("python3 run.py")
    elif (project_root / "app.py").exists():
        steps_en.append("python3 app.py")
        steps_zh.append("python3 app.py")
    if app_port:
        steps_en.append(f"open http://localhost:{app_port}")
        steps_zh.append(f"打开 http://localhost:{app_port}")
    return steps_en, steps_zh


def resolve_structure(project_root: Path) -> Optional[str]:
    structure_path = project_root / "PROJECT_STRUCTURE.md"
    if not structure_path.exists():
        return None
    text = read_text(structure_path)
    match = CODE_BLOCK_RE.search(text)
    if not match:
        return None
    return match.group(1).strip()


def resolve_configuration(project_root: Path) -> Tuple[List[str], List[str]]:
    config_files = []
    for candidate in ["config.json", "configs/ai_model_config.json", "configs/doca_config.json"]:
        if (project_root / candidate).exists():
            config_files.append(candidate)
    if not config_files:
        return [], []
    en_items = [f"{path}" for path in config_files]
    zh_items = [f"{path}" for path in config_files]
    return en_items, zh_items


def resolve_credits(config_data: Dict[str, object]) -> Tuple[Optional[str], Optional[str]]:
    credits_en = config_data.get("credits_en")
    credits_zh = config_data.get("credits_zh")
    return credits_en, credits_zh


def build_context(project_root: Path, config_data: Dict[str, object]) -> Dict[str, object]:
    readme_path = project_root / "README.md"
    readme_text = read_text(readme_path) if readme_path.exists() else None
    config_json = load_json(project_root / "config.json") if (project_root / "config.json").exists() else {}

    name_en, name_zh = resolve_project_name(readme_text, config_data)
    if not name_en and not name_zh:
        repo_name = project_root.name
        name_en = repo_name
        name_zh = repo_name
    if not name_en and name_zh:
        name_en = name_zh
    if not name_zh and name_en:
        name_zh = name_en

    tag_en, tag_zh = resolve_tagline(config_data, config_json)
    overview_en, overview_zh = resolve_overview(readme_text, config_data)
    features_en, features_zh = resolve_features(readme_text, config_data)
    components_en, components_zh = resolve_components(readme_text, config_data)

    port = detect_port(project_root / "app.py")
    qs_en, qs_zh = resolve_quickstart(readme_text, config_data, project_root, port)

    contents_en, contents_zh = collect_top_level_contents(project_root)
    config_en, config_zh = resolve_configuration(project_root)
    structure_tree = resolve_structure(project_root)

    license_name = config_data.get("license") or detect_license_text(project_root / "LICENSE")
    python_version = config_data.get("python_version") or "3.8+"
    badges = make_badges(license_name, python_version)

    credits_en, credits_zh = resolve_credits(config_data)

    return {
        "project_name_en": name_en,
        "project_name_zh": name_zh,
        "tagline_en": tag_en or "",
        "tagline_zh": tag_zh or "",
        "overview_en": overview_en or "",
        "overview_zh": overview_zh or "",
        "features_en": features_en,
        "features_zh": features_zh,
        "components_en": components_en,
        "components_zh": components_zh,
        "quick_start_en": qs_en,
        "quick_start_zh": qs_zh,
        "contents_en": contents_en,
        "contents_zh": contents_zh,
        "configuration_en": config_en,
        "configuration_zh": config_zh,
        "structure_tree": structure_tree or "",
        "license": license_name or "",
        "badges": badges,
        "credits_en": credits_en or "",
        "credits_zh": credits_zh or "",
    }


def render_readme(template_text: str, ctx: Dict[str, object], lang: str) -> str:
    def section(title: str, body: str) -> str:
        return format_section(title, body)

    if lang == "en":
        overview = section("Overview", ctx["overview_en"])
        contents = section("Contents", format_bullets(ctx["contents_en"]))
        features = section("Key Capabilities", format_bullets(ctx["features_en"]))
        components = section("System Components", format_bullets(ctx["components_en"]))
        quickstart = section("Quick Start", format_code_block(ctx["quick_start_en"]))
        configuration = section("Configuration", format_bullets(ctx["configuration_en"]))
        structure = section("Project Structure", f"```\n{ctx['structure_tree']}\n```" if ctx["structure_tree"] else "")
        license_section = section("License", ctx["license"])
        credits = section("Credits", ctx["credits_en"])
        placeholders = {
            "project_name_en": ctx["project_name_en"],
            "tagline_en": ctx["tagline_en"],
            "badges": ctx["badges"],
            "overview_section": overview,
            "contents_section": contents,
            "features_section": features,
            "components_section": components,
            "quickstart_section": quickstart,
            "configuration_section": configuration,
            "structure_section": structure,
            "license_section": license_section,
            "credits_section": credits,
        }
    else:
        overview = section("项目简介", ctx["overview_zh"])
        contents = section("内容", format_bullets(ctx["contents_zh"]))
        features = section("关键能力", format_bullets(ctx["features_zh"]))
        components = section("系统组件", format_bullets(ctx["components_zh"]))
        quickstart = section("快速上手", format_code_block(ctx["quick_start_zh"]))
        configuration = section("配置", format_bullets(ctx["configuration_zh"]))
        structure = section("目录结构", f"```\n{ctx['structure_tree']}\n```" if ctx["structure_tree"] else "")
        license_section = section("许可证", ctx["license"])
        credits = section("鸣谢", ctx["credits_zh"])
        placeholders = {
            "project_name_zh": ctx["project_name_zh"],
            "tagline_zh": ctx["tagline_zh"],
            "badges": ctx["badges"],
            "overview_section": overview,
            "contents_section": contents,
            "features_section": features,
            "components_section": components,
            "quickstart_section": quickstart,
            "configuration_section": configuration,
            "structure_section": structure,
            "license_section": license_section,
            "credits_section": credits,
        }

    rendered = template_text
    for key, value in placeholders.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))

    rendered = re.sub(r"\{\{[^}]+\}\}", "", rendered)
    return normalize_output(rendered)


def load_template(template_dir: Path, filename: str, fallback: str) -> str:
    path = template_dir / filename
    if path.exists():
        return read_text(path)
    return fallback


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate bilingual README files.")
    parser.add_argument("--project-root", default=".", help="Repository root path")
    parser.add_argument("--config", default=None, help="Path to release_assistant.json")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: project root)")
    parser.add_argument("--template-dir", default=None, help="Template directory")
    parser.add_argument("--language", choices=["en", "zh", "both"], default="both")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing README files")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else project_root

    config_path = Path(args.config).resolve() if args.config else None
    config_data = load_config(config_path)

    template_dir = Path(args.template_dir).resolve() if args.template_dir else Path(__file__).resolve().parent.parent / "assets"
    template_en = load_template(template_dir, TEMPLATE_EN, DEFAULT_EN_TEMPLATE)
    template_zh = load_template(template_dir, TEMPLATE_ZH, DEFAULT_ZH_TEMPLATE)

    ctx = build_context(project_root, config_data)

    outputs = []
    if args.language in ("en", "both"):
        out_path = output_dir / "README.md"
        if out_path.exists() and not args.overwrite:
            raise RuntimeError(f"{out_path} exists (use --overwrite to replace).")
        out_path.write_text(render_readme(template_en, ctx, "en"), encoding="utf-8")
        outputs.append(out_path)

    if args.language in ("zh", "both"):
        out_path = output_dir / "README.zh.md"
        if out_path.exists() and not args.overwrite:
            raise RuntimeError(f"{out_path} exists (use --overwrite to replace).")
        out_path.write_text(render_readme(template_zh, ctx, "zh"), encoding="utf-8")
        outputs.append(out_path)

    print("Generated:")
    for path in outputs:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
