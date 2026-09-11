"""Frozen HTML chapters -> separate, evidence-bound presentation content.

No input spreadsheet reads, narrative invention, source-model mutation or legacy
PPT contract coercion. Both presentation consumers must validate against source.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from canonical_json import canonical_sha256
from chart_contract import project_chart
from html_analysis import binding, check_binding, resolve_text, sealed, verify, write_new
from model_validation import validate_report_model
from ppt_theme_selection import validate_selection, slideviber_theme
from presentation_story import validate_story, page_navigation, overview_blocks, visual_role

VERSION = "chapter-presentation/1"


def split_text(text: str, limit: int = 110) -> list[str]:
    """Lossless capacity split; concatenation must equal the original content."""
    if not isinstance(text, str):
        raise ValueError("presentation content must be text")
    chunks = []
    while len(text) > limit:
        ends = [text.rfind(mark, limit // 2, limit) for mark in "。；，、 \n"]
        cut = max(ends) + 1
        if cut < limit // 2:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:]
    if text:
        chunks.append(text)
    return chunks


def validate_source(model: dict) -> None:
    if model.get("contract_version") != "html-chapters/1":
        raise ValueError("explicit html-chapters/1 source required; use legacy path for old models")
    validate_report_model(model)
    snapshot = model["snapshot"]
    check_binding(snapshot, model["binding"])
    expected = {}
    chapter_ids = set()
    for chapter in model["chapters"]:
        if chapter["id"] in chapter_ids:
            raise ValueError("duplicate chapter id")
        chapter_ids.add(chapter["id"])
        scopes = {eid: canonical_sha256(snapshot["evidence"][eid]["scope"])
                  for eid in chapter["evidence_ids"]}
        if scopes != chapter["scope_bindings"]:
            raise ValueError("chapter scope binding mismatch")
        for chart in chapter["charts"]:
            if chart.get("version") != "chart-spec/1":
                raise ValueError("presentation requires explicit shared chart-spec/1")
            if chart["evidence_id"] not in chapter["evidence_ids"]:
                raise ValueError("chart outside owning chapter evidence")
            view = project_chart(chart, snapshot["evidence"][chart["evidence_id"]])
            if chart["id"] in expected:
                raise ValueError("duplicate chart id")
            expected[chart["id"]] = {**view, "chapter_id": chapter["id"],
                "scope_sha256": scopes[chart["evidence_id"]], "snapshot_binding": binding(snapshot)}
    if model.get("chart_views", {}) != expected:
        raise ValueError("frozen chart projection differs from source evidence")
    for item in [*model["summary"], *model["actions"]]:
        if not item["chapter_ids"] or not set(item["chapter_ids"]) <= chapter_ids:
            raise ValueError("summary/action chapter binding mismatch")


def project(model: dict, selection: dict, story: dict | None = None) -> dict:
    validate_source(model)
    intent = validate_story(model, story)
    themes = intent['themes'] if intent else None
    config = validate_selection(selection)
    if selection.get("source_model_sha256") != model["sha256"]:
        raise ValueError("theme/source model binding mismatch")
    # The installed legacy renderer still has its own independent limitations.
    # This consumer currently validates the familiar business layouts only.
    if config["layout"] == "editorial":
        raise ValueError("editorial full chapter deck layout is not yet validated")
    snapshot = model["snapshot"]
    request = snapshot["request"]
    trend = snapshot["evidence"].get("trend", {})
    periods = [str(row["__period"]) for row in trend.get("rows", []) if "__period" in row]
    period = f"{periods[0]} 至 {periods[-1]}" if periods else "期间见数据口径"
    slides = []

    def add(kind, title, blocks=(), *, refs=(), chart_id=None, owner=None, display_period=None,
            chapter_ids=(), purpose=None, action_number=None):
        if not title or len(title) > 88:
            raise ValueError("presentation title capacity exceeded; revise upstream bound wording")
        slide = {"id": f"page-{len(slides)+1:03d}", "kind": kind, "title": title,
                 "blocks": list(blocks), "evidence_ids": sorted(set(refs)),
                 "chart_id": chart_id, "owner": owner, "period": display_period or period}
        phase = {'cover':'开场','summary':'开场','overview':'全局背景','action':'行动安排','method':'附录'}.get(kind,'判断展开')
        slide['navigation'] = page_navigation(model, chapter_ids, purpose or {'cover':'汇报目标','summary':'核心判断','overview':'经营基本盘','chart':'图表依据','chapter':'证据与判断','method':'指标口径'}.get(kind,'执行安排'), themes=themes, action_number=action_number, phase=phase)
        if intent and intent['visual'] is not None:
            slide['visual'] = visual_role(slide,intent['visual'],model.get('chart_views',{}))
        slide["content_sha256"] = canonical_sha256(slide)
        slides.append(slide)

    def text_pages(kind, title, fields, refs, owner, *, chapter_ids=(), purpose=None, action_number=None):
        blocks = []
        for label, text in fields:
            for index, chunk in enumerate(split_text(text)):
                blocks.append({"label": label + ("（续）" if index else ""), "text": chunk})
        for start in range(0, len(blocks), 3):
            add(kind, title + ('（续）' if start else ''), blocks[start:start+3], refs=refs, owner=owner,
                chapter_ids=chapter_ids, purpose=purpose, action_number=action_number)

    add("cover", model["title"], [{"label": "分析期间", "text": period},
        {"label": "汇报目标", "text": request["objective"]}])
    if model["summary"]:
        refs = set()
        for item in model["summary"]:
            refs.update(e for c in model["chapters"] if c["id"] in item["chapter_ids"] for e in c["evidence_ids"])
        blocks = []
        for index,item in enumerate(model['summary']):
            for chunk_index,chunk in enumerate(split_text(item['text'])):
                blocks.append({'label':item.get('headline','判断')+('（续）' if chunk_index else ''), 'text':chunk,'conclusion_number':index+1})
        for start in range(0,len(blocks),3):
            add('summary','核心判断'+('（续）' if start else ''),blocks[start:start+3],refs=refs,owner='summary')
    overview = overview_blocks(model)
    if intent and intent['visual'] is not None:
        # Source-declared metric order, not magnitude or assumed importance.
        names = [m['name'] for m in snapshot['metrics']]
        overview.sort(key=lambda b:names.index(b['evidence_cell']['column']) if b['evidence_cell']['column'] in names else len(names))
    overview_periods = snapshot['evidence']['overview']['scope']['periods']
    overview_period = f'{overview_periods[0]} 至 {overview_periods[-1]}'
    for start in range(0,len(overview),6):
        add('overview','分析期总体概况'+('（续）' if start else ''),overview[start:start+6],refs=['overview'],owner='overview',display_period=overview_period)
    chart_order = []
    for chapter in model["chapters"]:
        text_pages("chapter", chapter["title"], [("证据与判断", chapter["body"]),
            ("业务含义", chapter["meaning"]), ("适用边界", chapter["limitations"])],
            chapter["evidence_ids"], chapter["id"], chapter_ids=[chapter['id']])
        for chart in chapter["charts"]:
            view = model["chart_views"][chart["id"]]
            title = intent['chart_titles'][chart['id']] if intent else resolve_text(chart["title"], snapshot, [chart["evidence_id"]])
            # Numeric content comes exclusively from the verified projection.
            chart_scope = view["scope"]
            chart_periods = chart_scope["periods"]
            chart_period = f"{chart_periods[0]} 至 {chart_periods[-1]}"
            filters = "；".join(f"{item['field']}：{'、'.join(map(str, item['values']))}" for item in chart_scope["filters"])
            scope_label = f"{chart_period}；{'全体观测' if not filters else filters}；{chart_scope['rows']}条记录"
            add("chart", title, [{"label": "范围", "text": scope_label}],
                refs=[chart["evidence_id"]], chart_id=chart["id"], owner=chapter["id"], display_period=chart_period,
                chapter_ids=[chapter['id']])
            chart_order.append(chart["id"])
    for number, action in enumerate(model["actions"], 1):
        refs = {e for c in model["chapters"] if c["id"] in action["chapter_ids"] for e in c["evidence_ids"]}
        text_pages("action", action["title"], [("行动对象", action["target"]), ("依据", action["basis"]),
            ("执行步骤", action["steps"])], refs, f"action-{number}",chapter_ids=action['chapter_ids'],purpose='执行安排',action_number=number)
        text_pages("action", action["title"]+'：验证与边界', [("验证信号", action["success_signal"]),
            ("行动边界", action["boundary"])], refs, f"action-{number}",chapter_ids=action['chapter_ids'],purpose='验证与边界',action_number=number)
        if action.get('suggested_role'):
            text_pages('action', action['title'], [('建议协同角色', action['suggested_role'])], refs, f'action-{number}-role',chapter_ids=action['chapter_ids'],purpose='建议协同',action_number=number)
    policies = {"exclude": "排除未完成周期", "keep": "保留并提示未完成周期"}
    fields = [("期间", period), ("完整性处理", policies.get(request.get("incomplete_period_policy", "exclude"), "按已确认周期合同处理"))]
    text_pages('method','数据范围与期间',fields,['overview'],'method',purpose='数据范围')
    fields = [(m.get("display_name") or m["name"],
        (f"{m['numerator']} 合计 ÷ {m['denominator']} 合计 × {m.get('scale', 1)}"
         if m["aggregation"] == "ratio" else f"{m['name']}：{m['aggregation']}") + f"；单位 {m['unit']}")
        for m in snapshot["metrics"]]
    text_pages('method','指标定义',fields,['overview'],'method',purpose='指标定义')
    fields = [(m.get("display_name") or m["name"],
        "单行分母为零仍进入分子与分母合计；仅排除缺失配对，合计分母为零时不计算"
        if m.get("zero_denominator_policy") == "include_in_totals"
        else "沿用已确认旧口径：排除单行分母为零的记录")
        for m in snapshot["metrics"] if m["aggregation"] == "ratio"]
    fields += [("数据提醒", str(w)) for w in snapshot.get("warnings", [])]
    text_pages("method", "分母处理与数据提醒", fields, ["overview"], "method",purpose='分母与数据提醒')
    if not slides or len(slides) > 80:
        raise ValueError("presentation exceeds supported capacity")
    return sealed({"schema": VERSION, "source_model_sha256": model["sha256"],
        "source_snapshot_sha256": snapshot["sha256"], "source_binding": model["binding"],
        "selection": copy.deepcopy(selection), "story":copy.deepcopy(story), "slides": slides, "chart_order": chart_order,
        "chart_views": copy.deepcopy(model.get("chart_views", {})),
        "scope_records": {e: copy.deepcopy(snapshot["evidence"][e]["scope"])
                          for slide in slides for e in slide["evidence_ids"]},
        "slideviber_theme": slideviber_theme(selection) if selection["target"] == "slideviber" else None})


def validate_projection(deck: dict, model: dict, selection: dict, story: dict | None = None) -> None:
    verify(deck)
    if deck != project(model, selection, story):
        raise ValueError("presentation differs from frozen source/selection")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument('--story',type=Path)
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    story = json.loads(args.story.read_text(encoding='utf-8')) if args.story else None
    if args.verify:
        validate_projection(json.loads(args.verify.read_text(encoding="utf-8")), model, selection, story)
        print("verified")
    elif args.output:
        write_new(args.output, project(model, selection, story))
        print(args.output)
    else:
        parser.error("--output or --verify required")


if __name__ == "__main__":
    main()
