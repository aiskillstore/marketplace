# -*- coding: utf-8 -*-
"""
PPTX Converter Module
Converts HTML presentation to PowerPoint format with animations
"""

from .parsers import ConfigParser, DataParser
from .animation import AnimationResolver, AnimationBuilder
from .layout import LayoutCalculator
from .styles import StyleMapper
from .components import ComponentRenderers
from .renderer import SlideRenderer

__all__ = [
    'ConfigParser',
    'DataParser', 
    'AnimationResolver',
    'AnimationBuilder',
    'LayoutCalculator',
    'StyleMapper',
    'ComponentRenderers',
    'SlideRenderer',
]
