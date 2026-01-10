"""
Table Formatter - 表格格式输出
"""

from typing import List, Any
from .base import ToolFormatter
from ..models import Tool, InternalTool, ExternalTool


class TableFormatter(ToolFormatter):
    """表格格式化器"""

    def format(self, tools: List[Tool]) -> str:
        """格式化工具列表为表格"""
        if not tools:
            return "⚠️  未找到匹配的工具\n"

        # 分离内部工具和外部工具
        internal = [t for t in tools if isinstance(t, InternalTool)]
        external = [t for t in tools if isinstance(t, ExternalTool)]

        output = []

        # 内部工具
        if internal:
            output.append(self._format_internal_tools(internal))

        # 外部工具
        if external:
            if internal:
                output.append("")
            output.append(self._format_external_tools(external))

        return "\n".join(output) + "\n"

    def _format_internal_tools(self, tools: List[InternalTool]) -> str:
        """格式化内部工具"""
        lines = [
            f"📦 找到 {len(tools)} 个内部工具:",
            "=" * 110,
            f"{'名称':<25} {'ID':<25} {'语言':<8} {'用途':<15} {'描述':<30}",
            "-" * 110
        ]

        for tool in tools:
            purposes = ",".join(tool.metadata.purpose)[:13]
            desc = tool.description[:28]
            lines.append(
                f"{tool.tool_name:<25} {tool.tool_id:<25} {tool.language:<8} {purposes:<15} {desc:<30}"
            )

        lines.append("=" * 110)
        return "\n".join(lines)

    def _format_external_tools(self, tools: List[ExternalTool]) -> str:
        """格式化外部工具"""
        lines = [
            f"🌟 找到 {len(tools)} 个外部工具:",
            "=" * 100,
            f"{'名称':<25} {'ID':<20} {'分类':<12} {'安装状态':<10} {'描述':<30}",
            "-" * 100
        ]

        for tool in tools:
            status = tool.status
            desc = tool.description[:30]
            lines.append(
                f"{tool.tool_name:<25} {tool.tool_id:<20} {tool.category:<12} {status:<10} {desc:<30}"
            )

        lines.append("=" * 100)
        lines.extend([
            "",
            "💡 提示: 使用 --external 仅显示外部工具",
            "💡 提示: 外部工具是系统级的CLI工具，需单独安装"
        ])

        return "\n".join(lines)

    def format_single(self, tool: Tool) -> str:
        """格式化单个工具详情"""
        if isinstance(tool, InternalTool):
            return self._format_internal_tool(tool)
        elif isinstance(tool, ExternalTool):
            return self._format_external_tool(tool)
        else:
            return self._format_generic_tool(tool)

    def _format_internal_tool(self, tool: InternalTool) -> str:
        """格式化内部工具详情"""
        lines = [
            "",
            "=" * 70,
            f"📦 {tool.tool_name}",
            "=" * 70,
            f"ID: {tool.tool_id}",
            f"语言: {tool.language}",
            f"文件: {tool.file}",
            f"复杂度: {tool.complexity}",
            f"用途: {', '.join(tool.metadata.purpose)}",
            "",
            "📋 描述:",
            f"  {tool.description}",
            ""
        ]

        if tool.usage:
            lines.append("🚀 使用方法:")
            if '命令' in tool.usage:
                lines.append(f"  命令: {tool.usage['命令']}")
            if '参数' in tool.usage:
                lines.append("  参数:")
                for param, desc in tool.usage['参数'].items():
                    lines.append(f"    - {param}: {desc}")
            if '示例' in tool.usage:
                lines.append("  示例:")
                for example in tool.usage.get('示例', [])[:3]:
                    lines.append(f"    • {example}")
            lines.append("")

        if tool.metadata.satisfaction > 0:
            lines.extend([
                "📊 使用统计:",
                f"  满意度: {tool.metadata.satisfaction}/1.0",
                ""
            ])

        lines.extend([
            "📂 文件位置:",
            f"  元数据: {tool.meta_file}",
            f"{'=' * 70}",
            ""
        ])

        return "\n".join(lines)

    def _format_external_tool(self, tool: ExternalTool) -> str:
        """格式化外部工具详情"""
        lines = [
            "",
            "=" * 70,
            f"🌟 {tool.tool_name}",
            "=" * 70,
            f"ID: {tool.tool_id}",
            f"分类: {tool.category}",
            f"命令: {tool.command}",
            f"状态: {tool.status}",
            "",
            "📋 描述:",
            f"  {tool.description}",
            "",
            "💡 使用场景:",
        ]

        for use_case in tool.use_cases:
            lines.append(f"  • {use_case}")

        lines.extend([
            "",
            "📥 安装指南:",
            f"  {tool.install_guide}",
            ""
        ])

        if tool.path:
            lines.extend([
                "📂 安装路径:",
                f"  {tool.path}",
                ""
            ])

        lines.append(f"{'=' * 70}\n")

        return "\n".join(lines)

    def _format_generic_tool(self, tool: Tool) -> str:
        """格式化通用工具详情"""
        return f"\n{'=' * 70}\n📦 {tool.tool_name} ({tool.tool_id})\n{'=' * 70}\n  描述: {tool.description}\n{'=' * 70}\n\n"
