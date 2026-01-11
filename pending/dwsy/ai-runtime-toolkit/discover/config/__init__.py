"""
Configuration management for toolkit discovery
"""

from pathlib import Path

CONFIG_ROOT = Path(__file__).parent
EXTERNAL_TOOLS_CONFIG = CONFIG_ROOT / "external_tools.yaml"

__all__ = [
    'CONFIG_ROOT',
    'EXTERNAL_TOOLS_CONFIG'
]
