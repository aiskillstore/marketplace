#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "playwright>=1.49.0",
#     "rich>=14.2.0",
#     "trafilatura>=2.0.0",
#     "typer>=0.20.1",
# ]
# ///

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import typer
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.panel import Panel
import trafilatura

APP = typer.Typer(add_completion=False)
CONSOLE = Console()


def detect_browser_path() -> str | None:
    """Try common local browser paths to avoid Playwright download."""

    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Arc.app/Contents/MacOS/Arc",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/microsoft-edge",
        "/usr/bin/microsoft-edge-stable",
        "/usr/bin/brave-browser",
        "/usr/bin/brave-browser-stable",
        "/snap/bin/chromium",
        "/snap/bin/brave",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def render_html(url: str, timeout_ms: int, browser_path: str | None) -> str:
    """使用 Playwright 渲染页面并返回完整 HTML。"""

    with sync_playwright() as playwright:
        launch_options: dict[str, Any] = {"headless": True}
        if browser_path:
            launch_options["executable_path"] = browser_path
        browser = playwright.chromium.launch(**launch_options)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        html = page.content()
        context.close()
        browser.close()
    return html


def extract_content(html: str, url: str, output_format: str) -> str:
    """使用 trafilatura 从 HTML 提取内容。"""

    content = trafilatura.extract(
        html,
        url=url,
        output_format=output_format,
        include_formatting=True,
        include_links=True,
    )
    if not content:
        raise ValueError("Failed to extract main content from the rendered HTML.")
    return content


@APP.command()
def fetch(
    url: str = typer.Argument(..., help="Target URL to render into content."),
    output: Path | None = typer.Option(None, help="Write output to file instead of stdout."),
    timeout_ms: int = typer.Option(60000, help="Playwright navigation timeout in milliseconds."),
    browser_path: Path | None = typer.Option(
        None,
        help="Optional local Chromium-based browser path. Auto-detected if omitted.",
    ),
    output_format: str = typer.Option(
        "markdown",
        help="Output format: csv, html, json, markdown, raw-html, txt, xml, xmltei.",
    ),
) -> None:
    """通过 Playwright 渲染并用 trafilatura 提取内容。"""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise typer.BadParameter("Only http or https URLs are supported.")

    resolved_browser_path = str(browser_path) if browser_path else detect_browser_path()
    try:
        html = render_html(url, timeout_ms=timeout_ms, browser_path=resolved_browser_path)
        content = html if output_format == "raw-html" else extract_content(html, url, output_format)
    except PlaywrightTimeoutError as exc:
        CONSOLE.print(
            Panel.fit(
                f"[red]Playwright timeout[/red]\n{exc}",
                title="Request Failed",
            )
        )
        raise typer.Exit(code=1) from exc
    except ValueError as exc:
        CONSOLE.print(
            Panel.fit(
                f"[red]Extraction failed[/red]\n{exc}",
                title="Request Failed",
            )
        )
        raise typer.Exit(code=1) from exc
    except PlaywrightError as exc:
        hint = "Install Playwright browsers with: uv run playwright install chromium"
        CONSOLE.print(
            Panel.fit(
                f"[red]Playwright launch failed[/red]\\n{exc}\\n{hint}",
                title="Request Failed",
            )
        )
        raise typer.Exit(code=1) from exc

    if output:
        output.write_text(content, encoding="utf-8")
        CONSOLE.print(f"[green]Saved output to[/green] {output}")
    else:
        CONSOLE.print(content, markup=False)


if __name__ == "__main__":
    APP()
