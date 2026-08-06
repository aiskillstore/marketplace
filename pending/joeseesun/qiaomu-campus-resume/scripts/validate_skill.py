#!/usr/bin/env python3
"""Validate the self-contained qiaomu-campus-resume package."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE.txt",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "manifest.json",
    "agents/interface.yaml",
    "assets/example-interview-ledger.json",
    "assets/example-resume.json",
    "docs/assets/campus-resume-kami.png",
    "evals/trigger_cases.json",
    "evals/output_cases.json",
    "scripts/extract_resume.py",
    "scripts/assess_interview.py",
    "scripts/render_resume.py",
    "scripts/validate_resume.py",
    "scripts/validate_style_set.py",
    "scripts/trigger_eval.py",
    "references/style-system.md",
    "references/best-practices.md",
    "references/intake-and-interview.md",
    "references/typography-system.md",
    "references/resume-collection-catalog.md",
    "reports/prior-art-research.md",
    "reports/creation-handoff.md",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="验证 qiaomu-campus-resume 技能包结构。")
    parser.add_argument("skill_dir", nargs="?", default=".", help="技能目录")
    args = parser.parse_args()
    root = Path(args.skill_dir).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"缺少文件：{relative}")
    entries = [path.relative_to(root).as_posix() for path in root.rglob("SKILL.md")]
    if entries != ["SKILL.md"]:
        errors.append(f"可发现入口必须且只能有根 SKILL.md，当前：{entries}")

    skill_path = root / "SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8") if skill_path.is_file() else ""
    if not re.search(r"^name:\s*qiaomu-campus-resume\s*$", skill_text, re.MULTILINE):
        errors.append("SKILL.md 名称不匹配")
    if "description:" not in skill_text or "大学生" not in skill_text or "PDF" not in skill_text:
        errors.append("SKILL.md description 缺少关键路由信息")
    for required in ("四种能力路由", "从 0 问答写简历", "排版快速路径", "提供 JD 针对性定制", "一次生成多种风格"):
        if required not in skill_text:
            errors.append(f"SKILL.md 缺少宣传能力路由：{required}")
    for link in re.findall(r"\]\(([^)]+\.md)\)", skill_text):
        if not (root / link).is_file():
            errors.append(f"SKILL.md 引用了不存在的文件：{link}")

    for relative in (
        "manifest.json",
        "assets/example-interview-ledger.json",
        "assets/example-resume.json",
        "evals/trigger_cases.json",
        "evals/output_cases.json",
    ):
        path = root / relative
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{relative} JSON 无效：{exc}")

    manifest_path = root / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("name") != "qiaomu-campus-resume":
            errors.append("manifest name 不匹配")
        if not re.match(r"^\d+\.\d+\.\d+$", str(manifest.get("version", ""))):
            errors.append("manifest version 不是语义化版本")
        if manifest.get("maturity_tier") != "production":
            warnings.append("maturity_tier 不是 production")
        version_match = re.search(r'^\s*version:\s*["\']?([^"\'\s]+)', skill_text, re.MULTILINE)
        if version_match and manifest.get("version") != version_match.group(1):
            errors.append("SKILL.md 与 manifest.json 版本不一致")

    renderer_path = root / "scripts/render_resume.py"
    if renderer_path.is_file():
        renderer_text = renderer_path.read_text(encoding="utf-8")
        for theme in ("ats-classic", "kami", "swiss", "tech", "campus", "compact"):
            if f'"{theme}"' not in renderer_text:
                errors.append(f"渲染器缺少主题：{theme}")
        if "--all-themes" not in renderer_text:
            errors.append("渲染器缺少六主题批量入口 --all-themes")
        if "--all-reference-styles" not in renderer_text:
            errors.append("渲染器缺少参考预设批量入口 --all-reference-styles")
        for reference_style in ("rc-003", "rc-071", "rc-102", "rc-109", "rc-150", "rc-214"):
            if f'"{reference_style}"' not in renderer_text:
                errors.append(f"渲染器缺少参考预设：{reference_style}")

    interface = root / "agents/interface.yaml"
    if interface.is_file():
        interface_text = interface.read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:", "adapter_targets:"):
            if field not in interface_text:
                errors.append(f"agents/interface.yaml 缺少 {field}")
        for required in ("从 0", "JD", "source_resume", "--all-themes"):
            if required not in interface_text:
                errors.append(f"agents/interface.yaml 缺少能力路由：{required}")

    intake_path = root / "references/intake-and-interview.md"
    if intake_path.is_file():
        intake_text = intake_path.read_text(encoding="utf-8")
        for required in (
            "每轮只问一个核心问题",
            "当前判断",
            "interview-ledger.json",
            "assess_interview.py",
            "最终确认",
            "旧简历纯排版快速路径",
            "JD 定制路径",
        ):
            if required not in intake_text:
                errors.append(f"对话访谈协议缺少：{required}")

    practices_path = root / "references/best-practices.md"
    if practices_path.is_file():
        practices_text = practices_path.read_text(encoding="utf-8")
        for required in ("A-C-R-E", "Greenhouse", "CMU", "自适应密度", "要求 → 事实证据"):
            if required not in practices_text:
                errors.append(f"最佳实践参考缺少：{required}")

    report = {"ok": not errors, "root": str(root), "errors": errors, "warnings": warnings}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
