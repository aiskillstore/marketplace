from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any
from html_evidence import business_name, proof_table, scope_notes, uncovered_evidence_ids

from content_resolver import (
    project_legacy_content_refs,
    resolve_model_for_pages,
    resolve_page_content,
    validate_renderer_model,
)


CHART_COLORS = ("#2457d6", "#19a974", "#f59e0b", "#e45757")


def _fmt(value: Any, unit: str = "") -> str:
    if value is None:
        return "—"
    number = float(value)
    if unit == "%":
        return f"{number:,.2f}%"
    if unit == "x":
        return f"{number:,.2f}倍"
    if abs(number) >= 1000 or unit in {"元", "单"}:
        return f"{number:,.0f}"
    return f"{number:,.2f}"


def _fmt_compact(value: Any, unit: str = "") -> str:
    if value is None:
        return "—"
    number = float(value)
    if unit == "%":
        return f"{number:,.2f}%"
    if unit == "x":
        return f"{number:,.2f}倍"
    if abs(number) >= 100_000_000:
        return f"{number / 100_000_000:,.2f}亿"
    if abs(number) >= 10_000:
        return f"{number / 10_000:,.2f}万"
    if unit == "单" or abs(number) >= 1000:
        return f"{number:,.0f}"
    return f"{number:,.2f}"


def _comparison_basis(model: dict[str, Any]) -> str:
    configured = model.get("periods", {}).get("comparison_label")
    if configured:
        return str(configured)
    period_type = str(model.get("request", {}).get("period_type", "custom"))
    return {"monthly": "上月", "weekly": "上周"}.get(period_type, "上一完整周期")


def _comparison_text(item: dict[str, Any], basis: str) -> str:
    change = item.get("change_pct")
    if change is None:
        return f"暂无{basis}可比数据"
    if str(item.get("unit", "")) == "%":
        delta = item.get("change_delta")
        if delta is None and item.get("previous_value") is not None:
            delta = float(item["value"]) - float(item["previous_value"])
        if delta is not None:
            return f"较{basis} {float(delta):+.2f} 个百分点"
    return f"较{basis} {float(change):+.2f}%"


def _comparison_delta_text(item: dict[str, Any]) -> str:
    change = item.get("change_pct")
    if change is None:
        return "暂无可比数据"
    if str(item.get("unit", "")) == "%":
        delta = item.get("change_delta")
        if delta is None and item.get("previous_value") is not None:
            delta = float(item["value"]) - float(item["previous_value"])
        if delta is not None:
            return f"{float(delta):+.2f} 个百分点"
    return f"{float(change):+.2f}%"


def _svg_chart(chart: dict[str, Any], scope_html: str = "") -> str:
    width, height = 860, 330
    left, right, bottom = 72, 28, 54
    series = [
        {
            "name": str(item.get("name", "")),
            "values": [float(value) for value in item.get("values", [])],
        }
        for item in chart.get("series", [])
        if item.get("values")
    ]
    categories = [str(value) for value in chart.get("categories", [])]
    chart_id = html.escape(str(chart["chart_id"]), quote=True)
    title = html.escape(str(chart.get("title", "")))
    display_unit = html.escape(
        str(chart.get("display_unit") or chart.get("unit") or "数值")
    )
    scope_label = html.escape(str(chart.get("scope_label", "")))
    if not series:
        return (
            f'<figure class="chart" id="{chart_id}" data-chart-id="{chart_id}">'
            f"<h3>{title}</h3><p>暂无可绘制数据。</p></figure>"
        )

    has_legend = len(series) > 1
    top = 48 if has_legend else 24
    plot_w = width - left - right
    plot_h = height - top - bottom
    all_values = [value for item in series for value in item["values"]]
    low = min(0.0, min(all_values))
    high = max(all_values)
    span = high - low or 1.0

    def y_pos(value: float) -> float:
        return top + plot_h - (value - low) / span * plot_h

    grid_lines: list[str] = []
    for step in range(5):
        y = top + plot_h * step / 4
        value = high - span * step / 4
        grid_lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" class="gridline"/>'
            f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" class="axis-label">{html.escape(_fmt_compact(value, str(chart.get("unit", ""))))}</text>'
        )

    marks: list[str] = []
    chart_type = str(chart.get("chart_type", "line"))
    if chart_type == "bar":
        category_count = max(1, len(categories))
        series_count = max(1, len(series))
        group_w = plot_w / category_count
        bar_w = max(8.0, group_w * 0.62 / series_count)
        for category_index in range(category_count):
            group_center = left + (category_index + 0.5) * group_w
            group_start = group_center - bar_w * series_count / 2
            for series_index, item in enumerate(series):
                if category_index >= len(item["values"]):
                    continue
                value = item["values"][category_index]
                x = group_start + series_index * bar_w
                y = y_pos(value)
                bar_height = top + plot_h - y
                color = CHART_COLORS[series_index % len(CHART_COLORS)]
                marks.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_height:.1f}" '
                    f'rx="4" class="bar" fill="{color}"/>'
                )
    else:
        denominator = max(1, len(categories) - 1)
        for series_index, item in enumerate(series):
            points = [
                (left + index * plot_w / denominator, y_pos(value))
                for index, value in enumerate(item["values"])
            ]
            color = CHART_COLORS[series_index % len(CHART_COLORS)]
            point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            marks.append(
                f'<polyline points="{point_text}" class="line" style="stroke:{color}"/>'
            )
            marks.extend(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" class="point" style="fill:{color}"/>'
                for x, y in points
            )

    label_step = max(1, len(categories) // 6)
    labels: list[str] = []
    denominator = max(1, len(categories) - 1)
    category_count = max(1, len(categories))
    for index, label in enumerate(categories):
        if index % label_step and index != len(categories) - 1:
            continue
        if chart_type == "bar":
            x = left + (index + 0.5) * plot_w / category_count
        else:
            x = left + index * plot_w / denominator
        labels.append(
            f'<text x="{x:.1f}" y="{height - 22}" text-anchor="middle" class="axis-label">{html.escape(label)}</text>'
        )

    legend = ""
    if has_legend:
        legend_items = []
        for index, item in enumerate(series):
            x = left + index * 170
            color = CHART_COLORS[index % len(CHART_COLORS)]
            legend_items.append(
                f'<circle cx="{x}" cy="20" r="5" fill="{color}"/>'
                f'<text x="{x + 11}" y="24" class="axis-label">{html.escape(item["name"])}</text>'
            )
        legend = f'<g class="legend">{"".join(legend_items)}</g>'

    return f"""
<figure class="chart" id="{chart_id}" data-chart-id="{chart_id}">
  <div class="chart-heading"><h3>{title}</h3><span>{scope_label} · 单位：{display_unit}</span></div>
  {scope_html}
  <svg viewBox="0 0 {width} {height}" role="img" aria-label="{title}">
    {legend}
    {''.join(grid_lines)}
    {''.join(marks)}
    {''.join(labels)}
  </svg>
</figure>"""


def _insight_label(item: dict[str, Any]) -> str:
    if item.get("display_label"):
        return str(item["display_label"])
    signal_type = str(item.get("signal_type", ""))
    return {
        "risk": "风险",
        "opportunity": "机会",
        "seasonality": "季节性",
    }.get(signal_type, {"inference": "结构判断", "fact": "趋势信号"}.get(str(item.get("kind")), "关键判断"))


def _localized_policy(value: Any) -> str:
    return {
        "exclude": "排除并提示未完成周期",
        "include": "包含未完成周期并提示",
        "monday": "周一",
    }.get(str(value), str(value))


def _render_engineering_html(model: dict[str, Any], output_path: Path) -> None:
    """Render an engineering dossier without business-review framing."""

    source_profile = model["data_profile"]
    engineered_profile = model.get("engineered_profile", source_profile)
    engineering_qa = model.get("engineering_qa", {})
    reconciliation = engineering_qa.get("metric_reconciliation", {})
    reconciliation_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('metric_name', '')))}</td>"
        f"<td>{html.escape(str(item.get('aggregation', '')))}</td>"
        f"<td>{html.escape(_fmt(item.get('expected_total')))}</td>"
        f"<td>{html.escape(_fmt(item.get('recomputed_total')))}</td>"
        f"<td>{'通过' if item.get('status') == 'passed' else '失败'}</td>"
        "</tr>"
        for item in reconciliation.get("items", [])
    ) or '<tr><td colspan="5">本次请求未配置可复算指标。</td></tr>'
    contract_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('display_name') or item.get('name') or ''))}</td>"
        f"<td>{html.escape(str(item.get('aggregation') or ''))}</td>"
        f"<td>{html.escape(str(item.get('formula_display') or ''))}</td>"
        "</tr>"
        for item in model.get("metric_contracts", [])
    ) or '<tr><td colspan="3">未配置指标合同。</td></tr>'
    reasons = "".join(
        f"<li>{html.escape(str(reason))}</li>"
        for reason in engineering_qa.get("acceptance_reasons", [])
    )
    source_missing = sum(
        int(value or 0) for value in source_profile.get("missing_by_column", {}).values()
    )
    engineered_missing = sum(
        int(value or 0) for value in engineered_profile.get("missing_by_column", {}).values()
    )
    report_title = str(model.get("report_title") or model.get("title") or "工程回归核验")
    document = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(report_title)}</title>
<style>
:root{{--ink:#132238;--muted:#667085;--line:#dce3ec;--accent:#2457d6;--ok:#167a55;--bg:#f3f6fa;--paper:#fff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif}}
main{{max-width:1080px;margin:auto;padding:48px 28px 72px}}header,section{{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:28px;margin-bottom:20px}}
header{{background:linear-gradient(135deg,#102f67,#2457d6);color:#fff}}h1{{font-size:38px;margin:0 0 10px}}h2{{font-size:25px;margin:0 0 18px}}p,li{{line-height:1.7}}.muted{{color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}.card{{border:1px solid var(--line);border-radius:12px;padding:18px;background:#f8faff}}.card strong{{display:block;font-size:28px;margin-top:8px}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:12px 10px;border-bottom:1px solid var(--line);text-align:left}}th{{color:var(--muted);font-size:14px}}.status{{display:inline-block;padding:6px 12px;border-radius:999px;background:#e9f7f1;color:var(--ok);font-weight:700}}
@media(max-width:700px){{.grid{{grid-template-columns:1fr}}main{{padding:24px 14px}}}}
</style></head><body><main>
<header><h1>{html.escape(report_title)}</h1><p>{html.escape(str(model.get('report_subtitle') or ''))}</p><span class="status">产物生成完成 · 工程验收待完成</span></header>
<section><h2>工程核验概览</h2><p>本报告仅核验输入画像、加工结果、指标合同与复算一致性，不输出经营结论、机会判断或业务行动。</p></section>
<section><h2>源表数据概况</h2><div class="grid"><div class="card">源表行数<strong>{int(source_profile.get('row_count', 0)):,}</strong></div><div class="card">源表字段数<strong>{int(source_profile.get('column_count', 0)):,}</strong></div><div class="card">源表缺失值<strong>{source_missing:,}</strong></div><div class="card">重复行<strong>{int(source_profile.get('duplicate_rows', 0)):,}</strong></div></div></section>
<section><h2>加工后数据概况</h2><div class="grid"><div class="card">加工后行数<strong>{int(engineered_profile.get('row_count', 0)):,}</strong></div><div class="card">加工后字段数<strong>{int(engineered_profile.get('column_count', 0)):,}</strong></div><div class="card">加工后缺失值<strong>{engineered_missing:,}</strong></div><div class="card">新增字段数<strong>{max(0, int(engineered_profile.get('column_count', 0)) - int(source_profile.get('column_count', 0))):,}</strong></div></div></section>
<section><h2>指标合同核验</h2><table><thead><tr><th>指标</th><th>聚合</th><th>计算口径</th></tr></thead><tbody>{contract_rows}</tbody></table></section>
<section><h2>复算与验收状态</h2><p>指标复算：<strong>{'通过' if reconciliation.get('status') == 'passed' else '失败'}</strong>；工程验收：<strong>待完成</strong>。</p><table><thead><tr><th>指标</th><th>聚合</th><th>分析结果</th><th>独立复算</th><th>状态</th></tr></thead><tbody>{reconciliation_rows}</tbody></table><ul>{reasons}</ul></section>
<section><h2>数据范围与限制</h2><p class="muted">源表时间范围 {html.escape(str(source_profile.get('date_min', '')))} 至 {html.escape(str(source_profile.get('date_max', '')))}。当前未建立历史性能基线，运行耗时与内存仅作为本次观测；稳定性需要独立重复运行后验收。</p></section>
</main></body></html>"""
    Path(output_path).write_text(document, encoding="utf-8")


def render_html(model: dict[str, Any], output_path: Path) -> None:
    if model.get("contract_version") == "html-chapters/1":
        from html_chapter_renderer import render
        from model_validation import validate_report_model
        validate_report_model(model)
        output_path.write_text(render(model), encoding="utf-8")
        return
    model = project_legacy_content_refs(model)
    validate_renderer_model(model)
    if str(model.get("request", {}).get("analysis_intent") or "") == "engineering_regression":
        _render_engineering_html(model, output_path)
        return
    canonical_model = model
    selected_chapters = [
        item for item in model.get("analysis_chapters", [])
        if isinstance(item, dict) and item.get("selection_status") == "selected"
    ]
    pages = list(model.get("slide_plan", []))
    appendix_contracts: list[dict[str, Any]] = []
    if pages and all(isinstance(page.get("content_refs"), dict) for page in pages):
        appendix = next(
            (page for page in pages if page.get("layout_id") == "data-appendix"),
            None,
        )
        if appendix is not None:
            appendix_contracts = resolve_page_content(model, appendix)["metric_contracts"]
        model = resolve_model_for_pages(model)
    else:
        # Direct legacy HTML fixtures have no page plan to project.  Keep their
        # existing derived-metric disclosure while new models use appendix refs.
        appendix_contracts = [
            contract for contract in model.get("metric_contracts", [])
            if contract.get("source_kind") == "derived"
        ]
    # Chapter refs are an explicit HTML contract, independent of the deferred
    # slide layout. Include only selected chapter records, never raw leftovers.
    model = dict(model)
    for collection, ref_key, id_key, label in (
        ("charts", "chart_ids", "chart_id", "图表"),
        ("actions", "action_ids", "action_id", "行动"),
    ):
        available = {str(item.get(id_key) or ""): item for item in canonical_model.get(collection, [])}
        visible = list(model.get(collection, []))
        visible_ids = {str(item.get(id_key) or "") for item in visible}
        for chapter in selected_chapters:
            for ref in chapter.get(ref_key, []):
                ref = str(ref)
                if ref not in available:
                    raise ValueError(f"章节 {chapter.get('chapter_id')} 引用的{label}不存在：{ref}")
                if ref not in visible_ids:
                    visible.append(available[ref])
                    visible_ids.add(ref)
        model[collection] = visible
    # A supported time series remains useful context even when it cannot answer
    # a deeper operating question. Reuse its canonical payload without promoting
    # the question, inventing a chart, or changing its evidence scope.
    baseline_trend = next((chart for chart in canonical_model.get('charts', [])
                           if chart.get('chart_type') == 'line' and chart.get('evidence_ids')
                           and all(canonical_model.get('evidence_index', {}).get(ref, {}).get('kind') == 'metric_trend'
                                   for ref in chart['evidence_ids'])), None)
    if baseline_trend and not any(c['chart_id'] == baseline_trend['chart_id'] for c in model['charts']):
        model['charts'] = [baseline_trend, *model['charts']]
    profile = model["data_profile"]
    request = model["request"]
    period_overview = model.get("period_overview", {})
    latest_snapshot = model.get("latest_snapshot", {})
    basis = str(latest_snapshot.get("comparison_label") or _comparison_basis(model))
    snapshot_items = list(latest_snapshot.get("kpis") or model["kpis"])
    snapshot_has_comparison = any(
        item.get("previous_value") is not None
        or item.get("change_pct") is not None
        or item.get("change_delta") is not None
        for item in snapshot_items
    )
    snapshot_scope_copy = (
        f"{latest_snapshot.get('label', '')}，较{latest_snapshot.get('comparison_label', basis)}"
        if snapshot_has_comparison
        else f"{latest_snapshot.get('label', '')} · 暂无前一完整周期"
    )
    latest_scope_heading = {
        "monthly": "最新完整月表现",
        "weekly": "最新完整周表现",
        "custom": "最新完整周期表现",
    }.get(str(request.get("period_type", "")), "最新完整周期表现")
    report_title = str(model.get("report_title") or model.get("title") or "数据分析简报")
    report_subtitle = str(model.get("report_subtitle") or "")
    executive_summary = model.get("executive_summary", {})
    key_conclusions = list(executive_summary.get("key_conclusions", []))
    priority_actions = list(executive_summary.get("priority_actions", []))
    contract_by_name = {
        str(contract["name"]): contract for contract in model.get("metric_contracts", [])
    }

    def render_scope(record: dict) -> str:
        notes = scope_notes(canonical_model, record)
        if not notes:
            return ''
        summary = '；'.join(notes[0].split('；')[:2])
        summary = re.sub(r'(\d{4}-\d{2})(?:、\d{4}-\d{2})*、(\d{4}-\d{2})', r'\1 至 \2', summary)
        return (f'<details class="scope-details"><summary>范围：{html.escape(summary)} · 查看口径</summary>'
                + ''.join(f'<p class="scope-disclosure">范围：{html.escape(note)}</p>' for note in notes) + '</details>')

    summary_chapters = {c.get("chapter_id"): c for c in selected_chapters}
    conclusion_scopes = executive_summary.get("key_conclusion_chapter_ids", [])
    conclusion_items = []
    for index, text in enumerate(key_conclusions):
        refs = conclusion_scopes[index] if index < len(conclusion_scopes) else []
        refs = [refs] if isinstance(refs, str) else refs
        scope = ''.join(render_scope(summary_chapters[ref]) for ref in refs if ref in summary_chapters)
        conclusion_items.append(f'<li>{html.escape(str(text))}{scope}</li>')

    def summary_list(items: list[Any]) -> str:
        return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)

    summary_rows = f"""
<div class="summary-row">
  <span class="summary-label">核心结论</span>
  <ul>{''.join(conclusion_items)}</ul>
</div>
<div class="summary-row">
  <span class="summary-label">下一步重点</span>
  <ul>{summary_list(priority_actions)}</ul>
</div>"""

    def render_kpi_cards(items: list[dict[str, Any]], *, show_comparison: bool) -> str:
        cards: list[str] = []
        for item in items:
            contract = contract_by_name.get(str(item["name"]), {})
            metric_note = ""
            if contract.get("source_kind") == "derived" and not show_comparison:
                metric_note = (
                    f'<small class="metric-note">计算口径：'
                    f'{html.escape(str(contract.get("formula_display", "")))}</small>'
                )
            comparison = (
                f'<span>{html.escape(_comparison_delta_text(item))}</span>'
                if show_comparison
                and (
                    item.get("previous_value") is not None
                    or item.get("change_pct") is not None
                    or item.get("change_delta") is not None
                )
                else ""
            )
            cards.append(f"""
<article class="kpi">
  <p>{html.escape(business_name(canonical_model, item.get('display_name') or item['name']))}</p>
  <strong>{html.escape(_fmt(item.get('value'), str(item.get('unit', ''))))}</strong>
  {comparison}
  {metric_note}
</article>""")
        return "".join(cards)

    overview_kpi_cards = render_kpi_cards(
        list(period_overview.get("kpis") or model["kpis"]),
        show_comparison=False,
    )
    snapshot_kpi_cards = render_kpi_cards(
        snapshot_items,
        show_comparison=True,
    )
    chapter_chart_ids = {
        str(value) for chapter in selected_chapters for value in chapter.get("chart_ids", [])
    }
    chart_blocks = "".join(
        _svg_chart(chart, render_scope(chart)) for chart in model["charts"]
        if str(chart.get("chart_id")) not in chapter_chart_ids
    ) or '<p class="footnote">证明图表已随对应业务问题展示，请结合章节判断阅读。</p>'

    lever_items: list[str] = []
    for lever in model.get("levers", []):
        metric_rows = "".join(
            f"""
<div class="lever-metric">
  <span>{html.escape(str(metric.get('display_name') or metric['name']))}</span>
  <strong>{html.escape(_fmt_compact(metric.get('value'), str(metric.get('unit', ''))))}</strong>
  <small>{html.escape(_comparison_text(metric, basis))}</small>
</div>"""
            for metric in lever.get("items", [])
        )
        takeaway = str(lever.get("takeaway") or lever.get("headline") or "")
        lever_items.append(
            f"""
<article class="lever">
  <span class="lever-label">{html.escape(str(lever['label']))}</span>
  <div class="lever-metrics">{metric_rows}</div>
  <p class="lever-takeaway">{html.escape(takeaway)}</p>
</article>"""
        )

    selection = model.get("value_selection", {})
    allowed_insight_ids = {
        str(item.get("insight_id") or "")
        for item in (selection.get("featured", []) if isinstance(selection, dict) else [])
        if isinstance(item, dict)
    }
    if not allowed_insight_ids and (not isinstance(selection, dict) or not selection):
        # Legacy direct-render fixtures have no value-selection payload, but
        # their explicit featured IDs remain the sole visible-insight contract.
        allowed_insight_ids = {str(value) for value in model.get("featured_insight_ids", [])}
    visible_insights = [
        item for item in model.get("insights", [])
        if str(item.get("insight_id") or "") in allowed_insight_ids
    ]
    insight_items = "".join(
        f"""
<article class="insight{' featured' if index == 0 else ''}">
  <span class="eyebrow">{html.escape(_insight_label(item))}</span>
  <h3>{html.escape(str(item.get('headline') or item['statement']))}</h3>
  {f"<p>{html.escape(str(item.get('implication') or ''))}</p>" if str(item.get('implication') or '').strip() else ''}
</article>"""
        for index, item in enumerate(visible_insights)
    )

    actions_by_id = {
        str(item.get("action_id") or ""): item
        for item in model.get("actions", []) if isinstance(item, dict)
    }
    charts_by_id = {
        str(item.get("chart_id") or ""): item
        for item in model.get("charts", []) if isinstance(item, dict)
    }
    action_anchors = {
        str(item.get("action_id") or ""): f"action-plan-{index}"
        for index, item in enumerate(model.get("actions", []), start=1)
    }
    rendered_charts: set[str] = set()
    proof_anchors: dict[str, str] = {}
    chapter_items: list[str] = []
    for index, chapter in enumerate(selected_chapters, start=1):
        proofs: list[str] = []
        for chart_id in dict.fromkeys(str(value) for value in chapter.get("chart_ids", [])):
            chart = charts_by_id[chart_id]
            if chart_id in rendered_charts:
                proofs.append(
                    f'<p class="chapter-proof-link">共同证据：<a href="#{html.escape(chart_id, quote=True)}">'
                    f'{html.escape(str(chart.get("title") or "查看图表"))}</a></p>'
                )
            else:
                proofs.append(_svg_chart(chart, render_scope(chart)))
                rendered_charts.add(chart_id)
        for evidence_id in uncovered_evidence_ids(canonical_model, chapter):
            if evidence_id in proof_anchors:
                proofs.append(f'<p class="chapter-proof-link">共同证据：<a href="#{proof_anchors[evidence_id]}">查看前文数值证明表</a></p>')
                continue
            table = proof_table(canonical_model, evidence_id)
            anchor = f"evidence-proof-{len(proof_anchors) + 1}"
            proof_anchors[evidence_id] = anchor
            headers = ''.join(f'<th scope="col">{html.escape(value)}</th>' for value in table["headers"])
            rows = ''.join('<tr>' + ''.join(f'<td>{html.escape(value)}</td>' for value in row) + '</tr>' for row in table["rows"])
            proofs.append(f'<div class="proof-block"><div class="evidence-table-wrap" tabindex="0" role="region" aria-label="数值证明表">'
                          f'<table class="evidence-table" id="{anchor}"><caption>数值证明</caption>'
                          f'<thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>'
                          + render_scope(canonical_model["evidence_index"][evidence_id]) + '</div>')
            if table.get("history"):
                history = table["history"]
                headings = ''.join(f'<th scope="col">{html.escape(value)}</th>' for value in history["headers"])
                cells = ''.join('<tr>' + ''.join(f'<td>{html.escape(value)}</td>' for value in row) + '</tr>' for row in history["rows"])
                proofs.append(f'<div class="evidence-table-wrap" tabindex="0" role="region" aria-label="集中度逐月证明">'
                    f'<table class="evidence-table" id="{anchor}-history"><caption>集中度逐月证明</caption>'
                    f'<thead><tr>{headings}</tr></thead><tbody>{cells}</tbody></table></div>')
        chapter_actions = [
            actions_by_id[str(action_id)]
            for action_id in chapter.get("action_ids", [])
            if str(action_id) in actions_by_id
        ]
        action_lines = "".join(
            f'<li><a href="#{action_anchors[str(item.get("action_id") or "")]}">'
            f"{html.escape(str(item.get('headline') or item.get('text') or ''))}</a>"
            f"<small>成功信号：{html.escape(str(item.get('success_signal') or item.get('verification_signal') or ''))}</small></li>"
            for item in chapter_actions
        )
        limitations = "".join(
            f"<li>{html.escape(str(value))}</li>"
            for value in chapter.get("limitations", []) if str(value).strip()
        )
        chapter_items.append(f"""
<article class="analysis-chapter" data-chapter-position="{index}" id="chapter-{index}">
  <p class="chapter-question">{html.escape(str(chapter.get('decision_question') or ''))}</p>
  <h3>{html.escape(str(chapter.get('report_language') or chapter.get('judgement') or ''))}</h3>
  <p class="chapter-implication">经营含义：{html.escape(str(chapter.get('operating_implication') or ''))}</p>
  {render_scope(chapter)}
  {f'<div class="chapter-actions"><strong>对应行动</strong><ul>{action_lines}</ul></div>' if action_lines else ''}
  {f'<div class="chapter-limitations"><strong>边界</strong><ul>{limitations}</ul></div>' if limitations else ''}
  <div class="proof-grid">{''.join(proofs)}</div>
</article>""")
    decision_content = (
        f'<div class="chapter-stack">{"".join(chapter_items)}</div>'
        if chapter_items else f'<div class="insight-grid">{insight_items}</div>'
    )

    action_items: list[str] = []
    for index, item in enumerate(model["actions"], start=1):
        headline = str(item.get("headline") or item["text"])
        body = str(item.get("text", "")) if headline != str(item.get("text", "")) else ""
        body_html = f"<p>{html.escape(body)}</p>" if body else ""
        details: list[str] = []
        for field, label in (("target", "对象"), ("basis", "依据"), ("rationale", "机制与假设")):
            if str(item.get(field) or "").strip():
                details.append(f'<p><strong>{label}：</strong>{html.escape(str(item[field]))}</p>')
        for field, label, tag, css_class in (
            ("steps", "执行步骤", "ol", "action-steps"),
            ("guardrails", "止损与约束", "ul", "action-guardrails"),
            ("limitations", "适用边界", "ul", "action-limitations"),
        ):
            values = [str(value) for value in item.get(field, []) if str(value).strip()]
            if values:
                details.append(
                    f'<div><strong>{label}</strong><{tag} class="{css_class}">'
                    + "".join(f'<li>{html.escape(value)}</li>' for value in values)
                    + f'</{tag}></div>'
                )
        action_items.append(
            f"""
<article class="action" id="action-plan-{index}" data-action-id="{html.escape(str(item.get('action_id') or ''), quote=True)}">
  <span class="priority">P{item.get('priority', index)}</span>
  <div><h3>{html.escape(headline)}</h3>
  {body_html}
  {render_scope(item)}
  {''.join(details)}
  <p class="verification">成功信号：{html.escape(str(item.get('success_signal') or item.get('verification_signal') or ''))}</p></div>
</article>"""
        )

    missing_total = sum(
        int(value or 0) for value in profile.get("missing_by_column", {}).values()
    )
    period_type = str(request.get("period_type", "custom"))
    comparison_copy = {
        "monthly": "最近两个完整月",
        "weekly": "最近两个完整周",
    }.get(period_type, "最近两个完整周期")
    weekly_copy = (
        f"；每周以{_localized_policy(request.get('week_start'))}为起点"
        if period_type == "weekly"
        else ""
    )
    contract_definition_items = "".join(
        f"<li><strong>{html.escape(str(contract['display_name']))}</strong>："
        f"{html.escape(str(contract['definition']))} 计算口径："
        f"{html.escape(str(contract['formula_display']))}</li>"
        for contract in appendix_contracts
    )
    contract_definition_block = (
        f'<div class="metric-definitions"><h3>指标口径</h3><ul>{contract_definition_items}</ul></div>'
        if contract_definition_items
        else ""
    )
    selection_meta = model.get("narrative_selection", {})
    selection_meta_block = (
        f'<section><h2>决策展示状态</h2><p class="footnote">{html.escape(str(selection_meta.get("reason") or ""))}</p></section>'
        if selection_meta.get("status") == "no_findings_selected" else ""
    )
    if selection_meta.get("status") == "partial_coverage":
        pending_blocks = []
        for item in selection_meta.get("unresolved_questions", []):
            pending_blocks.append(
                '<article class="question-disposition">'
                f'<h3>{html.escape(str(item["business_question"]))}</h3>'
                f'<p>{html.escape(str(item["reason"]))}</p>'
                f'<p>后续处理：{html.escape(str(item["next_step"]))}</p></article>'
            )
        selection_meta_block = ('<section class="unresolved-questions"><h2>尚未形成核心判断的问题</h2>'
                                f'<p>{html.escape(str(selection_meta["reason"]))}</p>{"".join(pending_blocks)}</section>')
    insight_section = f'<section id="insights"><h2>关键洞察</h2>{decision_content}</section>'
    chapter_navigation = ''.join(f'<a href="#chapter-{i}">洞察 {i}</a>' for i, _ in enumerate(selected_chapters, 1))

    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(report_title)}</title>
  <style>
    :root{{--ink:#132238;--muted:#667085;--line:#dce3ec;--accent:#2457d6;--accent2:#19a974;--risk:#d94f4f;--bg:#f3f6fa;--paper:#fff;}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif}}
    main{{max-width:1120px;margin:0 auto;padding:52px 28px 80px}} h1{{font-size:42px;line-height:1.24;margin:8px 0 10px;max-width:920px}}
    h2{{font-size:28px;margin:0 0 20px}} h3{{line-height:1.45}} .hero{{background:linear-gradient(135deg,#102f67,#2457d6);color:white;border-radius:24px;padding:42px;margin-bottom:24px}}
    .subtitle{{font-size:16px;opacity:.82;margin:0 0 26px}} .summary-row{{display:grid;grid-template-columns:112px 1fr;gap:18px;padding:14px 0;border-top:1px solid rgba(255,255,255,.2)}} .summary-label{{font-size:15px;font-weight:700;color:#dfe9ff}} .summary-row ul{{margin:0;padding-left:20px}} .summary-row li{{font-size:16px;line-height:1.65;margin:0 0 5px}} section{{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:28px;margin-top:22px}}
    .scope-head{{display:flex;align-items:baseline;justify-content:space-between;gap:18px;margin:4px 0 14px}} .scope-head h3{{font-size:20px;margin:0}} .scope-head p{{margin:0;color:var(--muted);font-size:14px}} .scope-head.latest{{margin-top:30px;padding-top:24px;border-top:1px solid var(--line)}}
    .kpi-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}} .kpi{{border-top:4px solid var(--accent);background:#f8faff;border-radius:12px;padding:20px}}
    .kpi p{{margin:0;color:var(--muted)}} .kpi strong{{display:block;font-size:29px;margin:10px 0 7px}} .kpi span{{display:block;color:var(--muted);font-size:14px}} .kpi .metric-note{{display:block;color:var(--muted);font-size:12px;margin-top:8px}}
    .chart{{margin:28px 0 0;padding:20px;border:1px solid var(--line);border-radius:16px}} .chart:first-of-type{{margin-top:0}} .chart-heading{{display:flex;align-items:baseline;justify-content:space-between;gap:18px}} .chart-heading h3{{margin:0}} .chart-heading span{{color:var(--muted);font-size:14px;white-space:nowrap}} .chart svg{{width:100%;height:auto;background:#fff}} .gridline{{stroke:#e5e9f0;stroke-width:1}} .axis-label{{fill:#667085;font-size:12px}}
    .line{{fill:none;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}} .bar{{shape-rendering:geometricPrecision}}
    .lever-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}} .lever{{min-height:210px;padding:22px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(145deg,#fff,#f6f8fc)}}
    .lever-label{{display:inline-block;padding:5px 10px;border-radius:999px;background:#eaf0ff;color:#1846b2;font-size:13px;font-weight:700}} .lever-metrics{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:16px 0}}
    .lever-metric{{padding:12px;background:#fff;border:1px solid #e8edf4;border-radius:10px}} .lever-metric span,.lever-metric small{{display:block;color:var(--muted);font-size:13px}} .lever-metric strong{{display:block;font-size:21px;margin:5px 0}} .lever-takeaway{{margin:4px 0 0;line-height:1.65;color:#33445d}}
    .insight-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}} .insight{{padding:20px;border-left:5px solid var(--accent2);background:#f6fffb;border-radius:10px}} .insight.featured{{grid-column:1/-1;background:#eefbf6}}
    .eyebrow{{font-size:13px;color:#087d57;font-weight:700}} .insight h3{{font-size:19px;margin:10px 0}} .insight p{{line-height:1.7;color:#46556b;margin:0}}
    .scope-details{{font-size:14px;line-height:1.65;margin:10px 0;overflow-wrap:anywhere}} .scope-details summary{{cursor:pointer;padding:8px 0}} .scope-details summary:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}} .scope-details p{{margin:8px 0}} .hero .scope-details{{color:#e3ecff}}
    .chapter-stack{{display:grid;gap:36px}} .analysis-chapter{{min-width:0;padding:0 0 28px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}} .analysis-chapter:last-child{{border-bottom:0;padding-bottom:0}}
    .question-disposition{{max-width:75ch;overflow-wrap:anywhere;margin-top:24px}} .question-disposition h3{{font-size:18px;margin:0 0 8px}} .question-disposition p{{line-height:1.7;margin:8px 0}}
    .chapter-question{{margin:0 0 8px;color:var(--muted)}} .analysis-chapter h3{{font-size:22px;margin:0 0 12px}} .chapter-implication,.chapter-proof-link{{line-height:1.7;color:#33445d}} .analysis-chapter .chart h3{{font-size:18px}} .analysis-chapter p{{max-width:75ch}}
    .chapter-actions,.chapter-limitations{{margin-top:14px;padding-top:12px;border-top:1px solid var(--line)}} .chapter-actions ul,.chapter-limitations ul{{margin:8px 0 0;padding-left:20px}} .chapter-actions li,.chapter-limitations li{{line-height:1.65;margin-bottom:6px}} .chapter-actions small{{display:block;color:#176b52}}
    .scope-disclosure{{font-size:14px;line-height:1.65;color:#46556b;overflow-wrap:anywhere;margin:8px 0 16px}} .summary-row .scope-disclosure{{color:inherit;opacity:1;font-size:14px}}
    .evidence-table-wrap{{max-width:100%;overflow-x:auto;margin:20px 0;scroll-margin-top:24px}} .evidence-table-wrap:focus-visible{{outline:2px solid var(--accent);outline-offset:4px}}
    .evidence-table{{width:100%;border-collapse:collapse;font-size:16px;font-variant-numeric:tabular-nums}} .evidence-table caption{{text-align:left;font-weight:700;margin-bottom:10px}}
    .evidence-table th,.evidence-table td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--line);overflow-wrap:anywhere;min-width:8ch}} .evidence-table th{{color:#33445d;background:#f3f6fa}}
    @media print{{.evidence-table-wrap{{overflow:visible}}.evidence-table thead{{display:table-header-group}}.evidence-table tr{{break-inside:avoid}}}}
    .action{{display:flex;gap:16px;padding:20px 0;border-bottom:1px solid var(--line)}} .action:last-child{{border-bottom:0}} .priority{{flex:0 0 44px;height:44px;border-radius:50%;background:var(--accent);color:#fff;display:grid;place-items:center;font-weight:700}}
    .action h3{{font-size:19px;margin:0 0 8px}} .action p{{margin:0 0 8px;line-height:1.65;color:#46556b}} .action .verification{{color:#176b52}} .footnote{{line-height:1.8;color:var(--muted);margin:0}} .metric-definitions{{margin-top:20px;padding-top:18px;border-top:1px solid var(--line)}} .metric-definitions h3{{font-size:18px;margin:0 0 10px}} .metric-definitions li{{line-height:1.7;margin-bottom:6px;color:#46556b}}
    .action>div{{min-width:0;max-width:75ch;overflow-wrap:anywhere}} .action ol,.action ul{{padding-left:24px;margin:8px 0 16px}} .action li{{line-height:1.7;margin-bottom:6px}} a{{color:#1846b2;text-underline-offset:3px}} a:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}} .chart,.action{{scroll-margin-top:20px}}
    @media(max-width:900px){{.kpi-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
    @media(max-width:620px){{main{{padding:24px 14px 48px}}.hero{{padding:28px 22px}}h1{{font-size:32px}}section{{padding:20px}}.summary-row{{grid-template-columns:1fr;gap:6px}}.kpi-grid,.lever-grid,.insight-grid{{grid-template-columns:1fr}}.insight.featured{{grid-column:auto}}.lever-metrics{{grid-template-columns:1fr}}}}
    @media(max-width:620px){{.chart{{padding:12px}}.chart-heading,.scope-head{{flex-direction:column;gap:8px}}.chart-heading span{{white-space:normal}}.chart svg{{min-width:540px}}.chart{{overflow-x:auto}}.action{{gap:10px}}}}
    .report-nav{{position:fixed;top:0;left:0;right:0;z-index:20;display:flex;gap:8px;align-items:center;padding:9px max(14px,calc((100vw - 1064px)/2));height:56px;background:#fff;border-bottom:1px solid var(--line);overflow-x:auto;white-space:nowrap}}
    .report-nav a{{padding:7px 10px;border-radius:6px;text-decoration:none;font-size:14px;flex-shrink:0}} .report-nav a:hover{{background:#eaf0ff}}
    main{{padding-top:84px}} [id]{{scroll-margin-top:76px}} .proof-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;margin-top:24px;align-items:start}} .proof-block{{min-width:0;border-top:1px solid var(--line)}} .proof-grid>.chart,.proof-grid>.chapter-proof-link,.proof-grid>.evidence-table-wrap{{grid-column:1/-1}} .proof-block .evidence-table-wrap{{margin-bottom:8px}} .proof-block .evidence-table td,.proof-block .evidence-table th{{padding:10px 8px}}
    @media(max-width:700px){{.proof-grid{{grid-template-columns:1fr}}main{{padding-top:76px}}}}
    @media print{{.report-nav{{display:none}}main{{padding-top:0}}.proof-grid{{display:block}}.proof-block{{break-inside:avoid}}}}
  </style>
</head>
<body><nav class="report-nav" aria-label="报告导航"><a href="#summary">摘要</a>{chapter_navigation}<a href="#metrics">指标</a><a href="#trends">趋势</a><a href="#actions">行动</a><a href="#definitions">口径</a></nav><main>
  <header class="hero" id="summary">
    <h1>{html.escape(report_title)}</h1>
    <p class="subtitle">{html.escape(report_subtitle)}</p>
    {summary_rows}
  </header>
  {insight_section if selected_chapters else ''}
  <section id="metrics"><h2>核心指标</h2>
    <div class="scope-head"><h3>分析期经营概览</h3><p>{html.escape(str(period_overview.get('label', '')))} · 累计／整体口径</p></div>
    <div class="kpi-grid">{overview_kpi_cards}</div>
    <div class="scope-head latest"><h3>{latest_scope_heading}</h3><p>{html.escape(snapshot_scope_copy)}</p></div>
    <div class="kpi-grid">{snapshot_kpi_cards}</div>
  </section>
  <section id="trends"><h2>关键趋势与结构</h2>{chart_blocks}</section>
  {('<section><h2>经营表现拆解</h2><div class="lever-grid">' + ''.join(lever_items) + '</div></section>') if lever_items else ''}
  {insight_section if not selected_chapters else ''}
  <section id="actions"><h2>关键决策建议</h2>{''.join(action_items)}</section>
  {selection_meta_block}
  <section id="definitions"><h2>数据口径与质量</h2><p class="footnote">数据范围 {html.escape(str(profile['date_min']))} 至 {html.escape(str(profile['date_max']))}，共 {int(profile['row_count']):,} 行。比较口径使用{comparison_copy}，百分比指标以百分点展示变化，其他指标以相对变化率展示。重复行 {int(profile.get('duplicate_rows', 0)):,} 条，缺失值 {missing_total:,} 个；未完成周期按“{html.escape(_localized_policy(request.get('incomplete_period_policy')))}”处理{weekly_copy}。</p>{contract_definition_block}</section>
</main></body></html>"""
    Path(output_path).write_text(document, encoding="utf-8")
