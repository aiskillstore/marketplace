"""Shared Chrome / Playwright Chromium launch and actionable setup errors."""
from __future__ import annotations

from _net import resolve_proxy


async def launch_browser(playwright, proxy: str | None = None):
    value = resolve_proxy(proxy)
    options = {"headless": True, "timeout": 15000,
               "args": ["--disable-blink-features=AutomationControlled"]}
    if value:
        options["proxy"] = {"server": value.replace("socks5h://", "socks5://")}
    else:
        options["args"].append("--no-proxy-server")
    errors = []
    for channel in ("chrome", None):
        try:
            browser = await playwright.chromium.launch(
                **({"channel": channel} if channel else {}), **options)
            return browser, "Google Chrome" if channel else "Playwright Chromium"
        except Exception as exc:
            errors.append(f"{channel or 'chromium'}: {str(exc).splitlines()[0]}")
    raise RuntimeError(
        "Neither Google Chrome nor Playwright Chromium could start. "
        "Run `uvx playwright install chromium` and retry; on Linux, missing system libraries "
        "may require `uvx playwright install --with-deps chromium`. "
        + " | ".join(errors))
