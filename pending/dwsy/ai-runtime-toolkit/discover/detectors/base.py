"""
Base detector interface for toolkit discovery
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any
from ..models import Tool


class ToolDetector(ABC):
    """抽象基类：工具检测器"""

    def __init__(self, root_path: Path):
        self.root = root_path
        self._tools = []

    @property
    def tools(self) -> List[Tool]:
        """获取检测到的工具列表"""
        return self._tools

    @abstractmethod
    def detect(self) -> List[Tool]:
        """
        检测工具

        Returns:
            List[Tool]: 检测到的工具列表
        """
        pass

    @abstractmethod
    def find_tool(self, name_or_id: str) -> Tool:
        """
        查找工具

        Args:
            name_or_id: 工具名称或ID

        Returns:
            Tool: 找到的工具

        Raises:
            ToolDetectorError: 如果工具未找到
        """
        pass

    def refresh(self):
        """刷新工具列表"""
        self._tools = self.detect()
