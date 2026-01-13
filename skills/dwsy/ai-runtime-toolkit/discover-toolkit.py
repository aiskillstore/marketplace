#!/usr/bin/env python3
"""
Toolkit Discovery and Management Tool for AI-Runtime

该工具用于发现、查询和管理 ai-runtime 的工具装备系统。

功能：
- 列出所有内部工具（ai-runtime创建的工具）
- 检测外部CLI工具（fzf, eza, fd等）
- 按语言/用途过滤工具
- 智能工具推荐
- 显示工具详情和使用方法
- JSON格式输出支持

使用方法：
    python3 discover-toolkit.py list                    # 列出所有内部工具
    python3 discover-toolkit.py list --external         # 仅显示外部工具
    python3 discover-toolkit.py list --include-external # 显示所有工具
    python3 discover-toolkit.py show TOOL_ID            # 显示工具详情
    python3 discover-toolkit.py recommend "分析日志"     # 推荐工具
    python3 discover-toolkit.py search json             # 搜索工具
    python3 discover-toolkit.py run tool-id [args]      # 运行工具

架构：
    使用模块化设计，包含以下组件：
    - detectors/  : 工具检测器（内部/外部）
    - models/     : 数据模型（Tool, InternalTool, ExternalTool）
    - formatters/ : 输出格式化器（表格/JSON）
    - config/     : 配置文件

旧版本备份：discover-toolkit.py.old（单文件实现）
新版本：模块化包结构（discover/）
"""

import sys
from pathlib import Path

# 将 discover 包添加到路径
toolkit_root = Path(__file__).parent
sys.path.insert(0, str(toolkit_root))

from discover.cli import ToolkitCLI


def main():
    """主函数 - 调用 discover 包"""
    cli = ToolkitCLI(toolkit_root)
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
