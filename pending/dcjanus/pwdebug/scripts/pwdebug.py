#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.57.0",
#     "typer>=0.20.1",
# ]
# ///

from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
import time
import urllib.request
from datetime import datetime
from typing import List, Optional

import typer
from playwright.sync_api import BrowserType, ConsoleMessage, Error, sync_playwright

from pwdebug.browser import (
    format_result,
    get_or_create_context,
    get_or_create_page,
    pick_context,
)
from pwdebug.picker import get_picker_script
from pwdebug.state import (
    append_log_entry,
    clear_log,
    get_cdp_endpoint,
    get_profile_dir,
    read_state,
    tail_log_entries,
    write_state,
)

app = typer.Typer(add_completion=False, help="PWDebug 浏览器调试 CLI。")


def _resolve_browser_type(playwright, browser_name: str) -> BrowserType:
    """根据名称解析 Playwright 浏览器类型。"""
    try:
        return getattr(playwright, browser_name)
    except AttributeError as exc:
        raise typer.BadParameter(f"不支持的浏览器类型: {browser_name}") from exc


def _is_process_alive(pid: int) -> bool:
    """判断进程是否存活。"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _ensure_args(args: Optional[List[str]]) -> List[str]:
    """清理命令行参数列表。"""
    if not args:
        return []
    return args


def _wait_for_cdp(port: int, timeout: float = 6.0) -> None:
    """等待 CDP 端口就绪。"""
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/json/version"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("CDP 端口未就绪，请检查浏览器是否成功启动。")


@app.command()
def start(
    headless: bool = typer.Option(False, "--headless/--headed", help="是否无头模式。"),
    port: int = typer.Option(9222, "--port", help="CDP 调试端口。"),
    arg: Optional[List[str]] = typer.Option(None, "--arg", help="额外的浏览器启动参数。"),
) -> None:
    """启动 Chromium 浏览器服务。"""
    with sync_playwright() as playwright:
        browser_type = _resolve_browser_type(playwright, "chromium")
        executable_path = browser_type.executable_path

    if not executable_path or not os.path.exists(executable_path):
        typer.echo("未找到 Chromium 可执行文件，请先安装 Playwright 浏览器。", err=True)
        raise typer.Exit(code=1)

    profile_dir = get_profile_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)

    args = [
        executable_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    if headless:
        args.append("--headless=new")

    args.extend(_ensure_args(arg))

    process = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    cdp_endpoint = f"http://127.0.0.1:{port}"
    clear_log()

    try:
        _wait_for_cdp(port)
    except Exception:
        process.terminate()
        raise

    write_state(cdp_endpoint, process.pid, "chromium")

    typer.echo("浏览器服务已启动。")
    typer.echo(f"cdp_endpoint: {cdp_endpoint}")


@app.command()
def stop() -> None:
    """停止 Playwright 浏览器服务。"""
    state = read_state()
    pid = state.get("pid")
    if not pid:
        raise typer.BadParameter("状态文件缺少 pid。")
    if not _is_process_alive(pid):
        typer.echo("浏览器服务进程已退出。")
        return
    os.kill(pid, signal.SIGTERM)
    typer.echo("已发送停止信号。")


@app.command()
def status() -> None:
    """查看浏览器服务状态。"""
    try:
        state = read_state()
    except FileNotFoundError:
        typer.echo("未找到浏览器服务状态。")
        return
    pid = state.get("pid")
    cdp_endpoint = state.get("cdp_endpoint")
    browser_type = state.get("browser_type", "chromium")
    running = bool(pid and _is_process_alive(pid))
    typer.echo(json.dumps(
        {
            "running": running,
            "pid": pid,
            "browser_type": browser_type,
            "cdp_endpoint": cdp_endpoint,
        },
        ensure_ascii=False,
        indent=2,
    ))


@app.command()
def nav(
    url: str = typer.Argument(..., help="要打开的 URL。"),
    new_tab: bool = typer.Option(False, "--new", help="是否新开标签页。"),
    context_index: Optional[int] = typer.Option(None, "--context-index", help="上下文索引。"),
) -> None:
    """在浏览器中导航到指定 URL。"""
    with sync_playwright() as playwright:
        cdp_endpoint = get_cdp_endpoint()
        browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
        context = pick_context(browser, context_index)
        page = get_or_create_page(context, new_tab=new_tab)
        page.goto(url, wait_until="domcontentloaded")
        typer.echo(f"已打开: {url}")


@app.command()
def evaluate(
    expression: str = typer.Argument(..., help="需要执行的 JS 表达式。"),
    context_index: Optional[int] = typer.Option(None, "--context-index", help="上下文索引。"),
) -> None:
    """在页面中执行 JS 表达式并输出结果。"""
    with sync_playwright() as playwright:
        cdp_endpoint = get_cdp_endpoint()
        browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
        context = pick_context(browser, context_index)
        page = get_or_create_page(context)
        script = f"() => ({expression})"
        try:
            result = page.evaluate(script)
        except Error as exc:
            typer.echo("执行失败。")
            typer.echo(str(exc))
            raise typer.Exit(code=1)
        typer.echo(format_result(result))


@app.command()
def screenshot(
    full_page: bool = typer.Option(False, "--full", help="是否截取完整页面。"),
    context_index: Optional[int] = typer.Option(None, "--context-index", help="上下文索引。"),
) -> None:
    """对当前页面进行截图。"""
    with sync_playwright() as playwright:
        cdp_endpoint = get_cdp_endpoint()
        browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
        context = pick_context(browser, context_index)
        page = get_or_create_page(context)
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot-{timestamp}.png"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        page.screenshot(path=filepath, full_page=full_page)
        typer.echo(filepath)


@app.command()
def pick(
    message: str = typer.Argument(..., help="提示语，例如: 点击登录按钮"),
    context_index: Optional[int] = typer.Option(None, "--context-index", help="上下文索引。"),
) -> None:
    """在页面中交互式选择元素。"""
    with sync_playwright() as playwright:
        cdp_endpoint = get_cdp_endpoint()
        browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
        context = pick_context(browser, context_index)
        page = get_or_create_page(context)
        page.evaluate(get_picker_script())
        result = page.evaluate("msg => window.pick(msg)", message)
        typer.echo(format_result(result))


@app.command()
def watch_logs(
    context_index: Optional[int] = typer.Option(None, "--context-index", help="上下文索引。"),
) -> None:
    """监听控制台日志并写入本地文件。"""
    with sync_playwright() as playwright:
        cdp_endpoint = get_cdp_endpoint()
        browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
        context = pick_context(browser, context_index)
        page = get_or_create_page(context)

        def _handle_console(msg: ConsoleMessage) -> None:
            """处理 console 事件并落地日志。"""
            entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": msg.type,
                "text": msg.text,
                "location": msg.location,
            }
            append_log_entry(entry)

        def _handle_page_error(error: Error) -> None:
            """处理页面异常并落地日志。"""
            entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "error",
                "text": str(error),
                "location": {},
            }
            append_log_entry(entry)

        page.on("console", _handle_console)
        page.on("pageerror", _handle_page_error)
        typer.echo("已开始监听控制台日志，按 Ctrl+C 结束。")
        while True:
            time.sleep(0.5)


@app.command()
def logs(
    limit: int = typer.Argument(100, help="最多输出的日志条数。"),
) -> None:
    """读取最近的控制台日志。"""
    if limit < 1:
        raise typer.BadParameter("limit 必须为正整数。")
    limit = min(limit, 500)
    entries = tail_log_entries(limit)
    if not entries:
        typer.echo("暂无日志。")
        return
    typer.echo(f"最近 {len(entries)} 条日志:\n")
    for entry in entries:
        timestamp = entry.get("timestamp", "")
        level = str(entry.get("level", "")).upper().ljust(5)
        text = entry.get("text", "")
        location = entry.get("location", {}) or {}
        location_text = ""
        if location.get("url"):
            location_text = f"  at {location.get('url')}:{location.get('lineNumber', '')}"
        typer.echo(f"[{timestamp}] {level} {text}")
        if location_text.strip():
            typer.echo(location_text)
        typer.echo("")


if __name__ == "__main__":
    app()
