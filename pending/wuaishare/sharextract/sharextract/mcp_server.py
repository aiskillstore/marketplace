from __future__ import annotations

import argparse
from typing import Any, Literal

from . import __version__
from .capabilities import get_capabilities
from .health import get_adapter_health
from .router import extract

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover - optional-dependency boundary
    raise RuntimeError(
        'MCP dependencies are not installed. Install with: pip install -e ".[mcp]"'
    ) from exc


mcp = MCPServer(
    "ShareXtract",
    instructions=(
        "Extract content that is already publicly accessible using ShareXtract's "
        "protocol-first router. Do not use this server to bypass authentication, "
        "CAPTCHAs, paywalls, WAFs, or private sharing controls."
    ),
)


def extract_public_url_impl(
    url: str,
    strategy: Literal["auto", "native", "media", "web"] = "auto",
    timeout: float = 20.0,
    max_bytes: int = 8 * 1024 * 1024,
) -> dict[str, Any]:
    return extract(
        url,
        strategy=strategy,
        timeout=timeout,
        max_bytes=max_bytes,
    ).to_dict()


@mcp.tool()
def extract_public_url(
    url: str,
    strategy: Literal["auto", "native", "media", "web"] = "auto",
    timeout: float = 20.0,
    max_bytes: int = 8 * 1024 * 1024,
) -> dict[str, Any]:
    """Extract and normalize one public HTTP(S) share/content URL."""
    return extract_public_url_impl(
        url=url,
        strategy=strategy,
        timeout=timeout,
        max_bytes=max_bytes,
    )


@mcp.tool()
def list_sharextract_capabilities() -> dict[str, Any]:
    """List the installed ShareXtract extraction routes and safety boundary."""
    return {"version": __version__, **get_capabilities()}


@mcp.tool()
def get_sharextract_adapter_health(
    live: bool = False,
    adapter_names: list[str] | None = None,
    timeout: float = 12.0,
) -> dict[str, Any]:
    """Validate adapter registry/fixtures and optionally probe fixed public samples."""
    return {
        "version": __version__,
        **get_adapter_health(
            live=live,
            adapter_names=adapter_names,
            timeout=timeout,
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the ShareXtract MCP server.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    parser.add_argument("--json-response", action="store_true")
    args = parser.parse_args(argv)

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            json_response=args.json_response,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
