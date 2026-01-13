"""
Toolkit Discovery Package

A modular toolkit discovery and management system for ai-runtime.
"""

__version__ = "2.0.0"
__author__ = "AI-Runtime Team"

from .discovery import ToolkitDiscovery
from .models import Tool, InternalTool, ExternalTool, ToolMetadata
from .detectors import ToolDetector, InternalToolDetector, ExternalToolDetector
from .formatters import ToolFormatter, TableFormatter, JsonFormatter
from .cli import ToolkitCLI

__all__ = [
    # Main classes
    'ToolkitDiscovery',
    'ToolkitCLI',

    # Models
    'Tool',
    'InternalTool',
    'ExternalTool',
    'ToolMetadata',

    # Detectors
    'ToolDetector',
    'InternalToolDetector',
    'ExternalToolDetector',

    # Formatters
    'ToolFormatter',
    'TableFormatter',
    'JsonFormatter',
]
