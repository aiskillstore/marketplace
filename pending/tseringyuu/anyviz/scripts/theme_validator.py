#!/usr/bin/env python3
"""
anyviz 主题一致性验证器

验证生成的图表配置是否符合 anyviz 默认美学规范，
以及多图表之间的一致性。

用法:
    python theme_validator.py --config chart_config.json
    python theme_validator.py --config chart_config.json --multi-chart
"""

import json
import sys
import argparse
from typing import Dict, List, Any, Optional, Tuple


# 从 default.json 加载的参考规范
DEFAULT_SPEC = {
    "typography": {
        "h1": {"size_px": 16, "weight": 600, "color": "#1A1A1A"},
        "h2": {"size_px": 13, "weight": 400, "color": "#555555"},
        "h3": {"size_px": 11, "weight": 400, "color": "#333333"},
        "h4": {"size_px": 10, "weight": 400, "color": "#666666"},
        "h5": {"size_px": 10, "weight": 400, "color": "#555555"},
        "h6": {"size_px": 9, "weight": 400, "color": "#888888"},
    },
    "spacing": {
        "chart_margin": {"top": 48, "right": 36, "bottom": 56, "left": 56},
        "legend_to_plot_gap": 20,
        "title_to_legend_gap": 16,
    },
    "title": {
        "anchor": "canvas",
        "alignment": "center",
    },
    "legend": {
        "clearance_px": {
            "title_to_legend": 16,
            "legend_to_plot": 20,
            "legend_to_axis_label": 16,
            "legend_to_data_label": 16,
        }
    },
    "export": {
        "visual_centering": {"enabled": True},
        "embedded_source_policy": "off_by_default",
    },
    "stroke": {
        "line": {"width_px": 2.0},
        "grid": {"width_px": 0.5, "color": "#E0E0E0"},
    },
    "color": {
        "categorical_palette": [
            "#4269d0", "#3ca951", "#ff725c", "#a463f2", "#efb118",
            "#6cc5b0", "#9696a0", "#f5a623", "#ca5bb8", "#ff8ab7"
        ]
    }
}


def load_config(path: str) -> Dict:
    with open(path, 'r') as f:
        return json.load(f)


def validate_typography(config: Dict) -> List[str]:
    """验证排版参数是否符合规范"""
    issues = []
    typo = config.get("typography", {})

    for level in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        level_config = typo.get(level, {})
        spec = DEFAULT_SPEC["typography"][level]

        actual_size = level_config.get("size_px")
        if actual_size is not None and actual_size != spec["size_px"]:
            issues.append(
                f"[排版] {level} 字号: 期望 {spec['size_px']}px, "
                f"实际 {actual_size}px — 如非用户指定，请统一"
            )

        actual_weight = level_config.get("weight")
        if actual_weight is not None and actual_weight != spec["weight"]:
            issues.append(
                f"[排版] {level} 字重: 期望 {spec['weight']}, "
                f"实际 {actual_weight}"
            )

    return issues


def validate_spacing(config: Dict) -> List[str]:
    """验证间距参数是否符合规范"""
    issues = []
    spacing = config.get("spacing", {})
    margin = spacing.get("chart_margin", {})
    spec = DEFAULT_SPEC["spacing"]["chart_margin"]

    for key in ["top", "right", "bottom", "left"]:
        actual = margin.get(key)
        expected = spec[key]
        if actual is not None and actual != expected:
            issues.append(
                f"[间距] chart_margin.{key}: 期望 {expected}px, "
                f"实际 {actual}px"
            )

    for key in ["legend_to_plot_gap", "title_to_legend_gap"]:
        actual = spacing.get(key)
        expected = DEFAULT_SPEC["spacing"][key]
        if actual is not None and actual < expected:
            issues.append(
                f"[间距] {key}: 至少 {expected}px, 实际 {actual}px — 图例或标题可能与图表主体过近"
            )

    return issues


def validate_title_layout(config: Dict) -> List[str]:
    """验证标题是否以整张画布为参照居中。"""
    issues = []
    title = config.get("title", {})
    if not title:
        return issues

    expected_anchor = DEFAULT_SPEC["title"]["anchor"]
    expected_alignment = DEFAULT_SPEC["title"]["alignment"]

    actual_anchor = title.get("anchor")
    if actual_anchor is not None and actual_anchor != expected_anchor:
        issues.append(
            f"[标题] anchor: 期望 {expected_anchor}, 实际 {actual_anchor} — 主标题应以整张画布居中"
        )

    actual_alignment = title.get("alignment")
    if actual_alignment is not None and actual_alignment != expected_alignment:
        issues.append(
            f"[标题] alignment: 期望 {expected_alignment}, 实际 {actual_alignment}"
        )

    return issues


def validate_legend_layout(config: Dict) -> List[str]:
    """验证图例与标题、绘图区和标签之间的安全距离。"""
    issues = []
    legend = config.get("legend", {})
    if not legend:
        return issues

    clearance = legend.get("clearance_px", {})
    expected = DEFAULT_SPEC["legend"]["clearance_px"]
    for key, minimum in expected.items():
        actual = clearance.get(key)
        if actual is not None and actual < minimum:
            issues.append(
                f"[图例] clearance_px.{key}: 至少 {minimum}px, 实际 {actual}px"
            )

    return issues


def validate_export_policy(config: Dict) -> List[str]:
    """验证导出时的视觉居中与来源说明策略。"""
    issues = []
    export = config.get("export", {})
    visual_centering = export.get("visual_centering", {})
    if "enabled" in visual_centering and not visual_centering["enabled"]:
        issues.append("[导出] visual_centering.enabled 应为 true，避免紧裁切造成视觉偏移")

    policy = export.get("embedded_source_policy")
    if policy is not None and policy not in {"off_by_default", "forbidden_when_document_caption_exists"}:
        issues.append(
            "[导出] embedded_source_policy 应为 off_by_default 或 forbidden_when_document_caption_exists"
        )

    publication = config.get("publication", {})
    source_note = publication.get("source_note", {})
    if source_note.get("outside_chart") is True and source_note.get("inside_chart") is True:
        issues.append("[论文] source_note 不能同时要求 inside_chart 与 outside_chart，避免资料来源重复")

    return issues


def validate_stroke(config: Dict) -> List[str]:
    """验证线条样式是否符合规范"""
    issues = []
    stroke = config.get("stroke", {})

    line = stroke.get("line", {})
    spec_line = DEFAULT_SPEC["stroke"]["line"]
    if "width_px" in line and line["width_px"] != spec_line["width_px"]:
        issues.append(
            f"[线条] 线宽: 期望 {spec_line['width_px']}px, "
            f"实际 {line['width_px']}px"
        )

    grid = stroke.get("grid", {})
    spec_grid = DEFAULT_SPEC["stroke"]["grid"]
    if "color" in grid and grid["color"] != spec_grid["color"]:
        issues.append(
            f"[网格] 颜色: 期望 {spec_grid['color']}, "
            f"实际 {grid['color']}"
        )
    if "width_px" in grid and grid["width_px"] != spec_grid["width_px"]:
        issues.append(
            f"[网格] 线宽: 期望 {spec_grid['width_px']}px, "
            f"实际 {grid['width_px']}px"
        )

    return issues


def validate_color_palette(config: Dict) -> List[str]:
    """验证色板是否在默认色板范围内。

    使用默认色板的前缀（按顺序取前 N 色）视为一致——类别较少时
    只取前几色是正常且推荐的用法。仅当色板包含默认色板之外的颜色，
    或未按默认顺序取色时，才提示可能为用户定制。
    """
    issues = []
    palette = config.get("color", {}).get("categorical_palette", [])
    default = DEFAULT_SPEC["color"]["categorical_palette"]

    if not palette:
        return issues

    # 归一化为小写比较，避免大小写差异误报
    norm_palette = [c.lower() for c in palette]
    norm_default = [c.lower() for c in default]

    is_ordered_prefix = (
        len(norm_palette) <= len(norm_default)
        and norm_palette == norm_default[:len(norm_palette)]
    )

    if not is_ordered_prefix:
        issues.append(
            "[色板] 色板与默认值不同 — 请确认是否为用户定制"
        )

    return issues


def validate_multi_chart_consistency(charts: List[Dict]) -> List[str]:
    """验证多图表之间的一致性"""
    issues = []
    if len(charts) < 2:
        return issues

    # 提取每个图表的排版参数
    typographies = []
    for i, chart in enumerate(charts):
        typo = chart.get("typography", {})
        typographies.append({
            "index": i,
            "name": chart.get("name", f"Chart {i+1}"),
            "h1_size": typo.get("h1", {}).get("size_px"),
            "h1_color": typo.get("h1", {}).get("color"),
            "h4_size": typo.get("h4", {}).get("size_px"),
            "h4_color": typo.get("h4", {}).get("color"),
            "h5_size": typo.get("h5", {}).get("size_px"),
            "h6_size": typo.get("h6", {}).get("size_px"),
        })

    # 检查标题一致性
    h1_sizes = set(t["h1_size"] for t in typographies if t["h1_size"])
    if len(h1_sizes) > 1:
        issues.append(
            f"[一致性-标题] 多图表标题字号不一致: {h1_sizes}"
        )

    h1_colors = set(t["h1_color"] for t in typographies if t["h1_color"])
    if len(h1_colors) > 1:
        issues.append(
            f"[一致性-标题] 多图表标题颜色不一致: {h1_colors}"
        )

    # 检查刻度标签一致性
    h4_sizes = set(t["h4_size"] for t in typographies if t["h4_size"])
    if len(h4_sizes) > 1:
        issues.append(
            f"[一致性-刻度] 多图表刻度字号不一致: {h4_sizes}"
        )

    # 检查图例一致性
    h5_sizes = set(t["h5_size"] for t in typographies if t["h5_size"])
    if len(h5_sizes) > 1:
        issues.append(
            f"[一致性-图例] 多图表图例字号不一致: {h5_sizes}"
        )

    # 检查颜色映射一致性
    color_mappings = []
    for chart in charts:
        cm = chart.get("color_mapping", {})
        if cm:
            color_mappings.append(cm)

    if len(color_mappings) > 1:
        keys = set()
        for cm in color_mappings:
            keys.update(cm.keys())

        for key in keys:
            values = set()
            for cm in color_mappings:
                if key in cm:
                    values.add(cm[key])
            if len(values) > 1:
                issues.append(
                    f"[一致性-颜色] 实体 '{key}' 在不同图表中颜色不一致: {values}"
                )

    # 检查间距一致性
    margins = []
    for chart in charts:
        m = chart.get("spacing", {}).get("chart_margin", {})
        if m:
            margins.append(m)

    if len(margins) > 1:
        for key in ["top", "right", "bottom", "left"]:
            values = set(m.get(key) for m in margins if m.get(key) is not None)
            if len(values) > 1:
                issues.append(
                    f"[一致性-间距] margin.{key} 不一致: {values}"
                )

    return issues


def main():
    parser = argparse.ArgumentParser(
        description="anyviz 主题一致性验证器"
    )
    parser.add_argument(
        "--config", "-c", required=True,
        help="图表配置 JSON 文件路径"
    )
    parser.add_argument(
        "--multi-chart", "-m", action="store_true",
        help="多图表模式，额外检查图表间一致性"
    )
    args = parser.parse_args()

    config = load_config(args.config)

    all_issues = []

    # 确定待校验的图表列表：
    # 1) 显式 --multi-chart，或
    # 2) 配置顶层包含 charts 数组（自动识别多图表配置，避免把外层包装对象误当单图表，导致漏检）
    if isinstance(config, dict) and isinstance(config.get("charts"), list):
        charts = config["charts"]
        multi_chart = True
    elif args.multi_chart:
        charts = config.get("charts", [config])
        multi_chart = True
    else:
        charts = [config]
        multi_chart = False

    for chart in charts:
        all_issues.extend(validate_typography(chart))
        all_issues.extend(validate_spacing(chart))
        all_issues.extend(validate_title_layout(chart))
        all_issues.extend(validate_legend_layout(chart))
        all_issues.extend(validate_export_policy(chart))
        all_issues.extend(validate_stroke(chart))
        all_issues.extend(validate_color_palette(chart))

    # 多图表一致性验证
    if multi_chart and len(charts) > 1:
        all_issues.extend(validate_multi_chart_consistency(charts))

    # 输出结果
    if all_issues:
        print(f"❌ 发现 {len(all_issues)} 个问题：\n")
        for issue in all_issues:
            print(f"  • {issue}")
        print(f"\n共 {len(all_issues)} 个问题需要处理。")
        sys.exit(1)
    else:
        print("✅ 所有检查通过！图表配置符合 anyviz 默认美学规范。")
        sys.exit(0)


if __name__ == "__main__":
    main()
