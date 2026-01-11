"""
Main Discovery Orchestrator - 协调内部和外部工具检测
"""

from pathlib import Path
from typing import List, Optional
from .detectors import InternalToolDetector, ExternalToolDetector
from .models import Tool, InternalTool, ExternalTool
from .formatters import ToolFormatter, TableFormatter, JsonFormatter


class ToolkitDiscovery:
    """工具包发现主类 - 协调所有检测器"""

    def __init__(self, toolkit_root: Path):
        self.root = toolkit_root
        self.internal_detector = InternalToolDetector(toolkit_root)
        self.external_detector = ExternalToolDetector(toolkit_root)

        # 格式化器
        self.table_formatter = TableFormatter()
        self.json_formatter = JsonFormatter()

        # 初始化时加载所有工具
        self.refresh()

    def refresh(self):
        """刷新所有工具列表"""
        self.internal_detector.refresh()
        self.external_detector.refresh()

    @property
    def internal_tools(self) -> List[InternalTool]:
        """获取内部工具列表"""
        return self.internal_detector.tools

    @property
    def external_tools(self) -> List[ExternalTool]:
        """获取外部工具列表"""
        return self.external_detector.tools

    @property
    def all_tools(self) -> List[Tool]:
        """获取所有工具列表"""
        return self.internal_tools + self.external_tools

    def list_tools(
        self,
        internal_only: bool = False,
        external_only: bool = False
    ) -> List[Tool]:
        """
        列出工具

        Args:
            internal_only: 仅返回内部工具
            external_only: 仅返回外部工具

        Returns:
            List[Tool]: 工具列表
        """
        if internal_only:
            return self.internal_tools
        elif external_only:
            return self.external_tools
        else:
            return self.all_tools

    def find_tool(self, name_or_id: str) -> Optional[Tool]:
        """
        查找工具（同时搜索内部和外部）

        Args:
            name_or_id: 工具名称或ID

        Returns:
            Tool: 找到的工具，如果未找到返回None
        """
        # 先搜索内部工具
        tool = self.internal_detector.find_tool(name_or_id)
        if tool:
            return tool

        # 再搜索外部工具
        tool = self.external_detector.find_tool(name_or_id)
        if tool:
            return tool

        return None

    def filter_tools(
        self,
        lang: Optional[str] = None,
        purpose: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[InternalTool]:
        """
        过滤内部工具

        Args:
            lang: 按语言过滤
            purpose: 按用途过滤
            query: 按名称或描述搜索

        Returns:
            List[InternalTool]: 过滤后的内部工具列表
        """
        tools = self.internal_tools

        if lang:
            tools = [t for t in tools if t.language == lang]

        if purpose:
            tools = [t for t in tools if purpose in t.metadata.purpose]

        if query:
            query_lower = query.lower()
            tools = [
                t for t in tools
                if query_lower in t.tool_name.lower() or query_lower in t.description.lower()
            ]

        return tools

    def search_tools(self, keyword: str) -> List[Tool]:
        """
        搜索工具（内部和外部）

        Args:
            keyword: 搜索关键词

        Returns:
            List[Tool]: 匹配的工具列表
        """
        keyword_lower = keyword.lower()

        # 搜索内部工具
        internal_matches = [
            t for t in self.internal_tools
            if (keyword_lower in t.tool_name.lower() or
                keyword_lower in t.description.lower())
        ]

        # 搜索外部工具
        external_matches = [
            t for t in self.external_tools
            if (keyword_lower in t.tool_name.lower() or
                keyword_lower in t.description.lower() or
                keyword_lower in t.category.lower())
        ]

        return internal_matches + external_matches

    def recommend_tools(self, task_description: str) -> List[InternalTool]:
        """
        根据任务描述推荐工具

        Args:
            task_description: 任务描述

        Returns:
            List[InternalTool]: 推荐的工具列表（按匹配度排序）
        """
        keywords = task_description.lower().split()

        # 简单的推荐算法：匹配关键词数量
        scores = {}
        for tool in self.internal_tools:
            score = 0
            tool_text = (
                tool.tool_name + ' ' +
                tool.description + ' ' +
                ' '.join(tool.metadata.purpose)
            ).lower()

            for keyword in keywords:
                if keyword in tool_text:
                    score += 1

            if score > 0:
                scores[tool] = score

        # 按分数排序
        sorted_tools = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [tool for tool, _ in sorted_tools[:5]]  # 返回前5个

    def format_tools(
        self,
        tools: List[Tool],
        format_type: str = 'table'
    ) -> str:
        """
        格式化工具列表

        Args:
            tools: 工具列表
            format_type: 格式类型 ('table' 或 'json')

        Returns:
            str: 格式化后的字符串
        """
        if format_type == 'json':
            return self.json_formatter.format(tools)
        else:
            return self.table_formatter.format(tools)

    def format_tool(self, tool: Tool, format_type: str = 'table') -> str:
        """
        格式化单个工具

        Args:
            tool: 工具对象
            format_type: 格式类型 ('table' 或 'json')

        Returns:
            str: 格式化后的字符串
        """
        if format_type == 'json':
            return self.json_formatter.format_single(tool)
        else:
            return self.table_formatter.format_single(tool)
