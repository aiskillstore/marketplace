"""
External Tool Detector - 检测系统已安装的外部CLI工具
"""

import yaml
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from .base import ToolDetector
from ..models import ExternalTool, ToolMetadata


class ExternalToolDetector(ToolDetector):
    """外部工具检测器

    从external/目录扫描.meta.yml文件来发现外部工具配置
    """

    def __init__(self, root_path: Path):
        super().__init__(root_path)
        self._external_dir = root_path / "external"

    def detect(self) -> List[ExternalTool]:
        """
        扫描external/目录检测外部工具

        Returns:
            List[ExternalTool]: 检测到的外部工具列表
        """
        self._tools = []

        # 扫描external目录下的所有.meta.yml文件
        if self._external_dir.exists():
            for meta_file in self._external_dir.rglob("*.meta.yml"):
                tool = self._parse_meta_file(meta_file)
                if tool:
                    self._tools.append(tool)

        return self._tools

    def _parse_meta_file(self, meta_file: Path) -> Optional[ExternalTool]:
        """解析外部工具的meta.yml文件"""
        try:
            content = yaml.safe_load(meta_file.read_text(encoding='utf-8'))
            if not content:
                return None

            # 获取基本信息
            basic_info = content.get("基本信息", {})
            tool_type = basic_info.get("类型", "external")

            # 只处理external类型的工具
            if tool_type != "external":
                return None

            command = basic_info.get("命令", "")
            if not command:
                return None

            # 检测是否已安装
            command_name = command.split()[0]
            is_installed = shutil.which(command_name) is not None
            tool_path = shutil.which(command_name)

            # 创建metadata
            metadata = ToolMetadata(
                tool_id=content.get("tool_id", "unknown"),
                tool_name=content.get("tool_name", "未命名工具"),
                description=content.get("功能描述", {}).get("简介", "")
            )

            # 获取功能描述
            func_desc = content.get("功能描述", {})

            # 获取快速开始信息
            quick_start = content.get("快速开始", {})

            return ExternalTool(
                metadata=metadata,
                command=command,
                category=basic_info.get("类别", "unknown"),
                use_cases=content.get("使用场景", []),
                install_guide=quick_start.get("安装", ""),
                installed=is_installed,
                path=tool_path
            )

        except Exception as e:
            # 静默失败单个工具的检测
            return None

    def refresh(self):
        """刷新工具列表"""
        # 重新扫描external目录
        super().refresh()

    def find_tool(self, name_or_id: str) -> Optional[ExternalTool]:
        """
        查找外部工具

        Args:
            name_or_id: 工具名称或ID

        Returns:
            ExternalTool: 找到的工具，如果未找到返回None
        """
        # 先尝试精确匹配
        for tool in self._tools:
            if tool.tool_id == name_or_id or tool.tool_name == name_or_id:
                return tool

        # 尝试模糊匹配（名称包含）
        matches = [t for t in self._tools if name_or_id.lower() in t.tool_name.lower()]

        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            # 不打印，由调用者处理
            return None

        return None

    def get_uninstalled_tools(self) -> List[ExternalTool]:
        """获取未安装的工具列表"""
        return [t for t in self._tools if not t.installed]

    def get_installed_tools(self) -> List[ExternalTool]:
        """获取已安装的工具列表"""
        return [t for t in self._tools if t.installed]
