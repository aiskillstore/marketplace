#!/usr/bin/env python3
"""Memory Discovery CLI for AI Runtime

提供基于 SQL 风格参数的情景记忆 (episodic) 查询能力。

示例：
    python3 .ai-runtime/memory/memory_cli.py query \
        --select "id,timestamp,title" \
        --where "date>='2025-11-14' AND tags CONTAINS 'architecture'" \
        --order-by "timestamp desc" \
        --limit 20
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 确保可以从当前目录导入 memory_discovery
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))

from memory_discovery import MemoryDiscovery  # type: ignore


class MemoryCLI:
    """Episodic 记忆查询 CLI 接口"""

    def __init__(self, memory_root: Path) -> None:
        self.memory_root = memory_root
        self.discovery = MemoryDiscovery(memory_root)

    # ------------------------------------------------------------------
    # 外部入口
    # ------------------------------------------------------------------
    def run(self, args: None | list[str] = None) -> int:
        parser = self._create_parser()
        parsed = parser.parse_args(args)

        if not parsed.command:
            parser.print_help()
            return 0

        if parsed.command == "query":
            return self._cmd_query(parsed)

        parser.print_help()
        return 0

    # ------------------------------------------------------------------
    # Parser 定义
    # ------------------------------------------------------------------
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Memory discovery and query tool (episodic)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""示例:
  python3 .ai-runtime/memory/memory_cli.py query \
    --select "id,timestamp,title" \
    --where "level='day' AND date>='2025-11-14'" \
    --order-by "timestamp desc" \
    --limit 20
            """,
        )

        subparsers = parser.add_subparsers(dest="command", help="可用命令")
        self._add_query_parser(subparsers)

        return parser

    def _add_query_parser(self, subparsers: argparse._SubParsersAction) -> None:
        query = subparsers.add_parser("query", help="查询 episodic 记忆事件")
        query.add_argument(
            "--select",
            help="SELECT 字段列表，逗号分隔 (默认: id,timestamp,title)",
            default="id,timestamp,title",
        )
        query.add_argument(
            "--where",
            help="SQL 风格 WHERE 条件，仅支持 AND / = / != / >= / <= / tags CONTAINS",
        )
        query.add_argument(
            "--order-by",
            dest="order_by",
            help="排序字段，如 'timestamp desc' 或 'date asc'",
        )
        query.add_argument(
            "--limit",
            type=int,
            default=50,
            help="LIMIT 结果数量 (默认 50)",
        )
        query.add_argument(
            "--offset",
            type=int,
            default=0,
            help="OFFSET 偏移量 (默认 0)",
        )
        query.add_argument(
            "--format",
            choices=["table", "json"],
            default="table",
            help="输出格式 (table/json)",
        )

    # ------------------------------------------------------------------
    # 命令实现
    # ------------------------------------------------------------------
    def _cmd_query(self, args: argparse.Namespace) -> int:
        # 解析 select 字段
        select_fields = [f.strip() for f in (args.select or "").split(",") if f.strip()]

        events = self.discovery.query(
            where=args.where,
            order_by=args.order_by,
            limit=args.limit,
            offset=args.offset,
        )

        output = self.discovery.format_events(events, select=select_fields, format_type=args.format)
        print(output)
        return 0


def main() -> int:
    memory_root = CURRENT_DIR  # .ai-runtime/memory
    cli = MemoryCLI(memory_root)
    return cli.run()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
