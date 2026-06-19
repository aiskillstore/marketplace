#!/usr/bin/env python3
"""Static layout contract for Review Studio HTML."""

import html
from pathlib import Path


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by render_review_studio.py to keep Review Studio layout and CSS out of gate logic."


ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets"


REVIEW_STUDIO_NAV = [
    ("#overview", "审查总览"),
    ("#intent", "意图画布"),
    ("#trigger", "触发实验"),
    ("#output", "输出实验"),
    ("#actions", "修复动作"),
    ("#annotations", "审查批注"),
    ("#runtime", "运行矩阵"),
    ("#trust", "信任报告"),
    ("#permissions", "权限批准"),
    ("#permission-probes", "权限探针"),
    ("#atlas", "组合治理"),
    ("#telemetry", "运营回路"),
    ("#waivers", "人工批准"),
    ("#world-class", "世界证据"),
    ("#registry", "注册审计"),
    ("#release", "发布路线"),
]


def read_layout_asset(filename: str) -> str:
    return (ASSET_DIR / filename).read_text(encoding="utf-8").strip()


def render_review_nav(nav_items: list[tuple[str, str]] | None = None) -> str:
    items = REVIEW_STUDIO_NAV if nav_items is None else nav_items
    return "".join(
        f"<a href='{html.escape(href)}'>{html.escape(label)}</a>"
        for href, label in items
    )


def review_studio_css() -> str:
    return read_layout_asset("review-studio.css")
