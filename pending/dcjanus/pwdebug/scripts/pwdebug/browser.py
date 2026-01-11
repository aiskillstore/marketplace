"""浏览器连接与页面选择工具。"""

from __future__ import annotations

from typing import Optional

from playwright.sync_api import Browser, BrowserContext


def get_or_create_context(browser: Browser) -> BrowserContext:
    """获取已有的浏览器上下文，若不存在则创建新上下文。"""
    if browser.contexts:
        return browser.contexts[-1]
    return browser.new_context(viewport=None)


def get_or_create_page(
    context: BrowserContext,
    new_tab: bool = False,
) -> "playwright.sync_api.Page":
    """获取已有页面或新建页面。"""
    if new_tab or not context.pages:
        return context.new_page()
    return context.pages[-1]


def format_result(result: object) -> str:
    """将 evaluate 结果格式化为可读文本。"""
    if isinstance(result, list):
        lines = []
        for index, item in enumerate(result):
            if index:
                lines.append("")
            if isinstance(item, dict):
                lines.extend([f"{key}: {value}" for key, value in item.items()])
            else:
                lines.append(str(item))
        return "\n".join(lines)

    if isinstance(result, dict):
        return "\n".join([f"{key}: {value}" for key, value in result.items()])

    return str(result)


def pick_context(
    browser: Browser,
    context_index: Optional[int] = None,
) -> BrowserContext:
    """根据索引选择上下文，默认选择最新的上下文。"""
    contexts = browser.contexts
    if not contexts:
        return browser.new_context(viewport=None)
    if context_index is None:
        return contexts[-1]
    if context_index < 0 or context_index >= len(contexts):
        raise IndexError("上下文索引超出范围。")
    return contexts[context_index]
