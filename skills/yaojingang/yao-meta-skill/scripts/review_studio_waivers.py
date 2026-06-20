#!/usr/bin/env python3
"""Review Studio waiver candidate rendering helpers."""

import html
from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by render_review_studio.py to keep waiver candidate layout out of the main renderer."


def render_waiver_candidates_panel(review_waivers: dict[str, Any]) -> str:
    candidates = review_waivers.get("waiver_candidates", []) if isinstance(review_waivers, dict) else []
    if not candidates:
        return "<p class='muted'>当前没有需要 reviewer 处理的批准候选。</p>"
    cards = []
    for item in candidates:
        allowed = bool(item.get("waiver_allowed"))
        allowed_label = "可批准" if allowed else "不可批准"
        status = str(item.get("status", "unknown"))
        required_review = item.get("required_review", [])
        required_html = "".join(
            f"<li>{html.escape(str(review_item))}</li>"
            for review_item in required_review
        ) or "<li>证据不足，需要先补充审查条件。</li>"
        decision_options = item.get("decision_options", [])
        decision_options_label = ", ".join(str(option) for option in decision_options) if decision_options else "无"
        cards.append(
            "<article class='waiver-card "
            + ("allowed" if allowed else "blocked")
            + "'>"
            f"<div><span>{html.escape(allowed_label)} · {html.escape(status)}</span>"
            f"<h3>{html.escape(str(item.get('label') or item.get('gate_key') or 'Waiver Candidate'))}</h3></div>"
            f"<p>{html.escape(str(item.get('risk_summary') or '证据不足'))}</p>"
            "<dl>"
            f"<dt>Gate</dt><dd><code>{html.escape(str(item.get('gate_key', '')))}</code></dd>"
            f"<dt>证据</dt><dd><code>{html.escape(str(item.get('suggested_evidence', '')))}</code></dd>"
            f"<dt>选项</dt><dd>{html.escape(decision_options_label)}</dd>"
            f"<dt>边界</dt><dd>{html.escape(str(item.get('world_class_boundary', '')))}</dd>"
            "</dl>"
            "<div class='waiver-review'><h4>审查条件</h4>"
            f"<ul>{required_html}</ul></div>"
            "<div class='waiver-command'><span>建议命令</span>"
            f"<code>{html.escape(str(item.get('suggested_command', '')))}</code></div>"
            "</article>"
        )
    return "<div class='waiver-candidate-grid'>" + "".join(cards) + "</div>"
