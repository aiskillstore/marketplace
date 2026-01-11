"""
数据模型：工具和元数据定义
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class ToolUsage:
    """工具使用信息"""
    command: str
    task: str
    trigger: str
    expected: str

    execution_status: str = "unknown"
    output_files: List[str] = field(default_factory=list)
    key_findings: Dict[str, Any] = field(default_factory=dict)
    satisfaction: float = 0.0
    duration: float = 0.0

    followup_actions: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class ToolMetadata:
    """工具元数据基类"""
    tool_id: str
    tool_name: str
    description: str
    purpose: List[str] = field(default_factory=list)
    last_used: Optional[datetime] = None
    satisfaction: float = 0.0

    related_tools: Dict[str, List[str]] = field(default_factory=dict)
    maintenance_notes: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"


@dataclass
class Tool:
    """工具基类"""
    metadata: ToolMetadata

    @property
    def tool_id(self) -> str:
        return self.metadata.tool_id

    @property
    def tool_name(self) -> str:
        return self.metadata.tool_name

    @property
    def description(self) -> str:
        return self.metadata.description


@dataclass
class InternalTool(Tool):
    """内部工具（AI-runtime创建的工具）"""
    meta_file: str
    tool_file: Optional[str]
    language: str
    file: str
    complexity: str

    usage: Dict[str, Any] = field(default_factory=dict)
    full_meta: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not isinstance(self.metadata, ToolMetadata):
            self.metadata = ToolMetadata(
                tool_id=self.tool_id,
                tool_name=self.tool_name,
                description=self.description,
                purpose=self.metadata.get("purpose", []) if isinstance(self.metadata, dict) else self.metadata.purpose
            )


@dataclass
class ExternalTool(Tool):
    """外部工具（第三方CLI工具）"""
    command: str
    category: str
    use_cases: List[str]
    install_guide: str

    installed: bool = False
    path: Optional[str] = None

    @property
    def status(self) -> str:
        """获取安装状态"""
        return "✅ 已安装" if self.installed else "❌ 未安装"


class ToolDetectorError(Exception):
    """工具检测异常"""
    pass


class ToolFormatError(Exception):
    """工具格式化异常"""
    pass
