"""
CLI Interface for Toolkit Discovery
"""

import sys
import argparse
from pathlib import Path
from .discovery import ToolkitDiscovery


class ToolkitCLI:
    """Toolkit Discovery CLI Interface"""

    def __init__(self, toolkit_root: Path):
        self.toolkit_root = toolkit_root
        self.discovery = ToolkitDiscovery(toolkit_root)

    def run(self, args=None):
        """运行CLI"""
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.command:
            parser.print_help()
            return 0

        try:
            return self._execute_command(parsed_args)
        except Exception as e:
            print(f"❌ 错误: {e}", file=sys.stderr)
            return 1

    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            description="工具包发现和管理工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  python -m discover list                    # 列出所有工具
  python -m discover list --lang python     # 列出Python工具
  python -m discover list --external        # 仅显示外部工具
  python -m discover show SERVICE-CHECK-001 # 查看工具详情
  python -m discover recommend '分析日志'   # 推荐工具
  python -m discover search json            # 搜索工具
            """
        )

        subparsers = parser.add_subparsers(dest="command", help="可用命令")

        # list 命令
        self._add_list_parser(subparsers)

        # show 命令
        self._add_show_parser(subparsers)

        # run 命令
        self._add_run_parser(subparsers)

        # recommend 命令
        self._add_recommend_parser(subparsers)

        # search 命令
        self._add_search_parser(subparsers)

        return parser

    def _add_list_parser(self, subparsers):
        """添加list命令"""
        list_parser = subparsers.add_parser("list", help="列出所有工具")
        list_parser.add_argument("--lang", help="按语言过滤 (bash/python/node)")
        list_parser.add_argument("--purpose", help="按用途过滤 (DATA/CODE/TEST/BUILD/MONITOR/DOC)")
        list_parser.add_argument("--query", help="按名称或描述搜索")
        list_parser.add_argument("--json", action="store_true", help="JSON格式输出")
        list_parser.add_argument("--external", action="store_true", help="仅显示外部工具")
        list_parser.add_argument("--include-external", action="store_true", help="包含外部工具")

    def _add_show_parser(self, subparsers):
        """添加show命令"""
        show_parser = subparsers.add_parser("show", help="显示工具详情")
        show_parser.add_argument("tool", help="工具ID或名称")

    def _add_run_parser(self, subparsers):
        """添加run命令"""
        run_parser = subparsers.add_parser("run", help="运行工具")
        run_parser.add_argument("tool", help="工具ID或名称")
        run_parser.add_argument("args", nargs=argparse.REMAINDER, help="工具参数")

    def _add_recommend_parser(self, subparsers):
        """添加recommend命令"""
        recommend_parser = subparsers.add_parser("recommend", help="推荐工具")
        recommend_parser.add_argument("task", help="任务描述")

    def _add_search_parser(self, subparsers):
        """添加search命令"""
        search_parser = subparsers.add_parser("search", help="搜索工具")
        search_parser.add_argument("keyword", help="搜索关键词")

    def _execute_command(self, args) -> int:
        """执行命令"""
        if args.command == "list":
            return self._cmd_list(args)
        elif args.command == "show":
            return self._cmd_show(args)
        elif args.command == "run":
            return self._cmd_run(args)
        elif args.command == "recommend":
            return self._cmd_recommend(args)
        elif args.command == "search":
            return self._cmd_search(args)

        return 0

    def _cmd_list(self, args) -> int:
        """执行list命令"""
        # 判断输出格式
        format_type = "json" if args.json else "table"

        # 获取工具列表
        if args.external:
            tools = self.discovery.external_tools
        elif args.include_external:
            tools = self.discovery.all_tools
        else:
            tools = self.discovery.internal_tools

        # 过滤内部工具
        if not args.external:
            tools = self.discovery.filter_tools(
                lang=args.lang,
                purpose=args.purpose,
                query=args.query
            )

        # 输出
        output = self.discovery.format_tools(tools, format_type=format_type)
        print(output)
        return 0

    def _cmd_show(self, args) -> int:
        """执行show命令"""
        tool = self.discovery.find_tool(args.tool)
        if not tool:
            print(f"❌ 未找到工具: {args.tool}")
            return 1

        print(self.discovery.format_tool(tool))
        return 0

    def _cmd_run(self, args) -> int:
        """执行run命令"""
        # 注意: 这里简化处理，实际应该直接从文件执行
        # 为了保持向后兼容，这里直接调用工具文件
        import subprocess

        tool = self.discovery.find_tool(args.tool)
        if not tool:
            print(f"❌ 未找到工具: {args.tool}")
            return 1

        # 检查是否有tool_file（仅内部工具有）
        if not hasattr(tool, 'tool_file') or not tool.tool_file:
            print(f"❌ 外部工具无法直接运行: {args.tool}")
            return 1

        tool_path = self.toolkit_root / tool.tool_file
        if not tool_path.exists():
            print(f"❌ 工具文件不存在: {tool_path}")
            return 1

        print(f"🚀 运行工具: {tool.tool_name}")
        print(f"📁 文件: {tool.tool_file}")
        print(f"⏳ 正在执行...")
        print("=" * 70)

        try:
            cmd = [str(tool_path)] + args.args
            result = subprocess.run(cmd, capture_output=False)
            print("=" * 70)
            print(f"✅ 执行完成 (退出码: {result.returncode})")
            return result.returncode
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            return 1

    def _cmd_recommend(self, args) -> int:
        """执行recommend命令"""
        tools = self.discovery.recommend_tools(args.task)

        if not tools:
            print(f"💡 未找到匹配的工具，尝试使用更通用的关键词搜索")
            return 0

        print(f"\n🔍 为任务 '{args.task}' 推荐工具:")
        print("=" * 70)

        for i, tool in enumerate(tools[:5], 1):
            print(f"\n{i}. {tool.tool_name}")
            print(f"   ID: {tool.tool_id}")
            print(f"   语言: {tool.language}")
            print(f"   描述: {tool.description[:60]}...")

        print("\n" + "=" * 70)
        print("💡 使用: show <tool-id> 查看详情")
        return 0

    def _cmd_search(self, args) -> int:
        """执行search命令"""
        tools = self.discovery.search_tools(args.keyword)

        if not tools:
            print(f"⚠️  未找到包含 '{args.keyword}' 的工具")
            return 0

        print(f"\n🔍 搜索 '{args.keyword}' 找到 {len(tools)} 个结果:")
        for tool in tools:
            print(f"  • {tool.tool_name} ({tool.tool_id}) - {tool.description[:50]}...")
        print()
        return 0


def main():
    """主函数"""
    toolkit_root = Path(__file__).parent.parent
    cli = ToolkitCLI(toolkit_root)
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
