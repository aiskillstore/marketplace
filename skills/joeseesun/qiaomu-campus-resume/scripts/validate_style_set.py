#!/usr/bin/env python3
"""Validate a six-style core-theme or reference-style resume manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_resume import REFERENCE_STYLE_CHECKS, THEME_CHECKS, inspect_html, inspect_pdf, validate_data


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取{label}：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}根节点必须是对象")
    return value


def validate_set(data: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    base_errors, base_warnings, counts = validate_data(data)
    errors = list(base_errors)
    warnings = list(base_warnings)
    set_type = str(manifest.get("set_type") or "core_themes")
    if set_type == "reference_styles":
        expected_ids = set(REFERENCE_STYLE_CHECKS)
    elif set_type == "core_themes":
        expected_ids = set(THEME_CHECKS)
    else:
        expected_ids = set()
        errors.append(f"批量清单 set_type 无效：{set_type}")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, list):
        outputs = []
        errors.append("风格清单 outputs 必须是数组")
    seen: list[str] = []
    style_reports: list[dict[str, Any]] = []
    language = data.get("language", "zh-CN")
    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    expected_text = [
        str(basics.get("name", "")),
        str(basics.get("email", "")),
        "教育经历" if language == "zh-CN" else "EDUCATION",
    ]

    for index, item in enumerate(outputs, 1):
        item_errors: list[str] = []
        item_warnings: list[str] = []
        if not isinstance(item, dict):
            errors.append(f"outputs[{index}] 必须是对象")
            continue
        theme = str(item.get("theme", ""))
        reference_style = str(item.get("reference_style", "")).strip() or None
        style_id = reference_style if set_type == "reference_styles" else theme
        seen.append(style_id or "")
        if theme not in THEME_CHECKS:
            item_errors.append(f"未知主题：{theme}")
        if style_id not in expected_ids:
            item_errors.append(f"未知风格：{style_id}")
        if reference_style:
            expected_theme = REFERENCE_STYLE_CHECKS.get(reference_style, {}).get("theme")
            if expected_theme and theme != expected_theme:
                item_errors.append(f"{reference_style} 的基础主题应为 {expected_theme}，当前为 {theme}")
        html_path = Path(str(item.get("html", ""))).expanduser().resolve()
        pdf_path = Path(str(item.get("pdf", ""))).expanduser().resolve()
        html_facts: dict[str, Any] | None = None
        pdf_facts: dict[str, Any] | None = None
        if theme in THEME_CHECKS and style_id in expected_ids:
            html_errors, html_warnings, html_facts = inspect_html(html_path, theme=theme, reference_style=reference_style)
            pdf_errors, pdf_warnings, pdf_facts = inspect_pdf(
                pdf_path,
                expected_text,
                theme=theme,
                require_theme_font=language != "en",
            )
            item_errors.extend(html_errors)
            item_errors.extend(pdf_errors)
            item_warnings.extend(html_warnings)
            item_warnings.extend(pdf_warnings)
        errors.extend(f"{style_id or index}: {message}" for message in item_errors)
        warnings.extend(f"{style_id or index}: {message}" for message in item_warnings)
        style_reports.append(
            {
                "theme": theme,
                "reference_style": reference_style,
                "ok": not item_errors,
                "html": html_facts,
                "pdf": pdf_facts,
                "errors": item_errors,
                "warnings": item_warnings,
            }
        )

    if len(outputs) != 6:
        errors.append(f"风格清单必须正好包含 6 个输出，当前为 {len(outputs)}")
    if len(seen) != len(set(seen)):
        errors.append("风格清单存在重复风格")
    missing = sorted(expected_ids - set(seen))
    extra = sorted(set(seen) - expected_ids)
    if missing:
        errors.append(f"风格清单缺少风格：{', '.join(missing)}")
    if extra:
        errors.append(f"风格清单包含未知风格：{', '.join(extra)}")
    if manifest.get("theme_count") != 6:
        errors.append("风格清单 theme_count 必须为 6")

    return {
        "ok": not errors,
        "set_type": set_type,
        "theme_count": len(outputs),
        "counts": counts,
        "styles": style_reports,
        "errors": errors,
        "warnings": warnings,
        "evidence_boundary": "deterministic six-style structure/runtime checks only; visual quality requires page-by-page inspection",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="一次检查六套核心主题或参考预设大学生简历 HTML/PDF。")
    parser.add_argument("input", help="resume-data.json 路径")
    parser.add_argument("manifest", help="render_resume.py 批量模式生成的风格清单")
    parser.add_argument("--output", "-o", help="汇总验证报告输出路径")
    args = parser.parse_args()

    try:
        data = load_object(Path(args.input).expanduser().resolve(), "简历 JSON")
        manifest = load_object(Path(args.manifest).expanduser().resolve(), "六风格清单")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
    report = validate_set(data, manifest)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
