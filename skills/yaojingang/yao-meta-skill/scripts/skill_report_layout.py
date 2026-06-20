#!/usr/bin/env python3
"""Static layout contract for skill overview report HTML."""

import html
from pathlib import Path
from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by render_skill_overview.py to keep overview report layout and CSS out of data rendering."


ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets"


def read_layout_asset(filename: str) -> str:
    return (ASSET_DIR / filename).read_text(encoding="utf-8").strip()


def bi_span(zh: str, en: str) -> str:
    return (
        f'<span data-lang="zh-CN">{html.escape(str(zh))}</span>'
        f'<span data-lang="en">{html.escape(str(en))}</span>'
    )


def render_report_nav(nav_items: list[dict[str, Any]]) -> str:
    return "".join(
        f"<a href=\"#{html.escape(str(item['href']))}\">{bi_span(str(item['label']), str(item['label_en']))}</a>"
        for item in nav_items
    )


def render_language_switch() -> str:
    return (
        '<div class="language-switch" aria-label="语言切换">'
        '<button type="button" data-set-lang="zh-CN" aria-pressed="true">简体</button>'
        '<button type="button" data-set-lang="en" aria-pressed="false">EN</button>'
        "</div>"
    )


def skill_overview_css() -> str:
    return read_layout_asset("skill-overview.css")


def skill_overview_script() -> str:
    return read_layout_asset("skill-overview.js")
