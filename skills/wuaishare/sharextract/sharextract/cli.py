from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .capabilities import get_capabilities
from .health import get_adapter_health, render_health_markdown
from .router import extract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sharextract",
        description="Extract normalized content from a public URL or inspect ShareXtract health.",
    )
    parser.add_argument("url", nargs="?", help="Public http(s) URL to extract")
    parser.add_argument(
        "--strategy",
        choices=("auto", "native", "media", "web"),
        default="auto",
        help="Extraction strategy (default: auto)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown", "text"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("--output", "-o", help="Write output to a file instead of stdout")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-bytes", type=int, default=8 * 1024 * 1024)
    parser.add_argument("--compact", action="store_true", help="Compact JSON output")
    parser.add_argument(
        "--health",
        action="store_true",
        help="Validate adapter registry, router integration, and packaged fixtures.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="With --health, also verify configured fixed public samples.",
    )
    parser.add_argument(
        "--adapter",
        action="append",
        default=[],
        help="With --health, limit checks to one adapter name; repeat as needed.",
    )
    parser.add_argument(
        "--capabilities",
        action="store_true",
        help="Print machine-readable installed capabilities instead of extracting a URL.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.health:
            report = get_adapter_health(
                live=args.live,
                adapter_names=args.adapter,
                timeout=args.timeout,
                max_bytes=args.max_bytes,
            )
            rendered = _render_health(
                report,
                args.format,
                compact=args.compact,
            )
            _write_output(rendered, args.output)
            return 0 if report.get("status") == "ok" else 1

        if args.capabilities:
            if args.live:
                parser.error("--live is only valid with --health")
            rendered = json.dumps(
                get_capabilities(),
                ensure_ascii=False,
                indent=None if args.compact else 2,
                separators=(",", ":") if args.compact else None,
            )
            _write_output(rendered, args.output)
            return 0

        if args.live:
            parser.error("--live is only valid with --health")
        if args.adapter:
            parser.error("--adapter is only valid with --health")
        if not args.url:
            parser.error("a public URL is required unless --health or --capabilities is used")

        result = extract(
            args.url,
            strategy=args.strategy,
            timeout=args.timeout,
            max_bytes=args.max_bytes,
        )
        rendered = _render(result, args.format, compact=args.compact)
    except Exception as exc:
        print(f"sharextract: {exc}", file=sys.stderr)
        return 2

    _write_output(rendered, args.output)
    return 0


def _write_output(rendered: str, output: str | None) -> None:
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


def _render_health(
    report: dict[str, Any],
    fmt: str,
    *,
    compact: bool,
) -> str:
    if fmt in {"markdown", "text"}:
        return render_health_markdown(report)
    return json.dumps(
        report,
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    )


def _render(result, fmt: str, *, compact: bool) -> str:
    if fmt == "markdown":
        return result.markdown or result.text
    if fmt == "text":
        return result.text or result.markdown
    return json.dumps(
        result.to_dict(),
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
