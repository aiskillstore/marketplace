"""
Grasshopper Tools CLI 快捷腳本

在 grasshopper_tools 目錄下也可以直接運行
"""

import sys
import os

# 添加父目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 導入並運行 CLI
if __name__ == '__main__':
    from grasshopper_tools.cli import main
    main()

