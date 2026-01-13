#!/usr/bin/env python3
"""
Playwright Undetected Skill Executor
=====================================
Localhost + Private IP + Bot bypass browser automation.

Usage:
    python executor.py --list                    # List tools
    python executor.py --call '{"tool": "screenshot", "args": {"url": "http://localhost:3000"}}'
"""

import asyncio
import json
import sys
import base64
from pathlib import Path

# Patchright import
try:
    from patchright.async_api import async_playwright
    HAS_PATCHRIGHT = True
except ImportError:
    HAS_PATCHRIGHT = False
    print("Error: patchright not installed. Run: pip install patchright", file=sys.stderr)

# Global browser state
_browser = None
_page = None


async def launch_browser(headless: bool = False):
    """Launch Chrome browser with patchright stealth."""
    global _browser, _page

    if _browser:
        return {"status": "already_running", "message": "Browser already launched"}

    pw = await async_playwright().start()
    _browser = await pw.chromium.launch(
        headless=headless,
        channel='chrome',
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-gpu',
            '--no-first-run'
        ]
    )
    _page = await _browser.new_page()
    return {"status": "success", "message": "Browser launched"}


async def close_browser():
    """Close browser."""
    global _browser, _page

    if _browser:
        await _browser.close()
        _browser = None
        _page = None
        return {"status": "success", "message": "Browser closed"}
    return {"status": "not_running", "message": "No browser to close"}


async def navigate(url: str):
    """Navigate to URL (localhost supported!)."""
    global _page

    if not _page:
        await launch_browser()

    await _page.goto(url, wait_until='networkidle', timeout=30000)
    return {
        "status": "success",
        "url": _page.url,
        "title": await _page.title()
    }


async def screenshot(path: str = None, full_page: bool = False):
    """Take screenshot and save to file."""
    global _page

    if not _page:
        return {"status": "error", "message": "No page open. Navigate first."}

    if not path:
        path = f"screenshot_{int(asyncio.get_event_loop().time())}.png"

    await _page.screenshot(path=path, full_page=full_page)
    return {
        "status": "success",
        "path": str(Path(path).absolute()),
        "url": _page.url
    }


async def screenshot_base64(full_page: bool = False):
    """Take screenshot and return as base64."""
    global _page

    if not _page:
        return {"status": "error", "message": "No page open. Navigate first."}

    data = await _page.screenshot(full_page=full_page)
    return {
        "status": "success",
        "base64": base64.b64encode(data).decode(),
        "url": _page.url
    }


async def click(selector: str):
    """Click element."""
    global _page

    if not _page:
        return {"status": "error", "message": "No page open"}

    await _page.click(selector, timeout=10000)
    return {"status": "success", "selector": selector}


async def type_text(selector: str, text: str):
    """Type text into input."""
    global _page

    if not _page:
        return {"status": "error", "message": "No page open"}

    await _page.fill(selector, text)
    return {"status": "success", "selector": selector}


async def get_text(selector: str):
    """Get text content of element."""
    global _page

    if not _page:
        return {"status": "error", "message": "No page open"}

    text = await _page.text_content(selector)
    return {"status": "success", "text": text}


async def wait_for(selector: str, timeout: int = 10000):
    """Wait for element to appear."""
    global _page

    if not _page:
        return {"status": "error", "message": "No page open"}

    await _page.wait_for_selector(selector, timeout=timeout)
    return {"status": "success", "selector": selector}


async def get_url():
    """Get current URL."""
    global _page

    if not _page:
        return {"status": "error", "message": "No page open"}

    return {"status": "success", "url": _page.url}


async def get_title():
    """Get page title."""
    global _page

    if not _page:
        return {"status": "error", "message": "No page open"}

    return {"status": "success", "title": await _page.title()}


# Tool registry
TOOLS = {
    "launch": {
        "fn": launch_browser,
        "description": "Launch Chrome browser with stealth mode",
        "args": {"headless": "bool (default: false)"}
    },
    "close": {
        "fn": close_browser,
        "description": "Close browser",
        "args": {}
    },
    "navigate": {
        "fn": navigate,
        "description": "Navigate to URL (localhost supported!)",
        "args": {"url": "string (required)"}
    },
    "screenshot": {
        "fn": screenshot,
        "description": "Take screenshot and save to file",
        "args": {"path": "string (optional)", "full_page": "bool (default: false)"}
    },
    "screenshot_base64": {
        "fn": screenshot_base64,
        "description": "Take screenshot and return as base64",
        "args": {"full_page": "bool (default: false)"}
    },
    "click": {
        "fn": click,
        "description": "Click element by selector",
        "args": {"selector": "string (required)"}
    },
    "type": {
        "fn": type_text,
        "description": "Type text into input field",
        "args": {"selector": "string (required)", "text": "string (required)"}
    },
    "get_text": {
        "fn": get_text,
        "description": "Get text content of element",
        "args": {"selector": "string (required)"}
    },
    "wait_for": {
        "fn": wait_for,
        "description": "Wait for element to appear",
        "args": {"selector": "string (required)", "timeout": "int (default: 10000)"}
    },
    "get_url": {
        "fn": get_url,
        "description": "Get current page URL",
        "args": {}
    },
    "get_title": {
        "fn": get_title,
        "description": "Get current page title",
        "args": {}
    }
}


def list_tools():
    """List all available tools."""
    result = []
    for name, info in TOOLS.items():
        result.append({
            "name": name,
            "description": info["description"],
            "args": info["args"]
        })
    return result


async def call_tool(tool_name: str, args: dict = None):
    """Call a tool by name with arguments."""
    if tool_name not in TOOLS:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    args = args or {}
    fn = TOOLS[tool_name]["fn"]

    try:
        result = await fn(**args)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python executor.py --list")
        print("  python executor.py --call '{\"tool\": \"navigate\", \"args\": {\"url\": \"http://localhost:3000\"}}'")
        sys.exit(1)

    if not HAS_PATCHRIGHT:
        print(json.dumps({"status": "error", "message": "patchright not installed"}))
        sys.exit(1)

    if sys.argv[1] == "--list":
        print(json.dumps(list_tools(), indent=2))

    elif sys.argv[1] == "--call":
        if len(sys.argv) < 3:
            print(json.dumps({"status": "error", "message": "Missing call JSON"}))
            sys.exit(1)

        try:
            call_data = json.loads(sys.argv[2])
            tool_name = call_data.get("tool")
            args = call_data.get("args", {})

            result = await call_tool(tool_name, args)
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError as e:
            print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
            sys.exit(1)

    else:
        print(json.dumps({"status": "error", "message": f"Unknown command: {sys.argv[1]}"}))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
