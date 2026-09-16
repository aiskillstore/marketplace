from __future__ import annotations

from pathlib import Path
from typing import Any

from presentation_contracts import comparison_context_text
from content_resolver import project_legacy_content_refs, resolve_page_content, validate_renderer_model
from slideviber_consistency import build_slide_lock_spec


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    return f"{float(value):,.2f}"


def render_slideviber_handoff(model: dict[str, Any], output_path: Path, *, theme_selection: dict | None = None) -> None:
    model = project_legacy_content_refs(model)
    validate_renderer_model(model)
    theme_note = '主题选择尚未单独确认；依照 references/ppt-theme-selection.md 处理，旧request主题仅作推荐。'
    if theme_selection is not None:
        from ppt_theme_selection import validate_selection
        selected = validate_selection(theme_selection)
        theme_note = f"沿用 {selected['name']}；选择来源 {theme_selection['selection_source']}；配置指纹 {theme_selection['config_sha256']}。美化版为矢量形状，原生图表数据编辑要求需另行核对。"
    lock_by_slide = {
        item["slide_id"]: item for item in build_slide_lock_spec(model)
    }
    slides: list[str] = []
    for slide in model["slide_plan"]:
        payload = resolve_page_content(model, slide)
        evidence = ", ".join(slide.get("evidence_ids", [])) or "无（封面或导航页）"
        charts = ", ".join(slide.get("chart_ids", [])) or "无"
        visual_spec = slide.get("visual_spec", {})
        display_claim = str(visual_spec.get("display_claim") or slide["claim"])
        comparison_context = comparison_context_text(
            visual_spec.get("comparison_contexts", [])
        ) or "无"
        locked_tokens = "\n".join(
            f"  - `{token}`"
            for token in lock_by_slide[slide["slide_id"]]["locked_tokens"]
        )
        semantic_locks = lock_by_slide[slide["slide_id"]].get("semantic_locks", [])
        semantic_lines = "\n".join(
            f"  - `{item['lock_id']}`｜{item['lock_type']}｜"
            f"{item.get('name') or item.get('statement', '')}"
            + (
                f"｜值 {item.get('value')} {item.get('unit', '')}｜"
                f"周期 {item.get('period', '')}｜范围 {item.get('scope', '')}"
                if item.get("lock_type") == "metric"
                else f"｜口径 {item.get('formula', '')}"
                if item.get("lock_type") == "metric_contract"
                else ""
            )
            for item in semantic_locks
        ) or "  - 无新增语义锁"
        chart_lines = "\n".join(
            f"  - `{item['chart_id']}`｜指标 {item.get('metric_name', '')}｜"
            f"类型 {item.get('chart_type', '')}｜序列 {len(item.get('series', []))}"
            for item in lock_by_slide[slide["slide_id"]].get("chart_locks", [])
        ) or "  - 无图表锁"
        slides.append(
            f"""### {slide['slide_id']}｜{display_claim}

- 页面目标：{slide['purpose']}
- 推荐版式：`{slide['layout_id']}`（轮廓 `{slide['silhouette']}`）
- 页级比较口径：{comparison_context}
- 锁定 evidence ID：{evidence}
- 图表 ID：{charts}
- 本页已选内容：KPI {len(payload['kpis'])}｜洞察 {len(payload['insights'])}｜行动 {len(payload['actions'])}｜杠杆 {len(payload['levers'])}
- 锁定内容：数字、日期、指标口径、判断含义、行动含义与图表对应关系不得改变；仅可压缩冗余措辞和调整换行。
- 精修版必须保留的机器核验 token：
{locked_tokens}
- 语义锁：
{semantic_lines}
- 图表锁：
{chart_lines}
"""
        )

    output = f"""# SlideViber 可选精修交接

标准汇报版 `report.pptx` 必须先独立达到职场汇报标准。若需要更强的演示感，可继续使用 SlideViber，核验预览后导出 `report-polished.pptx`；没有已确认风格且未授权代选时先提供两页主题小样等待选择，不得覆盖标准版。

{theme_note}

## 使用边界

- SlideViber 是可选能力，不是本 Skill 的硬依赖，也不会自动安装。
- 官方项目：https://github.com/tf71991/slideviber-skill
- 数字、日期、指标口径、结论含义、行动含义和 evidence 对应关系全部锁定；evidence ID 只保留在交接与模型中，不进入观众可见页面。
- 可以调整布局、配色、字体、视觉层级、留白、换行和冗余措辞。
- 序号、项目符号或优先级标识与右侧正文组成同一行时，标识必须与整个多行文本块垂直居中，不得只对齐首行基线；单行与多行内容使用同一对齐契约。
- 有色强调卡或分区色带中的独立标题、标签和核心数值必须以容器几何中心为基准水平居中；SVG 文本使用容器中心 x 坐标并设置 `text-anchor="middle"`，多行组合按整体视觉中心布置，不得用固定左侧内边距假装居中。
- 日期、数字与单位、指标名称和英文缩写属于不可拆语义单元；在 SVG `foreignObject` 中使用 `white-space: nowrap` 的内联容器保护，或使用等效不换行标记，不得把同一语义单元拆到两行。若整句装不下，先扩容或精简，不得缩小字号硬塞。
- 同一页的完整同比／环比周期只在固定元信息区声明一次；标题使用 `display_claim`，正文只保留“同比／环比”短标签与业务判断。语义锁中的完整原句用于追溯，不得机械复制到每个段落。
- 任何实质性改写都必须重新经过用户确认。
- 导出后必须检查锁定数字、日期、结论与行动是否仍存在，并核对逐页 evidence 对应关系未改变。
- 导出后执行：`python scripts/slideviber_consistency.py --model report_model.json --pptx report-polished.pptx --output slideviber_qa.json`。

## 受众与核心信息

- 受众：{model['request']['audience']}
- 分析目标：{model['request']['objective']}
- 主题建议：{model['request']['theme']}
- 核心信息：{model['slide_plan'][1]['claim']}

## 逐页锁定规格

{''.join(slides)}

## 可直接调用 SlideViber 的指令

请以 `report_model.json` 的 `slide_plan` 为唯一内容真相源，按以上逐页 ID 和锁定证据重绘 16:9 演示稿；先依照上述主题选择来源处理：已确认方向直接沿用，明确授权代选时默认清晰商务，否则先给候选方向和每种两页真实小样等待选择；选定后核验完整预览，不重复询问已确认偏好。只优化视觉与精简冗余表达，不改变任何数字、日期、口径、结论含义、行动含义或 evidence 对应关系；每页完整同比／环比周期只在固定元信息区声明一次，标题使用 `visual_spec.display_claim`，正文仅保留短标签和业务判断；日期、数字与单位、指标名称和英文缩写保持不可拆语义单元；evidence ID 不放在观众可见页面；核验后另存 `report-polished.pptx`，不要覆盖 `report.pptx`。
"""
    Path(output_path).write_text(output, encoding="utf-8")
