"""
[INPUT]: 依赖 Python 标准库 logging
[OUTPUT]: 对外提供 logger 日志实例
[POS]: 日志模块，统一的日志记录功能
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

import logging


# ============================================================================
#  日志配置
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
