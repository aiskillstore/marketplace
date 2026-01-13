"""
JSON Formatter - JSON格式输出
"""

import json
from typing import List
from .base import ToolFormatter
from ..models import Tool, InternalTool, ExternalTool


class JsonFormatter(ToolFormatter):
    """JSON格式化器"""

    def format(self, tools: List[Tool]) -> str:
        """格式化工具列表为JSON"""
        result = []
        for tool in tools:
            result.append(self._tool_to_dict(tool))
        return json.dumps(result, indent=2, ensure_ascii=False)

    def format_single(self, tool: Tool) -> str:
        """格式化单个工具为JSON"""
        return json.dumps(self._tool_to_dict(tool), indent=2, ensure_ascii=False)

    def _tool_to_dict(self, tool: Tool) -> dict:
        """将工具对象转换为字典"""
        # 基础信息
        data = {
            "tool_id": tool.tool_id,
            "tool_name": tool.tool_name,
            "description": tool.description
        }

        # 内部工具特有信息
        if isinstance(tool, InternalTool):
            data.update({
                "type": "internal",
                "language": tool.language,
                "file": tool.file,
                "complexity": tool.complexity,
                "meta_file": tool.meta_file,
                "tool_file": tool.tool_file,
                "purpose": tool.metadata.purpose,
                "usage": tool.usage
            })

            if tool.metadata.satisfaction > 0:
                data["satisfaction"] = tool.metadata.satisfaction

        # 外部工具特有信息
        elif isinstance(tool, ExternalTool):
            data.update({
                "type": "external",
                "command": tool.command,
                "category": tool.category,
                "use_cases": tool.use_cases,
                "install_guide": tool.install_guide,
                "installed": tool.installed
            })

            if tool.path:
                data["path"] = tool.path

            if tool.metadata.version != "1.0.0":
                data["version"] = tool.metadata.version

        return data
