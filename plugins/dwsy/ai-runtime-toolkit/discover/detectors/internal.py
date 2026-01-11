"""
Internal Tool Detector - 检测AI-runtime内部创建的工具
"""

import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base import ToolDetector
from ..models import InternalTool, ToolMetadata


class InternalToolDetector(ToolDetector):
    """内部工具检测器"""

    def detect(self) -> List[InternalTool]:
        """
        扫描工具包目录检测内部工具

        Returns:
            List[InternalTool]: 检测到的内部工具列表
        """
        self._tools = []

        # 加载registry.md（暂时跳过详细解析）
        registry_file = self.root / "registry.md"
        if registry_file.exists():
            # 这里可以扩展registry解析逻辑
            pass

        # 扫描所有语言目录
        for lang_dir in self.root.iterdir():
            if lang_dir.is_dir() and not lang_dir.name.startswith('.') and lang_dir.name != 'discover':
                self._scan_language_directory(lang_dir)

        return self._tools

    def _scan_language_directory(self, lang_dir: Path):
        """扫描语言目录下的工具"""
        for meta_file in lang_dir.rglob("*.meta.yml"):
            try:
                tool = self._parse_meta_file(meta_file)
                if tool:
                    self._tools.append(tool)
            except Exception as e:
                print(f"⚠️  解析失败 {meta_file}: {e}", file=sys.stderr)

    def _parse_meta_file(self, meta_file: Path) -> Optional[InternalTool]:
        """解析元数据文件"""
        try:
            content = yaml.safe_load(meta_file.read_text(encoding='utf-8'))
            if not content:
                return None

            # 获取工具文件
            tool_file = self._find_tool_file(meta_file)

            # 解析基本信息
            basic_info = content.get("基本信息", {})

            # 创建metadata
            metadata = ToolMetadata(
                tool_id=content.get("tool_id", "unknown"),
                tool_name=content.get("tool_name", "未命名工具"),
                description=content.get("功能描述", {}).get("简介", ""),
                purpose=content.get("用途分类", [])
            )

            # 解析上次使用信息
            last_use = content.get("上次使用", {})
            if last_use:
                metadata.satisfaction = last_use.get("满意度", 0.0)

            return InternalTool(
                metadata=metadata,
                meta_file=str(meta_file.relative_to(self.root)),
                tool_file=str(tool_file.relative_to(self.root)) if tool_file else None,
                language=basic_info.get("语言", "unknown"),
                file=basic_info.get("文件", "unknown"),
                complexity=basic_info.get("复杂度", "unknown"),
                usage=content.get("使用方法", {}),
                full_meta=content
            )

        except Exception as e:
            print(f"⚠️  警告: 解析元数据文件失败 {meta_file}: {e}", file=sys.stderr)
            return None

    def _find_tool_file(self, meta_file: Path) -> Optional[Path]:
        """查找与meta文件对应的工具文件"""
        possible_extensions = ['.sh', '.py', '.js', '.ts', '.java', '.go', '.rs']

        for ext in possible_extensions:
            possible_file = meta_file.with_suffix(ext)
            if possible_file.exists():
                return possible_file

        # 如果没找到，尝试与meta文件同名（去掉.meta部分）
        name_without_meta = meta_file.stem.replace('.meta', '')
        for ext in possible_extensions:
            possible_file = meta_file.parent / f"{name_without_meta}{ext}"
            if possible_file.exists():
                return possible_file

        return None

    def find_tool(self, name_or_id: str) -> Optional[InternalTool]:
        """
        查找内部工具

        Args:
            name_or_id: 工具名称或ID

        Returns:
            InternalTool: 找到的工具，如果未找到返回None
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
            print(f"⚠️  找到多个匹配工具:")
            for i, tool in enumerate(matches[:5], 1):
                print(f"  {i}. {tool.tool_name} ({tool.tool_id})")
            return None

        return None

    def refresh(self):
        """刷新工具列表"""
        super().refresh()
