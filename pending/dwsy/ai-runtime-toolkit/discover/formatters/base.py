"""
Abstract base class for tool formatters
"""

from abc import ABC, abstractmethod
from typing import List
from ..models import Tool


class ToolFormatter(ABC):
    """抽象基类：工具输出格式化器"""

    @abstractmethod
    def format(self, tools: List[Tool]) -> str:
        """
        格式化工具列表

        Args:
            tools: 工具列表

        Returns:
            str: 格式化后的字符串
        """
        pass

    @abstractmethod
    def format_single(self, tool: Tool) -> str:
        """
        格式化单个工具

        Args:
            tool: 工具对象

        Returns:
            str: 格式化后的字符串
        """
        pass
