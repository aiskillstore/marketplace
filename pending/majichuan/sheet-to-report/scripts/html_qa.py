from __future__ import annotations

import argparse
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from content_resolver import resolve_page_content
from narrative_planner import unresolved_question_records
from html_evidence import proof_table, scope_notes, uncovered_evidence_ids


class _VisibleDOM(HTMLParser):
    """Small static DOM audit; visual/CSS layout remains a browser acceptance gate."""
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.nodes, self.stack = [], []
        self.feed(document)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        hidden = (tag in {"style", "script", "template"} or "hidden" in attrs or attrs.get("aria-hidden") == "true"
                  or bool(re.search(r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:[;\s]|$)", attrs.get("style", ""), re.IGNORECASE))
                  or bool(self.stack and self.stack[-1]["hidden"]))
        node = {"tag": tag, "attrs": attrs, "hidden": hidden, "children": []}
        if self.stack:
            self.stack[-1]["children"].append(node)
        self.nodes.append(node)
        if tag not in {"br", "hr", "meta", "link", "img", "input", "source", "wbr"}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                self.stack = self.stack[:index]
                break

    def handle_data(self, data):
        if self.stack:
            self.stack[-1]["children"].append(data)


def _visible_text(node):
    if isinstance(node, str):
        return node
    if node["hidden"]:
        return ""
    return " ".join(_visible_text(child) for child in node["children"])


def _descendants(node):
    for child in node.get("children", []):
        if isinstance(child, dict):
            yield child
            yield from _descendants(child)


def _visible_proof_violations(document, model):
    dom = _VisibleDOM(document)
    violations, anchors, proved = [], {}, set()
    chapters = [c for c in model.get("analysis_chapters", []) if c.get("selection_status") == "selected"]
    chapter_nodes = [n for n in dom.nodes if n["tag"] == "article" and n["attrs"].get("class") == "analysis-chapter"]

    def verify_scope(record, node):
        expected = scope_notes(model, record)
        nodes = [n for n in _descendants(node) if n["attrs"].get("class") == "scope-disclosure"]
        text = " ".join(_visible_text(n) for n in nodes)
        if any(note not in text for note in expected):
            violations.append({"code": "scope_not_visible", "scope_id": record.get("scope_id")})

    for index, chapter in enumerate(chapters):
        node = chapter_nodes[index] if index < len(chapter_nodes) else {"children": []}
        verify_scope(chapter, node)
        descendants = list(_descendants(node))
        for ref in uncovered_evidence_ids(model, chapter):
            anchor = anchors.setdefault(ref, f"evidence-proof-{len(anchors) + 1}")
            expected = proof_table(model, ref)
            if sum(n["attrs"].get("id") == anchor for n in dom.nodes) != 1:
                violations.append({"code": "chapter_evidence_not_visible", "chapter_id": chapter.get("chapter_id"), "reason": "证明表锚点缺失或不唯一。"})
                continue
            matches = [n for n in descendants if n["tag"] == "table" and n["attrs"].get("id") == anchor]
            linked = ref in proved and any(n["tag"] == "a" and not n["hidden"] and n["attrs"].get("href") == "#" + anchor for n in descendants)
            if len(matches) == 1:
                matrix = [[_visible_text(cell).strip() for cell in row["children"] if isinstance(cell, dict) and cell["tag"] in {"th", "td"}]
                          for row in _descendants(matches[0]) if row["tag"] == "tr"]
                if matrix == [expected["headers"], *expected["rows"]]:
                    if expected.get("history"):
                        history_nodes = [n for n in descendants if n["tag"] == "table" and n["attrs"].get("id") == anchor + "-history" and not n["hidden"]]
                        history_matrix = ([[ _visible_text(cell).strip() for cell in row["children"] if isinstance(cell, dict) and cell["tag"] in {"th", "td"}]
                                           for row in _descendants(history_nodes[0]) if row["tag"] == "tr"] if len(history_nodes) == 1 else [])
                        if history_matrix != [expected["history"]["headers"], *expected["history"]["rows"]]:
                            violations.append({"code": "chapter_evidence_not_visible", "chapter_id": chapter.get("chapter_id"), "reason": "集中度逐月证明缺失或与证据不符。"})
                            continue
                    proved.add(ref)
                    verify_scope(model["evidence_index"][ref], node)
                    continue
            if not linked:
                violations.append({"code": "chapter_evidence_not_visible", "chapter_id": chapter.get("chapter_id")})
    summary_nodes = [n for n in dom.nodes if n["tag"] == "div" and n["attrs"].get("class") == "summary-row"]
    chapter_by_id = {c.get("chapter_id"): c for c in chapters}
    summary_items = [n for n in _descendants(summary_nodes[0]) if n["tag"] == "li"] if summary_nodes else []
    for index, refs in enumerate(model.get("executive_summary", {}).get("key_conclusion_chapter_ids", [])):
        for ref in ([refs] if isinstance(refs, str) else refs):
            if ref in chapter_by_id:
                verify_scope(chapter_by_id[ref], summary_items[index] if index < len(summary_items) else {"children": []})
    for collection, tag, attr, key in (("charts", "figure", "id", "chart_id"), ("actions", "article", "data-action-id", "action_id")):
        for record in model.get(collection, []):
            for node in dom.nodes:
                if node["tag"] == tag and node["attrs"].get(attr) == record.get(key):
                    verify_scope(record, node)
    return violations


PLACEHOLDER_PATTERN = re.compile(r"\{[A-Za-z_][A-Za-z0-9_.-]*\}")
INTERNAL_EVIDENCE_PATTERN = re.compile(
    r"(?:metric|dimension|dimension-yoy|dimension-slice-yoy|seasonality):[^<\s]+"
)
EXTERNAL_REFERENCE_PATTERN = re.compile(
    r"(?:src|href)\s*=\s*['\"]https?://", re.IGNORECASE
)
CODE_LIKE_BUSINESS_OBJECT_PATTERN = re.compile(
    r"(?<![\w])(?:SKU|ITEM|PRODUCT|PROD|STOCK|USER|CUSTOMER|CONTENT|PROJECT|TASK|ORDER)[-_]?\d+(?![\w])",
    re.IGNORECASE,
)
REQUIRED_SECTIONS = (
    "核心指标",
    "关键趋势与结构",
    "经营表现拆解",
    "关键洞察",
    "关键决策建议",
    "数据口径与质量",
)
ENGINEERING_REQUIRED_SECTIONS = (
    "工程核验概览",
    "源表数据概况",
    "加工后数据概况",
    "指标合同核验",
    "复算与验收状态",
    "数据范围与限制",
)
ENGINEERING_FORBIDDEN_SECTIONS = (
    "下一步重点",
    "分析期经营概览",
    "经营表现拆解",
    "关键洞察",
    "关键决策建议",
)


def _business_experience_violations(
    document: str, model: dict[str, Any], *, engineering_regression: bool,
) -> list[dict[str, Any]]:
    if engineering_regression:
        return []
    violations: list[dict[str, Any]] = []
    try:
        violations.extend(_visible_proof_violations(document, model))
    except (ValueError, KeyError, TypeError):
        violations.append({"code": "chapter_evidence_not_visible", "reason": "证据或范围缺少可靠的展示合同。"})
    pending = (unresolved_question_records(model, model.get("slide_plan", []))
               if "analysis_brief" in model and model.get("value_selection", {}).get("featured")
               else model.get("narrative_selection", {}).get("unresolved_questions", []))
    if pending:
        blocks = re.findall(r'<article\s+class="question-disposition".*?</article>', document, re.DOTALL)
        if len(blocks) != len(pending) or any(
            any(html.escape(str(item.get(field) or "")) not in block for field in ("business_question", "reason", "next_step"))
            for item, block in zip(pending, blocks)
        ):
            violations.append({"code": "unresolved_question_not_visible", "reason": "未完成问题、真实缺口和后续处理必须在 HTML 中可见。"})
    selected_chapter_count = sum(
        1 for item in model.get("analysis_chapters", [])
        if isinstance(item, dict) and item.get("selection_status") == "selected"
    )
    rendered_chapter_count = len(re.findall(
        r'<article\s+class="analysis-chapter"(?:\s|>)', document,
    ))
    if rendered_chapter_count == 0 or (
        selected_chapter_count and rendered_chapter_count != selected_chapter_count
    ):
        violations.append({
            "code": "legacy_metric_stack",
            "reason": "业务正文未按已选问题章节组织，仍是孤立指标与模块堆叠。",
            "expected_chapters": selected_chapter_count,
            "rendered_chapters": rendered_chapter_count,
        })

    selected_chapters = [
        item for item in model.get("analysis_chapters", [])
        if isinstance(item, dict) and item.get("selection_status") == "selected"
    ]
    chapter_blocks = re.findall(r'<article\s+class="analysis-chapter".*?</article>', document, re.DOTALL)
    actions = {str(item.get("action_id") or ""): item for item in model.get("actions", [])}
    proven_charts: set[str] = set()
    checked_actions: set[str] = set()
    for index, chapter in enumerate(selected_chapters):
        block = chapter_blocks[index] if index < len(chapter_blocks) else ""
        for chart_id in dict.fromkeys(str(value) for value in chapter.get("chart_ids", [])):
            escaped = re.escape(html.escape(chart_id, quote=True))
            figure = re.search(rf'<figure\b[^>]*\bid="{escaped}".*?</figure>', block, re.DOTALL)
            # A shared proof may point to an earlier chapter, not merely to an
            # unrelated global figure that happens to exist somewhere in HTML.
            linked = chart_id in proven_charts and f'href="#{html.escape(chart_id, quote=True)}"' in block
            if figure:
                proven_charts.add(chart_id)
            elif not linked:
                violations.append({"code": "chapter_proof_not_visible", "chapter_id": chapter.get("chapter_id"), "chart_id": chart_id})
        for action_id in chapter.get("action_ids", []):
            action_id = str(action_id)
            action = actions.get(action_id, {})
            if action_id in checked_actions:
                continue
            checked_actions.add(action_id)
            escaped = re.escape(html.escape(action_id, quote=True))
            match = re.search(rf'<article\b[^>]*\bdata-action-id="{escaped}".*?</article>', document, re.DOTALL)
            action_block = match.group() if match else ""
            readable = html.unescape(re.sub(r'<[^>]+>', ' ', action_block))
            required = [action.get(field) for field in ("target", "basis", "rationale", "success_signal")]
            required += [value for field in ("steps", "guardrails", "limitations") for value in action.get(field, [])]
            missing = [str(value) for value in required if str(value or "").strip() and str(value) not in readable]
            if not match or missing:
                violations.append({"code": "action_plan_not_visible", "action_id": action_id, "missing": missing})

    semantic = model.get("analysis_contract", {}).get("semantic_contract", {})
    bindings = semantic.get("object_bindings", []) if isinstance(semantic, dict) else []
    display_bound = any(
        isinstance(item, dict)
        and str(item.get("identifier_field") or "").strip()
        and str(item.get("display_field") or "").strip()
        for item in bindings
    )
    visible = re.sub(r"<(?:style|script)\b.*?</(?:style|script)>", " ", document, flags=re.DOTALL | re.IGNORECASE)
    visible = html.unescape(re.sub(r"<[^>]+>", " ", visible))
    identifier_tokens = sorted(set(CODE_LIKE_BUSINESS_OBJECT_PATTERN.findall(visible)))
    if display_bound and identifier_tokens:
        violations.append({
            "code": "id_only_business_object",
            "reason": "正文出现编码型对象，但语义合同已提供业务展示字段。",
            "tokens": identifier_tokens[:10],
        })
    return violations


def qa_html(path: Path, model: dict[str, Any]) -> dict[str, Any]:
    document = Path(path).read_text(encoding="utf-8")
    engineering_regression = str(
        model.get("request", {}).get("analysis_intent") or ""
    ) == "engineering_regression"
    unresolved_placeholders = sorted(set(PLACEHOLDER_PATTERN.findall(document)))
    internal_metadata_violations = sorted(
        set(INTERNAL_EVIDENCE_PATTERN.findall(document))
    )
    required_sections = (
        ENGINEERING_REQUIRED_SECTIONS if engineering_regression else REQUIRED_SECTIONS
    )
    pages = list(model.get("slide_plan", []))
    visible_levers = (
        [lever for page in pages for lever in resolve_page_content(model, page)["levers"]]
        if pages and all(isinstance(page.get("content_refs"), dict) for page in pages)
        else model.get("levers", [])
    )
    if not visible_levers:
        required_sections = tuple(section for section in required_sections if section != "经营表现拆解")
    forbidden_section_names = (
        ENGINEERING_FORBIDDEN_SECTIONS if engineering_regression else ()
    )
    missing_sections = [section for section in required_sections if section not in document]
    forbidden_sections = [
        section for section in forbidden_section_names if section in document
    ]
    missing_chart_ids: list[str] = []
    chart_content_violations: list[dict[str, Any]] = []
    charts_by_id = {str(chart["chart_id"]): chart for chart in model.get("charts", [])}
    pages = list(model.get("slide_plan", []))
    if pages and all(isinstance(page.get("content_refs"), dict) for page in pages):
        selected_chart_ids = [
            chart_id
            for page in pages
            for chart_id in resolve_page_content(model, page)["chart_ids"]
        ]
        expected_charts = [charts_by_id[chart_id] for chart_id in dict.fromkeys(selected_chart_ids)]
    else:
        expected_charts = list(model.get("charts", []))
    expected_ids = {str(chart["chart_id"]) for chart in expected_charts}
    for chapter in model.get("analysis_chapters", []):
        if chapter.get("selection_status") != "selected":
            continue
        for chart_id in chapter.get("chart_ids", []):
            if chart_id not in charts_by_id:
                missing_chart_ids.append(str(chart_id))
            elif chart_id not in expected_ids:
                expected_charts.append(charts_by_id[chart_id])
                expected_ids.add(chart_id)
    for chart in expected_charts:
        chart_id = str(chart["chart_id"])
        marker = f'id="{html.escape(chart_id, quote=True)}"'
        if marker not in document:
            missing_chart_ids.append(chart_id)
            continue
        figure_match = re.search(
            rf'<figure[^>]+id="{re.escape(html.escape(chart_id, quote=True))}".*?</figure>',
            document,
            re.DOTALL,
        )
        if not figure_match:
            chart_content_violations.append(
                {"chart_id": chart_id, "reason": "figure_not_closed"}
            )
            continue
        figure = figure_match.group(0)
        categories = [str(category) for category in chart.get("categories", [])]
        required_categories = (
            categories
            if chart.get("chart_type") == "bar"
            else list(dict.fromkeys(categories[:1] + categories[-1:]))
        )
        missing_categories = [
            str(category)
            for category in required_categories
            if html.escape(str(category)) not in figure
        ]
        if missing_categories:
            chart_content_violations.append(
                {
                    "chart_id": chart_id,
                    "reason": "missing_categories",
                    "categories": missing_categories,
                }
            )
    external_references = EXTERNAL_REFERENCE_PATTERN.findall(document)
    business_experience_violations = _business_experience_violations(
        document, model, engineering_regression=engineering_regression,
    )
    report_title_present = html.escape(str(model.get("report_title", ""))) in document
    passed = not any(
        (
            unresolved_placeholders,
            internal_metadata_violations,
            missing_sections,
            forbidden_sections,
            missing_chart_ids,
            chart_content_violations,
            external_references,
            business_experience_violations,
        )
    ) and report_title_present
    return {
        "status": "passed" if passed else "failed",
        "self_contained": not external_references,
        "report_title_present": report_title_present,
        "missing_sections": missing_sections,
        "forbidden_sections": forbidden_sections,
        "missing_chart_ids": missing_chart_ids,
        "chart_content_violations": chart_content_violations,
        "unresolved_placeholders": unresolved_placeholders,
        "internal_metadata_violations": internal_metadata_violations,
        "external_references": external_references,
        "business_experience_violations": business_experience_violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a rendered sheet-to-report HTML artifact."
    )
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    result = qa_html(args.html, model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
