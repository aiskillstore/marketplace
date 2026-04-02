#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qryma Platform Adapter
"""
import argparse
import json
import sys
from typing import List, Dict, Any

# Try relative import, fall back to absolute import if failed
try:
    from ..search_core import QrymaSearchCore
except (ImportError, ValueError):
    # Use absolute import when running as standalone script
    import os
    import sys
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from search_core import QrymaSearchCore


def main():
    """Main entry point for the skill"""
    parser = QrymaAdapter.create_parser()
    args = parser.parse_args()
    adapter = QrymaAdapter(api_key=getattr(args, "api_key", None))
    adapter.run(args)


def to_brave_like(obj: dict) -> dict:
    """Convert to Brave search-like format (title/url/snippet)"""
    results = []
    for r in obj.get("results", []) or []:
        result = {
            "title": r.get("title"),
            "url": r.get("url"),
            "content": r.get("content"),  # Use content as snippet
        }
        results.append(result)
    out = {"query": obj.get("query"), "results": results}
    if "answer" in obj:
        out["answer"] = obj.get("answer")
    return out


def to_markdown(obj: dict) -> str:
    """Convert to Markdown format"""
    lines = []
    if obj.get("answer"):
        lines.append(obj["answer"].strip())
        lines.append("")

    for i, r in enumerate(obj.get("results", []) or [], 1):
        title = (r.get("title") or "").strip() or r.get("url") or "(no title)"
        url = r.get("url") or ""
        content = (r.get("content") or "").strip()

        lines.append(f"{i}. {title}")
        if url:
            lines.append(f" {url}")
        if content:
            lines.append(f" - {content}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


class QrymaAdapter:
    """Qryma adapter"""

    def __init__(self, core: QrymaSearchCore = None, api_key: str = None):
        if core:
            self.core = core
        else:
            self.core = QrymaSearchCore(api_key=api_key)
    def run(self, args: argparse.Namespace) -> None:        
        """Execute search"""
        try:
            result = self.core.search(
                query=args.query,
                max_results=args.max_results,
                lang=getattr(args, "lang", None),
                start=getattr(args, "start", 0),
                safe=getattr(args, "safe", False),
                mode=getattr(args, "mode", "fulltext"),
            )

            if args.format == "md":
                output = to_markdown(result)
                # 直接向缓冲区写入UTF-8编码的字节，避免编码问题
                sys.stdout.buffer.write(output.encode('utf-8'))
            elif args.format == "brave":
                result = to_brave_like(result)
                # 使用UTF-8编码写入JSON
                json_str = json.dumps(result, ensure_ascii=False, default=str)
                sys.stdout.buffer.write(json_str.encode('utf-8'))
                sys.stdout.buffer.write(b'\n')
            else:
                json_str = json.dumps(result, ensure_ascii=False, default=str)
                sys.stdout.buffer.write(json_str.encode('utf-8'))
                sys.stdout.buffer.write(b'\n')

        except Exception as e:
            raise SystemExit(f"Error: {e}")

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create command line parser"""
        parser = argparse.ArgumentParser(
            description="Qryma search tool"
        )
        parser.add_argument("--api-key", help="Qryma API key")
        parser.add_argument("--query", required=True, help="Search query")
        parser.add_argument(
            "--max-results",
            type=int,
            default=5,
            help="Maximum number of results",
        )
        parser.add_argument(
            "--lang",
            default=None,
            help="Language code (default: auto-detect)",
        )
        parser.add_argument(
            "--start",
            type=int,
            default=0,
            help="Start offset (default: 0)",
        )
        parser.add_argument(
            "--safe",
            action="store_true",
            help="Enable safe search (default: False)",
        )
        parser.add_argument(
            "--mode",
            default="fulltext",
            choices=["fulltext", "snippet"],
            help="Search mode: fulltext (detailed) | snippet (concise) (default: fulltext)",
        )
        parser.add_argument(
            "--format",
            default="raw",
            choices=["raw", "brave", "md"],
            help="Output format: raw | brave | md",
        )
        return parser


if __name__ == "__main__":
    main()
