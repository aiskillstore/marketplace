#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "playwright>=1.61.0",
#     "rich>=15.0.0",
#     "trafilatura>=2.1.0",
#     "typer>=0.26.8",
# ]
# ///

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any, Literal
from time import monotonic
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import typer
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.panel import Panel
import trafilatura

APP = typer.Typer(add_completion=False)
CONSOLE = Console()

OutputFormat = Literal[
    "csv", "html", "json", "markdown", "raw-html", "txt", "xml", "xmltei"
]
FetchStrategy = Literal["auto", "agent", "jina", "browser"]
TWITTER_HOSTS = {
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
    "mobile.x.com",
    "mobile.twitter.com",
}
FXTWITTER_API_ROOT = "https://api.fxtwitter.com/2/status"
JINA_READER_API_ROOT = "https://r.jina.ai/"
JINA_API_KEY_ENV = "JINA_API_KEY"
JINA_BLOCK_PAGE_SIGNALS = (
    ("rate limit", "jina"),
    ("too many requests", "jina"),
    ("rate limit exceeded", "jina"),
    ("retry after", "jina"),
    ("request limit reached", "jina"),
    ("security verification", "jina"),
)
# FxTwitter source repository: https://github.com/allnodes/FxTwitter


def escape_markdown_text(value: str) -> str:
    """Escape common Markdown control characters for plain-text rendering."""

    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>])", r"\\\1", value)


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


def render_html(
    url: str,
    timeout_ms: int,
    browser_path: str | None,
    verbose: bool,
) -> str:
    """使用 Playwright 渲染页面并返回完整 HTML。"""

    if verbose:
        CONSOLE.print(
            f"[cyan]Launching browser[/cyan] "
            f"(strategy=domcontentloaded+load+stability, timeout_ms={timeout_ms})",
            highlight=False,
        )

    with sync_playwright() as playwright:
        launch_options: dict[str, Any] = {"headless": True}
        if browser_path:
            launch_options["executable_path"] = browser_path
            if verbose:
                CONSOLE.print(
                    f"[cyan]Using browser path[/cyan] {browser_path}",
                    highlight=False,
                )
        elif verbose:
            CONSOLE.print(
                "[cyan]Using Playwright-managed Chromium[/cyan]", highlight=False
            )

        browser = playwright.chromium.launch(**launch_options)
        context = browser.new_context()
        page = context.new_page()
        if verbose:
            CONSOLE.print(f"[cyan]Navigating[/cyan] {url}", highlight=False)
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            page.wait_for_load_state("load", timeout=min(timeout_ms, 5000))
            if verbose:
                CONSOLE.print("[cyan]Load event reached[/cyan]", highlight=False)
        except PlaywrightTimeoutError:
            if verbose:
                CONSOLE.print(
                    "[yellow]Load event wait timed out, continue[/yellow]",
                    highlight=False,
                )

        # Wait briefly for client-side rendering to settle without risking long hangs.
        deadline = monotonic() + 2.0
        previous_size: int | None = None
        stable_rounds = 0
        while monotonic() < deadline:
            current_size = page.evaluate(
                "() => document.body ? document.body.innerHTML.length : 0"
            )
            if previous_size is not None and abs(current_size - previous_size) <= 64:
                stable_rounds += 1
            else:
                stable_rounds = 0
            if stable_rounds >= 2:
                if verbose:
                    CONSOLE.print("[cyan]DOM stabilized[/cyan]", highlight=False)
                break
            previous_size = current_size
            page.wait_for_timeout(300)
        html = page.content()
        context.close()
        browser.close()

    if verbose:
        CONSOLE.print(
            f"[green]Rendered HTML size[/green] {len(html)} chars", highlight=False
        )

    return html


def extract_content(
    html: str, url: str, output_format: OutputFormat, verbose: bool
) -> str:
    """使用 trafilatura 从 HTML 提取内容。"""
    if verbose:
        CONSOLE.print(
            f"[cyan]Extracting content[/cyan] as {output_format}", highlight=False
        )

    content = trafilatura.extract(
        html,
        url=url,
        output_format=output_format,
        include_formatting=True,
        include_links=True,
    )
    if not content:
        raise ValueError("Failed to extract main content from the rendered HTML.")

    if verbose:
        CONSOLE.print(
            f"[green]Extracted content size[/green] {len(content)} chars",
            highlight=False,
        )

    return content


def fetch_agent_markdown(url: str, timeout_ms: int, verbose: bool) -> str | None:
    """通过 Accept 协商优先请求 text/markdown，命中则直接返回。"""

    if verbose:
        CONSOLE.print(
            "[cyan]Trying Markdown for Agents negotiation[/cyan]", highlight=False
        )

    request = Request(  # noqa: S310 - 本地 CLI 可信输入, URL 由用户主动提供
        url,
        headers={
            "Accept": "text/markdown, text/html;q=0.9, */*;q=0.1",
            "User-Agent": "fetch-url/1.0 (+https://github.com/cloudflare/markdown-for-agents)",
        },
    )
    try:
        with urlopen(request, timeout=max(timeout_ms / 1000.0, 1.0)) as response:  # noqa: S310
            content_type = response.headers.get_content_type()
            if verbose:
                CONSOLE.print(
                    f"[cyan]Negotiated content-type[/cyan] {content_type}",
                    highlight=False,
                )
            if content_type != "text/markdown":
                return None
            charset = response.headers.get_content_charset() or "utf-8"
            markdown = response.read().decode(charset, errors="replace")
            if not markdown.strip():
                return None
            if verbose:
                CONSOLE.print(
                    f"[green]Markdown for Agents hit[/green] {len(markdown)} chars",
                    highlight=False,
                )
            return markdown
    except (URLError, OSError) as exc:
        if verbose:
            CONSOLE.print(
                f"[yellow]Markdown negotiation failed, fallback to browser render[/yellow] ({exc})",
                highlight=False,
            )
        return None


def fetch_jina_reader_markdown(url: str, timeout_ms: int, verbose: bool) -> str | None:
    """通过 Jina Reader 获取 Markdown, 命中则直接返回。"""

    reader_url = f"{JINA_READER_API_ROOT}{url}"
    api_key = os.getenv(JINA_API_KEY_ENV, "").strip()
    headers = {
        "Accept": "text/markdown, text/plain;q=0.9, */*;q=0.1",
        "User-Agent": "fetch-url/1.0 (+https://github.com/DCjanus/prompts/tree/master/skills/fetch-url)",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if verbose:
        auth_mode = f"with {JINA_API_KEY_ENV}" if api_key else "without API key"
        CONSOLE.print(
            f"[cyan]Trying Jina Reader[/cyan] {auth_mode}",
            highlight=False,
        )

    request = Request(  # noqa: S310 - 本地 CLI 可信输入, URL 由用户主动提供
        reader_url,
        headers=headers,
    )
    try:
        with urlopen(request, timeout=max(timeout_ms / 1000.0, 1.0)) as response:  # noqa: S310
            charset = response.headers.get_content_charset() or "utf-8"
            markdown = response.read().decode(charset, errors="replace")
            if not markdown.strip():
                return None
            if is_obvious_jina_block_page(markdown):
                if verbose:
                    CONSOLE.print(
                        "[yellow]Jina Reader returned a probable rate-limit page[/yellow]",
                        highlight=False,
                    )
                return None
            if verbose:
                CONSOLE.print(
                    f"[green]Jina Reader hit[/green] {len(markdown)} chars",
                    highlight=False,
                )
            return markdown
    except (URLError, OSError) as exc:
        if verbose:
            CONSOLE.print(
                f"[yellow]Jina Reader failed[/yellow] ({exc})",
                highlight=False,
            )
        return None


def is_obvious_jina_block_page(content: str) -> bool:
    """识别少数非常明显的 Jina 限流或挑战页。"""

    snippet = content[:4000].lower()
    return any(
        all(part in snippet for part in signal) for signal in JINA_BLOCK_PAGE_SIGNALS
    )


def extract_twitter_status_id(url: str) -> str | None:
    """从 x.com/twitter.com 推文链接提取 status id。"""

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in TWITTER_HOSTS:
        return None

    path = parsed.path.rstrip("/")
    patterns = (
        r"^/i/status/(\d{2,20})(?:/(?:photo|video)/\d+)?$",
        r"^/[A-Za-z0-9_]+/status(?:es)?/(\d{2,20})(?:/(?:photo|video)/\d+)?$",
    )
    for pattern in patterns:
        matched = re.match(pattern, path)
        if matched:
            return matched.group(1)
    return None


def fetch_fxtwitter_status(
    status_id: str, timeout_ms: int, verbose: bool
) -> dict[str, Any] | None:
    """调用 FxTwitter API 获取结构化推文数据。"""

    api_url = f"{FXTWITTER_API_ROOT}/{status_id}"
    if verbose:
        CONSOLE.print(f"[cyan]Fetching FxTwitter API[/cyan] {api_url}", highlight=False)

    request = Request(  # noqa: S310 - 固定 HTTPS API 根地址 + 数字 status id
        api_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "fetch-url/1.0 (+https://github.com/DCjanus/prompts/tree/master/skills/fetch-url)",
        },
    )
    try:
        with urlopen(request, timeout=max(timeout_ms / 1000.0, 1.0)) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except (URLError, OSError, json.JSONDecodeError) as exc:
        if verbose:
            CONSOLE.print(
                f"[yellow]FxTwitter API request failed[/yellow] ({exc})",
                highlight=False,
            )
        return None

    if not isinstance(payload, dict):
        return None
    if payload.get("code") != 200 or not isinstance(payload.get("status"), dict):
        if verbose:
            CONSOLE.print(
                "[yellow]FxTwitter payload invalid[/yellow]",
                highlight=False,
            )
        return None
    return payload


def _extract_thread_entries(
    payload: dict[str, Any], root_status_id: str
) -> list[dict[str, Any]]:
    """从 FxTwitter payload 中提取 thread 条目并去重。"""

    thread = payload.get("thread")
    raw_entries: list[Any] = []
    if isinstance(thread, list):
        raw_entries.extend(thread)
    elif isinstance(thread, dict):
        for key in ("tweets", "statuses", "items", "entries", "thread", "posts"):
            value = thread.get(key)
            if isinstance(value, list):
                raw_entries.extend(value)
        if not raw_entries:
            status_value = thread.get("status")
            if isinstance(status_value, dict):
                raw_entries.append(status_value)
            else:
                # Best effort fallback: some payloads may store id->status dictionaries.
                dict_values = [
                    value for value in thread.values() if isinstance(value, dict)
                ]
                raw_entries.extend(dict_values)

    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = {root_status_id}
    for raw_item in raw_entries:
        if not isinstance(raw_item, dict):
            continue
        item = raw_item.get("status")
        if not isinstance(item, dict):
            item = raw_item.get("tweet")
        if not isinstance(item, dict):
            item = raw_item

        item_id = str(item.get("id") or "").strip()
        if not item_id or item_id in seen_ids:
            continue
        seen_ids.add(item_id)
        entries.append(item)

    return entries


def _render_thread_item_markdown(item: dict[str, Any], index: int) -> list[str]:
    author = item.get("author", {})
    author_name = escape_markdown_text(str(author.get("name") or "Unknown"))
    screen_name = escape_markdown_text(str(author.get("screen_name") or "unknown"))
    item_id = escape_markdown_text(str(item.get("id") or "N/A"))
    item_url = str(item.get("url") or "").strip()
    created_at = escape_markdown_text(str(item.get("created_at") or "N/A"))
    raw_text = item.get("raw_text")
    if isinstance(raw_text, dict):
        fallback_text = raw_text.get("text")
    else:
        fallback_text = raw_text
    text = str(item.get("text") or fallback_text or "").strip()
    if not text:
        text = "_(No text content returned by FxTwitter API)_"
    safe_text = escape_markdown_text(text)

    lines = [
        f"### {index}. {author_name} (@{screen_name})",
        f"- ID: {item_id}",
        f"- Created: {created_at}",
    ]
    if item_url:
        lines.append(f"- URL: {item_url}")
    lines.extend(["", safe_text])

    media = item.get("media")
    if isinstance(media, dict):
        all_media = media.get("all")
        if isinstance(all_media, list) and all_media:
            lines.append("")
            lines.append("Media:")
            for media_item in all_media:
                if not isinstance(media_item, dict):
                    continue
                media_type = str(media_item.get("type") or "media")
                media_url = str(
                    media_item.get("url") or media_item.get("thumbnail_url") or ""
                ).strip()
                if media_url:
                    lines.append(f"- {media_type}: {media_url}")
    lines.append("")
    return lines


def render_fxtwitter_markdown(payload: dict[str, Any], source_url: str) -> str:
    """将 FxTwitter API 响应渲染为 Markdown。"""

    status = payload.get("status", {})
    author = status.get("author", {})
    author_name = str(author.get("name") or "Unknown")
    screen_name = str(author.get("screen_name") or "unknown")
    status_url = str(status.get("url") or source_url)
    created_at = str(status.get("created_at") or "N/A")
    raw_text = status.get("raw_text")
    if isinstance(raw_text, dict):
        fallback_text = raw_text.get("text")
    else:
        fallback_text = raw_text
    text = str(status.get("text") or fallback_text or "").strip()
    if not text:
        text = "_(No text content returned by FxTwitter API)_"
    safe_author_name = escape_markdown_text(author_name)
    safe_screen_name = escape_markdown_text(screen_name)
    safe_text = escape_markdown_text(text)
    root_status_id = str(status.get("id") or "").strip()

    likes = status.get("likes")
    reposts = status.get("reposts")
    replies = status.get("replies")
    views = status.get("views")
    stats = (
        f"❤️ {likes if likes is not None else 'N/A'} | "
        f"🔁 {reposts if reposts is not None else 'N/A'} | "
        f"💬 {replies if replies is not None else 'N/A'} | "
        f"👀 {views if views is not None else 'N/A'}"
    )

    lines = [
        f"# {safe_author_name} (@{safe_screen_name})",
        "",
        "- Source: FxTwitter API (not direct page access)",
        f"- Canonical URL: {status_url}",
        f"- Created: {created_at}",
        f"- Stats: {stats}",
        "",
        "## Text",
        safe_text,
    ]

    media = status.get("media")
    if isinstance(media, dict):
        all_media = media.get("all")
        if isinstance(all_media, list) and all_media:
            lines.extend(["", "## Media"])
            for item in all_media:
                if not isinstance(item, dict):
                    continue
                media_type = str(item.get("type") or "media")
                media_url = str(
                    item.get("url") or item.get("thumbnail_url") or ""
                ).strip()
                if media_url:
                    lines.append(f"- {media_type}: {media_url}")

    thread_entries = _extract_thread_entries(payload, root_status_id=root_status_id)
    if thread_entries:
        lines.extend(["", "## Thread"])
        for index, thread_item in enumerate(thread_entries, start=1):
            lines.extend(_render_thread_item_markdown(thread_item, index=index))

    return "\n".join(lines).strip() + "\n"


@APP.command()
def fetch(
    url: str = typer.Argument(..., help="Target URL to render into content."),
    output: Path | None = typer.Option(
        None, help="Write output to file instead of stdout."
    ),
    timeout_ms: int = typer.Option(
        60000, help="Playwright navigation timeout in milliseconds."
    ),
    browser_path: Path | None = typer.Option(
        None,
        help="Optional local Chromium-based browser path. Auto-detected if omitted.",
    ),
    output_format: OutputFormat = typer.Option(
        "markdown",
        help="Output format: csv, html, json, markdown, raw-html, txt, xml, xmltei.",
    ),
    fetch_strategy: FetchStrategy = typer.Option(
        "auto",
        help="Fetch strategy for markdown: auto, agent, jina, browser.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Print progress and diagnostic logs."
    ),
) -> None:
    """通过 Playwright 渲染并用 trafilatura 提取内容。"""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise typer.BadParameter("Only http or https URLs are supported.")
    if output_format != "markdown" and fetch_strategy != "auto":
        raise typer.BadParameter(
            "Custom fetch strategy is only supported with markdown output."
        )

    resolved_browser_path = str(browser_path) if browser_path else detect_browser_path()
    try:
        content: str | None = None
        if output_format == "markdown" and fetch_strategy == "auto":
            twitter_status_id = extract_twitter_status_id(url)
            if twitter_status_id:
                payload = fetch_fxtwitter_status(
                    twitter_status_id,
                    timeout_ms=timeout_ms,
                    verbose=verbose,
                )
                if payload is None:
                    raise ValueError(
                        "FxTwitter API request failed for this Twitter/X URL. "
                        "Use --fetch-strategy agent, jina, or browser to skip this path."
                    )
                content = render_fxtwitter_markdown(payload, source_url=url)
                if verbose:
                    CONSOLE.print(
                        "[green]Using FxTwitter API markdown path[/green]",
                        highlight=False,
                    )
        if output_format == "markdown":
            if content is None:
                if fetch_strategy == "auto":
                    content = fetch_agent_markdown(
                        url, timeout_ms=timeout_ms, verbose=verbose
                    )
                    if content is None:
                        content = fetch_jina_reader_markdown(
                            url,
                            timeout_ms=timeout_ms,
                            verbose=verbose,
                        )
                elif fetch_strategy == "agent":
                    content = fetch_agent_markdown(
                        url, timeout_ms=timeout_ms, verbose=verbose
                    )
                    if content is None:
                        raise ValueError(
                            "Markdown negotiation did not return usable content. "
                            "Try --fetch-strategy jina or --fetch-strategy browser."
                        )
                elif fetch_strategy == "jina":
                    content = fetch_jina_reader_markdown(
                        url, timeout_ms=timeout_ms, verbose=verbose
                    )
                    if content is None:
                        raise ValueError(
                            "Jina Reader did not return usable content. "
                            f"If this is rate limiting, configure {JINA_API_KEY_ENV} or try "
                            "--fetch-strategy browser."
                        )
                elif fetch_strategy == "browser" and verbose:
                    CONSOLE.print(
                        "[cyan]Skipping non-browser markdown readers[/cyan]",
                        highlight=False,
                    )
        if content is None:
            html = render_html(
                url,
                timeout_ms=timeout_ms,
                browser_path=resolved_browser_path,
                verbose=verbose,
            )
            content = (
                html
                if output_format == "raw-html"
                else extract_content(html, url, output_format, verbose=verbose)
            )
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
        CONSOLE.print(f"[green]Saved output to[/green] {output}", highlight=False)
    else:
        CONSOLE.print(content, markup=False)


if __name__ == "__main__":
    APP()
